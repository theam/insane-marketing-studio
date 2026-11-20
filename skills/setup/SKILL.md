---
name: setup
description: Set up the Insane Marketing Studio on this Mac, or fix it when something is missing — tools (ffmpeg, Node, Playwright, macOS Vision tools), the keys file, and the ElevenLabs connector. Use when someone says "set me up", "install the studio", "set up the Insane Marketing Studio", "it says something is missing", or when `studio doctor` reports a MISS.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(${CLAUDE_PLUGIN_ROOT}/setup/setup.sh), Bash(open *), Read
---

# Set up the studio

The person may not be an engineer. Do the work; explain each step in one sentence; never ask them to read code. The
first setup takes about five minutes, mostly downloads: say so before you start.

1. Run `"${CLAUDE_PLUGIN_ROOT}/scripts/studio" doctor` and read the result to them in plain words.
2. **Tools missing** (ffmpeg, Node 20+, git-lfs, gh, Playwright, Chromium, Vision tools): run
   `"${CLAUDE_PLUGIN_ROOT}/scripts/studio" setup`. It installs with Homebrew and is safe to repeat.
   - If Homebrew itself is missing, the person must install it in Terminal (it asks for their Mac password, which you
     must never handle). Send them to https://brew.sh to copy its one line into Terminal, follow its "Next steps", then restart
     this session (or the desktop app) so the new PATH is seen.
   - If the Swift compiler is missing, they run `xcode-select --install` (a macOS dialog) and you run setup again.
     Only cut-outs and screen tracking need it.
3. **Keys.** Run `"${CLAUDE_PLUGIN_ROOT}/scripts/studio" keys`: it opens their keys file in TextEdit. Tell them where to get
   each key (the comments in the file say it), to paste it after the `=`, save and close. **Never ask them to paste a
   key into the chat**; if they do, tell them to revoke it on the service's site and make a new one. Run doctor again:
   it shows each key as set or not set, never the value.
   - **ElevenLabs** is required for every video (voice, music, effects, Scribe). A key with a credit limit is the
     recommended setup: it gives word timing in one call, music with sections, and batch takes.
   - **Higgsfield** only for generated clips; **OpenRouter** optional.
   - **Codex** (plates): no key; they install the Codex app or CLI and sign in with ChatGPT (`codex login`).
4. **The ElevenLabs connector.** Check whether this session has ElevenLabs tools (search your tools for
   `creative_generate_speech`). If not, they add it at claude.ai → Settings → Connectors (the "ElevenLabs" connector)
   and restart Claude. It lets them cast voices by listening to previews, design a voice, make speech takes and effects,
   and transcribe with Scribe, all without a key. It has **no music**: music needs the key, or the full ElevenLabs
   connector added as a custom connector with the URL `https://api.elevenlabs.io/v1/mcp`. Explain the difference with
   `${CLAUDE_PLUGIN_ROOT}/references/elevenlabs-mcp.md`.
5. Finish with a test: `"${CLAUDE_PLUGIN_ROOT}/scripts/studio" new ~/Videos/studio-test`, then in that folder
   `studio timing --placeholder`, `studio points`, `studio sheet`, and open `out/review/sheet.png`. If they see eight
   colourful frames, the studio works. Delete the test folder after if they want.
