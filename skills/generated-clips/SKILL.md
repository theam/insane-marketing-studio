---
name: generated-clips
description: Add generated video clips (Seedance 2.5 on Higgsfield) to a video safely — cost estimate and explicit approval first, a cap, a ledger with idempotency keys, chaining shots from the previous take's frame, lip sync placed from Scribe, speed ramps, corner-pinning a UI onto a screen in the footage. Use when a shot needs real motion footage (a character acting, a scene) rather than cut-outs.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit
---

# Generated clips (Seedance 2.5 on Higgsfield)

Clips cost real money per second (Higgsfield list price ≈ $0.46 a second at 720p, $1.14 at 1080p; see
`${CLAUDE_PLUGIN_ROOT}/references/spend.md`). The style works without them: use plates and cut-outs first, and add
clips only where motion carries the joke. **Lock the rest of the video before buying clips** ("once the base is right I'll
buy more credits").

## Before any spend

1. Plates first: every clip starts from a still (`first_frame`) that is already right (the **plates-and-cutouts**
   skill). Fix the plate, not the clip.
2. Write `gen/shots.json` with `cap_usd` (agreed with the director) and one entry per shot: `id`, `prompt`,
   `first_frame` (a plate, or `"after:<id>"` / `"after:<id>@<seconds>"` to start from the previous take's frame),
   `duration` (5 s is the unit), `resolution` (720p; 1080p where a face matters), and `reference_audio` for lip sync.
3. `studio seedance estimate` (free) prints the price of one take of each shot. Generated seconds run about 2× what the
   cut uses: budget for it.
4. **Ask:** "These N clips will cost about $X (one take each). Go?" Only an explicit yes counts; silence never does.
   Log the answer in `brief.md`.

## Run

`studio seedance run e1 e2` (one take each by default; `--takes 2` only when a choice is worth paying twice). Every take
is recorded in `gen/clips/<id>.json` before its request, with an idempotency key, and every event in `gen/ledger.jsonl`.
It stops before the cap. Higgsfield's balance can't be read through the API: when it runs dry, takes fail with "credit
balance is too low"; stop and tell the director. Quote real spend from Higgsfield's billing page, not the ledger.

## What the Shepherdr production learned

- **Chain shots** from the previous take's frame (`first_frame: "after:e4"`), so a cut joins.
- **Wrong geometry again and again? Change the camera**, don't regenerate the same plate: the final shot was made from
  outside the window, from the last frame of the take before, with no desk in frame.
- **Morphs between takes read as strange camera moves.** Cut instead.
- **Reject the CG look** ("the goats look like 3D animation") and doubled details (two star clips); keep some motion in
  the background. A logo the model draws is removed with `delogo` (see below).
- **Lip sync: reference-to-video does NOT follow the reference audio's timing.** The mouth follows the take's own
  generated speech. Transcribe the delivered take: `studio scribe gen/clips/e5/take-1.mp4 gen/clips/e5/words.json`
  (or through the connector), and place the clean lines at the times Scribe hears (Shepherdr: "Hey" at 1.12 s, the line
  at 3.28-4.68 s; the lines were moved to 1.04 s and 3.18 s). Don't cut the shot mid-line.
- **OpenRouter** (same model, about half the price) refuses photoreal people ("input image may contain real person");
  it's fine for animals and objects.

## Into the page

1. `gen/picks.json`: `{"shots": {"hey": {"take": "gen/clips/e5/take-1.mp4", "from": 0.0, "to": 3.6}}}`; optional
   `"ramps": [[0.45, 1.85, 2.8]]` (those take seconds at 2.8×: drops frames with 1-2-1 blending, cuts a dead hold;
   never slow a take down) and `"delogo": [x, y, w, h]`.
2. `studio clip-frames` → `assets/gen/<shot>/000.jpg…` and `assets/gen/manifest.js`.
3. In the page: `cut(at, 'none', el => ({ g: genSlot(el, 'hey') }), (s, t, a) => drawGen(s.g, t, a), { label: 'hey', noScan: true })`.
   Before the clip exists, `genSlot` shows its plate with a PENDING tag, so the video always renders.
4. **A UI on a screen in the footage:** measure the screen's corners on one frame, then
   `studio cornerpin hey --quad "x,y x,y x,y x,y" --crop "x y w h"` (macOS Vision registration, smoothed); load
   `assets/gen/hey-screen.js` in the page and `pinTo(uiEl, w, h, SCREENS.hey, t, a)` every frame. Check every corner
   on stills ("each of the corners must fit perfectly").
5. Check lip sync and joins on stills and in QuickTime before the final render.
