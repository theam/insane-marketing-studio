// Renders a cover page to the video's cover image: a PNG, plus a JPEG under 5 MB for X's image limit.
// Extracted from the Shepherdr production (render-cover.js). Covers are HTML like the video: same fonts, cut-outs and blocks.
//
//   studio cover [cover.html] [out/cover]       → out/cover.png, out/cover.jpg
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
const { launch } = require('./browser');

(async () => {
  const DIR = process.env.PROJECT_DIR || process.cwd();
  const html = process.argv[2] || 'cover.html', out = path.resolve(DIR, process.argv[3] || 'out/' + path.basename(html, '.html'));
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(DIR, html));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0), null, { timeout: 15000 }).catch(() => console.log('an image did not load'));
  if (await page.evaluate(() => typeof window.render === 'function')) await page.evaluate(() => window.render(window.COVER_T || 0));
  await page.screenshot({ path: `${out}.png` });
  await browser.close();
  for (const q of [90, 80, 70, 60]) {
    execFileSync('sips', ['-s', 'format', 'jpeg', '-s', 'formatOptions', String(q), `${out}.png`, '--out', `${out}.jpg`], { stdio: 'ignore' });
    if (fs.statSync(`${out}.jpg`).size < 5e6) break;
  }
  console.log(`${path.relative(DIR, out)}.png, ${path.relative(DIR, out)}.jpg (${(fs.statSync(`${out}.jpg`).size / 1e6).toFixed(1)} MB)`);
})().catch(e => { console.error(e.message); process.exit(1); });
