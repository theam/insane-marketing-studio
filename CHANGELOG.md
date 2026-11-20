# Changelog

## 0.2.0 · 2026-11-20 · Insane Marketing Studio

The kit goes open source under its new name.

- Renamed from "Marketing Video Studio": plugin `insane-studio`, marketplace `insane-marketing-studio`. The first
  `studio setup` moves an earlier install's tools and keys file to the new paths.
- One-command install with `claude plugin install insane-studio --marketplace theam/insane-marketing-studio`; the first
  video sets up the tools. The GitHub-only bootstrap script is gone.
- Licences: code MIT, the kit's images CC BY 4.0; The Agile Monkeys' wordmarks are trademarks, not licensed
  (`references/credits-and-licenses.md`).
- No music ships with the kit: ElevenLabs Music's terms don't allow sharing generated music for others to reuse, so the
  Shepherdr score stays with the team. `studio fit-music --library NAME` lays a score you have the rights to, from
  `~/.local/share/insane-marketing-studio/music/` (`library/music/README.md`).
- End cards and covers no longer show The Agile Monkeys' wordmark by default: pass your own logo.
- `studio master` no longer drops the last frames of black: the picture sets the length and the sound is padded to it.
- References and skills rewritten for anyone: no private links; the director's notes in English.
- A new sample: the Insane Marketing Studio infomercial (README and the v0.2.0 release).

## 0.1.1 · 2026-11-03

Fixes from the first end-to-end run: silent sound-effect takes flagged and skipped, the storyboard opens from the disk,
connector estimates documented, the end-card music no longer fades to silence.

## 0.1.0 · 2026-11-03

First version, for The Agile Monkeys' marketing team: the skills, tools and references behind the INSANE Shepherdr
infomercial.
