"""Roads for the wasteland: route between waypoints avoiding water and buildings, then build them.

usage: roads.py route <world dir> <roads.json> <out routes.json> [--meander A] [--wavelength N]
       roads.py build <world dir> <routes.json> [--style S] [--dry-run]
       roads.py check <world dir> <routes.json>                        water / built / slope along each built road

roads.json: [{"name": "...", "points": [[x, z], ...], "width": 7, "style": "trunk"}, ...]  - waypoints in
blocks; the router finds the path between consecutive waypoints. Cell cost:
1 + 40*water + 80*built + 3*|slope| + meander; the path stays on land wherever land exists and crosses
water only where the detour would be longer than the crossing is worth. `--meander A` (0.4 is a good
value) adds a smooth noise field of amplitude A so a long road on flat ground wanders instead of running
dead straight; it is far below the water and building costs, so it never re-routes a road, only bends it.
routes.json carries the block-level polyline, the width and the class per road.

Classes (--style, or "style" per route, which wins): trunk / skadowsky 9 wide with andesite-wall kerbs,
road 7 wide with cobble kerbs, track 5 wide gravel and coarse dirt. Every built road writes
`road_<name>_mask.npz` next to the bridge masks so the terrain tools can protect it.

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
# Skadowsky vocabulary (v8, owner 2026-09-04): a stone / andesite / gravel carriageway with andesite-wall kerbs and no centre
# line; tracks are gravel and coarse dirt. Materials are picked per column from a hash so the mix is stable.
# Three classes (v8 road review, step 4): a trunk between named places, a road to a sector's gate, a farm track.
# "skadowsky" is kept as the trunk's old name so the existing plan files still build.
STYLE = {"default": None,
         "skadowsky": {"road": [("minecraft:stone", 45), ("minecraft:andesite", 35), ("minecraft:gravel", 20)],
                       "kerb": [("minecraft:andesite_wall", 100)], "line": None, "fill": "minecraft:dirt"},
         "trunk": {"road": [("minecraft:stone", 45), ("minecraft:andesite", 35), ("minecraft:gravel", 20)],
                   "kerb": [("minecraft:andesite_wall", 100)], "line": None, "fill": "minecraft:dirt"},
         "road": {"road": [("minecraft:andesite", 40), ("minecraft:gravel", 35), ("minecraft:cobblestone", 25)],
                  "kerb": [("minecraft:cobblestone", 60), ("minecraft:gravel", 40)], "line": None, "fill": "minecraft:dirt"},
         "track": {"road": [("minecraft:gravel", 60), ("minecraft:coarse_dirt", 40)], "kerb": None, "line": None, "fill": "minecraft:dirt"}}
DEFAULT_WIDTH = {"skadowsky": 9, "trunk": 9, "road": 7, "track": 5}
_style = None
_meander = 0.0     # amplitude of the wander cost in step-cost units (--meander); 0 keeps the old ruler-straight router
_wavelength = 224  # blocks per noise cell of the wander field
FLARE = 4          # a junction opens by this many blocks over FLARE_LEN at each end of a route
FLARE_LEN = 14


def _hash2(i, j, seed=1013):
    h = (i * 374761393 + j * 668265263 + seed * 2147483647) & 0xffffffff
    h = (h ^ (h >> 13)) * 1274126177 & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def wander(x, z):
    """Smooth value noise in [-1, 1] over `_wavelength` blocks: the term that makes a long road meander
    instead of running dead straight over flat ground (v8 road review, finding 2.4)."""
    c = _wavelength
    fi, fj = x / c, z / c
    i0, j0 = int(fi // 1), int(fj // 1); tx, tz = fi - i0, fj - j0
    sx, sz = tx * tx * (3 - 2 * tx), tz * tz * (3 - 2 * tz)
    a = _hash2(i0, j0) * (1 - sx) + _hash2(i0 + 1, j0) * sx
    b = _hash2(i0, j0 + 1) * (1 - sx) + _hash2(i0 + 1, j0 + 1) * sx
    return (a * (1 - sz) + b * sz) * 2 - 1


def styled(kind, x, z):
    """Resolve ROAD / KERB / LINE for a column under the active style; None means 'do not place'."""
    if _style is None: return kind
    key = {ROAD: "road", KERB: "kerb", LINE: "line"}.get(kind)
    if key is None: return kind
    choices = _style[key]
    if choices is None: return None
    h = (x * 73856093 ^ z * 19349663) & 0xffff; total = sum(w for _, w in choices); pick = h % total
    for name, wgt in choices:
        pick -= wgt
        if pick < 0: return name
    return choices[-1][0]


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
                if _meander:
                    # a low-frequency field the path prefers to follow; too small to beat water (40) or a
                    # building (80), big enough to bend a kilometre of flat ground by a few tens of metres
                    cost += step * _meander * (wander(m[0] * CELL, m[1] * CELL) + 1) * 0.5
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
        st = r.get("style")
        routes.append({"name": r["name"], "width": r.get("width", DEFAULT_WIDTH.get(st, 7)), "style": st, "polyline": poly, **stats})
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
    fill = (_style or {}).get("fill") or FILL
    for yy in range(g + 1, y):
        world.set(x, yy, z, fill)
    if g >= y:
        for yy in range(y + 1, g + 1): world.set(x, yy, z, "minecraft:air")
        for yy in range(y - 1, max(y - 3, -60), -1):
            if world.get(x, yy, z) in AIR or world.get(x, yy, z) in LIQUID: world.set(x, yy, z, fill)
    mat = styled(kind, x, z)
    if mat is None: mat = styled(ROAD, x, z) if kind == LINE else None
    if mat is not None: world.set(x, y, z, mat)
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


def save_road_mask(name, cols):
    """The road's columns as a protect mask, the way bridge.py writes one, so river.py / shoreline.py /
    lakefill.py / smoothcliffs.py can be told to leave the carriageway and its kerbs alone."""
    import numpy as np
    if not cols: return
    xs = [c[0] for c in cols]; zs = [c[1] for c in cols]; ox, oz = min(xs) - 2, min(zs) - 2
    m = np.zeros((max(zs) - oz + 3, max(xs) - ox + 3), bool)
    for x, z in cols: m[z - oz - 1:z - oz + 2, x - ox - 1:x - ox + 2] = True
    out = Path(r"G:/GSCraft/incoming/census") / f"road_{name}_mask.npz"
    np.savez_compressed(out, mask=m, origin=np.array([ox, oz]))
    return out


def half_at(k, n, half):
    """Half-width at step k of n: the carriageway opens by FLARE over the last FLARE_LEN blocks at each
    end, so a connector meets the network as a junction instead of butting into it."""
    d = min(k, n - 1 - k)
    if d >= FLARE_LEN: return half
    return half + int(round(FLARE * (1 - d / FLARE_LEN)))


def cmd_build(world, routes, dry):
    global _style
    outer = _style; total = 0
    for r in routes:
        _style = STYLE[r["style"]] if r.get("style") in STYLE else outer      # a route may carry its own class
        pts = densify(r["polyline"]); hs = target_heights(world, pts); half = r.get("width", 7) // 2
        road_cols = {}; n = 0
        for k, ((x, z), y) in enumerate(zip(pts, hs)):       # pass 1: every road column, centre wins over kerb
            h = half_at(k, len(pts), half)
            for dx in range(-h, h + 1):
                for dz in range(-h, h + 1):
                    if dx * dx + dz * dz > h * h + h: continue
                    px, pz = x + dx, z + dz
                    edge = max(abs(dx), abs(dz)) == h
                    kind = KERB if edge else (LINE if (dx == 0 and dz == 0 and (x + z) % 6 < 3) else ROAD)
                    prev = road_cols.get((px, pz))
                    if prev is None or (prev[1] == KERB and kind != KERB): road_cols[(px, pz)] = (y, kind)
        for (px, pz), (y, kind) in road_cols.items():
            if lay_column(world, px, pz, y, kind): n += 1
        shoulders = {}
        for i, ((x, z), y) in enumerate(zip(pts, hs)):        # pass 2: shoulders, never over a road column
            h = half_at(i, len(pts), half)
            for k in range(1, 9):
                for dx, dz in ((h + k, 0), (-h - k, 0), (0, h + k), (0, -h - k)):
                    px, pz = x + dx, z + dz
                    if (px, pz) in road_cols or (px, pz) in shoulders: continue
                    shoulders[(px, pz)] = (y, k)
        for (px, pz), (y, k) in shoulders.items():
            g = world.ground(px, pz)
            if g is None or surface_built(world, px, pz): continue
            shoulder_column(world, px, pz, y + (g - y) * k // 9, g)
        total += n
        if not dry: save_road_mask(r["name"], list(road_cols))
        print(f"  road {r['name']}: {len(pts)} steps, {n} road columns laid ({r.get('style') or 'default'}, {r.get('width', 7)} wide)")
    _style = outer
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
    global _style, _meander, _wavelength
    if len(a) < 4: sys.exit(__doc__)
    if "--style" in a: _style = STYLE[a[a.index("--style") + 1]]
    if "--meander" in a: _meander = float(a[a.index("--meander") + 1])
    if "--wavelength" in a: _wavelength = int(a[a.index("--wavelength") + 1])
    cmd, world = a[1], World(a[2])
    if cmd == "route": cmd_route(world, json.load(open(a[3])), a[4])
    elif cmd == "build": cmd_build(world, json.load(open(a[3])), "--dry-run" in a)
    elif cmd == "check": cmd_check(world, json.load(open(a[3])))
    else: sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
