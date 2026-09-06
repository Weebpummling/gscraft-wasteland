import json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
CEN = Path(r"G:/GSCraft/incoming/census"); X0, Z0 = -3900, -3900
g = json.load(open("gaps.json"))
names = sorted({k.split("|")[0] for k in g}, key=lambda s: int(s[1:]))
idx = {n: i for i, n in enumerate(names)}; N = len(names)
M = np.full((N, N), np.inf); info = {}
for k, (d, pa, pb) in g.items():
    a, b = k.split("|"); i, j = idx[a], idx[b]
    if d < M[i, j]: M[i, j] = M[j, i] = d; info[(min(i,j), max(i,j))] = (d, pa, pb)
sizes = json.load(open("sizes.json")) if Path("sizes.json").exists() else {}
T = minimum_spanning_tree(csr_matrix(np.where(np.isinf(M), 0, M)))
edges = []
for i, j in zip(*T.nonzero()):
    d, pa, pb = info[(min(i,j), max(i,j))]
    edges.append((d, names[i], names[j], pa, pb))
edges.sort(reverse=True)
print("minimum set of links that would make the 21 corridors one network (spanning tree), longest first:\n")
tot = 0
for d, a, b, pa, pb in edges:
    tot += d
    tag = "NEW ROAD" if d >= 60 else ("patch   " if d >= 20 else "hairline")
    print(f"  {tag}  {a:>3s} - {b:<3s} {d:6.0f} m   {tuple(pa)} -> {tuple(pb)}")
print(f"\n{len(edges)} links, {tot:,.0f} m total; {sum(1 for e in edges if e[0]>=60)} need real road, {sum(1 for e in edges if 20<=e[0]<60)} are short patches, {sum(1 for e in edges if e[0]<20)} are hairline breaks")
