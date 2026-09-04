"""World terrain editing on local region files (run with the server stopped before uploading).

  terrain.py gaps    <world> <plan.json>                 report height gaps along every transplanted rectangle edge
  terrain.py smooth  <world> <plan.json> [--dry-run]     ramp generated terrain to the transplanted edges
  terrain.py pad     <world> x1 z1 x2 z2 [--y Y] [--protect X1 Z1 X2 Z2 ...] [--label NAME] [--clear-only] [--no-outline] [--dry-run]
                        level a rectangle to one height (above any water it touches) with a marked border;
                        --clear-only removes everything built above the ground and levels nothing
  terrain.py ramp    <world> x1 z1 x2 z2 --y Y [--label NAME]   ramp the terrain outside a levelled pad
  terrain.py outline <world> x1 z1 x2 z2 [--label NAME]         border ring + corner posts following the ground
Edited chunks lose Heightmaps and light so the game recomputes them on load.
"""
import json, sys, statistics, collections
from pathlib import Path
from transplant import R, W, read_region_raw, write_region, slot_of, region_of, T_COMPOUND, T_STRING
from anvil import Chunk, AIR

FILL = "minecraft:terracotta"          # wasteland ground body
TOP = "minecraft:terracotta"           # wasteland ground surface
BORDER = "minecraft:yellow_concrete"   # pad outline
POST = "minecraft:yellow_concrete"     # pad corner posts
SLOPE = 1.5                            # ramp width = |gap| * SLOPE columns (a 34-degree bank)
BLEND_MIN, BLEND_MAX = 8, 96
WATER = "minecraft:water"
NATURAL = {"minecraft:terracotta", "minecraft:orange_terracotta", "minecraft:red_terracotta", "minecraft:brown_terracotta",
    "minecraft:white_terracotta", "minecraft:yellow_terracotta", "minecraft:light_gray_terracotta", "minecraft:grass_block",
    "minecraft:dirt", "minecraft:stone", "minecraft:red_sand", "minecraft:sand", "minecraft:gravel", "minecraft:water",
    "minecraft:dead_bush", "minecraft:moss_block", "minecraft:coarse_dirt", "minecraft:deepslate", "minecraft:sandstone",
    "minecraft:red_sandstone", "minecraft:short_grass", "minecraft:grass", "minecraft:tall_grass", "minecraft:bedrock",
    "minecraft:podzol", "minecraft:mycelium", "minecraft:snow", "minecraft:snow_block", "minecraft:ice", "minecraft:clay",
    "minecraft:andesite", "minecraft:diorite", "minecraft:granite", "minecraft:tuff", "minecraft:calcite", "minecraft:lava",
    "minecraft:gray_terracotta", "minecraft:black_terracotta", "minecraft:cyan_terracotta", "minecraft:purple_terracotta",
    "minecraft:blue_terracotta", "minecraft:green_terracotta", "minecraft:lime_terracotta", "minecraft:pink_terracotta",
    "minecraft:magenta_terracotta", "minecraft:light_blue_terracotta",
    # Lost Cities fills the old district's city ground with these - terrain, not a build
    "immersiveengineering:hempcrete", "immersiveengineering:hempcrete_pillar", "immersiveengineering:hempcrete_brick"}
PLANT = {"minecraft:dead_bush", "minecraft:short_grass", "minecraft:grass", "minecraft:tall_grass", "minecraft:fern"}
LIQUID = {"minecraft:water", "minecraft:lava"}


class World:
    def __init__(self, path):
        self.path = Path(path); self.regions = {}; self.chunks = {}; self.dirty = set()

    def _region(self, rx, rz):
        if (rx, rz) not in self.regions:
            self.regions[(rx, rz)] = read_region_raw(self.path / "region" / f"r.{rx}.{rz}.mca")
        return self.regions[(rx, rz)]

    def chunk(self, cx, cz):
        key = (cx, cz)
        if key in self.chunks: return self.chunks[key]
        rx, rz = region_of(cx, cz); reg = self._region(rx, rz)
        ent = reg.get(slot_of(cx, cz))
        if not ent: self.chunks[key] = None; return None
        name, root = R(ent[2]).root()
        if root.get("Status", (0, ""))[1] not in ("minecraft:full", "full"):
            self.chunks[key] = None; return None
        self.chunks[key] = (name, root, Chunk(root)); return self.chunks[key]

    def get(self, x, y, z):
        c = self.chunk(x >> 4, z >> 4)
        return c[2].get(x & 15, y, z & 15) if c else None

    def set(self, x, y, z, name, props=None):
        c = self.chunk(x >> 4, z >> 4)
        if not c: return False
        ok = c[2].set(x & 15, y, z & 15, name, props)
        if ok: self.dirty.add((x >> 4, z >> 4))
        return ok

    def top(self, x, z, ignore=AIR):
        c = self.chunk(x >> 4, z >> 4)
        return c[2].top(x & 15, z & 15, ignore=ignore) if c else (None, None)

    def ground(self, x, z):
        """Highest natural solid terrain block (skips plants, water and anything built)."""
        c = self.chunk(x >> 4, z >> 4)
        if not c: return None
        ch = c[2]; lx, lz = x & 15, z & 15
        start = ch.surface_hint(lx, lz)
        for y in range(start, -65, -1):
            n = ch.get(lx, y, lz)
            if n in NATURAL and n not in PLANT and n not in LIQUID: return y
        return None

    def clear_column(self, x, z, from_y, to_y=319):
        c = self.chunk(x >> 4, z >> 4)
        if not c: return
        ch = c[2]; lx, lz = x & 15, z & 15
        for y in range(from_y, to_y + 1):
            if ch.get(lx, y, lz) not in AIR:
                ch.set(lx, y, lz, "minecraft:air"); self.dirty.add((x >> 4, z >> 4))

    def drop_block_entities(self, x1, z1, x2, z2, floor, protected=None):
        """Remove block entities inside the box above the floor. floor is an int y, or a
        callable (x, z) -> y giving the column's ground when clearing to natural terrain."""
        n = 0
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                c = self.chunk(cx, cz)
                if not c: continue
                root = c[1]; lst = root.get("block_entities")
                if not lst: continue
                keep = []
                for be in lst[1][1]:
                    bx, by, bz = be["x"][1], be["y"][1], be["z"][1]
                    if x1 <= bx <= x2 and z1 <= bz <= z2 and not (protected and protected(bx, bz)):
                        fl = floor(bx, bz) if callable(floor) else floor
                        if fl is not None and by > fl: n += 1; continue
                    keep.append(be)
                if len(keep) != len(lst[1][1]):
                    root["block_entities"] = (lst[0], (lst[1][0], keep)); self.dirty.add((cx, cz))
        return n

    def save(self, dry=False):
        touched = collections.defaultdict(list)
        for (cx, cz) in self.dirty:
            name, root, ch = self.chunks[(cx, cz)]
            ch.commit()
            touched[region_of(cx, cz)].append((cx, cz))
        files = []
        for (rx, rz), cl in touched.items():
            reg = self._region(rx, rz)
            for (cx, cz) in cl:
                name, root, ch = self.chunks[(cx, cz)]
                ts, comp, raw = reg[slot_of(cx, cz)]
                reg[slot_of(cx, cz)] = (ts, comp, W().root(name, root))
            p = self.path / "region" / f"r.{rx}.{rz}.mca"
            if not dry: write_region(p, reg)
            files.append(p.name)
        return sorted(files), len(self.dirty)


# ----------------------------------------------------------------------------- geometry helpers

def rect_targets(plan):
    for r in plan:
        x1, z1, x2, z2 = r["chunks"]; dx, dz = r["offset"]
        yield [x1 + dx, z1 + dz, x2 + dx, z2 + dz]


def edge_columns(rect):
    """(inside_x, inside_z, outward_dx, outward_dz) for every block column on the outer edge of a chunk rect."""
    cx1, cz1, cx2, cz2 = rect
    yield from block_edge_columns(cx1 * 16, cz1 * 16, cx2 * 16 + 15, cz2 * 16 + 15)


def block_edge_columns(x1, z1, x2, z2):
    for x in range(x1, x2 + 1):
        yield x, z1, 0, -1
        yield x, z2, 0, 1
    for z in range(z1, z2 + 1):
        yield x1, z, -1, 0
        yield x2, z, 1, 0


def inside_any(x, z, rects):
    return any(r[0] * 16 <= x <= r[2] * 16 + 15 and r[1] * 16 <= z <= r[3] * 16 + 15 for r in rects)


def column_is_built(world, x, z):
    """True when something non-terrain stands on this column (a building, road, or player block)."""
    y, b = world.top(x, z)
    return b is not None and b not in NATURAL


def water_top(world, x, z):
    """Water surface height at the column if its top block is water, else None."""
    y, b = world.top(x, z)
    return y if b == WATER else None


# ----------------------------------------------------------------------------- column edit

def smooth_column(world, x, z, want, water=None):
    """Move the ground at (x,z) to height want. Never touches built columns.
    Water: a pond on the column keeps its own surface; water = a lake level at the edge being
    ramped to. Ground raised above a water surface removes that water; ground left below one is
    flooded up to it, so lakes keep their basins instead of pouring into a trench."""
    g = world.ground(x, z)
    if g is None or want == g: return False
    if column_is_built(world, x, z): return False
    wt = water_top(world, x, z)
    level = max([v for v in (wt, water) if v is not None], default=None)
    if want > g:
        for y in range(g + 1, want + 1):
            world.set(x, y, z, FILL if y < want else TOP)
        world.clear_column(x, z, want + 1, max(want + 1, wt or 0))   # plants, or water now below ground
    else:
        world.clear_column(x, z, want + 1, g)
        world.set(x, want, z, TOP)
    if level is not None and want < level:
        for y in range(want + 1, level + 1):
            world.set(x, y, z, WATER)
    return True


def ramp_from_edges(world, edges, inside, height_at_edge, water_at_edge):
    """Plan ramps outward from edge columns. edges yields (x, z, dx, dz); inside(x, z) says whether a
    column is part of the protected interior; height_at_edge/water_at_edge give the edge height/lake."""
    wants = {}
    for x, z, dx, dz in edges:
        if inside(x + dx, z + dz): continue
        gi = height_at_edge(x, z)
        go = world.ground(x + dx, z + dz)
        if gi is None or go is None: continue
        wl = water_at_edge(x, z)
        width = int(max(BLEND_MIN, min(BLEND_MAX, abs(go - gi) * SLOPE)))
        for k in range(1, width + 1):
            ox, oz = x + dx * k, z + dz * k
            if inside(ox, oz): break
            g = world.ground(ox, oz)
            if g is None: break
            frac = 1.0 - (k - 1) / width
            want = round(g + (gi - g) * frac)
            key = (ox, oz)
            if key not in wants or abs(want - g) > abs(wants[key][0] - g):
                wants[key] = (want, wl)
    return wants


# ----------------------------------------------------------------------------- commands

def cmd_gaps(world, plan):
    rects = list(rect_targets(plan))
    hist = collections.Counter(); missing = 0; n = 0; worst = []; per_rect = []; built = 0
    for r in rects:
        rn = 0; rbig = 0
        for x, z, dx, dz in edge_columns(r):
            if inside_any(x + dx, z + dz, rects): continue
            gi = world.ground(x, z); go = world.ground(x + dx, z + dz)
            if gi is None or go is None: missing += 1; continue
            d = go - gi; n += 1; rn += 1; hist[max(-40, min(40, d))] += 1
            if abs(d) >= 3:
                rbig += 1
                if column_is_built(world, x + dx, z + dz) or column_is_built(world, x, z): built += 1
            if abs(d) >= 8: worst.append((abs(d), x, z, gi, go))
        per_rect.append((r, rn, rbig))
    print(f"edge columns compared: {n}; neighbour missing (not generated): {missing}")
    print("gap histogram (generated minus transplanted, blocks):")
    for k in sorted(hist): print(f"  {k:+4d}: {hist[k]}")
    big = sum(v for k, v in hist.items() if abs(k) >= 3)
    print(f"columns with |gap| >= 3: {big} ({100 * big / max(n, 1):.1f}%), of which at a built column: {built}")
    print("per rectangle (chunks, edge columns, |gap|>=3):")
    for r, rn, rbig in per_rect: print(f"  {r}  {rn:6d}  {rbig:6d}")
    worst.sort(reverse=True)
    for w in worst[:15]: print("  worst", w)


def cmd_smooth(world, plan, dry):
    rects = list(rect_targets(plan))
    def edges():
        for r in rects: yield from edge_columns(r)
    wants = ramp_from_edges(world, edges(), lambda x, z: inside_any(x, z, rects),
                            world.ground, lambda x, z: water_top(world, x, z))
    changed = sum(1 for (x, z), (want, wl) in wants.items() if smooth_column(world, x, z, want, wl))
    files, chunks = world.save(dry)
    print(f"columns planned: {len(wants)}; adjusted: {changed}; chunks changed: {chunks}; region files: {len(files)}")
    print("DRY RUN - nothing written" if dry else "written")


def cmd_ramp(world, x1, z1, x2, z2, y, dry, label=""):
    def inside(x, z): return x1 <= x <= x2 and z1 <= z <= z2
    wants = ramp_from_edges(world, block_edge_columns(x1, z1, x2, z2), inside, lambda x, z: y, lambda x, z: None)
    changed = sum(1 for (x, z), (want, wl) in wants.items() if smooth_column(world, x, z, want, wl))
    files, chunks = world.save(dry)
    print(f"ramp {label} around x {x1}..{x2} z {z1}..{z2} at y={y}: planned {len(wants)}, adjusted {changed}, chunks {chunks}, files {len(files)}")
    print("DRY RUN - nothing written" if dry else "written")


def draw_outline(world, x1, z1, x2, z2, protected, y=None):
    """Border ring on the surface (fixed y, or each column's own ground) plus 3-high corner posts."""
    def surf(x, z): return y if y is not None else world.ground(x, z)
    for x in range(x1, x2 + 1):
        for z in (z1, z2):
            s = surf(x, z)
            if s is not None and not protected(x, z): world.set(x, s, z, BORDER)
    for z in range(z1, z2 + 1):
        for x in (x1, x2):
            s = surf(x, z)
            if s is not None and not protected(x, z): world.set(x, s, z, BORDER)
    for (x, z) in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        s = surf(x, z)
        if s is not None and not protected(x, z):
            for yy in range(s + 1, s + 4): world.set(x, yy, z, POST)


def cmd_pad(world, x1, z1, x2, z2, y, protect, label, clear_only, dry, outline=True):
    x1, x2 = sorted((x1, x2)); z1, z2 = sorted((z1, z2))

    def protected(x, z):
        return any(p[0] <= x <= p[2] and p[1] <= z <= p[3] for p in protect)

    if clear_only:
        # Reference surface per 16x16 cell = median ground of the cell's NATURAL columns (buildings sit
        # on basements far below the street, so a built column's own ground would leave a pit).
        cell = {}
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                hs = []
                for x in range(cx * 16, cx * 16 + 16, 2):
                    for z in range(cz * 16, cz * 16 + 16, 2):
                        if x1 <= x <= x2 and z1 <= z <= z2 and not protected(x, z) and not column_is_built(world, x, z):
                            g = world.ground(x, z)
                            if g is not None: hs.append(g)
                if hs: cell[(cx, cz)] = int(statistics.median(hs))
        def surface(x, z):
            k = (x >> 4, z >> 4)
            if k in cell: return cell[k]
            near = [v for (a, b), v in cell.items() if abs(a - k[0]) <= 2 and abs(b - k[1]) <= 2]
            return int(statistics.median(near)) if near else None
        cols = 0; rebuilt = 0
        floors = {}
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                if protected(x, z): continue
                g = world.ground(x, z)
                if g is None: continue
                wt = water_top(world, x, z)
                if column_is_built(world, x, z):
                    s = surface(x, z)
                    if s is None: s = g
                    world.clear_column(x, z, min(g, s) + 1)
                    if g < s:
                        for yy in range(g + 1, s + 1): world.set(x, yy, z, FILL if yy < s else TOP)
                    else:
                        world.set(x, s, z, TOP)
                    floors[(x, z)] = s; rebuilt += 1
                else:
                    world.clear_column(x, z, g + 1)
                    floors[(x, z)] = g
                    if wt is not None:                       # a pond stays a pond
                        for yy in range(g + 1, wt + 1): world.set(x, yy, z, WATER)
                cols += 1
        dropped = world.drop_block_entities(x1, z1, x2, z2, lambda x, z: floors.get((x, z)), protected)
        print(f"built columns rebuilt to the local surface: {rebuilt}")
        files, chunks = world.save(dry)
        print(f"clear {label} x {x1}..{x2} z {z1}..{z2}: {cols} columns cleared to ground, {dropped} block entities dropped, {chunks} chunks, files {files}")
        print("DRY RUN - nothing written" if dry else "written")
        return None

    samples = [(x, z) for x in range(x1, x2 + 1, 4) for z in range(z1, z2 + 1, 4) if not protected(x, z)]
    if y is None:
        hs = [h for h in (world.ground(x, z) for x, z in samples) if h is not None]
        y = int(statistics.median(hs)); print(f"pad height from median ground: {y} (range {min(hs)}..{max(hs)})")
    # never sit below water the pad or its ramps would touch
    wts = [w for w in (water_top(world, x, z) for x, z in samples) if w is not None]
    ring = [(x, z) for x, z, dx, dz in block_edge_columns(x1 - BLEND_MAX // 2, z1 - BLEND_MAX // 2, x2 + BLEND_MAX // 2, z2 + BLEND_MAX // 2)]
    wts += [w for w in (water_top(world, x, z) for x, z in ring[::4]) if w is not None]
    if wts and y <= max(wts):
        print(f"pad raised from {y} to {max(wts) + 1} to clear water at {max(wts)}"); y = max(wts) + 1
    cols = 0
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if protected(x, z): continue
            g = world.ground(x, z)
            if g is None: continue
            world.clear_column(x, z, y + 1)
            if g < y:
                for yy in range(g + 1, y + 1): world.set(x, yy, z, FILL if yy < y else TOP)
            else:
                world.set(x, y, z, TOP)
            cols += 1
    dropped = world.drop_block_entities(x1, z1, x2, z2, y, protected)
    if outline: draw_outline(world, x1, z1, x2, z2, protected, y)
    files, chunks = world.save(dry)
    print(f"pad {label} x {x1}..{x2} z {z1}..{z2} at y={y}: {cols} columns levelled, {dropped} block entities dropped, {chunks} chunks, files {files}")
    print("DRY RUN - nothing written" if dry else "written")
    return y


def cmd_outline(world, x1, z1, x2, z2, label, dry):
    draw_outline(world, x1, z1, x2, z2, lambda x, z: False)
    files, chunks = world.save(dry)
    print(f"outline {label} x {x1}..{x2} z {z1}..{z2} on the ground: {chunks} chunks, files {files}")
    print("DRY RUN - nothing written" if dry else "written")


def main(argv):
    cmd = argv[1]; world = World(argv[2]); dry = "--dry-run" in argv
    label = argv[argv.index("--label") + 1] if "--label" in argv else ""
    if cmd == "gaps":
        cmd_gaps(world, json.load(open(argv[3])))
    elif cmd == "smooth":
        cmd_smooth(world, json.load(open(argv[3])), dry)
    elif cmd == "ramp":
        x1, z1, x2, z2 = map(int, argv[3:7]); y = int(argv[argv.index("--y") + 1])
        cmd_ramp(world, x1, z1, x2, z2, y, dry, label)
    elif cmd == "outline":
        x1, z1, x2, z2 = map(int, argv[3:7])
        cmd_outline(world, x1, z1, x2, z2, label, dry)
    elif cmd == "pad":
        x1, z1, x2, z2 = map(int, argv[3:7]); y = None; protect = []
        a = argv[7:]
        while a:
            if a[0] == "--y": y = int(a[1]); a = a[2:]
            elif a[0] == "--protect": protect.append(list(map(int, a[1:5]))); a = a[5:]
            else: a = a[1:]
        cmd_pad(world, x1, z1, x2, z2, y, protect, label, "--clear-only" in argv, dry, outline="--no-outline" not in argv)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
