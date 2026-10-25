// Optional local browser smoke test. Browser tooling lives in ignored .cache/.
// npm install --prefix .cache/browser --ignore-scripts playwright-core@1.64.1 @sparticuz/chromium@153.0.0
// Start the static docs server, then: node scripts/smoke_current_site.cjs
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium: playwright } = require('../.cache/browser/node_modules/playwright-core');
const ROOT = path.resolve(__dirname, '..');
const base = process.env.SITE_BASE_URL || 'http://127.0.0.1:8000';
const card = JSON.parse(fs.readFileSync(path.join(ROOT, 'registry/current_run.json')));
const scratch = path.join(ROOT, 'work/browser-magrest');
fs.mkdirSync(scratch, { recursive: true });
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const assert = (v, m) => { if (!v) throw new Error(m); };

(async () => {
  let browser;
  const result = {
    checked_utc: new Date().toISOString(), scope: 'Local static preview, not public Pages HTTP or organizer access',
    no_fit_candidate_or_submission: true, viewports: [], downloads: [], errors: []
  };
  try {
    const { default: chromium } = await import('../.cache/browser/node_modules/@sparticuz/chromium/build/index.js');
    const { inflate } = await import('../.cache/browser/node_modules/@sparticuz/chromium/build/lambdafs.js');
    const libs = await inflate(path.join(ROOT, '.cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    process.env.LD_LIBRARY_PATH = path.join(libs, 'lib') + ':' + (process.env.LD_LIBRARY_PATH || '');
    result.tool_versions = { playwright_core: '1.64.1', chromium: '153.0.0' };
    browser = await playwright.launch({ args: chromium.args, executablePath: await chromium.executablePath(), headless: true });
    const page = await browser.newPage({ acceptDownloads: true });
    await page.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    page.on('pageerror', e => result.errors.push(e.message));
    for (const viewport of [{ width: 1440, height: 1000 }, { width: 820, height: 1180 }, { width: 390, height: 844 }]) {
      await page.setViewportSize(viewport);
      for (const file of ['index.html', 'executive-summary.html', 'research.html', 'sources.html', 'register/index.html']) {
        const response = await page.goto(`${base}/${file}`, { waitUntil: 'networkidle' });
        assert(response.ok(), `${file} HTTP ${response.status()}`);
        const width = await page.evaluate(() => document.documentElement.scrollWidth);
        assert(width <= viewport.width + 1, `${file} horizontal viewport overflow: ${width} > ${viewport.width}`);
        const text = await page.locator('body').innerText();
        if (file === 'index.html') {
          assert(text.includes('DO NOT SUBMIT') && text.includes('100% overlap'), 'current STOP not prominent');
          assert(await page.getByRole('link', { name: 'Download new research TIFF', exact: true }).first().isVisible(), 'download action not visible');
          await page.screenshot({ path: path.join(scratch, `home-${viewport.width}.png`), fullPage: true });
        }
        if (file === 'executive-summary.html') {
          assert(text.includes('ok_to_submit: true') && text.includes('Today it says false'), 'conditional workflow/status missing');
          await page.screenshot({ path: path.join(scratch, `executive-${viewport.width}.png`), fullPage: true });
        }
        result.viewports.push({ width: viewport.width, page: file, http_status: response.status(), no_horizontal_page_overflow: true });
      }
      await page.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
      for (const [key, label] of [['file', 'Download new research TIFF'], ['zip_file', 'One-TIFF ZIP']]) {
        const pending = page.waitForEvent('download');
        await page.getByRole('link', { name: label, exact: true }).first().click();
        const download = await pending;
        const target = path.join(scratch, `${viewport.width}-${download.suggestedFilename()}`);
        await download.saveAs(target);
        assert(!await download.failure(), 'browser download failed');
        const actual = sha(fs.readFileSync(target));
        const expected = sha(fs.readFileSync(path.join(ROOT, card[key])));
        assert(actual === expected, 'browser did not download the reviewed bytes');
        result.downloads.push({ width: viewport.width, file: download.suggestedFilename(), sha256: actual, exact_disk_bytes: true });
      }
    }
    assert(result.errors.length === 0, 'browser runtime errors');
    result.passed = true;
  } catch (e) {
    result.passed = false;
    result.errors.push(e.stack || String(e));
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    fs.writeFileSync(path.join(ROOT, 'evidence/browser_magrest_smoke_20261025.json'), JSON.stringify(result, null, 1) + '\n');
    console.log(JSON.stringify(result, null, 1));
  }
})();
