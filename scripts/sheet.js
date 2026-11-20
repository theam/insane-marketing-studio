// Contact sheets for review: one labelled tile per cut (or per given time), 4 across, as one PNG.
// Labels are drawn in HTML (ffmpeg from Homebrew has no drawtext), so the sheet reads: "#3 · 4.27 s · title".
//
//   studio sheet                       a still of every cut of video.html (40 % into it) → out/review/sheet.png
//   studio sheet out/final.mp4         frames of a finished video at every cut of the edit → out/review/sheet-final.png
//   studio sheet out/final.mp4 1,5,9   frames at those seconds
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
const { launch } = require('./browser');

const DIR = process.env.PROJECT_DIR || process.cwd();
const [video, times] = process.argv.slice(2);

(async () => {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const tmp = path.join(DIR, 'out/review/tiles');
  fs.rmSync(tmp, { recursive: true, force: true });
  fs.mkdirSync(tmp, { recursive: true });
  // The tiles: the edit's own cuts (from timing/points.json, else the page), or the given times.
  let tiles;
  const pts = path.join(DIR, 'timing/points.json');
  if (times) tiles = times.split(',').map(Number).map((t, i) => ({ t, label: `#${i + 1}` }));
  else {
    const P = fs.existsSync(pts) ? JSON.parse(fs.readFileSync(pts, 'utf8')) : null;
    if (!P) { console.error('run `studio points` first'); process.exit(1); }
    tiles = P.cuts.map((k, i) => {
      const end = P.cuts[i + 1] ? P.cuts[i + 1].t : P.duration;
      return { t: Math.min(k.t + 0.4 * (end - k.t), k.t + 1.2), cut: k.t, label: `#${i + 1}${k.label ? ' · ' + k.label : ''}` };
    });
  }
  if (!video) {
    await page.goto('file://' + path.join(DIR, 'video.html'));
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => Promise.all([...document.images].map(i => (i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))));
  }
  for (const [i, k] of tiles.entries()) {
    k.file = path.join(tmp, `${String(i).padStart(3, '0')}.jpg`);
    if (video) execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-ss', String(k.t), '-i', path.resolve(DIR, video), '-frames:v', '1', '-vf', 'scale=480:-2', '-q:v', '3', k.file]);
    else {
      await page.evaluate(t => window.render(t), k.t);
      await page.screenshot({ path: k.file, type: 'jpeg', quality: 80 });
    }
  }
  const html = `<html><body style="margin:0;background:#111;font:600 15px -apple-system,Helvetica,sans-serif;color:#eee">
<div style="display:grid;grid-template-columns:repeat(4,480px);gap:8px;padding:8px">${tiles.map(k => `<div><img src="file://${k.file}" style="width:480px;height:270px;object-fit:cover;display:block"><div style="padding:4px 2px">${k.label} · ${k.t.toFixed(2)} s</div></div>`).join('')}</div></body></html>`;
  const htmlFile = path.join(tmp, 'sheet.html');
  fs.writeFileSync(htmlFile, html);
  const sheet = await browser.newPage({ viewport: { width: 4 * 488 + 8, height: 600 } });
  await sheet.goto('file://' + htmlFile);
  await sheet.evaluate(() => Promise.all([...document.images].map(i => (i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))));
  const out = path.join(DIR, 'out/review', video ? `sheet-${path.basename(video, path.extname(video))}.png` : 'sheet.png');
  await sheet.screenshot({ path: out, fullPage: true });
  await browser.close();
  console.log(path.relative(DIR, out), `(${tiles.length} tiles)`);
})().catch(e => { console.error(e.message); process.exit(1); });
