---
name: motion-and-render
description: Build and change a video's motion graphics — the deterministic video.html page where every cut lands on a narration cue — and render it frame by frame. Use to lay out shots, add or change a gag, an animation, a caption, the end card, timing of a visual, or to render stills, a preview or the final picture.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit, Grep
---

# Motion graphics and the render

The picture is one HTML page, `video.html`. Playwright loads it, calls `window.render(t)` for every frame and pipes the
screenshots to ffmpeg. The page must be **deterministic**: the same `t` always draws the same frame (no
`Date.now()`, no `Math.random()`: use `rng(seed)`; no CSS transitions or animations: everything is computed from `t`).

Read `${CLAUDE_PLUGIN_ROOT}/references/engine.md` for every building block, and the project's own `video.html` (the
starter uses most of them). The engine is in the project's `engine/` folder (a copy: projects don't change when the
kit updates).

## How a page is built

```js
// One cut per idea, on its word: c('name') is the start of the word marked {#name}; W('name', 2) the 3rd word after it.
cut(c('title'), 'rainbow', el => ({                 // background: a style's name ('green', 'amber', 'grey', 'laser'…)
  o: sprite(el, 'kit:crown', 520),                  // build once: elements and state
  w: words(el, [['THE PRODUCT!', 260, c('title'), 'wa']]),
}), (s, t, a, b) => {                               // draw every frame: t now, a/b the cut's start and end
  place(s.o, 960, 350, stepS(settle(t, a) * drift(t, a, b)), 1);
  drawWords(s.w, t);
}, { label: 'title' });                             // the shot id on the storyboard
sfx(c('title'), 'hit'); boom(c('title'), 480, 420); FLASH.push({ t: c('title'), amp: 1 });
…
setEnding(c('final'), 3);   // the end card holds 3 s, fades, then full black (≥ 15 frames)
buildHits();                // CAPITALISED words punch the frame (infomercial)
ready();
```

- **Every animation follows a cue.** Never type a time in seconds for something tied to the words: when a line
  changes, the voice and `studio timing` re-time everything. Fixed-length beats (an implosion, a typing gag) must fit
  the gap they get; shorten them when the narration tightens.
- **The style's rules** (`${CLAUDE_PLUGIN_ROOT}/references/style-infomercial.md`): Impact meme type big; real photo
  cut-outs; one idea per cut, centred; things land on their word in a 2-frame step; the problem in black and white on
  the grey set, colour floods in on the reveal; exaggerate (fire on the reveal, explosions, physical motion: drop the
  ingredients into the blender, don't pop them in); explosions at the sides, never over the words they celebrate; no
  awkward crops of people (full body or a clean bust).
- Captions are on by default (`SHOW_CAPTIONS`), from the script, in English.
- The end card carries the credits (`window.PROJECT.credits` from `project.json`: AI disclosure, photo credits,
  Claudia's credit) above the caption line.

## Check and render

Run from the project folder with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`).

1. `studio timing --placeholder` before any voice (estimated times), `studio timing` after it (real ones).
2. `studio points`: dumps cuts, effects and duration. It prints **MISSING CUES** (a `c('name')` the script doesn't
   have: that cut is skipped) and **PAGE ERRORS**: fix both before anything else.
3. Look before rendering: `studio stills 3.2,5,9.1` (`out/stills/`) and `studio sheet` (`out/review/sheet.png`).
   Open them and check them yourself first: text inside the frame, nothing covering the words, no empty frames.
4. `studio render` → `out/silent.mp4` (about 1-2 minutes per 30 s). Then the **mix-and-master** skill.
5. `studio sheet out/<name>.mp4` for a sheet of the finished video, and open it in QuickTime.

A new version of an approved video goes in a new project folder (`studio new`), never over the approved one. Note each
version in `log.md`: what changed, whose note it answers, gaps, spend.
