#!/usr/bin/env python3
"""The mix: narration, the music bed ducked under it, the edit's sound effects and any other audio the edit places.

Extracted from the Shepherdr production (mix.py, generalized). Inputs: audio/voice-lead.wav,
audio/music.mp3 (optional), timing/chunks.json (when the voice sounds), timing/points.json (`studio points`: effects,
audio events, music events, the ending), audio/sfx/<kind>.wav (`studio sfx`).

  studio mix        writes audio/mix.wav (48 kHz, 24-bit); `studio master` brings it to -14 LUFS with the picture

- The bed sits mix.bed_under_voice_db under the voice between phrases and mix.duck_db further while anyone speaks
  (the duck starts 150 ms before each phrase). It is stopped dead at a musicStop() and muted in a musicMute() span,
  and fades out with the picture's fade to black.
- Each effect is brought to a loudness for its family (impact +3 LU, tonal -4 LU and low-passed at 6 kHz, around
  mix.sfx_lufs) instead of one fixed gain: in the Shepherdr infomercial the files' own levels spread 37 dB.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
PRE, ATTACK, RELEASE, PHRASE_GAP = 0.15, 0.12, 0.3, 0.35
FAMILY = {"impact": 3, "tonal": -4, "other": 0}


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    v = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", r.stderr)
    return float(v[-1]) if v and v[-1] != "-inf" else -70.0


def phrases(spans):
    out = []
    for a, b in sorted(spans):
        if out and a - out[-1][1] <= PHRASE_GAP: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def speech_expr(ph):
    if not ph:
        return "0"
    return "min(1," + "+".join(f"clip((t-{a - PRE:.3f})/{ATTACK},0,1)*clip(({b + RELEASE:.3f}-t)/{RELEASE},0,1)" for a, b in ph) + ")"


def main():
    proj = json.loads((ROOT / "project.json").read_text())
    M = {"bed_under_voice_db": 6, "duck_db": 7, "sfx_lufs": -19, **proj.get("mix", {})}
    lib = json.loads((ROOT / "sfx.json").read_text())
    pts = json.loads((ROOT / "timing/points.json").read_text())
    chunks = json.loads((ROOT / "timing/chunks.json").read_text())
    total = float(pts["duration"])
    voice = ROOT / "audio/voice-lead.wav"
    ph = phrases([tuple(c["sound"]) for c in chunks])
    inputs = ["-i", str(voice)]
    chains = [f"[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur={total}[voice]"]
    mixes, n = ["[voice]"], 1
    music = ROOT / "audio/music.mp3"
    if music.exists():
        gain = (lufs(voice) + 3.0 - M["bed_under_voice_db"]) - lufs(music)
        gate = "1"
        for e in pts.get("music", []):
            if e["type"] == "stop": gate += f"*clip(({e['t']:.3f}+0.02-t)/0.02,0,1)"
            elif e["type"] == "mute": gate += f"*(1-between(t,{e['t']:.3f},{e['end']:.3f}))"
        end = pts.get("end") or {}
        fade_to = total - end.get("black", 0.6)
        fade_from = fade_to - max(1.0, end.get("fade", 0.8) + 0.4)
        inputs += ["-i", str(music)]
        chains.append(f"[{n}:a]aresample=48000,atrim=0:{total},volume=volume='pow(10,({gain:.2f}-{M['duck_db']}*{speech_expr(ph)})/20)*{gate}':eval=frame,"
                      f"afade=t=out:st={fade_from:.3f}:d={fade_to - fade_from:.3f},apad=whole_dur={total}[bed]")
        mixes.append("[bed]"); n += 1
    else:
        print("no audio/music.mp3: mixing without a bed", file=sys.stderr)
    gains, missing = {}, set()
    for p in pts["sfx"]:
        kind = lib["alias"].get(p["kind"], p["kind"])
        f = ROOT / f"audio/sfx/{kind}.wav"
        if not f.exists():
            missing.add(kind); continue
        fam = lib["kinds"].get(kind, ["", 0, "other"])[2]
        if kind not in gains:
            L = lufs(f)
            if L <= -60:  # silent or broken: never boost it into the mix
                missing.add(f"{kind} (silent take: run `studio sfx` again)"); gains[kind] = None; continue
            gains[kind] = max(-30.0, min(12.0, M["sfx_lufs"] + FAMILY.get(fam, 0) - L))
        if gains[kind] is None:
            continue
        tone = ",lowpass=f=6000" if fam == "tonal" else ""
        inputs += ["-i", str(f)]
        chains.append(f"[{n}:a]aresample=48000{tone},volume={gains[kind]:.2f}dB,adelay={int(round(max(0, p['t']) * 1000))}:all=1[x{n}]")
        mixes.append(f"[x{n}]"); n += 1
    for e in pts.get("audio", []):
        f = ROOT / e["file"]
        if not f.exists():
            missing.add(e["file"]); continue
        trim = f"atrim={e.get('from', 0)}:{e['to']}," if "to" in e else (f"atrim=start={e['from']}," if "from" in e else "")
        fx = (e["filter"] + ",") if e.get("filter") else ""
        fades = (f"afade=t=in:d={e['fadeIn']}," if e.get("fadeIn") else "")
        if e.get("fadeOut") and "to" in e:
            fades += f"afade=t=out:st={max(0, e['to'] - e.get('from', 0) - e['fadeOut']):.3f}:d={e['fadeOut']},"
        inputs += ["-i", str(f)]
        chains.append(f"[{n}:a]aresample=48000,{trim}asetpts=PTS-STARTPTS,{fx}{fades}volume={e.get('gain', 0)}dB,"
                      f"aformat=channel_layouts=stereo,adelay={int(round(e['t'] * 1000))}:all=1[x{n}]")
        mixes.append(f"[x{n}]"); n += 1
    graph = ";".join(chains) + ";" + "".join(mixes) + f"amix=inputs={len(mixes)}:normalize=0:duration=first,atrim=0:{total}[a]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[a]",
                    "-ar", "48000", "-c:a", "pcm_s24le", str(ROOT / "audio/mix.wav")], check=True)
    print(f"audio/mix.wav: {len(mixes)} tracks, {len(pts['sfx'])} effect points, {total:.2f} s")
    if gains:
        print("effect gains: " + ", ".join(f"{k} {g:+.1f} dB" for k, g in sorted(((k, g) for k, g in gains.items() if g is not None), key=lambda kv: kv[1])))
    if missing:
        print("MISSING (left out of the mix): " + ", ".join(sorted(missing)) + ". Run `studio sfx` for effects.")


if __name__ == "__main__":
    main()
