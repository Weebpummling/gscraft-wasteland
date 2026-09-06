import json
from pathlib import Path
import numpy as np
from scipy import ndimage
PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900; S = 4
net = np.load("roadnet.npz")["net"]
big = ndimage.binary_closing(net, np.ones((9,9)))
lab, n = ndimage.label(big, np.ones((3,3))); sizes = ndimage.sum(big, lab, range(1, n+1))
ids = [int(k) for k in np.argsort(sizes)[::-1] + 1 if sizes[k-1] >= 3000]
name = {cid: f"C{k+1}" for k, cid in enumerate(ids)}
corr = np.where(np.isin(lab, ids), lab, 0)
c4 = corr[::S, ::S]                       # 4-block grid
np.save("corr.npy", corr)
res = {}
for a in ids:
    ma = c4 == a
    dist, idx = ndimage.distance_transform_edt(~ma, return_indices=True)
    for b in ids:
        if a == b: continue
        mb = c4 == b
        sub = np.where(mb, dist, np.inf)
        i, j = np.unravel_index(np.argmin(sub), sub.shape)
        res[(a, b)] = (float(sub[i, j]) * S, (int(j*S+X0), int(i*S+Z0)), (int(idx[1,i,j])*S+X0, int(idx[0,i,j])*S+Z0))
json.dump({f"{name[a]}|{name[b]}": v for (a, b), v in res.items()}, open("gaps.json","w"))
print("--- gaps under 900 m between the 8 largest corridors")
top = ids[:8]
for a in range(len(top)):
    for b in range(a+1, len(top)):
        g, pb, pa = res[(top[a], top[b])]
        if g < 900: print(f"  {name[top[a]]:>3s} <-> {name[top[b]]:<3s} gap {g:6.0f} m   between {pa} and {pb}")
print("\n--- each corridor's nearest neighbour")
for a in ids:
    g, pb, pa = min(((res[(b,a)][0], res[(b,a)][1], res[(b,a)][2]), b) for b in ids if b != a)[0], None, None
    best = min(((res[(b,a)], b) for b in ids if b != a), key=lambda t: t[0][0])
    (g, pa2, pb2), b = best
    ys, xs = np.nonzero(corr == a)
    print(f"  {name[a]:>3s} {int(sizes[a-1]):8d} px  x {xs.min()+X0:6d}..{xs.max()+X0:6d} z {ys.min()+Z0:6d}..{ys.max()+Z0:6d}  nearest {name[b]:>3s} at {g:5.0f} m")
