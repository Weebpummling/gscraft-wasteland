"""Pull Skadowsky's forest out of the world as per-column vegetation stacks."""
import sys, json, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, r"G:/GSCraft/repo/tools")
from transplant import read_region_raw, R, slot_of, region_of
from applyheight import decode_chunk

WORLD = Path(r"G:/GSCraft/server/wasteland-v8")
AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
# what counts as ground we stand the stack on
GROUND = {"minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol",
          "minecraft:stone", "minecraft:gravel", "minecraft:sand", "minecraft:mycelium",
          "minecraft:moss_block", "minecraft:rooted_dirt", "minecraft:clay", "minecraft:mud"}
# everything we are willing to lift: canopy, trunk, undergrowth
VEG_SUFFIX = ("_leaves", "_log", "_wood", "_sapling")
VEG_EXACT = {"minecraft:vine", "minecraft:moss_carpet", "minecraft:grass", "minecraft:short_grass",
             "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern", "minecraft:dead_bush",
             "minecraft:brown_mushroom", "minecraft:red_mushroom", "minecraft:sweet_berry_bush",
             "minecraft:azalea", "minecraft:flowering_azalea", "minecraft:mushroom_stem",
             "minecraft:brown_mushroom_block", "minecraft:red_mushroom_block", "minecraft:cobweb"}


def is_veg(n):
    return n.endswith(VEG_SUFFIX) or n in VEG_EXACT


_cache = {}
def chunk_blocks(cx, cz):
    key = (cx, cz)
    if key in _cache:
        return _cache[key]
    rk = region_of(cx, cz)
    p = WORLD / "region" / f"r.{rk[0]}.{rk[1]}.mca"
    out = None
    if p.exists():
        e = read_region_raw(p).get(slot_of(cx, cz))
        if e:
            try:
                name, root = R(e[2]).root()
                ids, pal, tmpl = decode_chunk(root)
                out = np.array([x["Name"][1] for x in pal], object)[ids]
            except Exception:
                out = None
    if len(_cache) > 300:
        _cache.clear()
    _cache[key] = out
    return out


def column(x, z):
    a = chunk_blocks(x >> 4, z >> 4)
    return None if a is None else a[:, z & 15, x & 15]


def stack_at(x, z, max_h=40):
    """(ground_y, [block names from ground+1 upward]) or None if there is nothing worth taking."""
    col = column(x, z)
    if col is None:
        return None
    # ground: the highest solid natural surface under the vegetation
    top = None
    for y in range(200, 40, -1):
        n = str(col[y + 64])
        if n in AIR:
            continue
        if n in GROUND:
            top = y
            break
        if not is_veg(n):
            return None           # something built or unexpected: skip this column
    if top is None:
        return None
    out = []
    for y in range(top + 1, min(top + 1 + max_h, 250)):
        n = str(col[y + 64])
        if n in AIR:
            out.append(None)
        elif is_veg(n):
            out.append(n)
        else:
            return None           # a non-vegetation block above ground: skip
    while out and out[-1] is None:
        out.pop()
    return (top, out)


def main():
    # the densest 64-block stands in the sector (38-47% canopy), plus two wider windows for the
    # thinner edge-of-wood look, so patches vary between close-grown and open
    windows = [(-968, -1240, 64, 64), (-968, -1160, 64, 64), (-880, -1080, 64, 64),
               (-968, -1104, 64, 64), (-856, -1136, 64, 64),
               (-880, -1152, 128, 128), (-960, -1136, 96, 96)]
    lib = {}
    counts = collections.Counter()
    for wx, wz, w, h in windows:
        got = 0
        for dz in range(h):
            for dx in range(w):
                s = stack_at(wx + dx, wz + dz)
                if s is None:
                    continue
                gy, blocks = s
                if not blocks:
                    continue
                lib[f"{wx},{wz}|{dx},{dz}"] = blocks
                got += 1
                for b in blocks:
                    if b:
                        counts[b] += 1
        print(f"window ({wx},{wz}) {w}x{h}: {got} columns with vegetation")
    json.dump(lib, open("forest_lib.json", "w"), separators=(",", ":"))
    print(f"\n{len(lib)} source columns saved to forest_lib.json")
    print("blocks:", ", ".join(f"{k.split(':')[-1]} {v:,}" for k, v in counts.most_common(10)))
    hs = [len(v) for v in lib.values()]
    print(f"stack height: median {sorted(hs)[len(hs)//2]}, max {max(hs)}")


if __name__ == "__main__":
    main()
