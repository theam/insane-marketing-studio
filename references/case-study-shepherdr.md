# Case study: the INSANE Shepherdr infomercial

The production this kit is extracted from: launch videos for [Shepherdr](https://github.com/theam/shepherdr), The Agile
Monkeys' open-source macOS console for coding agents. Claude Code sessions did the production work and one person at The
Agile Monkeys directed it. The production repository (every take, plate and version) is private; this page
describes what's in it and where each piece ended up in the kit.

## What was made (20-22 October 2026)

| Video | Length | What |
|---|---|---|
| The INSANE Shepherdr infomercial | 2:29.1 | A slopcore late-night infomercial, with a Seedance epilogue starring Claudia. v6, the final. |
| The social cut | 0:40.1 | Cut from the long one at its own cut times, re-mixed, with a CTA card. For LinkedIn and X. |
| The making-of | 2:32.7 | Prompts, rejected takes next to their fixes, set to a remix of the stems of a song the company owns. |
| The corporate explainer | 1:42.7 | The calm style: the second style in this kit. |

All 1920×1080, 30 fps, H.264, AAC 48 kHz at -14 LUFS. The director's verdict: "It has been a huge hit."

## How it was built, and where each piece is

| Piece | In the production | In this kit |
|---|---|---|
| The page: deterministic HTML, `window.render(t)` | `video.html` (1,556 lines) | `engine/engine.js` + `engine/infomercial.js` |
| The renderer (Playwright → ffmpeg) | `render.js` | `scripts/render.js` |
| Cues from word timestamps | `build-timing.js` | `scripts/build_timing.js` |
| Sentence takes, audible edges, tempo | `voices.py` | `scripts/voices.py` |
| Music from a sectioned composition plan; re-fit | `music.py`, `fit_music.py` | `scripts/music.py`, `scripts/fit_music.py` |
| Effects; mix by family, ducked bed | `sfx.py`, `mix.py` | `scripts/sfx.py`, `scripts/mix.py` |
| Master at -14 LUFS | `master.sh` | `scripts/master.py` (adds the checks) |
| Social cut | `short.py` | `scripts/short.py` |
| Covers | `render-cover.js`, `cover.html` | `scripts/render_cover.js`, `templates/*/cover.html` |
| Seedance on Higgsfield, cap, ledger | `seedance_hf.py`, `gen/ledger.jsonl` | `scripts/seedance.py` |
| Clip frames, speed ramps, screen tracking | `epi.py` | `scripts/clip_frames.py`, `scripts/cornerpin.py` |
| Vision: cut-outs, registration | `subject.swift`, `track.swift`, `alphabox.swift` | `scripts/vision/` |
| Codex plates | `codexgen.py` | `scripts/codexgen.py` |
| Storyboard | `board.py`, an Artifact | `scripts/board.py`, `templates/storyboard/` |
| The version log | one Markdown log for the whole production | each project's `log.md` |

## The versions (from the production's version log)

- **Mock-up v1** (overnight, 21 Oct): script v8, every voice, 35 effects, a sectioned bed, Seedance epilogue (5 clips + 2
  animated plates). 2:31.
- **v2**: script v9 (no testimonials, absurd prices, no whispers), 62 sentence chunks, narrator at 1.2× with a
  broadcast chain, Claudia through a telephone filter, real cut-outs of Dario, Elon and Jensen, fire and explosions.
- **Epilogue v2**: new takes after a credit top-up; lip sync on "Hey!".
- **v4**: narrator 10 % faster without new TTS; UI corner-pinned with Vision; effects normalized by family; soft
  replacements for the shrill ones; Claudia's credit on the end card.
- **v5**: the morph and the CG goats dropped; lip sync placed from Scribe; the cameo 1.15× faster; music re-fitted per
  section; ends on 18 black frames.
- **v6**: frantic pacing (audible edges, gaps 0.05-0.15 s): 2:29.1. The final.
- **Social cut** (22 Oct): 40.1 s.

## Rebuilding

Every assembled file in the production rebuilds byte for byte from the committed takes with no API key (checked 31 Oct
2026). That is the rule the kit's **deliver** skill follows for every project: commit every take, leave out renders.
What the production learned is in lessons.md and failures.md; what it cost, in spend.md.
