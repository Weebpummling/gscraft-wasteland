#!/usr/bin/env python3
"""The camp's own ruins: small wrecks and containers scattered inside the starting area so Act I's
introductions have something to loot within 300 m of spawn (the v6 build cleared the area to natural
ground). Eight ruin pieces as sparse structure templates, placed by one datapack function at ground
level, each with one or two chests bound to a gscraft loot table.

    python camp_ruins.py <world dir>     write templates, loot tables, the placement function and
                                          tools/camp_ruins.json; ground heights are read from <world dir>

Outputs (all under build/datapacks/gscraft/data/gscraft/):
  structures/ruin_<piece>.nbt        the eight pieces
  functions/camp_ruins.mcfunction    24 `place template` lines at the scattered positions
  loot_tables/ruins/<table>.json     hardware / electrical / medical / mixed (gscraft items; live in Phase C)
Keep-out: every NPC pad (tools/pads_camp.json + 8), the tower compound, the crater, the spawn
plaza, and 12 blocks either side of the spine's line to the gate. v2 (2026-09-03) builds the wrecks from
Doomsday Decoration's car segments, sandbags, oil drums, wire mesh and cones; `camp_ruins_clear`
removes the v1 blocks at the recorded placements first.
"""
import gzip
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import W, R, T_BYTE, T_INT, T_LONG, T_STRING, T_LIST, T_COMPOUND, read_region_raw, region_of, slot_of  # noqa: E402
from anvil import Chunk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATAPACK = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft"
DATA_VERSION = 3465
CAMP = (-176, -176, 207, 207)
KEEP_OUT = [(64 - 8, -144 - 8, 191 + 8, -17 + 8),   # tower compound
            (-24, -24, 55, 55),                      # crater + spawn plaza
            ]
SEED = 2404991234066556536

IE = "immersiveengineering:"
SHEET, SCAF, CONC = IE + "sheetmetal_steel", IE + "steel_scaffolding_standard", IE + "concrete"
AIR, GRAVEL, COBBLE, MOSSY, IRON_BARS, CHAIN, BARREL, CHEST = ("minecraft:air", "minecraft:gravel", "minecraft:cobblestone",
    "minecraft:mossy_cobblestone", "minecraft:iron_bars", "minecraft:chain", "minecraft:barrel", "minecraft:chest")
STONE_BRICK, CRACKED, SLAB, WALL, WOOL, FENCE, GLASS_PANE, LANTERN = ("minecraft:stone_bricks", "minecraft:cracked_stone_bricks",
    "minecraft:smooth_stone_slab", "minecraft:cobblestone_wall", "minecraft:gray_wool", "minecraft:spruce_fence",
    "minecraft:gray_stained_glass_pane", "minecraft:soul_lantern")
IRON_TRAP, IRON_BLOCK, BLACK_CONC, DEEPSLATE_TILE = "minecraft:iron_trapdoor", "minecraft:iron_block", "minecraft:black_concrete", "minecraft:deepslate_tiles"

# Loot tables. The gscraft items arrive in Phase C; until then every entry carries a vanilla
# stand-in so the datapack loads clean, and the intended id sits beside it for the swap.
LOOT = {
    "hardware": [("minecraft:iron_nugget", "gscraft:bolt", 2, 6), ("minecraft:iron_nugget", "gscraft:nut", 2, 6),
                 ("minecraft:iron_nugget", "gscraft:screw", 2, 6), ("minecraft:iron_nugget", "gscraft:nail", 2, 8),
                 ("minecraft:iron_ingot", "gscraft:metal_scrap", 1, 4), ("minecraft:string", "gscraft:duct_tape", 1, 2),
                 ("minecraft:iron_pickaxe", "gscraft:wrench", 0, 1)],
    "electrical": [("minecraft:copper_ingot", "gscraft:wire_spool", 1, 3), ("minecraft:lead", "gscraft:power_cord", 0, 2),
                   ("minecraft:glowstone_dust", "gscraft:light_bulb", 0, 2), ("minecraft:redstone", "gscraft:capacitor", 1, 3),
                   ("minecraft:comparator", "gscraft:circuit_board", 0, 1), ("minecraft:jukebox", "gscraft:broken_radio", 0, 1)],
    "medical": [("minecraft:paper", "gscraft:bandage", 2, 4), ("minecraft:sugar", "gscraft:painkillers", 1, 2),
                ("minecraft:honey_bottle", "gscraft:antiseptic", 0, 1), ("minecraft:glass_bottle", "gscraft:syringe", 0, 2),
                ("minecraft:charcoal", "gscraft:water_filter", 0, 1)],
    "mixed": [("minecraft:iron_ingot", "gscraft:metal_scrap", 1, 3), ("minecraft:string", "gscraft:duct_tape", 0, 2),
              ("minecraft:paper", "gscraft:bandage", 1, 2), ("minecraft:copper_ingot", "gscraft:wire_spool", 0, 2),
              ("minecraft:flint", "gscraft:spark_plug", 0, 1), ("minecraft:gunpowder", "minecraft:gunpowder", 1, 3)],
}


# ------------------------------------------------------------------ pieces
def piece_v1(name, table_a, table_b=None):
    blocks = []

    def put(x, y, z, n, **p):
        blocks.append((x, y, z, n, p, None))

    def chest(x, y, z, table, facing="north"):
        blocks.append((x, y, z, CHEST, {"facing": facing}, table))

    def box(x0, y0, z0, x1, y1, z1, n, **p):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    put(x, y, z, n, **p)

    if name == "car":                              # a burnt-out car, 7 x 3 x 4
        box(1, 0, 0, 5, 0, 3, SHEET); box(2, 1, 1, 4, 1, 2, SHEET)
        put(0, 0, 0, IRON_TRAP, half="bottom", facing="east", open="false"); put(6, 0, 3, IRON_TRAP, half="bottom", facing="west", open="false")
        put(1, 1, 0, GLASS_PANE); put(5, 1, 3, GLASS_PANE)
        chest(3, 1, 3, table_a, "south")
    elif name == "bus":                            # a bus on its side, 12 x 4 x 4
        box(0, 0, 0, 11, 2, 3, SHEET)
        for x in range(1, 11, 2):
            put(x, 1, 0, GLASS_PANE); put(x, 1, 3, GLASS_PANE)
        box(3, 1, 1, 8, 1, 2, AIR); box(3, 2, 1, 8, 2, 2, AIR)
        put(0, 1, 1, AIR); put(0, 1, 2, AIR)
        chest(8, 1, 1, table_a, "west"); chest(4, 1, 2, table_b or table_a, "east")
    elif name == "shed":                           # collapsed shed, 7 x 4 x 6
        box(0, 0, 0, 6, 0, 5, GRAVEL)
        for x in range(0, 7):
            for z in (0, 5):
                put(x, 1, z, CRACKED if (x + z) % 3 else STONE_BRICK)
        for z in range(1, 5):
            put(0, 1, z, STONE_BRICK); put(0, 2, z, CRACKED if z % 2 else AIR)
        box(1, 3, 1, 3, 3, 4, SLAB, type="bottom")
        put(6, 1, 2, AIR); put(6, 1, 3, AIR)
        chest(1, 1, 1, table_a, "east"); put(5, 1, 4, BARREL, facing="up")
    elif name == "containers":                     # a stack of shipping containers, 6 x 3 x 5
        box(0, 0, 0, 5, 1, 1, SHEET); box(0, 0, 3, 5, 1, 4, BLACK_CONC); box(0, 2, 1, 5, 3, 3, SHEET)
        put(0, 0, 0, AIR); put(0, 1, 0, AIR); put(5, 0, 4, AIR); put(5, 1, 4, AIR)
        chest(1, 0, 0, table_a, "west"); chest(4, 0, 4, table_b or table_a, "east")
    elif name == "drums":                          # fuel drums and a pump, 4 x 2 x 4
        for (x, z) in ((0, 0), (1, 0), (0, 1), (2, 2), (3, 3), (3, 1)):
            put(x, 0, z, BARREL, facing="up")
        put(1, 1, 0, BARREL, facing="up"); put(2, 0, 0, IRON_BLOCK); put(2, 1, 0, CHAIN, axis="y")
        chest(1, 0, 2, table_a, "south")
    elif name == "scrap":                          # a scrap heap, 5 x 2 x 5
        rng = random.Random(SEED ^ 0x5C)
        for x in range(5):
            for z in range(5):
                if rng.random() < 0.7:
                    put(x, 0, z, rng.choice((GRAVEL, COBBLE, MOSSY, IRON_BARS)))
        put(2, 1, 2, IRON_BARS); put(1, 1, 3, SCAF)
        chest(3, 0, 1, table_a, "north")
    elif name == "tent":                           # a camp tent, 5 x 3 x 5
        box(0, 0, 0, 4, 0, 4, GRAVEL)
        for z in range(5):
            put(0, 1, z, WOOL); put(4, 1, z, WOOL); put(1, 2, z, WOOL); put(3, 2, z, WOOL)
        put(2, 3, 0, FENCE); put(2, 3, 4, FENCE); put(2, 2, 1, LANTERN, hanging="false")
        put(2, 1, 0, AIR)
        chest(2, 1, 3, table_a, "north")
    elif name == "checkpoint":                     # a checkpoint of walls and a hut, 7 x 3 x 7
        for x in range(7):
            put(x, 0, 0, WALL); put(x, 0, 6, WALL)
        for z in range(1, 6):
            put(0, 0, z, WALL)
        box(4, 0, 2, 6, 0, 4, DEEPSLATE_TILE); box(4, 1, 2, 6, 2, 4, CONC); box(5, 1, 3, 5, 2, 3, AIR)
        put(4, 1, 3, AIR); put(4, 2, 3, AIR)
        put(6, 3, 3, LANTERN, hanging="false")
        chest(5, 1, 4, table_a, "north"); put(1, 0, 3, BARREL, facing="up")
    return blocks


# ---------------------------------------------------------------- v2: Doomsday Decoration props
DD = "doomsday_decoration:"
JEEP_F, JEEP_B, VAN_F, VAN_B, WAGON_END, SEDAN_F = DD + "green_jeep_1", DD + "green_jeep_2", DD + "discardgreenvan_1", DD + "discardgreenvan_2", DD + "discardbluestationwagon", DD + "frontgreensedan"
YVAN_F, YVAN_B, BJEEP_F, BJEEP_B = DD + "yellowvan_1", DD + "yellowvan_2", DD + "black_jeep_1", DD + "black_jeep_2"
SANDBAG, SANDBAG3, OILTANK, WIREMESH, CONE, FORKLIFT, MOTORCYCLE = DD + "sandbag", DD + "sandbag_3", DD + "oiltank", DD + "wiremesh", DD + "trafficcone", DD + "forklifttruck", DD + "motorcycle"


def piece(name, table_a, table_b=None):
    """v2 pieces: the same footprints as v1, built from the mod's wrecks, sandbags and drums."""
    blocks = []

    def put(x, y, z, n, **p):
        blocks.append((x, y, z, n, p, None))

    def chest(x, y, z, table, facing="north"):
        blocks.append((x, y, z, CHEST, {"facing": facing}, table))

    def box(x0, y0, z0, x1, y1, z1, n, **p):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    put(x, y, z, n, **p)

    if name == "car":                              # two wrecks nose to tail on a gravel patch, 7 x 2 x 4
        box(0, 0, 0, 6, 0, 3, GRAVEL)
        put(1, 1, 1, JEEP_F, facing="west"); put(2, 1, 1, JEEP_B, facing="west")
        put(4, 1, 2, SEDAN_F, facing="east"); put(5, 1, 2, WAGON_END, facing="east")
        put(3, 1, 0, CONE)
        chest(3, 1, 3, table_a, "south")
    elif name == "bus":                            # a van convoy that never left, 12 x 3 x 4
        box(0, 0, 0, 11, 0, 3, GRAVEL)
        put(1, 1, 1, VAN_F, facing="west"); put(2, 1, 1, VAN_B, facing="west")
        put(5, 1, 2, YVAN_F, facing="west"); put(6, 1, 2, YVAN_B, facing="west")
        put(9, 1, 1, BJEEP_F, facing="west"); put(10, 1, 1, BJEEP_B, facing="west")
        put(4, 1, 0, CONE); put(8, 1, 3, CONE); put(7, 1, 0, MOTORCYCLE, facing="north")
        chest(3, 1, 3, table_a, "south"); chest(8, 1, 0, table_b or table_a, "north")
    elif name == "shed":                           # collapsed shed with a forklift, 7 x 4 x 6
        box(0, 0, 0, 6, 0, 5, GRAVEL)
        for x in range(0, 7):
            for z in (0, 5):
                put(x, 1, z, CRACKED if (x + z) % 3 else STONE_BRICK)
        for z in range(1, 5):
            put(0, 1, z, STONE_BRICK); put(0, 2, z, CRACKED if z % 2 else AIR)
        box(1, 3, 1, 3, 3, 4, SLAB, type="bottom")
        put(6, 1, 2, AIR); put(6, 1, 3, AIR)
        put(4, 1, 2, FORKLIFT, facing="east")
        chest(1, 1, 1, table_a, "east"); put(5, 1, 4, OILTANK, facing="north")
    elif name == "containers":                     # shipping containers behind wire, 6 x 4 x 5
        box(0, 0, 0, 5, 1, 1, SHEET); box(0, 0, 3, 5, 1, 4, BLACK_CONC); box(0, 2, 1, 5, 3, 3, SHEET)
        put(0, 0, 0, AIR); put(0, 1, 0, AIR); put(5, 0, 4, AIR); put(5, 1, 4, AIR)
        put(0, 0, 2, WIREMESH, facing="west"); put(5, 0, 2, WIREMESH, facing="east")
        chest(1, 0, 0, table_a, "west"); chest(4, 0, 4, table_b or table_a, "east")
    elif name == "drums":                          # oil drums and a pump, 4 x 2 x 4
        for (x, z) in ((0, 0), (1, 0), (0, 1), (2, 2), (3, 3), (3, 1)):
            put(x, 0, z, OILTANK, facing="north")
        put(1, 1, 0, OILTANK, facing="north"); put(2, 0, 0, IRON_BLOCK); put(2, 1, 0, CHAIN, axis="y")
        chest(1, 0, 2, table_a, "south")
    elif name == "scrap":                          # a scrap heap, 5 x 2 x 5
        rng = random.Random(SEED ^ 0x5C)
        for x in range(5):
            for z in range(5):
                if rng.random() < 0.7:
                    put(x, 0, z, rng.choice((GRAVEL, COBBLE, MOSSY, IRON_BARS)))
        put(2, 1, 2, IRON_BARS); put(1, 1, 3, SCAF)
        chest(3, 0, 1, table_a, "north")
    elif name == "tent":                           # a camp tent behind a sandbag, 5 x 4 x 5
        box(0, 0, 0, 4, 0, 4, GRAVEL)
        for z in range(5):
            put(0, 1, z, WOOL); put(4, 1, z, WOOL); put(1, 2, z, WOOL); put(3, 2, z, WOOL)
        put(2, 3, 0, FENCE); put(2, 3, 4, FENCE); put(2, 2, 1, LANTERN, hanging="false")
        put(2, 1, 0, AIR); put(1, 1, 0, SANDBAG, facing="north")
        chest(2, 1, 3, table_a, "north")
    elif name == "checkpoint":                     # a checkpoint: sandbags, wire, a hut, 7 x 4 x 7
        for x in range(7):
            put(x, 0, 0, SANDBAG3 if x % 2 else SANDBAG, facing="north"); put(x, 0, 6, SANDBAG, facing="south")
        for z in range(1, 6):
            put(0, 0, z, WIREMESH, facing="west")
        box(4, 0, 2, 6, 0, 4, DEEPSLATE_TILE); box(4, 1, 2, 6, 2, 4, CONC); box(5, 1, 3, 5, 2, 3, AIR)
        put(4, 1, 3, AIR); put(4, 2, 3, AIR)
        put(6, 3, 3, LANTERN, hanging="false"); put(2, 0, 3, CONE)
        chest(5, 1, 4, table_a, "north"); put(1, 0, 3, OILTANK, facing="east")
    return blocks


def rotate(x, z, rot):
    """Vanilla structure rotation about the origin block."""
    return {"none": (x, z), "clockwise_90": (-z, x), "180": (-x, -z), "counterclockwise_90": (z, -x)}[rot]


def clear_function(placed, out: Path):
    """setblock air for every block the v1 templates put down, so the v2 pieces can go over them."""
    lines = []
    for p in placed:
        spec = next(s for s in PIECES if s[0] == p["piece"])
        for x, y, z, name, props, table in piece_v1(spec[0], *spec[1:]):
            if name == AIR:
                continue
            rx, rz = rotate(x, z, p["rotation"])
            lines.append(f"setblock {p['x'] + rx} {p['y'] + y} {p['z'] + rz} minecraft:air")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


PIECES = [("car", "hardware"), ("bus", "mixed", "medical"), ("shed", "hardware"), ("containers", "electrical", "hardware"),
          ("drums", "hardware"), ("scrap", "hardware"), ("tent", "medical"), ("checkpoint", "electrical")]
# how many of each to scatter (24 in all)
SCATTER = {"car": 5, "bus": 2, "shed": 3, "containers": 2, "drums": 3, "scrap": 4, "tent": 3, "checkpoint": 2}


# ------------------------------------------------------------------ template writer (per-piece size, chest NBT)
def write_template(blocks, path: Path):
    xs = [b[0] for b in blocks]; ys = [b[1] for b in blocks]; zs = [b[2] for b in blocks]
    size = (max(xs) + 1, max(ys) + 1, max(zs) + 1)
    palette, index, out = [], {}, []
    for x, y, z, name, props, table in blocks:
        key = (name, tuple(sorted(props.items())))
        if key not in index:
            index[key] = len(palette)
            entry = {"Name": (T_STRING, name)}
            if props:
                entry["Properties"] = (T_COMPOUND, {k: (T_STRING, str(v)) for k, v in props.items()})
            palette.append(entry)
        b = {"pos": (T_LIST, (T_INT, [x, y, z])), "state": (T_INT, index[key])}
        if table:
            b["nbt"] = (T_COMPOUND, {"id": (T_STRING, "minecraft:chest"),
                                     "LootTable": (T_STRING, f"gscraft:ruins/{table}"),
                                     "LootTableSeed": (T_LONG, 0)})
        out.append(b)
    root = {"size": (T_LIST, (T_INT, list(size))), "entities": (T_LIST, (T_COMPOUND, [])),
            "blocks": (T_LIST, (T_COMPOUND, out)), "palette": (T_LIST, (T_COMPOUND, palette)),
            "DataVersion": (T_INT, DATA_VERSION)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(W().root("", root)))
    return size, len(out)


# ------------------------------------------------------------------ ground
class Ground:
    def __init__(self, world: Path):
        self.world = world; self.cache = {}

    def chunk(self, cx, cz):
        key = (cx, cz)
        if key not in self.cache:
            rx, rz = region_of(cx, cz)
            raw = read_region_raw(self.world / "region" / f"r.{rx}.{rz}.mca").get(slot_of(cx, cz))
            self.cache[key] = Chunk(R(raw[2]).root()[1]) if raw else None
        return self.cache[key]

    def top(self, x, z):
        c = self.chunk(x >> 4, z >> 4)
        if c is None:
            return None, None
        y, name = c.top(x & 15, z & 15, ignore={"minecraft:air", "minecraft:cave_air", "minecraft:void_air",
                                                 "minecraft:grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:dead_bush"})
        return y, name


def keep_out_rects():
    rects = list(KEEP_OUT)
    for pad in json.loads((ROOT / "tools" / "pads_camp.json").read_text(encoding="utf-8")):
        x0, z0, x1, z1 = pad["blocks"]
        rects.append((x0 - 8, z0 - 8, x1 + 8, z1 + 8))
    return rects


def spine_clear(x, z):
    # the spine leaves the gate at (173, 8) heading east; keep the approach inside the camp clear
    return 120 <= x <= 207 and -4 <= z <= 20


def inside(x, z, r):
    return r[0] <= x <= r[2] and r[1] <= z <= r[3]


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    ground = Ground(Path(argv[1]))
    rng = random.Random(SEED)
    rects = keep_out_rects()
    sizes = {}
    for spec in PIECES:
        name, *tables = spec
        size, n = write_template(piece(name, *tables), DATAPACK / "structures" / f"ruin_{name}.nbt")
        sizes[name] = size
        print(f"ruin_{name:11} {n:3} blocks  size {size}  loot {tables}")
    for table, rows in LOOT.items():
        entries = [{"type": "minecraft:item", "name": item, "weight": 10 if lo else 3, "gscraft_item": intended,
                    "functions": [{"function": "minecraft:set_count", "count": {"min": max(lo, 1), "max": hi}}]}
                   for item, intended, lo, hi in rows]
        tbl = {"type": "minecraft:chest", "pools": [{"rolls": {"min": 2, "max": 4}, "entries": entries}]}
        p = DATAPACK / "loot_tables" / "ruins" / f"{table}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(tbl, indent=1), encoding="utf-8")
    placed = []
    lines = []
    tries = 0
    order = [n for n, k in SCATTER.items() for _ in range(k)]
    rng.shuffle(order)
    for name in order:
        w, h, d = sizes[name]
        for _ in range(400):
            tries += 1
            x = rng.randint(CAMP[0] + 8, CAMP[2] - 8 - w); z = rng.randint(CAMP[1] + 8, CAMP[3] - 8 - d)
            if any(inside(x + dx, z + dz, r) for r in rects for dx in (0, w) for dz in (0, d)) or spine_clear(x, z):
                continue
            if any(abs(x - p["x"]) < 20 and abs(z - p["z"]) < 20 for p in placed):
                continue
            ys = [ground.top(x + dx, z + dz)[0] for dx in (0, w // 2, w - 1) for dz in (0, d // 2, d - 1)]
            if any(y is None for y in ys) or max(ys) - min(ys) > 3:
                continue
            _, top_block = ground.top(x + w // 2, z + d // 2)
            if "water" in top_block or "lava" in top_block:
                continue
            y = max(ys) + 1
            rot = rng.choice(("none", "clockwise_90", "180", "counterclockwise_90"))
            placed.append({"piece": name, "x": x, "y": y, "z": z, "rotation": rot, "size": [w, h, d]})
            lines.append(f"place template gscraft:ruin_{name} {x} {y} {z} {rot} none")
            break
        else:
            print("  could not place", name)
    fn = DATAPACK / "functions" / "camp_ruins.mcfunction"
    fn.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "tools" / "camp_ruins.json").write_text(json.dumps({"seed": SEED, "camp": CAMP, "placed": placed}, indent=1), encoding="utf-8")
    n_clear = clear_function(placed, DATAPACK / "functions" / "camp_ruins_clear.mcfunction")
    print(f"camp_ruins_clear: {n_clear} setblocks over the v1 footprints")
    print(f"\nplaced {len(placed)} of {len(order)} pieces in {tries} tries -> {fn}")
    for p in placed:
        print(f"   {p['piece']:11} ({p['x']:5}, {p['y']:3}, {p['z']:5}) {p['rotation']}")


if __name__ == "__main__":
    main(sys.argv)
