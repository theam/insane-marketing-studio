#!/usr/bin/env python3
"""The storyboard data for the review Artifact: one card per cut of the edit, with its frame, time and words.

  studio board            writes board/board.json and board/img/<shot>.jpg (640 px) from the current edit

Each cut's id is its label (cut(..., { label: 'title' })), so notes keep pointing at the same shot after a re-edit;
cuts without a label get s01, s02… by order. The frame is rendered 40 % into the cut (at most 1.2 s in). The words are
the narration spoken while the cut is on screen. Publish templates/storyboard/index.html with these files (the
storyboard skill says how); notes left on the page land in the Artifact's database, collection "notes", one document
per shot id.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
KIT = Path(__file__).resolve().parent.parent


def grab(js, name):
    m = re.search(rf"window\.{name} = (.*?);\n", js, re.S)
    return json.loads(m.group(1)) if m else None


def main():
    pts = json.loads((ROOT / "timing/points.json").read_text())
    js = (ROOT / "timing.js").read_text()
    words, project = grab(js, "WORDS") or [], json.loads((ROOT / "project.json").read_text())
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\*\*(\d+)\s*·\s*(.+?)\*\*", (ROOT / "script.md").read_text(), re.M)}
    cuts, shots, seen = pts["cuts"], [], set()
    for i, k in enumerate(cuts):
        end = cuts[i + 1]["t"] if i + 1 < len(cuts) else pts["duration"]
        sid = re.sub(r"[^a-z0-9]+", "-", (k.get("label") or "").lower()).strip("-") or f"s{i + 1:02d}"
        if sid in seen: sid = f"{sid}-{i + 1}"
        seen.add(sid)
        said = [w for w in words if k["t"] - 0.1 <= w["s"] < end - 0.1]
        secs = [w["sec"] for w in said if w.get("sec")]
        shots.append({"id": sid, "n": i + 1, "t": round(k["t"], 2), "end": round(end, 2), "label": k.get("label") or "",
                      "text": " ".join(w["w"] for w in said),
                      "section": titles.get(secs[0], "") if secs else "", "frame_t": round(min(k["t"] + 0.4 * (end - k["t"]), k["t"] + 1.2), 2)})
    times = ",".join(f"{s['frame_t']:.2f}" for s in shots)
    subprocess.run(["node", str(KIT / "scripts/render.js"), "stills", times], check=True, cwd=ROOT, capture_output=True)
    img = ROOT / "board/img"
    shutil.rmtree(img, ignore_errors=True); img.mkdir(parents=True)
    for s in shots:
        src = ROOT / f"out/stills/t{s['frame_t']:06.2f}.png"
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "--resampleWidth", "640", str(src), "--out", str(img / f"{s['id']}.jpg")],
                       check=True, capture_output=True)
        s["img"] = f"img/{s['id']}.jpg"
    log = (ROOT / "log.md").read_text() if (ROOT / "log.md").exists() else ""
    version = len(re.findall(r"^## ", log, re.M)) or 1
    board = {"title": project.get("title", ROOT.name), "version": version, "duration": round(pts["duration"], 2), "shots": shots}
    (ROOT / "board/board.json").write_text(json.dumps(board, indent=1, ensure_ascii=False))
    # The same data as a script, so board/index.html also opens straight from the disk (browsers block fetch() there).
    (ROOT / "board/board.js").write_text("window.BOARD = " + json.dumps(board, ensure_ascii=False) + ";\n")
    page = ROOT / "board/index.html"
    if not page.exists():
        shutil.copy(KIT / "templates/storyboard/index.html", page)
    print(f"board/board.json: {len(shots)} shots, frames in board/img/ (version {version})")


if __name__ == "__main__":
    main()
