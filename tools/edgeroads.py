"""Connect every remaining road stub at a footprint edge (edgeaudit.py, kind road, 3..30 wide) to the road network: the
census roads (components of 3000+ pixels) plus the connectors already built (routes_v8_*.json polylines, the bridge stubs).
Writes a roads.py job list; stubs already within `touch` blocks of the network, stubs wider than 30 (a paved block edge) and
stubs of removed sectors are skipped; stubs closer than 24 blocks to each other on the same edge are merged.

usage: edgeroads.py <edge_features.json> <sectors_v8.json> <routes.json,...> <out roads.json> [--max 500] [--touch 40]
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage

CENSUS = Path(r"G:/GSCraft/incoming/census"); X0, Z0 = -3900, -3900
DIRS = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}


def main(a):
    if len(a) < 5: sys.exit(__doc__)
    feats = json.load(open(a[1])); sectors = {p["id"]: p for p in json.load(open(a[2]))["sectors"]}
    mx = int(a[a.index("--max") + 1]) if "--max" in a else 500; touch = int(a[a.index("--touch") + 1]) if "--touch" in a else 40
    cls = np.load(CENSUS / "classes.npy"); H, W = cls.shape
    road = (cls == 1) | (cls == 2)
    lab, n = ndimage.label(road); sizes = ndimage.sum(road, lab, range(1, n + 1)); net = np.isin(lab, np.nonzero(sizes >= 3000)[0] + 1)
    for f in a[3].split(","):
        for r in json.load(open(f)):
            for (x, z) in r.get("polyline", []):
                i, j = z - Z0, x - X0
                if 0 <= i < H and 0 <= j < W: net[max(i - 2, 0):i + 3, max(j - 2, 0):j + 3] = True
    for p in sectors.values():                                                   # a footprint's own roads are not the network
        net[max(p["z0"] - Z0, 0):p["z1"] - Z0 + 1, max(p["x0"] - X0, 0):p["x1"] - X0 + 1] = False
    net4 = ndimage.zoom(net.astype(np.float32), 0.25, order=1) > 0.15
    dist4, idx4 = ndimage.distance_transform_edt(~net4, return_indices=True)
    def nearest(x, z):
        i, j = min(max(int((z - Z0) / 4), 0), net4.shape[0] - 1), min(max(int((x - X0) / 4), 0), net4.shape[1] - 1)
        return dist4[i, j] * 4, (int(idx4[1, i, j] * 4 + X0), int(idx4[0, i, j] * 4 + Z0))
    stubs = [f for f in feats if f["kind"] == "road" and 3 <= f["width"] <= 30 and sectors[f["sector"]].get("group") != "removed"]
    stubs.sort(key=lambda f: (f["sector"], f["side"], f["from"]))
    merged = []
    for f in stubs:
        mxp, mzp = (f["from"][0] + f["to"][0]) // 2, (f["from"][1] + f["to"][1]) // 2
        if merged and merged[-1]["sector"] == f["sector"] and merged[-1]["side"] == f["side"] and math.hypot(mxp - merged[-1]["x"], mzp - merged[-1]["z"]) < 80:
            if f["width"] > merged[-1]["width"]: merged[-1].update(x=mxp, z=mzp, width=f["width"])       # one gate per 80 m of edge: the widest stub
            continue
        merged.append({"sector": f["sector"], "side": f["side"], "x": mxp, "z": mzp, "width": f["width"]})
    jobs, skipped = [], []
    sys.path.insert(0, str(Path(__file__).resolve().parent)); from terrain import World, LIQUID
    world = World(Path(a[a.index("--world") + 1])) if "--world" in a else None
    for k, s in enumerate(merged):
        dx, dz = DIRS[s["side"]]; gate = (s["x"] + dx * 6, s["z"] + dz * 6)
        if world is not None and (world.top(*gate)[1] in LIQUID or world.top(s["x"] + dx * 2, s["z"] + dz * 2)[1] in LIQUID):
            skipped.append((s["sector"], s["side"], "quay", 0)); continue                  # the road ends at water: a quay, not a stub
        d, t = nearest(*gate)
        if d < touch: skipped.append((s["sector"], s["side"], "touches", int(d))); continue
        if d > mx: skipped.append((s["sector"], s["side"], "far", int(d))); continue
        style = "skadowsky" if s["width"] >= 7 and not s["sector"].startswith("old") else "track"
        jobs.append({"name": f"{s['sector']}_{s['side']}{k}", "points": [list(gate), list(t)], "width": 9 if style == "skadowsky" else 5, "style": style,
                     "note": f"{sectors[s['sector']]['name']} {s['side']} stub (width {s['width']}) -> network, {int(d)} m"})
    # at most three stub connectors per sector (the widest), so a small build does not sprout a fan of tracks
    per = {}
    for j in sorted(jobs, key=lambda j: -int(j["note"].split("width ")[1].split(")")[0])):
        sid = j["name"].rsplit("_", 1)[0]; per.setdefault(sid, []).append(j)
    jobs = [j for lst in per.values() for j in lst[:3]]
    json.dump(jobs, open(a[4], "w"), indent=1)
    print(f"{len(stubs)} road stubs -> {len(merged)} gates -> {len(jobs)} connectors ({sum(1 for x in skipped if x[2]=='touches')} touch the network already, {sum(1 for x in skipped if x[2]=='quay')} end at water (quays), {sum(1 for x in skipped if x[2]=='far')} farther than {mx} m)")
    for j in jobs: print(f"  {j['name']:14s} {j['points'][0]} -> {j['points'][1]} {j['style']:9s} {j['note'].split('->')[-1].strip()}")
    for s in skipped:
        if s[2] == "far": print("  far:", s)


if __name__ == "__main__":
    main(sys.argv)
