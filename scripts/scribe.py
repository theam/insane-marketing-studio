#!/usr/bin/env python3
"""Word timestamps of any audio or video file with ElevenLabs Scribe (key). The connector does the same without a key:
upload the file, transcribe it, and save its words_download_url with `studio fetch` (the voice skill shows how).

  studio scribe audio/voice-lead.wav timing/stt-check.json      check the narration: every word heard?
  studio scribe gen/clips/e5/take-1.mp4 gen/clips/e5/words.json  where the words of a generated clip really are

Writes {"text": ..., "words": [{text, start, end, type}]}: the format `studio timing words.json` reads.
Seedance's reference-to-video does NOT follow the reference audio's timing: the mouth follows the take's own audio,
so place the lines at the times Scribe hears in the take.
"""
import json, mimetypes, os, sys, uuid, urllib.error, urllib.request
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("No ELEVENLABS_API_KEY: use the ElevenLabs connector's transcription instead (see the voice skill).")
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\nscribe_v1\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"timestamps_granularity\"\r\n\r\nword\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{src.name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(src.name)[0] or 'application/octet-stream'}\r\n\r\n").encode() + src.read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs HTTP {e.code}: {e.read().decode()[:800]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"text": data.get("text"), "words": data.get("words", [])}, indent=1))
    w = [x for x in data.get("words", []) if x.get("type") == "word"]
    print(f"{out}: {len(w)} words, {w[0]['start'] if w else 0:.2f}-{w[-1]['end'] if w else 0:.2f} s")
    print(data.get("text", "")[:400])


if __name__ == "__main__":
    main()
