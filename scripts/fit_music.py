#!/usr/bin/env python3
"""Re-fit a composed music take to the current narration, section by section, without composing again.

Extracted from the Shepherdr production (fit_music.py). Each chunk of the take (as composed, from
its plan file) is time-stretched on its own (atempo) to the span `studio music` would give it today, so every change of
style still lands where the story turns after the narration is re-timed.

  studio fit-music [audio/music-take-N.mp3]     default: the latest take; writes audio/music.mp3

A stretch beyond ±10 % starts to sound rough, and 1.15-1.27× did in the Shepherdr infomercial: when any chunk goes past
it, this prints a warning; compose a new take (`studio music`) if it sounds wrong.

  studio fit-music --library NAME     no way to compose? lay a score you have the rights to instead: NAME.mp3 and its
                                      sections file NAME.json, in ~/.local/share/insane-marketing-studio/music/ (or the
                                      kit's library/music/). Each chunk of music.json plays the section named in its
                                      "library" field, from that section's first beat, cut to the chunk's span (no stretch)
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent))
from music import plan  # noqa: E402


def library(name):
    """Re-cut a library score: every chunk starts on its section's downbeat and is cut, never stretched."""
    home = Path(os.environ.get("STUDIO_HOME", Path.home() / ".local/share/insane-marketing-studio")) / "music"
    kit = Path(__file__).resolve().parent.parent / "library/music"
    where = next((d for d in (home, kit) if (d / f"{name}.mp3").exists() and (d / f"{name}.json").exists()), None)
    if not where:
        sys.exit(f"No score {name}: put {name}.mp3 and its sections file {name}.json in {home} (see library/music/README.md in the kit).")
    src, meta = where / f"{name}.mp3", json.loads((where / f"{name}.json").read_text())
    spec = json.loads((ROOT / "music.json").read_text())
    _, new = plan()
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)]))
    chains = []
    for k, (ch, c, d) in enumerate(zip(spec["chunks"], new, new[1:])):
        sec = meta["sections"].get(ch.get("library", ""))
        if not sec:
            sys.exit(f'music.json chunk {k} needs "library": one of {", ".join(meta["sections"])}')
        a, need = sec["start"], d - c
        last = k == len(spec["chunks"]) - 1
        fade = f"afade=t=out:st={max(0, need - 1.2):.3f}:d=1.2" if last else f"afade=t=out:st={max(0, need - 0.015):.4f}:d=0.015"
        chains.append(f"[0:a]atrim={a:.4f}:{min(total, a + need):.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,apad=whole_dur={need:.4f},{fade}[s{k}]")
        print(f"chunk {k}: {c:7.2f}-{d:7.2f} s ← {ch['library']} from {a:.2f} s")
    graph = ";".join(chains) + ";" + "".join(f"[s{k}]" for k in range(len(chains))) + f"concat=n={len(chains)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-filter_complex", graph,
                    "-map", "[o]", "-ar", "48000", "-b:a", "192k", str(ROOT / "audio/music.mp3")], check=True)
    (ROOT / "audio/music-plan.json").write_text(json.dumps({"library": name, "starts": new[:-1], "end": new[-1]}, indent=1))
    print(f"audio/music.mp3 written from the score {name}, {new[-1]:.2f} s. Credit: {meta.get('source', '(none in its .json)')}")


def main():
    if "--library" in sys.argv:
        (ROOT / "audio").mkdir(exist_ok=True)
        return library(sys.argv[sys.argv.index("--library") + 1])
    takes = sorted((ROOT / "audio").glob("music-take-*.mp3"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    src = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (takes[-1] if takes else None)
    if not src or not src.exists():
        sys.exit("No composed take to fit: run `studio music` first.")
    meta = json.loads(src.with_suffix(".json").read_text())
    _, new = plan()
    old = meta["starts"] + [meta["end"]]
    if len(old) != len(new):
        sys.exit("music.json has a different number of chunks than this take: compose a new take (`studio music`).")
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)]))
    old[-1] = total                      # the take's extra milliseconds ride with the last chunk
    chains, rough = [], []
    for k, (a, b, c, d) in enumerate(zip(old, old[1:], new, new[1:])):
        x = (b - a) / (d - c)
        if not 0.9 <= x <= 1.1: rough.append(f"chunk {k} ×{x:.2f}")
        chains.append(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,atempo={x:.5f}[s{k}]")
        print(f"chunk {k}: {a:7.2f}-{b:7.2f} s -> {c:7.2f}-{d:7.2f} s  ×{x:.4f}")
    graph = ";".join(chains) + ";" + "".join(f"[s{k}]" for k in range(len(chains))) + f"concat=n={len(chains)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-filter_complex", graph,
                    "-map", "[o]", "-ar", "48000", "-b:a", "192k", str(ROOT / "audio/music.mp3")], check=True)
    (ROOT / "audio/music-plan.json").write_text(json.dumps({"take": src.name, "fitted": True, "starts": new[:-1], "end": new[-1]}, indent=1))
    print(f"audio/music.mp3 written from {src.name}, {new[-1]:.2f} s")
    if rough:
        print("WARNING: stretched beyond ±10 % (" + ", ".join(rough) + "). Listen to it; if it sounds rough, compose a new take.")


if __name__ == "__main__":
    main()
