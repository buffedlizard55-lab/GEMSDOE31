/* Public metadata only: no authentication, leaderboard polling, or submission actions. */
(async () => {
  const state = document.getElementById('feed-status');
  const panel = document.getElementById('source-health');
  if (!state || !panel) return;
  const fetchJSON = async (url) => {
    const options = {credentials: 'omit'};
    if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') {
      options.signal = AbortSignal.timeout(15000);
    }
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  };
  try {
    const feed = await fetchJSON('feed.json');
    const published = await fetchJSON('source-health.json').catch(() => null);
    const targets = feed.public_sources;
    if (!Array.isArray(targets) || !targets.length) throw new Error('public GitHub source targets are missing from feed.json');
    const targetKey = targets.map((source) => `${source.repo}@${source.pin}`).join('|');
    const key = `gems31-source-status-v3-${targetKey}`;
    let cached = null;
    try { cached = JSON.parse(localStorage.getItem(key)); } catch (_) { /* storage is optional */ }
    let checks;
    let fromCache = false;
    if (cached && Array.isArray(cached.checks) && cached.checks.length === targets.length
        && Number.isFinite(cached.at) && cached.at <= Date.now() && Date.now() - cached.at < 3600000) {
      checks = cached.checks;
      fromCache = true;
    } else {
      checks = await Promise.all(targets.map(async (source) => {
        try {
          const commits = await fetchJSON(`https://api.github.com/repos/${source.repo}/commits?per_page=1`);
          if (!Array.isArray(commits) || !commits[0]?.sha) throw new Error('unexpected response');
          const head = commits[0];
          return {...source, ok: true, current: head.sha, date: head.commit?.committer?.date || 'unknown'};
        } catch (error) { return {...source, ok: false, error: error.message}; }
      }));
      cached = {at: Date.now(), checks};
      try { localStorage.setItem(key, JSON.stringify(cached)); } catch (_) { /* no storage required */ }
    }
    const browserCount = checks.filter((row) => row.ok).length;
    const snapshotByRepo = new Map((published?.checks || []).map((row) => [row.repo, row]));
    checks = checks.map((row) => {
      if (row.ok) return row;
      const snapshot = snapshotByRepo.get(row.repo);
      if (snapshot?.ok) {
        return {...snapshot, fromSnapshot: true, snapshotChecked: published.checked_utc};
      }
      return row;
    });
    const available = checks.filter((row) => row.ok).length;
    const browserTime = new Date(cached.at).toISOString();
    const snapshotTime = published?.checked_utc || 'unavailable';
    const browserLabel = fromCache ? 'cached browser metadata responses' : 'fresh browser metadata responses';
    state.textContent = `${available}/${checks.length} repository HEAD records available; browser check ${browserTime} (${browserCount}/${checks.length} ${browserLabel}). Dated snapshot: ${snapshotTime}. No live score is known.`;
    for (const row of checks) {
      const box = document.createElement('div'); box.className = 'health-row'; box.setAttribute('role', 'listitem');
      const anchor = document.createElement('a'); anchor.textContent = row.repo;
      anchor.href = `https://github.com/${row.repo}`;
      const detail = document.createElement('small');
      const pinShort = row.pin?.slice(0, 12) || 'missing';
      if (row.ok && row.fromSnapshot) {
        detail.textContent = `Published snapshot HEAD: ${row.current.slice(0, 12)} (${row.date}); audited pin: ${pinShort}; snapshot checked ${row.snapshotChecked}; ${row.current === row.pin ? 'same commit' : 'differs — not re-audited; results unchanged'}.`;
      } else if (row.ok) {
        detail.textContent = `Public HEAD at browser check: ${row.current.slice(0, 12)} (${row.date}); audited pin: ${pinShort}; ${row.current === row.pin ? 'same commit' : 'differs — not re-audited; results unchanged'}.`;
      } else {
        detail.textContent = `Unverified: ${row.error}. No current-source or leaderboard claim made.`;
      }
      box.append(anchor, detail); panel.appendChild(box);
    }
  } catch (error) {
    state.textContent = `Source status unavailable (${error.message}). Frozen audit files remain accessible; no current external verification is claimed.`;
  }
})();
