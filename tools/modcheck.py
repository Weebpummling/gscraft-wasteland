"""Static conflict review of the jars in G:/GSCraft/server/mods (owner: "do a code review of the mods to see if they would
conflict each other"). Reads every jar's META-INF/mods.toml and mixin configs and reports:
  1. duplicate mod ids (two jars providing the same mod, including jar-in-jar nested jars),
  2. dependency ranges that the installed versions do not satisfy (mandatory and optional),
  3. mixin configs that target the same vanilla classes (a hotspot list; overlap is not a conflict by itself, but the
     classes touched by 3+ mods are where load-order bugs show up),
  4. Forge/Minecraft version ranges vs the installed Forge (47.4.23).
usage: modcheck.py [--forge 47.4.23] [--json out.json]
Version comparison follows Forge's Maven-style rules loosely: dotted numeric segments compared left to right, letters after
numbers ignored; ranges "[a,b)", "[a,)", "(,b]" are honoured. Anything it cannot parse is reported as 'unparsed'.
"""
import json, re, sys, zipfile, io, collections
from pathlib import Path

MODS = Path("G:/GSCraft/server/mods")
FORGE = sys.argv[sys.argv.index("--forge") + 1] if "--forge" in sys.argv else "47.4.23"
MC = "1.20.1"


def toml_lite(text):
    """Enough TOML for mods.toml: top-level keys, [[mods]] tables, [[dependencies.<id>]] tables."""
    mods, deps, top = [], collections.defaultdict(list), {}
    cur = top
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip() if not raw.strip().startswith("#") else ""
        if not line: continue
        m = re.match(r"^\[\[(.+?)\]\]$", line)
        if m:
            name = m.group(1).strip()
            if name == "mods": cur = {}; mods.append(cur)
            elif name.startswith("dependencies."): cur = {}; deps[name.split(".", 1)[1].strip('"')].append(cur)
            else: cur = {}
            continue
        if re.match(r"^\[.+\]$", line): cur = {}; continue
        m = re.match(r'^([A-Za-z0-9_\-]+)\s*=\s*(.+)$', line)
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith('"""'): v = v.strip('"')
        elif v.startswith('"') or v.startswith("'"): v = v[1:].rsplit(v[0], 1)[0]
        elif v in ("true", "false"): v = v == "true"
        cur[k] = v
    return top, mods, deps


def ver_key(v):
    v = str(v).split("+", 1)[0].split("-", 1)[0]
    parts = []
    for seg in re.split(r"[.]", v):
        m = re.match(r"(\d+)", seg)
        parts.append(int(m.group(1)) if m else 0)
    while len(parts) < 4: parts.append(0)
    return tuple(parts[:6])


def in_range(version, rng):
    """-> True/False/None(unparsed)."""
    rng = rng.strip()
    if not rng or rng == "*": return True
    m = re.match(r"^([\[(])\s*([^,\]\)]*)\s*(?:,\s*([^\]\)]*))?\s*([\])])$", rng)
    if not m:
        if re.match(r"^[\w.\-+]+$", rng): return ver_key(version) >= ver_key(rng)     # a bare version is a Maven soft requirement: at least that version
        return None
    lo_inc, lo, hi, hi_inc = m.group(1) == "[", m.group(2).strip(), m.group(3), m.group(4) == "]"
    v = ver_key(version)
    if hi is None:                    # "[1.2]" exact
        return v == ver_key(lo)
    hi = hi.strip()
    if lo:
        if v < ver_key(lo) or (v == ver_key(lo) and not lo_inc): return False
    if hi:
        if v > ver_key(hi) or (v == ver_key(hi) and not hi_inc): return False
    return True


def read_jar(path, nested_from=None):
    out = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        info = {"jar": path.name if nested_from is None else f"{nested_from} :: {Path(path.name).name}", "mods": [], "deps": {}, "mixins": [], "mixin_targets": [], "nested": []}
        if "META-INF/mods.toml" in names:
            top, mods, deps = toml_lite(z.read("META-INF/mods.toml").decode("utf-8", "replace"))
            info["mods"] = mods; info["deps"] = deps
            # ${file.jarVersion} -> Implementation-Version from the manifest
            impl = None
            if "META-INF/MANIFEST.MF" in names:
                mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
                mm = re.search(r"^Implementation-Version:\s*(.+)$", mf, re.M); impl = mm.group(1).strip() if mm else None
                for cfg in re.findall(r"^MixinConfigs:\s*(.+)$", mf, re.M): info["mixins"] += [c.strip() for c in cfg.split(",") if c.strip()]
            for m in mods:
                if "${file.jarVersion}" in str(m.get("version", "")): m["version"] = impl or "0"
        for n in names:
            if n.endswith(".mixins.json") or (n.endswith(".json") and "mixin" in n.lower() and "/" not in n):
                try: mj = json.loads(z.read(n).decode("utf-8", "replace"))
                except Exception: continue
                if not isinstance(mj, dict) or "package" not in mj: continue
                if n not in info["mixins"]: info["mixins"].append(n)
                pkg = mj.get("package", "")
                for grp in ("mixins", "client", "server"):
                    for cls in mj.get(grp, []) or []:
                        info["mixin_targets"].append((n, grp, f"{pkg}.{cls}"))
        out.append(info)
        for n in names:
            if n.startswith("META-INF/jarjar/") and n.endswith(".jar"):
                try: out += read_jar_bytes(z.read(n), n, info["jar"])
                except Exception as e: info["nested"].append(f"{n}: unreadable ({e})")
    return out


def read_jar_bytes(data, name, parent):
    class P:  # minimal path-like for the name
        pass
    p = Path(name)
    tmp = io.BytesIO(data)
    with zipfile.ZipFile(tmp) as z:
        names = z.namelist()
        info = {"jar": f"{parent} :: {p.name}", "mods": [], "deps": {}, "mixins": [], "mixin_targets": [], "nested": []}
        if "META-INF/mods.toml" in names:
            top, mods, deps = toml_lite(z.read("META-INF/mods.toml").decode("utf-8", "replace"))
            impl = None
            if "META-INF/MANIFEST.MF" in names:
                mm = re.search(r"^Implementation-Version:\s*(.+)$", z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace"), re.M); impl = mm.group(1).strip() if mm else None
            for m in mods:
                if "${file.jarVersion}" in str(m.get("version", "")): m["version"] = impl or "0"
            info["mods"] = mods; info["deps"] = deps
    return [info]


def main():
    jars = sorted(MODS.glob("*.jar"))
    infos = []
    for j in jars:
        try: infos += read_jar(j)
        except Exception as e: print(f"!! {j.name}: {e}")
    installed = {"forge": FORGE, "minecraft": MC}
    providers = collections.defaultdict(list)
    for i in infos:
        for m in i["mods"]:
            mid = m.get("modId");
            if not mid: continue
            providers[mid].append((i["jar"], str(m.get("version", "?"))))
            if mid not in installed or "::" not in i["jar"]: installed[mid] = str(m.get("version", "?"))
    print(f"{len(jars)} jars, {len(infos)} mod files incl. nested, {len(installed) - 2} mod ids\n")
    # 1. duplicates
    print("## 1. Duplicate mod ids")
    dups = {k: v for k, v in providers.items() if len(v) > 1}
    for k, v in sorted(dups.items()):
        print(f"  {k}: " + "; ".join(f"{j} ({ver})" for j, ver in v))
    if not dups: print("  none")
    # 2. dependencies
    print("\n## 2. Dependency ranges not satisfied by the installed set")
    problems, optional_missing, unparsed = [], [], []
    for i in infos:
        for owner, lst in i["deps"].items():
            for d in lst:
                dep = d.get("modId"); rng = str(d.get("versionRange", "*")); mandatory = d.get("mandatory", True); side = d.get("side", "BOTH")
                if side == "CLIENT" and dep not in installed: optional_missing.append(f"{dep} (client-side, for {owner})"); continue
                if dep in ("forge", "minecraft"): have = installed[dep]
                else: have = installed.get(dep)
                if have is None:
                    if mandatory: problems.append(f"  {i['jar']} [{owner}] needs {dep} {rng}: NOT INSTALLED")
                    else: optional_missing.append(f"{dep} (for {owner})")
                    continue
                ok = in_range(have, rng)
                if ok is None: unparsed.append(f"  {i['jar']} [{owner}] {dep} range '{rng}' (installed {have})")
                elif not ok: problems.append(f"  {i['jar']} [{owner}] needs {dep} {rng}, installed {have}{'' if mandatory else '  (optional)'}")
    print(*(problems or ["  none - every mandatory and optional dependency present is inside its declared range"]), sep="\n")
    if unparsed: print("  unparsed ranges:", *unparsed, sep="\n  ")
    print(f"  optional dependencies not installed ({len(set(optional_missing))}): " + ", ".join(sorted(set(optional_missing))[:60]))
    # 3. mixin hotspots
    print("\n## 3. Mixin targets (classes patched by several mods)")
    by_target = collections.defaultdict(set)
    for i in infos:
        for cfg, grp, cls in i["mixin_targets"]:
            # the mixin class name usually mirrors the target: strip common suffixes
            key = re.sub(r"(Mixin|_Mixin|Mixins|Accessor|Invoker|Transformer)$", "", cls.rsplit(".", 1)[-1])
            by_target[key].add(i["jar"].split(" ::")[0])
    hot = sorted(((k, v) for k, v in by_target.items() if len(v) >= 3), key=lambda kv: -len(kv[1]))
    for k, v in hot[:40]: print(f"  {k}: {len(v)} mods - " + ", ".join(sorted(v)))
    mixin_mods = sum(1 for i in infos if i["mixins"] and "::" not in i["jar"])
    print(f"  ({mixin_mods} jars carry mixins; {len(by_target)} distinct mixin class names; {len(hot)} names shared by 3+ mods)")
    # 4. Forge / MC ranges
    print("\n## 4. Loader ranges")
    bad = []
    for i in infos:
        for owner, lst in i["deps"].items():
            for d in lst:
                if d.get("modId") in ("forge", "minecraft"):
                    ok = in_range(installed[d["modId"]], str(d.get("versionRange", "*")))
                    if ok is False: bad.append(f"  {i['jar']} [{owner}] {d['modId']} {d.get('versionRange')} vs {installed[d['modId']]}")
    print(*(bad or [f"  every declared forge/minecraft range accepts Forge {FORGE} / Minecraft {MC}"]), sep="\n")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump({"installed": installed, "providers": providers, "problems": problems, "unparsed": unparsed, "hot": [(k, sorted(v)) for k, v in hot],
                   "infos": [{k: v for k, v in i.items() if k != "mixin_targets"} for i in infos]}, open(out, "w"), indent=1, default=list)
        print("->", out)


if __name__ == "__main__":
    main()
