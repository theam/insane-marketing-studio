# Lessons from the INSANE Shepherdr infomercial

What the production learned, as rules, each with where it comes from. The production ran 20-22 October 2026: Claude
Code sessions did the production work and a human director gave the notes (see case-study-shepherdr.md). Quotes are the
director's notes, translated from Spanish. Version numbers (v2-v6) are the production's own cuts, logged in its version
log.

## Script, tone and humour

- **Infomercial structure, starting from the problem**: "an infomercial structure, starting from the problem", framed
  as the viewer's problem.
- **Nerdy, never sexualized**: "let's not use that device ourselves; let's be nerdier".
- **Wink at references; never copy them**: "I don't want us to literally copy the backgrounds and lines" of the video
  being parodied; "winks… not a remix".
- **Escalate to the absurd with current memes, and say who said what**: "10, 100, no… 1000 AGENTS"; "let's say 'Dario
  said…' … to place the meme better"; that week's Tesla Roadster reveal went in because "it's a meme".
- **Clarity beats cleverness**: "the Manhattan bit doesn't land"; a us-east-1 joke was rejected for the same reason.
- **Cut the weakest part and cap the length**: "2:30 at most; which part would you say is the weakest?"; the
  testimonials went ("they drop the intensity a lot"), and so did "Season with YAML".
- **A self-aware hook**: "Fed up of AI Psychosys?" became the opening line.
- What the director loved, which must survive: "type to it, shout to it!"; the absurd recipe (a senior engineer, a Siberian tiger, a
  cubic metre of coffee, a flying Roadster, blended); the offer and the spacetime gag.

## Voice and pacing

- **Takes in pieces, so one line can be redone**: "generate the audio in pieces". → `studio voice` makes one take per
  sentence; `audio/lines/retakes.json` redoes one.
- **No whispers in the infomercial**; in the explainer, no forced laughs: "remove the laughs, play only with the tone".
- **Check pronunciation with speech-to-text**: the voice said "4th mension" for "fourth dimension". → `studio scribe` +
  `studio timing --check`.
- **Speed up by time-stretching, not regenerating**: "speed the audio up by about 10%… without regenerating". TTS speed
  barely changed the length; `atempo` does. The narrator ran at 1.32×.
- **The frantic 80s toy-commercial pace**: "the frantic rhythm of 80s toy commercials". Takes are placed by their
  audible edges (silencedetect at -40 dB) with gaps of 0.05/0.10/0.15 s: pauses went from 16.4 s to 1.5 s and the
  narration from 1:59.4 to 1:47.9 (v6).
- **A cameo line trimmed and sped up**: "That's so agentic." ran 1.15× and 0.08 s after the narrator.
- **A character voice designed from her canon**; it sounded too clean, so a telephone filter: "as if she were talking
  on the phone".

## Music

- **The bed runs the whole clip, audible, and changes with the story**: "the music should last the whole clip and vary
  the instruments". → one ElevenLabs Music composition plan whose sections start at the narration's turning points.
- **Re-fit per section, not one global stretch**: v4 stretched the whole take ×1.0915; v5 fit it chunk by chunk
  (`fit_music.py`). v6 ran at 1.15-1.27×, flagged as the main audio risk: beyond ±10 %, compose again.
- **The space is a filter**: "when the window opens we must remove the filter on the music".
- **Stop the music dead on the gag**: "at that moment the music stops dead".
- **End card: the song back to the end of its hook, then black.**

## Sound effects

- **Nothing shrill**: "swap the very loud beeping effects for something… less irritating". Airhorn, alarm, laser,
  buzzer, slide whistle and chiptune were replaced by soft takes.
- **Loudness by family, not one fixed gain**: the files spread 37 dB (-40.6 to -6 LUFS) at a fixed -6 dB. Impacts
  +3 LU, tonal blips -4 LU and low-passed.
- **Trim each file's leading silence** so it hits on its frame.
- **A motivated sound beats a stock gag**: a falling mic with feedback instead of a sad trombone.

## Picture and motion graphics

- **Deterministic HTML rendered frame by frame**: `window.render(t)` and `window.DURATION`, Playwright screenshots piped
  to ffmpeg. Every animation follows a cue from the narration's word timestamps, so a changed line re-times everything.
- **Impact, big, with real photo cut-outs, not drawings**: "big Impact is much more meme".
- **Exaggerate and animate physically**: fire on the reveal, explosions, ingredients falling into the blender instead of
  popping in. **Effects on stills stand in for video**: "effects on images, without real video".
- **Cheap and homemade beats polished**: "much cheaper and more homemade". Full body, no awkward crops.
- **Show a real UI whole and clean**: "show the real UI better".
- **End on full black held for at least 15 frames**, not mid-fade (fixed with 18 black frames, YAVG 0).

## Generated video (Seedance 2.5 on Higgsfield)

- **Lock the base before buying credits**: "once the base is right I'll buy more credits".
- **Estimate first, cap in the runner, ledger and idempotency keys** (`seedance.py`; the cap stopped the run).
- **Fix the plate before generating; the plate is the shot's first state**: "generate a new plate before generating";
  "in the plate the window is already open".
- **Change the camera when the geometry keeps failing**: the last shot was made from outside the window, from the
  previous take's last frame, with no desk in frame.
- **Chain shots from the previous take's frame.** **If the join still shows, drop the shot.**
- **Morphs between takes read as strange camera moves**: "a weird movement" (frames 3693-3711); the morphed shot was
  dropped. Cut instead.
- **Reject the CG look**: "the goats look like 3D animation". Keep some motion in the background.
- **Remove dead holds by dropping frames**: 1.4 s of eye roll became 0.5 s, dropped frames blended 1-2-1.
- **Reference-to-video does NOT follow the reference audio's timing**: transcribe the take's own audio with Scribe and
  place the lines at those word times (see failures.md).

## Compositing

- **Corner-pin a UI exactly**: "each of the corners must fit perfectly" → macOS Vision image registration per frame,
  smoothed, CSS `matrix3d`.
- **Cut out subjects with Vision's foreground mask**; plates with Codex image generation (OpenRouter refuses photoreal
  plates of a character).
- **Check lip sync by eye**: "look closely at the lip sync".

## Review loop

- **Show the script before generating audio**, next to the reference: "open the script for me before generating audio".
- **Open every review file in QuickTime.**
- **A storyboard Artifact with stable shot ids.** The director's notes still came in chat, by shot id, frame number or
  timecode; the Artifact's notes collection was empty when read. → Accept both.
- **A new variant goes in a new folder**; the approved one stays.
- **Ask for a cost estimate before generating.** Overnight runs stay within a stated budget.
- **The director invites proposals**: options A/B/C with a recommendation; the director mixed them.
- **Every round: what changed, known gaps, spend**, plus a version log (each project's `log.md`).
- **Commit everything that can't be regenerated, release the videos.**

## Derivatives

- **The social cut is cut from the long one at its own cut times, then re-mixed**: each stretch starts one frame after
  its cut, the voice keeps its cut's first sound, the music is one continuous slice per section starting on its hit.
- **Covers are HTML rendered with Playwright**: a PNG and a JPEG under 5 MB for X. No spoilers; the mascot must appear.
- **A making-of remixes a song's stems in whole bars on its downbeats.** Making-ofs show the prompts, lightly cleaned
  up.

## Content

See content-rules.md: English on screen; full name and title on quotes; no confidential screens; licensed photos of
real people with credits; Claudia's credit from her MCP; AI disclosure; no cloning a voice without rights.

## Why this kit exists

The video worked, and the same style was wanted for much more than one launch: the purpose is brand, not hard
sell. Two registers, each in its own folder: a calm corporate cut for a company's channels and a crazy cut for a
launch.
