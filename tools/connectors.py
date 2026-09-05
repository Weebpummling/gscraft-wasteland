"""Plan the connector roads for v8 step 7/8: from each build's own stubs (stubs_v8.json) - or, for a build without any,
a fallback gate on the footprint edge facing the nearest existing road - to the nearest point of the existing network
(road class in classes.npy, outside every footprint). Writes roads_v8.json in roads.py format; run
`roads.py route` on it and `roads.py build --style skadowsky|track` afterwards. Nothing is written to the world here.

usage: connectors.py <census dir> <sectors_v8.json> <stubs_v8.json> <out roads.json>
Rules: at most two gates per build (the widest stub per side, sides facing the network first); farmsteads and the small
builds (library, hempcrete compound, runway) get tracks (width 5); sectors get the Skadowsky carriageway (width 9);
a gate whose nearest road is under 40 blocks away needs no connector (the build already touches the network).
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage

X0, Z0 = -3900, -3900
TRACK = {"lib", "hemp", "runway"}


def main(a):
    if len(a) < 5: sys.exit(__doc__)
    cdir, out = Path(a[1]), Path(a[4])
    sectors = json.load(open(a[2]))["sectors"]; stubs = json.load(open(a[3]))
    cls = np.load(cdir / "classes.npy"); H, W = cls.shape
    road = (cls == 1) | (cls == 2)
    inside = np.zeros_like(road)
    for p in sectors:
        x0, z0, x1, z1 = p["x0"] - X0, p["z0"] - Z0, p["x1"] - X0, p["z1"] - Z0
        inside[max(z0, 0):z1 + 1, max(x0, 0):x1 + 1] = True
    net = road & ~inside
    lab, n = ndimage.label(net); sizes = ndimage.sum(net, lab, range(1, n + 1))
    net &= np.isin(lab, np.nonzero(sizes >= 3000)[0] + 1)          # the network proper: fragments (a 40-px farm track) are not a target
    # distance to the network and the index of the nearest network pixel, on a 4-block grid
    net4 = ndimage.zoom(net.astype(np.float32), 0.25, order=1) > 0.15
    dist4, idx4 = ndimage.distance_transform_edt(~net4, return_indices=True)
    def nearest(x, z):
        i, j = min(max(int((z - Z0) / 4), 0), net4.shape[0] - 1), min(max(int((x - X0) / 4), 0), net4.shape[1] - 1)
        d = dist4[i, j] * 4; ti, tj = idx4[0, i, j], idx4[1, i, j]
        return d, (int(tj * 4 + X0), int(ti * 4 + Z0))
    roads = []
    for p in sectors:
        if p["id"] == "camp": continue
        if p.get("group") == "removed": continue
        s = stubs.get(p["id"], {}).get("stubs", [])
        gates = []
        best_per_side = {}
        for q in s:
            if q["side"] not in best_per_side or q["width"] > best_per_side[q["side"]]["width"]: best_per_side[q["side"]] = q
        for q in best_per_side.values():
            # step the gate 6 blocks outside the footprint so the connector starts clear of the build
            dx, dz = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}[q["side"]]
            gates.append(((q["x"] + dx * 6, q["z"] + dz * 6), q["side"], q["width"], q["material"]))
        if not gates:
            cx, cz = (p["x0"] + p["x1"]) / 2, (p["z0"] + p["z1"]) / 2
            cands = [((cx, p["z0"] - 6), "N"), ((cx, p["z1"] + 6), "S"), ((p["x0"] - 6, cz), "W"), ((p["x1"] + 6, cz), "E")]
            cands.sort(key=lambda c: nearest(*c[0])[0])
            gates = [((int(cands[0][0][0]), int(cands[0][0][1])), cands[0][1], 0, "fallback")]
        gates.sort(key=lambda g: nearest(*g[0])[0])
        for k, (g, side, width, mat) in enumerate(gates[:2]):
            d, t = nearest(*g)
            if d < 40: continue
            style = "track" if (p["id"] in TRACK or p["id"].startswith("old")) else "skadowsky"
            roads.append({"name": f"{p['id']}_{side}", "points": [list(g), list(t)], "width": 5 if style == "track" else 9, "style": style,
                          "note": f"{p['name']} {side} gate ({mat}, stub width {width}) -> nearest existing road, {round(d)} m"})
    json.dump(roads, open(out, "w"), indent=1)
    print(f"{len(roads)} connectors planned ->", out)
    for r in roads: print(f"  {r['name']:12s} {r['points'][0]} -> {r['points'][1]}  {r['style']}  {r['note'].split('->')[-1].strip()}")


if __name__ == "__main__":
    main(sys.argv)
