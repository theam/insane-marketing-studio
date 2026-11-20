#!/usr/bin/env python3
"""Seedance 2.5 clips on Higgsfield's API, with an estimate first, a cost cap, a ledger and idempotency keys.

Extracted from the Shepherdr production (seedance_hf.py, generalized). Shots are in gen/shots.json:

  {"cap_usd": 20,
   "shots": [
     {"id": "e1", "prompt": "…", "first_frame": "assets/gen/plates/e1.png", "duration": 5, "resolution": "720p"},
     {"id": "e2", "prompt": "…", "first_frame": "after:e1"},         starts on e1's picked (or first delivered) take's last frame
     {"id": "e3", "prompt": "…", "first_frame": "after:e1@3.0"},     … or its frame at 3.0 s
     {"id": "e5", "prompt": "…", "first_frame": "assets/gen/plates/e5.png", "reference_audio": "audio/lines/hey.wav"}
   ]}                                                                 reference_audio = lip-sync (reference-to-video)

  studio seedance estimate             price one take of every shot (free; the API's own estimate)
  studio seedance run e1 e2 [--takes 1]   submit, poll and download → gen/clips/<id>/take-N.mp4
  studio seedance poll                 poll takes in flight once

Every take is written to gen/clips/<id>.json BEFORE its POST, with an Idempotency-Key, so a retry never pays twice;
the run stops before the estimates would pass cap_usd. Every event goes to gen/ledger.jsonl. Higgsfield's balance is
not readable through the API: when it runs dry, takes fail with "credit balance is too low" and the run stops.
Reference-to-video does NOT follow the reference audio's timing: run `studio scribe` on the delivered take and place
the lines at the times it hears. HIGGSFIELD_API_KEY ("<key id>:<secret>") is sent only to api.higgsfield.ai.
"""
import hashlib, json, math, os, re, subprocess, sys, time, urllib.error, urllib.request, uuid
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
API = "https://api.higgsfield.ai"
EP = {"reference": "bytedance/seedance-2.5/reference-to-video", "first_frame": "bytedance/seedance-2.5/image-to-video"}
LIVE, FREE = ("sending", "queued", "in_progress"), ("declined", "failed", "nsfw", "canceled")
CLIPS = ROOT / "gen/clips"


def key():
    k = os.environ.get("HIGGSFIELD_API_KEY")
    if not k:
        sys.exit("No HIGGSFIELD_API_KEY. Add it with `studio keys` (as <key id>:<secret>).")
    return k


def call(method, url, body=None, headers=None, data=None, raw=False):
    h = {"User-Agent": "insane-marketing-studio/1.0", **(headers or {})}
    if url.startswith("/"): url = API + url
    if url.startswith(API + "/"): h["Authorization"] = f"Key {key()}"
    if body is not None: data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method=method, data=data, headers=h), timeout=300) as r:
            out = r.read()
            return r.status, (out if raw else json.loads(out or b"{}"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try: return e.code, json.loads(txt)
        except ValueError: return e.code, {"detail": txt[:500]}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, {"detail": f"network: {e}"}


def log(**kw):
    with open(ROOT / "gen/ledger.jsonl", "a") as f: f.write(json.dumps({"ts": time.strftime("%FT%T"), **kw}) + "\n")


def spec():
    s = json.loads((ROOT / "gen/shots.json").read_text())
    if "cap_usd" not in s:
        sys.exit("gen/shots.json needs a cap_usd: the most this project may spend on clips (agreed with whoever pays).")
    return s


def records():
    CLIPS.mkdir(parents=True, exist_ok=True)
    out = {}
    for s in spec()["shots"]:
        f = CLIPS / f"{s['id']}.json"
        r = json.loads(f.read_text()) if f.exists() else {"id": s["id"], "takes": []}
        r.update(mode="reference" if s.get("reference_audio") else "first_frame", start=s["first_frame"], audio=s.get("reference_audio"),
                 body={"prompt": s["prompt"], "duration": s.get("duration", 5), "resolution": s.get("resolution", "720p"),
                       "aspect_ratio": s.get("aspect_ratio", "16:9")})
        out[s["id"]] = r
    return out


def save(r): (CLIPS / f"{r['id']}.json").write_text(json.dumps(r, indent=2))


def body_for(r, img, aud):
    b = r["body"]
    if r["mode"] == "reference":
        return {"prompt": b["prompt"], "duration": b["duration"], "resolution": b["resolution"], "aspect_ratio": b["aspect_ratio"],
                "generate_audio": True, "image_urls": [img], "audio_urls": [aud]}
    return {"prompt": b["prompt"], "duration": b["duration"], "resolution": b["resolution"], "generate_audio": False, "image_url": img}


def estimate_one(r, img="https://example.com/a.png", aud="https://example.com/a.wav"):
    code, resp = call("POST", f"/estimate/{EP[r['mode']]}", body_for(r, img, aud))
    if code != 200: return None, f"{code} {json.dumps(resp)[:200]}"
    if resp.get("usd") is not None: return float(resp["usd"]), resp
    m = re.search(r"1,000 video tokens costs \$([\d.]+) at 480p or 720p", resp.get("pricing_description", ""))
    if not m: return None, f"unreadable estimate: {json.dumps(resp)[:200]}"
    w, h = (1280, 720) if r["body"]["resolution"] == "720p" else (1920, 1080)
    tokens = math.ceil(w * h * r["body"]["duration"] * 24 / 1024)
    return round(tokens / 1000 * float(m[1]), 4), f"{tokens} tokens"


def committed(recs):
    return sum(t.get("est_usd", 0) for r in recs.values() for t in r["takes"] if t["status"] not in FREE)


def upload(path, ctype):
    code, u = call("POST", "/files/generate-upload-url", {"content_type": ctype})
    if code != 200: raise RuntimeError(f"upload url {code} {json.dumps(u)[:200]}")
    c2, _ = call("PUT", u["upload_url"], data=Path(path).read_bytes(), headers=u.get("upload_headers", {}), raw=True)
    if c2 not in (200, 201, 204): raise RuntimeError(f"upload put {c2}")
    return u["public_url"]


def start_frame(r, recs):
    if not r["start"].startswith("after:"):
        return ROOT / r["start"]
    sid, at = (r["start"][6:].split("@") + [None])[:2]
    picks = json.loads((ROOT / "gen/picks.json").read_text()).get("shots", {}) if (ROOT / "gen/picks.json").exists() else {}
    src = next((ROOT / p["take"] for p in picks.values() if f"/{sid}/" in p["take"]), None)
    if src is None:
        done = [t for t in recs[sid]["takes"] if t["status"] == "delivered"]
        if not done: return None
        src = ROOT / done[0]["file"]
    out = CLIPS / f"{r['id']}-start.png"
    seek = ["-ss", at] if at else ["-sseof", "-0.1"]
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *seek, "-i", str(src), "-frames:v", "1", str(out)], check=True)
    return out


def submit(r, recs, cap):
    img_path = start_frame(r, recs)
    if img_path is None: return "wait"
    img = upload(img_path, "image/png")
    aud = upload(ROOT / r["audio"], "audio/wav") if r["mode"] == "reference" else None
    body = body_for(r, img, aud)
    usd, info = estimate_one(r, img, aud)
    if usd is None: print(r["id"], "estimate failed:", info); return "skip"
    if committed(recs) + usd > cap: print(f"STOP: the cap (${cap}) would be passed"); return "stop"
    t = {"n": len(r["takes"]) + 1, "endpoint": EP[r["mode"]], "idem": str(uuid.uuid4()), "status": "sending", "est_usd": usd,
         "prompt_sha": hashlib.sha1(body["prompt"].encode()).hexdigest()[:12], "prompt": body["prompt"]}
    r["takes"].append(t); save(r)
    for attempt in range(4):
        code, resp = call("POST", f"/{t['endpoint']}", body, headers={"Idempotency-Key": t["idem"]})
        if code == 0 or code >= 500: time.sleep(5 * 2 ** attempt); continue
        break
    detail = json.dumps(resp)[:300]
    if code in (200, 201, 202) and resp.get("request_id"):
        t.update(status=resp.get("status", "queued"), job=resp["request_id"], status_url=resp["status_url"], submitted_at=time.strftime("%FT%T"))
        res = "ok"
    elif code == 400 and "concurrent" in detail.lower():
        r["takes"].remove(t); save(r); return "busy"
    elif code == 0 or code >= 500:
        print(r["id"], "no answer; the take stays 'sending' (its Idempotency-Key makes a retry safe):", detail); save(r); return "skip"
    else:
        t.update(status="declined", http=code, est_usd=0, error=resp)
        res = "stop" if code in (401, 402, 403) else "skip"
    save(r); log(event="submit", clip=r["id"], take=t["n"], http=code, status=t["status"], est_usd=t["est_usd"], detail=detail if t["status"] == "declined" else None)
    print(r["id"], f"take {t['n']}:", t["status"], code, "" if t["status"] in LIVE else detail, flush=True)
    return res


def poll(recs):
    live = 0
    for r in recs.values():
        changed = False
        for t in r["takes"]:
            if t["status"] not in ("queued", "in_progress"): continue
            code, resp = call("GET", t["status_url"])
            if code != 200: live += 1; continue
            st = resp.get("status")
            if st == "completed":
                c2, data = call("GET", resp["video"]["url"], raw=True)
                if c2 == 200 and isinstance(data, bytes) and len(data) > 10000:
                    out = CLIPS / r["id"] / f"take-{t['n']}.mp4"; out.parent.mkdir(exist_ok=True); out.write_bytes(data)
                    t.update(status="delivered", file=str(out.relative_to(ROOT)), delivered_at=time.strftime("%FT%T"))
                    log(event="delivered", clip=r["id"], take=t["n"], est_usd=t["est_usd"])
                    print(r["id"], f"take {t['n']} delivered → {t['file']}", flush=True)
                else:
                    live += 1; continue
            elif st in ("failed", "nsfw", "canceled"):
                t.update(status=st, error=resp.get("error")); log(event=st, clip=r["id"], take=t["n"], error=resp.get("error"))
                print(r["id"], f"take {t['n']}:", st, resp.get("error"), flush=True)
            else:
                t["status"] = st; live += 1
            changed = True
        if changed: save(r)
    return live


def run(ids, takes):
    cap = float(spec()["cap_usd"])
    recs = records()
    queue = [(cid, n) for cid in ids for n in range(takes) if sum(1 for t in recs[cid]["takes"] if t["status"] not in FREE) <= n]
    stopped = False
    while True:
        recs = records()
        for cid, r in recs.items():  # keep the takes already recorded
            f = CLIPS / f"{cid}.json"
            if f.exists(): r["takes"] = json.loads(f.read_text())["takes"]
        live = poll(recs)
        held = []
        while queue and live < 4 and not stopped:
            cid, n = queue.pop(0)
            res = submit(recs[cid], recs, cap)
            if res == "busy": queue.insert(0, (cid, n)); break
            if res == "wait": held.append((cid, n)); continue
            if res == "ok": live += 1
            if res == "stop": stopped = True; queue.clear()
        queue = held + queue
        if (not queue or stopped) and live == 0: break
        print(time.strftime("%T"), f"in flight {live}, waiting {len(queue)}, committed ${committed(recs):.2f} of ${cap}", flush=True)
        time.sleep(20)
    print(f"done; committed ${committed(records()):.2f} of ${cap} (estimates: quote real spend from Higgsfield's billing page)")


if __name__ == "__main__":
    args = sys.argv[1:] or ["estimate"]
    if args[0] == "estimate":
        recs, tot = records(), 0
        for r in recs.values():
            usd, info = estimate_one(r); tot += usd or 0
            print(f"{r['id']:8} {r['mode']:11} {r['body']['duration']} s {r['body']['resolution']}  ${usd}  {info if usd is None else ''}")
        print(f"total ${tot:.2f} for one take of every shot (cap ${spec()['cap_usd']}). Generated seconds usually run about 2× what the cut uses.")
    elif args[0] == "run":
        takes = int(args[args.index("--takes") + 1]) if "--takes" in args else 1
        ids = [a for a in args[1:] if not a.startswith("--") and not a.isdigit()] or [s["id"] for s in spec()["shots"]]
        run(ids, takes)
    elif args[0] == "poll":
        print(poll(records()), "in flight")
    else:
        sys.exit(__doc__)
