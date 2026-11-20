# Setup, in detail

The [README](../README.md) has the short version: install the plugin, then ask Claude for a video. This page is
everything around it: what you need, what the first run installs, the two ways to give the studio ElevenLabs, updating,
and what to do when something goes wrong. You never need to read code.

## What you need

- **A Mac** with macOS 14 or newer and about 3 GB free (the studio uses macOS's own image recognition and fonts).
- **Claude Code**: the `claude` command in Terminal, or the Code tab of the Claude desktop app in a **local** session.
  Both read the same plugins and settings. Cowork, the claude.ai chat and cloud sessions can't run the studio: it runs
  tools on your Mac ([why](../references/surfaces.md)).
- **[Homebrew](https://brew.sh)**, the Mac's installer for tools. If you don't have it, paste the line from brew.sh into
  Terminal (it asks for your Mac password; you type it blind) and follow its "Next steps".
- **[ElevenLabs](https://elevenlabs.io)** for the voices, music and sound effects: an account with a paid plan if you'll
  publish what you make (check your plan's commercial-use terms). A video like the one in the README costs well under a
  dollar of credits.
- Optional: **ChatGPT** for new pictures (Codex image generation, on your ChatGPT plan), **Higgsfield** for generated
  video clips (paid per second; the studio always shows the cost and asks first).

## Install

In Terminal:

```sh
claude plugin install insane-studio --marketplace theam/insane-marketing-studio
```

Or inside a Claude Code session in the terminal, type:

```text
/plugin install insane-studio --marketplace theam/insane-marketing-studio
```

and choose **Install for you**. The desktop app reads the same plugins as the terminal, so either way the studio shows
up in its Code tab too (its own plugin manager, **+ → Plugins**, lists marketplaces you've added). On Claude Code older than 2.1.292 (shell) or 2.1.275 (session), add the marketplace
first: `/plugin marketplace add theam/insane-marketing-studio`, then `/plugin install insane-studio@insane-marketing-studio`.

Start a new session (or run `/reload-plugins`) and type `/insane` to see the studio's skills.

## The first run

Ask for a video ("make me an insane infomercial for my app") or say "set up the Insane Marketing Studio". Claude checks
your Mac and installs what's missing, once, with Homebrew and npm:

| What | Why |
|---|---|
| ffmpeg | Cuts, mixes and encodes the video. |
| Node 20+ and Playwright's Chromium (in `~/.local/share/insane-marketing-studio`) | Renders the motion graphics frame by frame, like a screenshot per frame. |
| macOS Vision tools (compiled from `scripts/vision/`) | Cut-outs and screen tracking. Needs Apple's command line tools (`xcode-select --install`). |
| git-lfs, gh | Saving a finished project to GitHub, if you want to. |
| A keys file (`~/.config/insane-marketing-studio/keys.env`, readable only by you) | API keys, if you use any. |

It takes about five minutes, mostly downloads. Claude asks before running each command; the first time you can allow
the studio's commands for the session.

## ElevenLabs: a key or the connector

Use either; the key gives you everything.

**A · An API key (recommended).** On elevenlabs.io: **Developers → API keys → Create**, with access to Text to Speech,
Sound Effects, Music, Speech to Text and Voices (read), and a credit limit. Then tell Claude "open my studio keys file":
it opens in TextEdit; paste the key after `ELEVENLABS_API_KEY=`, save and close. **Never paste a key into the chat** (or
Slack, email, a document): if that happens, delete it on the website and make a new one.

**B · The ElevenLabs connector (no key).** In Claude: **Settings → Connectors → ElevenLabs**, connect your account, and
restart the session. Claude can then cast voices (with previews to listen to), make the narration and the sound effects,
and time every word with Scribe. It **can't compose music**: for that without a key, add the *full* ElevenLabs connector as
a custom connector (**Settings → Connectors → Add custom connector**, URL `https://api.elevenlabs.io/v1/mcp`), or bring
a track you have the rights to ([library scores](../library/music/README.md)).
[What each route can do, tested](../references/elevenlabs-mcp.md).

The README's video was made without a key: the voice, the effects and the word timing through the connector.

## Updating

```sh
claude plugin update insane-studio@insane-marketing-studio
```

or `/plugin` → **Installed** → Insane Marketing Studio → **Update now**. Then say "run the studio setup" once, in case a
tool changed. Projects carry their own copy of the engine, so an update never changes a video you already made.

## If something goes wrong

| You see | Do this |
|---|---|
| `/insane` shows nothing | Start a new session or run `/reload-plugins`. Check `claude plugin list` shows `insane-studio`. |
| `Homebrew isn't installed` | Install it from [brew.sh](https://brew.sh), close and reopen Terminal (or restart the desktop app), and ask again. |
| `The Swift compiler isn't here` | Paste `xcode-select --install` in Terminal, accept the dialog, then "run the studio setup" again. Only cut-outs need it. |
| `Playwright requires Node.js 20 or higher` | "Run the studio setup": it installs a newer Node next to yours. |
| `Invalid API key` | The key was deleted or mistyped: make a new one (A above). |
| No ElevenLabs tools in the session | Connect the connector (B above) and start a new session, or use a key. |
| Anything else | Ask Claude: "run the studio doctor and fix what's missing". Still stuck? [Open an issue](https://github.com/theam/insane-marketing-studio/issues). |

## Uninstall

```sh
claude plugin uninstall insane-studio@insane-marketing-studio
claude plugin marketplace remove insane-marketing-studio
rm -rf ~/.local/share/insane-marketing-studio ~/.local/bin/studio
```

Your keys file stays in `~/.config/insane-marketing-studio/` until you delete it.
