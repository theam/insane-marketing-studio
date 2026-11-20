---
name: music-and-sfx
description: Compose a video's music bed with ElevenLabs Music from a composition plan whose sections start at the narration's turning points, re-fit it after the narration changes, and generate, soften and level the sound effects the edit places. Use for the music, the bed, the score, sound effects, "the beeps are too loud", "the music doesn't change with the story".
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit
---

# Music and sound effects

Run from the project folder with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`). Do this after the voice
and the page exist: the bed's length comes from `timing/points.json` (`studio points`).

## The bed

- `music.json` has one chunk per script section: `starts_at` (section number), `offset` (seconds from that section's
  first sound; a little negative so a hit lands on the first word), the bracketed `text` (`[Reveal]\n{explosive
  orchestral hit on the first beat}`), `positive` and `negative` styles, `adherence`. The template's chunks are the
  Shepherdr score: sad detuned muzak for the problem, an explosive hit into 90s synth-funk on the reveal, relentless
  hype under the features, an urgent "call now" build for the offer, a triumphant hit and a sparkling pad to end.
- Every chunk must last at least 3 s; merge short sections into one chunk.
- `studio music --dry-run` prints the plan with its times (free). `studio music` composes it (one call, about 1-2
  minutes, ElevenLabs credits) → `audio/music-take-N.mp3` (kept) and `audio/music.mp3`.
- The bed runs the whole video, audible (6 dB under the voice between phrases, 7 dB more under speech), and changes with
  each section ("the music should last the whole clip and vary the instruments").
- **After the narration re-times**: `studio fit-music` re-fits the latest take chunk by chunk (atempo per section)
  instead of composing again. It warns past ±10 %: Shepherdr's v6 ran at 1.15-1.27× and that was flagged as its main
  audio risk. If it sounds rough, compose a new take.
- **Gags with the music:** `musicStop(t)` in the page stops the bed dead on a beat ("the music stops dead");
  `musicMute(a, b)` mutes a span (the record scratch). A song the team owns can play as `audio(t, 'path.wav', {from,
  to, gain, filter})`: through a wall, `filter: 'highpass=f=180,lowpass=f=650,aecho=0.8:0.6:40:0.3'`.
- **Composing needs the key** (or the full ElevenLabs connector): the restricted connector has no music. Without
  them, two fallbacks:
  - **A library score the director has the rights to**, with its sections file, in
    `~/.local/share/insane-marketing-studio/music/` (the kit ships none; the format is in
    `${CLAUDE_PLUGIN_ROOT}/library/music/README.md`): `studio fit-music --library NAME` lays it section by section.
    Each chunk plays the section named in its `"library"` field (the template names muzak, build, reveal, hype,
    escalate, butwait, cooking, offer, finale), from that section's first beat, cut to fit. It's the same music in
    every video that uses it: compose a new bed when the video matters.
  - **A track the director has the rights to** (bought, licensed, CC BY with credit): save it as `audio/music.mp3`, cut
    to the video's length (`studio points` prints it) with a short fade at the end, and credit it on the end card. It
    won't change with the sections; place hits with `sfx()` instead.

## Sound effects

- The page places them: `sfx(t, 'kind')`, on the same cue as the picture (`boom()` places its own explosion sound).
  `sfx.json` holds every kind with its prompt, length and family. `studio points`, then `studio sfx` generates only the
  kinds the edit uses (in parallel; about 1 credit-cent each) and trims their leading silence, so each hits on its frame.
- **No loud beeps** (the director: "swap the very loud beeping effects for something less irritating"). Shrill
  kinds are aliased to soft ones in `sfx.json`: airhorn → brass hits, alarm → a soft wobbly "woop woop", buzzer → a tuba
  "bwomp", laser → soft "pew pew", slide whistle → a round swoop, chiptune → triangle waves.
- **Loudness by family, not one fixed gain**: impacts +3 LU, tonal blips -4 LU and low-passed at 6 kHz, around
  `mix.sfx_lufs` (-19 for the infomercial, -24 for the explainer). Shepherdr's files spread 37 dB when mixed at a
  fixed -6 dB.
- Prefer a motivated sound to a stock gag: a falling mic with feedback beat the sad trombone.
- **Through the connector instead of the key:** `studio sfx --plan` lists the missing kinds with `prompt`,
  `duration_seconds` and `save_to`; for each, `creative_generate_in_flow` (node_type `sfx`, model
  `eleven_text_to_sound_v2`, `generations_count: 1`; it can't set the length, so effects come back at 1-2 s), poll,
  `studio fetch "<content_url>" <save_to>`; then `studio sfx` trims them and flags any take that came back silent
  (retake it with a sharper prompt).

Then `studio mix` (the **mix-and-master** skill) and listen: `open -a "QuickTime Player" audio/mix.wav`.
