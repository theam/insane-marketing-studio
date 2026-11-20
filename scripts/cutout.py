#!/usr/bin/env python3
"""Lift the subject out of a photo with macOS Vision (VNGenerateForegroundInstanceMaskRequest) and trim it to its
content: a cut-out PNG with transparency, ready for sprite(el, 'name', w).

  studio cutout photo.jpg assets/cutouts/name.png                 the whole photo
  studio cutout photo.jpg assets/cutouts/name.png 120 40 900 1200 only that crop (x y w h, px from the top-left)
  studio cutout photo.jpg out.png --instances 1                   only Vision's first subject (it prints them)

Use it for plates the image model made, and for photos of real people only under a licence that allows it (CC BY,
CC BY-SA, public domain), with the attribution in the description or on the end card. Record it in
assets/cutouts/CREDITS.md.
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

a = sys.argv[1:]
inst = None
if "--instances" in a:
    i = a.index("--instances"); inst = a[i + 1]; del a[i:i + 2]
if len(a) not in (2, 6):
    sys.exit(__doc__)
src, out = Path(a[0]), Path(a[1])
if not shutil.which("subject"):
    sys.exit("The Vision tools aren't built: run `studio setup` (needs Xcode's command line tools: xcode-select --install).")
w, h = map(int, subprocess.check_output(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(src)], text=True).split()[-3::2])
box = a[2:6] if len(a) == 6 else ["0", "0", str(w), str(h)]
tmp = Path(tempfile.mkdtemp()) / "mask.png"
cmd = ["subject", str(src), *box, str(tmp)] + ([inst] if inst else [])
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode or not tmp.exists():
    sys.exit("Vision found no subject in that picture. Try a tighter crop, or generate the sprite on flat green and use `studio chroma`.")
crop = subprocess.check_output(["alphabox", str(tmp), "0.5"], text=True).strip()
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp), "-vf", crop, str(out)], check=True)
print(f"{out} ({crop})")
