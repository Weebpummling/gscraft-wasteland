import sys
from pathlib import Path
from transplant import R, read_region_raw, slot_of, region_of
from anvil import Chunk
from terrain import NATURAL
world = Path(sys.argv[1]); x1, z1, x2, z2 = map(int, sys.argv[2:6]); step = int(sys.argv[7]) if len(sys.argv) > 7 else 1
cache = {}
def chunk(cx, cz):
    rx, rz = region_of(cx, cz)
    if (rx, rz) not in cache: cache[(rx, rz)] = read_region_raw(world / "region" / f"r.{rx}.{rz}.mca")
    raw = cache[(rx, rz)].get(slot_of(cx, cz)); return Chunk(R(raw[2]).root()[1]) if raw else None
chunks = {}
print("top y per column (. = water/terrain):")
print("     x=" + "".join(f"{x:4d}" for x in range(x1, x2 + 1, step)))
for z in range(z1, z2 + 1, step):
    line = ""
    for x in range(x1, x2 + 1, step):
        k = (x >> 4, z >> 4)
        if k not in chunks: chunks[k] = chunk(*k)
        ch = chunks[k]
        y, b = ch.top(x & 15, z & 15)
        line += "   ." if b in NATURAL or b == "minecraft:water" else f"{y:4d}"
    print(f"z={z:4d}" + line)
