"""Road-only travel: can you get there without leaving a road surface, and how far is it?"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
import heapq
CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900; S = 4
net = np.load("roadnet.npz")["net"]
net4 = ndimage.maximum_filter(net, S)[::S, ::S]
h4, w4 = net4.shape
sec = {p["id"]: p for p in json.load(open(PLAN/"sectors_v8.json"))["sectors"]}
def centre(i): p = sec[i]; return ((p["x0"]+p["x1"])//2, (p["z0"]+p["z1"])//2)
def nearest_road(x, z, r=200):
    i, j = (z-Z0)//S, (x-X0)//S
    sub = net4[max(i-r//S,0):i+r//S, max(j-r//S,0):j+r//S]
    ys, xs = np.nonzero(sub)
    if not len(ys): return None, None
    oi, oj = max(i-r//S,0), max(j-r//S,0)
    dd = (ys+oi-i)**2 + (xs+oj-j)**2; k = dd.argmin()
    return (int(ys[k]+oi), int(xs[k]+oj)), float(dd[k]**0.5)*S
def dij(src):
    D = np.full(net4.shape, np.inf); D[src] = 0; q=[(0.0, src)]
    while q:
        c,(i,j)=heapq.heappop(q)
        if c>D[i,j]: continue
        for di,dj,w in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)):
            a,b=i+di,j+dj
            if 0<=a<h4 and 0<=b<w4 and net4[a,b] and c+w<D[a,b]:
                D[a,b]=c+w; heapq.heappush(q,(c+w,(a,b)))
    return D
KEY = ["skad","hub","mega","indu","hemp","lib","runway","plaza","novo","biogen","camp","old12","old29","old19","old26","old14"]
nodes = {}
for k in KEY:
    n, d = nearest_road(*centre(k))
    nodes[k] = (n, d)
    print(f"  {k:8s} nearest road {('%.0f m'%d) if d is not None else 'none within 200 m'}")
print("\nroad-only distance between destinations (-- = no continuous road route)\n")
hdr = "          " + "".join(f"{k[:6]:>8s}" for k in KEY); print(hdr)
D = {}
for a in KEY:
    if nodes[a][0] is None: continue
    D[a] = dij(nodes[a][0])
for a in KEY:
    row = f"  {a:8s}"
    for b in KEY:
        if a==b: row += f"{'-':>8s}"; continue
        if a not in D or nodes[b][0] is None: row += f"{'?':>8s}"; continue
        v = D[a][nodes[b][0]]
        row += f"{('%.1fk'%(v*S/1000)) if np.isfinite(v) else '--':>8s}"
    print(row)
