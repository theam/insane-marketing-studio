// =====================================================================================================================
// The infomercial style: slopcore late-night TV. Extracted from the INSANE Shepherdr infomercial.
//
// Backgrounds: a phosphor CRT grid rushing to the horizon (green, amber, cyan, blue, rainbow), a laser show, a
// kaleidoscope tunnel, black, and the studio set (grey for the black-and-white "problem", blue after it).
// Blocks: Impact meme words (WordArt), photo cut-outs and stickers, 8-bit badges, rubber stamps, red slashes and Xs,
// a terminal, a speech bubble, a starburst, walls and columns of fire, explosions, raining cut-outs, edge duplicates,
// the price gag and an end card. Load after engine.js.
// =====================================================================================================================

// ---------- backgrounds ----------
const PAL = { green: [75, 227, 138], amber: [244, 168, 58], cyan: [82, 198, 234], blue: [107, 140, 255], pink: [255, 43, 214] };
const STARS = (() => { const R = rng(5); return Array.from({ length: 70 }, () => ({ x: Math.floor(R() * 480), y: Math.floor(R() * 112), p: R() * 6.28, b: R() })); })();
const HSL = h => { const f = n => { const k = (n + h / 30) % 12; return 255 * (0.5 - 0.5 * Math.max(-1, Math.min(k - 3, 9 - k, 1))); }; return [f(0), f(8), f(4)]; };
// The CRT pasture. mode: green | amber | cyan | blue | pink | rainbow; frozen: the grid stops (a record-scratch beat).
function drawPasture(t, mode = 'green', frozen = false) {
  const HZ = 118, VX = 240;
  const rainbow = mode === 'rainbow';
  const base = PAL[mode] || PAL.green;
  const col = (k, a) => { const q = rainbow ? HSL((k * 37 + t * 240) % 360) : base; return `rgba(${q[0] | 0},${q[1] | 0},${q[2] | 0},${a})`; };
  const sky = g.createLinearGradient(0, 0, 0, HZ);
  sky.addColorStop(0, '#000'); sky.addColorStop(1, col(0, 0.22));
  g.fillStyle = '#010503'; g.fillRect(0, 0, 480, 270);
  g.fillStyle = sky; g.fillRect(0, 0, 480, HZ);
  STARS.forEach(s => { if (Math.sin(t * 3 + s.p) > -0.3 || frozen) { g.fillStyle = s.b > 0.85 ? '#fff' : col(1, 0.7); g.fillRect(s.x, s.y, s.b > 0.85 ? 2 : 1, s.b > 0.85 ? 2 : 1); } });
  // A pixel sun on the horizon, banded like an old arcade cabinet.
  for (let r = 0; r < 34; r++) {
    if (r % 6 > 3 && r > 12) continue;
    const w = Math.floor(Math.sqrt(34 * 34 - (34 - r) * (34 - r)));
    g.fillStyle = col(2 + r, 0.55 - r * 0.008); g.fillRect(VX - w, HZ - 34 + r, w * 2, 1);
  }
  // Ground and the perspective grid rushing toward us.
  g.fillStyle = '#020c06'; g.fillRect(0, HZ, 480, 270 - HZ);
  const ph = frozen ? 0.35 : (t * 1.6) % 1;
  for (let i = 0; i < 22; i++) {
    const z = i + 1 - ph;
    if (z <= 0.05) continue;
    const y = Math.floor(HZ + 150 / z);
    if (y > 270) continue;
    g.fillStyle = col(i, clamp(0.25 + 0.75 / z, 0, 1)); g.fillRect(0, y, 480, 1);
  }
  for (let k = -16; k <= 16; k++) {
    g.strokeStyle = col(k + 40, 0.8); g.lineWidth = 1;
    g.beginPath(); g.moveTo(VX + 0.5, HZ); g.lineTo(VX + k * 44 + 0.5, 270); g.stroke();
  }
  g.fillStyle = col(3, 1); g.fillRect(0, HZ, 480, 1);
  if (rainbow) { // glitch: a few rows slip sideways for a frame or two
    const R = rng(Math.floor(t * 15));
    for (let i = 0; i < 6; i++) { const y = Math.floor(R() * 270), h = 2 + Math.floor(R() * 10), dx = Math.floor((R() - 0.5) * 30); g.drawImage(bg, 0, y, 480, h, dx, y, 480, h); }
  }
}
// A laser show and a kaleidoscope tunnel, for the peaks.
function drawLasers(t) {
  g.fillStyle = '#05010b'; g.fillRect(0, 0, 480, 270);
  const C = ['#ff2bd6', '#2bf4ff', '#4be38a', '#ffe14a', '#6b8cff'];
  [[0, 270], [480, 270], [0, 0], [480, 0], [240, 285]].forEach(([sx, sy], k) => {
    for (let j = 0; j < 3; j++) {
      const a = (sy > 135 ? -Math.PI / 2 : Math.PI / 2) + Math.sin(t * (1.1 + 0.37 * k) + j * 2.1 + k * 1.3) * 1.1;
      const ex = sx + Math.cos(a) * 640, ey = sy + Math.sin(a) * 640;
      g.strokeStyle = C[(k + j) % 5];
      g.globalAlpha = 0.25; g.lineWidth = 9; g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.stroke();
      g.globalAlpha = 1; g.lineWidth = 2; g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.stroke();
    }
  });
}
function drawTunnel(t) {
  g.fillStyle = '#000'; g.fillRect(0, 0, 480, 270);
  const C = ['#2b0f4a', '#b8279f', '#ffd84a', '#52c6ea'], ph = (t * 1.5) % 1, n = Math.floor(t * 1.5);
  for (let i = 18; i >= 0; i--) {
    const r = 5 * Math.pow(1.3, i + ph);
    g.fillStyle = C[(((i - n) % 4) + 4) % 4];
    g.beginPath(); g.moveTo(240, 150 - r); g.lineTo(240 + r * 0.866, 150 + r / 2); g.lineTo(240 - r * 0.866, 150 + r / 2); g.closePath(); g.fill();
  }
}
['green', 'amber', 'cyan', 'blue', 'pink', 'rainbow'].forEach(m => { BACKGROUNDS[m] = { canvas: true, draw: (t, k) => drawPasture(t, m, !!k.freeze) }; });
BACKGROUNDS.laser = { canvas: true, draw: drawLasers };
BACKGROUNDS.tunnel = { canvas: true, draw: drawTunnel };
BACKGROUNDS.black = { canvas: true, draw: () => { g.fillStyle = '#000'; g.fillRect(0, 0, 480, 270); } };
BACKGROUNDS.grey = { dom: 'grey' };   // the black-and-white studio: use .bw cut-outs on it
BACKGROUNDS.studio = { dom: 'blue' };
BACKGROUNDS.none = {};
// An old-TV flicker on the grey set.
OVERLAYS.push((t, cur) => { set.style.opacity = cur && (cur.bgAt ? cur.bgAt(t) : cur.bg) === 'grey' ? 0.93 + 0.07 * rng(Math.floor(t * 15) + 11)() : 1; });

// ---------- words ----------
// Big words, one line per entry: [text, size, at, cls]. Each line pops on its time; lines shrink to fit 1760 px.
// cls: '' white, 'wa' WordArt, 'amb' 'cy' 'bl' 'rd' 'grn' 'yl' colours, combinable ('yl wa').
function words(el, lines) {
  const box = mk('div', 'words', el);
  return lines.map(([text, size, at, cls]) => { const d = mk('div', cls || '', box, text); d.style.fontSize = Math.round(size * 1.18) + 'px'; d.style.visibility = 'hidden'; return { d, at, fit: null }; });
}
function drawWords(list, t) {
  list.forEach(l => {
    if (l.fit == null && l.d.offsetWidth) l.fit = Math.min(1, (l.max || 1760) / l.d.scrollWidth);
    l.d.style.visibility = t >= l.at ? 'visible' : 'hidden';
    l.d.style.transform = `scale(${(settle(t, l.at) || 1) * (l.fit || 1)})`;
  });
}
// A cut that is only words; a cut that is one cut-out popping in and drifting.
function wordsCut(at, bgName, lines, opts = {}) { return cut(Math.max(at, lines[0][2]), bgName, el => ({ w: words(el, lines) }), (s, t) => drawWords(s.w, t), opts); }
function objCut(at, bgName, name, w, { x = 960, y = 560, r = 0, cls = 'obj' } = {}) {
  return cut(at, bgName, el => ({ o: sprite(el, name, w, cls) }), (s, t, a, b) => place(s.o, x, y, stepS(settle(t, a) * drift(t, a, b)), 1, r));
}
// The same words cut off at the frame's edges in party colours (the reveal).
function dupes(el, text, at, bottomOnly = false) {
  const cols = ['#ff2bd6', '#4be38a', '#ffe14a', '#52c6ea', '#ff2a2a', '#6b8cff'];
  return [[300, 55], [1560, 65], [1640, 1015], [280, 1025]].slice(bottomOnly ? 2 : 0).map(([x, y], i) => {
    const d = mk('div', 'quiet', el, text); d.style.cssText += `font: 400 130px Impact, sans-serif; color:${cols[i]}; -webkit-text-stroke: 8px #000; paint-order: stroke fill; z-index: 4;`;
    return { d, x, y, at: at + i * 0.06 };
  });
}
function drawDupes(list, t) { list.forEach(k => place(k.d, k.x, k.y, 1, t >= k.at ? 1 : 0)); }

// ---------- badges, stamps and marks ----------
// An 8-bit sticker; color is its outer border.
function sticker(el, html, size = 34, color = 'var(--green)') { const e = mk('div', 'sticker', el, html); e.style.fontSize = size + 'px'; e.style.setProperty('--c', color); return e; }
// A rubber stamp lands big and thumps down in two frames: place(e, x, y, stampS(t, at), t >= at ? 1 : 0, -8).
const stampS = (t, at) => (t < at ? 0 : t < at + 1 / FPS ? 1.6 : t < at + 2 / FPS ? 1.15 : 1);
function stamp(el, text, size, color = '#e8261f') { const e = mk('div', 'stamp', el, text); e.style.fontSize = size + 'px'; e.style.color = color; e.style.borderColor = color; return e; }
function redBar(el, w, h = 46) { const e = mk('div', 'quiet', el); e.style.cssText += `width: ${w}px; height: ${h}px; background: #ff2a2a; box-shadow: 0 0 0 6px #000;`; return e; }
function redX(el, w) {
  return mk('div', 'quiet', el, [45, -45].map(r => `<div style="position:absolute; left:${-w / 2}px; top:-26px; width:${w}px; height:52px; background:#ff2a2a; box-shadow:0 0 0 7px #000; transform: rotate(${r}deg)"></div>`).join(''));
}
// A plain terminal window.
function term(el, title, lines, w = 560) {
  const d = mk('div', 'card', el, `<div style="background:#2b2b2b; padding: 10px 16px; font: 400 18px 'Fira Code'; color:#aaa"><span style="color:#ddd">● ● ●</span>&nbsp;&nbsp;${title}</div><div style="padding: 16px 22px; font: 400 24px 'Fira Code'; color:#d6ded9; line-height: 1.6; white-space: pre">${lines.join('\n')}</div>`);
  d.style.cssText += `width: ${w}px; background:#0b0d0c; border-radius: 10px; overflow: hidden; box-shadow: 0 0 0 2px #777, 14px 14px 0 2px rgba(0,0,0,0.5);`;
  return d;
}
// A comic speech bubble. tail: 'right' points down-right from its bottom-right; 'left' reaches far down-left.
function bubble(el, text, size, tail = 'right') {
  const svg = tail === 'left'
    ? '<svg class="l" width="260" height="130" viewBox="0 0 260 130"><path d="M250 4 L10 122 L150 4" fill="#fff" stroke="#111" stroke-width="8" stroke-linejoin="round"/></svg>'
    : '<svg width="110" height="96" viewBox="0 0 110 96"><path d="M8 4 L92 90 L70 4" fill="#fff" stroke="#111" stroke-width="8" stroke-linejoin="round"/></svg>';
  const e = mk('div', 'bubble', el, `<span class="tx">${text}</span>${svg}`);
  e.style.fontSize = size + 'px';
  return e;
}
// A starburst behind a cut-out or a price: mk('div', 'quiet', el, starburst(340, 20, '#ffd84a')).
function starburst(r, n, fill = '#ffd84a') {
  const pts = Array.from({ length: n * 2 }, (_, i) => { const a = Math.PI * i / n, rr = i % 2 ? r * 0.78 : r; return `${(r + 10 + Math.cos(a) * rr).toFixed(1)},${(r + 10 + Math.sin(a) * rr).toFixed(1)}`; }).join(' ');
  return `<svg width="${2 * r + 20}" height="${2 * r + 20}"><polygon points="${pts}" fill="${fill}" stroke="#000" stroke-width="10" stroke-linejoin="round"/></svg>`;
}
const commas = n => Math.round(n).toLocaleString('en-US');

// ---------- fire, explosions, flying cut-outs ----------
function fxImg(el, name, w) { const e = mk('img', 'fx', el); e.src = `engine/fx/${name}.jpg`; e.style.width = w + 'px'; return e; }
// Flames: a wall along the bottom and columns ([x, y, scale]); two takes of each cross-fade and stretch, so stills flicker.
function fire(el, { wall = true, cols = [], w = 2300, cw = 520, h = 1 } = {}) {
  const parts = [];
  if (wall) [1, 2].forEach(i => parts.push({ e: fxImg(el, `flames-wall-${i}`, w), x: 960, y: 1130, i, c: 0, flip: i === 2 }));
  cols.forEach(([x, y, k], ci) => [1, 2].forEach(i => parts.push({ e: fxImg(el, `flame-tall-${i}`, cw * (k || 1)), x, y, i, c: ci + 1, flip: ci % 2 === 1 })));
  return { parts, h };
}
function drawFire(f, t, at, k = 1) {
  const fr = Math.floor(t * 15), grow = ease(t, at, 0.3) * k;
  f.parts.forEach(p => {
    const R = rng(fr * 13 + p.i * 7 + p.c * 29);
    const mix = 0.5 + 0.5 * Math.sin(t * 9 + p.c * 2 + p.i * Math.PI);
    p.e.style.transform = `translate(${p.x}px, ${p.y}px) translate(-50%, -100%) scale(${(p.flip ? -1 : 1) * (1 + 0.05 * (R() - 0.5))}, ${(0.85 + 0.3 * R()) * grow * f.h})`;
    p.e.style.opacity = t < at ? 0 : clamp(0.35 + 0.65 * mix);
  });
}
// Explosions on top of everything (inside the stage, so they shake with it): a fireball and a spark burst, 0.75 s.
// Each boom also places its sound effect.
const BOOMS = [];
function boom(t, x = 960, y = 540, k = 1) { if (!Number.isFinite(t)) return; BOOMS.push({ t, x, y, k }); sfx(t, k >= 0.9 ? 'explosion' : 'explosion-small'); }
const boomLayer = mk('div', 'abs', $('stage'));
boomLayer.style.cssText += 'width: 1920px; height: 1080px; z-index: 50; pointer-events: none; mix-blend-mode: screen;';
const BOOM_POOL = Array.from({ length: 5 }, () => ['fireball', 'explosion'].map(n => { const e = fxImg(boomLayer, n, 1000); e.style.transformOrigin = '50% 50%'; e.style.opacity = 0; return e; }));
function drawBooms(t) {
  const live = BOOMS.filter(b => t >= b.t && t < b.t + 0.75);
  BOOM_POOL.forEach(([f, x], i) => {
    const b = live[i];
    if (!b) { f.style.opacity = x.style.opacity = 0; return; }
    const d = (t - b.t) / 0.75, R = rng(Math.round(b.t * 100));
    f.style.transform = `translate(${b.x}px, ${b.y}px) translate(-50%, -50%) rotate(${Math.round(R() * 360)}deg) scale(${b.k * (0.3 + 1.1 * E.out(Math.min(1, d * 1.8)))})`;
    x.style.transform = `translate(${b.x}px, ${b.y}px) translate(-50%, -50%) rotate(${Math.round(R() * 360)}deg) scale(${b.k * (0.5 + 1.5 * E.out(Math.min(1, d * 2.5)))})`;
    f.style.opacity = d < 0.45 ? 1 : 1 - (d - 0.45) / 0.55;
    x.style.opacity = d < 0.25 ? 1 : Math.max(0, 1 - (d - 0.25) / 0.4);
  });
}
OVERLAYS.push(t => drawBooms(t));
// Cut-outs flying across the frame (or raining down), each with a white sticker outline.
function flyers(el, names, n, seed, { w = 240, rain = false } = {}) {
  const R = rng(seed);
  return Array.from({ length: n }, (_, i) => ({ e: sprite(el, names[i % names.length], w * (0.7 + 0.6 * R()), 'obj stk'), p: R(), d: R() * 0.9, v: 700 + R() * 900, r: (R() - 0.5) * 540, dir: R() > 0.5 ? 1 : -1, rain }));
}
function drawFlyers(list, t, a) {
  list.forEach(f => {
    const u = t - a - f.d;
    const x = f.rain ? (f.xs ?? 120 + f.p * 1680) : f.dir > 0 ? -300 + u * f.v : 2220 - u * f.v;
    const y = f.rain ? -300 + ((u * f.v) % 1700) : 100 + f.p * 880 + Math.sin(u * 3) * 40;
    place(f.e, x, y, 1, u > 0 ? 1 : 0, Math.round(u * f.r));
  });
}
// A cut-out that drops into place from above (ingredients into the blender: animate the fall, never just pop in).
function dropIn(e, t, at, x, y, { from = -400, dur = 0.35, r0 = -40, r1 = 0 } = {}) {
  const p = ease(t, at, dur, E.out);
  place(e, x, lerp(from, y, p), 1, t >= at ? 1 : 0, lerp(r0, r1, p));
}

// ---------- the price gag ----------
// "How much would you pay? $???  A thousand? A TRILLION? … It's free." A yellow tag whose price flips on cues, then a
// red slash and a stamp. steps: [[at, text, size?], …]; slash: { at, stamp: 'FREE · $0', color } (optional).
function priceTag(el, { label = 'ONLY', fine = '*plus shipping & handling' } = {}) {
  const d = mk('div', 'price', el, `<div class="lab">${label}</div><div class="p">$???</div><div class="fine">${fine}</div>`);
  return { d, p: d.querySelector('.p') };
}
function priceCut(at, bgName, steps, { label, fine, slash, x = 960, y = 490, opts } = {}) {
  return cut(at, bgName, el => ({ ...priceTag(el, { label, fine }), bar: slash ? redBar(el, 1450, 56) : null, st: slash && slash.stamp ? stamp(el, slash.stamp, 150, slash.color || '#25a85c') : null }), (s, t, a) => {
    const live = steps.filter(([sat]) => t >= sat).pop();
    const txt = live ? live[1] : (Math.floor(t * 4) % 2 ? '$???' : '$ ??');
    s.p.textContent = txt; s.p.style.fontSize = ((live && live[2]) || 300) + 'px';
    const flip = steps.some(([sat]) => t >= sat && t < sat + 0.1) ? 0.25 : 1;
    const last = steps[steps.length - 1][0];
    const big = t >= last ? (t < last + 1 / FPS ? 1.25 : t < last + 2 / FPS ? 1.1 : 1.03) : 1;
    const shake = t >= last && !(slash && t >= slash.at) ? (Math.floor(t * 20) % 2 ? 3 : -3) : -3;
    s.d.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) rotate(${shake}deg) scale(${(settle(t, a) || 1) * big}, ${flip * big})`;
    if (s.bar) place(s.bar, x, y + 10, 1, t >= slash.at - 0.2 ? 1 : 0, -8);
    if (s.st) place(s.st, x + 290, y + 370, stampS(t, slash.at), t >= slash.at ? 1 : 0, -8);
  }, opts);
}

// ---------- the end card ----------
// A wordmark (or a big title), a URL, a line, and the credits the video needs (Claudia, photos, AI disclosure).
// lines: [title, url, tagline]; credits: [string, …] (small, at the bottom). Kicks on the beat times given.
// logo: a cut-out name (your logo in assets/cutouts/), none by default; pass a logo and a title to stack a small logo
// above the title.
function endCard(at, bgName, { logo, logoW = 900, title = null, lines = [], credits = [], beats = [], fireOn = true, rainNames = [] } = {}) {
  if (logo === undefined) logo = null;
  if (logo && title) logoW = Math.min(logoW, 420);
  return cut(at, bgName, el => {
    const fl = fireOn ? fire(el, { cols: [[150, 1130, 1], [1770, 1130, 1]], h: 0.6 }) : null;
    const rain = rainNames.length ? flyers(el, rainNames, 8, 91, { w: 200, rain: true }) : [];
    rain.forEach((f, i) => { f.xs = i % 2 ? 130 + f.p * 400 : 1390 + f.p * 400; }); // side lanes keep the hero clear
    const hero = mk('div', 'quiet', el); hero.style.zIndex = 3;
    if (logo) { const i = sprite(hero, logo, logoW, 'obj'); i.style.left = -logoW / 2 + 'px'; i.style.top = (title ? -400 : -260) + 'px'; i.style.transform = 'none'; }
    if (title) { const t1 = mk('div', 'quiet', hero, title); t1.style.cssText += "font: 400 170px Impact, sans-serif; color: #fff; -webkit-text-stroke: 12px #000; paint-order: stroke fill; transform: translate(-50%, -100%); top: -20px;"; }
    const txt = lines.map((l, i) => { const d = mk('div', 'quiet', hero, l); d.style.cssText += `font: ${i === 0 ? 700 : 400} ${i === 0 ? 46 : 30}px 'Fira Code'; color: ${i === 0 ? 'var(--ink)' : '#cfe3d6'}; background: rgba(2,10,6,0.72); padding: 4px 16px;`; return d; });
    txt.forEach((d, i) => place(d, 0, 60 + i * 58, 1, 1));
    const cred = mk('div', 'quiet', el, credits.map((l, i) => `<div style="font: 400 ${i ? 18 : 22}px 'Fira Code'; color: ${i ? '#9fb3a8' : '#e8f0eb'}; margin-top: ${i ? 6 : 0}px; text-align: center">${l}</div>`).join(''));
    cred.style.cssText += 'z-index: 5; background: rgba(2,10,6,0.78); padding: 12px 26px; box-shadow: 0 0 0 2px rgba(75,227,138,0.35);';
    return { fl, rain, hero, cred };
  }, (s, t, a) => {
    const slam = t - a < 1 / FPS ? 1.25 : t - a < 2 / FPS ? 1.12 : 1;
    const db = [a, ...beats].filter(d => d <= t).pop(), dd = t - db;
    const kick = dd < 1 / FPS ? 1.08 : dd < 2 / FPS ? 1.05 : dd < 3 / FPS ? 1.02 : 1;
    place(s.hero, 960, 420, stepS(slam * kick), 1);
    if (s.fl) drawFire(s.fl, t, a, 1);
    drawFlyers(s.rain, t, a);
    // Above the caption bar, so a line spoken over the card never covers the credits.
    if (credits.length) place(s.cred, 960, 1080 - 96 - s.cred.offsetHeight / 2, 1, t >= a + 0.3 ? 1 : 0);
  }, { label: 'end card' });
}
