#!/bin/bash
# studio setup: installs what the kit needs on this Mac. Safe to run again: it only adds what's missing.
#   - Homebrew packages: ffmpeg, node (20 or newer), git-lfs, gh
#   - Playwright and its Chromium, shared by every project (in ~/.local/share/insane-marketing-studio)
#   - the macOS Vision tools (cut-outs, screen tracking), compiled from scripts/vision/*.swift
#   - your keys file (~/.config/insane-marketing-studio/keys.env), created empty, readable only by you
set -e
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STUDIO_HOME="${STUDIO_HOME:-$HOME/.local/share/insane-marketing-studio}"
KEYS="${STUDIO_KEYS:-$HOME/.config/insane-marketing-studio/keys.env}"
PLAYWRIGHT_VERSION=1.64.1
say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# Homebrew may be installed but not on this shell's PATH (a fresh install, or the desktop app's environment).
for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do command -v brew >/dev/null || { [ -x "$b" ] && eval "$("$b" shellenv)"; }; done
if ! command -v brew >/dev/null; then
  echo "Homebrew isn't installed. Install it from https://brew.sh (paste its one line in Terminal; it asks for your Mac"
  echo "password), then run this again."; exit 1
fi
eval "$(brew shellenv)"

# Earlier versions of the kit were called "marketing-video-studio": move their tools and keys file over.
OLD_HOME="$HOME/.local/share/marketing-video-studio"; OLD_KEYS="$HOME/.config/marketing-video-studio/keys.env"
[ -d "$OLD_HOME" ] && [ ! -e "$STUDIO_HOME" ] && mkdir -p "$(dirname "$STUDIO_HOME")" && mv "$OLD_HOME" "$STUDIO_HOME" && echo "moved $OLD_HOME → $STUDIO_HOME"
[ -f "$OLD_KEYS" ] && [ ! -e "$KEYS" ] && mkdir -p "$(dirname "$KEYS")" && mv "$OLD_KEYS" "$KEYS" && rmdir "$(dirname "$OLD_KEYS")" 2>/dev/null; true

say "1/5 Homebrew packages"
need=()
command -v ffmpeg >/dev/null || need+=(ffmpeg)
command -v git-lfs >/dev/null || need+=(git-lfs)
command -v gh >/dev/null || need+=(gh)
# Node 20 or newer: the first on the PATH, Homebrew's, or the newest nvm one (the studio command picks it the same way).
nodeok=0
for n in "$(command -v node)" /opt/homebrew/bin/node /usr/local/bin/node $(ls -d "$HOME"/.nvm/versions/node/v*/bin/node 2>/dev/null); do
  [ -x "$n" ] && [ "$("$n" -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)" -ge 20 ] 2>/dev/null && { nodeok=1; NODEBIN="$(dirname "$n")"; break; }
done
[ $nodeok = 1 ] && export PATH="$NODEBIN:$PATH" || need+=(node)
if [ ${#need[@]} -gt 0 ]; then echo "installing: ${need[*]}"; brew install "${need[@]}"; else echo "ffmpeg, node, git-lfs and gh are installed"; fi
git lfs install --skip-repo >/dev/null && echo "Git LFS ready"

say "2/5 Playwright and Chromium (the renderer's browser)"
mkdir -p "$STUDIO_HOME"
if [ ! -f "$STUDIO_HOME/node_modules/playwright/package.json" ] || ! grep -q "\"version\": \"$PLAYWRIGHT_VERSION\"" "$STUDIO_HOME/node_modules/playwright/package.json"; then
  (cd "$STUDIO_HOME" && [ -f package.json ] || echo '{"name":"insane-marketing-studio-tools","private":true}' > "$STUDIO_HOME/package.json"
   cd "$STUDIO_HOME" && npm install --no-audit --no-fund --loglevel=error "playwright@$PLAYWRIGHT_VERSION")
fi
(cd "$STUDIO_HOME" && npx --yes playwright install chromium >/dev/null) && echo "Chromium ready"

say "3/5 macOS Vision tools"
mkdir -p "$STUDIO_HOME/bin"
if ! command -v swiftc >/dev/null; then
  echo "The Swift compiler isn't here. Run: xcode-select --install  (then this again). Only cut-outs and screen tracking need it."
else
  for f in "$KIT"/scripts/vision/*.swift; do
    b="$STUDIO_HOME/bin/$(basename "$f" .swift)"
    if [ ! -x "$b" ] || [ "$f" -nt "$b" ]; then swiftc -O "$f" -o "$b" 2>/dev/null && echo "built $(basename "$b")" || echo "could not build $(basename "$f")"; fi
  done
  echo "Vision tools ready"
fi

say "4/5 Your keys file"
mkdir -p "$(dirname "$KEYS")"
[ -f "$KEYS" ] || cp "$KIT/setup/keys.env.example" "$KEYS"
chmod 600 "$KEYS"
echo "$KEYS (only you can read it). Ask Claude to open it, or run: studio keys"

say "5/5 The studio command and a check"
# `studio` on your PATH, for running a step yourself in Terminal (Claude runs it from the plugin either way). It points
# at the marketplace's copy, which stays put across updates; another program called `studio` is never replaced.
TARGET="$HOME/.claude/plugins/marketplaces/insane-marketing-studio/scripts/studio"; [ -x "$TARGET" ] || TARGET="$KIT/scripts/studio"
LINK="$HOME/.local/bin/studio"; mkdir -p "$HOME/.local/bin"
if [ -L "$LINK" ] || [ ! -e "$LINK" ]; then
  other="$(command -v studio 2>/dev/null || true)"
  if [ -n "$other" ] && [ "$other" != "$LINK" ]; then echo "another 'studio' is on your PATH ($other): skipped the link"
  else ln -sfn "$TARGET" "$LINK" && echo "studio → $TARGET"; fi
fi
"$KIT/scripts/studio" doctor || true
