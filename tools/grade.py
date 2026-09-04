"""Grade terrain to ONE continuous surface: a flat core at a chosen level, a smooth falloff to the natural
ground around it, and (optionally) a bowl blended down to a crater/lake inside it. Replaces the per-pad ramps
(terrain.py ramp), which left terraces wherever pads at different levels sat close together and skipped
every built column.

usage: grade.py <world dir> x1 z1 x2 z2 --y Y [--falloff R] [--bowl bx1 bz1 bx2 bz2 --bowl-floor F --bowl-width W]
                [--protect x1 z1 x2 z2 ...] [--keep-built-beyond N] [--label L] [--dry-run]

  core x1..x2 z1..z2  every column inside becomes ground level Y (buildings removed, ponds filled)
  --falloff R         outside the core the surface blends from Y to the natural ground over R blocks
                      (smoothstep), so the slope is about (|Y - ground| / R); default 64
  --bowl ...          a rect inside the core that is left untouched (the crater lake and its island); the
                      ground around it is blended from --bowl-floor at the rect edge up to Y over
                      --bowl-width blocks (a crater wall)
  --protect ...       rects never touched (block coordinates, repeatable)
  --keep-built-beyond N   built columns further than N blocks outside the core are left alone (a city
                      around a site keeps its buildings; N=0 removes every building the falloff reaches;
                      default: remove everything inside core+falloff)
Heights are read from natural ground (terrain.py World.ground); built columns are cleared to the local
16x16-cell median first, as terrain.py's clear-only pad does. Block entities above the new ground are dropped.
"""
import json, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, column_is_built, water_top, FILL, TOP, WATER, AIR


def smoothstep(t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return t * t * (3 - 2 * t)


def cheb_dist(x, z, r):
    """Euclidean distance from (x,z) to the rect r=(x1,z1,x2,z2); 0 inside. (Named for its old Chebyshev
    form; the Euclidean form rounds the corners of the bowl and the falloff instead of squaring them.)"""
    dx = max(r[0] - x, 0, x - r[2]); dz = max(r[1] - z, 0, z - r[3])
    return (dx * dx + dz * dz) ** 0.5


def grade(world, core, y, falloff=64, bowl=None, bowl_floor=None, bowl_width=32, protect=(), keep_built_beyond=None,
          label="", dry=False):
    x1, z1, x2, z2 = core
    R = falloff
    rx1, rz1, rx2, rz2 = x1 - R, z1 - R, x2 + R, z2 + R

    def protected(x, z):
        return any(p[0] <= x <= p[2] and p[1] <= z <= p[3] for p in protect) or (bowl and cheb_dist(x, z, bowl) == 0)

    # 1. reference surface: per 16x16 cell, the median natural ground of the cell's unbuilt columns
    cell = {}
    for cx in range(rx1 >> 4, (rx2 >> 4) + 1):
        for cz in range(rz1 >> 4, (rz2 >> 4) + 1):
            hs = []
            for x in range(cx * 16, cx * 16 + 16, 2):
                for z in range(cz * 16, cz * 16 + 16, 2):
                    if not column_is_built(world, x, z):
                        g = world.ground(x, z)
                        if g is not None: hs.append(g)
            if hs: cell[(cx, cz)] = int(statistics.median(hs))

    def ref(x, z):
        k = (x >> 4, z >> 4)
        near = [v for (a, b), v in cell.items() if abs(a - k[0]) <= 1 and abs(b - k[1]) <= 1]
        return int(statistics.median(near)) if near else cell.get(k)

    # 2. target height per column
    target = {}
    for x in range(rx1, rx2 + 1):
        for z in range(rz1, rz2 + 1):
            if protected(x, z): continue
            built = column_is_built(world, x, z)
            g = world.ground(x, z)
            if g is None: continue
            d = cheb_dist(x, z, core)
            if d == 0:
                t = y
                if bowl is not None:
                    db = cheb_dist(x, z, bowl)
                    if db <= bowl_width:
                        t = round(bowl_floor + (y - bowl_floor) * smoothstep(db / bowl_width))
            else:
                if keep_built_beyond is not None and built and d > keep_built_beyond: continue
                base = ref(x, z) if built else g
                if base is None: continue
                # keep the natural texture: blend toward the column's own ground, pulled to the cell reference
                t = round(y * (1 - smoothstep(d / R)) + base * smoothstep(d / R))
            target[(x, z)] = t

    # 3. light blur outside the core so cell-median seams and single-column spikes disappear
    blurred = {}
    for (x, z), t in target.items():
        if cheb_dist(x, z, core) == 0 and (bowl is None or cheb_dist(x, z, bowl) > bowl_width):
            blurred[(x, z)] = t; continue
        acc = [];
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                v = target.get((x + dx, z + dz))
                if v is not None: acc.append(v)
        blurred[(x, z)] = round(sum(acc) / len(acc)) if acc else t
    target = blurred

    # 4. apply
    changed = rebuilt = 0
    for (x, z), t in target.items():
        g = world.ground(x, z)
        if g is None: continue
        wt = water_top(world, x, z)
        if column_is_built(world, x, z):
            world.clear_column(x, z, min(g, t) + 1)
            rebuilt += 1
        if t > g:
            for yy in range(g + 1, t + 1): world.set(x, yy, z, FILL if yy < t else TOP)
            world.clear_column(x, z, t + 1)
        elif t < g:
            world.clear_column(x, z, t + 1)
            world.set(x, t, z, TOP)
        else:
            world.clear_column(x, z, t + 1)
        if wt is not None and t < wt and cheb_dist(x, z, core) > 0:
            for yy in range(t + 1, wt + 1): world.set(x, yy, z, WATER)   # a lake outside the core keeps its level
        changed += 1
    dropped = world.drop_block_entities(rx1, rz1, rx2, rz2, lambda x, z: target.get((x, z)), protected)
    files, chunks = world.save(dry)
    print(f"grade {label}: core x {x1}..{x2} z {z1}..{z2} at y={y}, falloff {R}, bowl {bowl}: {changed} columns set "
          f"({rebuilt} built columns removed), {dropped} block entities dropped, {chunks} chunks, files {len(files)}")
    print("DRY RUN - nothing written" if dry else "written")


def main(a):
    if len(a) < 6: sys.exit(__doc__)
    world = World(Path(a[1]))
    core = tuple(int(v) for v in a[2:6])
    def opt(name, n, default=None, cast=int):
        if name not in a: return default
        i = a.index(name); vals = [cast(v) for v in a[i + 1:i + 1 + n]]
        return vals[0] if n == 1 else tuple(vals)
    protect = []
    for i, v in enumerate(a):
        if v == "--protect": protect.append(tuple(int(q) for q in a[i + 1:i + 5]))
    grade(world, core, opt("--y", 1), opt("--falloff", 1, 64), opt("--bowl", 4), opt("--bowl-floor", 1),
          opt("--bowl-width", 1, 32), protect, opt("--keep-built-beyond", 1), opt("--label", 1, "", str), "--dry-run" in a)


if __name__ == "__main__":
    main(sys.argv)
