---
name: social-cut-and-covers
description: Make a video's derivatives — the 30-45 s social cut taken from the long video at its own cut times and re-mixed, its call-to-action card, and the covers (PNG plus a JPEG under 5 MB for X). Use for "make a short version", "a cut for LinkedIn/X", "a thumbnail", "a cover image".
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit
---

# Social cut and covers

From the project folder, with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`). The long video must be
final (`out/silent.mp4`, `audio/mix.wav`, `timing/points.json` current).

## The social cut

Cut it **from the long one at the edit's own cut times** and **re-mix** it; never slice the finished audio (the music
would jump at every join).

1. `studio sheet` and pick the stretches: the hook, the reveal, the two or three best features, the price gag, the
   name. Leave out what needs context (an epilogue, the long end card, testimonials).
2. Write `short.json`: `"cuts"` as cut numbers from the sheet (`3` or `[5, 7]` for 5 through 7), `"card"` seconds of a
   call-to-action card, `"name"`.
3. The card: in `video.html`, **after** `setEnding(…)`, add
   ```js
   shortCard(3.5, at => endCard(at, 'green', { title: 'THE PRODUCT!', lines: ['theproduct.example'], credits: window.PROJECT.credits }));
   ```
   It is drawn after the film's end only when the page is opened with `?short`, so the long video doesn't change; it
   fades and holds black for its last 0.6 s. Set `"card": 3.5` in `short.json`.
4. `studio short` → `out/<project>-<name>.mp4`: each stretch after the first starts one frame late (so the previous
   caption doesn't flash), the voice keeps each stretch's first sound, effects come with their stretch, and the bed
   is one continuous slice per anchor, ducked under the short's own phrases. It's mastered and checked like the long one.
   For better musical joins, add `"music": [[stretch, music time], …]` anchors so each slice starts on a hit.

## Covers

Covers are HTML pages like the video (`cover.html` in the project: the same blocks, one frame). **No spoilers**, and
the mascot or hero object must appear. `studio cover` → `out/cover.png` and `out/cover.jpg` (under 5 MB, for X). For a
second cover, copy `cover.html` to `cover-2.html` and run `studio cover cover-2.html`.
