# Executive summary — 2026-10-26 session `arena/f4d7fb29-gemsdoe31`

**H31-Y unique GeoTIFF generated. OK TO DOWNLOAD FOR RESEARCH: YES. OK TO SUBMIT: NO.**

Download: [`docs/downloads/gemsdoe31-h31y-kinpied-37654-20261026-46a5b6c3-zeros.tif`](../docs/downloads/gemsdoe31-h31y-kinpied-37654-20261026-46a5b6c3-zeros.tif)
(SHA-256 `6b06127f405eb6fb279e69bfc1645d01ab037d8b2f369933db0e06fa36199aa8`).
Portal name `gemsdoe31-h31y-kinpied-37654-20261026-46a5b6c3`. Note ≤140 chars on the run card.
All-finite float32 in `[0,1]` — cannot trigger `Predicted values must be in range [0, 1]`.

The **selector primary for a real weekly slot remains H31-X** (or whichever file `registry/selector_decision_20261026.json` lists after the re-run). This lane does not spend a slot.

## Why H33-2-B2 is 0.2778 USER-REPORTED (not a unique new entry)

H33-2-B2 = D2.8 Poisson ridge dots with every pixel ≤2 px of the public catalogue deleted (37,654 dots). Sibling ladder (USER-REPORTED, no organizer receipt): 60,069→0.2477, 44,090→0.2600, 40,199→0.2708, 37,654→0.2778. Mechanism (INFERENCE): hidden expert truth is depleted beside mapped faults; DTI α=0.2 charges each wasted FP. **Do not resubmit H33 or any >70% 3-px twin.** User-stated 0.4413 / 0.3195 remain unverified.

## This session's lane (H31-Y KIN-PIED)

Gravity-defined hanging-wall polarity splits LiDAR `downface_max` into synthetic (face basin) vs antithetic (face range), plus low-slope gravity HG. Winner **Y3 = SYNTH**. Complementary to H31-X junction (26% 3-px overlap).

| Item | Value | Label |
|---|---|---|
| HOLDOUT-DTI screen | 0.0973 [0.0833, 0.1106], n=60,988 | HOLDOUT-DTI `gems57-pooled-hide-v2` |
| vs CTRL / SLOPE | +0.0302 [+0.0048, +0.0536] / +0.0485; 3/4 quads | HOLDOUT-DTI paired |
| Confirmation | 0.0860 vs CTRL 0.0573, Δ +0.0287 [+0.0066, +0.0504], n=30,424 | HOLDOUT-DTI seed 3104 |
| Off-cat SGMC | 0.1188 vs H33 0.0940 (piedmont 0.020 vs 0.059) | COMPUTED proxy, not truth |
| PROJECTION | 0.348 [0.343, 0.354] | PROJECTION, never a score |
| Final-dot 3-px max | 63.0% (H3 LiDAR 50k); vs H33 24.8%; vs H31-X 26.0% | COMPUTED unique under 70% rule |
| Top-K 3-px | 90.5% | G5 FAIL (lane card) |
| Leakage canary | max AUC SLOPE 0.7565 ≤ 0.90 | COMPUTED |
| Format | EPSG:32611, 3730×3292, {0,1}, 0 on catalogue | G1 PASS |

**Verdict: negative** (G5). Negative result is a deliverable. ANTI/GRAVPIED lost the holdout (Y2 0.065, Y1 0.059 vs Y3 0.097). SYNTH is a mountain-front scarp polarity line — it does **not** fix H31-X's piedmont weakness.

## Nine-site table (USER-REPORTED claims; unique? = 3-px vs H33 ≤70%)

| Site | Highest listed claim | File to download from that site | Unique vs H33? | Submit as new? |
|---|---|---|---|---|
| GEMSDOE32 | 0.2778 | h33-h33-2-b2-…-zeros | 100% twin of D2.8 prune | NO |
| GEMSDOE36 | 0.2750 | anderson-geothermal-pinn-38854 | ~97% | NO |
| GEMSDOE28 | 0.2710 | h36-1-rung30-blind-r1 | ~95% | NO |
| GEMSDOE31 hist. | 0.2708 | h27-4-solo-d28 | ~95% | NO |
| GEMSDOE33 | 0.2632 | h33d-analog-tip-stepover-r30 | ~93% | NO |
| GEMSDOE25 | 0.2600 | dotted-h19-5-d2-8 | ~88% | NO |
| GEMSDOE30 | 0.2600 | d28-poisson300m-offcat-44090 | ~88% | NO |
| GEMSDOE24 | 0.2477 | h25-1-dotted-h19-5-d1-5 | ~88% | NO |
| GEMSDOE27 | 0.2449 | topo-gap-closure-t-v2-on-d1-5 | ~87% | NO |
| **This repo H31-Y** | no live score | `gemsdoe31-h31y-kinpied-37654-20261026-46a5b6c3-zeros.tif` | 24.8% vs H33 | **NO (G5)** |
| **Selector primary** | PROJECTION ~0.355 | H31-X zeros (see selector JSON) | 57% vs H33 | **YES if selector still lists it** |

## Ranked hypotheses (this session)

1. KIN-PIED (run) — SYNTH won holdout; ANTI/piedmont gravity lost; G5 top-K stop.
2. TEX RTP structure-tensor — not run (budget).
3. Lahontan ASL mask — blocked (`det_elev` is detrended).
4. InSAR — sandbox allowlist blocked.
5. X+Y ensemble — would likely duplicate H31-X.

## Limitations

No DrivenData auth, no organizer receipt, no weekly slot spent. Literal 695-lattice 3-px overlap ~99.7% for any nonempty raster. Proxy DTI ≠ live score.
