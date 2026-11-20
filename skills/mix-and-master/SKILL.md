---
name: mix-and-master
description: Mix a video's narration, music bed and sound effects, master it to -14 LUFS with a limiter (AAC 384 kbps, 48 kHz), mux it with the picture and run the delivery checks (loudness, true peak, lengths, ends on 15+ black frames). Use for the final mix, "the music is too quiet/loud", "the effects are too loud", or before delivering any MP4.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Edit
---

# Mix and master

From the project folder, with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`):

1. `studio points` (the edit's effects and ending must be current), `studio sfx` (effects the edit uses), then
   `studio mix` → `audio/mix.wav`:
   - the voice untouched;
   - the bed `mix.bed_under_voice_db` (6) under the voice between phrases and `mix.duck_db` (7) further while anyone
     speaks, the duck starting 150 ms before each phrase; stopped and muted where the page says (`musicStop`,
     `musicMute`); fading out with the picture;
   - each effect levelled by family (impacts hotter, tonal blips lower and low-passed) around `mix.sfx_lufs`;
   - other audio the page places with `audio()`.
   It prints the effect gains and anything missing.
2. Listen: `open -a "QuickTime Player" audio/mix.wav`. If the bed is inaudible, lower `bed_under_voice_db` (the
   Shepherdr explainer's first mix sat 14-20 dB under and nobody heard it); if an effect is harsh, alias it to a soft
   kind in `sfx.json` or move it to the `tonal` family.
3. `studio render` (if the picture changed) → `out/silent.mp4`.
4. `studio master` → `out/<project>.mp4`: the mix brought to -14 LUFS with a limiter at about -1.5 dBFS, AAC 384 kbps
   48 kHz, the picture copied as it is. Then the checks print:
   - 1920×1080, H.264 yuv420p, the project's fps; AAC 48 kHz;
   - loudness -14 ±1 LUFS; true peak at or under -1 dBTP;
   - picture and sound the same length;
   - **the last 15+ frames fully black** (never end mid-fade).
   Any FAIL is fixed before the director sees it. `studio qc FILE.mp4` reruns only the checks.
5. Open it: `open -a "QuickTime Player" out/<project>.mp4`, plus `studio sheet out/<project>.mp4` for the contact sheet.
