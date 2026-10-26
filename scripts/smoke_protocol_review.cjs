// Optional browser regression: local preview only; never contacts DrivenData.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium: playwright } = require('../.cache/browser/node_modules/playwright-core');
const ROOT = path.resolve(__dirname, '..');
const base = process.env.SITE_BASE_URL || 'http://127.0.0.1:8000';
const card = JSON.parse(fs.readFileSync(path.join(ROOT, 'evidence/review_9883b598/run_card.json')));
const assert = (v, m) => { if (!v) throw new Error(m); };
(async () => {
  const result = {scope: 'local preview only, not public deployment', pages: [], downloads: [], errors: []};
  const { default: chromium } = await import('../.cache/browser/node_modules/@sparticuz/chromium/build/index.js');
  const { inflate } = await import('../.cache/browser/node_modules/@sparticuz/chromium/build/lambdafs.js');
  const libs = await inflate(path.join(ROOT, '.cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  process.env.LD_LIBRARY_PATH = path.join(libs, 'lib') + ':' + (process.env.LD_LIBRARY_PATH || '');
  const browser = await playwright.launch({args: chromium.args, executablePath: await chromium.executablePath(), headless: true});
  try {
    const page = await browser.newPage({acceptDownloads: true});
    await page.route('**/*', r => new URL(r.request().url()).origin === new URL(base).origin ? r.continue() : r.abort());
    page.on('pageerror', e => result.errors.push(e.message));
    for (const width of [390, 820, 1440]) {
      await page.setViewportSize({width, height: 1000});
      for (const file of ['index.html', 'executive-summary.html']) {
        const response = await page.goto(`${base}/${file}`, {waitUntil: 'networkidle'});
        assert(response.ok(), `${file} HTTP ${response.status()}`);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
        assert(!overflow, `${file}: viewport overflow at ${width}`);
        const text = (await page.locator('body').innerText()).replaceAll('NOT OK TO SUBMIT', 'DO NOT SUBMIT');
        assert(text.includes('DO NOT SUBMIT'), 'missing STOP');
        assert(!text.includes('OK TO SUBMIT') && !text.includes('SUBMIT THIS FILE'), 'stale approval');
        const pending = page.waitForEvent('download');
        await page.getByRole('link', {name: 'Download existing H31-X research .tif — DO NOT SUBMIT', exact: true}).click();
        const download = await pending;
        const filePath = await download.path();
        assert(!await download.failure(), 'download failure');
        const hash = crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
        assert(hash === card.raster_sha256, 'download hash mismatch');
        result.pages.push({file, width, no_overflow: true, status: response.status()});
        result.downloads.push({file, width, sha256: hash});
      }
    }
    assert(!result.errors.length, 'browser errors');
    fs.writeFileSync(path.join(ROOT, 'evidence/review_9883b598/browser_checks.json'), JSON.stringify(result, null, 2) + '\n');
    console.log('PASS: 6 responsive page visits and 6 exact-hash research downloads');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
