"""Settle transplanted builds into the landscape (v8 step 6, owner: "modify the sectors themselves to unify and
integrate them to the terrain"). Inside each footprint the structures stay; every open column (nothing built on it) is
re-grounded: its imported ground (desert sand, superflat plates, hillside) is replaced by the local ground materials at a
height that meets the neighbouring structures' foundations and the surrounding land, so the footprint edge disappears.

usage: settle.py <world dir> <sectors_v8.json> [--only id,id] [--skip id,id] [--level 65] [--dry-run]
Per footprint:
  1. classify columns: built = a non-natural block stands on the column at or above the ground (structure, pavement,
     fence, rail...), else open.
  2. foundation height of each built column = the ground block under the structure.
  3. target for an open column = distance-weighted mean of foundation heights within 24 blocks (the ground rises to meet
     a building's base), blended toward the outside level over the last 32 blocks before the footprint edge.
  4. rewrite the open column: clear everything above the target, then dirt below and grass on top; trees standing on the
     column are kept when the target equals the current ground (only their soil changes), otherwise removed.
Skadowsky (its own river, forest and roads are landscape) is skipped unless asked.
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, NATURAL, PLANT, LIQUID, AIR

SOIL = {"minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:sand", "minecraft:red_sand",
        "minecraft:gravel", "minecraft:mud", "minecraft:clay", "minecraft:moss_block", "minecraft:rooted_dirt", "minecraft:snow_block",
        "minecraft:mycelium", "minecraft:dirt_path", "minecraft:farmland"}
WASTE = {"minecraft:terracotta", "minecraft:orange_terracotta", "minecraft:red_terracotta", "minecraft:brown_terracotta",
         "minecraft:white_terracotta", "minecraft:light_gray_terracotta", "minecraft:yellow_terracotta", "minecraft:stone",
         "minecraft:andesite", "minecraft:granite", "minecraft:diorite", "minecraft:sandstone", "minecraft:smooth_sandstone"}
COVER = PLANT | LIQUID | AIR | {"minecraft:snow", "minecraft:grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern",
                                "minecraft:dead_bush", "minecraft:seagrass", "minecraft:kelp", "minecraft:lily_pad", "minecraft:vine",
                                "minecraft:dandelion", "minecraft:poppy", "minecraft:sweet_berry_bush", "minecraft:cobweb", "minecraft:cactus"}
LEAF = ("_leaves", "_log", "_wood", "_sapling", "azalea", "mangrove_roots", "bamboo", "mushroom")
GROUND = SOIL           # reassigned per footprint (SOIL, or SOIL | WASTE for builds lifted from the wasteland world)


def is_tree(n):
    return any(k in n for k in LEAF)


def column_profile(w, x, z, ground_set, level, ymax=200):
    """-> (ground_y, built, tree). Top-down: cover and trees are skipped; the first other block decides - a soil block is
    the ground (open column); a hard block above level+1 is structure; a hard block at or below level+1 is pavement or
    an imported floor and counts as structure too (kept). ground_y = the highest ground-set block."""
    top, _ = w.top(x, z)
    if top is None: return None, False, False
    built = False; tree = False; ground = None
    for y in range(min(top, ymax), -64, -1):
        n = w.get(x, y, z)
        if n is None or n in AIR: continue
        if n in COVER: continue
        if is_tree(n): tree = True; continue
        if n in ground_set:
            ground = y; break
        built = True
        # find the ground under the structure for the foundation height
        for yy in range(y - 1, -64, -1):
            m = w.get(x, yy, z)
            if m in ground_set: ground = yy; break
        break
    return ground, built, tree


def settle(w, rect, level, dry, label, ground_set):
    x0, z0, x1, z1 = rect
    W_, H_ = x1 - x0 + 1, z1 - z0 + 1
    ground = np.full((H_, W_), -999, np.int32); built = np.zeros((H_, W_), bool); tree = np.zeros((H_, W_), bool)
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            g, b, t = column_profile(w, x, z, ground_set, level)
            if g is None: continue
            ground[z - z0, x - x0] = g; built[z - z0, x - x0] = b; tree[z - z0, x - x0] = t
    valid = ground > -900
    if not built.any():
        print(f"  {label}: nothing built inside, skipped"); return 0
    # foundation field: mean foundation height of built columns within 24 blocks, distance weighted
    fnd = np.where(built, ground, 0).astype(np.float32); wgt = built.astype(np.float32)
    num = ndimage.gaussian_filter(fnd, 8, truncate=3.0); den = ndimage.gaussian_filter(wgt, 8, truncate=3.0)
    near = ndimage.distance_transform_edt(~built)
    foundation = np.where(den > 1e-3, num / np.maximum(den, 1e-3), level)
    w_f = np.clip(1 - near / 24.0, 0, 1)                                   # 1 at a wall, 0 at 24 blocks out
    # edge blend to the outside level over the last 32 blocks
    zz, xx = np.mgrid[0:H_, 0:W_]; edge = np.minimum(np.minimum(xx, W_ - 1 - xx), np.minimum(zz, H_ - 1 - zz))
    w_e = np.clip(edge / 32.0, 0, 1)
    target = (foundation * w_f + level * (1 - w_f)) * w_e + level * (1 - w_e)
    target = np.round(target).astype(np.int32)
    changed = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            iz, ix = z - z0, x - x0
            if not valid[iz, ix] or built[iz, ix]: continue
            g = int(ground[iz, ix]); t = int(target[iz, ix])
            top, _ = w.top(x, z)
            # ground material swap: the top 4 natural blocks become dirt, the surface grass
            if t == g:
                for yy in range(g - 3, g):
                    if w.get(x, yy, z) in ground_set: w.set(x, yy, z, "minecraft:dirt")
                if w.get(x, g, z) != "minecraft:grass_block": w.set(x, g, z, "minecraft:grass_block")
                # imported ground cover that is not grass-world cover (dead bushes on sand) -> removed
                n = w.get(x, g + 1, z)
                if n in ("minecraft:dead_bush", "minecraft:cactus", "minecraft:sweet_berry_bush"): w.set(x, g + 1, z, "minecraft:air")
                changed += 1; continue
            # height change: everything above the new target goes (trees included), then dirt + grass
            w.clear_column(x, z, min(g, t) + 1)
            if t > g:
                for yy in range(g + 1, t + 1): w.set(x, yy, z, "minecraft:dirt" if yy < t else "minecraft:grass_block")
            else:
                w.set(x, t, z, "minecraft:grass_block")
                for yy in range(t - 3, t):
                    if w.get(x, yy, z) in ground_set: w.set(x, yy, z, "minecraft:dirt")
            changed += 1
    files, chunks = w.save(dry)
    print(f"  {label}: {int(built.sum()):,} built columns kept, {changed:,} open columns re-grounded, {chunks} chunks, {len(files)} files{' (dry)' if dry else ''}")
    return changed


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    w = World(Path(a[1])); sectors = json.load(open(a[2]))["sectors"]
    level = int(a[a.index("--level") + 1]) if "--level" in a else 65; dry = "--dry-run" in a
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    skip = set(a[a.index("--skip") + 1].split(",")) if "--skip" in a else {"skad", "camp"}
    for p in sectors:
        if only and p["id"] not in only: continue
        if p["id"] in skip: continue
        waste = p["id"] in ("mega", "indu", "hemp", "lib") or p["id"].startswith("old")   # lifted from the wasteland world: terracotta ground
        settle(w, (p["x0"], p["z0"], p["x1"], p["z1"]), level, dry, p["name"], SOIL | WASTE if waste else SOIL)


if __name__ == "__main__":
    main(sys.argv)
