# ruff: noqa: E701,E702,E402
#!/usr/bin/env python3
"""XFCOH31 lane: canary (EXP-1), hide-and-recover holdout (EXP-2), final fit+emit (EXP-3).
Preregistered in knowledge/2026-10-26_xfcoh31_preregistration.md before fitting."""
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter, distance_transform_edt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"))
from gemsdoe31 import holdout as ho
from gemsdoe31.emission import emit_dots

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def rz(a, fp):
    v=a[fp]; med=np.nanmedian(v); mad=np.nanmedian(np.abs(v-med)) or 1.0
    z=np.clip((np.where(np.isfinite(a),a,med)-med)/(1.4826*mad),-8,8); return np.where(fp,z,0).astype(np.float32)
def gm(z,s):
    gy=gaussian_filter(z,sigma=s,order=(1,0),mode='nearest'); gx=gaussian_filter(z,sigma=s,order=(0,1),mode='nearest')
    return gx,gy,np.hypot(gx,gy).astype(np.float32)

log("loading bands")
with rasterio.open(ROOT/"data/sample_submission.tif") as d: fp=np.isfinite(d.read(1))
with rasterio.open(ROOT/"data/labels.tif") as d: cat=d.read(1)==1
names19=["mag_anom","rtp","tmi_hg","geod_2ndinv","iso_grav_slope","tc","geod_shear","geod_dilate","tmi_vg","deq","iso_grav_vg","det_elev","iso_grav","tmi","depth_base","ieq","cond_surf","iso_grav_hg","det_elev_slope"]
H,W=fp.shape; NF=29
cache=ROOT/".cache"; cache.mkdir(exist_ok=True)
mm=np.memmap(cache/"xfcoh_X.f32",dtype=np.float32,mode="w+",shape=(NF,H,W))
def read_band(i):
    with rasterio.open(ROOT/"data/training_features.tif") as d:
        a=d.read(i).astype(np.float32); a[~np.isfinite(a)|(a<-1e30)]=np.nan; return a
for i,nm in enumerate(names19):
    mm[i]=rz(read_band(i+1),fp); log(f"base {nm}")
idx={n:i for i,n in enumerate(names19)}
def Z(n): return np.array(mm[idx[n]])
gx_r,gy_r,g_r=gm(Z("rtp"),1.5); gx_g,gy_g,g_g=gm(Z("iso_grav"),1.5)
_,_,g_r3=gm(Z("rtp"),3.0); _,_,g_g3=gm(Z("iso_grav"),3.0); _,_,g_d=gm(Z("depth_base"),1.5)
zgr,zg_g,zgd=rz(g_r,fp),rz(g_g,fp),rz(g_d,fp)
same=np.minimum(zgr,zg_g)
off=np.zeros_like(same)
for dy in (-2,0,2):
    for dx in (-2,0,2):
        if dy==0 and dx==0: continue
        sh=np.roll(np.roll(zgr,dy,0),dx,1); off=np.maximum(off,np.minimum(sh,zg_g))
offset=np.clip(off-same,0,None).astype(np.float32)
cosang=np.abs((gx_r*gx_g+gy_r*gy_g)/(g_r*g_g+1e-6)).astype(np.float32)
novel=[g_r,g_g,g_d,g_r3,g_g3,same,offset,rz(cosang,fp),np.minimum(zgr,zgd)]
novel_names=["xf_grad_rtp_s1.5","xf_grad_grav_s1.5","xf_grad_depth_s1.5","xf_grad_rtp_s3","xf_grad_grav_s3","xf_samepixel_coherence","xf_offset_coherence_2px","xf_orientation_abs_cos","xf_rtp_depth_coherence"]
for j,a in enumerate(novel): mm[19+j]=a
mm.flush()
class Stack:
    def __getitem__(self,j): return mm[j]
X=mm; FEATS=names19+novel_names
log(f"stack {X.shape} memmap")
rng=np.random.default_rng(31026)
# ---- EXP-1 canary: novel feature AUC vs catalogue on footprint sample
sample_idx=np.flatnonzero(fp.ravel()); sel=rng.choice(sample_idx,size=400000,replace=False)
y=cat.ravel()[sel]; canary={}
for j,nm in enumerate(novel_names):
    v=np.asarray(X[19+j]).ravel()[sel]; auc=float(roc_auc_score(y,v)); canary[nm]=max(auc,1-auc)
log(f"canary {canary}")
assert max(canary.values())<=0.90, "LEAKAGE CANARY STOP"

def train_predict(train_mask, feat_idx):
    pos=np.flatnonzero((cat&train_mask).ravel()); negc=np.flatnonzero((fp&train_mask&~cat).ravel())
    neg=rng.choice(negc,size=min(200000,len(negc)),replace=False); tr=np.concatenate([pos,neg])
    Xtr=np.stack([np.asarray(X[j]).ravel()[tr] for j in feat_idx],1); ytr=cat.ravel()[tr].astype(int)
    m=HistGradientBoostingClassifier(max_iter=140,learning_rate=0.08,max_leaf_nodes=31,min_samples_leaf=60,l2_regularization=2.0,early_stopping=False)
    m.fit(Xtr,ytr)
    return m
def predict(m,feat_idx):
    out=np.zeros(fp.shape,np.float32)
    for r0 in range(0,fp.shape[0],128):
        blk=np.stack([np.asarray(X[j][r0:r0+128]).reshape(-1) for j in feat_idx],1)
        out[r0:r0+128]=m.predict_proba(blk)[:,1].reshape(-1,fp.shape[1]).astype(np.float32)
    return out

# ---- EXP-2 holdout
arms={"xfcoh":list(range(29)),"base19":list(range(19))}
blocks={a:[] for a in arms}; surfaces={}
for fold in range(4):
    sp=ho.fold_split(cat,fp,fold); log(f"fold {fold} truth {sp['n_truth_pixels']}")
    for a,fi in arms.items():
        m=train_predict(sp["train_allowed"],fi); surf=predict(m,fi); surfaces[(a,fold)]=surf
        valid=sp["domain"]&~cat
        n_dots=int(round(37654*sp["domain"].sum()/fp.sum()))
        dots=emit_dots(surf,valid,max_dots=n_dots)
        blocks[a].append(ho.score_fold(dots.astype(float),cat,sp))
pooled={}
for a in arms:
    bs=blocks[a]; tp=sum(b["TPw"] for b in bs); fpw=sum(b["FPw"] for b in bs); fn=sum(b["FNw"] for b in bs); nt=sum(b["truth_pixels"] for b in bs)
    pooled[a]={"evidence_class":"HOLDOUT-DTI","evaluator_version":ho.EVALUATOR_ID,"dti":float(tp/(tp+0.2*fpw+0.8*fn)),"tpw":float(tp),"fpw":float(fpw),"fnw":float(fn),"withheld_positive_pixels":int(nt)}
    # block bootstrap CI
    allb=[]
    for b in bs: allb.extend(b["block_stats"] if isinstance(b["block_stats"],list) else [b["block_stats"]])
    pooled[a]["block_stats"]=allb
# paired bootstrap using per-block dicts if available
try:
    boot=ho.paired_block_bootstrap({a:[b["block_stats"] for b in blocks[a]] for a in arms},resamples=1000)
    pooled["_bootstrap"]=boot
except Exception as e:
    pooled["_bootstrap_error"]=str(e)
log(json.dumps({a:{k:v for k,v in pooled[a].items() if k!='block_stats'} for a in arms},indent=1))

# ---- EXP-3 final
m=train_predict(fp,list(range(29))); surf=predict(m,list(range(29)))
np.save(ROOT/".cache_xf_surf.npy",surf) if False else (ROOT/".cache").mkdir(exist_ok=True); np.save(ROOT/".cache/xfcoh31_surface.npy",surf.astype(np.float32))
dc=distance_transform_edt(~cat)
valid=fp&(dc>2)
dots=emit_dots(surf,valid,max_dots=37654)
pred=np.where(fp,dots.astype(np.float32),0.0).astype(np.float32)
name="gems31-xfcoh31-xfield-coherence-37654-20261026"
outdir=ROOT/"docs/downloads"; tif=outdir/f"{name}-zeros.tif"; nantif=outdir/f"{name}-nan.tif"
with rasterio.open(ROOT/"data/sample_submission.tif") as d: prof=d.profile.copy()
for path,arr in ((tif,pred),(nantif,np.where(fp,pred,np.nan).astype(np.float32))):
    p=dict(prof); p.update(dtype="float32",count=1,nodata=None) 
    with rasterio.open(path,"w",**p) as o: o.write(arr,1)
    with zipfile.ZipFile(path.with_suffix(".zip"),"w",zipfile.ZIP_DEFLATED) as z: z.write(path,path.name)
res={"canary":canary,"holdout":{a:{k:v for k,v in pooled[a].items() if k!='block_stats'} for a in arms},
 "bootstrap":pooled.get("_bootstrap"),"bootstrap_error":pooled.get("_bootstrap_error"),
 "dots":int(dots.sum()),"sha256_zeros":sha(tif),"sha256_nan":sha(nantif),
 "surface_sha256":hashlib.sha256(surf.tobytes()).hexdigest(),"file":str(tif.relative_to(ROOT))}
(ROOT/"evidence/xfcoh31_results.json").write_text(json.dumps(res,indent=1,default=str))
print("RESULT_JSON",json.dumps(res,indent=1,default=str)[:4000])
