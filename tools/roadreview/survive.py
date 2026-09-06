"""Walk every standing connector and report where its surface is no longer road (later passes wiped it)."""
import sys, json
sys.path.insert(0, r"G:/GSCraft/repo/tools"); sys.path.insert(0, ".")
from pathlib import Path
from terrain import World, LIQUID
from built import built
ROADK = ("cobblestone","stone","andesite","gravel","concrete","stone_brick","smooth_stone","coarse_dirt","terracotta","hempcrete","blackstone","dirt_path","sand")
def kind(x, z, W):
    y, b = W.top(x, z)
    if b is None: return "?"
    if b in LIQUID: return "W"
    k = b.split(":")[-1]
    if any(t in k for t in ROADK) and "grass" not in k: return "."
    return "X"
W = World(Path(r"G:/GSCraft/scratch/worlds/v8-build"))
tot = miss = 0
print("connector       trace along the centre line ('.' road  'X' not road  'W' water), 8 m per character")
rows = []
for r in sorted(built(), key=lambda r: -r["metres"]):
    s = "".join(kind(x, z, W) for (x, z) in r["polyline"])
    tot += len(s); m = s.count("X") + s.count("W"); miss += m
    # longest run of non-road
    best = cur = 0
    for c in s:
        cur = cur + 1 if c in "XW" else 0; best = max(best, cur)
    rows.append((best*8, r["name"], r["metres"], 100*m/len(s), s))
for worst, n, met, pct, s in sorted(rows, reverse=True):
    tag = "  <<<" if worst >= 24 else ""
    print(f"  {n:14s} {met:6.0f} m  {pct:5.1f}% off-road  worst run {worst:4d} m{tag}")
    if worst >= 24: print(f"                 {s}")
print(f"\noverall: {miss} of {tot} centre-line samples ({100*miss/tot:.1f}%) are no longer a road surface")
