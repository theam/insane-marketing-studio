# Failures and their fixes

What broke in the Shepherdr production (and in building this kit), why, and what fixed it. Quotes are the director's
notes, translated from Spanish.

| # | What broke | Why | What fixed it |
|---|---|---|---|
| 1 | **Lip sync** off in the epilogue's "Hey! … I'm trying to work here!" | Seedance's reference-to-video ignores the reference audio's timing: the mouth follows the take's own generated speech. The edit also cut the shot at 3.6 s, mid-line. | Scribe on the take: "Hey" at 1.12 s, the line at 3.28-4.68 s. The clean lines were moved to 1.04 s and 3.18 s (under 0.02 s off per word) and the shot extended. |
| 2 | **Plate geometry**: the room's layout and her head direction changed between takes; the desk kept moving walls. | Each plate and take re-imagines the room. A master plate plus a floor plan as references didn't hold it. | Change the camera: the last shot was generated from the previous take's last frame, seen from outside the window, with no desk in frame. |
| 3 | **Morph** between two takes read as "a weird movement". | The second take reframed the first one's frame about 1.2× with parallax: matching the crop reached only 25.9 dB, so an optical-flow morph and a dissolve bridged it. | The shot was dropped. Cut between takes; don't morph. |
| 4 | **Loud beeps.** | Every effect went in at a fixed -6 dB while the files spread 37 dB (-40.6 to -6 LUFS). | A loudness target per family and six softer regenerated variants, aliased in place of the shrill ones. |
| 5 | **Music stretched too far.** | v4: one global ×1.0915; v6: per section, but at 1.15-1.27× after the narration tightened. | Fit per section (`fit_music.py`); flagged beyond ±10 %. Compose a new take when it sounds rough. |
| 6 | **Slow pacing.** | TTS speed barely changed the length; the TTS word timestamps leave silent tails: 16.4 s of silence over 59 pauses. | `atempo` for speed; takes placed by audible edges (silencedetect -40 dB), gaps 0.05/0.10/0.15 s: 1:59.4 → 1:47.9. Fixed-length beats were shortened; a 1.4 s hold became 0.5 s with blended dropped frames. |
| 7 | **Ended mid-fade.** | The fade to black ran to the last frame. | Hold full black at least 15 frames; verified the last frames' YAVG is 0: 18 black frames. `studio master` now checks it. |
| 8 | **OpenRouter refused** the character's photoreal plates (4 HTTP 400s: "InputImageSensitiveContentDetected.PrivacyInformation"). | BytePlus's filter on images that may contain a real person. Goats went through. | Character shots on Higgsfield; never alter an image to get past a filter. |
| 9 | **Higgsfield ran dry mid-batch** (6 jobs: "credit balance is too low"). | The runner's cap was $90, above the account's real balance, which can't be read through the API. | Stop, report, ask for a top-up. Quote real spend from the provider's billing page. |
| 10 | **Codex blocked a character plate** (probably the word "glamorous"); without face references her likeness drifted. | Content filter; no references attached. | Rephrase; always attach face references for a character. |
| 11 | **Explainer music nearly inaudible.** | 14-20 dB under the voice, plus a -3 dB pan bug. | 6 dB under between phrases, 13 dB under speech. The kit's default: 6 dB under, 7 dB more under speech. |
| 12 | **Seedance identity swap mid-shot**, a doubled star clip, an Apple logo on the iMac. | Model artefacts. | Re-take or drop; the logo removed with ffmpeg `delogo` (`picks.json` → `delogo`). |

## Found while building this kit (3 Nov 2026)

| # | What broke | Fix in the kit |
|---|---|---|
| 13 | The ElevenLabs key kept in the production's project folder had been revoked ("Invalid API key"). | Keys live in one per-person file outside every project (`studio keys`); `studio doctor` reports whether each is set. The sample was made through the ElevenLabs connector, with no key. |
| 14 | Homebrew's ffmpeg 9 has no `drawtext` (no freetype). | No kit tool uses `drawtext`: contact sheets are labelled in HTML and screenshotted. |
| 15 | Playwright 1.64 refuses Node 18 ("requires Node.js 20 or higher"). | `studio` picks Node 20+ (Homebrew's or the newest nvm one); `studio setup` installs it if none. |
| 16 | A script whose prose mentioned "## Script" broke the parser. | The heading is matched only at the start of a line. |
| 17 | The restricted ElevenLabs connector has no music. | `studio fit-music --library <name>` re-cuts a library score section by section (a track you have the rights to, with a sections file); composing needs the key or the full connector. |
| 18 | The Shepherdr masters went out full-range `yuvj420p`, tagged BT.601 (`bt470bg`), for HD video: some platforms re-encode that with shifted levels. | `studio render` converts to limited range and tags BT.709; `studio master` checks `yuv420p`. |

## Found by the sample run (3 Nov 2026: a fresh install, the entry skill, no key)

| # | What broke | Fix in the kit |
|---|---|---|
| 19 | A sound effect came back nearly silent; trimming its leading silence emptied it and the mix boosted it +12 dB, with no warning. | `studio sfx` flags an empty or silent take (keeps a too-quiet take untrimmed); `studio mix` never boosts a silent file and lists it. |
| 20 | The connector's `estimate_only` misses both ways: Scribe 7.9 credits estimated, 116.8 charged; an effect 60.6 estimated, 16.7 charged. | spend.md: record each run's own price; budget Scribe at about 5.5 credits a second. |
| 21 | The score's "finale" section decays to near silence 2.5 s in, so a longer end card played silent. | The template's last chunk uses "butwait"; the score's notes say what each section does. |
| 22 | The template's explosions covered the words it celebrates (the title, the end card). | Moved to the corners and made smaller. |
| 23 | The connector's effect tool can't set a length (the docs said it could). | elevenlabs-mcp.md and the skill corrected. |
| 24 | No Artifact tool in a headless session: the storyboard step had no fallback. | `studio board` also writes `board.js`, so `board/index.html` opens from the disk; the skill says what to do without the tool. |
| 25 | `studio music --dry-run` before the voice crashed with a traceback; `studio doctor` called the key missing when the connector covers it. | A plain message saying the order; the key is optional in doctor, with the connector named. |
| 26 | `studio` on the PATH is a symlink and didn't find its own folder (`studio keys`, `studio doctor` from Terminal failed). | It resolves the link first. |
