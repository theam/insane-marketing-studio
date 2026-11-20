# Which Claude to use: Claude Code, in Terminal or the desktop app's Code tab

**Use Claude Code on your Mac**: in Terminal (`claude`), or in the Claude desktop app's **Code** tab in a **local**
session, which is the same thing in a window. Not Cowork, not a chat, not a cloud session.

The pipeline runs local tools on the Mac: ffmpeg, Node with Playwright and its Chromium, Python, and Swift binaries
that call macOS Vision. It reads and writes a project folder of a few hundred megabytes. So it needs a surface that
runs commands **on the Mac itself**.

## Installing the plugin

| Where | How |
|---|---|
| A shell (Claude Code 2.1.292+) | `claude plugin install insane-studio --marketplace theam/insane-marketing-studio` adds the marketplace and installs the plugin at user scope in one command. |
| A Claude Code session (2.1.275+) | `/plugin install insane-studio --marketplace theam/insane-marketing-studio`: it confirms the new marketplace, then asks for a scope (pick "for you", user scope). |
| Older versions | `claude plugin marketplace add theam/insane-marketing-studio`, then `claude plugin install insane-studio@insane-marketing-studio`. |
| The desktop app | Its local Code sessions read the same `~/.claude` settings as the CLI, so a user-scope install from Terminal (or from a session) shows up there too. The app also has a plugin manager (**+ → Plugins** or **Add plugins**); adding this marketplace from it was not tested. |

Type `/insane-studio:` in a session to see the skills; or just ask for a video.

## The surfaces

| Surface | Runs on the Mac? | Plugins from a GitHub marketplace | claude.ai connectors (ElevenLabs) | Artifacts (storyboard) | Verdict |
|---|---|---|---|---|---|
| **Desktop app → Code tab, local session** | Yes: "Local: runs on your machine with direct access to your files"; no sandbox. The app ships its own copy of Claude Code. | Yes, from the shared settings (see above). | Yes: **+ → Connectors** in a local session with a Claude account. | Yes (desktop 1.13576.0 or later). | **Recommended** for directors who prefer a window. |
| **Claude Code CLI** (Terminal) | Yes. | Yes (commands above). | Yes, automatically, when signed in with a claude.ai account. | Yes (Pro, Max, Team or Enterprise; claude.ai sign-in). | Equivalent; for people comfortable with Terminal. |
| **Cowork** | Anthropic says it "works directly on your computer", but independent reports describe its agent work running in a Linux VM (Apple's Virtualization framework), and it does not read `~/.claude`. macOS Vision (Swift) can't run in a Linux VM. | Yes (Customize → Plugins → Add marketplace). | Yes. | Not documented. | Not recommended: the VM claim is unconfirmed, but the Vision tools and Homebrew binaries would not work there. |
| **Cloud sessions** (claude.ai/code) | No: a remote environment. | Doesn't load plugins installed on the Mac. | — | — | Can't run the pipeline. |
| **Claude chat** (desktop or web) | No local execution. | Plugins add skills, not a shell. | Yes. | Yes. | Can't run the pipeline. |

The claude.ai connectors (the ElevenLabs one included) load in Claude Code only when it's signed in with a claude.ai
account, not with an API key. Without them, use an ElevenLabs API key (see elevenlabs-mcp.md).

Evidence (read November 2026; Claude Code 2.1.317-2.1.328, Claude desktop 4.16336.0 on the test Mac):
code.claude.com/docs/en/desktop.md, /discover-plugins, /plugins/install.md, /mcp.md, /skills.md, /artifacts.md,
/sandboxing.md; claude.com/docs/plugins/overview, /cowork/overview.md, /cowork/guide/plugins.md; for the Cowork VM,
secondary reports (The Hacker News, July 2026; 9to5Mac; Obot). Not verified by driving the desktop app's window: that a
user-scope plugin installed from the CLI shows up in the Code tab is the documented behaviour.
