#!/usr/bin/env python3
"""Start a video project: a folder with the style's starter page, script, settings, music plan and effects, plus a
copy of the engine, so the project keeps rendering the same way after the kit is updated.

  studio new ~/Videos/spring-launch --style infomercial --title "SPRING LAUNCH!"
  studio new ~/Videos/q3-explainer --style explainer
"""
import argparse, json, shutil, subprocess, sys
from datetime import date
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
IMPACT = Path("/System/Library/Fonts/Supplemental/Impact.ttf")

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("--style", default="infomercial", choices=["infomercial", "explainer"])
ap.add_argument("--title", default=None)
a = ap.parse_args()

dst = Path(a.folder).expanduser().resolve()
if dst.exists() and any(dst.iterdir()):
    sys.exit(f"{dst} exists and isn't empty. Pick a new folder (a new version of a video goes in a new folder too).")
tpl = KIT / "templates" / a.style
dst.mkdir(parents=True, exist_ok=True)
for f in tpl.iterdir():
    shutil.copy(f, dst / f.name) if f.is_file() else shutil.copytree(f, dst / f.name)
shutil.copy(KIT / "templates/shared/sfx.json", dst / "sfx.json")
for f in ("gitignore", "gitattributes"):
    shutil.copy(KIT / f"templates/shared/{f}", dst / f".{f}")
shutil.copytree(KIT / "engine", dst / "engine")
if IMPACT.exists():
    shutil.copy(IMPACT, dst / "engine/fonts/Impact.ttf")
elif a.style == "infomercial":
    print("WARNING: Impact isn't on this Mac (/System/Library/Fonts/Supplemental/Impact.ttf); the big words will fall back to another font.")
for d in ("assets/cutouts", "assets/plates", "assets/screens", "assets/gen/plates", "audio/lines", "audio/sfx/raw", "timing", "board", "gen", "out"):
    (dst / d).mkdir(parents=True, exist_ok=True)
(dst / "assets/gen/manifest.js").write_text("// Generated clips extracted to frames (studio clip-frames). Empty until a clip is picked.\nwindow.GEN = {};\n")
proj = json.loads((dst / "project.json").read_text())
if a.title:
    proj["title"] = a.title
    page = dst / "video.html"
    page.write_text(page.read_text().replace("<title>THE PRODUCT!</title>", f"<title>{a.title}</title>"))
proj["created"] = date.today().isoformat()
proj["kit"] = subprocess.run(["git", "-C", str(KIT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
(dst / "project.json").write_text(json.dumps(proj, indent=2) + "\n")
(dst / "brief.md").write_text(f"# Brief — {proj['title']}\n\nThe ask, verbatim, and every decision after it, dated. Never edit an old entry: add a new one that supersedes it.\n\n## {date.today().isoformat()} · the ask\n\n(paste the request here, word for word)\n")
(dst / "log.md").write_text(f"# Version log — {proj['title']}\n\nOne entry per version: what changed, why (whose note), known gaps, spend.\n")
(dst / "gen/ledger.jsonl").touch()
subprocess.run(["git", "init", "-q", "-b", "main", str(dst)])
print(f"{dst}: {a.style} project ready.")
print("Next: write script.md, then `studio timing --placeholder` to see the starter page move before any voice exists.")
