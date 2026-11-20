---
name: storyboard
description: Build and publish the storyboard review for a video — a contact sheet of every cut and a claude.ai Artifact with one card per shot where the director marks OK or Change and leaves notes — and read the notes back. Use for the board checkpoint, for every later review round, and whenever someone asks for stills, frames at given times or a contact sheet.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Bash(cp *), Read, Write, Edit
---

# Storyboard and review

The director judges pictures, not descriptions. Every review round gives them: a contact sheet, the storyboard Artifact
(on claude.ai, shareable with the team), and stills of anything they ask about. Run every command from the project
folder with `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`).

## Stable shot ids

Give every cut in `video.html` a unique `label` (`cut(at, bg, build, draw, { label: 'price' })`). The label is the shot
id on the board, in notes and in `log.md`, and it survives re-edits; cuts without one get `s01`, `s02`… by order, which
shift when a cut is added. Keep ids short and human: `hook`, `title`, `feature-1`, `price`, `end card`.

## The round

1. `studio points` (the edit's cuts and duration), then `studio sheet` → `out/review/sheet.png`, one labelled tile per
   cut (`#n · id · time`). Open it: `open out/review/sheet.png`.
2. `studio board` → `board/board.json`, `board/board.js` and `board/img/<id>.jpg` (every shot's frame, time span, the
   words spoken over it and its section), and the ready-made page `board/index.html` (copied once per project).
   `open board/index.html` shows it straight from the disk.
3. Publish it as an Artifact with the Artifact tool:
   - `file_path`: the project's `board/index.html`; `icon`: `film`; `description`: "Storyboard of <title>, v<n>".
   - `files`: `{"board.js": "board/board.js", "board.json": "board/board.json", "img/<id>.jpg": "board/img/<id>.jpg", …}` (every image).
   - `capabilities`: `{"db": {}, "user": {"scopes": ["profile"]}}` on the first publish; omit it on later publishes.
   - Republish the same `board/index.html` for every new version: the link stays, and notes stay attached to their
     shot ids. Save the link in `brief.md`.
   Then check the notes collection once (`ArtifactData` → `list`, collection `notes`): empty is expected.
   **No Artifact tool in this session** (Claude Code run headless, or signed in with an API key): skip the publish,
   open `board/index.html` and the contact sheet for the director, and take the notes in chat by shot id.
4. Tell the director in two lines: the link, and "mark each shot OK or Change and say what to change; or just tell me
   here by shot id or timecode."
5. **Read the notes** when they say they're done (or at the next turn): `ArtifactData` `list` on collection `notes`
   (one document per shot id: `status` ok/change, `note`, `by`, `at`). Notes may also come **in chat** by shot id,
   timecode or frame number — in the Shepherdr production they all did. Log every note verbatim in `brief.md` against
   its shot id, apply every one, and say which you applied in the round's report. When two notes conflict, the later
   one wins.

## Stills and sheets on request

- `studio stills 12.4,15` → `out/stills/t012.40.png`… (from the page, before any render).
- `studio sheet out/<name>.mp4` → frames of the finished video at every cut; `studio sheet out/<name>.mp4 3,7.5,12` at
  given seconds. A frame number n is n / fps seconds.
- Before the final render of a round with notes on specific shots, show those shots' stills first.
