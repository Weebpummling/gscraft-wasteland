"""Radio tower model as progressive repair stages.

Builds the radio-tower compound block by block and writes it as vanilla structure templates, one per
repair stage, so the quest reward for installing a part is a single `/place template` and the tower
visibly grows in the world. Stage 0 is the ruin the players find; stages 1-5 each add one part.

usage:
  tower.py build                 write the templates + functions into build/datapacks/gscraft and render
  tower.py render <out.png>      render only (elevation + plan per stage)

Outputs:
  build/datapacks/gscraft/data/gscraft/structures/tower_stage_{0..5}.nbt
  build/datapacks/gscraft/data/gscraft/functions/tower_stage_{0..5}.mcfunction   (place at the pad)
  build/tower_parts.json                                  part -> stage -> role -> template
  docs/renders/radio_tower_stages.png

Every block id here was checked against the pack: vanilla 1.20.1 and ImmersiveEngineering 10.2.0.
Templates are sparse (only the blocks listed are placed), so each stage adds to the previous one and
never wipes what the players built around it.
"""
import gzip, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from transplant import W, T_BYTE, T_INT, T_STRING, T_LIST, T_COMPOUND

ROOT = Path(__file__).resolve().parents[1]
DATAPACK = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft"
DATA_VERSION = 3465                                   # 1.20.1

# ------------------------------------------------------------------ placement in the world
PAD = (64, -144, 191, -17)                             # radio tower pad IN THE CAMP (north-east corner), blocks (x0 z0 x1 z1), pad level y 99
GROUND_Y = 99
SIZE = (41, 90, 41)                                   # template box W H D; local (20, *, 20) is the mast centre
ORIGIN = ((PAD[0] + PAD[2]) // 2 - SIZE[0] // 2, GROUND_Y + 1, (PAD[1] + PAD[3]) // 2 - SIZE[2] // 2)
CX, CZ = 20, 20
MAST_TOP = 64                                         # legs run y 1..64; antenna above

# ------------------------------------------------------------------ blocks
IE = "immersiveengineering:"
SCAF, FENCE, CONC, TILE, SHEET, STEEL = IE + "steel_scaffolding_standard", IE + "steel_fence", IE + "concrete", IE + "concrete_tile", IE + "sheetmetal_steel", IE + "storage_steel"
RAZOR, PIPE, RADIATOR, TRANSFORMER, CAP, RELAY, FLOOD = IE + "razor_wire", IE + "fluid_pipe", IE + "radiator", IE + "transformer", IE + "capacitor_mv", IE + "connector_hv_relay", IE + "floodlight"
THERMO, LIGHT_ENG, HEAVY_ENG, BREAKER, CT, LANTERN = IE + "thermoelectric_generator", IE + "light_engineering", IE + "heavy_engineering", IE + "breaker_switch", IE + "current_transformer", IE + "electric_lantern"
AIR, IRON, CHAIN, ROD, LAMP, TRAP, BEACON, GRAVEL, COBBLE, SLAB, GLASS = ("minecraft:air", "minecraft:iron_block", "minecraft:chain", "minecraft:lightning_rod",
    "minecraft:sea_lantern", "minecraft:iron_trapdoor", "minecraft:beacon", "minecraft:gravel", "minecraft:cobblestone", "minecraft:smooth_stone_slab", "minecraft:glass")

# stage -> list of (x, y, z, name, properties)
STAGES = {i: [] for i in range(6)}
PARTS = [  # (stage, complete part handed in, loot-only component and where it is found, intermediates, what the stage adds)
    (1, "Mast section kit", "heavy anchor cable (Novo Expograd)", "6 steel frame + 2 fastener kit, Workshop 2", "mast to full height, cross braces, four guy anchors and wires"),
    (2, "Cooling loop", "industrial pump (industrial plant)", "2 filter cartridge + 2 coolant + 2 sealed tubing, Water 2", "two coolant tanks, pipe run, radiator bank at the mast base"),
    (3, "Generator kit", "transformer core (FR-06 reactor plaza)", "2 wiring harness + 1 motor assembly, Generator 2", "generator shed, relays on the mast, aviation lights and floodlights come on"),
    (4, "Transmitter", "military circuit board (Financial Plaza)", "2 circuit assembly + 1 wiring harness, Radio 2", "hall repaired and fitted out, dish on the roof"),
    (5, "Antenna array", "phased array element (the hub, air ring only)", "4 antenna element + 1 circuit assembly, Radio 3", "spire, dipoles, and the beacon that proves the tower is live"),
]


def put(stage, x, y, z, name, **props):
    STAGES[stage].append((x, y, z, name, props))


def box(stage, x0, y0, z0, x1, y1, z1, name, **props):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(stage, x, y, z, name, **props)


def shell(stage, x0, y0, z0, x1, y1, z1, name, **props):
    """Walls only (no floor, no roof)."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    put(stage, x, y, z, name, **props)


LEGS = [(CX - 2, CZ - 2), (CX + 2, CZ - 2), (CX - 2, CZ + 2), (CX + 2, CZ + 2)]
HALL = (4, 26, 14, 32)          # transmitter hall footprint x0 z0 x1 z1 (south-west of the mast)
SHED = (26, 6, 32, 10)          # generator shed (north-east)
TANKS = [(6, 18), (10, 18)]     # coolant tank centres (west)


def build_model():
    rng = random.Random(2404991234066556536)
    # ---------------- stage 0: the ruin
    box(0, CX - 4, 0, CZ - 4, CX + 4, 0, CZ + 4, TILE)                      # plinth
    for (lx, lz), h in zip(LEGS, (7, 3, 5, 0)):                             # leg stubs, one gone
        for y in range(1, h + 1):
            put(0, lx, y, lz, SCAF)
    for _ in range(40):                                                     # rubble
        x, z = rng.randint(2, 38), rng.randint(2, 38)
        if abs(x - CX) <= 4 and abs(z - CZ) <= 4:
            continue
        put(0, x, 0, z, rng.choice((GRAVEL, COBBLE, COBBLE, CONC)))
    x0, z0, x1, z1 = HALL
    box(0, x0, 0, z0, x1, 0, z1, TILE)                                      # hall floor
    shell(0, x0, 1, z0, x1, 4, z1, CONC)                                    # walls...
    for (hx, hz) in [(x0, 28), (x0, 29), (7, z0), (8, z0), (11, z1), (x1, 30), (x1, 31), (x1, 29)]:
        for y in (2, 3, 4):
            put(0, hx, y, hz, AIR)                                          # ...with holes
    for y in (1, 2):
        put(0, 9, y, z1, AIR)                                               # doorway
    for x in range(x0, x1 + 1):                                             # half the roof left
        for z in range(z0, z1 + 1):
            if (x + z) % 3 != 0 and x < 11:
                put(0, x, 5, z, SHEET)
    for i in range(0, 41, 2):                                               # broken fence line
        if rng.random() < 0.7:
            put(0, i, 1, 1, FENCE); put(0, i, 1, 39, FENCE)
        if rng.random() < 0.7:
            put(0, 1, 1, i, FENCE); put(0, 39, 1, i, FENCE)

    # ---------------- stage 1: anchors and mast
    for lx, lz in LEGS:
        for y in range(1, MAST_TOP + 1):
            put(1, lx, y, lz, SCAF)
    for y in range(4, MAST_TOP + 1, 4):                                     # cross braces between legs
        for d in range(-1, 2):
            put(1, CX + d, y, CZ - 2, FENCE); put(1, CX + d, y, CZ + 2, FENCE)
            put(1, CX - 2, y, CZ + d, FENCE); put(1, CX + 2, y, CZ + d, FENCE)
    for y in range(16, MAST_TOP + 1, 16):                                   # work platforms
        box(1, CX - 2, y, CZ - 2, CX + 2, y, CZ + 2, SCAF)
    for sx, sz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):                     # guy anchors and wires
        ax, az = CX + 16 * sx, CZ + 16 * sz
        box(1, ax - 1, 0, az - 1, ax, 1, az, CONC)
        for i in range(15):                                                 # stepped chain from anchor to y 48
            x, z = ax - sx * i, az - sz * i
            for y in range(2 + i * 3, 2 + i * 3 + 3):
                if y < 48 and (abs(x - CX) > 2 or abs(z - CZ) > 2):
                    put(1, x, y, z, CHAIN, axis="y")

    # ---------------- stage 2: cooling loop
    for tx, tz in TANKS:
        box(2, tx - 1, 0, tz - 1, tx + 1, 0, tz + 1, CONC)
        shell(2, tx - 1, 1, tz - 1, tx + 1, 5, tz + 1, SHEET)
        box(2, tx - 1, 6, tz - 1, tx + 1, 6, tz + 1, SHEET)
    for x in range(8, CX - 3):                                              # pipe run east to the mast base
        put(2, x, 1, 18, PIPE)
    for z in range(19, 26):                                                 # and south to the hall
        put(2, 8, 1, z, PIPE)
    for x in range(CX - 3, CX + 4):                                         # radiator bank across the plinth edge
        put(2, x, 1, CZ - 4, RADIATOR)

    # ---------------- stage 3: power
    x0, z0, x1, z1 = SHED
    box(3, x0, 0, z0, x1, 0, z1, TILE)
    shell(3, x0, 1, z0, x1, 3, z1, CONC)
    box(3, x0, 4, z0, x1, 4, z1, SHEET)
    for y in (1, 2):
        put(3, x0, y, 8, AIR)                                               # door faces the mast
    put(3, 28, 1, 8, THERMO); put(3, 30, 1, 8, THERMO)
    put(3, 29, 1, 7, TRANSFORMER); put(3, 29, 1, 9, CAP); put(3, 31, 1, 7, CAP)
    put(3, 27, 1, 9, BREAKER); put(3, 27, 1, 7, CT)
    put(3, 29, 5, 8, RELAY)                                                 # relay on the shed roof
    for y in (12, 28, 44):
        put(3, CX + 2, y, CZ - 3, RELAY)                                    # relays up the mast
    for y in range(16, MAST_TOP + 1, 16):                                   # aviation lights on the platforms
        for lx, lz in LEGS:
            put(3, lx, y + 1, lz, LAMP)
    for x in (HALL[0], HALL[2]):
        put(3, x, 6, 29, FLOOD)                                             # floodlights on the hall roof
    for x in range(x0, x1 + 1, 3):
        put(3, x, 5, 8, LANTERN)

    # ---------------- stage 4: transmitter
    x0, z0, x1, z1 = HALL
    shell(4, x0, 1, z0, x1, 4, z1, CONC)                                    # walls whole again
    for y in (1, 2):
        put(4, 9, y, z1, AIR)                                               # keep the doorway
    for z in (28, 30):
        put(4, x0, 3, z, GLASS); put(4, x1, 3, z, GLASS)                    # windows
    box(4, x0, 5, z0, x1, 5, z1, SHEET)                                     # full roof
    put(4, 6, 1, 28, HEAVY_ENG); put(4, 6, 1, 30, LIGHT_ENG); put(4, 12, 1, 28, LIGHT_ENG)
    put(4, 12, 1, 30, BREAKER); put(4, 9, 1, 28, CT)
    for x in range(7, 12):
        put(4, x, 1, 31, SLAB, type="bottom")                               # operator desk
    for x in range(7, 12):                                                  # the dish: a 5x5 plate of iron trapdoors
        for z in range(27, 32):
            put(4, x, 7, z, TRAP)
    put(4, 9, 6, 29, STEEL); put(4, 9, 8, 29, ROD)                          # dish mount and feed

    # ---------------- stage 5: antenna array and beacon
    box(5, CX - 2, MAST_TOP + 1, CZ - 2, CX + 2, MAST_TOP + 1, CZ + 2, IRON)   # 5x5 iron cap = beacon base
    put(5, CX, MAST_TOP + 2, CZ, BEACON)
    sx, sz = LEGS[0]
    for y in range(MAST_TOP + 2, MAST_TOP + 14):                            # spire on the north-west leg
        put(5, sx, y, sz, CHAIN, axis="y")
    put(5, sx, MAST_TOP + 14, sz, ROD)
    for (lx, lz), facing in zip(LEGS[1:], ("east", "west", "east")):        # dipoles on the other legs
        put(5, lx, MAST_TOP + 2, lz, ROD)
        for y in (40, 48, 56):
            put(5, lx + (1 if facing == "east" else -1), y, lz, ROD, facing=facing)
    for y in (24, 36):                                                      # side arrays lower down
        put(5, CX - 3, y, CZ, ROD, facing="west"); put(5, CX + 3, y, CZ, ROD, facing="east")
    return STAGES


# ------------------------------------------------------------------ structure template writer
def write_template(blocks, path: Path):
    palette, index = [], {}
    out_blocks = []
    for x, y, z, name, props in blocks:
        key = (name, tuple(sorted(props.items())))
        if key not in index:
            index[key] = len(palette)
            entry = {"Name": (T_STRING, name)}
            if props:
                entry["Properties"] = (T_COMPOUND, {k: (T_STRING, str(v)) for k, v in props.items()})
            palette.append(entry)
        out_blocks.append({"pos": (T_LIST, (T_INT, [x, y, z])), "state": (T_INT, index[key])})
    root = {
        "size": (T_LIST, (T_INT, list(SIZE))),
        "entities": (T_LIST, (T_COMPOUND, [])),
        "blocks": (T_LIST, (T_COMPOUND, out_blocks)),
        "palette": (T_LIST, (T_COMPOUND, palette)),
        "DataVersion": (T_INT, DATA_VERSION),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(W().root("", root)))
    return len(out_blocks), len(palette)


# ------------------------------------------------------------------ render
COLOURS = {SCAF: (150, 150, 160), FENCE: (110, 110, 120), CONC: (170, 170, 165), TILE: (150, 150, 145), SHEET: (120, 125, 135),
           STEEL: (90, 95, 105), RAZOR: (90, 90, 90), PIPE: (160, 120, 60), RADIATOR: (200, 80, 40), TRANSFORMER: (60, 60, 70),
           CAP: (70, 90, 60), RELAY: (200, 160, 60), FLOOD: (255, 240, 150), THERMO: (80, 80, 90), LIGHT_ENG: (90, 110, 130),
           HEAVY_ENG: (70, 80, 100), BREAKER: (200, 60, 60), CT: (180, 140, 60), LANTERN: (255, 230, 120), IRON: (215, 215, 215),
           CHAIN: (60, 60, 65), ROD: (190, 110, 60), LAMP: (180, 240, 230), TRAP: (170, 175, 185), BEACON: (120, 220, 240),
           GRAVEL: (130, 125, 120), COBBLE: (128, 128, 128), SLAB: (150, 150, 150), GLASS: (170, 220, 230), AIR: None}


def render(stages, out: str):
    import numpy as np
    from PIL import Image, ImageDraw
    W_, H_, D_ = SIZE
    panels = []
    world = {}
    for s in range(6):
        for x, y, z, name, props in stages[s]:
            if name == AIR:
                world.pop((x, y, z), None)
            else:
                world[(x, y, z)] = name
        elev = np.full((H_, W_, 3), 236, dtype=np.uint8)                   # south elevation: x across, y up, nearest z wins
        plan = np.full((D_, W_, 3), 236, dtype=np.uint8)                    # plan: highest block wins
        best_z, best_y = {}, {}
        for (x, y, z), name in world.items():
            c = COLOURS.get(name, (200, 120, 200))
            if (x, y) not in best_z or z > best_z[(x, y)]:
                best_z[(x, y)] = z; elev[H_ - 1 - y, x] = c
            if (x, z) not in best_y or y > best_y[(x, z)]:
                best_y[(x, z)] = y; plan[z, x] = c
        panel = np.full((H_ + D_ + 4, W_, 3), 236, dtype=np.uint8)
        panel[:H_] = elev; panel[H_ + 4:] = plan
        panels.append(panel)
    scale = 4
    img = Image.new("RGB", ((W_ * scale + 12) * 6, (H_ + D_ + 4) * scale + 24), (236, 236, 236))
    d = ImageDraw.Draw(img)
    for i, p in enumerate(panels):
        tile = Image.fromarray(p).resize((W_ * scale, (H_ + D_ + 4) * scale), Image.NEAREST)
        img.paste(tile, (i * (W_ * scale + 12), 24))
        label = "0 as found" if i == 0 else f"{i} {PARTS[i - 1][1]}"
        d.text((i * (W_ * scale + 12) + 2, 4), label, fill=(30, 30, 30))
    img.save(out)
    return img.size


def main(argv):
    stages = build_model()
    if argv[1:2] == ["render"]:
        print("rendered", render(stages, argv[2]))
        return
    manifest = {"origin": list(ORIGIN), "size": list(SIZE), "pad": list(PAD),
                "place": f"place template gscraft:tower_stage_N {ORIGIN[0]} {ORIGIN[1]} {ORIGIN[2]}", "stages": []}
    for s in range(6):
        n, pal = write_template(stages[s], DATAPACK / "structures" / f"tower_stage_{s}.nbt")
        fn = DATAPACK / "functions" / f"tower_stage_{s}.mcfunction"
        fn.parent.mkdir(parents=True, exist_ok=True)
        fn.write_text(f"place template gscraft:tower_stage_{s} {ORIGIN[0]} {ORIGIN[1]} {ORIGIN[2]}\n", encoding="utf-8")
        entry = {"stage": s, "template": f"gscraft:tower_stage_{s}", "function": f"gscraft:tower_stage_{s}", "blocks": n, "palette": pal}
        if s == 0:
            entry.update(part="as found", source="world build", materials="-", adds="ruined plinth, leg stubs, wrecked hall, broken fence")
        else:
            _, part, source, materials, adds = PARTS[s - 1]
            entry.update(part=part, source=source, materials=materials, adds=adds)
        manifest["stages"].append(entry)
        print(f"stage {s}: {n:5} blocks, palette {pal:2}  {entry['part']}")
    (ROOT / "build" / "tower_parts.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    out = ROOT / "docs" / "renders" / "radio_tower_stages.png"
    print("rendered", render(stages, str(out)), out)
    print("origin", ORIGIN, "size", SIZE)


if __name__ == "__main__":
    main(sys.argv)
