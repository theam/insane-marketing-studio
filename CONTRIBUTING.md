# Contributing

Thanks for wanting to make the studio better. Issues and pull requests are welcome: a lesson from a production, a new
block for the engine, a new style, a fix. Please be kind; the [code of conduct](CODE_OF_CONDUCT.md) applies everywhere.

## Where things go

- **A lesson from a production** goes in `references/lessons.md` (the rule, then where it came from), and into the
  skill it changes.
- **A new building block** goes in the style's `engine/<style>.js` and `references/engine.md`, with a use in the
  style's starter `templates/<style>/video.html` so it's exercised.
- **A new style** is `engine/<style>.css` + `engine/<style>.js` + `templates/<style>/` (`video.html`, `script.md`,
  `project.json`, `music.json`, `cover.html`, `short.json`) + `references/style-<style>.md`, and its name in
  `scripts/new_project.py`.
- **A new tool** is a script in `scripts/` run through `scripts/studio` (add the command and a line to its COMMANDS).
  Python uses only the standard library; Node uses only Playwright.
- **Skills** (`skills/*/SKILL.md`) are written for Claude, and the person Claude talks to may not be an engineer: they
  never edit code, never type a command and never paste a key into a chat.
- Bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` together, and add a line to
  [CHANGELOG.md](CHANGELOG.md).

## Try your change

Load your working copy instead of the installed plugin:

```sh
claude --plugin-dir .
```

Before a pull request:

```sh
claude plugin validate .
K=$PWD
$K/scripts/studio new /tmp/x && cd /tmp/x
$K/scripts/studio timing --placeholder && $K/scripts/studio points && $K/scripts/studio sheet && open out/review/sheet.png
$K/scripts/studio scan $K
```

(`studio new` makes a starter project; `timing --placeholder`, `points` and `sheet` render a contact sheet of it without
any API key; `scan` looks for secrets.) Projects carry a copy of the engine, so a change here never alters a video
already made.

## Assets

Only add pictures, sounds or music you have the right to release under the repository's terms (code MIT, images
CC BY 4.0), and credit them in the folder's `CREDITS.md`. No photos of real people, no logos but your own.
