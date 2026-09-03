"""ASCII map of a chunk range: one char per 2x2 columns. . terrain  ~ water  # built  B building-ish  digits = height/10 of terrain"""
import sys
from pathlib import Path
from transplant import R, read_region_raw, slot_of, region_of
from anvil import Chunk
from terrain import NATURAL
world = Path(sys.argv[1]); cx1, cz1, cx2, cz2 = map(int, sys.argv[2:6])
cache = {}
def chunk(cx, cz):
    rx, rz = region_of(cx, cz)
    if (rx, rz) not in cache: cache[(rx, rz)] = read_region_raw(world / "region" / f"r.{rx}.{rz}.mca")
    raw = cache[(rx, rz)].get(slot_of(cx, cz))
    return Chunk(R(raw[2]).root()[1]) if raw else None
chunks = {(cx, cz): chunk(cx, cz) for cx in range(cx1, cx2+1) for cz in range(cz1, cz2+1)}
print("      x=" + "".join(f"{(cx*16)%1000:<8d}" for cx in range(cx1, cx2+1)))
for z in range(cz1*16, cz2*16+16, 2):
    line = ""
    for x in range(cx1*16, cx2*16+16, 2):
        ch = chunks.get((x>>4, z>>4))
        if not ch: line += "?"; continue
        y, b = ch.top(x & 15, z & 15)
        if b == "minecraft:water": line += "~"
        elif b in NATURAL: line += str((y // 10) % 10)
        else: line += "#"
    print(f"z={z:5d} " + line)
