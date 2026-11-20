#!/usr/bin/env python3
"""Sound effects: generate the kinds the edit uses with ElevenLabs, and trim each file's leading silence.

Extracted from the Shepherdr production (sfx.py). The edit places effects with sfx(t, kind) in
video.html; `studio points` dumps them to timing/points.json. Kinds and their prompts are in the project's sfx.json
(shrill kinds are aliased to soft ones there: no loud beeps).

  studio sfx            generate every used kind that's missing (needs ELEVENLABS_API_KEY), then trim
  studio sfx --plan     list the missing kinds as JSON, to make them through the ElevenLabs connector instead
                        (save each to the file it names, then run `studio sfx` again to trim them)
  studio sfx --all      every kind in sfx.json, used or not

audio/sfx/raw/<kind>.mp3 is what ElevenLabs returned (keep it); audio/sfx/<kind>.wav is trimmed (rebuilt from raw).
"""
import json, os, re, subprocess, sys, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
RAW, OUT = ROOT / "audio/sfx/raw", ROOT / "audio/sfx"


def library():
    return json.loads((ROOT / "sfx.json").read_text())


def used(lib):
    pts = ROOT / "timing/points.json"
    if "--all" in sys.argv or not pts.exists():
        if not pts.exists() and "--all" not in sys.argv:
            print("timing/points.json not found: run `studio points` first (or use --all).", file=sys.stderr)
        return sorted(lib["kinds"]) if "--all" in sys.argv else []
    kinds = {lib["alias"].get(p["kind"], p["kind"]) for p in json.loads(pts.read_text())["sfx"]}
    unknown = sorted(k for k in kinds if k not in lib["kinds"])
    if unknown:
        print(f"the edit uses kinds sfx.json doesn't define (add a prompt for each): {', '.join(unknown)}", file=sys.stderr)
    return sorted(k for k in kinds if k in lib["kinds"])


def gen(item):
    kind, (text, dur, _family) = item
    out = RAW / f"{kind}.mp3"
    if out.exists():
        return f"{kind} cached"
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192", method="POST",
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
                                 data=json.dumps({"text": text, "duration_seconds": dur, "prompt_influence": 0.55}).encode())
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            out.write_bytes(r.read())
        return f"{kind} generated"
    except urllib.error.HTTPError as e:
        return f"{kind} FAILED: HTTP {e.code} {e.read().decode()[:200]}"


def probe(path):
    """(duration, peak dBFS) of a file; (0, -inf) if it has no audio."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    d = re.findall(r"time=(\d+):(\d+):([\d.]+)", r)
    dur = (int(d[-1][0]) * 3600 + int(d[-1][1]) * 60 + float(d[-1][2])) if d else 0.0
    pk = re.findall(r"max_volume: (-?[\d.]+) dB", r)
    return dur, float(pk[0]) if pk else float("-inf")


def trim(kind):
    """Cut the leading silence (below -45 dB) so the sound starts on its frame; keep 5 ms before the onset.
    A take that is all quiet would be cut to nothing: then it is kept untrimmed. Returns a problem, or None."""
    src, dst = RAW / f"{kind}.mp3", OUT / f"{kind}.wav"
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return None
    dur, peak = probe(src)
    if dur < 0.05 or peak < -50:
        dst.unlink(missing_ok=True)
        return f"{kind}: the take is empty or silent ({dur:.2f} s, peak {peak:.0f} dB). Delete {src.relative_to(ROOT)} and make it again."
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.005,afade=t=in:d=0.004",
                    "-ar", "48000", str(dst)], check=True)
    if probe(dst)[0] < 0.05:  # all of it was under the threshold: keep it as it came
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-ar", "48000", str(dst)], check=True)
    return None


def main():
    lib = library()
    kinds = used(lib)
    RAW.mkdir(parents=True, exist_ok=True)
    missing = [k for k in kinds if not (RAW / f"{k}.mp3").exists()]
    if "--plan" in sys.argv:
        print(json.dumps([{"kind": k, "prompt": lib["kinds"][k][0], "duration_seconds": lib["kinds"][k][1],
                           "save_to": str((RAW / f"{k}.mp3").relative_to(ROOT))} for k in missing], indent=1))
        print(f"{len(missing)} of {len(kinds)} kinds missing", file=sys.stderr)
        return
    if missing:
        if not os.environ.get("ELEVENLABS_API_KEY"):
            sys.exit(f"{len(missing)} effects missing and no ELEVENLABS_API_KEY: make them through the connector "
                     f"(`studio sfx --plan`) or add the key (`studio keys`).")
        with ThreadPoolExecutor(4) as ex:
            for line in ex.map(gen, [(k, lib["kinds"][k]) for k in missing]):
                print(line)
    problems = [p for p in (trim(k) for k in kinds if (RAW / f"{k}.mp3").exists()) if p]
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(kinds) - len(problems)} of {len(kinds)} kinds ready in audio/sfx/")


if __name__ == "__main__":
    main()
