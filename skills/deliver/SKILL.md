---
name: deliver
description: Deliver a finished video — a private GitHub repository for the project with Git LFS for every non-regenerable file (every AI take, rejected ones too), renders left out, a secret scan before every push, the videos and covers in a GitHub release, and the credits, AI disclosure and posting copy. Use when a video is approved, or for "save the project", "share the files", "make a release", "write the post".
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(git *), Bash(gh *), Bash(open *), Read, Write, Edit
---

# Delivery

**Ask before anything leaves this Mac**: creating a repository, pushing, making a release, posting. Say what, where
and who will see it, and wait for a yes. Never make a repository public without the director's explicit yes; never post to chat or social media yourself.

## What gets committed

The rule (from the Shepherdr production): **everything that can't be regenerated deterministically is committed; media goes
through Git LFS** (the project's `.gitattributes` already routes mp3, wav, mp4, png, jpg… to LFS).

- **Committed:** the script and its earlier versions, `project.json`, `music.json`, `sfx.json`, `video.html`,
  `cover.html`, `short.json`, the engine copy, `brief.md`, `log.md`, `gen/` (shots, picks, the ledger), every
  generated take with its alignment (`audio/lines/*.mp3` and `.json`, `audio/music-take-*`, `audio/sfx/raw/`, clips in
  `gen/clips/`), every plate candidate (rejected ones too), cut-outs and their `CREDITS.md`, board data.
- **Left out** (`.gitignore`): renders (`out/`), the assembled audio (`voice-lead.wav`, `mix.wav`, `music.mp3`,
  processed takes), extracted clip frames, Impact (a macOS font that may not be redistributed), any `.env`.

## Steps

1. `studio scan` in the project: **no push while it reports anything.** Keys live only in
   `~/.config/insane-marketing-studio/keys.env`.
2. Commit: `git add -A && git commit -m "<title>: v<n>"` (the project was created as a git repository).
3. With the director's yes, the repository: private, in the account or organization they name (ask), named after
   the video: `gh repo create <org>/<name>-video --private --source . --push`. If they can't create repositories there,
   they ask an admin; don't fall back to a public or personal one without asking.
4. The release, with the director's yes: `gh release create v1.0.0 out/<project>.mp4 out/<project>-social.mp4
   out/cover.jpg --repo <org>/<name>-video --title "<title>" --notes-file out/release-notes.md`. Write the notes first:
   what each file is (length, 1920×1080, 30 fps, -14 LUFS), the credits, the AI disclosure.
5. A README in the repository: what it is, how it rebuilds (`studio voice`, `timing`, `points`, `fit-music`, `mix`,
   `render`, `master`, all from committed takes without spending), credits.

## Credits and disclosure (in the post, the release notes and on the end card)

- **AI-generated content:** say what was generated and with what: "Voice, music and sound effects generated with
  ElevenLabs; images with Codex image generation; footage with Seedance 2.5 on Higgsfield."
- **Photos of real people / third-party images:** author, licence, source, as in `assets/cutouts/CREDITS.md` (CC BY and
  CC BY-SA require it wherever the video is posted).
- **Claudia**, if she appears: "Claudia is an open character by @anabology · claudia.gallery".
- **Music** you didn't compose for this video: its title and owner.

See `${CLAUDE_PLUGIN_ROOT}/references/credits-and-licenses.md`. Draft the posting copy (LinkedIn, X) for the
director, with the credits; they post it.
