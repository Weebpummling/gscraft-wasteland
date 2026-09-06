"""Road-network review: corridors, which destinations they serve, gaps between corridors."""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage

CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8")
X0, Z0 = -3900, -3900
z = np.load("roadnet.npz"); net = z["net"]; H, W = net.shape
d = np.load(CEN / "v8_cell_pass7_inspect.npz", allow_pickle=True)
gy = d["gy"].astype(np.int32); wt = d["wtop"].astype(np.int32)
water = wt > -999

# corridors: bridge gaps up to 8 blocks, drop noise under 2000 px
big = ndimage.binary_closing(net, np.ones((9,9)))
lab, n = ndimage.label(big, np.ones((3,3)))
sizes = ndimage.sum(big, lab, range(1, n+1))
keep = np.nonzero(sizes >= 3000)[0] + 1
corr = np.where(np.isin(lab, keep), lab, 0)
ids = sorted(keep, key=lambda k: -sizes[k-1])
print(f"{len(ids)} corridors (>=3000 px after 8-block closing); {net.sum():,} road px total")

sec = json.load(open(PLAN / "sectors_v8.json"))["sectors"]
label_of = {}
for k, cid in enumerate(ids): label_of[cid] = k+1
def corridor_at(x, z_, r=40):
    i, j = z_ - Z0, x - X0
    sub = corr[max(i-r,0):i+r, max(j-r,0):j+r]
    v = sub[sub > 0]
    if v.size == 0: return None
    return label_of.get(int(np.bincount(v).argmax()))

print("\n--- corridor sizes")
for k, cid in enumerate(ids):
    m = corr == cid; ys, xs = np.nonzero(m)
    print(f"  C{k+1:<2d} {int(sizes[cid-1]):8d} px  x {xs.min()+X0:6d}..{xs.max()+X0:6d}  z {ys.min()+Z0:6d}..{ys.max()+Z0:6d}")

print("\n--- which corridor serves each destination (centre of footprint, 40-block search)")
for p in sec:
    if p.get("group") == "removed": continue
    cx, cz = (p["x0"]+p["x1"])//2, (p["z0"]+p["z1"])//2
    c = corridor_at(cx, cz, 60)
    # distance from footprint to nearest corridor px
    i0,i1,j0,j1 = p["z0"]-Z0, p["z1"]-Z0, p["x0"]-X0, p["x1"]-X0
    print(f"  {p['id']:8s} {str(p.get('group')):10s} corridor {('C'+str(c)) if c else '--':4s}  {p['name']}")
