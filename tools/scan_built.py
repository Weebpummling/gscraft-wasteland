"""Where is Skadowsky actually built up?

The sector's hospital, camp, mast and bridge are measured in the design, but the station and the rail
yard never were, and a spawn pass that puts the Dead "in the buildings" needs to know which ground is
buildings. So count built blocks per 32 x 32 cell across the sector and print a map of it.

Built means a block that terrain generation does not place here: bricks, concrete, planks, glass, iron,
rails and the rest. Stone, dirt, grass, sand, gravel, water, logs and leaves are landscape.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, r"G:/GSCraft/repo/tools")
from applyheight import decode_chunk          # noqa: E402
from transplant import read_region_raw, R, slot_of, region_of  # noqa: E402

WORLD = Path(r"G:/GSCraft/server/wasteland-v8")
X0, X1, Z0, Z1 = -1088, -625, -1488, -737     # the Skadowsky sector
CELL = 32

NATURAL = ("air", "stone", "dirt", "grass_block", "sand", "gravel", "water", "lava", "deepslate",
           "granite", "diorite", "andesite", "clay", "coarse_dirt", "podzol", "mud", "sandstone",
           "log", "leaves", "wood", "vine", "grass", "fern", "flower", "seagrass", "kelp", "moss",
           "ore", "bedrock", "tuff", "calcite", "snow", "ice", "terracotta", "rooted", "mycelium",
           "dripstone", "sculk", "azalea", "cave_", "bubble", "magma", "obsidian", "farmland", "path")


def natural(name):
    n = name.split(":", 1)[-1]
    return any(k in n for k in NATURAL)


def main():
    cells = Counter()
    regions = {}
    cx0, cx1 = X0 >> 4, X1 >> 4
    cz0, cz1 = Z0 >> 4, Z1 >> 4
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            rk = region_of(cx, cz)
            if rk not in regions:
                p = WORLD / "region" / f"r.{rk[0]}.{rk[1]}.mca"
                regions[rk] = read_region_raw(p) if p.exists() else {}
            ent = regions[rk].get(slot_of(cx, cz))
            if not ent:
                continue
            try:
                _, root = R(ent[2]).root()
                ids, pal, _ = decode_chunk(root)
            except Exception:
                continue
            names = np.array([e["Name"][1] for e in pal], object)
            built = np.array([not natural(str(n)) for n in names])
            if not built.any():
                continue
            n = int(built[ids].sum())
            if n:
                cells[((cx * 16) // CELL * CELL, (cz * 16) // CELL * CELL)] += n

    if not cells:
        print("nothing found")
        return
    top = cells.most_common()
    print(f"{len(cells)} cells with built blocks; densest 24:")
    for (x, z), n in top[:24]:
        print(f"   x {x:6d} z {z:6d}   {n:7d}")
    # a coarse picture: rows of the sector, marking cells above a threshold
    thresh = top[len(top) // 4][1] if len(top) > 4 else 1
    print(f"\nmap, '#' is a cell above {thresh:,} built blocks, '.' below, ' ' empty")
    for z in range(Z0 // CELL * CELL, Z1 + CELL, CELL):
        row = ""
        for x in range(X0 // CELL * CELL, X1 + CELL, CELL):
            n = cells.get((x, z), 0)
            row += "#" if n >= thresh else ("." if n else " ")
        print(f"  z {z:6d}  {row}")
    print(f"  x from {X0 // CELL * CELL} to {X1}, each column {CELL} blocks")


if __name__ == "__main__":
    main()
