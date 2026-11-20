#!/usr/bin/env python3
"""Save a file from a connector's result link to disk: how the ElevenLabs connector's takes, effects and transcripts
reach the pipeline. The links are signed and expire after about 2.5 hours, so save them right away.

  studio fetch "<content_url>" audio/lines/ab12cd34ef56.mp3        a speech take (the path `studio voice --plan` names)
  studio fetch "<content_url>" audio/sfx/raw/boing.mp3              an effect (the path `studio sfx --plan` names)
  studio fetch "<words_download_url>" timing/scribe-words.json      Scribe's words, for `studio timing`

  studio put "<upload_url>" audio/voice-lead.wav audio/wav          send a local file to an upload link
                                                                    (the connector's creative_create_asset_upload)
"""
import json, sys, urllib.request
from pathlib import Path


def put(url, path, mime):
    data = Path(path).read_bytes()
    req = urllib.request.Request(url, data=data, method="PUT", headers={"Content-Type": mime, "User-Agent": "insane-marketing-studio/1.0"})
    with urllib.request.urlopen(req, timeout=600) as r:
        print(f"uploaded {path} ({len(data):,} bytes): HTTP {r.status}")


def main():
    if len(sys.argv) == 5 and sys.argv[1] == "--put":
        return put(sys.argv[2], sys.argv[3], sys.argv[4])
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    url, out = sys.argv[1], Path(sys.argv[2])
    if not url.startswith("https://"):
        sys.exit("expected an https link from the connector's result")
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "insane-marketing-studio/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data, ctype = r.read(), r.headers.get("Content-Type", "")
    if out.suffix == ".json":
        words = json.loads(data)
        if isinstance(words, list):  # Scribe's word list on its own: wrap it the way `studio timing` reads it
            data = json.dumps({"words": words}, indent=1).encode()
    out.write_bytes(data)
    print(f"{out} ({len(data):,} bytes, {ctype or 'unknown type'})")


if __name__ == "__main__":
    main()
