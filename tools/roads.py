"""Roads for the wasteland: route between waypoints avoiding water and buildings, then build them.

usage: roads.py route <world dir> <roads.json> <out routes.json>     find least-cost paths (32-block cells)
       roads.py build <world dir> <routes.json> [--dry-run]            lay the roads into the world
       roads.py check <world dir> <routes.json>                        water / built / slope along each built road

roads.json: [{"name": "...", "points": [[x, z], ...], "width": 7}, ...]  - waypoints in blocks; the router
finds the path between consecutive waypoints. Cell cost: 1 + 40*water + 80*built + 3*|slope|; the path
stays on land wherever land exists and crosses water only where the detour would be longer than the
crossing is worth. routes.json carries the block-level polyline per road.

build: for each road, a target height per step = the ground under the centre line, median-smoothed
over +-24 blocks and slope-limited to 1 block per 3; each column within width/2 of the line is set to
that height: black concrete (centre) / gray concrete (kerbs), terracotta below down to the old ground
or the lake bed (a causeway where the line crosses water), headroom cleared above. Built columns
(Lost Cities buildings) are never touched; the router keeps the line off them. Shoulders are ramped
8 blocks out with the terrain tool's smoothing. Edited chunks lose heightmaps/light (recomputed by
the game).
"""
import sys, json, heapq, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, smooth_column, column_is_built, water_top, FILL, NATURAL, PLANT, LIQUID, AIR

CELL = 8
MARGIN = 512      # blocks of search room around each segment's bounding box
ROAD = "minecraft:black_concrete"
KERB = "minecraft:gray_concrete"
LINE = "minecraft:white_concrete"


class Grid:
    """8-block cells: ground, water and built flags, read lazily from the world."""
    def __init__(self, world):
        self.w = world; self.c = {}

    def cell(self, i, j):
        k = (i, j)
        if k in self.c: return self.c[k]
        x, z = i * CELL + CELL // 2, j * CELL + CELL // 2
        g = self.w.ground(x, z)
        if g is None: self.c[k] = None; return None
        wt = water_top(self.w, x, z); built = column_is_built(self.w, x, z)
        self.c[k] = (g, wt is not None and wt > g, built)
        return self.c[k]


def route(world, a, b):
    """A* from block a to block b over 8-block cells."""
    grid = Grid(world)
    s = (a[0] // CELL, a[1] // CELL); t = (b[0] // CELL, b[1] // CELL)
    # search box: the waypoints' bounding box plus MARGIN blocks each way. Without it A* over hilly ground
    # wanders across the world, decoding every chunk it touches (the 1.6 km Woods spur reached 23 GB).
    bi0, bi1 = min(s[0], t[0]) - MARGIN // CELL, max(s[0], t[0]) + MARGIN // CELL
    bj0, bj1 = min(s[1], t[1]) - MARGIN // CELL, max(s[1], t[1]) + MARGIN // CELL
    def h(n): return max(abs(n[0] - t[0]), abs(n[1] - t[1]))
    openq = [(h(s), 0, s, None)]; came = {}; best = {s: 0}
    while openq:
        f, g, n, p = heapq.heappop(openq)
        if n in came: continue
        came[n] = p
        if n == t: break
        if n == t: break
        cn = grid.cell(*n)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not di and not dj: continue
                m = (n[0] + di, n[1] + dj)
                if m in came or not (bi0 <= m[0] <= bi1 and bj0 <= m[1] <= bj1): continue
                cm = grid.cell(*m)
                if cm is None: continue
                step = 1.414 if di and dj else 1.0
                slope = abs(cm[0] - cn[0]) if cn else 0
                cost = step * (1 + 40 * cm[1] + 80 * cm[2] + 3 * min(slope, 12) / 4)
                ng = g + cost
                if ng < best.get(m, 1e18):
                    best[m] = ng; heapq.heappush(openq, (ng + h(m), ng, m, n))
    if t not in came: return None, None
    path = []; n = t
    while n is not None: path.append(n); n = came[n]
    path.reverse()
    blocks = [(i * CELL + CELL // 2, j * CELL + CELL // 2) for i, j in path]
    blocks[0] = tuple(a); blocks[-1] = tuple(b)
    water = sum(1 for i, j in path if grid.cell(i, j) and grid.cell(i, j)[1]); built = sum(1 for i, j in path if grid.cell(i, j) and grid.cell(i, j)[2])
    return blocks, {"cells": len(path), "water_cells": water, "built_cells": built, "metres": len(path) * CELL}


def cmd_route(world, roads, out):
    routes = []
    for r in roads:
        pts = r["points"]; poly = []; stats = {"cells": 0, "water_cells": 0, "built_cells": 0, "metres": 0}
        for a, b in zip(pts, pts[1:]):
            seg, st = route(world, a, b)
            if seg is None: print(f"  {r['name']}: no route {a} -> {b}"); continue
            poly += seg if not poly else seg[1:]
            for k in stats: stats[k] += st[k]
        routes.append({"name": r["name"], "width": r.get("width", 7), "polyline": poly, **stats})
        print(f"  {r['name']}: {stats['metres']} m, water cells {stats['water_cells']} (~{stats['water_cells'] * CELL} m), built cells {stats['built_cells']}")
    json.dump(routes, open(out, "w"), indent=1)
    print("->", out)


def densify(poly):
    """Every block position along the polyline (Bresenham-ish), with running distance."""
    out = []
    for (x1, z1), (x2, z2) in zip(poly, poly[1:]):
        n = max(abs(x2 - x1), abs(z2 - z1), 1)
        for k in range(n):
            out.append((round(x1 + (x2 - x1) * k / n), round(z1 + (z2 - z1) * k / n)))
    out.append(tuple(poly[-1]))
    dedup = []
    for p in out:
        if not dedup or dedup[-1] != p: dedup.append(p)
    return dedup


def road_ground(world, x, z):
    """Ground for the road profile: the existing road surface if one is there, else natural ground."""
    y, nm = world.top(x, z)
    if nm in (ROAD, KERB, LINE): return y
    return world.ground(x, z)


def target_heights(world, pts):
    raw = []
    for x, z in pts:
        g = road_ground(world, x, z); wt = water_top(world, x, z)
        if g is None: raw.append(None); continue
        raw.append((wt + 1) if (wt is not None and wt > g) else g)     # over water: ride 1 above the surface
    # fill gaps, median smooth +-24, slope limit 1/3
    last = next((v for v in raw if v is not None), 64)
    filled = []
    for v in raw:
        if v is None: v = last
        filled.append(v); last = v
    sm = []
    for i in range(len(filled)):
        win = filled[max(0, i - 24): i + 25]; sm.append(int(statistics.median(win)))
    for i in range(1, len(sm)):
        if sm[i] > sm[i - 1] + 1 and i % 3: sm[i] = sm[i - 1]
        if sm[i] > sm[i - 1] + 1: sm[i] = sm[i - 1] + 1
    for i in range(len(sm) - 2, -1, -1):
        if sm[i] > sm[i + 1] + 1 and i % 3: sm[i] = sm[i + 1]
        if sm[i] > sm[i + 1] + 1: sm[i] = sm[i + 1] + 1
    return sm


CLEARABLE = {"minecraft:yellow_concrete", "minecraft:dead_bush", "minecraft:short_grass", "minecraft:grass", "minecraft:tall_grass",
             "minecraft:fern", "minecraft:snow", "minecraft:water", "minecraft:oak_leaves", "minecraft:birch_leaves", "minecraft:spruce_leaves",
             "minecraft:dark_oak_leaves", "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:azalea_leaves",
             "minecraft:oak_log", "minecraft:birch_log", "minecraft:spruce_log", "minecraft:dark_oak_log", "minecraft:sweet_berry_bush",
             "minecraft:vine", "minecraft:brown_mushroom", "minecraft:red_mushroom", "minecraft:sugar_cane", "minecraft:cactus",
             ROAD, KERB, LINE}


def surface_built(world, x, z):
    """A building stands on this column: the top block is something other than terrain, plants, trees,
    water, our own road or the pad outline. (terrain.column_is_built looks at the whole column and
    treats generated cellars and ore-free mod strata under the ground as 'built', which skipped 60 % of
    every road.)"""
    y, nm = world.top(x, z)
    if nm is None: return True
    if nm in NATURAL or nm in PLANT or nm in LIQUID or nm in CLEARABLE: return False
    if nm.endswith("_leaves") or nm.endswith("_log") or nm.startswith("immersive_weathering:"): return False
    return True


def lay_column(world, x, z, y, kind):
    if surface_built(world, x, z): return False
    g = world.ground(x, z)
    if g is None: return False
    # everything above the surface up to 6 blocks headroom goes (plants, water above the road, trees)
    for yy in range(min(g, y) + 1, y + 7):
        n = world.get(x, yy, z)
        if n is not None and n not in AIR and yy != y: world.set(x, yy, z, "minecraft:air")
    for yy in range(g + 1, y):
        world.set(x, yy, z, FILL)
    if g >= y:
        for yy in range(y + 1, g + 1): world.set(x, yy, z, "minecraft:air")
        for yy in range(y - 1, max(y - 3, -60), -1):
            if world.get(x, yy, z) in AIR or world.get(x, yy, z) in LIQUID: world.set(x, yy, z, FILL)
    world.set(x, y, z, kind)
    return True


def shoulder_column(world, x, z, want, g):
    """Move a shoulder column to `want` without the whole-column built test: fill up with terracotta or
    cut down to natural ground, clearing plants above."""
    if want == g: return
    if want > g:
        for yy in range(g + 1, want + 1): world.set(x, yy, z, FILL)
    else:
        for yy in range(want + 1, g + 1): world.set(x, yy, z, "minecraft:air")
    for yy in range(want + 1, want + 4):
        n = world.get(x, yy, z)
        if n in PLANT or (n and (n.endswith("_leaves") or n in CLEARABLE) and n not in (ROAD, KERB, LINE)): world.set(x, yy, z, "minecraft:air")


def cmd_build(world, routes, dry):
    total = 0
    for r in routes:
        pts = densify(r["polyline"]); hs = target_heights(world, pts); half = r.get("width", 7) // 2
        road_cols = {}; n = 0
        for (x, z), y in zip(pts, hs):                       # pass 1: every road column, centre wins over kerb
            for dx in range(-half, half + 1):
                for dz in range(-half, half + 1):
                    if dx * dx + dz * dz > half * half + half: continue
                    px, pz = x + dx, z + dz
                    edge = max(abs(dx), abs(dz)) == half
                    kind = KERB if edge else (LINE if (dx == 0 and dz == 0 and (x + z) % 6 < 3) else ROAD)
                    prev = road_cols.get((px, pz))
                    if prev is None or (prev[1] == KERB and kind != KERB): road_cols[(px, pz)] = (y, kind)
        for (px, pz), (y, kind) in road_cols.items():
            if lay_column(world, px, pz, y, kind): n += 1
        shoulders = {}
        for (x, z), y in zip(pts, hs):                       # pass 2: shoulders, never over a road column
            for k in range(1, 9):
                for dx, dz in ((half + k, 0), (-half - k, 0), (0, half + k), (0, -half - k)):
                    px, pz = x + dx, z + dz
                    if (px, pz) in road_cols or (px, pz) in shoulders: continue
                    shoulders[(px, pz)] = (y, k)
        for (px, pz), (y, k) in shoulders.items():
            g = world.ground(px, pz)
            if g is None or surface_built(world, px, pz): continue
            shoulder_column(world, px, pz, y + (g - y) * k // 9, g)
        total += n
        print(f"  road {r['name']}: {len(pts)} steps, {n} road columns laid")
    files, chunks = world.save(dry)
    print(f"roads: {total} columns, chunks {chunks}, files {len(files)}; {'DRY RUN' if dry else 'written'}")


def cmd_check(world, routes):
    for r in routes:
        pts = densify(r["polyline"]); water = built = 0; steps = 0; maxslope = 0; last = None
        for x, z in pts:
            y, name = world.top(x, z); steps += 1
            if name == "minecraft:water": water += 1
            if surface_built(world, x, z): built += 1
            if last is not None and y is not None: maxslope = max(maxslope, abs(y - last))
            last = y
        print(f"  {r['name']}: {steps} m, water on line {water} m, buildings on line {built}, max step {maxslope}")


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    cmd, world = a[1], World(a[2])
    if cmd == "route": cmd_route(world, json.load(open(a[3])), a[4])
    elif cmd == "build": cmd_build(world, json.load(open(a[3])), "--dry-run" in a)
    elif cmd == "check": cmd_check(world, json.load(open(a[3])))
    else: sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
