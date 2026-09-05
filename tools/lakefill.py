"""Water fixes for the v8 cell: turn artificial land inside a lake or river into water, and clear tree canopies over water.

usage: lakefill.py <world dir> <jobs.json> [--dry-run]
jobs: [{"fill": name, "box": [x0, z0, x1, z1], "level": 57, "depth": 6, "round": 12, "clear_built": true},
       {"clear_over_water": name, "box": [x0, z0, x1, z1]}]
fill: every column in the box that is not water becomes water at `level` over a gravel/sand bed at level - depth (the old
column above the bed is cleared, built columns too when clear_built). `round` > 0 shrinks the fill by a disc of that radius
and grows it back (opening), so the box's corners become arcs, and a low-frequency noise wobbles the boundary. Columns kept
by an integrate mask (--protect) are never touched. clear_over_water: everything above the water surface in water columns
of the box goes (leaves, logs, floating blocks).
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, LIQUID, AIR
from river import Protect
from integrate import value_noise


def fill(world, job, dry):
    x0, z0, x1, z1 = job["box"]; level = job["level"]; depth = job.get("depth", 6); rnd = job.get("round", 0)
    protect = Protect(job.get("protect")); H, W = z1 - z0 + 1, x1 - x0 + 1
    m = np.ones((H, W), bool)
    if rnd:
        yy, xx = np.mgrid[-rnd:rnd + 1, -rnd:rnd + 1]; disk = (xx * xx + yy * yy) <= rnd * rnd
        pad = np.pad(m, rnd, constant_values=False); m = ndimage.binary_opening(pad, disk)[rnd:-rnd, rnd:-rnd]
        n = value_noise((H, W), 12, 1.0, 41)
        d = ndimage.distance_transform_edt(m); m &= d > (2 + 3 * n)              # wobble the boundary by a few blocks
    changed = 0
    for iz in range(H):
        for ix in range(W):
            if not m[iz, ix]: continue
            x, z = x0 + ix, z0 + iz
            if protect(x, z): continue
            ty, tb = world.top(x, z)
            if tb is None: continue
            if tb in LIQUID and ty <= level: continue
            bed = level - depth
            world.clear_column(x, z, bed + 1)
            g = world.ground(x, z)
            if g is not None and g < bed:
                for yy in range(g + 1, bed + 1): world.set(x, yy, z, "minecraft:dirt")
            world.set(x, bed, z, "minecraft:gravel" if (x * 7 + z * 13) % 5 else "minecraft:sand")
            for yy in range(bed + 1, level + 1): world.set(x, yy, z, "minecraft:water")
            changed += 1
    files, chunks = world.save(dry)
    print(f"fill {job['fill']}: {changed} columns -> water at y {level}, {chunks} chunks{' (dry)' if dry else ''}")


def clear_over_water(world, job, dry):
    x0, z0, x1, z1 = job["box"]; n = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            ty, tb = world.top(x, z)
            if tb is None or tb in LIQUID: continue
            # a water column with something above it: find the water surface under the top
            y = ty; found = None
            while y > ty - 40 and y > -60:
                b = world.get(x, y, z)
                if b in LIQUID: found = y; break
                y -= 1
            if found is None: continue
            # only leaves/logs/plants above water (not a bridge deck)
            names = [world.get(x, yy, z) for yy in range(found + 1, ty + 1)]
            if all(nm in AIR or nm.endswith(("_leaves", "_log", "_wood", "vine", "_sapling", "_fence")) or "grass" in nm or "fern" in nm or "mushroom" in nm for nm in names):
                world.clear_column(x, z, found + 1); n += 1
    files, chunks = world.save(dry)
    print(f"clear_over_water {job['clear_over_water']}: {n} water columns cleared of canopy, {chunks} chunks{' (dry)' if dry else ''}")


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world = World(Path(a[1])); jobs = json.load(open(a[2])); dry = "--dry-run" in a
    for j in jobs:
        if "fill" in j: fill(world, j, dry)
        elif "clear_over_water" in j: clear_over_water(world, j, dry)


if __name__ == "__main__":
    main(sys.argv)
