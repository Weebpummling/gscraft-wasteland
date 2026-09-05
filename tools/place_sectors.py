"""Step 4 of the v8 plan, art pass (owner, 2026-09-04): set the builds into the existing landscape.

usage: place_sectors.py <census dir> <heightplan dir> <out dir> [--seed N]
Rules: the four Novo Expograd builds (hub, industrial zone, Financial Plaza + sewers, Bio Gen) form ONE cyberpunk
district; the player builds scatter individually; the 29 small old sites scatter as farmsteads along roads; the Woods
is a named area on the existing forest (no relief, nothing placed inside except farmsteads); nothing sits on water or
rail, on the town or the plant; every build stands 12-90 blocks from an existing road (never on it), on flat ground,
16 blocks clear of anything built and 48 clear of other placed builds. Preferences are visual: the mega-base on the
lake shore, the runway on a flat strip near the north edge, the cyberpunk district against the west ridge at the end of
the south-west road, Skadowsky against the rail embankment, the library and hempcrete compound in clearings near the
town. Writes sectors_v8.json and sectors_v8.png over the height preview.
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

X0, Z0, X1, Z1 = -3900, -3900, 1200, 700
CAMP = ((-1600, -2300), 384, 384)
WOODS = (-2450, -1350, -1600, 100)      # the forest south-east of the town; the cyberpunk district takes the ridge foot west of it
TOWN = (-3750, -3750, -1800, -1400); PLANT = (-1150, -400, 1200, 700)
MARGIN = 16


def main(a):
    cdir, hdir, out = Path(a[1]), Path(a[2]), Path(a[3]); out.mkdir(parents=True, exist_ok=True)
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 3
    cls = np.load(cdir / "classes.npy"); hgt = np.load(hdir / "height.npy").astype(np.float32); H, W = cls.shape
    fixed = np.isin(cls, (1, 2, 3, 4)).astype(np.uint8); hard = np.isin(cls, (2, 3)).astype(np.uint8)
    I = np.zeros((H + 1, W + 1), np.int64); I[1:, 1:] = fixed.cumsum(0).cumsum(1)
    J = np.zeros((H + 1, W + 1), np.int64); J[1:, 1:] = hard.cumsum(0).cumsum(1)

    def count(M, x0, z0, x1, z1):
        x0, z0 = max(x0 - X0, 0), max(z0 - Z0, 0); x1, z1 = min(x1 - X0 + 1, W), min(z1 - Z0 + 1, H)
        return 10 ** 9 if x1 <= x0 or z1 <= z0 else int(M[z1, x1] - M[z0, x1] - M[z1, x0] + M[z0, x0])

    def blocked(x0, z0, x1, z1):
        area = (x1 - x0 + 1) * (z1 - z0 + 1)
        return count(J, x0, z0, x1, z1) > 0 or count(I, x0, z0, x1, z1) > 0.02 * area

    road8 = ndimage.zoom(((cls == 1) | (cls == 2)).astype(np.float32), 1 / 8, order=1) > 0.1
    droad8 = ndimage.distance_transform_edt(~road8) * 8
    water8 = ndimage.zoom((cls == 3).astype(np.float32), 1 / 8, order=1) > 0.1
    dwater8 = ndimage.distance_transform_edt(~water8) * 8
    bare8 = ndimage.zoom((cls == 6).astype(np.float32), 1 / 8, order=1) > 0.3
    dbare8 = ndimage.distance_transform_edt(~bare8) * 8
    tree8 = ndimage.zoom((cls == 5).astype(np.float32), 1 / 8, order=1)
    hgt8 = ndimage.zoom(hgt, 1 / 8, order=1)

    def at8(A, x, z):
        return float(A[min(max(int((z - Z0) / 8), 0), A.shape[0] - 1), min(max(int((x - X0) / 8), 0), A.shape[1] - 1)])

    def rough(x0, z0, x1, z1):
        s = hgt8[max(0, (z0 - Z0) // 8):(z1 - Z0) // 8 + 1, max(0, (x0 - X0) // 8):(x1 - X0) // 8 + 1]
        return float(s.std()) if s.size else 99

    def inside(x, z, r):
        return r[0] <= x <= r[2] and r[1] <= z <= r[3]

    (ccx, ccz), cw, ch = CAMP
    placed = [{"id": "camp", "name": "Camp", "x0": ccx - cw // 2, "z0": ccz - ch // 2, "x1": ccx + cw // 2 - 1, "z1": ccz + ch // 2 - 1,
               "group": "camp", "source": "camp on the plateau; the basin is its crater lake"}]
    rng = np.random.default_rng(seed)

    def try_place(sid, name, w, h, group, src, region, prefer, tries=8000, gap=48, near=None):
        best = None
        for _ in range(tries):
            if near:
                ang = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, near[2])
                cx, cz = near[0] + r * math.cos(ang), near[1] + r * math.sin(ang)
            else:
                cx, cz = rng.uniform(region[0], region[2]), rng.uniform(region[1], region[3])
            x0, z0 = int(cx - w / 2) // 16 * 16, int(cz - h / 2) // 16 * 16; x1, z1 = x0 + w - 1, z0 + h - 1
            if x0 - MARGIN < X0 + 48 or z0 - MARGIN < Z0 + 48 or x1 + MARGIN > X1 - 48 or z1 + MARGIN > Z1 - 48: continue
            if inside(cx, cz, TOWN) or inside(cx, cz, PLANT): continue
            if group != "farmstead" and inside(cx, cz, WOODS): continue
            if blocked(x0 - MARGIN, z0 - MARGIN, x1 + MARGIN, z1 + MARGIN): continue
            if any(not (x1 + gap < p["x0"] or x0 - gap > p["x1"] or z1 + gap < p["z0"] or z0 - gap > p["z1"]) for p in placed): continue
            rd = at8(droad8, cx, cz)
            if rd < 12: continue
            score = (0 if rd <= 90 else (rd - 90)) + 40 * rough(x0, z0, x1, z1) + prefer(cx, cz, x0, z0, x1, z1)
            if best is None or score < best[0]: best = (score, x0, z0, x1, z1, rd)
        if best is None:
            print(f"  {name}: NO POSITION"); return None
        _, x0, z0, x1, z1, rd = best
        p = {"id": sid, "name": name, "x0": x0, "z0": z0, "x1": x1, "z1": z1, "group": group, "road_m": round(rd), "source": src}
        placed.append(p); print(f"  {name:34s} x {x0}..{x1} z {z0}..{z1}  road {round(rd)} m  [{group}]"); return p

    ALL = (X0, Z0, X1, Z1)
    SW = (-2980, -900, -2600, 400)        # the hub's west edge then clears the ridge foot (x -3450) by 50+; the Woods start east of it
    EAST = (-1300, -2200, 1100, -500); NORTH = (-3600, -3850, -800, -3300)
    hub = try_place("hub", "Novo Expograd hub (desert city)", 832, 640, "cyber", "scratch/upgrade/world hub (1.12), ships cut", SW,
                    lambda cx, cz, *r: 0.3 * abs(cx - (-2950)) + 0.2 * abs(cz - (-300)))
    if hub:
        hx, hz = (hub["x0"] + hub["x1"]) / 2, (hub["z0"] + hub["z1"]) / 2
        for sid, name, w, h, src in (("novo", "Novo Expograd Industrial Zone", 144, 160, "scratch/upgrade/novo_industrial (1.12)"),
                                     ("plaza", "Financial Plaza + sewers", 160, 144, "scratch/upgrade/financial_plaza + sewers (1.12)"),
                                     ("biogen", "Bio Gen offices", 64, 256, "scratch/upgrade/biogen_strip (1.12)")):
            try_place(sid, name, w, h, "cyber", src, SW, lambda cx, cz, *r: 0.4 * math.hypot(cx - hx, cz - hz), near=(hx, hz, 700), gap=32)
    try_place("skad", "Skadowsky sector", 464, 752, "sector", "incoming/skadowsky 1.2", (-2600, -1500, -200, -400),
              lambda cx, cz, x0, z0, x1, z1: 0.5 * min(at8(dbare8, cx, z1 + 40), at8(dbare8, cx, z0 - 40)))
    try_place("mega", "Mega-base", 384, 528, "player", "live world x 2192..2575 z 400..927", EAST,
              lambda cx, cz, x0, z0, x1, z1: 0.6 * min(at8(dwater8, x0 - 30, cz), at8(dwater8, x1 + 30, cz), at8(dwater8, cx, z0 - 30), at8(dwater8, cx, z1 + 30)))
    try_place("indu", "Industrial district", 464, 272, "player", "live world x 1904..2367 z 864..1135", (-1300, -1500, 1100, -450),
              lambda cx, cz, *r: 0.2 * abs(cz - (-700)) + 0.1 * abs(cx - 600))
    try_place("hemp", "Hempcrete compound", 320, 320, "player", "live world x 1568..1887 z 1152..1471", ALL,
              lambda cx, cz, *r: 60 * (1 - at8(tree8, cx, cz)) + 0.1 * math.hypot(cx - (-2600), cz - (-1200)))
    try_place("lib", "Library", 96, 96, "player", "live world x 2032..2127 z 1392..1487", (-3800, -3850, -1500, -1300),
              lambda cx, cz, *r: 0.5 * math.hypot(cx - (-2500), cz - (-3800)))
    try_place("runway", "Runway (pad)", 512, 192, "pad", "built pad", NORTH, lambda cx, cz, *r: 0)
    try_place("settle", "Settlement", 272, 288, "player", "scratch/upgrade/world east site (1.12)", (-1300, -2200, 1100, -500),
              lambda cx, cz, *r: 0.15 * abs(cx - (-300)) + 0.15 * abs(cz - (-1900)))
    for i in range(29):
        try_place(f"old{i + 1:02d}", f"farmstead {i + 1}", 64, 64, "farmstead", "live world, old site", ALL,
                  lambda cx, cz, *r: 0.5 * abs(at8(droad8, cx, cz) - 40), tries=3000, gap=150)
    json.dump({"border": [X0, Z0, X1, Z1], "sectors": placed, "areas": {"woods": list(WOODS), "town": list(TOWN), "plant": list(PLANT)}},
              open(out / "sectors_v8.json", "w"), indent=1)
    prev = Image.open(hdir / "height_preview.png").convert("RGB"); k = prev.width / W; d = ImageDraw.Draw(prev)
    COL = {"camp": (255, 230, 80), "cyber": (255, 90, 220), "sector": (255, 140, 60), "player": (120, 220, 255), "pad": (200, 200, 200), "farmstead": (140, 255, 140)}
    wx0, wz0, wx1, wz1 = WOODS
    d.rectangle([(wx0 - X0) * k, (wz0 - Z0) * k, (wx1 - X0) * k, (wz1 - Z0) * k], outline=(80, 200, 80), width=2)
    d.text(((wx0 - X0) * k + 4, (wz0 - Z0) * k + 4), "THE WOODS (named area, existing forest)", fill=(120, 255, 120))
    for p in placed:
        col = COL[p["group"]]; box = [(p["x0"] - X0) * k, (p["z0"] - Z0) * k, (p["x1"] - X0) * k, (p["z1"] - Z0) * k]
        d.rectangle(box, outline=col, width=2 if p["group"] == "farmstead" else 3)
        if p["group"] != "farmstead":
            d.rectangle([box[0], box[1] - 12, box[0] + len(p["name"]) * 6 + 4, box[1]], fill=(0, 0, 0)); d.text((box[0] + 2, box[1] - 11), p["name"], fill=col)
    prev.save(out / "sectors_v8.png"); print("->", out)


if __name__ == "__main__":
    main(sys.argv)
