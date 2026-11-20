#!/usr/bin/env python3
"""The social cut: stretches of the long video between its own cut times, plus a call-to-action card, re-mixed.

Extracted from the Shepherdr production (short.py, generalized). The picture comes from the long
video's silent render (out/silent.mp4) at the edit's cut boundaries; the sound is mixed again for the cut, so nothing
jumps: narration and effects come from the same stretches, the bed is laid as one continuous slice per anchor (each
starting on its own hit at a cut), ducked under the short's own phrases.

short.json (in the project):
  {"cuts": [1, 2, [5, 7], 12],          cut numbers from `studio sheet` (#1…); [a, b] = cuts a through b
   "card": 3.5,                          seconds of the CTA card (the page's SHORT_CARD, rendered with ?short); 0 = none
   "music": [[0, 0.0], [2, 27.91]],      optional: [stretch index, music time laid at its start]; default: the
                                         music under each stretch's first frame, i.e. the long mix's own bed
   "name": "social-40s"}

  studio short       → out/<project>-<name>.mp4 at -14 LUFS
"""
import json, math, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mix import FAMILY, lufs, phrases, speech_expr  # noqa: E402

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
KIT = Path(__file__).resolve().parent.parent


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)


def main():
    spec = json.loads((ROOT / "short.json").read_text())
    proj = json.loads((ROOT / "project.json").read_text())
    FPS = proj.get("fps", 30)
    M = {"bed_under_voice_db": 6, "duck_db": 7, "sfx_lufs": -19, **proj.get("mix", {})}
    pts = json.loads((ROOT / "timing/points.json").read_text())
    cuts = [k["t"] for k in pts["cuts"]] + [pts["duration"]]
    ranges = []
    for c in spec["cuts"]:
        a, b = (c, c) if isinstance(c, int) else c
        ranges.append((cuts[a - 1], cuts[b]))
    frames = lambda t: math.ceil(t * FPS - 1e-6)
    # Each stretch after the first starts one frame after its cut: on a cut's first frame the long video can still
    # show the previous line's caption.
    fr = [(frames(a) + (1 if i else 0), frames(b)) for i, (a, b) in enumerate(ranges)]
    segs = [(a / FPS, b / FPS) for a, b in fr]
    starts, t = [], 0.0
    for a, b in segs:
        starts.append(t); t += b - a
    card_at, card_len = t, float(spec.get("card", 0))
    total = card_at + card_len
    name = spec.get("name", "social")
    tmp = ROOT / "out/short"; tmp.mkdir(parents=True, exist_ok=True)
    # Picture.
    inputs = ["-i", str(ROOT / "out/silent.mp4")]
    graph = "".join(f"[0:v]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(fr))
    parts = "".join(f"[v{i}]" for i in range(len(segs)))
    if card_len:
        card = tmp / "card.mp4"
        subprocess.run(["node", str(KIT / "scripts/render.js"), "range", str(card.relative_to(ROOT)), "short", str(card_len), "--query", "?short"], check=True, cwd=ROOT)
        inputs += ["-i", str(card)]
        graph += "[1:v]setpts=PTS-STARTPTS[vc];"; parts += "[vc]"
    graph += parts + f"concat=n={len(segs) + (1 if card_len else 0)}:v=1:a=0[v]"
    silent = tmp / "silent.mp4"
    ff(*inputs, "-filter_complex", graph, "-map", "[v]", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
       "-crf", "16", "-preset", "medium", "-tune", "animation", "-r", str(FPS), str(silent))

    def short_time(film_t):
        for (a, b), s in zip(segs, starts):
            if a - 1e-6 <= film_t < b + 1e-6:
                return s + film_t - a
        return None
    # Voice: the same stretches, one frame ahead of the picture (each keeps its cut's first sound), 10 ms edges.
    vsegs = [(a - (1 / FPS if i else 0), b - (1 / FPS if i else 0)) for i, (a, b) in enumerate(segs)]
    chains = ["".join(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b - a - 0.01:.4f}:d=0.01[s{i}];" for i, (a, b) in enumerate(vsegs))
              + "".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur={total:.3f}[x0]"]
    ins, mixes, n = ["-i", str(ROOT / "audio/voice-lead.wav")], ["[x0]"], 1
    music = ROOT / "audio/music.mp3"
    if music.exists():
        chunks = json.loads((ROOT / "timing/chunks.json").read_text())
        spans = [(short_time(c["sound"][0]), short_time(c["sound"][1] - 0.02)) for c in chunks]
        ph = phrases([s for s in spans if None not in s])
        anchors = spec.get("music") or [[i, segs[i][0]] for i in range(len(segs))]
        bounds = [starts[k] for k, _ in anchors] + [total]
        mp = []
        for j, ((k, mt), s0, s1) in enumerate(zip(anchors, bounds, bounds[1:])):
            L = s1 - s0
            fade = f"afade=t=out:st={L - 0.6:.3f}:d=0.6" if j == len(anchors) - 1 else f"afade=t=out:st={L - 0.03:.3f}:d=0.03"
            mp.append(f"[{n}:a]atrim={mt:.4f}:{mt + L:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,{fade}[m{j}]")
        gain = (lufs(ROOT / "audio/voice-lead.wav") + 3.0 - M["bed_under_voice_db"]) - lufs(music)
        chains.append(";".join(mp) + ";" + "".join(f"[m{j}]" for j in range(len(mp))) + f"concat=n={len(mp)}:v=0:a=1,aresample=48000,"
                      f"volume=volume='pow(10,({gain:.2f}-{M['duck_db']}*{speech_expr(ph)})/20)':eval=frame,apad=whole_dur={total:.3f}[x{n}]")
        ins += ["-i", str(music)]; mixes.append(f"[x{n}]"); n += 1
    lib = json.loads((ROOT / "sfx.json").read_text())
    gains = {}
    for p in pts["sfx"]:
        kind = lib["alias"].get(p["kind"], p["kind"])
        f = ROOT / f"audio/sfx/{kind}.wav"
        at = next((s + max(0.0, p["t"] - a) for (a, b), s in zip(segs, starts) if a - 0.1 <= p["t"] < b - 0.15), None)
        if at is None or not f.exists(): continue
        fam = lib["kinds"].get(kind, ["", 0, "other"])[2]
        gains.setdefault(kind, max(-30.0, min(12.0, M["sfx_lufs"] + FAMILY.get(fam, 0) - lufs(f))))
        ins += ["-i", str(f)]
        chains.append(f"[{n}:a]aresample=48000{',lowpass=f=6000' if fam == 'tonal' else ''},volume={gains[kind]:.2f}dB,adelay={int(at * 1000)}:all=1[x{n}]")
        mixes.append(f"[x{n}]"); n += 1
    mixwav = ROOT / "audio/short-mix.wav"
    ff(*ins, "-filter_complex", ";".join(chains) + ";" + "".join(mixes) + f"amix=inputs={len(mixes)}:normalize=0:duration=first,atrim=0:{total:.3f}[a]",
       "-map", "[a]", "-c:a", "pcm_s24le", str(mixwav))
    out = ROOT / f"out/{ROOT.name}-{name}.mp4"
    subprocess.run([sys.executable, str(KIT / "scripts/master.py"), str(silent), str(mixwav), str(out)], cwd=ROOT)
    print(f"{len(segs)} stretches + {card_len:.1f} s card = {total:.2f} s → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
