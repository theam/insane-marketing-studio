#!/usr/bin/env python3
"""The music bed: one ElevenLabs Music composition whose sections start at the narration's turning points.

Extracted from the Shepherdr production (music.py). The plan is the project's music.json: one chunk
per script section, each with its styles. Chunk durations are measured from timing/sections.json (written by
`studio voice`), so every change of style lands where the story turns. The bed runs the whole video, to the end card.

  studio music --dry-run   print the plan with its timings (free)
  studio music             compose audio/music.mp3 (needs ELEVENLABS_API_KEY; about 1-2 minutes)

Every composed take is kept as audio/music-take-N.mp3 with its plan (audio/music-take-N.json), so `studio fit-music`
can re-fit it after the narration re-times instead of composing again.
"""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()


def video_end():
    """Where the bed must end: the video's duration if the edit has been dumped, else the last word + end_pad."""
    pts = ROOT / "timing/points.json"
    if pts.exists():
        return float(json.loads(pts.read_text())["duration"])
    sec = json.loads((ROOT / "timing/sections.json").read_text())
    pad = json.loads((ROOT / "project.json").read_text()).get("music", {}).get("end_pad", 1.5)
    return max(v["end"] for v in sec.values()) + pad


def plan():
    spec = json.loads((ROOT / "music.json").read_text())
    if not (ROOT / "timing/sections.json").exists():
        sys.exit("The music follows the narration's sections: make the voice first (`studio voice`), then `studio points`, then the music.")
    sec = {int(k): v for k, v in json.loads((ROOT / "timing/sections.json").read_text()).items()}
    chunks = spec["chunks"]
    starts = []
    for ch in chunks:
        s = ch["starts_at"]
        if s not in sec:
            sys.exit(f"music.json: chunk {ch['text']!r} starts at section {s}, which the script doesn't have ({sorted(sec)})")
        starts.append(max(0.0, sec[s]["start"] + ch.get("offset", 0)))
    starts[0] = 0.0
    starts.append(video_end())
    out = []
    for ch, a, b in zip(chunks, starts, starts[1:]):
        out.append({"text": ch["text"], "duration_ms": int(round((b - a) * 1000)), "positive_styles": ch["positive"],
                    "negative_styles": spec.get("no_voice", []) + ch.get("negative", []),
                    "context_adherence": ch.get("adherence", "low")})
    return {"chunks": out}, starts


def main():
    p, starts = plan()
    for c, t in zip(p["chunks"], starts):
        print(f"{t:7.2f} s  {c['duration_ms'] / 1000:6.2f} s  {c['text'].splitlines()[0]}")
    print(f"total {sum(c['duration_ms'] for c in p['chunks']) / 1000:.2f} s")
    short = [c["text"] for c in p["chunks"] if c["duration_ms"] < 3000]
    if short:
        sys.exit(f"ElevenLabs Music needs every section to last at least 3 s; too short: {short}. Merge those chunks in music.json.")
    if "--dry-run" in sys.argv:
        return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("No ELEVENLABS_API_KEY: music needs the key (the restricted ElevenLabs connector has no music). `studio keys` opens the keys file.")
    model = json.loads((ROOT / "project.json").read_text()).get("music", {}).get("model", "music_v2_5")
    req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_48000_192", method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json"},
                                 data=json.dumps({"composition_plan": p, "model_id": model}).encode())
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            data, ctype = r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs HTTP {e.code}: {e.read().decode()[:2000]}")
    if "audio" not in ctype:
        sys.exit(f"unexpected response ({ctype}): {data[:500]!r}")
    (ROOT / "audio").mkdir(exist_ok=True)
    n = 1 + len(list((ROOT / "audio").glob("music-take-*.mp3")))
    take = ROOT / f"audio/music-take-{n}.mp3"
    take.write_bytes(data)
    (ROOT / f"audio/music-take-{n}.json").write_text(json.dumps({"plan": p, "starts": starts[:-1], "end": starts[-1]}, indent=1))
    (ROOT / "audio/music.mp3").write_bytes(data)
    (ROOT / "audio/music-plan.json").write_text(json.dumps({"take": take.name, "plan": p, "starts": starts[:-1], "end": starts[-1]}, indent=1))
    print(f"{take.name} composed ({len(data)} bytes) → audio/music.mp3")


if __name__ == "__main__":
    main()
