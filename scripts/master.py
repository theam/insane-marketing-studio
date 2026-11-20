#!/usr/bin/env python3
"""Master and check: mux the silent render with the mix at -14 LUFS, then check the result.

Extracted from the Shepherdr production (master.sh). The mix is brought to -14 LUFS (YouTube and social) with a limiter at about
-1.5 dBFS, encoded AAC 384 kbps at 48 kHz, and muxed with the picture without re-encoding it.

  studio master [out/silent.mp4] [audio/mix.wav] [out/NAME.mp4]     default name: the project folder's name
  studio qc out/NAME.mp4                                            only the checks

The checks: 1920×1080 at the project's fps, H.264 yuv420p, AAC 48 kHz, loudness -14 ±1 LUFS, true peak under -1 dBTP,
sound and picture the same length, and the last 15 frames fully black (the director: never end mid-fade).
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()


def probe(f):
    return json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)]))


def loud(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    tp = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", r)
    return i, float(tp[-1]) if tp and tp[-1] != "-inf" else -99.0


def black_tail(f, fps):
    """How many of the last frames are black (YAVG at or under 17 on the 16-235 scale)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-sseof", "-1.5", "-i", str(f), "-map", "0:v", "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    ys = [float(x) for x in re.findall(r"YAVG=([\d.]+)", r)]
    n = 0
    for y in reversed(ys):
        if y > 17: break
        n += 1
    return n


def qc(f):
    proj = json.loads((ROOT / "project.json").read_text()) if (ROOT / "project.json").exists() else {}
    fps = proj.get("fps", 30)
    d = probe(f)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    rate = eval(v["r_frame_rate"])
    checks = [
        ("picture", f"{v['width']}×{v['height']} {v['codec_name']} {v['pix_fmt']} {v.get('color_range', '?')} range {v.get('color_space', '?')} {rate:g} fps",
         v["width"] == proj.get("width", 1920) and v["height"] == proj.get("height", 1080) and v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p" and abs(rate - fps) < 0.01),
    ]
    if a:
        i, tp = loud(f)
        checks += [
            ("sound", f"{a['codec_name']} {a['sample_rate']} Hz {int(a.get('bit_rate', 0)) // 1000} kbps", a["codec_name"] == "aac" and a["sample_rate"] == "48000"),
            ("loudness", f"{i:.1f} LUFS (target -14)", abs(i + 14) <= 1.0),
            ("true peak", f"{tp:.1f} dBTP", tp <= -1.0),
            ("lengths", f"picture {float(v['duration']):.2f} s, sound {float(a['duration']):.2f} s", abs(float(v["duration"]) - float(a["duration"])) < 0.1),
        ]
    else:
        checks.append(("sound", "none", False))
    nb = black_tail(f, fps)
    checks.append(("ends on black", f"{nb} black frames at the end (need ≥ 15)", nb >= 15))
    size = os.path.getsize(f) / 1e6
    print(f"{f}: {float(d['format']['duration']):.2f} s, {size:.1f} MB")
    ok = True
    for name, val, good in checks:
        print(f"  {'OK  ' if good else 'FAIL'} {name:14} {val}")
        ok &= good
    return ok


def main():
    args = sys.argv[1:]
    if args and args[0] == "qc":
        sys.exit(0 if qc(Path(args[1])) else 1)
    video = Path(args[0]) if len(args) > 0 else ROOT / "out/silent.mp4"
    mix = Path(args[1]) if len(args) > 1 else ROOT / "audio/mix.wav"
    out = Path(args[2]) if len(args) > 2 else ROOT / f"out/{ROOT.name}.mp4"
    target = json.loads((ROOT / "project.json").read_text()).get("mix", {}).get("target_lufs", -14)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mix), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    L = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    gain = round(target - L, 2)
    print(f"mix {L:.1f} LUFS → gain {gain:+.2f} dB")
    out.parent.mkdir(parents=True, exist_ok=True)
    # The picture sets the length: the sound is padded or trimmed to it. (-shortest dropped the last 5 frames of black
    # when the AAC stream ended a few milliseconds before the picture.)
    vd = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                                    "-of", "json", str(video)], capture_output=True, text=True).stdout)["streams"][0]["duration"]
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-i", str(mix), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", f"volume={gain}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,aresample=48000,apad,atrim=0:{vd}",
                    "-c:a", "aac", "-b:a", "384k", "-ar", "48000", "-t", vd, "-movflags", "+faststart", str(out)], check=True)
    sys.exit(0 if qc(out) else 1)


if __name__ == "__main__":
    main()
