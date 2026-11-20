# The engine: building blocks of a video page

A project's `video.html` loads `timing.js` (from `studio timing`), `assets/gen/manifest.js`, `engine/engine.js` and one
style (`engine/infomercial.js` or `engine/explainer.js`, with its CSS). Then it defines its cuts and calls
`setEnding(…)`, `buildHits()` (infomercial) and `ready()`. All coordinates are in a 1920×1080 frame.

## Core (`engine/engine.js`)

| Call | What it does |
|---|---|
| `c(name)` / `cue(name)` | Start time of the word marked `{#name}`, minus a 2-frame visual lead. NaN (the cut is skipped and listed as MISSING) if the script lost the cue. |
| `W(name, k, end)` | Start (or end) of the k-th word after the cue. |
| `cut(at, bg, build, draw, opts)` | A shot from `at` until the next cut. `build(el)` makes elements once and returns state; `draw(state, t, start, end)` poses them for frame `t`. `opts`: `label` (the shot id), `bgAt(t)`, `freeze`, `stageRot(t,a,b)`, `noScan`, `noCaps`. |
| `place(e, x, y, scale, opacity, rotation)` | Centre an element on (x, y). |
| `settle(t, at)` | The 2-frame landing step (0 before `at`). `stepS(s)` snaps a scale to 1/40. `drift(t, a, b)` a 4 % push. |
| `prog(t, a, b)`, `ease(t, at, dur, E.out)`, `lerp`, `clamp`, `rng(seed)` | Timing maths; `rng` is the only randomness allowed. |
| `mk(tag, cls, parent, html)` | Make an element. |
| `sprite(el, name, w, cls)` | A cut-out: `'name'` = `assets/cutouts/name.png`, `'kit:name'` = the kit's starters. `cls`: `'obj'`, `'obj stk'` (sticker outline), `'obj bw'` (black and white). |
| `plate(el, name)`, `kenBurns(e, t, a, b)` | A full-bleed plate from `assets/plates/` and its slow push. |
| `sfx(t, kind)` | A sound effect for the mix (kinds in `sfx.json`). |
| `audio(t, file, {from, to, gain, filter, fadeIn, fadeOut})` | Any other audio file placed by the edit. |
| `musicStop(t)`, `musicMute(a, b)` | Stop the bed dead; mute it for a span. |
| `PUNCH.push({t, amp})`, `FLASH.push({t, amp})`, `CALM.push([a, b])` | A zoom-shake, a white flash; a span where shouted words don't punch. `buildHits()` adds a punch on every CAPITALISED narrator word. |
| `genSlot(el, shot)`, `drawGen(s, t, a)` | A generated clip's frames (or its plate with a PENDING tag until it exists). |
| `pinTo(el, w, h, track, t, a)`, `quadMatrix(w, h, quad)` | Corner-pin an element onto a tracked screen. |
| `setEnding(at, hold, fade, black)` | The end card starts at `at` and holds `hold` s, then fades and stays black ≥ 15 frames. Sets the duration. |
| `shortCard(len, at => …)` | The social cut's CTA card, drawn only with `?short`, after the film's end. |
| `SHOW_CAPTIONS` | Captions from the script (default on). |
| `BACKGROUNDS[name] = {canvas, draw(t, cut)}` or `{dom: 'class'}` | Register a background. `g` is the 480×270 canvas context. |
| `OVERLAYS.push((t, cut) => …)` | Something drawn on top of every frame. |

## Infomercial (`engine/infomercial.js`)

| Call | What |
|---|---|
| Backgrounds | `'green' 'amber' 'cyan' 'blue' 'pink' 'rainbow'` (the CRT grid), `'laser'`, `'tunnel'`, `'black'`, `'grey'` (studio set, for `.bw` cut-outs), `'studio'` (blue set), `'none'`. |
| `words(el, [[text, size, at, cls], …])`, `drawWords(list, t)` | Impact meme lines popping on their times; `cls`: `'wa'` WordArt, colours `'amb' 'cy' 'bl' 'rd' 'grn' 'yl'`. Lines shrink to fit. |
| `wordsCut(at, bg, lines, opts)`, `objCut(at, bg, name, w, {x, y, r, cls})` | One-call cuts. |
| `dupes(el, text, at)`, `drawDupes` | The name at every edge in party colours. |
| `sticker(el, html, size, color)` | An 8-bit badge. |
| `stamp(el, text, size, color)` + `stampS(t, at)` | A rubber stamp thumping down. |
| `redBar(el, w)`, `redX(el, w)` | A slash; a big red X. |
| `term(el, title, lines)` | A plain terminal window. |
| `bubble(el, text, size, tail)` | A comic speech bubble. |
| `starburst(r, n, fill)` | SVG for `mk('div', 'quiet', el, starburst(…))`. |
| `fire(el, {wall, cols, h})`, `drawFire(f, t, at)` | A wall and columns of flames. |
| `boom(t, x, y, k)` | An explosion (with its sound). Keep them off the words. |
| `flyers(el, names, n, seed, {w, rain})`, `drawFlyers` | Cut-outs flying across or raining. |
| `dropIn(e, t, at, x, y)` | A cut-out falling into place. |
| `priceCut(at, bg, [[t, '$1,000'], …], {slash: {at, stamp}, label, fine, opts})` | The price gag. |
| `endCard(at, bg, {logo, title, lines, credits, beats, fireOn, rainNames})` | The end card with the credits above the caption line. `logo` is a cut-out name: use your own (`assets/cutouts/logo.png` → `logo: 'logo'`). |

## Explainer (`engine/explainer.js`)

| Call | What |
|---|---|
| Backgrounds | `'dark'`, `'grid'` (a faint drifting dot grid). Every cut dips in from black (`opts.hard` to cut). |
| `headline(el, html, {top, size})`, `drawHeadline(h, t, at, cps)` | A typed monospace headline; `<em>` is the accent. |
| `windowShot(el, file, crop, w)`, `drawShot(sh, t, t0, t1, viewA, viewB, x, y)` | A screenshot (`assets/screens/`) in a window; the camera pans between views `[cx, cy, zoom]`. |
| `frameBox(el)`, `drawFrame(f, sh, view, rect, t, at)` | A highlight round a region of the screenshot. |
| `chip(el, html)`, `tile(el, n, label)`, `countUp(t, at, to)` | Chips, stat tiles, counting numbers. |
| `rise(e, t, at, x, y)` | Fade and rise into place. |
| `logoCard(at, {logo, lines, credits})` | The logo end card. |

## Adding a block or a style

A new block is a function in the style file that builds elements (`mk`, `sprite`) and a draw function of `t`. A new
style is `engine/<style>.css` + `engine/<style>.js` (backgrounds and blocks) + `templates/<style>/` (a starter
`video.html`, `script.md`, `project.json`, `music.json`, `cover.html`, `short.json`). See CONTRIBUTING.md.
