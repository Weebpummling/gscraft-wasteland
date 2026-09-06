"""The labelled world map of the v8 cell, rendered from a render_inspect.py npz.

Colours the surface by what is actually on it (water, forest, grass, sand, rock, road, building), hillshades it from the
ground heights, then draws the coordinate grid, the world border, every named place and the road classes.

usage: worldmap.py <inspect.npz> <out.png> [--scale 2] [--no-labels] [--no-roads]
`--scale N` is blocks per pixel (2 gives a 2550 x 2300 map of the cell).
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8")
X0, Z0 = -3900, -3900
BORDER = (-1350.5, -1600.5, 5200.0)          # centre x, centre z, size (tools/worldborder.py)

C = {"water": (58, 96, 140), "shallow": (78, 122, 165), "forest": (58, 82, 48), "scrub": (96, 112, 70),
     "grass": (118, 132, 84), "sand": (176, 166, 122), "rock": (122, 120, 114), "road": (74, 70, 66),
     "track": (122, 108, 84), "build": (96, 92, 88), "concrete": (140, 138, 132), "none": (40, 40, 40),
     "netroad": (196, 188, 170), "nettrack": (170, 150, 116)}
LABELS = {"hub": "Novo Expograd", "novo": "Novo Industrial", "plaza": "Financial Plaza", "biogen": "Bio Gen",
          "skad": "Skadowsky", "mega": "Mega-base", "indu": "Industrial District", "hemp": "Hempcrete Compound",
          "lib": "Library", "runway": "Runway", "camp": "Camp"}


def font(size, bold=False):
    for n in (("arialbd.ttf" if bold else "arial.ttf"), "segoeui.ttf"):
        try: return ImageFont.truetype(f"C:/Windows/Fonts/{n}", size)
        except Exception: pass
    return ImageFont.load_default()


def classify(d):
    sn = d["sname"]; names = list(d["names"]); wt = d["wtop"].astype(np.int32); gy = d["gy"].astype(np.int32)
    built = d["built"]
    def ids(test): return np.array([i for i, n in enumerate(names) if test(n)], np.int32)
    def has(n, *k): return any(t in n.split(":")[-1] for t in k)
    forest = np.isin(sn, ids(lambda n: has(n, "leaves", "log", "wood", "mushroom_block")))
    scrub = np.isin(sn, ids(lambda n: has(n, "fern", "tall_grass", "bush", "vine", "moss", "podzol", "bamboo", "cactus", "dead_bush")))
    grass = np.isin(sn, ids(lambda n: has(n, "grass", "dirt", "farmland", "mycelium", "clay", "mud") and not has(n, "coarse")))
    sand = np.isin(sn, ids(lambda n: has(n, "sand", "red_sand")))
    track = np.isin(sn, ids(lambda n: has(n, "gravel", "coarse_dirt", "dirt_path")))
    road = np.isin(sn, ids(lambda n: has(n, "cobblestone", "andesite", "stone", "asphalt", "blackstone", "brick") and not has(n, "sand")))
    conc = np.isin(sn, ids(lambda n: has(n, "concrete", "terracotta", "hempcrete", "iron", "glass", "factory")))
    water = wt > -999
    img = np.full(sn.shape + (3,), C["none"], np.uint8)
    for m, k in ((grass, "grass"), (scrub, "scrub"), (sand, "sand"), (forest, "forest"),
                 (conc, "concrete"), (road, "road"), (track, "track")):
        img[m] = C[k]
    img[built & ~water] = np.where(road[built & ~water][:, None], np.array(C["road"]), np.array(C["build"]))
    shallow = water & (gy > -999) & (wt - gy <= 2)
    img[water] = C["water"]; img[shallow] = C["shallow"]
    return img, gy, water


def road_overlay(d):
    """The road network as the map should show it: the source maps' roads that are still paved, plus every
    carriageway roads.py / roadpatch.py laid (their protect masks) and the bridge decks."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from roadmask import RoadMask
    sn = d["sname"]; names = list(d["names"]); wt = d["wtop"].astype(np.int32)
    H, W = sn.shape
    mat = np.isin(sn, np.array([i for i, n in enumerate(names)
                                if any(t in n.split(":")[-1] for t in ("cobblestone", "stone", "andesite", "gravel",
                                "concrete", "coarse_dirt", "blackstone", "dirt_path", "brick"))
                                and "grass" not in n], np.int32))
    water = wt > -999
    cls = np.load(CEN / "classes.npy")
    laid = RoadMask(0).array()[:H, :W]
    net = (((cls == 1) & mat) | laid) & ~water
    track = np.isin(sn, np.array([i for i, n in enumerate(names)
                                  if any(t in n.split(":")[-1] for t in ("gravel", "coarse_dirt", "dirt_path"))], np.int32))
    return net, net & track


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    d = np.load(a[1], allow_pickle=True)
    S = int(a[a.index("--scale") + 1]) if "--scale" in a else 2
    img, gy, water = classify(d)
    H, W = gy.shape
    g = ndimage.gaussian_filter(np.where(gy > -999, gy.astype(np.float32), 62), 1.6)
    dz, dx = np.gradient(g)
    sh = np.clip(0.80 + 0.34 * (dx * 0.7 - dz * 0.7) / 2.6, 0.45, 1.30)
    sh[water] = 1.0
    out = np.clip(img.astype(np.float32) * sh[..., None], 0, 255).astype(np.uint8)
    if "--no-roads" not in a:
        net, trk = road_overlay(d)
        net = ndimage.binary_dilation(net, iterations=max(S // 2, 1))       # so a 5-wide track survives the downscale
        trk = ndimage.binary_dilation(trk, iterations=max(S // 2, 1)) & net
        out[net] = C["netroad"]; out[trk] = C["nettrack"]
    im = Image.fromarray(out).resize((W // S, H // S), Image.LANCZOS)
    dr = ImageDraw.Draw(im, "RGBA")
    def px(x, z): return ((x - X0) // S, (z - Z0) // S)
    if "--no-labels" not in a:
        f_grid, f_small, f_big = font(11), font(13, True), font(19, True)
        for x in range(-3500, 1201, 500):                                   # coordinate grid
            u = px(x, 0)[0]; dr.line([u, 0, u, im.size[1]], fill=(255, 255, 255, 34))
            dr.text((u + 3, 4), f"x {x}", font=f_grid, fill=(255, 255, 255, 150))
        for z in range(-3500, 701, 500):
            v = px(0, z)[1]; dr.line([0, v, im.size[0], v], fill=(255, 255, 255, 34))
            dr.text((4, v + 3), f"z {z}", font=f_grid, fill=(255, 255, 255, 150))
        cx, cz, sz = BORDER                                                 # world border
        dr.rectangle([px(cx - sz / 2, cz - sz / 2), px(cx + sz / 2, cz + sz / 2)], outline=(240, 90, 90, 210), width=2)
        for p in json.load(open(PLAN / "sectors_v8.json"))["sectors"]:
            if p.get("group") == "removed": continue
            a0, b0 = px(p["x0"], p["z0"]); a1, b1 = px(p["x1"], p["z1"])
            named = p["id"] in LABELS
            dr.rectangle([a0, b0, a1, b1], outline=(255, 255, 255, 190 if named else 120))
            t = LABELS.get(p["id"], p["id"].replace("old", "farm "))
            fnt = f_big if named else f_small
            w = dr.textlength(t, font=fnt); h = fnt.size
            tx, ty = (a0 + a1) // 2 - w / 2, b0 - h - 5
            dr.rectangle([tx - 4, ty - 2, tx + w + 4, ty + h + 3], fill=(20, 22, 20, 165))
            dr.text((tx, ty), t, font=fnt, fill=(255, 255, 255))
        # legend and scale
        leg = [("water", "water"), ("forest", "forest"), ("grass", "open ground"), ("sand", "sand and shore"),
               ("netroad", "paved road"), ("nettrack", "gravel track"), ("build", "buildings"), ("concrete", "concrete and metal")]
        bw, bh = 210, 20 + len(leg) * 17 + 46
        dr.rectangle([12, im.size[1] - bh - 12, 12 + bw, im.size[1] - 12], fill=(18, 20, 18, 205))
        dr.text((22, im.size[1] - bh - 4), "GSCraft wasteland, v8", font=font(15, True), fill=(255, 255, 255))
        for k, (key, t) in enumerate(leg):
            y = im.size[1] - bh + 16 + k * 17
            dr.rectangle([22, y, 36, y + 12], fill=C[key]); dr.text((44, y - 1), t, font=f_small, fill=(226, 226, 220))
        y = im.size[1] - 40
        dr.line([22, y, 22 + 500 // S, y], fill=(255, 255, 255), width=3)
        dr.text((26 + 500 // S, y - 8), "500 m", font=f_small, fill=(255, 255, 255))
        dr.text((22, y + 9), "world border: 50 m outside this map's edge", font=f_small, fill=(240, 150, 150))
    im.save(a[2])
    print(f"{a[2]}  {im.size[0]} x {im.size[1]} px, {S} blocks per pixel")


if __name__ == "__main__":
    main(sys.argv)
