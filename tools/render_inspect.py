"""inspect2.py <world> <label> x0 z0 x1 z1 ppb  -> hillshaded top-down render + npz (sy, gy, wtop, built, sname) for review.
Fast: block flags are computed per palette entry, then indexed. built = a man-made block (not natural/plant/water/air)
anywhere in the column above y 30."""
import sys, collections, time
import numpy as np
sys.path.insert(0, r"G:\GSCraft\repo\tools")
from pathlib import Path
from transplant import read_region_raw, R, slot_of, region_of
from applyheight import decode_chunk
from terrain import NATURAL, PLANT, LIQUID
from PIL import Image
from scipy import ndimage

W = Path(sys.argv[1]); LABEL = sys.argv[2]; X0, Z0, X1, Z1 = map(int, sys.argv[3:7]); PPB = int(sys.argv[7])
OUT = Path(r"G:\GSCraft\incoming\census")
H, Wd = Z1 - Z0 + 1, X1 - X0 + 1
sy = np.full((H, Wd), -999, np.int16); gy = np.full((H, Wd), -999, np.int16); wtop = np.full((H, Wd), -999, np.int16)
built = np.zeros((H, Wd), bool); sname = np.zeros((H, Wd), np.int32)   # index into NAMES
NAMES = ["", ]; NIDX = {"": 0}
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
PLANT_K = ("grass", "fern", "bush", "flower", "dandelion", "poppy", "leaves", "log", "vine", "sapling", "kelp", "seagrass", "lily", "wood", "azalea", "mushroom", "snow", "cobweb", "tulip", "orchid", "allium", "daisy", "cornflower", "lily_of", "rose", "peony", "lilac", "sunflower", "bamboo", "cactus", "dead_bush", "moss_carpet", "pumpkin", "melon", "wheat", "carrot", "potato", "beetroot", "sugar_cane", "torchflower", "pitcher")
def is_plant(n):
    k = n.split(":")[-1]
    if n in PLANT: return True
    if k in ("grass_block", "mangrove_roots", "muddy_mangrove_roots"): return False
    return n.startswith("minecraft:") and any(t in k for t in PLANT_K)
YS = np.arange(-64, 320, dtype=np.int16)[:, None, None]
t0 = time.time(); regs = {}; nchunks = 0
for cx in range(X0 >> 4, (X1 >> 4) + 1):
    for cz in range(Z0 >> 4, (Z1 >> 4) + 1):
        rk = region_of(cx, cz)
        if rk not in regs:
            p = W / "region" / f"r.{rk[0]}.{rk[1]}.mca"; regs[rk] = read_region_raw(p) if p.exists() else {}
        ent = regs[rk].get(slot_of(cx, cz))
        if not ent: continue
        name, root = R(ent[2]).root()
        try: ids, pal, tmpl = decode_chunk(root)
        except Exception: continue
        nchunks += 1
        names = [e["Name"][1] for e in pal]
        n = len(names)
        f_air = np.array([nm in AIRS for nm in names] + [True]); f_water = np.array([nm in LIQUID or nm == "minecraft:ice" for nm in names] + [False])
        f_plant = np.array([is_plant(nm) for nm in names] + [False])
        f_nat = np.array([(nm in NATURAL) or is_plant(nm) or nm in LIQUID or nm in AIRS or nm.endswith("_leaves") or nm.endswith("_log") for nm in names] + [True])
        for nm in names:
            if nm not in NIDX: NIDX[nm] = len(NAMES); NAMES.append(nm)
        gidx = np.array([NIDX[nm] for nm in names] + [0], np.int32)
        ids2 = np.where(ids < 0, n, ids)
        air = f_air[ids2]; water = f_water[ids2]; plant = f_plant[ids2]; nat = f_nat[ids2]
        top = np.where(~air, YS, -999).max(axis=0)
        ground = np.where(~air & ~water & ~plant, YS, -999).max(axis=0)
        wt = np.where(water & (YS > ground), YS, -999).max(axis=0)
        man = (~nat & (YS > 30)).any(axis=0)
        topidx = np.clip(top.astype(np.int32) + 64, 0, 383)
        tn = gidx[ids2[topidx, np.arange(16)[:, None], np.arange(16)[None, :]]]
        tn[top <= -999] = 0
        z0c, x0c = cz * 16, cx * 16
        zs = slice(max(z0c, Z0) - Z0, min(z0c + 15, Z1) - Z0 + 1); xs = slice(max(x0c, X0) - X0, min(x0c + 15, X1) - X0 + 1)
        lzs = slice(max(z0c, Z0) - z0c, min(z0c + 15, Z1) - z0c + 1); lxs = slice(max(x0c, X0) - x0c, min(x0c + 15, X1) - x0c + 1)
        sy[zs, xs] = top[lzs, lxs]; gy[zs, xs] = ground[lzs, lxs]; wtop[zs, xs] = wt[lzs, lxs]; built[zs, xs] = man[lzs, lxs]; sname[zs, xs] = tn[lzs, lxs]
print(f"{nchunks} chunks decoded in {time.time()-t0:.0f}s")
np.savez_compressed(OUT / f"{LABEL}_inspect.npz", sy=sy, gy=gy, wtop=wtop, built=built, sname=sname, names=np.array(NAMES, dtype=object))
def col(n):
    k = n.split(":")[-1]
    if k in ("water", "ice"): return (40, 80, 180)
    if k == "lava": return (230, 120, 20)
    if k == "grass_block": return (90, 140, 60)
    if "leaves" in k: return (45, 100, 40)
    if k in ("dirt", "coarse_dirt", "rooted_dirt", "podzol"): return (110, 80, 50)
    if k in ("sand", "sandstone", "smooth_sandstone"): return (215, 205, 150)
    if k in ("red_sand", "red_sandstone"): return (190, 110, 60)
    if k in ("gravel",): return (130, 125, 120)
    if k in ("stone", "andesite", "cobblestone", "diorite", "granite", "tuff"): return (120, 120, 120)
    if "terracotta" in k: return (150, 90, 60)
    if k in ("grass", "short_grass", "tall_grass", "fern", "large_fern"): return (95, 150, 65)
    if "concrete" in k or "quartz" in k: return (200, 200, 205)
    if k == "": return (0, 0, 0)
    h = hash(k) & 0xffffff; return (90 + (h & 127), 40 + ((h >> 8) & 63), 90 + ((h >> 16) & 127))   # man-made: magenta-ish
g = gy.astype(np.float32); g[gy <= -999] = np.nan; gf = np.nan_to_num(g, nan=float(np.nanmean(g)))
dx = ndimage.sobel(gf, axis=1) / 8; dz = ndimage.sobel(gf, axis=0) / 8
shade = np.clip(1.0 + 0.35 * (dx - dz), 0.45, 1.5)
tint = np.where(gy > -999, np.clip(1.0 + 0.03 * (gy.astype(np.float32) - 65), 0.6, 1.3), 1.0)
pal_rgb = np.array([col(n) for n in NAMES], np.float32)
im = pal_rgb[sname] * (shade * tint)[..., None]
im[built] = im[built] * 0.7 + np.array([120, 0, 160]) * 0.3       # built columns: purple cast
img = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).resize((Wd * PPB, H * PPB), Image.NEAREST)
px = img.load()
for x in range(X0, X1 + 1):
    if x % 64 == 0:
        for iz in range(0, H * PPB, 2): px[(x - X0) * PPB, iz] = (255, 255, 255)
for z in range(Z0, Z1 + 1):
    if z % 64 == 0:
        for ix in range(0, Wd * PPB, 2): px[ix, (z - Z0) * PPB] = (255, 255, 255)
img.save(OUT / f"{LABEL}_inspect.png"); print("->", OUT / f"{LABEL}_inspect.png", img.size, "(white grid every 64 blocks)")
wm = wtop > -999; lab, n = ndimage.label(wm); sizes = ndimage.sum(wm, lab, range(1, n + 1))
print(f"water bodies: {n}, water columns {int(wm.sum())}, built columns {int(built.sum())}")
for i in np.argsort(-sizes)[:25]:
    m = lab == i + 1; zz, xx = np.nonzero(m); lv = collections.Counter(wtop[m].tolist()).most_common(3)
    print(f"  size {int(sizes[i]):6d}  x {xx.min()+X0}..{xx.max()+X0}  z {zz.min()+Z0}..{zz.max()+Z0}  levels {lv}")
vals = gy[gy > -999]
print("ground y histogram:", sorted(collections.Counter(vals.tolist()).items()))
cnt = collections.Counter(sname[sy > -999].tolist())
print("surface names:", [(NAMES[k], v) for k, v in cnt.most_common(30)])
