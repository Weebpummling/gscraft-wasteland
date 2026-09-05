"""Fill the ungenerated chunks inside a rectangle of a 1.20.1 world with flat ground (bedrock, stone, dirt, grass at
GROUND), so a world assembled from a superflat pack has no holes. usage: flatfill.py <world dir> x0 z0 x1 z1 [--ground 65] [--dry-run]
Writes minimal 'full' chunks (sections, biomes plains, empty heightmaps recomputed by the game) straight into the
region files; existing chunks are never touched."""
import sys, zlib, struct, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, W as NbtW

T_END, T_BYTE, T_SHORT, T_INT, T_LONG, T_STRING, T_LIST, T_COMPOUND, T_INT_ARRAY, T_LONG_ARRAY = 0, 1, 2, 3, 4, 8, 9, 10, 11, 12

def section(y, blocks):
    """blocks: single block name (uniform) or list of 16 layer names bottom->top."""
    if isinstance(blocks, str):
        bs = {"palette": (T_LIST, (T_COMPOUND, [{"Name": (T_STRING, blocks)}]))}
    else:
        names = sorted(set(blocks)); pal = [{"Name": (T_STRING, n)} for n in names]
        bits = max(4, (len(names) - 1).bit_length()); per = 64 // bits
        idx = [names.index(blocks[i >> 8]) for i in range(4096)]
        longs = []
        for i in range(0, 4096, per):
            v = 0
            for k, j in enumerate(range(i, min(i + per, 4096))): v |= idx[j] << (k * bits)
            longs.append(v - (1 << 64) if v >= (1 << 63) else v)
        bs = {"palette": (T_LIST, (T_COMPOUND, pal)), "data": (T_LONG_ARRAY, longs)}
    return {"Y": (T_BYTE, y), "block_states": (T_COMPOUND, bs),
            "biomes": (T_COMPOUND, {"palette": (T_LIST, (T_STRING, ["minecraft:plains"]))})}

def flat_chunk(cx, cz, ground):
    secs = []
    for sy in range(-4, 20):
        base = sy * 16
        if base + 15 < ground - 4: 
            secs.append(section(sy, "minecraft:bedrock" if sy == -4 else ("minecraft:deepslate" if base < 0 else "minecraft:stone")))
        elif base > ground: secs.append(section(sy, "minecraft:air"))
        else:
            layers = []
            for y in range(base, base + 16):
                layers.append("minecraft:stone" if y < ground - 3 else "minecraft:dirt" if y < ground else "minecraft:grass_block" if y == ground else "minecraft:air")
            if sy == -4: layers[0] = "minecraft:bedrock"
            secs.append(section(sy, layers))
    root = {"DataVersion": (T_INT, 3465), "xPos": (T_INT, cx), "zPos": (T_INT, cz), "yPos": (T_INT, -4),
            "Status": (T_STRING, "minecraft:full"), "LastUpdate": (T_LONG, 0), "InhabitedTime": (T_LONG, 0),
            "sections": (T_LIST, (T_COMPOUND, secs)), "block_entities": (T_LIST, (T_COMPOUND, [])),
            "isLightOn": (T_BYTE, 0), "PostProcessing": (T_LIST, (T_LIST, [(T_END, []) for _ in range(24)])),
            "structures": (T_COMPOUND, {"References": (T_COMPOUND, {}), "starts": (T_COMPOUND, {})}),
            "Heightmaps": (T_COMPOUND, {})}
    return NbtW().root("", root)

def main(a):
    if len(a) < 6: sys.exit(__doc__)
    world = Path(a[1]); x0, z0, x1, z1 = map(int, a[2:6]); ground = int(a[a.index("--ground") + 1]) if "--ground" in a else 65; dry = "--dry-run" in a
    added = 0; files = 0
    for rx in range(x0 >> 9, (x1 >> 9) + 1):
        for rz in range(z0 >> 9, (z1 >> 9) + 1):
            f = world / "region" / f"r.{rx}.{rz}.mca"; reg = read_region_raw(f) if f.exists() else {}
            n0 = len(reg)
            for slot in range(1024):
                cx, cz = rx * 32 + (slot & 31), rz * 32 + (slot >> 5)
                if cx * 16 + 15 < x0 or cx * 16 > x1 or cz * 16 + 15 < z0 or cz * 16 > z1 or slot in reg: continue
                reg[slot] = (int(time.time()), 2, flat_chunk(cx, cz, ground)); added += 1
            if len(reg) != n0:
                files += 1
                if not dry: write_region(f, reg)
    print(f"{'DRY RUN: would add' if dry else 'added'} {added} flat chunks at ground {ground} in {files} region files")

if __name__ == "__main__": main(sys.argv)
