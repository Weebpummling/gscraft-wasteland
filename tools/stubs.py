"""Find every placed build's road and rail stubs (v8 step 7): where its own roads, tracks, pavements or rails reach the
footprint edge. Those are the gates the connector roads hook onto - never the box midpoints.

usage: stubs.py <world dir> <sectors_v8.json> <out dir> [--only id,id]
For each footprint the outer 3-block ring is scanned; columns whose surface block is a road material (stone, andesite,
gravel, cobblestone, concrete, slabs of those, sandstone pavements, rails) are clustered along the edge; each cluster
becomes a stub {side, x, z, width, material}. Writes stubs_v8.json and stubs_v8.png (markers on the settled render).
"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World

ROAD = {"minecraft:gravel", "minecraft:stone", "minecraft:andesite", "minecraft:polished_andesite", "minecraft:cobblestone", "minecraft:mossy_cobblestone",
        "minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:smooth_stone", "minecraft:gray_concrete", "minecraft:light_gray_concrete",
        "minecraft:black_concrete", "minecraft:white_concrete", "minecraft:polished_blackstone", "minecraft:blackstone", "minecraft:basalt",
        "minecraft:smooth_stone_slab", "minecraft:stone_slab", "minecraft:cobblestone_slab", "minecraft:stone_brick_slab", "minecraft:andesite_slab",
        "minecraft:polished_andesite_slab", "minecraft:sandstone", "minecraft:smooth_sandstone", "minecraft:red_sandstone", "minecraft:smooth_red_sandstone",
        "minecraft:dirt_path", "minecraft:coarse_dirt", "minecraft:rail", "minecraft:powered_rail", "minecraft:gray_concrete_powder", "minecraft:terracotta",
        "immersiveengineering:concrete", "immersiveengineering:hempcrete", "chisel:factory/", "factory_blocks:"}
RAIL = {"minecraft:rail", "minecraft:powered_rail", "minecraft:detector_rail", "minecraft:activator_rail"}


def is_road(n):
    if n is None: return False
    return n in ROAD or any(n.startswith(p) for p in ("chisel:factory", "factory_blocks:", "immersiveengineering:concrete", "immersiveengineering:hempcrete"))


def edge_columns(x0, z0, x1, z1, depth=3):
    for d in range(depth):
        for x in range(x0, x1 + 1):
            yield "N", x, z0 + d
            yield "S", x, z1 - d
        for z in range(z0, z1 + 1):
            yield "W", x0 + d, z
            yield "E", x1 - d, z


def leads_inward(w, side, cluster, x0, z0, x1, z1, depth=12):
    """A stub is a road that continues into the build: the same road material must be found at 6 and 12 blocks inward
    from the cluster's centre; a plate edge or a wall base fails this."""
    mid = cluster[len(cluster) // 2]; x, z = mid[2], mid[3]
    dx, dz = {"N": (0, 1), "S": (0, -1), "W": (1, 0), "E": (-1, 0)}[side]
    ok = 0
    for k in (6, depth):
        y, b = w.top(x + dx * k, z + dz * k)
        if b is None: continue
        if is_road(b) or is_road(w.get(x + dx * k, (y or 0) - 1, z + dz * k)): ok += 1
    return ok == 2


def stubs_for(w, p):
    x0, z0, x1, z1 = p["x0"], p["z0"], p["x1"], p["z1"]
    hits = {}
    for side, x, z in edge_columns(x0, z0, x1, z1):
        y, b = w.top(x, z)
        if b is None: continue
        # the surface may be a plant on the road; look one down
        if not is_road(b):
            b2 = w.get(x, y - 1, z)
            if not is_road(b2): continue
            b = b2
        pos = x if side in "NS" else z
        hits.setdefault(side, []).append((pos, b, x, z, y))
    out = []
    for side, lst in hits.items():
        lst.sort()
        cluster = [lst[0]]
        for h in lst[1:] + [None]:
            if h is not None and h[0] - cluster[-1][0] <= 2:
                cluster.append(h); continue
            positions = sorted(set(c[0] for c in cluster))
            width = positions[-1] - positions[0] + 1
            if 3 <= width <= 30 and leads_inward(w, side, cluster, x0, z0, x1, z1):
                mats = {}
                for c in cluster: mats[c[1]] = mats.get(c[1], 0) + 1
                mat = max(mats, key=mats.get)
                mid = cluster[len(cluster) // 2]
                out.append({"side": side, "x": int(mid[2]), "z": int(mid[3]), "y": int(mid[4]), "width": int(width), "material": mat,
                            "rail": any(c[1] in RAIL for c in cluster)})
            if h is not None: cluster = [h]
    return out


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    w = World(Path(a[1])); sectors = json.load(open(a[2]))["sectors"]; out = Path(a[3]); out.mkdir(parents=True, exist_ok=True)
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    result = {}
    for p in sectors:
        if only and p["id"] not in only: continue
        if p["id"] == "camp": continue
        if p.get("group") == "removed": continue
        s = stubs_for(w, p); result[p["id"]] = {"name": p["name"], "rect": [p["x0"], p["z0"], p["x1"], p["z1"]], "stubs": s}
        print(f"  {p['name']:34s} {len(s):2d} stubs: " + ", ".join(f"{q['side']}@({q['x']},{q['z']}) w{q['width']} {q['material'].split(':')[-1]}{' RAIL' if q['rail'] else ''}" for q in s[:6]))
    json.dump(result, open(out / "stubs_v8.json", "w"), indent=1)
    png = Path(r"G:/GSCraft/incoming/census/v8_cell_topdown_settled.png")
    if png.exists():
        im = Image.open(png).convert("RGB"); k = im.width / 5101; d = ImageDraw.Draw(im); X0, Z0 = -3900, -3900
        for sid, r in result.items():
            x0, z0, x1, z1 = r["rect"]; d.rectangle([(x0 - X0) * k, (z0 - Z0) * k, (x1 - X0) * k, (z1 - Z0) * k], outline=(255, 255, 255), width=1)
            for q in r["stubs"]:
                px, pz = (q["x"] - X0) * k, (q["z"] - Z0) * k; col = (255, 140, 40) if q["rail"] else (255, 240, 80)
                d.ellipse([px - 4, pz - 4, px + 4, pz + 4], fill=col, outline=(0, 0, 0))
        im.save(out / "stubs_v8.png"); print("->", out / "stubs_v8.png")


if __name__ == "__main__":
    main(sys.argv)
