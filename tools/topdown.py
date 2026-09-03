"""Top-down colour render of a region folder: one pixel per block (or per N blocks), the colour of
the topmost non-air block, plus a chunk-coordinate grid every 32 chunks. Fast path with numpy.

usage: topdown.py <region dir> <out.png> [--scale N] [--chunks x1 z1 x2 z2]
"""
import sys, json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from transplant import R, read_region_raw
from anvil import decode

COLOURS = [  # (substring, rgb) - first match wins
    ("water", (48, 96, 176)), ("lava", (230, 90, 20)), ("ice", (160, 200, 240)),
    ("grass_block", (96, 140, 60)), ("moss", (90, 130, 60)), ("leaves", (50, 100, 40)), ("vine", (60, 110, 50)),
    ("_log", (100, 70, 40)), ("_wood", (100, 70, 40)), ("planks", (170, 130, 80)),
    ("sand", (214, 200, 150)), ("red_sand", (190, 110, 60)), ("gravel", (130, 125, 120)), ("dirt", (120, 85, 55)),
    ("white_concrete", (230, 230, 230)), ("light_gray_concrete", (160, 160, 160)), ("gray_concrete", (80, 80, 84)),
    ("black_concrete", (18, 18, 22)), ("blue_concrete", (44, 46, 143)), ("cyan_concrete", (20, 120, 136)),
    ("light_blue_concrete", (36, 137, 199)), ("red_concrete", (142, 33, 33)), ("orange_concrete", (224, 97, 1)),
    ("yellow_concrete", (240, 175, 21)), ("lime_concrete", (94, 169, 25)), ("green_concrete", (73, 91, 36)),
    ("purple_concrete", (100, 32, 156)), ("magenta_concrete", (169, 48, 159)), ("pink_concrete", (213, 101, 142)),
    ("brown_concrete", (96, 60, 32)), ("concrete", (150, 150, 150)),
    ("terracotta", (150, 90, 60)), ("white_terracotta", (210, 178, 161)), ("orange_terracotta", (160, 84, 38)),
    ("yellow_terracotta", (186, 133, 35)), ("light_gray_terracotta", (135, 107, 98)), ("brown_terracotta", (77, 51, 36)),
    ("red_terracotta", (143, 61, 47)),
    ("glass", (170, 220, 230)), ("iron_bars", (120, 125, 130)), ("iron_block", (215, 215, 215)),
    ("copper", (170, 105, 60)), ("prismarine", (90, 160, 150)), ("quartz", (235, 230, 225)),
    ("deepslate", (70, 70, 75)), ("blackstone", (40, 36, 40)), ("basalt", (72, 72, 78)),
    ("cracked_stone_bricks", (110, 108, 104)), ("stone_bricks", (122, 120, 118)), ("cobblestone", (128, 128, 128)),
    ("andesite", (136, 136, 136)), ("diorite", (190, 190, 190)), ("granite", (150, 105, 90)), ("stone", (125, 125, 125)),
    ("factory", (105, 110, 120)), ("rust", (130, 80, 50)), ("wireframe", (60, 200, 220)), ("hempcrete", (170, 165, 140)),
    ("sculk", (10, 40, 60)), ("bookshelf", (140, 100, 60)), ("wool", (200, 200, 200)), ("bed", (200, 60, 60)),
    ("snow", (240, 240, 245)), ("netherrack", (110, 50, 50)), ("obsidian", (20, 15, 35)), ("chain", (90, 90, 100)),
    ("sheetmetal", (150, 155, 160)), ("scaffolding", (190, 160, 90)), ("mud", (90, 75, 65)), ("brick", (150, 90, 70)),
]
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def colour_of(name, cache={}):
    c = cache.get(name)
    if c is not None: return c
    path = name.split(":", 1)[-1]
    for sub, rgb in COLOURS:
        if sub in path: cache[name] = rgb; return rgb
    cache[name] = (200, 120, 200)   # unknown -> mauve, so it stands out
    return cache[name]


def chunk_top_colours(root):
    """(16,16) array of rgb for the chunk's top non-air blocks, z-major."""
    secs = [(s["Y"][1], decode(s)) for s in root.get("sections", (0, (0, [])))[1][1]]
    secs = [(y, d) for y, d in secs if d]
    if not secs: return None
    secs.sort(key=lambda t: -t[0])
    out = np.zeros((16, 16, 3), dtype=np.uint8); done = np.zeros((16, 16), dtype=bool)
    for y, (names, pal, idx) in secs:
        if done.all(): break
        if all(n in AIRS for n in names): continue
        arr = np.asarray(idx, dtype=np.int32).reshape(16, 16, 16)   # [y][z][x]
        air = np.array([n in AIRS for n in names])
        solid = ~air[arr]                                            # [y][z][x] bool
        top = np.where(solid.any(axis=0), 15 - np.argmax(solid[::-1], axis=0), -1)  # per z,x
        for z in range(16):
            for x in range(16):
                if done[z, x] or top[z, x] < 0: continue
                out[z, x] = colour_of(names[arr[top[z, x], z, x]]); done[z, x] = True
    return out


def main(argv):
    region = Path(argv[1]); out = argv[2]
    scale = int(argv[argv.index("--scale") + 1]) if "--scale" in argv else 1
    bounds = list(map(int, argv[argv.index("--chunks") + 1: argv.index("--chunks") + 5])) if "--chunks" in argv else None
    tiles = {}
    for f in sorted(region.glob("r.*.mca")):
        rx, rz = map(int, f.stem.split(".")[1:3])
        if bounds and (rx * 32 + 31 < bounds[0] or rx * 32 > bounds[2] or rz * 32 + 31 < bounds[1] or rz * 32 > bounds[3]): continue
        for slot, (ts, comp, raw) in read_region_raw(f).items():
            try: name, root = R(raw).root()
            except Exception: continue
            cx, cz = root.get("xPos", (0, 0))[1], root.get("zPos", (0, 0))[1]
            if bounds and not (bounds[0] <= cx <= bounds[2] and bounds[1] <= cz <= bounds[3]): continue
            t = chunk_top_colours(root)
            if t is not None: tiles[(cx, cz)] = t
    if not tiles: print("no chunks"); return
    xs = [k[0] for k in tiles]; zs = [k[1] for k in tiles]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    W, H = (x1 - x0 + 1) * 16, (z1 - z0 + 1) * 16
    img = np.full((H, W, 3), 236, dtype=np.uint8)
    for (cx, cz), t in tiles.items():
        img[(cz - z0) * 16:(cz - z0 + 1) * 16, (cx - x0) * 16:(cx - x0 + 1) * 16] = t
    for gx in range((x0 // 32) * 32, x1 + 1, 32):
        if x0 <= gx <= x1: img[:, (gx - x0) * 16] = (255, 255, 0)
    for gz in range((z0 // 32) * 32, z1 + 1, 32):
        if z0 <= gz <= z1: img[(gz - z0) * 16, :] = (255, 255, 0)
    if scale > 1:
        img = img[:H // scale * scale, :W // scale * scale].reshape(H // scale, scale, W // scale, scale, 3).mean(axis=(1, 3)).astype(np.uint8)
    from PIL import Image
    Image.fromarray(img).save(out)
    json.dump({"chunk_origin": [x0, z0], "chunk_max": [x1, z1], "scale": scale}, open(out + ".json", "w"))
    print(f"{out}: chunks x {x0}..{x1} z {z0}..{z1}, image {img.shape[1]}x{img.shape[0]} at 1px per {scale} blocks; yellow lines every 32 chunks")


if __name__ == "__main__":
    main(sys.argv)
