"""Travel cost between the destinations over the current network: road cells cheap, open land 3x, water impassable."""
import json, heapq
from pathlib import Path
import numpy as np
from scipy import ndimage
CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900; S = 4
d = np.load(CEN / "v8_cell_pass7_inspect.npz", allow_pickle=True)
gy = d["gy"].astype(np.float32); wt = d["wtop"].astype(np.int32); water = wt > -999
net = np.load("roadnet.npz")["net"]
H, W = gy.shape
net4 = ndimage.maximum_filter(net, S)[::S, ::S]
wat4 = ndimage.median_filter(water.astype(np.uint8), S)[::S, ::S] > 0
g4 = gy[::S, ::S]
slope = np.maximum(np.abs(np.gradient(g4, axis=0)), np.abs(np.gradient(g4, axis=1)))
cost = np.where(net4, 1.0, 3.0 + np.clip(slope - 1, 0, 12) * 1.5)
cost[wat4 & ~net4] = np.inf
h4, w4 = cost.shape
def cell(x, z): return ((z - Z0)//S, (x - X0)//S)
def dijkstra(src):
    D = np.full(cost.shape, np.inf); D[src] = 0; q = [(0.0, src)]
    while q:
        c, (i, j) = heapq.heappop(q)
        if c > D[i, j]: continue
        for di, dj, w in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)):
            a, b = i+di, j+dj
            if not (0 <= a < h4 and 0 <= b < w4): continue
            nc = c + w * cost[a, b]
            if nc < D[a, b]: D[a, b] = nc; heapq.heappush(q, (nc, (a, b)))
    return D
sec = {p["id"]: p for p in json.load(open(PLAN/"sectors_v8.json"))["sectors"]}
KEY = ["skad","hub","mega","indu","hemp","lib","runway","plaza","novo","biogen","camp"]
def centre(i): p = sec[i]; return ((p["x0"]+p["x1"])//2, (p["z0"]+p["z1"])//2)
D = dijkstra(cell(*centre("skad")))
print("travel cost from Skadowsky (1 = one 4 m step on road, 3+ = off road; inf = no land route)\n")
print(f"  {'to':10s} {'straight':>9s} {'cost':>9s} {'cost/dist':>10s}  reading")
for k in KEY:
    if k == "skad": continue
    cx, cz = centre(k); i, j = cell(cx, cz)
    sub = D[max(i-8,0):i+9, max(j-8,0):j+9]; c = np.nanmin(sub)
    sx, sz = centre("skad"); dist = ((cx-sx)**2 + (cz-sz)**2) ** 0.5
    ratio = c*S/dist if np.isfinite(c) else float("inf")
    read = "on road most of the way" if ratio < 1.35 else ("part road" if ratio < 2.0 else "mostly cross-country")
    print(f"  {k:10s} {dist:8.0f} m {c*S:8.0f} {ratio:10.2f}  {read}")
