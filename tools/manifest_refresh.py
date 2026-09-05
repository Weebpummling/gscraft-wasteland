"""Refresh build/manifest.json against G:/GSCraft/server/mods: every jar in server/mods gets an entry (sha256, modids and
requires read from its mods.toml; role "keep"), entries with role "keep" whose jar is no longer in server/mods are dropped
(replaced versions), every other role (nested libraries, client-only, conditional) is left as it is.
usage: manifest_refresh.py [--dry-run]"""
import hashlib, json, re, sys, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MODS = Path("G:/GSCraft/server/mods"); OUT = REPO / "build" / "manifest.json"


def sha256(p):
    h = hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()


def read_toml(jar):
    """modids and hard dependencies from META-INF/mods.toml (a light regex read; the file is small and regular)."""
    try:
        z = zipfile.ZipFile(jar); t = z.read("META-INF/mods.toml").decode("utf-8", "ignore")
    except Exception:
        return [], [], []
    modids = re.findall(r'^\s*modId\s*=\s*"([^"]+)"', t, re.M)
    deps = []
    for block in re.split(r'\[\[dependencies\.', t)[1:]:
        m = re.search(r'modId\s*=\s*"([^"]+)"', block); mand = re.search(r'mandatory\s*=\s*(true|false)', block)
        if m and m.group(1) not in ("forge", "minecraft") and (not mand or mand.group(1) == "true"): deps.append(m.group(1))
    nested = [n.split("/")[-1] for n in z.namelist() if n.startswith("META-INF/jarjar/") and n.endswith(".jar")]
    return sorted(set(modids)), sorted(set(deps) - set(modids)), nested


def main(a):
    dry = "--dry-run" in a
    man = json.load(open(OUT, encoding="utf-8"))
    present = {p.name: p for p in MODS.glob("*.jar")}
    roles = {}
    for k, v in man.items(): roles[v.get("role", "?")] = roles.get(v.get("role", "?"), 0) + 1
    print("roles before:", roles)
    # replaced versions: an entry whose jar is gone and whose mod ids are now served by another jar in server/mods
    served = {}
    for name, p in present.items():
        for mid in read_toml(p)[0]: served.setdefault(mid, name)
    dropped = [k for k, v in man.items() if k not in present and v.get("side") != "client"
               and ((v.get("role") == "keep") or any(m in served for m in v.get("modids", [])))]
    carried = {m: man[k] for k in dropped for m in man[k].get("modids", [])}      # a renamed jar keeps its old role
    for k in dropped: del man[k]
    added = []
    for name, p in sorted(present.items()):
        if name in man:
            if man[name].get("sha256") != sha256(p): man[name]["sha256"] = sha256(p); added.append(name + " (hash)")
            continue
        modids, deps, nested = read_toml(p)
        prev = next((carried[m] for m in modids if m in carried), None)
        man[name] = {"role": prev.get("role", "keep") if prev else "keep", "sha256": sha256(p), "modids": modids, "nested": nested, "requires": deps}
        if prev and prev.get("side"): man[name]["side"] = prev["side"]
        added.append(name)
    print(f"dropped {len(dropped)}: {dropped}")
    print(f"added/updated {len(added)}: {added}")
    if not dry:
        json.dump(dict(sorted(man.items())), open(OUT, "w", encoding="utf-8", newline="\n"), indent=2); print("->", OUT, len(man), "entries")


if __name__ == "__main__":
    main(sys.argv)
