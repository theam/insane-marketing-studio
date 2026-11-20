#!/usr/bin/env python3
"""studio doctor: what's ready on this Mac and in this project, in plain words. Keys are reported as set or not set,
never shown."""
import json, os, shutil, subprocess
from pathlib import Path

HOME = Path(os.environ.get("STUDIO_HOME", Path.home() / ".local/share/insane-marketing-studio"))
KEYS = Path(os.environ.get("STUDIO_KEYS", Path.home() / ".config/insane-marketing-studio/keys.env"))
PROJECT = Path(os.environ.get("PROJECT_DIR", "."))
rows, fixes = [], []


def out(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def check(name, ok, detail="", fix=None, optional=False):
    rows.append(("OK  " if ok else ("--  " if optional else "MISS"), name, detail))
    if not ok and fix:
        fixes.append(fix)


check("ffmpeg", bool(shutil.which("ffmpeg")), out("ffmpeg", "-version").split("\n")[0][:40], "brew install ffmpeg")
nv = out("node", "-p", "process.versions.node")
check("Node 20+", nv and int(nv.split(".")[0]) >= 20, nv, "brew install node")
pw = HOME / "node_modules/playwright/package.json"
check("Playwright", pw.exists(), json.loads(pw.read_text())["version"] if pw.exists() else "", "studio setup")
chrome = out("node", "-e", "try{const p=require('playwright').chromium.executablePath();console.log(require('fs').existsSync(p)?p:'')}catch(e){}")
check("Chromium", bool(chrome) or Path("/Applications/Google Chrome.app").exists(), "Playwright's" if chrome else "Google Chrome", "studio setup")
check("Impact font", Path("/System/Library/Fonts/Supplemental/Impact.ttf").exists(), "macOS system font")
vis = [p.name for p in (HOME / "bin").glob("*") if os.access(p, os.X_OK)] if (HOME / "bin").exists() else []
check("Vision tools", {"subject", "track", "alphabox"} <= set(vis), ", ".join(sorted(vis)), "xcode-select --install, then studio setup", optional=True)
check("Git LFS", bool(shutil.which("git-lfs")), "", "brew install git-lfs")
gh = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True) if shutil.which("gh") else None
check("GitHub sign-in", bool(gh) and gh.returncode == 0, "gh" if gh else "gh not installed", "gh auth login --web --git-protocol https")
check("Codex CLI (plates)", bool(shutil.which("codex")), "", "brew install --cask codex, then codex login", optional=True)
check("Keys file", KEYS.exists() and (KEYS.stat().st_mode & 0o077) == 0, str(KEYS), "studio keys")
for k, why in (("ELEVENLABS_API_KEY", "voice with word timing, music, effects"), ("HIGGSFIELD_API_KEY", "Seedance clips"), ("OPENROUTER_API_KEY", "Seedance fallback")):
    check(k, bool(os.environ.get(k)), "set" if os.environ.get(k) else f"not set ({why})", "studio keys", optional=True)
if not os.environ.get("ELEVENLABS_API_KEY"):
    rows.append(("    ", "  ElevenLabs", "no key: use the ElevenLabs connector in Claude (voice, effects, Scribe); music needs the full connector or a track of yours"))
if (PROJECT / "project.json").exists():
    p = json.loads((PROJECT / "project.json").read_text())
    check("project", True, f"{p.get('title')} ({p.get('style')})")
    for f, what in (("timing.js", "studio timing"), ("audio/voice-lead.wav", "studio voice"), ("timing/points.json", "studio points"),
                    ("audio/music.mp3", "studio music"), ("audio/mix.wav", "studio mix"), ("out/silent.mp4", "studio render")):
        check("  " + f, (PROJECT / f).exists(), "" if (PROJECT / f).exists() else f"next: {what}", optional=True)
w = max(len(r[1]) for r in rows)
for s, n, d in rows:
    print(f"{s} {n.ljust(w)}  {d}")
if fixes:
    print("\nTo fix: " + "; ".join(dict.fromkeys(fixes)))
