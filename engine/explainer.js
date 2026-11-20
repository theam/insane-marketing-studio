// =====================================================================================================================
// The calm explainer style: from the Shepherdr corporate explainer. Same engine, same cues, a quieter grammar:
// cuts dip in from black, a typed monospace headline with one accent word, a real screenshot in a window that the
// camera pans across, a frame that highlights one region, chips, stat tiles and a logo end card. No shakes, no punches.
// Load after engine.js.
// =====================================================================================================================
BACKGROUNDS.dark = { canvas: true, draw: () => { g.fillStyle = '#0a0d0c'; g.fillRect(0, 0, 480, 270); } };
// A faint dot grid that drifts, for cuts without a screenshot.
BACKGROUNDS.grid = { canvas: true, draw: t => {
  g.fillStyle = '#0a0d0c'; g.fillRect(0, 0, 480, 270);
  g.fillStyle = 'rgba(75,227,138,0.10)';
  const o = (t * 3) % 16;
  for (let y = -16; y < 286; y += 16) for (let x = -16; x < 496; x += 16) g.fillRect(Math.round(x + o), Math.round(y + o / 2), 1, 1);
} };
BACKGROUNDS.none = {};
bg.style.imageRendering = 'auto';

// Every cut dips in from black over 0.3 s (calm: no hard pops).
OVERLAYS.push((t, cur) => { if (cur) cur.el.style.opacity = cur.hard ? 1 : ease(t, cur.at, 0.3, E.inOut); });

// A headline typed in letter by letter from `at` (cps characters a second). html may carry <em>accent</em>.
function headline(el, html, { top = 52, size = 46 } = {}) {
  const e = mk('div', 'head', el); e.style.top = top + 'px'; e.style.fontSize = size + 'px';
  const plain = html.replace(/<[^>]+>/g, '');
  return { e, html, plain };
}
function drawHeadline(h, t, at, cps = 38) {
  const n = Math.max(0, Math.floor((t - at) * cps));
  if (n >= h.plain.length) { h.e.innerHTML = h.html; return; }
  // Type through the html, counting only visible characters, so the accent span stays intact.
  let out = '', k = 0;
  for (const part of h.html.split(/(<[^>]+>)/)) {
    if (part.startsWith('<')) { out += part; continue; }
    const take = part.slice(0, Math.max(0, n - k)); out += take; k += take.length;
  }
  h.e.innerHTML = out + '<span style="color:var(--accent)">▍</span>';
}
// A screenshot in a window frame, cropped to [x0, y0, x1, y1] of the image and shown w px wide.
function windowShot(el, file, crop, w) {
  const box = mk('div', 'win', el);
  const s = w / (crop[2] - crop[0]);
  box.style.width = w + 'px'; box.style.height = (crop[3] - crop[1]) * s + 'px';
  const img = mk('img', '', box); img.src = src(file, 'screens');
  return { box, img, s, crop, w, h: (crop[3] - crop[1]) * s };
}
// The camera inside the window: pan/zoom from view a to view b ([cx, cy, zoom] in image px) between t0 and t1.
function drawShot(sh, t, t0, t1, a, b, x = 960, y = 560, o = 1) {
  const p = ease(t, t0, Math.max(0.01, t1 - t0), E.inOut);
  const cx = lerp(a[0], b[0], p), cy = lerp(a[1], b[1], p), z = lerp(a[2], b[2], p);
  const k = sh.s * z;
  sh.img.style.transform = `translate(${sh.w / 2 - cx * k}px, ${sh.h / 2 - cy * k}px) scale(${k})`;
  place(sh.box, x, y, 1, o);
}
// A highlight frame round a region [x0, y0, x1, y1] of the image, for a shot drawn with drawShot at view v.
function frameBox(el, cls = '') { return mk('div', 'frame ' + cls, el); }
function drawFrame(f, sh, v, rect, t, at, x = 960, y = 560) {
  const k = sh.s * v[2];
  const fx = x - sh.w / 2 + sh.w / 2 + (rect[0] - v[0]) * k, fy = y - sh.h / 2 + sh.h / 2 + (rect[1] - v[1]) * k;
  f.style.left = fx - 8 + 'px'; f.style.top = fy - 8 + 'px';
  f.style.width = (rect[2] - rect[0]) * k + 16 + 'px'; f.style.height = (rect[3] - rect[1]) * k + 16 + 'px';
  f.style.opacity = ease(t, at, 0.25);
}
function chip(el, html) { return mk('div', 'chip', el, html); }
function tile(el, n, label) { const e = mk('div', 'tile', el, `<div class="n">${n}</div><div class="l">${label}</div>`); return { e, n: e.querySelector('.n') }; }
// A number that counts up to `to` between at and at + dur.
function countUp(t, at, to, dur = 0.8, fmt = v => Math.round(v).toLocaleString('en-US')) { return fmt(to * ease(t, at, dur)); }
// Fade-and-rise for anything: place(e, x, y + rise, 1, opacity).
function rise(e, t, at, x, y, d = 24) { const p = ease(t, at, 0.45); place(e, x, y + d * (1 - p), 1, p); }
// The logo end card: your logo (a cut-out name, e.g. 'my-logo' for assets/cutouts/my-logo.png), lines and the credits.
// Without a logo, the first line is the name, big.
function logoCard(at, { logo = null, logoW = 760, lines = [], credits = [] } = {}) {
  return cut(at, 'dark', el => {
    const l = logo ? sprite(el, logo, logoW, 'obj') : null;
    const ls = lines.map((h, i) => { const d = mk('div', 'quiet', el, h); d.style.cssText += `font: ${i ? 400 : 700} ${i ? 26 : (logo ? 34 : 64)}px var(--mono); color: ${i ? 'var(--ink-2)' : 'var(--ink)'};`; return d; });
    const cr = mk('div', 'quiet', el, credits.map(x => `<div style="font: 400 18px var(--mono); color: var(--muted); text-align:center; margin-top: 6px">${x}</div>`).join(''));
    return { l, ls, cr };
  }, (s, t, a) => {
    if (s.l) rise(s.l, t, a, 960, 430);
    s.ls.forEach((d, i) => rise(d, t, a + 0.3 + i * 0.15, 960, s.l ? 620 + i * 52 : 480 + i * 72));
    place(s.cr, 960, 1080 - 96 - s.cr.offsetHeight / 2, 1, ease(t, a + 0.6, 0.4)); // above the caption line
  }, { label: 'end card' });
}
