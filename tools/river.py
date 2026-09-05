"""Carve a river channel along a polyline (v8: connect the map's water to the Skadowsky sector's river).

usage: river.py build <world dir> <rivers.json> [--dry-run]
       river.py mouths <world dir> x0 z0 x1 z1            list water columns on the edges of a footprint (river mouths)
rivers.json: [{"name": "...", "points": [[x, z], ...], "width": 12, "level": 63, "depth": 3}, ...]
The channel bed is cut to level - depth, filled with water to level, bed of gravel/sand, banks graded 1:3 from the
water's edge up to the natural ground (dirt below, grass on top); built columns are never touched; trees inside the
channel and on the banks are removed. Use roads.py route to find the polyline first (it avoids buildings).
"""
import sys, json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, column_is_built, AIR, LIQUID, PLANT
from roads import densify

BANK = 3          # blocks of bank per block of height


def carve(world, river, dry):
    pts = river["points"]; width = river.get("width", 12); level = river.get("level", 63); depth = river.get("depth", 3)
    ground_ref = river.get("land")   # the surrounding land level the banks climb to (fills a previous over-cut)
    half = width / 2.0; reach = half + 1 + BANK * 12
    # sample the centre line densely, then work per column in the corridor
    line = densify([tuple(p) for p in pts])
    cols = {}
    for i in range(0, len(line), 2):
        cx, cz = line[i]
        for dx in range(-int(reach), int(reach) + 1):
            for dz in range(-int(reach), int(reach) + 1):
                x, z = int(cx) + dx, int(cz) + dz
                d = math.hypot(dx, dz)
                if d > reach: continue
                if (x, z) not in cols or d < cols[(x, z)]: cols[(x, z)] = d
    changed = 0
    for (x, z), d in cols.items():
        if column_is_built(world, x, z): continue
        g = world.ground(x, z)
        if g is None: continue
        if d <= half:                                       # channel: bed at level-depth, water to level
            bed = level - depth
            world.clear_column(x, z, bed + 1)
            if g < bed:
                for yy in range(g + 1, bed + 1): world.set(x, yy, z, "minecraft:dirt")
            world.set(x, bed, z, "minecraft:gravel" if (x + z) % 3 else "minecraft:sand")
            for yy in range(bed + 1, level + 1): world.set(x, yy, z, "minecraft:water")
            changed += 1
        else:                                               # bank: from the water's edge up to the ground over BANK blocks per block
            rise = (d - half) / BANK
            want = int(round(level + rise))
            natural = ground_ref if ground_ref is not None else g
            want = min(want, natural)                 # never rise above the land the bank meets
            if want == g: continue
            world.clear_column(x, z, min(g, want) + 1)
            if want > g:
                for yy in range(g + 1, want + 1): world.set(x, yy, z, "minecraft:dirt" if yy < want else "minecraft:grass_block")
            else:
                world.set(x, want, z, "minecraft:grass_block")
                for yy in range(want - 2, want):
                    if world.get(x, yy, z) not in AIR: world.set(x, yy, z, "minecraft:dirt")
            changed += 1
    files, chunks = world.save(dry)
    print(f"river {river['name']}: {len(line)} m, width {width}, level {level}: {changed} columns, {chunks} chunks, {len(files)} files{' (dry)' if dry else ''}")


def mouths(world, x0, z0, x1, z1):
    out = []
    for x in range(x0, x1 + 1):
        for z, side in ((z0, "N"), (z1, "S")):
            y, b = world.top(x, z)
            if b in LIQUID: out.append((side, x, z, y))
    for z in range(z0, z1 + 1):
        for x, side in ((x0, "W"), (x1, "E")):
            y, b = world.top(x, z)
            if b in LIQUID: out.append((side, x, z, y))
    # cluster consecutive water columns per side
    groups = {}
    for side, x, z, y in out: groups.setdefault(side, []).append((x, z, y))
    for side, lst in groups.items():
        lst.sort(); start = lst[0]; prev = lst[0]; run = [lst[0]]
        for p in lst[1:] + [None]:
            if p is not None and abs(p[0] - prev[0]) + abs(p[1] - prev[1]) <= 2: run.append(p); prev = p; continue
            mid = run[len(run) // 2]; print(f"  {side} mouth at ({mid[0]}, {mid[1]}) water y {mid[2]}, {len(run)} columns wide")
            if p is not None: run = [p]; prev = p


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    if a[1] == "mouths":
        mouths(World(Path(a[2])), *map(int, a[3:7])); return
    world = World(Path(a[2])); rivers = json.load(open(a[3])); dry = "--dry-run" in a
    for r in rivers: carve(world, r, dry)


if __name__ == "__main__":
    main(sys.argv)
