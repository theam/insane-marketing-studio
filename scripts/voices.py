#!/usr/bin/env python3
"""The narration: every sentence of script.md is its own ElevenLabs take, placed by its audible edges.

Extracted from the Shepherdr production (voices.py). Each sentence (a "chunk") is one text-to-speech
call in its speaker's voice, so any one of them can be re-taken, trimmed or dropped without touching the rest. A chunk
starts with the delivery tag in force at that point of the paragraph (Eleven v4 tags hold until the next one).

Processing per take: long pauses inside it are shortened (silencedetect at timing.silence_db), its leading and trailing
silence is trimmed, it is time-stretched (the voice's tempo; TTS speed barely changes the length) and run through the
voice's chain (broadcast punch for the narrator, a telephone filter for a cameo). Takes are then placed one after
another by their audible edges, with tight gaps (timing.gap_*: 0.05-0.15 s gives the frantic 80s toy-commercial pace).

  studio voice              generate what's missing (needs ELEVENLABS_API_KEY) and assemble
  studio voice --plan       list the takes that are missing, as JSON, for making them through the ElevenLabs
                            connector instead (save each one to the file it names, then run `studio voice` again)
  studio voice --dry-run    print the chunks and what each costs, without calling anything

Writes audio/voice-lead.wav, timing/chunks.json (every chunk: id, speaker, text, file, span), timing/sections.json and,
when every take has its word alignment (takes made with the key), timing/words-lead.json. Retake a chunk by adding
{"<chunk id>": 2} to audio/lines/retakes.json. The API key is read from the environment and never printed.
"""
import base64, hashlib, json, os, re, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
LINES = ROOT / "audio/lines"
CUE, TAG = re.compile(r"\{#\w+\}"), re.compile(r"\[[^\]]+\]")
CHAINS = {
    "broadcast": "acompressor=threshold=-22dB:ratio=3.5:attack=4:release=70:makeup=3,"
                 "equalizer=f=3200:t=q:w=1.0:g=3,equalizer=f=120:t=q:w=1.0:g=2,asoftclip=type=tanh:threshold=0.9",
    "telephone": "highpass=f=320,lowpass=f=3300,acompressor=threshold=-24dB:ratio=4:attack=3:release=60:makeup=4,"
                 "asoftclip=type=atan:threshold=0.7,volume=1dB",
    "clean": "acompressor=threshold=-24dB:ratio=2:attack=10:release=120:makeup=2",
    "none": "anull",
}

P = json.loads((ROOT / "project.json").read_text())
T = {"lead": 0.5, "gap_sentence": 0.05, "gap_paragraph": 0.10, "gap_section": 0.15, "gap_speaker": 0.10,
     "silence_db": -40, "max_pause": 0.16, "dramatic_pause": 0.38, "chunk_tempo": {}, "chunk_gap": {}, **P.get("timing", {})}


def run(*a, **kw):
    return subprocess.run(a, check=True, capture_output=True, text=True, **kw)


def duration(p):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)).stdout)


def chunks():
    s = (ROOT / "script.md").read_text()
    parts = re.split(r"^## Script[ \t]*$", s, maxsplit=1, flags=re.M)
    if len(parts) < 2:
        sys.exit('script.md needs a "## Script" heading above the narration')
    body = re.split(r"^## ", parts[1], maxsplit=1, flags=re.M)[0]
    out, section, para = [], 0, 0
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"\*\*(\d+)\s*·", line)
        if m:
            if re.search(r"no narrator", line, re.I):
                break
            section = int(m.group(1)); continue
        if line.startswith("**"):
            continue
        speaker = "narrator"
        sm = re.match(r"([A-Z][A-Z0-9_]+):\s*(.*)", line)
        if sm:
            speaker, line = sm.group(1).lower(), sm.group(2)
        line, para, active = CUE.sub("", line).strip(), para + 1, None
        for n, sent in enumerate(x for x in re.split(r"(?<=[.!?…])\s+(?=\S)", line) if x.strip()):
            tags = TAG.findall(sent)
            text = sent if sent.lstrip().startswith("[") or not active else f"{active} {sent}"
            active = tags[-1] if tags else active
            out.append({"id": f"{section:02d}-{para:02d}-{n + 1:02d}", "section": section, "para": para,
                        "speaker": speaker, "text": text.strip()})
    return out


def voice(speaker):
    v = P["voices"].get(speaker)
    if not v:
        sys.exit(f'script.md has a line for "{speaker.upper()}:" but project.json has no voice "{speaker}". '
                 f'Add one under "voices" (voice_id from the ElevenLabs voice library).')
    return v


def take_key(c, take_n):
    v = voice(c["speaker"])
    body = {"text": c["text"], "model_id": v.get("model", "eleven_v4")}
    if v.get("settings"): body["voice_settings"] = v["settings"]
    if take_n > 1: body["seed"] = take_n
    return hashlib.sha1(json.dumps([c["speaker"], v["voice_id"], body]).encode()).hexdigest()[:12], body


def api(path, body):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("No ELEVENLABS_API_KEY. Either add it to your keys file (`studio keys`), or make the missing takes "
                 "through the ElevenLabs connector: `studio voice --plan` lists them.")
    req = urllib.request.Request("https://api.elevenlabs.io" + path, method="POST", data=json.dumps(body).encode(),
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:800]
        if "voice_not_found" in msg or e.code == 404:
            msg += "\nThe voice isn't in this account. Add it from the ElevenLabs voice library (or pick another) and update project.json."
        sys.exit(f"ElevenLabs HTTP {e.code}: {msg}")


def tts(c, take_n=1, generate=True):
    """(mp3, alignment or None) for one reading, generated if missing and allowed."""
    k, body = take_key(c, take_n)
    mp3, meta = LINES / f"{k}.mp3", LINES / f"{k}.json"
    if not mp3.exists():
        if not generate:
            return None, None
        v = voice(c["speaker"])
        data = json.loads(api(f"/v1/text-to-speech/{v['voice_id']}/with-timestamps?output_format=mp3_44100_192", body))
        mp3.write_bytes(base64.b64decode(data["audio_base64"]))
        meta.write_text(json.dumps(data.get("alignment") or data.get("normalized_alignment")))
    al = json.loads(meta.read_text()) if meta.exists() else None
    return mp3, al


def words_of(al):
    if not al:
        return None
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    text = "".join(chars)
    tagged = set()
    for m in TAG.finditer(text):
        tagged.update(range(m.start(), m.end()))
    words, cur = [], []
    for i, ch in enumerate(text + " "):
        if i < len(text) and not ch.isspace() and i not in tagged:
            cur.append(i); continue
        if cur:
            words.append({"word": text[cur[0]:cur[-1] + 1], "start": st[cur[0]], "end": en[cur[-1]]}); cur = []
    return words


def silences(path, db, min_d):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"silencedetect=n={db}dB:d={min_d}",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    total = duration(path)
    return [(max(0.0, a), e[i] if i < len(e) else total) for i, a in enumerate(s)], total


def audible(wav):
    """(first, last) second of sound in a take (silencedetect at silence_db), cached beside it."""
    side = wav.with_suffix(".edges.json")
    if side.exists():
        return tuple(json.loads(side.read_text()))
    sil, total = silences(wav, T["silence_db"], 0.02)
    first = sil[0][1] if sil and sil[0][0] <= 0.001 else 0.0
    last = sil[-1][0] if sil and sil[-1][1] >= total - 0.005 else total
    side.write_text(json.dumps([round(first, 4), round(last, 4)]))
    return first, last


def process(mp3, words, c):
    """Shorten long pauses, trim the edges, time-stretch and run the speaker's chain.
    Returns the processed take and its words shifted into it (None without an alignment)."""
    v = voice(c["speaker"])
    tempo = T["chunk_tempo"].get(c["id"], v.get("tempo", 1.0))
    chain = CHAINS.get(v.get("chain", "none"), v.get("chain", "anull"))
    sig = hashlib.sha1(json.dumps([tempo, chain, T["max_pause"], T["dramatic_pause"], T["silence_db"]]).encode()).hexdigest()[:6]
    out = mp3.with_name(mp3.stem + f".proc-{sig}.wav")
    sil, total = silences(mp3, T["silence_db"], 0.05)
    inner = [(a, b) for a, b in sil if a > 0.001 and b < total - 0.005]
    first = sil[0][1] if sil and sil[0][0] <= 0.001 else 0.0
    last = sil[-1][0] if sil and sil[-1][1] >= total - 0.005 else total
    keep, t0 = [], max(0.0, first - 0.04)
    for a, b in inner:
        limit = T["max_pause"]
        if words:  # after an ellipsis, a dramatic pause is allowed
            before = [w for w in words if w["end"] <= a + 0.05]
            if before and before[-1]["word"].rstrip('"”').endswith(("...", "…")):
                limit = T["dramatic_pause"]
        if b - a > limit:
            keep.append((t0, a + limit / 2)); t0 = b - limit / 2
    keep.append((t0, min(total, last + 0.1)))
    if not out.exists():
        graph = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}];" for i, (a, b) in enumerate(keep))
        graph += "".join(f"[s{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,{atempo(tempo)},{chain}[o]"
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3), "-filter_complex", graph,
            "-map", "[o]", "-ar", "44100", "-ac", "1", str(out))

    def remap(x):
        acc = 0.0
        for a, b in keep:
            if x <= b: return acc + max(0.0, x - a)
            acc += b - a
        return acc
    shifted = [{"word": w["word"], "start": round(remap(w["start"]) / tempo, 3), "end": round(remap(w["end"]) / tempo, 3)}
               for w in words] if words else None
    return out, shifted


def atempo(x):
    """ffmpeg's atempo takes 0.5-2.0 per stage: chain stages for anything outside."""
    parts = []
    while x > 2.0: parts.append(2.0); x /= 2.0
    while x < 0.5: parts.append(0.5); x /= 0.5
    parts.append(x)
    return ",".join(f"atempo={p:.5f}" for p in parts)


def main():
    LINES.mkdir(parents=True, exist_ok=True)
    rt = LINES / "retakes.json"
    retakes = json.loads(rt.read_text()) if rt.exists() else {}
    cs = chunks()
    if "--dry-run" in sys.argv:
        n = 0
        for c in cs:
            n += len(c["text"])
            print(f'{c["id"]}  {c["speaker"]:10} {c["text"]}')
        print(f"{len(cs)} chunks, {n} characters (about {n} ElevenLabs credits for one take of each)")
        return
    if "--plan" in sys.argv:
        need = []
        for c in cs:
            k, body = take_key(c, retakes.get(c["id"], 1))
            if not (LINES / f"{k}.mp3").exists():
                v = voice(c["speaker"])
                need.append({"chunk": c["id"], "voice_id": v["voice_id"], "model_id": body["model_id"], "prompt": c["text"],
                             "save_to": str((LINES / f"{k}.mp3").relative_to(ROOT))})
        print(json.dumps(need, indent=1))
        print(f"{len(need)} takes missing of {len(cs)}", file=sys.stderr)
        return
    have_key = bool(os.environ.get("ELEVENLABS_API_KEY"))
    t, prev, parts, words, manifest, sound_end, aligned = T["lead"], None, [], [], [], None, True
    missing = []
    for c in cs:
        take = retakes.get(c["id"], 1)
        mp3, al = tts(c, take, generate=have_key)
        if mp3 is None:
            missing.append(c["id"]); continue
        wav, ws = process(mp3, words_of(al), c)
        first, last = audible(wav)
        if prev:
            gap = T["chunk_gap"][c["id"]] if c["id"] in T["chunk_gap"] else (
                T["gap_section"] if c["section"] != prev["section"] else T["gap_speaker"] if c["speaker"] != prev["speaker"]
                else T["gap_sentence"] if c["para"] == prev["para"] else T["gap_paragraph"])
            t = sound_end + gap - first
        sound_end = t + last
        parts.append((wav, t))
        if ws is None:
            aligned = False
        else:
            words += [{"word": w["word"], "start": round(t + w["start"], 3), "end": round(t + w["end"], 3), "speaker": c["speaker"]} for w in ws]
        manifest.append({**c, "file": str(wav.relative_to(ROOT)), "take": take, "start": round(t, 3),
                         "sound": [round(t + first, 3), round(t + last, 3)]})
        prev = c
    if missing:
        sys.exit(f"{len(missing)} takes are missing ({', '.join(missing)}). Make them with the key, or through the "
                 f"ElevenLabs connector (`studio voice --plan`), then run `studio voice` again.")
    inputs, chain = [], []
    for i, (wav, start) in enumerate(parts):
        inputs += ["-i", str(wav)]
        chain.append(f"[{i}:a]aresample=44100,adelay={int(round(start * 1000))}:all=1[a{i}]")
    graph = ";".join(chain) + ";" + "".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0:duration=longest[out]"
    (ROOT / "audio").mkdir(exist_ok=True)
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]",
        "-ar", "44100", "-c:a", "pcm_s16le", str(ROOT / "audio/voice-lead.wav"))
    (ROOT / "timing").mkdir(exist_ok=True)
    (ROOT / "timing/chunks.json").write_text(json.dumps(manifest, indent=1))
    spans = {}
    for m in manifest:
        sp = spans.setdefault(str(m["section"]), {"start": m["sound"][0], "end": m["sound"][1]})
        sp["end"] = max(sp["end"], m["sound"][1])
    (ROOT / "timing/sections.json").write_text(json.dumps(spans, indent=1))
    end = manifest[-1]["sound"][1]
    if aligned:
        (ROOT / "timing/words-lead.json").write_text(json.dumps(words, indent=1))
        print(f"{len(cs)} chunks, {len(words)} words; narration ends at {end:.2f} s. Next: `studio timing`.")
    else:
        stale = ROOT / "timing/words-lead.json"
        if stale.exists(): stale.unlink()
        print(f"{len(cs)} chunks; narration ends at {end:.2f} s. Some takes have no word alignment (made through the "
              f"connector): transcribe audio/voice-lead.wav with Scribe, save the words to timing/scribe-words.json, "
              f"then `studio timing timing/scribe-words.json`.")


if __name__ == "__main__":
    main()
