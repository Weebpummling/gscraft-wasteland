"""Edge audit (v8): every linear feature that runs off a transplanted footprint's edge and therefore needs a continuation
or a designed ending - water bodies, elevated structures (bridges, viaducts, pipes), rails, roads. stubs.py covers roads
and rails; this adds water and elevated features and writes one list for all sectors.

usage: edgeaudit.py <world dir> <sectors_v8.json> <out json> [--only id,id]
For each footprint the outer 2-block ring is scanned. Column kinds: water (surface is liquid), elevated (a non-natural block
4+ above the ground with air under it - a deck), rail, road (stubs.py's road materials). Runs of the same kind along an edge
become one feature {sector, side, kind, from, to, width, y}. Features under 3 blocks wide are dropped.
"""
import sys, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, NATURAL, PLANT, LIQUID, AIR
from stubs import is_road, RAIL


def kind_of(w, x, z):
    y, b = w.top(x, z)
    if b is None: return None, None
    if b in LIQUID: return "water", y
    if b in RAIL: return "rail", y
    g = w.ground(x, z)
    if g is not None and y - g >= 4:
        # a deck: non-natural block with air somewhere between it and the ground
        for yy in range(g + 1, y):
            if w.get(x, yy, z) in AIR:
                n = w.get(x, y, z)
                if n not in NATURAL and n not in PLANT and not n.endswith(("_leaves", "_log", "_wood")) and "vine" not in n: return "elevated", y
                break
    if is_road(b) or (y is not None and is_road(w.get(x, y - 1, z))): return "road", y
    return None, None


def audit(w, p):
    x0, z0, x1, z1 = p["x0"], p["z0"], p["x1"], p["z1"]
    out = []
    for side, cols in (("N", [(x, z0) for x in range(x0, x1 + 1)]), ("S", [(x, z1) for x in range(x0, x1 + 1)]),
                       ("W", [(x0, z) for z in range(z0, z1 + 1)]), ("E", [(x1, z) for z in range(z0, z1 + 1)])):
        run = None
        for c in cols + [None]:
            k, y = kind_of(w, *c) if c is not None else (None, None)
            x, z = c if c is not None else (None, None)
            if run and (k != run["kind"]):
                if run["width"] >= 3: out.append(run)
                run = None
            if k and not run: run = {"sector": p["id"], "side": side, "kind": k, "from": [x, z], "to": [x, z], "width": 1, "y": y}
            elif k: run["to"] = [x, z]; run["width"] += 1
    return out


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    w = World(Path(a[1])); sectors = json.load(open(a[2]))["sectors"]
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    feats = []
    for p in sectors:
        if only and p["id"] not in only: continue
        if p["id"] == "camp": continue
        f = audit(w, p); feats += f
        if f: print(f"{p['name']:34s} " + ", ".join(f"{q['side']} {q['kind']} w{q['width']} @{q['from']}" for q in f))
    json.dump(feats, open(a[3], "w"), indent=1)
    import collections
    print(f"\n{len(feats)} edge features -> {a[3]}; by kind:", dict(collections.Counter(q['kind'] for q in feats)))


if __name__ == "__main__":
    main(sys.argv)
