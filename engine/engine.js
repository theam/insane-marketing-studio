// =====================================================================================================================
// Insane Marketing Studio: the motion engine.
//
// A video is one deterministic HTML page. render.js loads it in a headless browser, calls window.render(t) for every
// frame (t in seconds) and pipes the screenshots to ffmpeg. Nothing here may depend on wall-clock time or randomness
// that is not seeded: the same t must always draw the same frame.
//
// Every animation is placed on a narration cue: script.md marks words with {#name}; build_timing.js turns the voice's
// word timestamps into window.CUES / window.WORDS / window.CAPTIONS (timing.js). Change a line, re-run the voice and
// the timing, and everything re-times itself.
//
// Extracted from the INSANE Shepherdr infomercial (its video.html).
// Style files (infomercial.js, explainer.js) add backgrounds and building blocks on top of this core.
// =====================================================================================================================
const FPS = (window.PROJECT && window.PROJECT.fps) || 30;
const QUERY = new URLSearchParams(location.search);
const SHORT = QUERY.has('short');               // the social cut's call-to-action card is rendered with ?short
const CUES = window.CUES || {}, WORDS = window.WORDS || [], CAPTIONS = window.CAPTIONS || [];
const GEN = window.GEN || {};                    // generated clips extracted to frames (scripts/clip_frames.py)
const VISUAL_LEAD = 0.07;                        // things land 2 frames before their word: it reads as on time
let SHOW_CAPTIONS = true;

// ---------- cues ----------
const WORD_AT = {};
WORDS.forEach((w, i) => { if (w.cue) WORD_AT[w.cue] = i; });
const MISSING = new Set();
// Start of the word a {#cue} mark sits on (minus the visual lead). NaN if the script lost the cue: the cut is skipped.
function cue(name) {
  const v = CUES[name];
  if (v == null) { if (!MISSING.has(name)) { MISSING.add(name); console.warn('missing cue (cut skipped): ' + name); } return NaN; }
  return v - VISUAL_LEAD;
}
const c = cue;
// Start (or end, with end=true) of the k-th word after a cue.
function W(name, k = 0, end = false) {
  const i = WORD_AT[name];
  if (i == null) return cue(name) + 0.3 * k;
  const w = WORDS[Math.min(WORDS.length - 1, i + k)];
  return (end ? w.e : w.s) - VISUAL_LEAD;
}
window.MISSING_CUES = () => [...MISSING];

// ---------- helpers ----------
const $ = id => document.getElementById(id);
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, p) => a + (b - a) * p;
const prog = (t, a, b) => (b <= a ? (t >= b ? 1 : 0) : clamp((t - a) / (b - a)));
const E = {
  out: p => 1 - Math.pow(1 - p, 3),
  inOut: p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  back: p => 1 + 2.70158 * Math.pow(p - 1, 3) + 1.70158 * Math.pow(p - 1, 2),
};
const ease = (t, at, dur = 0.3, f = E.out) => f(prog(t, at, at + dur));
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function mk(tag, cls, parent, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
// Centre an element on (x, y) with a scale, an opacity and a rotation in degrees.
function place(e, x, y, s = 1, o = null, r = 0) {
  e.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) rotate(${r}deg) scale(${s})`;
  if (o != null) e.style.opacity = o;
}
// Things appear on their word in a 2-frame step (overshoot, then settle): punchy, no smooth easing.
const settle = (t, at) => (t < at ? 0 : t < at + 1 / FPS ? 1.12 : t < at + 2 / FPS ? 1.05 : 1);
const drift = (t, a, b) => 1 + 0.04 * prog(t, a, b);   // a slow push while a cut holds
const stepS = s => Math.round(s * 40) / 40;           // scales snapped to 1/40 steps: "pixel stepped" motion

// ---------- images ----------
// A cut-out: a bare name is the project's own assets/cutouts/<name>.png; 'kit:<name>' is one of the kit's starter
// cut-outs in engine/cutouts/ (see engine/cutouts/CREDITS.md); a path with a slash or a dot is used as it is.
function src(name, dir = 'cutouts', ext = 'png') {
  if (name.startsWith('kit:')) return `engine/cutouts/${name.slice(4)}.png`;
  return name.includes('/') || name.includes('.') ? name : `assets/${dir}/${name}.${ext}`;
}
function sprite(el, name, w, cls = 'obj') { const e = mk('img', cls, el); e.src = src(name); e.style.width = w + 'px'; return e; }
// A full-bleed plate (assets/plates/<name>.png), drawn bigger than the frame so it can push in.
function plate(el, name) { const e = mk('img', 'plate', el); e.src = src(name, 'plates'); return e; }
function kenBurns(e, t, a, b, z0 = 1.03, z1 = 1.12, dx = 0, dy = 0) {
  const p = prog(t, a, b);
  e.style.transform = `translate(-50%, -50%) translate(${dx * p}px, ${dy * p}px) scale(${lerp(z0, z1, p)})`;
}

// ---------- sound landmarks for the mix (scripts/dump_points.js → timing/points.json → scripts/mix.py) ----------
const SFX = [], AUDIO = [];
// A sound effect of a kind from the project's sfx.json at time `at`.
function sfx(at, kind) { if (Number.isFinite(at)) SFX.push({ t: Math.round(at * 1000) / 1000, kind }); }
// Any other audio file placed by the edit: a song, a line from a generated clip, a jingle.
// opts: { from, to (seconds inside the file), gain (dB), filter (ffmpeg audio filter), fadeIn, fadeOut, bed (true: ducks under the voice) }
function audio(at, file, opts = {}) { if (Number.isFinite(at)) AUDIO.push({ t: Math.round(at * 1000) / 1000, file, ...opts }); }
// Music cues the mix applies to the bed: stop it dead on a gag, or mute it for a while.
const MUSIC_EVENTS = [];
function musicStop(at) { if (Number.isFinite(at)) MUSIC_EVENTS.push({ t: at, type: 'stop' }); }
function musicMute(a, b) { if (Number.isFinite(a) && Number.isFinite(b)) MUSIC_EVENTS.push({ t: a, end: b, type: 'mute' }); }
window.SFX_POINTS = () => SFX.slice().sort((a, b) => a.t - b.t);
window.AUDIO_EVENTS = () => AUDIO.slice().sort((a, b) => a.t - b.t);
window.MUSIC_EVENTS = () => MUSIC_EVENTS.slice().sort((a, b) => a.t - b.t);

// ---------- global hits: zoom punches and flashes ----------
const PUNCH = [], FLASH = [], CALM = [];               // CALM: [a, b] spans where shouted words don't punch
const ACRONYMS = new Set(['AI', 'QA', 'UI', 'API', 'TV', 'OK', 'CEO', 'CTA']);
function shouted(w) { const L = w.replace(/[^A-Za-z]/g, ''); return L.length >= 2 && L === L.toUpperCase() && !ACRONYMS.has(L); }
// Every narrator word written in CAPITALS in the script punches the frame (unless inside a CALM span).
function buildHits(amp = 1) {
  WORDS.forEach(w => {
    if (w.sp !== 'n' || !shouted(w.w)) return;
    const t = w.s - VISUAL_LEAD;
    if (CALM.some(([a, b]) => t >= a && t < b)) return;
    PUNCH.push({ t, amp });
  });
}
function globalShake(t) {
  let z = 0, x = 0, y = 0;
  const R = rng(Math.floor(t * FPS) + 7);
  for (const h of PUNCH) {
    const d = t - h.t;
    if (d < 0 || d > 0.25) continue;
    const k = h.amp * (d < 0.1 ? 1 : 0.4);
    z += 0.03 * k; x += Math.round((R() - 0.5) * 4) * 4 * k; y += Math.round((R() - 0.5) * 4) * 4 * k; // 4 px steps
  }
  return { z, x, y };
}
const flashAt = t => FLASH.reduce((o, f) => { const d = t - f.t; return d >= 0 && d < 0.2 ? Math.max(o, f.amp * (d < 0.07 ? 1 : 0.4)) : o; }, 0);

// ---------- cuts ----------
// A cut is shown from its start until the next cut starts. bg names a background a style registered (BACKGROUNDS).
// build(el, cut) makes its elements once and returns its state; draw(state, t, start, end) poses them for frame t.
// opts: { bgAt: t => bg (switch background mid-cut), freeze (background stops), stageRot: (t,a,b) => {deg, zoom}, noScan, noCaps }
const CUTS = [];
function cut(at, bg, build, draw = () => {}, opts = {}) {
  if (!Number.isFinite(at)) return { el: document.createElement('div'), st: {} }; // its cue is gone from the script
  const el = mk('div', 'cut', $('stage'));
  const k = { at, bg, el, draw, ...opts };
  k.st = build(el, k) || {};
  CUTS.push(k);
  return k;
}
window.CUT_TIMES = () => CUTS.map(k => Math.round(k.at * 1000) / 1000);
// For the storyboard: every cut's start and its label (opts.label, else the cue name it was built on).
window.CUT_LIST = () => CUTS.map(k => ({ t: Math.round(k.at * 1000) / 1000, label: k.label || '' }));

// ---------- backgrounds ----------
// A style registers draw functions by name. A canvas background draws on the 480×270 #bg canvas (blown up 4× with hard
// pixels); a DOM background toggles a class on #set. 'none' shows nothing (a cut that fills the frame itself).
const BACKGROUNDS = {};
const bg = $('bg'), g = bg.getContext('2d');
g.imageSmoothingEnabled = false;
const set = $('set');

// ---------- generated clips (Seedance takes) ----------
// A slot plays assets/gen/<shot>/NNN.jpg (scripts/clip_frames.py) once GEN[shot] lists it; until then, its first-frame
// plate (assets/gen/plates/<plate or shot>.png) with a slow push and a PENDING tag, so the cut still reads.
function genSlot(el, shot, { plate: pl, still } = {}) {
  const box = mk('div', 'gen', el);
  const img = mk('img', '', box);
  const live = !still && GEN[shot];
  img.src = live ? `assets/gen/${shot}/000.jpg` : `assets/gen/plates/${pl || shot}.png`;
  if (!live && !still) mk('div', 'tag', box, `GENERATED SHOT PENDING · ${shot}`);
  return { box, img, live, shot };
}
const PENDING = [];   // a frame that changes source is decoded before render() resolves: no blank captures
function drawGen(s, t, a) {
  if (s.live) {
    const k = Math.max(0, Math.min(s.live.frames - 1, Math.floor((t - a) * (s.live.fps || FPS))));
    const f = `assets/gen/${s.shot}/${String(k).padStart(3, '0')}.jpg`;
    if (s.img.getAttribute('src') !== f) { s.img.setAttribute('src', f); PENDING.push(s.img.decode().catch(() => {})); }
    s.img.style.transform = 'translate(-50%, -50%)';
  } else s.img.style.transform = `translate(-50%, -50%) scale(${1 + 0.04 * prog(t, a, a + 4)})`;
}
// Corner-pin: a CSS matrix3d that maps a w×h box onto a quad [[TL],[TR],[BR],[BL]] (scripts/cornerpin.py tracks one).
function quadMatrix(w, h, q) {
  const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = q;
  const dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3, dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1;
  const gg = (dx3 * dy2 - dx2 * dy3) / den, hh = (dx1 * dy3 - dx3 * dy1) / den;
  const a = x1 - x0 + gg * x1, b = x3 - x0 + hh * x3, d = y1 - y0 + gg * y1, e = y3 - y0 + hh * y3;
  const H = [a / w, b / h, x0, d / w, e / h, y0, gg / w, hh / h, 1];
  return `matrix3d(${H[0]},${H[3]},0,${H[6]},${H[1]},${H[4]},0,${H[7]},0,0,1,0,${H[2]},${H[5]},0,${H[8]})`;
}
// A screen pinned into a generated clip: pins `el` (w×h px) onto the tracked quad for frame k (cover-fitted to 1920×1080).
function pinTo(el, w, h, track, t, a) {
  const k = Math.max(0, Math.min(track.quads.length - 1, Math.floor((t - a) * FPS)));
  const [sw, sh] = track.src, z = Math.max(1920 / sw, 1080 / sh);
  const q = track.quads[k].map(([x, y]) => [960 + (x - sw / 2) * z, 540 + (y - sh / 2) * z]);
  el.style.transformOrigin = '0 0';
  el.style.transform = quadMatrix(w, h, q);
}

// ---------- the ending ----------
// Every video ends on full black held for at least 15 frames (the director: never end mid-fade). setEnding() is called by
// the page with the time its last cut (the end card) starts and how long it holds; the fade and the black follow.
const END = { at: null, hold: 4, fade: 0.8, black: 0.6 };
function setEnding(at, hold = 4, fade = 0.8, black = 0.6) {
  Object.assign(END, { at, hold, fade, black: Math.max(black, 15 / FPS) });
  window.DURATION = at + hold + END.black;
}
window.END_INFO = () => ({ ...END });
// The social cut's call-to-action card: drawn after the film's end, only when the page is opened with ?short, so the
// long video never changes. Call after setEnding(): shortCard(3.5, at => endCard(at, 'green', {...})). The card fades
// to black and holds black for its last 0.6 s too. `studio short` renders it (render.js range … short).
let SHORT_CARD = null;
function shortCard(len, make) {
  if (!SHORT) return;
  SHORT_CARD = { at: Math.ceil(window.DURATION) + 2, len };
  window.SHORT_CARD = SHORT_CARD;
  make(SHORT_CARD.at);
}
window.DURATION = window.DURATION || 10;

// ---------- overlays a style adds (explosions, scanlines…) ----------
const OVERLAYS = [];

// ---------- frame ----------
function render(t) {
  let cur = null;
  for (const k of CUTS) if (t >= k.at) cur = k;
  for (const k of CUTS) k.el.style.display = k === cur ? 'block' : 'none';
  let rot = null;
  if (cur) {
    const i = CUTS.indexOf(cur), next = CUTS[i + 1] ? CUTS[i + 1].at : window.DURATION;
    const name = cur.bgAt ? cur.bgAt(t) : cur.bg;
    const B = BACKGROUNDS[name];
    bg.style.display = B && B.canvas ? 'block' : 'none';
    set.className = B && B.dom ? B.dom : '';
    if (B && B.draw) B.draw(cur.freeze ? cur.at : t, cur, name);
    cur.draw(cur.st, t, cur.at, next);
    if (cur.stageRot) rot = cur.stageRot(t, cur.at, next);
  }
  const k = globalShake(t);
  $('stage').style.transform = `translate(${k.x}px, ${k.y}px) rotate(${rot ? rot.deg : 0}deg) scale(${1 + k.z + (rot ? rot.zoom : 0)})`;
  OVERLAYS.forEach(f => f(t, cur));
  const scan = $('scan'); if (scan) scan.style.opacity = cur && cur.noScan ? 0 : 1;   // no CRT lines on live-action footage
  $('flash').style.opacity = flashAt(t) * 0.85;
  const caps = $('caps');
  const cp = SHOW_CAPTIONS && !(cur && cur.noCaps) && CAPTIONS.find(x => t >= x.start - 0.05 && t < x.end);
  if (cp) {
    caps.textContent = cp.text;
    caps.className = cp.speaker && cp.speaker !== 'narrator' ? 'sp-' + cp.speaker : '';
    caps.style.opacity = 1;
  } else caps.style.opacity = 0;
  // The end: fade to full black, then hold black.
  const fadeAt = END.at == null ? Infinity : END.at + END.hold - END.fade;
  $('fade').style.opacity = SHORT_CARD && t >= SHORT_CARD.at ? prog(t, SHORT_CARD.at + SHORT_CARD.len - 1.1, SHORT_CARD.at + SHORT_CARD.len - 0.6)
    : prog(t, fadeAt, fadeAt + END.fade);
  if (PENDING.length) return Promise.all(PENDING.splice(0));
}
window.render = render;
// Call once, after every cut is defined.
function ready() {
  CUTS.sort((a, b) => a.at - b.at);
  if (END.at == null) console.warn('setEnding() was not called: the video will not end on black');
  render(0);
}
