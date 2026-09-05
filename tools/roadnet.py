"""Extract the road and rail network of the Pripyat cell from the surface class raster as a skeleton graph.

usage: roadnet.py <census dir> <out dir> [--cell 2]
Reads classes.npy (1 road, 2 rail). Closes small gaps, thins the road mask to one-block centre lines (Zhang-Suen),
finds junctions (3+ neighbours) and dead ends (1 neighbour), and writes:
  roadnet.json   {"nodes": [[x, z, degree], ...], "edges": [[node_a, node_b, length_blocks, [[x, z], ...]], ...]}
  roadnet.png    skeleton over the class raster (1 px = 3 blocks), junctions marked
Coordinates are world blocks (cell origin x -3900 z -3900). Rail is skeletonised separately and tagged "rail".
Dead ends at the cell border are the map's exits; dead ends elsewhere are stubs a placed sector can hook onto.
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

X0, Z0 = -3900, -3900


def thin(img):
    """Zhang-Suen thinning on a boolean image (vectorised)."""
    img = img.copy().astype(np.uint8)
    def neighbours(a):
        p2 = np.roll(a, 1, 0); p4 = np.roll(a, -1, 1); p6 = np.roll(a, -1, 0); p8 = np.roll(a, 1, 1)
        p3 = np.roll(p2, -1, 1); p5 = np.roll(p6, -1, 1); p7 = np.roll(p6, 1, 1); p9 = np.roll(p2, 1, 1)
        return p2, p3, p4, p5, p6, p7, p8, p9
    while True:
        changed = False
        for step in (0, 1):
            p2, p3, p4, p5, p6, p7, p8, p9 = neighbours(img)
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8) for i in range(8))
            if step == 0: c = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else: c = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            m = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if m.any(): img[m] = 0; changed = True
        if not changed: break
    return img.astype(bool)


def graph(skel, cell):
    ys, xs = np.nonzero(skel)
    pts = set(zip(xs.tolist(), ys.tolist()))
    def nb(p):
        x, y = p; return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (x + dx, y + dy) in pts]
    deg = {p: len(nb(p)) for p in pts}
    nodes = [p for p, d in deg.items() if d != 2]
    node_id = {p: i for i, p in enumerate(nodes)}
    edges = []; seen = set()
    for p in nodes:
        for q in nb(p):
            if (p, q) in seen: continue
            path = [p, q]; prev, cur = p, q
            while cur not in node_id:
                nxt = [r for r in nb(cur) if r != prev]
                if not nxt: break
                prev, cur = cur, nxt[0]; path.append(cur)
            seen.add((p, q)); seen.add((cur, prev))
            if cur in node_id:
                length = sum(np.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) for i in range(1, len(path))) * cell
                simp = path[::max(1, len(path) // 12)] + [path[-1]]
                edges.append([node_id[p], node_id[cur], round(length), [[int(x * cell + X0), int(y * cell + Z0)] for x, y in simp]])
    return [[int(x * cell + X0), int(y * cell + Z0), deg[(x, y)]] for x, y in nodes], edges


def main(a):
    cdir, out = Path(a[1]), Path(a[2]); out.mkdir(parents=True, exist_ok=True)
    cell = int(a[a.index("--cell") + 1]) if "--cell" in a else 2
    cls = np.load(cdir / "classes.npy"); H, W = cls.shape
    result = {"cell": cell, "origin": [X0, Z0], "networks": {}}
    canvas = Image.fromarray(np.where(cls == 0, 40, np.where(cls == 3, 90, 70)).astype(np.uint8)).convert("RGB").resize((W // 3, H // 3), Image.BOX)
    d = ImageDraw.Draw(canvas)
    for name, code, col in (("road", 1, (255, 230, 80)), ("rail", 2, (255, 120, 40))):
        m = cls == code
        m = ndimage.zoom(m.astype(np.float32), 1 / cell, order=1) > 0.25
        m = ndimage.binary_closing(m, iterations=2); m = ndimage.binary_opening(m, iterations=1)
        lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= (200 if code == 1 else 40) / (cell * cell)])
        skel = thin(keep)
        nodes, edges = graph(skel, cell)
        result["networks"][name] = {"nodes": nodes, "edges": edges, "length_km": round(sum(e[2] for e in edges) / 1000, 2)}
        ys, xs = np.nonzero(skel)
        for x, y in zip(xs, ys): d.point((x * cell / 3, y * cell / 3), fill=col)
        for x, z, deg in nodes:
            c = (255, 60, 60) if deg >= 3 else (80, 200, 255)
            px, py = (x - X0) / 3, (z - Z0) / 3; d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=c)
        print(f"{name}: {len(nodes)} nodes ({sum(1 for n in nodes if n[2] >= 3)} junctions, {sum(1 for n in nodes if n[2] == 1)} dead ends), {len(edges)} edges, {result['networks'][name]['length_km']} km")
    json.dump(result, open(out / "roadnet.json", "w"))
    d.rectangle([0, 0, canvas.width, 16], fill=(0, 0, 0)); d.text((6, 3), "road (yellow) and rail (orange) centre lines; red = junction, blue = dead end / stub", fill=(255, 255, 255))
    canvas.save(out / "roadnet.png"); print("->", out)


if __name__ == "__main__":
    main(sys.argv)
