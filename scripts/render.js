// Renders a project's video.html frame by frame: window.render(t) for every frame, screenshots piped to ffmpeg.
// Extracted from the Shepherdr production (render.js).
//
//   studio render                          silent video, the whole duration → out/silent.mp4
//   studio render stills 3,12.5,30         PNG stills at those seconds → out/stills/
//   studio render range out.mp4 FROM DUR   one stretch, silent (add --query ?short for the social cut's card)
//   studio render --page cover.html …      another page of the project (default video.html)
//
// The picture is H.264 High, CRF 14, yuv420p, at the project's fps; the sound is added by `studio master`.
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { launch } = require('./browser');

const DIR = process.env.PROJECT_DIR || process.cwd();
const argv = process.argv.slice(2);
const opt = (name, def) => { const i = argv.indexOf(name); if (i < 0) return def; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const PAGE = opt('--page', 'video.html');
const QUERY = opt('--query', process.env.PAGE_QUERY || '');
const [mode = 'video', a1, a2, a3] = argv;

async function open() {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(DIR, PAGE) + QUERY);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.images].map(i => (i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))));
  const fps = await page.evaluate(() => (window.PROJECT && window.PROJECT.fps) || 30);
  return { browser, page, errors, fps };
}

function encoder(out, fps, frames) {
  fs.mkdirSync(path.dirname(path.resolve(DIR, out)), { recursive: true });
  return spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    // Screenshots are full-range JPEGs: convert to the standard limited range and tag the video BT.709, so platforms
    // that re-encode don't shift levels or colours (the Shepherdr masters went out full-range, tagged BT.601).
    '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-c:v', 'libx264', '-profile:v', 'high', '-crf', '14', '-preset', 'medium', '-tune', 'animation',
    '-frames:v', String(frames), '-r', String(fps), '-movflags', '+faststart', path.resolve(DIR, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
}

async function frames(page, ff, from, n, fps, log = true) {
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), from + i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (log && i % 150 === 0) process.stdout.write(`frame ${i} / ${n}\r`);
  }
  ff.stdin.end();
  const code = await new Promise(r => ff.on('close', r));
  if (code) throw new Error('ffmpeg failed');
}

(async () => {
  const { browser, page, errors, fps } = await open();
  if (mode === 'stills') {
    const dir = path.join(DIR, 'out/stills');
    fs.mkdirSync(dir, { recursive: true });
    for (const t of (a1 || '1').split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      const f = path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.png`);
      await page.screenshot({ path: f });
      console.log(path.relative(DIR, f));
    }
  } else if (mode === 'range') {
    const short = await page.evaluate(() => window.SHORT_CARD || null);
    const from = a2 === 'short' ? short.at : Number(a2), n = Math.round(Number(a3 || (short && short.len) || 3) * fps);
    await frames(page, encoder(a1, fps, n), from, n, fps, false);
    console.log(`wrote ${a1} (${n} frames from ${from.toFixed(2)} s)`);
  } else {
    const dur = await page.evaluate(() => window.DURATION);
    const out = a1 || 'out/silent.mp4';
    const n = Math.round(dur * fps);
    const t0 = Date.now();
    await frames(page, encoder(out, fps, n), 0, n, fps);
    console.log(`wrote ${out}: ${dur.toFixed(2)} s, ${n} frames at ${fps} fps, in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  const missing = await page.evaluate(() => (window.MISSING_CUES ? window.MISSING_CUES() : []));
  if (missing.length) console.log('MISSING CUES (their cuts are skipped):', missing.join(', '));
  if (errors.length) { console.log('PAGE ERRORS:', errors); process.exitCode = 1; }
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
