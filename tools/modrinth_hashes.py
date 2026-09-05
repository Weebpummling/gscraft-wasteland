"""Refresh scratch/modrinth_files.json (the packwiz_build.py input) against the jars in G:/GSCraft/server/mods: every jar
whose sha1 is not in the file is looked up on Modrinth by hash; entries for jars no longer in server/mods are dropped.
usage: modrinth_hashes.py [--dry-run]"""
import hashlib, json, sys, time, urllib.request
from pathlib import Path

G = Path("G:/GSCraft"); MODS = G / "server" / "mods"; OUT = G / "scratch" / "modrinth_files.json"
UA = "gscraft-updater/1.0 (github.com/Weebpummling/gscraft-wasteland)"


def sha1(p):
    h = hashlib.sha1(); h.update(p.read_bytes()); return h.hexdigest()


def sha512(p):
    h = hashlib.sha512(); h.update(p.read_bytes()); return h.hexdigest()


def lookup(sha):
    req = urllib.request.Request(f"https://api.modrinth.com/v2/version_file/{sha}?algorithm=sha1", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise


def main(a):
    dry = "--dry-run" in a
    data = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {}
    jars = sorted(p.name for p in MODS.glob("*.jar"))
    dropped = [k for k in data if k not in jars]
    for k in dropped: del data[k]
    added, missing = [], []
    for name in jars:
        p = MODS / name
        if name in data and data[name].get("sha1") == sha1(p): continue
        v = lookup(sha1(p)); time.sleep(0.3)
        if not v: missing.append(name); data.pop(name, None); continue
        f = next((f for f in v["files"] if f["hashes"]["sha1"] == sha1(p)), v["files"][0])
        data[name] = {"project_id": v["project_id"], "version_id": v["id"], "version_number": v["version_number"], "url": f["url"],
                      "sha1": f["hashes"]["sha1"], "sha512": f["hashes"].get("sha512") or sha512(p), "size": f["size"], "filename": f["filename"]}
        added.append(f"{name} -> {v['version_number']}")
    print(f"{len(jars)} jars in server/mods; {len(data)} on Modrinth; dropped {len(dropped)}: {dropped}")
    print("added/updated:", *added, sep="\n  ")
    print("not on Modrinth (release-asset jars):", *missing, sep="\n  ")
    if not dry: json.dump(data, open(OUT, "w", encoding="utf-8"), indent=1); print("->", OUT)


if __name__ == "__main__":
    main(sys.argv)
