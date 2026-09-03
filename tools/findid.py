import sys
from pathlib import Path
from transplant import R, read_region_raw, T_COMPOUND, T_LIST
needle = sys.argv[2].encode()
def walk(t, v, path, out):
    if t == T_COMPOUND:
        for k, (et, val) in v.items(): walk(et, val, path + [k], out)
    elif t == T_LIST:
        et, items = v
        for i, it in enumerate(items): walk(et, it, path + [f"[{i}]"], out)
    elif isinstance(v, str) and needle.decode() in v:
        out.append("/".join(path) + " = " + v)
hits = {}
for f in sorted(Path(sys.argv[1]).glob("*.mca")):
    for slot, (ts, comp, raw) in read_region_raw(f).items():
        if needle not in raw: continue
        name, root = R(raw).root()
        out = []; walk(T_COMPOUND, root, [], out)
        for o in out:
            key = o.split(" = ")[0]
            import re; key = re.sub(r"\[\d+\]", "[n]", key)
            hits.setdefault(key, []).append((f.name, slot, o.split(" = ")[1]))
for k, v in hits.items():
    print(f"{len(v):4d}  {k}   e.g. {v[0]}")
