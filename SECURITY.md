# Security

The studio runs commands on your Mac and handles API keys, so we take reports seriously.

**To report a vulnerability**, use GitHub's private reporting: the repository's **Security** tab → **Report a
vulnerability**. Please don't open a public issue for it. We'll answer within a few working days.

How the kit treats secrets:

- API keys live in one file outside every project, `~/.config/insane-marketing-studio/keys.env`, readable only by you,
  and are loaded only for the steps that spend. Never paste a key into a chat with Claude.
- `studio scan <folder>` looks for keys and tokens before anything is pushed; the deliver skill runs it before every push.
- Nothing is published, posted or made public without an explicit yes from the person running the production.
