// Dumps the edit's landmarks from video.html to timing/points.json: sound effects, other audio events, music events,
// cut times and labels, the duration and any cue the script lost. Run after every change to video.html or timing.js.
//
//   studio points [page.html]      (default video.html)
const path = require('path');
const fs = require('fs');
const { launch } = require('./browser');

(async () => {
  const DIR = process.env.PROJECT_DIR || process.cwd();
  const page_ = process.argv[2] || 'video.html';
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(DIR, page_));
  const out = await page.evaluate(() => ({
    duration: window.DURATION,
    end: window.END_INFO ? window.END_INFO() : null,
    sfx: window.SFX_POINTS ? window.SFX_POINTS() : [],
    audio: window.AUDIO_EVENTS ? window.AUDIO_EVENTS() : [],
    music: window.MUSIC_EVENTS ? window.MUSIC_EVENTS() : [],
    cuts: window.CUT_LIST ? window.CUT_LIST() : [],
    missing_cues: window.MISSING_CUES ? window.MISSING_CUES() : [],
  }));
  fs.mkdirSync(path.join(DIR, 'timing'), { recursive: true });
  fs.writeFileSync(path.join(DIR, 'timing/points.json'), JSON.stringify(out, null, 1));
  console.log(`${out.cuts.length} cuts, ${out.sfx.length} sound effects, ${out.audio.length} audio events; duration ${out.duration.toFixed(2)} s`);
  if (out.missing_cues.length) console.log('MISSING CUES (their cuts are skipped):', out.missing_cues.join(', '));
  if (errors.length) { console.log('PAGE ERRORS:', errors); process.exitCode = 1; }
  await browser.close();
})();
