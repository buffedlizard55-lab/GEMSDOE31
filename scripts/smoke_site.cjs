#!/usr/bin/env node
/* Optional real-browser checks. Install Playwright/packaged Chromium outside Git:
   npm install --prefix .cache/browser playwright-core @sparticuz/chromium
   NODE_PATH=.cache/browser/node_modules node scripts/smoke_site.cjs [base-url]
   Start a static server first. No credentials or competition interaction.
*/
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {chromium: playwright} = require('playwright-core');
const chromiumModule = require('@sparticuz/chromium');
const chromium = chromiumModule.default || chromiumModule;
const root = path.resolve(__dirname, '..');
const base = (process.argv[2] || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const card = JSON.parse(fs.readFileSync(path.join(root, 'evidence/tgj31/run_card.json')));

(async () => {
  // The packaged Lambda libraries also support minimal Linux sandboxes.
  if (chromiumModule.inflate && chromiumModule.setupLambdaEnvironment) {
    const bin = path.join(path.dirname(require.resolve('@sparticuz/chromium')), '../bin');
    await chromiumModule.inflate(path.join(bin, 'al2023.tar.br'));
    chromiumModule.setupLambdaEnvironment(path.join(require('node:os').tmpdir(), 'al2023/lib'));
  }
  const args = chromium.args.filter((arg) => !arg.startsWith('--disable-web-security') && !arg.startsWith('--allow-running-insecure-content'));
  const browser = await playwright.launch({args, executablePath: await chromium.executablePath(), headless: true});
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}, acceptDownloads: true});
  const page = await context.newPage();
  const errors = [];
  const checked = [];
  page.on('pageerror', (error) => errors.push(error.message));
  try {
    for (const target of ['', 'executive-summary.html', 'research.html', 'validation.html', 'sources.html', 'register/index.html', 'experiments/index.html', 'feed.html']) {
      const response = await page.goto(base + target, {waitUntil: 'networkidle'});
      assert.equal(response.status(), 200);
      assert.equal(await page.locator('body').getAttribute('data-safe-to-submit'), 'false');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, target + ' horizontal overflow');
      checked.push(target || 'index.html');
    }
    await page.waitForFunction(() => !document.querySelector('#feed-status').textContent.startsWith('Checking'), {timeout: 30000});
    const feedStatus = await page.locator('#feed-status').innerText();
    await page.goto(base, {waitUntil: 'networkidle'});
    const download = page.locator('a[download]').first();
    assert((await download.boundingBox()).y < 850, 'desktop download must be prominent');
    const waiting = page.waitForEvent('download');
    await download.click();
    const saved = await waiting;
    assert.equal(saved.suggestedFilename(), path.basename(card.files.tif));
    const bytes = fs.readFileSync(await saved.path());
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), card.raster_sha256);
    fs.mkdirSync(path.join(root, '.cache'), {recursive: true});
    await page.screenshot({path: path.join(root, '.cache/site-desktop.png'), fullPage: true});
    await page.setViewportSize({width: 390, height: 844});
    for (const target of ['', 'executive-summary.html', 'research.html', 'validation.html', 'register/index.html']) {
      await page.goto(base + target, {waitUntil: 'networkidle'});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'mobile ' + target + ' horizontal overflow');
    }
    await page.goto(base, {waitUntil: 'networkidle'});
    assert((await page.locator('a[download]').first().boundingBox()).y < 844, 'mobile download must appear in first viewport');
    await page.screenshot({path: path.join(root, '.cache/site-mobile.png'), fullPage: true});
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({checked_pages: checked, desktop: [1440, 1000], mobile: [390, 844],
      no_horizontal_overflow: true, one_click_download_sha256: card.raster_sha256,
      negative_status_visible: true, page_errors: errors, feed_status: feedStatus}, null, 1));
  } finally {
    await browser.close();
  }
})().catch((error) => {console.error(error); process.exitCode = 1;});
