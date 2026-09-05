"""Step 4 of the v8 plan: place the sectors on the Pripyat cell for a balanced map.

usage: place_sectors.py <census dir> <heightplan dir> <out dir> [--seed N]
Inputs: classes.npy (surface classes), height.npy (the authored relief), roadnet/roadnet.json (optional, for stubs).
Each sector has a real footprint (from the source build) and a target ring - distance from the camp centre - taken from
the design's ranges compressed to the 5 km map: near 400-1100 m, mid 1100-2200 m, far 2200-3600 m.
A position is valid when the footprint plus a 24-block margin holds no fixed column (road, rail, water, building), lies
inside the border, and overlaps no other sector. Score = ring miss + 3 x distance to the nearest road (capped) + terrain
roughness inside the footprint + a tie-breaker that spreads sectors around the compass. The camp is fixed on the plateau.
Writes sectors_v8.json and sectors_v8.png (over the height preview).
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

X0, Z0, X1, Z1 = -3900, -3900, 1200, 700
CAMP = ((-1750, -2380), 384, 384)           # centre, w, h  (the plateau basin is its crater lake)
SECTORS = [  # id, name, w, h, ring (m from camp), source
    ("skad", "Skadowsky sector", 464, 752, (1100, 2000), "incoming/skadowsky 1.2 x -480..-17 z -1232..-481"),
    ("hub", "Novo Expograd hub (desert city)", 832, 640, (2400, 3600), "scratch/upgrade/world hub (1.12), ships cut"),
    ("mega", "Mega-base", 384, 528, (2200, 3400), "live world x 2192..2575 z 400..927"),
    ("indu", "Industrial district", 464, 272, (1500, 2600), "live world x 1904..2367 z 864..1135"),
    ("runway", "Runway (pad)", 512, 192, (2000, 3400), "built pad"),
    ("hemp", "Hempcrete compound", 320, 320, (1200, 2200), "live world x 1568..1887 z 1152..1471"),
    ("settle", "Settlement", 272, 288, (1400, 2600), "scratch/upgrade/world east site (1.12)"),
    ("old", "29 old sites cluster", 336, 384, (900, 2000), "live world, 29 rects"),
    ("plaza", "Financial Plaza + sewers", 160, 144, (500, 1200), "scratch/upgrade/financial_plaza + sewers (1.12)"),
    ("novo", "Novo Expograd Industrial Zone", 144, 160, (700, 1500), "scratch/upgrade/novo_industrial (1.12)"),
    ("biogen", "Bio Gen offices", 64, 256, (600, 1400), "scratch/upgrade/biogen_strip (1.12)"),
    ("lib", "Library", 96, 96, (400, 1100), "live world x 2032..2127 z 1392..1487"),
]
MARGIN = 16


def main(a):
    cdir, hdir, out = Path(a[1]), Path(a[2]), Path(a[3]); out.mkdir(parents=True, exist_ok=True)
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 1
    cls = np.load(cdir / "classes.npy"); hgt = np.load(hdir / "height.npy").astype(np.float32)
    H, W = cls.shape
    fixed = np.isin(cls, (1, 2, 3, 4)).astype(np.uint8)          # small sheds and field tracks may be overwritten (see below)
    hard = np.isin(cls, (2, 3)).astype(np.uint8)                   # rail and water never
    road = (cls == 1) | (cls == 2)
    # integral image of fixed columns for O(1) footprint tests
    I = np.zeros((H + 1, W + 1), np.int64); I[1:, 1:] = fixed.cumsum(0).cumsum(1)
    J = np.zeros((H + 1, W + 1), np.int64); J[1:, 1:] = hard.cumsum(0).cumsum(1)
    def count(M, x0, z0, x1, z1):
        x0, z0 = max(x0 - X0, 0), max(z0 - Z0, 0); x1, z1 = min(x1 - X0 + 1, W), min(z1 - Z0 + 1, H)
        if x1 <= x0 or z1 <= z0: return 10 ** 9
        return int(M[z1, x1] - M[z0, x1] - M[z1, x0] + M[z0, x0])
    def blocked(x0, z0, x1, z1):
        area = (x1 - x0 + 1) * (z1 - z0 + 1)
        return count(J, x0, z0, x1, z1) > 0 or count(I, x0, z0, x1, z1) > 0.02 * area   # <= 2 % small structures allowed
    # distance to the nearest road, on a 8-block grid
    road8 = ndimage.zoom(road.astype(np.float32), 1 / 8, order=1) > 0.1
    droad8 = ndimage.distance_transform_edt(~road8) * 8
    hgt8 = ndimage.zoom(hgt, 1 / 8, order=1)
    def road_dist(cx, cz): return float(droad8[min(int((cz - Z0) / 8), droad8.shape[0] - 1), min(int((cx - X0) / 8), droad8.shape[1] - 1)])
    def roughness(x0, z0, x1, z1):
        a = hgt8[max(0, (z0 - Z0) // 8):(z1 - Z0) // 8 + 1, max(0, (x0 - X0) // 8):(x1 - X0) // 8 + 1]
        return float(a.std()) if a.size else 99
    (ccx, ccz), cw, ch = CAMP
    placed = [{"id": "camp", "name": "Camp", "x0": ccx - cw // 2, "z0": ccz - ch // 2, "x1": ccx + cw // 2 - 1, "z1": ccz + ch // 2 - 1, "ring": [0, 0], "source": "camp on the plateau; crater lake = the basin"}]
    rng = np.random.default_rng(seed)
    used_angles = []
    for sid, name, w, h, (r0, r1), src in SECTORS:
        best = None
        for _ in range(6000):
            ang = rng.uniform(0, 2 * math.pi); r = rng.uniform(r0 * 0.9, r1 * 1.1)
            cx, cz = ccx + r * math.cos(ang), ccz + r * math.sin(ang)
            x0, z0 = int(cx - w / 2) // 16 * 16, int(cz - h / 2) // 16 * 16; x1, z1 = x0 + w - 1, z0 + h - 1
            if x0 - MARGIN < X0 + 64 or z0 - MARGIN < Z0 + 64 or x1 + MARGIN > X1 - 64 or z1 + MARGIN > Z1 - 64: continue
            if blocked(x0 - MARGIN, z0 - MARGIN, x1 + MARGIN, z1 + MARGIN): continue
            if any(not (x1 + 48 < p["x0"] or x0 - 48 > p["x1"] or z1 + 48 < p["z0"] or z0 - 48 > p["z1"]) for p in placed): continue
            d = math.hypot(cx - ccx, cz - ccz)
            miss = 0 if r0 <= d <= r1 else min(abs(d - r0), abs(d - r1))
            rd = road_dist(cx, cz)
            spread = min([abs(((ang - u + math.pi) % (2 * math.pi)) - math.pi) for u in used_angles] or [math.pi])
            score = miss + 3 * min(rd, 400) + 40 * roughness(x0, z0, x1, z1) + 200 * max(0, 0.5 - spread)
            if best is None or score < best[0]: best = (score, x0, z0, x1, z1, d, rd, ang)
        if best is None: print(f"  {name}: NO POSITION"); continue
        _, x0, z0, x1, z1, d, rd, ang = best; used_angles.append(ang)
        placed.append({"id": sid, "name": name, "x0": x0, "z0": z0, "x1": x1, "z1": z1, "ring": [r0, r1], "dist_m": round(d), "road_m": round(rd), "source": src})
        print(f"  {name:34s} at x {x0}..{x1} z {z0}..{z1}  {round(d)} m from camp (ring {r0}-{r1}), road {round(rd)} m")
    json.dump({"border": [X0, Z0, X1, Z1], "sectors": placed, "zones": {"woods": [-3400, -1350, -1600, 100], "ridge": [-3900, -2600, -3450, 700]}}, open(out / "sectors_v8.json", "w"), indent=1)
    # render over the height preview
    prev = Image.open(hdir / "height_preview.png").convert("RGB"); k = prev.width / W
    d = ImageDraw.Draw(prev)
    for p in placed:
        col = (255, 230, 80) if p["id"] == "camp" else (255, 140, 60) if p["id"] == "skad" else (120, 220, 255)
        box = [(p["x0"] - X0) * k, (p["z0"] - Z0) * k, (p["x1"] - X0) * k, (p["z1"] - Z0) * k]
        d.rectangle(box, outline=col, width=3); d.rectangle([box[0], box[1] - 12, box[0] + len(p["name"]) * 6 + 4, box[1]], fill=(0, 0, 0)); d.text((box[0] + 2, box[1] - 11), p["name"], fill=col)
    d.ellipse([(ccx - X0) * k - 4, (ccz - Z0) * k - 4, (ccx - X0) * k + 4, (ccz - Z0) * k + 4], fill=(255, 230, 80))
    for r in (1100, 2200, 3600): d.ellipse([(ccx - r - X0) * k, (ccz - r - Z0) * k, (ccx + r - X0) * k, (ccz + r - Z0) * k], outline=(255, 255, 255), width=1)
    prev.save(out / "sectors_v8.png"); print("->", out)


if __name__ == "__main__":
    main(sys.argv)
