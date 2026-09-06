"""Close a break in an existing road, in that road's own material and width (v8 road review, step 1).

The v8 cell's roads are in 21 separate pieces; a spanning tree over them (tools/roadreview/) says 792 m of road makes
them one network, and most of the cuts are 6-44 m of plain grass across a paved carriageway. Laying the Skadowsky
vocabulary across those would leave a visible splice, so each patch is built from what is already at its two ends: the
surface materials found within `--sample` blocks of each end become the carriageway mix, and the width is measured
across the road rather than assumed.

usage: roadpatch.py <world dir> <links.json> [--sample 24] [--max-stamp 80] [--dry-run] [--only name,name]
links.json: [{"d": 20.0, "a": "C1", "b": "C14", "pa": [x, z], "pb": [x, z]}, ...]  (tools/roadreview/mstlinks.json)
Each link is snapped to the nearest real road column at both ends. A gap up to `--max-stamp` is stamped straight;
a longer one is routed with roads.py (meander on) so it follows the ground. Every patch writes a road mask.
"""
import sys, json, math, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import roads
from roads import densify, lay_column, shoulder_column, surface_built, save_road_mask, ROAD, KERB, LINE
from terrain import World, LIQUID, AIR

ROADK = ("cobblestone", "stone", "andesite", "gravel", "concrete", "smooth_stone", "coarse_dirt", "blackstone",
         "terracotta", "hempcrete", "dirt_path", "asphalt", "brick")
SKIP = ("grass", "dirt_block")
KERBS = ("andesite_wall", "stone_brick_wall", "cobblestone_wall")
# a kerb, a step or a half block is not a carriageway material, and terracotta is the wasteland's own ground
NOT_SURFACE = ("_wall", "_slab", "_stairs", "_fence", "_pane", "_button", "_pressure_plate", "terracotta")


def is_road(name):
    if name is None or name in LIQUID: return False
    k = name.split(":")[-1]
    if any(t in k for t in SKIP): return False
    return any(t in k for t in ROADK)


def is_surface(name):
    """A material the carriageway itself can be made of: a full block, not a kerb or a step."""
    return is_road(name) and not any(t in name for t in NOT_SURFACE)


def snap(world, x, z, r=20):
    """The nearest column whose surface is a road material."""
    best = None
    for dz in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = dx * dx + dz * dz
            if d > r * r or (best and d >= best[0]): continue
            y, n = world.top(x + dx, z + dz)
            if is_road(n): best = (d, x + dx, z + dz, y)
    return best[1:] if best else None


def profile(world, x, z, r):
    """Material mix and kerb presence around a road end."""
    c = collections.Counter(); kerb = 0
    for dz in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dz * dz > r * r: continue
            y, n = world.top(x + dx, z + dz)
            if n is None: continue
            k = n.split(":")[-1]
            if any(t in k for t in KERBS): kerb += 1
            if is_surface(n): c[n] += 1
    return c, kerb


def width_across(world, x, z, ux, uz, lim=14):
    """Road width measured perpendicular to the link direction."""
    px, pz = -uz, ux; n = 1
    for s in (1, -1):
        for k in range(1, lim + 1):
            if not is_road(world.top(round(x + px * k * s), round(z + pz * k * s))[1]): break
            n += 1
    return n


def style_from(counts, kerb):
    """A roads.py style dict weighted by what is actually on the ground at the break."""
    top = [(n, c) for n, c in counts.most_common(4) if c >= counts.most_common(1)[0][1] * 0.12] or [("minecraft:stone", 1)]
    tot = sum(c for _, c in top)
    mix = [(n, max(int(round(100 * c / tot)), 1)) for n, c in top]
    return {"road": mix, "kerb": [("minecraft:andesite_wall", 100)] if kerb >= 8 else None,
            "line": None, "fill": "minecraft:dirt"}


def surface_y(world, x, z):
    y, n = world.top(x, z)
    if is_road(n): return y
    return world.ground(x, z)


def stamp(world, name, pts, hs, half, dry):
    cols = {}; n = 0
    for k, ((x, z), y) in enumerate(zip(pts, hs)):
        h = roads.half_at(k, len(pts), half)
        for dx in range(-h, h + 1):
            for dz in range(-h, h + 1):
                if dx * dx + dz * dz > h * h + h: continue
                kind = KERB if max(abs(dx), abs(dz)) == h else ROAD
                prev = cols.get((x + dx, z + dz))
                if prev is None or (prev[1] == KERB and kind != KERB): cols[(x + dx, z + dz)] = (y, kind)
    for (px, pz), (y, kind) in cols.items():
        if lay_column(world, px, pz, y, kind): n += 1
    sh = {}
    for i, ((x, z), y) in enumerate(zip(pts, hs)):
        h = roads.half_at(i, len(pts), half)
        for k in range(1, 7):
            for dx, dz in ((h + k, 0), (-h - k, 0), (0, h + k), (0, -h - k)):
                if (x + dx, z + dz) in cols or (x + dx, z + dz) in sh: continue
                sh[(x + dx, z + dz)] = (y, k)
    for (px, pz), (y, k) in sh.items():
        g = world.ground(px, pz)
        if g is None or surface_built(world, px, pz): continue
        shoulder_column(world, px, pz, y + (g - y) * k // 7, g)
    if not dry: save_road_mask(name, list(cols))
    return n


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world = World(Path(a[1])); links = json.load(open(a[2])); dry = "--dry-run" in a
    r = int(a[a.index("--sample") + 1]) if "--sample" in a else 24
    mx = int(a[a.index("--max-stamp") + 1]) if "--max-stamp" in a else 80
    mw = int(a[a.index("--max-width") + 1]) if "--max-width" in a else 11
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    total = 0; done = []
    for L in sorted(links, key=lambda L: L["d"]):
        name = f"patch_{L['a']}_{L['b']}"
        if only and name not in only: continue
        sa, sb = snap(world, *L["pa"]), snap(world, *L["pb"])
        if sa is None or sb is None:
            print(f"  {name}: no road within 20 m of {L['pa'] if sa is None else L['pb']}, skipped"); continue
        (ax, az, ay), (bx, bz, by) = sa, sb
        dist = math.hypot(bx - ax, bz - az)
        if dist < 2: print(f"  {name}: ends already touch, skipped"); continue
        ux, uz = (bx - ax) / dist, (bz - az) / dist
        ca, ka = profile(world, ax, az, r); cb, kb = profile(world, bx, bz, r)
        wa = width_across(world, ax, az, ux, uz); wb = width_across(world, bx, bz, ux, uz)
        width = min(max(min(wa, wb), 5), mw)          # a measurement across a plaza is not a road width
        roads._style = style_from(ca + cb, ka + kb)
        straight = densify([[ax, az], [bx, bz]])
        wet_straight = sum(1 for (x, z) in straight if world.top(x, z)[1] in LIQUID)
        if dist <= mx and not wet_straight:            # a straight causeway would dam whatever it crosses
            pts = straight
            hs = [round(ay + (by - ay) * k / (len(pts) - 1)) for k in range(len(pts))]
            # do not bury a rise between the two ends: follow the ground where it is higher
            hs = [max(h, (surface_y(world, x, z) or h)) if abs((surface_y(world, x, z) or h) - h) > 2 else h
                  for h, (x, z) in zip(hs, pts)]
            how = "stamped"
        else:
            roads._meander = 0.4
            seg, st = roads.route(world, (ax, az), (bx, bz))
            if seg is None: print(f"  {name}: no route, skipped"); continue
            pts = densify(seg)
            hs = roads.target_heights(world, pts)
            how = f"routed {st['metres']} m"
        wet = sum(1 for (x, z) in pts if world.top(x, z)[1] in LIQUID)
        n = stamp(world, name, pts, hs, width // 2, dry)
        mix = ", ".join(f"{m.split(':')[-1]} {w}%" for m, w in roads._style["road"])
        print(f"  {name:16s} ({ax},{az}) -> ({bx},{bz})  {dist:5.0f} m  width {width:2d}  {how:14s} {n:5d} columns   {mix}"
              + ("  + andesite kerbs" if roads._style["kerb"] else "") + (f"   WATER on {wet} m of the line" if wet else ""))
        total += n; done.append(name)
    files, chunks = world.save(dry)
    print(f"{len(done)} patches, {total} columns, {chunks} chunks{' (dry)' if dry else ''}")


if __name__ == "__main__":
    main(sys.argv)
