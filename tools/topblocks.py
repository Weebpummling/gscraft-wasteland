"""Tally the surface block of every column in a set of region files (what the terrain is made of)."""
import sys, collections
from pathlib import Path
from transplant import R, read_region_raw
from anvil import Chunk
c = collections.Counter(); under = collections.Counter(); heights = collections.Counter(); n = 0
for f in sorted(Path(sys.argv[1]).glob("*.mca")):
    for slot, (ts, comp, raw) in read_region_raw(f).items():
        name, root = R(raw).root()
        if root.get("Status", (0, ""))[1] not in ("minecraft:full", "full"): continue
        ch = Chunk(root); n += 1
        for x in range(0, 16, 4):
            for z in range(0, 16, 4):
                y, b = ch.top(x, z); c[b] += 1; heights[y // 8 * 8] += 1
                under[ch.get(x, y - 3, z)] += 1
print("full chunks:", n)
print("surface:"); [print(f"{v:7d} {k}") for k, v in c.most_common(25)]
print("3 below surface:"); [print(f"{v:7d} {k}") for k, v in under.most_common(12)]
print("height bands:", sorted(heights.items()))
