"""Survey the spawn structure: per-column top block and height over chunks cx1..cx2, cz1..cz2."""
import sys, collections
from pathlib import Path
from transplant import R, read_region_raw, slot_of, region_of
from anvil import Chunk, AIR
world = Path(sys.argv[1]); cx1, cz1, cx2, cz2 = map(int, sys.argv[2:6])
NATURAL = {"minecraft:terracotta","minecraft:orange_terracotta","minecraft:red_terracotta","minecraft:brown_terracotta","minecraft:white_terracotta","minecraft:yellow_terracotta","minecraft:light_gray_terracotta","minecraft:grass_block","minecraft:dirt","minecraft:stone","minecraft:red_sand","minecraft:sand","minecraft:gravel","minecraft:water","minecraft:dead_bush","minecraft:moss_block","minecraft:coarse_dirt","minecraft:deepslate","minecraft:sandstone","minecraft:red_sandstone","minecraft:short_grass","minecraft:grass","minecraft:tall_grass","minecraft:bedrock"}
cache = {}
def chunk(cx, cz):
    rx, rz = region_of(cx, cz)
    if (rx, rz) not in cache: cache[(rx, rz)] = read_region_raw(world / "region" / f"r.{rx}.{rz}.mca")
    raw = cache[(rx, rz)].get(slot_of(cx, cz))
    if not raw: return None
    return Chunk(R(raw[2]).root()[1])
rows = []
tops = collections.Counter(); nat_h = collections.Counter(); art_h = collections.Counter()
for cz in range(cz1, cz2 + 1):
    for cx in range(cx1, cx2 + 1):
        ch = chunk(cx, cz)
        if not ch: print("missing chunk", cx, cz); continue
        for z in range(16):
            for x in range(16):
                y, b = ch.top(x, z); tops[b] += 1
                (nat_h if b in NATURAL else art_h)[y] += 1
                rows.append((cx*16+x, cz*16+z, y, b))
print("top blocks:"); [print(f"{v:6d} {k}") for k, v in tops.most_common(30)]
print("natural-top heights:", sorted(nat_h.items()))
print("artificial-top heights:", sorted(art_h.items())[:40])
# bbox of artificial columns
arts = [(x, z, y) for x, z, y, b in rows if b not in NATURAL]
if arts:
    xs = [a[0] for a in arts]; zs = [a[1] for a in arts]; ys = [a[2] for a in arts]
    print("artificial bbox x", min(xs), max(xs), "z", min(zs), max(zs), "top y", min(ys), max(ys), "count", len(arts))
