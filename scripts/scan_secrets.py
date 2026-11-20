#!/usr/bin/env python3
"""Look for API keys and other secrets before anything is committed or pushed. Run it on a project before every push.

  studio scan              the current folder (files git would commit: tracked and untracked, not ignored)
  studio scan DIR
  studio scan --staged     only what's staged in git

Exit code 1 and a list of file:line when something looks like a secret. It also fails when a value from your keys
file appears anywhere, whatever its shape.
"""
import os, re, subprocess, sys
from pathlib import Path

PATTERNS = [
    ("ElevenLabs key", re.compile(r"\bsk_[0-9a-f]{40,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-(?:proj-|or-v1-)?[A-Za-z0-9_\-]{32,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("key assignment", re.compile(r"(?i)\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*['\"]?[A-Za-z0-9_\-:.]{16,}")),
]
TEXT = {".py", ".js", ".json", ".md", ".html", ".css", ".sh", ".txt", ".env", ".yml", ".yaml", ".toml", ".jsonl", ".swift", ""}


def files(root, staged):
    try:
        if staged:
            out = subprocess.check_output(["git", "-C", str(root), "diff", "--cached", "--name-only", "-z"], text=True)
        else:
            out = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"], text=True)
        return [root / f for f in out.split("\0") if f]
    except subprocess.CalledProcessError:
        return [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


def main():
    a = sys.argv[1:]
    staged = "--staged" in a
    root = Path(next((x for x in a if not x.startswith("--")), ".")).resolve()
    own = set()
    kf = Path(os.environ.get("STUDIO_KEYS", Path.home() / ".config/insane-marketing-studio/keys.env"))
    if kf.exists():
        for line in kf.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                v = line.split("=", 1)[1].strip().strip("'\"")
                if len(v) >= 12: own.add(v)
    hits = []
    for f in files(root, staged):
        if not f.exists() or f.suffix.lower() not in TEXT or f.stat().st_size > 5_000_000:
            continue
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        if f.name.endswith(".env") or f.name == ".env":
            hits.append((f, 0, "an .env file (keys belong in ~/.config/insane-marketing-studio/keys.env, never in a project)"))
        for n, line in enumerate(text.splitlines(), 1):
            for name, rx in PATTERNS:
                if rx.search(line) and "example" not in line.lower():
                    hits.append((f, n, name))
            if any(v in line for v in own):
                hits.append((f, n, "a value from your keys file"))
    for f, n, what in hits:
        print(f"SECRET? {f.relative_to(root)}:{n}  {what}")
    print(f"{'found ' + str(len(hits)) + ' possible secrets' if hits else 'no secrets found'} in {root}")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
