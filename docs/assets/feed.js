/* Public metadata only: no authentication, leaderboard polling, or submission actions. */
(async () => {
  const state = document.getElementById('feed-status');
  const panel = document.getElementById('source-health');
  if (!state || !panel) return;
  const fetchJSON = async (url) => {
    const response = await fetch(url, {signal: AbortSignal.timeout(15000), credentials: 'omit'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  };
  try {
    const feed = await fetchJSON('feed.json');
    const published = await fetchJSON('source-health.json').catch(() => null);
    const key = `gems31-source-status-v2-${feed.last_scientific_run_utc}`;
    let cached = null;
    try { cached = JSON.parse(localStorage.getItem(key)); } catch (_) { /* storage is optional */ }
    let checks;
    if (cached && Array.isArray(cached.checks) && Date.now() - cached.at < 3600000) {
      checks = cached.checks;
    } else {
      checks = await Promise.all(feed.public_sources.map(async (source) => {
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
    let mode = 'browser checks';
    let at = new Date(cached.at).toISOString();
    if (checks.every((row) => !row.ok) && published?.verified_count > 0 && Array.isArray(published.checks)) {
      checks = published.checks;
      at = published.checked_utc;
      mode = 'published snapshot checks (browser checks unavailable; snapshot is dated, not live)';
    }
    const good = checks.filter((row) => row.ok).length;
    state.textContent = `${good}/${checks.length} ${mode} succeeded. Checked ${at}. Scientific results remain frozen; no live score is known.`;
    for (const row of checks) {
      const box = document.createElement('div'); box.className = 'health-row';
      const anchor = document.createElement('a'); anchor.textContent = row.repo;
      anchor.href = `https://github.com/${row.repo}`;
      const detail = document.createElement('small');
      detail.textContent = row.ok
        ? `Public HEAD at check: ${row.current.slice(0, 12)} (${row.date}); ${row.current === row.pin ? 'same as audited pin' : 'differs from audited pin — not re-audited; results unchanged'}.`
        : `Unverified: ${row.error}. No source-health or leaderboard claim made.`;
      box.append(anchor, detail); panel.appendChild(box);
    }
  } catch (error) {
    state.textContent = `Source status unavailable (${error.message}). Frozen audit files remain accessible; no current external verification is claimed.`;
  }
})();
