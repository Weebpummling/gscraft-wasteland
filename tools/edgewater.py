"""Turn the edge audit's water features (a pond or canal of the source map cut straight at the footprint edge) into river.py
jobs that give each one a natural rounded end just outside the footprint: a short channel of the feature's width at the
feature's water level, running outward from the edge for 0.6 x width, with graded banks. The kept columns of the sector
are protected, so only the landscape outside changes.

usage: edgewater.py <edge_features.json> <sectors_v8.json> <out rivers.json> [--min-width 8]
"""
import sys, json
from pathlib import Path

DIRS = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    feats = json.load(open(a[1])); sectors = {p["id"]: p for p in json.load(open(a[2]))["sectors"]}
    minw = int(a[a.index("--min-width") + 1]) if "--min-width" in a else 8
    jobs = []
    for f in feats:
        if f["kind"] != "water" or f["width"] < minw: continue
        p = sectors[f["sector"]]
        if p.get("group") == "removed" or f["sector"] == "skad": continue                # Skadowsky's water is the region's river now
        dx, dz = DIRS[f["side"]]
        mx, mz = (f["from"][0] + f["to"][0]) // 2, (f["from"][1] + f["to"][1]) // 2
        w = min(f["width"], 60); L = max(int(w * 0.6), 6)
        jobs.append({"name": f"{f['sector']}_{f['side']}_{mx}_{mz}", "points": [[mx - dx * 2, mz - dz * 2], [mx + dx * L, mz + dz * L]],
                     "width": [w, w], "levels": [[0.0, f["y"]]], "depth": 2, "meander": None, "bank_slope": [2.5, 4.0],
                     "protect": f"integrate_{f['sector']}_mask.npz", "mouth_t": 0.0,
                     "note": f"{p['name']} {f['side']} edge: {f['kind']} {f['width']} wide at y {f['y']} cut by the footprint - rounded end outside"})
    json.dump(jobs, open(a[3], "w"), indent=1)
    print(f"{len(jobs)} water edge jobs -> {a[3]}")
    for j in jobs: print(f"  {j['name']:28s} width {j['width'][0]:3d} level {j['levels'][0][1]}")


if __name__ == "__main__":
    main(sys.argv)
