"""Upload every zip in a release folder to the GitHub release, skipping assets already there
(matched by name and size). Re-run until it reports nothing missing.

usage: release_upload.py [tag] [folder]
Needs the GitHub CLI (`gh`) signed in to the account that owns the repository.
"""
import json, shutil, subprocess, sys, time
from pathlib import Path

GH = shutil.which("gh") or "gh"
REPO = "Weebpummling/gscraft-wasteland"
TAG = sys.argv[1] if len(sys.argv) > 1 else "handoff-2026-09-02"
REL = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(r"C:\GSCraft\release")


def present():
    out = subprocess.run([GH, "release", "view", TAG, "-R", REPO, "--json", "assets"], capture_output=True, text=True).stdout
    try:
        return {a["name"]: a["size"] for a in json.loads(out)["assets"]}
    except Exception:
        return {}


def main():
    have = present()
    todo = [p for p in sorted(REL.glob("*.zip")) if have.get(p.name) != p.stat().st_size]
    print(f"{len(have)} assets on the release; {len(todo)} to upload", flush=True)
    for p in todo:
        t = time.time()
        r = subprocess.run([GH, "release", "upload", TAG, str(p), "-R", REPO, "--clobber"], capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{'ok  ' if ok else 'FAIL'} {p.stat().st_size / 1e6:7.1f} MB  {p.name}  ({int(time.time() - t)} s)", flush=True)
        if not ok:
            print("    ", (r.stderr or r.stdout).strip()[-300:], flush=True)
    have = present()
    missing = [p.name for p in REL.glob("*.zip") if have.get(p.name) != p.stat().st_size]
    print(f"assets on release: {len(have)}; still missing: {missing}", flush=True)


if __name__ == "__main__":
    main()
