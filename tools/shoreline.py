"""Shoreline shaping for the v8 cell (owner: no straight or chunk-stepped shores).

usage: shoreline.py <world dir> <jobs.json> <inspect.npz> [--dry-run]
jobs:
  {"organic": name, "box": [x0, z0, x1, z1], "level": 57, "depth": 6, "keep_water_from": "pass5.npz",
   "erode": 24, "amp": 14, "wavelength": 60}
      inside the box the water is: the water that was there in `keep_water_from` (the natural lake) plus an organic blob -
      the box shrunk by `erode` and grown back by a radius that wanders by +-amp along a low-frequency noise. Columns in
      that set become water (bed at level - depth); everything else in the box goes back to the relief plan (land).
  {"wobble": name, "box": [x0, z0, x1, z1], "water": "S", "level": 62, "amp": 12, "wavelength": 50}
      a straight shore along the box's water-side edge becomes wavy: land columns within amp*(0.5+0.5*noise) of that edge
      become water.
  {"square": name, "box": [x0, z0, x1, z1], "level": 62, "depth": 5}
      every column in the box becomes water (chunk-square islands).
  {"naturalize": name, "box": [x0, z0, x1, z1], "sigma": 5}
      the water mask of the box (from the inspect npz) is blurred and re-thresholded, so chunk staircases along the shore
      become curves: land that falls inside the blurred water becomes water at the neighbouring water's level; water that
      falls outside becomes land at the plan height. Built columns, protect masks and columns deeper than 6 below the
      surface are left alone.
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, LIQUID, AIR
from river import Land, column_op, Protect, column_built
from integrate import value_noise, smoothstep

CENSUS = Path(r"G:/GSCraft/incoming/census"); X0, Z0 = -3900, -3900


def to_water(world, x, z, level, depth):
    ty, tb = world.top(x, z)
    if tb is None: return 0
    if tb in LIQUID and ty <= level: return 0
    bed = level - depth
    world.clear_column(x, z, bed + 1)
    g = world.ground(x, z)
    if g is not None and g < bed:
        for yy in range(g + 1, bed + 1): world.set(x, yy, z, "minecraft:dirt")
    world.set(x, bed, z, "minecraft:gravel" if (x * 7 + z * 13) % 5 else "minecraft:sand")
    for yy in range(bed + 1, level + 1): world.set(x, yy, z, "minecraft:water")
    return 1


def to_land(world, land, x, z):
    nat = land.at(x, z)
    if nat is None: return 0
    return column_op(world, x, z, nat, "minecraft:grass_block", None)


def organic(world, land, job, dry):
    x0, z0, x1, z1 = job["box"]; level, depth = job["level"], job.get("depth", 6); H, W = z1 - z0 + 1, x1 - x0 + 1
    keep = np.load(CENSUS / job["keep_water_from"], allow_pickle=True)["wtop"][z0 - Z0:z1 - Z0 + 1, x0 - X0:x1 - X0 + 1] > -999
    er = job.get("erode", 24); amp = job.get("amp", 14); cell = max(job.get("wavelength", 60) // 3, 4)
    core = np.ones((H, W), bool); core[:er, :] = core[-er:, :] = core[:, :er] = core[:, -er:] = False
    d = ndimage.distance_transform_edt(~core)
    n = value_noise((H, W), cell, 1.0, 47)
    blob = d <= (er - 2) + amp * n                       # radius wanders between er-2-amp and er-2+amp
    mask = keep | blob
    wn = wl = 0
    for iz in range(H):
        for ix in range(W):
            x, z = x0 + ix, z0 + iz
            if column_built(world, x, z): continue
            if mask[iz, ix]: wn += to_water(world, x, z, level, depth)
            else:
                ty, tb = world.top(x, z)
                if tb in LIQUID: wl += to_land(world, land, x, z)
    files, chunks = world.save(dry)
    print(f"organic {job['organic']}: {wn} columns to water, {wl} back to land, {chunks} chunks{' (dry)' if dry else ''}")


def wobble(world, land, job, dry):
    x0, z0, x1, z1 = job["box"]; level = job["level"]; amp = job.get("amp", 12); cell = max(job.get("wavelength", 50) // 3, 4)
    H, W = z1 - z0 + 1, x1 - x0 + 1
    n = value_noise((H, W), cell, 1.0, 53)
    dist = {"S": lambda ix, iz: H - 1 - iz, "N": lambda ix, iz: iz, "E": lambda ix, iz: W - 1 - ix, "W": lambda ix, iz: ix}[job["water"]]
    wn = 0
    for iz in range(H):
        for ix in range(W):
            if dist(ix, iz) <= amp * (0.5 + 0.5 * n[iz, ix]):
                x, z = x0 + ix, z0 + iz
                if column_built(world, x, z): continue
                wn += to_water(world, x, z, level, job.get("depth", 4))
    files, chunks = world.save(dry)
    print(f"wobble {job['wobble']}: {wn} columns to water, {chunks} chunks{' (dry)' if dry else ''}")


def square(world, job, dry):
    x0, z0, x1, z1 = job["box"]; wn = 0; level, depth = job["level"], job.get("depth", 5)
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            if column_built(world, x, z): continue
            if job.get("force"):                                          # re-cut even where it is water already (deepen a shallow bed)
                bed = level - depth; world.clear_column(x, z, bed + 1); world.set(x, bed, z, "minecraft:gravel" if (x * 7 + z * 13) % 5 else "minecraft:sand")
                for yy in range(bed + 1, level + 1): world.set(x, yy, z, "minecraft:water")
                wn += 1; continue
            wn += to_water(world, x, z, level, depth)
    files, chunks = world.save(dry)
    print(f"square {job['square']}: {wn} columns to water, {chunks} chunks{' (dry)' if dry else ''}")


def naturalize(world, land, job, npz, dry):
    x0, z0, x1, z1 = job["box"]; sigma = job.get("sigma", 5)
    wt = npz["wtop"][z0 - Z0:z1 - Z0 + 1, x0 - X0:x1 - X0 + 1]; gy = npz["gy"][z0 - Z0:z1 - Z0 + 1, x0 - X0:x1 - X0 + 1]
    water = wt > -999
    blurred = ndimage.gaussian_filter(water.astype(np.float32), sigma) > 0.5
    _, idx = ndimage.distance_transform_edt(~water, return_indices=True)
    lvl = np.where(water, wt, 0)[idx[0], idx[1]]
    add = blurred & ~water; rem = ~blurred & water & (gy >= wt - 6)          # only shallow water becomes land
    protect = Protect(job.get("protect"))
    wn = wl = 0
    for iz, ix in zip(*np.nonzero(add)):
        x, z = x0 + ix, z0 + iz
        if protect(x, z) or column_built(world, x, z): continue
        wn += to_water(world, x, z, int(lvl[iz, ix]), job.get("depth", 5))
    for iz, ix in zip(*np.nonzero(rem)):
        x, z = x0 + ix, z0 + iz
        if protect(x, z) or column_built(world, x, z): continue
        wl += to_land(world, land, x, z)
    files, chunks = world.save(dry)
    print(f"naturalize {job['naturalize']}: {wn} shore columns to water, {wl} to land, {chunks} chunks{' (dry)' if dry else ''}")


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    world = World(Path(a[1])); jobs = json.load(open(a[2])); npz = np.load(a[3], allow_pickle=True); dry = "--dry-run" in a; land = Land()
    for j in jobs:
        if "organic" in j: organic(world, land, j, dry)
        elif "wobble" in j: wobble(world, land, j, dry)
        elif "square" in j: square(world, j, dry)
        elif "naturalize" in j: naturalize(world, land, j, npz, dry)


if __name__ == "__main__":
    main(sys.argv)
