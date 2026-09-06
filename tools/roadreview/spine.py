import sys
sys.path.insert(0, r"G:/GSCraft/repo/tools")
from pathlib import Path
from terrain import World, LIQUID
ROADK = ("cobblestone","stone","andesite","gravel","concrete","stone_bricks","smooth_stone","coarse_dirt","terracotta","hempcrete","blackstone","dirt_path","asphalt")
def roadish(b):
    if b is None: return False
    k = b.split(":")[-1]
    return any(t in k for t in ROADK) and "grass" not in k
W = World(Path(r"G:/GSCraft/scratch/worlds/v8-build"))
def scan(label, x0, x1, zs, axis="x"):
    print(f"\n### {label}")
    ok = []
    for v in range(x0, x1+1, 2):
        hit = False; ys = None
        for z in zs:
            if axis == "x": b = W.top(v, z)
            else: b = W.top(z, v)
            if roadish(b[1]): hit = True; ys = b[0]; break
            if b[1] in LIQUID: hit = None
        ok.append((v, hit, ys))
    runs = []; cur = None
    for v, hit, ys in ok:
        st = "road" if hit else ("water" if hit is None else "gap")
        if cur and cur[0] == st: cur[2] = v
        else:
            if cur: runs.append(cur)
            cur = [st, v, v]
    if cur: runs.append(cur)
    for st, a, b in runs:
        if st == "road" and b-a < 900: print(f"  road  {a:6d}..{b:6d}  ({b-a+1:4d} m)")
        elif st != "road": print(f"  {st.upper():5s} {a:6d}..{b:6d}  ({b-a+1:4d} m)   <<<" if b-a >= 6 else f"  {st:5s} {a:6d}..{b:6d}  ({b-a+1:4d} m)")
        else: print(f"  road  {a:6d}..{b:6d}  ({b-a+1:4d} m)")
scan("east-west trunk, z -200..-212, x -2600..-500", -2600, -500, range(-212, -199, 2))
scan("Skadowsky east connector, x -616..-624, z -950..-200", -950, -200, range(-624, -615, 2), axis="z")
scan("Skadowsky west connector, x -1232..-1240, z -950..-190", -950, -190, range(-1240, -1231, 2), axis="z")
