#!/usr/bin/env python3
"""The Line — a sparsely populated rural corridor that walks the players into the residential block.

Six small buildings a few hundred metres apart along an old power line, from the camp's south edge
past the freed substation pad to the block's west gate: a farmstead, a pump house on the water, two
fenced substations, the line workers' depot, and the switching station at the block's edge. Lattice
pylons every 48 m between them mark the way; each building has a chest on a site loot table and one
quest object. Written as sparse structure templates and one placement function, like the ruins.

    python theline.py <world dir>     -> structures/line_*.nbt, functions/theline.mcfunction,
                                         buildmap/theline_v7.json (every placement with its ground height)

Corridor waypoints are hand-set (WAYPOINTS); every building and pylon snaps to the ground read from
the world, skips water, and refuses a chunk with a Lost Cities fingerprint (the corridor is meant to
be empty ground). Blocks: vanilla, the IE ids tower.py verified, Doomsday Decoration props.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from camp_ruins import Ground, write_template, IE, SHEET, SCAF, CONC, AIR, GRAVEL, COBBLE, IRON_BARS, CHAIN, BARREL, CHEST, STONE_BRICK, CRACKED, SLAB, WALL, FENCE, GLASS_PANE, LANTERN, IRON_TRAP, DEEPSLATE_TILE, DD, VAN_F, VAN_B, OILTANK, WIREMESH, SANDBAG, CONE, YVAN_F, YVAN_B  # noqa: E402
from transplant import R, read_region_raw, region_of, slot_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATAPACK = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft"
STEEL_FENCE, TRANSFORMER, CAP, RELAY, BREAKER, CT, FLOOD, PIPE, PUMP, TANK = (IE + "steel_fence", IE + "transformer", IE + "capacitor_mv", IE + "connector_hv_relay",
    IE + "breaker_switch", IE + "current_transformer", IE + "floodlight", IE + "fluid_pipe", IE + "fluid_pump", IE + "storage_steel")
PLANKS, LOG, HAY, WHEAT, FARMLAND, DOOR, GLASS, BRICKS, TERRACOTTA, WATER = ("minecraft:spruce_planks", "minecraft:spruce_log", "minecraft:hay_block", "minecraft:wheat",
    "minecraft:farmland", "minecraft:spruce_door", "minecraft:glass", "minecraft:bricks", "minecraft:terracotta", "minecraft:water")
CITY_MARKS = {"immersiveengineering:hempcrete", "immersiveengineering:hempcrete_pillar", "superbwarfare:sandbag"}

# the corridor: camp south gate -> farmstead -> pump house -> substation A (the freed pad) -> depot -> substation B -> switching station -> the block
WAYPOINTS = [
    ("start", 40, 210),
    ("farmstead", 140, 430),
    ("pumphouse", 260, 720),
    ("substation_a", 300, 1480),
    ("depot", 640, 1330),
    ("substation_b", 960, 1410),
    ("switching", 1250, 1420),
    ("block_gate", 1328, 1430),
]
PYLON_STEP = 48


def piece(name):
    blocks = []

    def put(x, y, z, n, **p): blocks.append((x, y, z, n, p, None))

    def chest(x, y, z, table, facing="north"): blocks.append((x, y, z, CHEST, {"facing": facing}, table))

    def box(x0, y0, z0, x1, y1, z1, n, **p):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    put(x, y, z, n, **p)

    def shell(x0, y0, z0, x1, y1, z1, n, **p):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or z in (z0, z1): put(x, y, z, n, **p)

    if name == "pylon":                                     # 5 x 25 x 5 lattice
        for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
            box(x, 0, z, x, 0, z, CONC)
            for y in range(1, 23): put(x, y, z, SCAF)
        for y in (6, 12, 18, 22):
            for x in range(1, 4): put(x, y, 0, IRON_BARS); put(x, y, 4, IRON_BARS)
            for z in range(1, 4): put(0, y, z, IRON_BARS); put(4, y, z, IRON_BARS)
        for x in range(-1, 6): put(x, 23, 2, IRON_BARS)   # cross arm (x -1 becomes 0..6 after offset below)
        put(2, 24, 2, RELAY)
        blocks = [(x + 1, y, z, n, p, t) for x, y, z, n, p, t in blocks]  # shift so the arm fits: 7 wide
    elif name == "farmstead":                               # house 9x7, barn 11x9, a field; 30 x 6 x 14
        box(0, 0, 0, 8, 0, 6, COBBLE); shell(0, 1, 0, 8, 3, 6, PLANKS); box(0, 4, 0, 8, 4, 6, SLAB, type="bottom")
        put(4, 1, 6, AIR); put(4, 2, 6, AIR); put(2, 2, 6, GLASS); put(6, 2, 6, GLASS); put(0, 2, 3, GLASS); put(8, 2, 3, GLASS)
        chest(1, 1, 1, "gscraft:sites/line", "east"); put(7, 1, 1, BARREL, facing="up")
        box(13, 0, 0, 23, 0, 8, GRAVEL); shell(13, 1, 0, 23, 4, 8, LOG); box(13, 5, 0, 23, 5, 8, SLAB, type="bottom")
        for y in (1, 2, 3): put(18, y, 0, AIR); put(17, y, 0, AIR)
        put(14, 1, 7, HAY); put(15, 1, 7, HAY); put(14, 2, 7, HAY); put(22, 1, 1, HAY)
        chest(22, 1, 7, "gscraft:sites/line", "west")
        for x in range(0, 24):
            for z in (10, 13): put(x, 0, z, FENCE)
        for x in range(1, 23):
            for z in (11, 12): put(x, 0, z, FARMLAND, moisture="7"); put(x, 1, z, WHEAT, age="7")
        put(11, 0, 1, DD + "forklifttruck", facing="east")
    elif name == "pumphouse":                               # 7 x 5 x 7 brick hut with a pipe run to the water
        box(0, 0, 0, 6, 0, 6, DEEPSLATE_TILE); shell(0, 1, 0, 6, 3, 6, BRICKS); box(0, 4, 0, 6, 4, 6, SLAB, type="bottom")
        put(3, 1, 0, AIR); put(3, 2, 0, AIR); put(0, 2, 3, IRON_BARS); put(6, 2, 3, IRON_BARS)
        put(3, 1, 3, PUMP); put(3, 1, 4, PIPE); put(3, 1, 5, PIPE); put(3, 1, 6, PIPE); put(3, 1, 7, PIPE); put(3, 1, 8, PIPE)
        put(1, 1, 5, TANK); chest(5, 1, 5, "gscraft:sites/line", "west"); put(5, 1, 1, BARREL, facing="up")
    elif name == "substation":                              # 24 x 6 x 16 fenced yard, block house, four transformers
        box(0, 0, 0, 23, 0, 15, GRAVEL)
        for x in range(24): put(x, 1, 0, STEEL_FENCE); put(x, 1, 15, STEEL_FENCE)
        for z in range(1, 15): put(0, 1, z, STEEL_FENCE); put(23, 1, z, STEEL_FENCE)
        put(11, 1, 0, AIR); put(12, 1, 0, AIR)
        for (x, z) in ((5, 5), (9, 5), (5, 10), (9, 10)):
            box(x - 1, 0, z - 1, x + 1, 0, z + 1, CONC); put(x, 1, z, TRANSFORMER); put(x, 2, z, RELAY)
        put(14, 1, 5, CAP); put(14, 1, 10, CAP); put(16, 1, 7, BREAKER); put(16, 1, 8, CT)
        box(18, 0, 3, 22, 0, 12, CONC); shell(18, 1, 3, 22, 3, 12, CONC); box(18, 4, 3, 22, 4, 12, SHEET)
        put(18, 1, 7, AIR); put(18, 2, 7, AIR); put(20, 2, 3, GLASS_PANE); put(20, 2, 12, GLASS_PANE)
        chest(21, 1, 4, "gscraft:sites/line", "north"); put(21, 1, 11, BARREL, facing="up"); put(19, 4, 7, FLOOD)
        put(2, 1, 13, CONE); put(3, 1, 2, WIREMESH, facing="north")
    elif name == "depot":                                   # 14 x 6 x 10 line workers' garage with a van and drums
        box(0, 0, 0, 13, 0, 9, CONC); shell(0, 1, 0, 13, 4, 9, SHEET); box(0, 5, 0, 13, 5, 9, SHEET)
        for x in range(4, 10):
            for y in (1, 2, 3): put(x, y, 9, AIR)
        put(0, 2, 4, GLASS_PANE); put(13, 2, 4, GLASS_PANE); put(6, 5, 4, FLOOD)
        put(5, 1, 4, VAN_F, facing="south"); put(5, 1, 5, VAN_B, facing="south")
        put(9, 1, 3, YVAN_F, facing="south"); put(9, 1, 4, YVAN_B, facing="south")
        put(1, 1, 1, OILTANK, facing="east"); put(1, 1, 2, OILTANK, facing="east"); put(12, 1, 1, TANK)
        chest(12, 1, 8, "gscraft:sites/line", "west"); chest(1, 1, 8, "gscraft:sites/line", "east")
        put(2, 0, 11, SANDBAG, facing="south"); put(11, 0, 11, SANDBAG, facing="south")
    elif name == "switching":                               # 16 x 7 x 12 concrete hall with breakers, and a checkpoint at the door
        box(0, 0, 0, 15, 0, 11, CONC); shell(0, 1, 0, 15, 5, 11, CONC); box(0, 6, 0, 15, 6, 11, SHEET)
        put(7, 1, 0, AIR); put(7, 2, 0, AIR); put(8, 1, 0, AIR); put(8, 2, 0, AIR)
        for x in (3, 12): put(x, 3, 0, GLASS_PANE); put(x, 3, 11, GLASS_PANE)
        for x in range(2, 14, 2): put(x, 1, 3, BREAKER); put(x, 1, 8, CT)
        put(7, 1, 5, TRANSFORMER); put(8, 1, 5, TRANSFORMER); put(7, 2, 5, RELAY); put(8, 2, 5, RELAY)
        put(7, 5, 5, FLOOD); put(3, 6, 5, LANTERN, hanging="false"); put(12, 6, 5, LANTERN, hanging="false")
        chest(14, 1, 10, "gscraft:sites/line", "north"); chest(1, 1, 10, "gscraft:sites/line", "north")
        for x in range(4, 12): put(x, 0, -3 + 3, SANDBAG, facing="north") if False else None
        for x in range(4, 12): put(x, 1, 0, AIR) if x in (7, 8) else None
        for x in (4, 5, 10, 11): put(x, 0, 0, SANDBAG, facing="north")
        put(6, 0, 0, WIREMESH, facing="north"); put(9, 0, 0, WIREMESH, facing="north"); put(2, 1, 0, CONE); put(13, 1, 0, CONE)
    return [b for b in blocks if b is not None]


PIECES = ["pylon", "farmstead", "pumphouse", "substation", "depot", "switching"]
BUILDING_OF = {"farmstead": "farmstead", "pumphouse": "pumphouse", "substation_a": "substation", "depot": "depot", "substation_b": "substation", "switching": "switching"}


class World(Ground):
    def is_city(self, x, z):
        c = self.chunk(x >> 4, z >> 4)
        if c is None: return False
        names = set()
        for sec in c.root.get("sections", (9, (10, [])))[1][1]:
            bs = sec.get("block_states")
            if bs:
                names |= {p["Name"][1] for p in bs[1]["palette"][1][1]}
        return bool(names & CITY_MARKS)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    w = World(Path(argv[1]))
    sizes = {}
    for name in PIECES:
        size, n = write_template(piece(name), DATAPACK / "structures" / f"line_{name}.nbt")
        sizes[name] = size; print(f"line_{name:11} {n:4} blocks  size {size}")
    lines, placed, skipped = [], [], []

    NATURAL = ("grass_block", "dirt", "coarse_dirt", "podzol", "sand", "red_sand", "gravel", "stone", "terracotta", "sandstone",
               "mud", "clay", "moss_block", "rooted_dirt", "snow_block", "packed_mud", "deepslate", "smooth_stone_slab")

    def dry(x, z):
        """Natural, dry, non-city ground: a building goes on terrain, never on top of something built."""
        y, top = w.top(x, z)
        if y is None or top is None or "water" in top or "ice" in top: return False
        if not any(top.endswith(n) for n in NATURAL): return False
        return not w.is_city(x, z)

    def find_dry(x, z, radius=160, step=16):
        """Nearest dry, non-city ground to (x, z), searched on a widening square."""
        if dry(x, z): return x, z
        for r in range(step, radius + 1, step):
            ring_pts = [(x + dx, z + dz) for dx in range(-r, r + 1, step) for dz in (-r, r)] +                        [(x + dx, z + dz) for dz in range(-r, r + 1, step) for dx in (-r, r)]
            ring_pts.sort(key=lambda q: math.hypot(q[0] - x, q[1] - z))
            for q in ring_pts:
                if dry(*q): return q
        return None

    def water_fraction(a, b, samples=24):
        wet = 0
        for k in range(samples + 1):
            x = round(a[0] + (b[0] - a[0]) * k / samples); z = round(a[1] + (b[1] - a[1]) * k / samples)
            y, top = w.top(x, z)
            wet += (top is None) or ("water" in top) or ("ice" in top)
        return wet / (samples + 1)

    def route(a, b):
        """Straight if dry enough; otherwise the best single via-point off the perpendicular."""
        best = ([a, b], water_fraction(a, b))
        if best[1] <= 0.08: return best[0]
        dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz) or 1
        nx, nz = -dz / L, dx / L
        for frac in (0.35, 0.5, 0.65):
            for off in (-700, -500, -350, -200, 200, 350, 500, 700):
                m = (round(a[0] + dx * frac + nx * off), round(a[1] + dz * frac + nz * off))
                if not dry(*m): continue
                f = (water_fraction(a, m) + water_fraction(m, b)) / 2
                if f < best[1]: best = ([a, m, b], f)
        return best[0]

    def place(kind, x, z, rot="none"):
        y, top = w.top(x, z)
        if not dry(x, z):
            skipped.append((kind, x, z, "water" if top and "water" in top else "city" if top else "no chunk")); return
        lines.append(f"place template gscraft:line_{kind} {x} {y + 1} {z} {rot} none")
        placed.append({"piece": kind, "x": x, "y": y + 1, "z": z, "rotation": rot, "on": top})

    # buildings first, each moved to the nearest dry ground; then the pylon line through the final points
    points = []
    for name, x, z in WAYPOINTS:
        if name in BUILDING_OF:
            q = find_dry(x, z)
            if q is None:
                skipped.append((name, x, z, "no dry ground within 160 m")); continue
            if q != (x, z): print(f"   {name}: moved {x},{z} -> {q[0]},{q[1]} for dry ground")
            place(BUILDING_OF[name], q[0], q[1]); points.append((name, q[0], q[1]))
        else:
            points.append((name, x, z))
    legs = []
    for (n0, x0, z0), (n1, x1, z1) in zip(points, points[1:]):
        legs.append((n0, n1, route((x0, z0), (x1, z1))))
    for n0, n1, poly in legs:
        if len(poly) > 2: print(f"   leg {n0} -> {n1} detours via {poly[1]}")
        for a, b in zip(poly, poly[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1]); steps = max(1, int(d // PYLON_STEP))
            for k in range(1, steps):
                px, pz = round(a[0] + (b[0] - a[0]) * k / steps), round(a[1] + (b[1] - a[1]) * k / steps)
                place("pylon", px - 3, pz - 2)
    WAYPOINTS_FINAL = [(n, x, z) for n, x, z in points]
    fn = DATAPACK / "functions" / "theline.mcfunction"
    fn.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "buildmap" / "theline_v7.json").write_text(json.dumps({"waypoints": WAYPOINTS_FINAL, "legs": [[n0, n1, poly] for n0, n1, poly in legs], "placed": placed, "skipped": skipped}, indent=1), encoding="utf-8")
    n_b = sum(p["piece"] != "pylon" for p in placed); n_p = sum(p["piece"] == "pylon" for p in placed)
    print(f"\n{n_b} buildings, {n_p} pylons placed; {len(skipped)} skipped -> {fn.name}")
    for p in placed:
        if p["piece"] != "pylon": print(f"   {p['piece']:11} ({p['x']:5}, {p['y']:3}, {p['z']:5}) on {p['on'].split(':')[-1]}")
    for s in skipped[:12]: print("   skipped", s)


if __name__ == "__main__":
    main(sys.argv)
