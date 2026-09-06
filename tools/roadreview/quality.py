import json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900
d = np.load(CEN / "v8_cell_pass7_inspect.npz", allow_pickle=True)
gy = d["gy"].astype(np.int32); wt = d["wtop"].astype(np.int32); water = wt > -999
H, W = gy.shape
# the routes actually laid last for each name (lake > stubs > long > short > first)
ORDER = ["routes_v8.json","routes_v8_short.json","routes_v8_long.json","routes_v8_stubs.json","routes_v8_lake.json"]
final = {}
for f in ORDER:
    for r in json.load(open(PLAN/f)):
        if r["polyline"]: final[r["name"]] = dict(r, file=f)
print(f"{len(final)} distinct connectors laid, {sum(r['metres'] for r in final.values()):,.0f} m of new road\n")

print("--- straightness (a connector over 400 m whose path is within 8% of the straight line is a ruler line)")
for r in sorted(final.values(), key=lambda r: -r["metres"]):
    a, b = r["polyline"][0], r["polyline"][-1]; sl = math.hypot(b[0]-a[0], b[1]-a[1])
    if r["metres"] < 400: continue
    ratio = r["metres"]/sl
    # max lateral deviation from the chord
    dev = 0.0
    for (x, z) in r["polyline"]:
        num = abs((b[0]-a[0])*(a[1]-z) - (a[0]-x)*(b[1]-a[1]))
        dev = max(dev, num/max(sl,1))
    flag = "RULER" if dev < 0.04*sl else ""
    print(f"  {r['name']:14s} {r['metres']:6.0f} m  detour {ratio:4.2f}  max bend {dev:5.0f} m ({100*dev/sl:4.1f}% of chord) {flag}")

print("\n--- duplication: length of each farm track running within 48 m of another connector")
poly = {n: np.array(r["polyline"]) for n, r in final.items()}
for n, p in sorted(poly.items()):
    if final[n]["metres"] < 300: continue
    others = np.vstack([q for m, q in poly.items() if m != n])
    dup = 0
    for (x, z) in p[::2]:
        if np.min(np.abs(others[:,0]-x) + np.abs(others[:,1]-z)) <= 48: dup += 2
    L = len(p)
    print(f"  {n:14s} {final[n]['metres']:6.0f} m  {100*dup/max(L,1):5.1f}% shared corridor")

print("\n--- gradient along each connector (ground height every 8 m)")
for n, r in sorted(final.items(), key=lambda t: -t[1]["metres"]):
    if r["metres"] < 200: continue
    hs = []
    for (x, z) in r["polyline"]:
        i, j = z-Z0, x-X0
        if 0 <= i < H and 0 <= j < W and gy[i,j] > -999: hs.append(int(gy[i,j]))
    if len(hs) < 3: continue
    dh = np.abs(np.diff(hs)); climb = int(np.sum(np.diff(hs)[np.diff(hs)>0]))
    print(f"  {n:14s} {r['metres']:6.0f} m  y {min(hs):3d}..{max(hs):3d}  total climb {climb:4d}  worst step {dh.max():2d}/8m  steps>3: {(dh>3).sum()}")
