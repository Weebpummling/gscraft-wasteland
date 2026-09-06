"""Does each connector's inner end actually meet the build's own pavement?"""
import sys, json, math
sys.path.insert(0, r"G:/GSCraft/repo/tools"); sys.path.insert(0, ".")
from pathlib import Path
from terrain import World, LIQUID
from built import built
ROADMAT = {"cobblestone","stone","andesite","polished_andesite","gravel","light_gray_concrete","stone_bricks",
 "cracked_stone_bricks","stone_slab","smooth_stone_slab","cobblestone_slab","mossy_cobblestone","gray_concrete",
 "polished_blackstone","stone_brick_slab","andesite_slab","smooth_stone","black_concrete","coarse_dirt","white_concrete",
 "dirt_path","andesite_wall","concrete","terracotta","hempcrete","asphalt"}
def roadish(b):
    if b is None: return False
    k = b.split(":")[-1]
    return k in ROADMAT or any(t in k for t in ("concrete","asphalt","hempcrete"))
W = World(Path(r"G:/GSCraft/scratch/worlds/v8-build"))
sec = {p["id"]: p for p in json.load(open(r"G:/GSCraft/repo/buildmap/plan_v8/sectors_v8.json"))["sectors"]}
def run(x0, z0, dx, dz, n):
    """how far from (x0,z0) along (dx,dz) until we hit a road surface; -1 if never within n"""
    for k in range(n+1):
        b = W.top(x0+dx*k, z0+dz*k)[1]
        if roadish(b): return k
    return -1
print("connector      inner end        outer end        grass run at inner end / outer end")
bad = []
for r in sorted(built(), key=lambda r: r["name"]):
    a, b = r["polyline"][0], r["polyline"][-1]
    ia = 1 if roadish(W.top(*a)[1]) else 0
    # look outward from the inner end, away from the route, for the build's pavement
    p1 = r["polyline"][min(3, len(r["polyline"])-1)]
    dx, dz = a[0]-p1[0], a[1]-p1[1]; L = max(abs(dx), abs(dz)) or 1; dx, dz = round(dx/L), round(dz/L)
    da = run(a[0]+dx, a[1]+dz, dx, dz, 60)
    q1 = r["polyline"][max(len(r["polyline"])-4, 0)]
    ex, ez = b[0]-q1[0], b[1]-q1[1]; L = max(abs(ex), abs(ez)) or 1; ex, ez = round(ex/L), round(ez/L)
    db = run(b[0]+ex, b[1]+ez, ex, ez, 60)
    fa = "touches" if da == 0 else (f"{da} m of grass" if da > 0 else ">60 m NO ROAD")
    fb = "touches" if db == 0 else (f"{db} m of grass" if db > 0 else ">60 m NO ROAD")
    mark = "  <<<" if (da != 0 or db != 0) else ""
    print(f"  {r['name']:14s} {str(tuple(a)):>16s} {str(tuple(b)):>16s}   {fa:16s} / {fb:16s}{mark}")
    if da != 0 or db != 0: bad.append((r["name"], da, db))
print(f"\n{len(bad)} of {len(built())} connectors do not meet pavement at one or both ends")
