---
name: voice
description: Cast and generate a video's narration with ElevenLabs — sentence-sized Eleven v4 takes placed by their audible edges, tight gaps, time-stretch, per-line tempo and gap overrides, retakes, a telephone or broadcast chain — then its word timing and a speech-to-text check. Works with an ElevenLabs API key or through the ElevenLabs connector. Use for casting a voice, generating or redoing the voiceover, speeding it up, fixing a mispronounced word or the pacing.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit
---

# Voice

Run everything from the project folder with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`). The voice is
defined in `project.json` → `voices` (one entry per speaker: `voice_id`, `model`, `settings`, `tempo`, `chain`) and
`timing` (gaps, pauses, per-chunk overrides).

## Casting

- **The infomercial narrator** is "Voice Commander Xtreme — 90s toy commercial" (`Tsns2HvNFKfGiNjllgqo`, ElevenLabs
  library), at tempo 1.32 with the `broadcast` chain: that is the Shepherdr sound. **The explainer** default is
  "Justin Case — Warm, Trustworthy, Clear" (`DtQLDxHbTiQTpVVanTy1`), tempo 1.0, `clean` chain.
- To cast another voice, use the ElevenLabs connector: `creative_list_voices` (search plus filters such as
  use_cases `advertisement`, descriptives `hyped`) and give the director the `preview_url`s of three candidates to
  listen to. A voice id only ever comes from that tool or the director.
- A **character** (a cameo line) gets its own speaker: add `"cameo": {...}` to `voices` and write `CAMEO: …` in the
  script. A character voice can be designed (`creative_design_voice`, then `creative_save_designed_voice` for the pick);
  never clone a real person's voice without their written consent. If it sounds too clean, the `telephone` chain.

## Generate and assemble

**With the key (recommended):** `studio voice`. It generates every missing sentence take (one TTS call with word
timestamps each), processes and places them, and writes `audio/voice-lead.wav`, `timing/chunks.json`,
`timing/sections.json` and `timing/words-lead.json`. Then `studio timing` (real cue times) and `studio points`.

**Through the ElevenLabs connector (no key):** the connector's speech has no word timestamps, so the timing comes from
Scribe on the assembled narration.
1. `studio voice --plan` lists the missing takes: `prompt`, `voice_id`, `model_id`, `save_to`.
2. `creative_create_flow` once for the project (name it after the project) and reuse its `flow_id`. For each take:
   `creative_generate_speech` with that prompt, voice, model and `generations_count: 1`; poll
   `creative_get_flow_run_status` until done; then `studio fetch "<content_url>" <save_to>` (links expire in about
   2.5 hours: fetch right away).
3. `studio voice` assembles them.
4. Word timing: `creative_create_asset_upload` (name `voice-lead.wav`, mime `audio/wav`, the exact byte size from
   `stat -f %z audio/voice-lead.wav`), `studio put "<upload_url>" audio/voice-lead.wav audio/wav`,
   `creative_finalize_asset_upload` with the `flow_id`, `creative_transcribe_audio` with `connect_from` its node, poll,
   then `studio fetch "<words_download_url>" timing/scribe-words.json` and `studio timing timing/scribe-words.json`.

## Check it

- **Speech-to-text check, always**: with the key `studio scribe audio/voice-lead.wav timing/stt-check.json` then
  `studio timing --check timing/stt-check.json` (it changes nothing, it only compares); with the connector, step 4
  above already printed it. It lists every script word the transcript lacks or heard differently ("4th mension" for
  "fourth dimension"): fix the spelling in the script (the voice reads what's written; put the screen spelling in
  `project.json` → `display`) and retake that chunk.
- Listen: `open -a "QuickTime Player" audio/voice-lead.wav`.

## Pacing (the director's notes on Shepherdr)

- **Frantic 80s toy-commercial pace:** gaps of 0.05 (same paragraph) / 0.10 / 0.15 s (new section), measured on the
  audio itself (silence under -40 dB), not on the TTS word times (they leave quiet tails: 16.4 s of silence over 59
  pauses in Shepherdr's v5). Pauses inside a take are cut to 0.16 s (0.38 s after an ellipsis).
- **Faster without regenerating:** raise the voice's `tempo` ("speed the audio up by about 10 %… without regenerating"). TTS speed
  barely changes the length; time-stretch does.
- **Per-line overrides:** `timing.chunk_tempo {"04-12-01": 1.15}` and `timing.chunk_gap {"04-12-01": 0.08}` (a
  negative gap eats the previous take's tail). Chunk ids are in `timing/chunks.json` and `studio voice --dry-run`.
  Shepherdr's cameo "That's so agentic." ran 1.15× faster, 0.08 s after the narrator.
- **Retake one line:** `audio/lines/retakes.json` → `{"03-05-02": 2}` (a different seed); every take is kept.
- No whispers in the infomercial; no forced laughs in the explainer.
- After any change: `studio voice`, `studio timing`, `studio points`, then `studio fit-music` (the bed re-fits section by
  section) and `studio mix`. Everything on screen re-times itself from the cues.
