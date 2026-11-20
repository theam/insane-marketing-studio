#!/usr/bin/env python3
"""Plates and cut-out candidates with Codex image generation (runs on your ChatGPT plan through the Codex CLI), in
parallel. Extracted from the Shepherdr production (codexgen.py, generalized).

  studio plates assets/plates/book.json [ids…] [--n 2] [--jobs 4]

book.json: {"<id>": {"prompt": "…", "shape": "landscape|portrait|square", "n": 2,
                     "refs": ["assets/refs/face-1.png"]}}          reference images attached as they are
Candidates land in assets/plates/cands/<id>/<k>.png; pick one, then cut it out (`studio cutout`) or key it
(`studio chroma`). Every candidate is kept, rejected ones too.

Prompting that worked: "A real photograph of …, isolated on a pure black (#000000) background" for fire and
explosions (the page screens them in: the black disappears); "…isolated on a flat pure green (#00FF00) background, no
shadow on the background" for sprites to key; a full-bleed plate is the shot's first state (the window already open).
For a character, attach face references every time: without them the likeness drifts. Codex refuses some words (a
plate of Claudia was blocked, probably on "glamorous"): rephrase, never alter an image to get past a filter.
OpenRouter's video models refuse photoreal people ("input image may contain real person"); Codex makes those plates.
"""
import argparse, json, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os

P = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
SHAPES = {"landscape": "landscape (3:2)", "portrait": "portrait (2:3)", "square": "square (1:1)"}

ap = argparse.ArgumentParser()
ap.add_argument("book"); ap.add_argument("ids", nargs="*")
ap.add_argument("--n", type=int, default=None); ap.add_argument("--jobs", type=int, default=4)
a = ap.parse_args()
if not shutil.which("codex"):
    sys.exit("The Codex CLI isn't installed: brew install --cask codex, then `codex login` with your ChatGPT account.")
book = json.loads((P / a.book).read_text())
ids = a.ids or list(book)
(P / "logs").mkdir(exist_ok=True)


def run(task):
    pid, k = task
    spec = book[pid]
    out = P / "assets/plates/cands" / pid / f"{k}.png"
    if out.exists():
        return f"{pid}/{k} exists"
    out.parent.mkdir(parents=True, exist_ok=True)
    refs = spec.get("refs", [])
    note = ("The attached images are references: match the subject's identity to them, not their clothes, light or setting. " if refs else "")
    msg = ("Generate exactly one image with your built-in image generation tool. " + note
           + "Use this prompt verbatim (do not rewrite, shorten or embellish it):\n\n" + spec["prompt"] + "\n\n"
           + f"Size: {SHAPES[spec.get('shape', 'landscape')]}, highest quality. Then copy the generated image file to "
           + f"./{out.relative_to(P)}. Do nothing else. Reply only with the saved path.")
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write", "-o", str(P / f"logs/gen-{pid}-{k}.out")]
    for r in refs:
        cmd += ["-i", str(P / r)]
    cmd.append("-")
    with open(P / f"logs/gen-{pid}-{k}.log", "w") as log:
        rc = subprocess.run(cmd, input=msg, text=True, cwd=P, stdout=log, stderr=subprocess.STDOUT).returncode
    return f"{pid}/{k} {'ok' if out.exists() else f'FAILED (rc={rc}, see logs/gen-{pid}-{k}.log)'}"


tasks = [(pid, k) for pid in ids for k in range(1, (a.n or book[pid].get("n", 1)) + 1)]
with ThreadPoolExecutor(a.jobs) as ex:
    for line in ex.map(run, tasks):
        print(line, flush=True)
