#!/usr/bin/env python3
"""Land use of the built world, chunk by chunk: water, city (Lost Cities fingerprint), or wilderness.
Writes tools/landuse_v6.json (counts, per-ring ratios, and the grid as rows of characters:
'~' water, '#' city, '.' wilderness, ' ' outside the box / absent) and docs/renders/landuse_v6.png.

    python landuse.py <world dir>          (about 20 min: every chunk of the 10 km box is parsed)

City fingerprint: the section palettes contain Lost Cities' fills for this pack — IE hempcrete or
hempcrete pillar (city ground), Superb Warfare sandbags, or a spawner beside cracked stone bricks.
Water: the top block of the chunk's centre column is water or ice. Rings are the design's ranges
from the camp: foot < 1.5 km, road 1.5-4 km, air 4.5-6.5 km.
"""
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import R, read_region_raw  # noqa: E402
from anvil import Chunk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CENTRE = (1900, 1250); HALF = 5000
CAMP = (16, 16)
CITY_MARKS = {"immersiveengineering:hempcrete", "immersiveengineering:hempcrete_pillar", "superbwarfare:sandbag"}
WATER = {"minecraft:water", "minecraft:ice", "minecraft:packed_ice", "minecraft:frosted_ice"}


def ring(x, z):
    d = math.hypot(x - CAMP[0], z - CAMP[1])
    return "foot" if d < 1500 else "road" if d < 4000 else "air" if d <= 6500 else "beyond"


def classify(root):
    names = set()
    spawner = cracked = False
    for sec in root.get("sections", (9, (10, [])))[1][1]:
        bs = sec.get("block_states")
        if not bs:
            continue
        for p in bs[1]["palette"][1][1]:
            n = p["Name"][1]; names.add(n)
            if n == "minecraft:spawner": spawner = True
            if n == "minecraft:cracked_stone_bricks": cracked = True
    c = Chunk(root)
    y, top = c.top(8, 8)
    if top in WATER:
        return "~"
    if names & CITY_MARKS or (spawner and cracked):
        return "#"
    return "."


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    region = Path(argv[1]) / "region"
    cx0, cz0 = (CENTRE[0] - HALF) >> 4, (CENTRE[1] - HALF) >> 4
    n = (2 * HALF) >> 4
    grid = [[" "] * n for _ in range(n)]
    counts = {}; t0 = time.time()
    files = sorted(region.glob("r.*.mca"))
    for i, rp in enumerate(files):
        rx, rz = map(int, rp.stem.split(".")[1:])
        for slot, (ts, comp, raw) in read_region_raw(rp).items():
            cx, cz = rx * 32 + slot % 32, rz * 32 + slot // 32
            gx, gz = cx - cx0, cz - cz0
            if not (0 <= gx < n and 0 <= gz < n):
                continue
            root = R(raw).root()[1]
            k = classify(root)
            grid[gz][gx] = k
            r = ring(cx * 16 + 8, cz * 16 + 8)
            counts.setdefault(r, {"~": 0, "#": 0, ".": 0})[k] += 1
        if i % 40 == 0:
            print(f"  {i}/{len(files)} files, {time.time() - t0:.0f}s", flush=True)
    out = {"counts": counts, "grid_origin_chunk": [cx0, cz0], "grid": ["".join(row) for row in grid]}
    (ROOT / "tools" / "landuse_v6.json").write_text(json.dumps(out), encoding="utf-8")
    total = {k: sum(c[k] for c in counts.values()) for k in "~#."}
    land = total["#"] + total["."]
    print(f"\nchunks: water {total['~']}, city {total['#']}, wilderness {total['.']}; city share of land {100 * total['#'] / max(land, 1):.1f}%")
    for r, c in counts.items():
        l = c["#"] + c["."]
        print(f"  {r:7} water {c['~']:6} city {c['#']:6} wild {c['.']:6}  city/land {100 * c['#'] / max(l, 1):.1f}%")
    from PIL import Image
    img = Image.new("RGB", (n, n), (232, 230, 224)); px = img.load()
    col = {"~": (120, 160, 200), "#": (110, 60, 60), ".": (200, 190, 160), " ": (232, 230, 224)}
    for z in range(n):
        for x in range(n):
            px[x, z] = col[grid[z][x]]
    p = ROOT / "docs" / "renders" / "landuse_v6.png"; img.resize((n * 2, n * 2)).save(p); print("map:", p, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv)
