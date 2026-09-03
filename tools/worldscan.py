"""Full read of a world: per-chunk material layers, rendered as PNG heatmaps and saved as JSON.

usage: worldscan.py <world region dir> <out prefix>
Layers per chunk:
  placed   non-air blocks that are not terrain/ore/plant (anything built or generated-built)
  custom   blocks from families a player build uses and Lost Cities' apocalypse pack does not:
           factory_blocks, chisel, antiblocks, refurbished furniture, IE machines/decor, copper,
           prismarine, quartz, concrete, stained glass, terracotta walls, wool, sculk
  lc       Lost Cities apocalypse-pack fingerprint blocks: cracked stone bricks, cobblestone
           stairs, smooth basalt, polished blackstone, deepslate tiles, mossy variants
  spawners mob spawners in the chunk (LC buildings carry them; player builds rarely do)
  types    distinct block types in the chunk
"""
import json, sys, collections, struct, zlib
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from transplant import R, read_region_raw
from anvil import decode
from terrain import NATURAL, PLANT

ORE = ("_ore",)
GENERATED_NS = {"lostcities", "backrooms"}
LC = {"minecraft:cracked_stone_bricks", "minecraft:cobblestone_stairs", "minecraft:smooth_basalt",
      "minecraft:polished_blackstone", "minecraft:deepslate_tiles", "minecraft:cracked_deepslate_tiles",
      "minecraft:mossy_stone_bricks", "minecraft:mossy_cobblestone", "minecraft:cracked_polished_blackstone_bricks",
      "minecraft:polished_blackstone_bricks", "minecraft:cobbled_deepslate", "minecraft:stone_brick_stairs",
      "minecraft:stone_brick_slab", "minecraft:cobblestone"}
CUSTOM_NS = {"factory_blocks", "chisel", "antiblocksrechiseled", "refurbished_furniture", "immersiveengineering",
             "doomsday_decoration", "create", "createdeco", "warium", "chipped"}
CUSTOM_WORDS = ("concrete", "copper", "prismarine", "quartz", "stained_glass", "wool", "sculk", "glazed_terracotta",
                "purpur", "end_stone_brick", "sea_lantern", "glowstone", "redstone_lamp", "iron_block", "gold_block",
                "diamond_block", "emerald_block", "netherite", "beacon", "tinted_glass", "smooth_quartz", "honeycomb_block")
AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def classify(name):
    ns, _, path = name.partition(":")
    if name in AIR: return None
    if name in NATURAL or name in PLANT or any(o in path for o in ORE): return "terrain"
    if ns in GENERATED_NS: return "terrain"
    if ns in CUSTOM_NS or any(w in path for w in CUSTOM_WORDS): return "custom"
    if name in LC: return "lc"
    return "other"


def scan_world(region_dir: Path):
    cache = {}
    chunks = {}
    for f in sorted(region_dir.glob("r.*.mca")):
        for slot, (ts, comp, raw) in read_region_raw(f).items():
            try:
                name, root = R(raw).root()
            except Exception:
                continue
            cx, cz = root.get("xPos", (0, 0))[1], root.get("zPos", (0, 0))[1]
            placed = custom = lc = other = 0; types = set()
            for sec in root.get("sections", (0, (0, [])))[1][1]:
                d = decode(sec)
                if not d: continue
                names, pal, idx = d
                counts = np.bincount(np.asarray(idx, dtype=np.int32), minlength=len(names))
                for i, n in enumerate(names):
                    c = int(counts[i])
                    if not c: continue
                    k = cache.get(n)
                    if k is None: k = cache[n] = classify(n)
                    if k is None or k == "terrain": continue
                    types.add(n); placed += c
                    if k == "custom": custom += c
                    elif k == "lc": lc += c
                    else: other += c
            spawners = sum(1 for be in root.get("block_entities", (0, (0, [])))[1][1]
                           if be.get("id", (0, ""))[1] == "minecraft:mob_spawner")
            chunks[f"{cx},{cz}"] = [placed, custom, lc, other, spawners, len(types)]
    return chunks


def render(chunks, out_prefix):
    try:
        from PIL import Image
    except ImportError:
        import cv2
        Image = None
    keys = [tuple(map(int, k.split(","))) for k in chunks]
    if not keys: print("no chunks"); return
    xs = [k[0] for k in keys]; zs = [k[1] for k in keys]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    W, H = x1 - x0 + 1, z1 - z0 + 1
    S = 3  # px per chunk
    img = np.zeros((H * S, W * S, 3), dtype=np.uint8) + 235
    for (cx, cz), v in zip(keys, chunks.values()):
        placed, custom, lc, other, sp, types = v
        if placed == 0: col = (225, 222, 210)
        else:
            c = min(1.0, custom / 3000); l = min(1.0, lc / 2000); o = min(1.0, other / 4000)
            # custom -> magenta, lc -> grey-blue, other -> amber
            col = (int(120 + 135 * c) if c > l and c > o else int(90 + 60 * l),
                   int(60 + 40 * o) if o > c and o > l else int(60 + 40 * c),
                   int(150 + 105 * c) if c > l and c > o else int(110 + 90 * l))
            if sp >= 3: col = (60, 60, 60)
        img[(cz - z0) * S:(cz - z0 + 1) * S, (cx - x0) * S:(cx - x0 + 1) * S] = col
    # grid every 32 chunks (region boundaries) and axis ticks
    for gx in range((x0 // 32) * 32, x1 + 1, 32):
        if x0 <= gx <= x1: img[:, (gx - x0) * S] = (160, 160, 160)
    for gz in range((z0 // 32) * 32, z1 + 1, 32):
        if z0 <= gz <= z1: img[(gz - z0) * S, :] = (160, 160, 160)
    if Image:
        Image.fromarray(img).save(out_prefix + ".png")
    else:
        cv2.imwrite(out_prefix + ".png", img[:, :, ::-1])
    json.dump({"origin": [x0, z0], "px_per_chunk": S, "chunks": chunks}, open(out_prefix + ".json", "w"))
    print(f"{out_prefix}: chunks x {x0}..{x1} z {z0}..{z1} ({W}x{H}), image {W*S}x{H*S}; chunks {len(chunks)}")


def main(argv):
    region = Path(argv[1]); out = argv[2]
    chunks = scan_world(region)
    tot = collections.Counter()
    for v in chunks.values():
        tot["placed"] += v[0]; tot["custom"] += v[1]; tot["lc"] += v[2]; tot["other"] += v[3]; tot["spawners"] += v[4]
    print(out, dict(tot), "chunks", len(chunks), "with custom>500:", sum(1 for v in chunks.values() if v[1] > 500))
    render(chunks, out)


if __name__ == "__main__":
    main(sys.argv)
