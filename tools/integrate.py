"""Integrate a transplanted sector into the landscape (v8 step 6, second pass; owner: "the desert city is the part I want
preserved, the surrounding terrain can be discarded").

For a footprint the build itself is kept column by column (a mask: the man-made columns, courtyards closed, plus a small
apron); every other column inside the footprint - and every open column in a 48-block margin around it - is replaced by
the local landscape: the spine world's terrain with the relief plan applied, exactly what stood there before the
transplant and its edge grading. A band around the build is graded so the local ground meets the build's own floor level,
with low-frequency noise so no contour terraces form. The hub's kept components are lifted so their floors sit on the land.

usage: integrate.py <build world> <fresh transplant world> <sector id: hub|skad> [--dry-run]
  <fresh transplant world>: a scratch world holding only the sector's clean transplant (runplan.py with
  buildmap/plan_v8/transplant_plan_v8_fresh.json), so damage from earlier passes inside the footprint is not carried over.
Mask rules: hub  - man-made = a block in the top 9 of the column outside the desert's natural block set (sand, red sand,
                   sandstone, terracottas, stone, dirt, gravel, clay, water, plants, ores); specks under 60 columns dropped;
                   courtyards closed (r 10); apron 3; the source map's border fence along the east edge dropped; every
                   kept component lifted so its floor meets the land.
             skad - the Skadowsky map's own open terrain (ground above y 40, components of 2000+ columns) plus the man-made
                   columns standing on it; the flat plate (y 38, source y 3) the map was built on and the template displays
                   parked on it are discarded; closed r 4; apron 2.
Margin columns inside another sector's footprint or carrying anything man-made are never touched.
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, key_of, X0 as CX0, Z0 as CZ0, T_BYTE, T_STRING, T_LIST, T_COMPOUND
from terrain import NATURAL, PLANT, LIQUID

CENSUS = Path(r"G:/GSCraft/incoming/census"); HEIGHT = CENSUS / "heightplan" / "height.npy"
NAT_WORLD = Path(r"G:/GSCraft/scratch/upgrade/pripyat_after/world")
SECTORS_JSON = HERE.parent / "buildmap" / "plan_v8" / "sectors_v8.json"
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
PLANT_K = ("grass", "fern", "bush", "flower", "dandelion", "poppy", "leaves", "log", "vine", "sapling", "kelp", "seagrass", "lily", "wood",
           "azalea", "mushroom", "snow", "cobweb", "tulip", "orchid", "allium", "daisy", "cornflower", "rose", "peony", "lilac", "sunflower",
           "bamboo", "cactus", "dead_bush", "moss_carpet", "pumpkin", "melon", "wheat", "carrot", "potato", "beetroot", "sugar_cane", "torchflower",
           "bluet", "oxeye", "blossom")
DESERT_NATURAL = {"minecraft:sand", "minecraft:red_sand", "minecraft:sandstone", "minecraft:red_sandstone", "minecraft:grass_block", "minecraft:dirt",
                  "minecraft:coarse_dirt", "minecraft:gravel", "minecraft:clay", "minecraft:stone", "minecraft:andesite", "minecraft:diorite",
                  "minecraft:granite", "minecraft:bedrock", "minecraft:deepslate", "minecraft:tuff", "minecraft:calcite", "minecraft:water",
                  "minecraft:ice", "minecraft:lava", "minecraft:snow_block", "minecraft:obsidian", "minecraft:magma_block", "minecraft:podzol",
                  "minecraft:mycelium", "minecraft:packed_ice", "minecraft:dripstone_block", "minecraft:mud"} | AIRS
ROAD_TOPS = {"minecraft:stone", "minecraft:andesite", "minecraft:gravel", "minecraft:smooth_stone", "minecraft:stone_bricks", "minecraft:cobblestone"}
SECTORS = {
    "hub": dict(rect=(-3376, -624, -2545, 15), mode="manmade", close=10, apron=3, min_comp=60, band=32, edge_drop=20, lift=True),
    "skad": dict(rect=(-1088, -1488, -625, -737), mode="plate", close=4, apron=2, min_comp=0, band=40),
}
MARGIN = 48
YS = np.arange(-64, 320, dtype=np.int32)[:, None, None]


def is_plant(n):
    k = n.split(":")[-1]
    if n in PLANT: return True
    if k in ("grass_block", "mangrove_roots", "muddy_mangrove_roots"): return False
    return n.startswith("minecraft:") and any(t in k for t in PLANT_K)


def is_natural(n):
    return n in NATURAL or is_plant(n) or n in LIQUID or n in AIRS or n.endswith("_leaves") or n.endswith("_log") or "ore" in n.split(":")[-1] or n in DESERT_NATURAL


def is_desert_natural(n):
    return n in DESERT_NATURAL or n.endswith("terracotta") or is_plant(n) or n.endswith("_leaves") or n.endswith("_log") or "ore" in n.split(":")[-1]


def smoothstep(s):
    s = np.clip(s, 0, 1); return s * s * (3 - 2 * s)


def value_noise(shape, cell, amp, seed):
    rng = np.random.default_rng(seed)
    g = rng.uniform(-1, 1, (shape[0] // cell + 3, shape[1] // cell + 3))
    return ndimage.zoom(g, cell, order=3)[:shape[0], :shape[1]] * amp


class Regions:
    def __init__(self, world): self.world = Path(world); self.cache = {}
    def chunk(self, cx, cz):
        rk = region_of(cx, cz)
        if rk not in self.cache:
            p = self.world / "region" / f"r.{rk[0]}.{rk[1]}.mca"; self.cache[rk] = read_region_raw(p) if p.exists() else {}
        ent = self.cache[rk].get(slot_of(cx, cz))
        if not ent: return None, None, None
        name, root = R(ent[2]).root(); return ent, name, root


def column_stats(ids, pal, desert=False):
    """-> ground (top solid non-plant non-water), top, wtop, manmade, road_top (16x16 each) for one chunk."""
    names = [e["Name"][1] for e in pal]; n = len(names)
    f_air = np.array([nm in AIRS for nm in names] + [True]); f_water = np.array([nm in LIQUID or nm == "minecraft:ice" for nm in names] + [False])
    f_plant = np.array([is_plant(nm) for nm in names] + [False])
    f_nat = np.array([(is_desert_natural if desert else is_natural)(nm) for nm in names] + [True])
    f_road = np.array([("concrete" in nm or nm in ROAD_TOPS) for nm in names] + [False])
    ids2 = np.where(ids < 0, n, ids)
    air = f_air[ids2]; water = f_water[ids2]; plant = f_plant[ids2]; nat = f_nat[ids2]
    top = np.where(~air, YS, -999).max(axis=0)
    ground = np.where(~air & ~water & ~plant, YS, -999).max(axis=0)
    wtop = np.where(water & (YS > ground), YS, -999).max(axis=0)
    man = (~nat & (YS >= top[None] - 8) & (YS <= top[None])).any(axis=0)
    road_top = f_road[ids2[np.clip(top + 64, 0, 383), np.arange(16)[:, None], np.arange(16)[None, :]]]
    return ground, top, wtop, man, road_top


def relief_column_shift(col, gi, dy):
    """applyheight's whole-column shift for one column (col: 384 ids, gi: index of the ground block)."""
    base = max(gi - 3, 1)
    if dy > 0:
        col[base + dy:384] = col[base:384 - dy].copy()
        col[base:base + dy] = col[base] if col[base] >= 0 else col[gi]
    else:
        k = -dy
        col[base - k:384 - k] = col[base:384].copy(); col[384 - k:384] = -1


def merge_palettes(pal_a, pal_b):
    pal, index = [], {}
    def add(p):
        m = np.zeros(len(p) + 1, np.int32) - 1
        for i, e in enumerate(p):
            k = key_of(e)
            if k not in index: index[k] = len(pal); pal.append(e)
            m[i] = index[k]
        return m
    ma = add(pal_a); mb = add(pal_b); return pal, ma, mb


FLAT_PAL = [{"Name": (T_STRING, n)} for n in ("minecraft:air", "minecraft:bedrock", "minecraft:stone", "minecraft:dirt", "minecraft:grass_block")]
def flat_chunk(y_ground=65):
    col = np.zeros(384, np.int32); col[0] = 1; col[1:y_ground + 60] = 2; col[y_ground + 60:y_ground + 64] = 3; col[y_ground + 64] = 4
    return np.repeat(np.repeat(col[:, None, None], 16, 1), 16, 2)


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    build, fresh, sid = Path(a[1]), Path(a[2]), a[3]; dry = "--dry-run" in a
    cfg = SECTORS[sid]; x0, z0, x1, z1 = cfg["rect"]
    ax0, az0, ax1, az1 = x0 - MARGIN, z0 - MARGIN, x1 + MARGIN, z1 + MARGIN
    H, Wd = az1 - az0 + 1, ax1 - ax0 + 1
    cls = np.load(CENSUS / "classes.npy"); gnd = np.load(CENSUS / "ground_y.npy").astype(np.int32); tgt = np.load(HEIGHT).astype(np.int32)
    delta_all = tgt - gnd; delta_all[np.isin(cls, (1, 2, 3, 4, 7))] = 0
    def census(arr, x, z): return arr[z - CZ0, x - CX0]
    others = np.zeros((H, Wd), bool)
    for p in json.load(open(SECTORS_JSON))["sectors"]:
        if p["id"] == sid: continue
        ox0, oz0, ox1, oz1 = max(p["x0"], ax0), max(p["z0"], az0), min(p["x1"], ax1), min(p["z1"], az1)
        if ox0 <= ox1 and oz0 <= oz1: others[oz0 - az0:oz1 - az0 + 1, ox0 - ax0:ox1 - ax0 + 1] = True
    t0 = time.time()
    R_build, R_fresh, R_nat = Regions(build), Regions(fresh), Regions(NAT_WORLD)
    g_base = np.full((H, Wd), -999, np.int32); w_base = np.full((H, Wd), -999, np.int32); man = np.zeros((H, Wd), bool)
    g_nat = np.full((H, Wd), -999, np.int32); w_nat = np.full((H, Wd), -999, np.int32)
    inside = np.zeros((H, Wd), bool); inside[z0 - az0:z1 - az0 + 1, x0 - ax0:x1 - ax0 + 1] = True
    nofresh = np.zeros((H, Wd), bool); chunks = {}; missing = 0
    # ---- pass 1: per-column facts. base = the fresh transplant inside the footprint, the build world in the margin
    for cx in range(ax0 >> 4, (ax1 >> 4) + 1):
        for cz in range(az0 >> 4, (az1 >> 4) + 1):
            bx, bz = cx * 16 - ax0, cz * 16 - az0
            zs, xs = slice(max(bz, 0), min(bz + 16, H)), slice(max(bx, 0), min(bx + 16, Wd))
            lzs, lxs = slice(zs.start - bz, zs.stop - bz), slice(xs.start - bx, xs.stop - bx)
            in_fp = x0 <= cx * 16 <= x1 and z0 <= cz * 16 <= z1
            ent, name, root = R_fresh.chunk(cx, cz) if in_fp else (None, None, None)
            has_fresh = root is not None
            if not has_fresh:
                ent, name, root = R_build.chunk(cx, cz)
                if root is None: continue
                if in_fp: missing += 1
            ids, pal, tmpl = decode_chunk(root)
            g, top, wt, m, rt = column_stats(ids, pal, desert=(cfg["mode"] == "manmade" and has_fresh))
            if has_fresh and cfg.get("edge_drop"):                  # hub: the source map's border fence along the east edge goes; its roads stay
                xs_abs = np.arange(cx * 16, cx * 16 + 16)[None, :]
                m = m & ~((xs_abs >= x1 - cfg["edge_drop"]) & ~rt)
            if in_fp and not has_fresh: m[:] = False; g[:] = -999; wt[:] = -999; nofresh[zs, xs] = True
            g_base[zs, xs] = g[lzs, lxs]; w_base[zs, xs] = wt[lzs, lxs]; man[zs, xs] = m[lzs, lxs]
            nent, nname, nroot = R_nat.chunk(cx, cz)
            if nroot is None or "sections" not in nroot:
                nids, npal, ntmpl, nroot = flat_chunk(), list(FLAT_PAL), tmpl, None
            else:
                nids, npal, ntmpl = decode_chunk(nroot)
                for lz in range(16):
                    for lx in range(16):
                        x, z = cx * 16 + lx, cz * 16 + lz
                        dy = int(census(delta_all, x, z))
                        if dy: relief_column_shift(nids[:, lz, lx], int(census(gnd, x, z)) + 64, dy)
            ng, _, nw, _, _ = column_stats(nids, npal)
            g_nat[zs, xs] = ng[lzs, lxs]; w_nat[zs, xs] = nw[lzs, lxs]
            chunks[(cx, cz)] = (ent, name, root, ids, pal, tmpl, nroot, nids, npal, ntmpl, has_fresh, in_fp)
    print(f"pass 1: {len(chunks)} chunks read in {time.time()-t0:.0f}s ({missing} footprint chunks without a source chunk: landscape only); man-made columns in the footprint {int((man & inside).sum()):,}")
    # ---- keep mask
    small = np.zeros_like(man)
    if cfg["mode"] == "manmade":
        mask = man & inside
        lab, n = ndimage.label(mask); sizes = ndimage.sum(mask, lab, range(1, n + 1))
        small = np.isin(lab, np.nonzero(sizes < cfg["min_comp"])[0] + 1); mask[small] = False
        print(f"  {int((sizes < cfg['min_comp']).sum())} man-made specks under {cfg['min_comp']} columns dropped ({int(small.sum()):,} columns)")
    else:
        mask = inside & ~man & ((g_base > 40) | (w_base > 40)) & (g_base > -999)      # the map's open terrain
        lab, n = ndimage.label(mask); sizes = ndimage.sum(mask, lab, range(1, n + 1))
        mask &= ~np.isin(lab, np.nonzero(sizes < 2000)[0] + 1)                       # display pads on the plate are not terrain
    disk = lambda r: (lambda yy, xx: (xx * xx + yy * yy) <= r * r)(*np.mgrid[-r:r + 1, -r:r + 1])
    if cfg["close"]: mask = ndimage.binary_closing(mask, disk(cfg["close"]), border_value=0)
    if cfg["mode"] == "manmade": mask |= man & inside & ~small
    else:
        lab, n = ndimage.label((man & inside) | mask); keep_lab = np.unique(lab[mask & (g_base > 40)])
        mask |= np.isin(lab, keep_lab[keep_lab > 0]) & man & inside                    # man-made columns standing on the map's terrain
    if cfg["apron"]: mask = ndimage.binary_dilation(mask, disk(cfg["apron"]))
    mask &= inside & ~nofresh
    if cfg["mode"] == "manmade": mask &= ~((w_base > -999) & ~man)                    # no moats: imported water in the apron is landscape
    else: mask &= ~((g_base <= 40) & ~man)                                             # no plate columns in the apron (a trench at y 38 along the map edge, water-filled or not)
    # margin: open landscape columns outside the footprint are restored too (the old graded ring), builds and other sectors stay
    keep = mask | (~inside & (man | others | (g_nat <= -999)))
    restore = ~keep
    # lift (hub): every kept component is shifted vertically so its own floor (open apron columns) meets the local land
    lift = np.zeros((H, Wd), np.int32); open_in = mask & ~man & (g_base > -999)
    if cfg.get("lift"):
        labc, nc = ndimage.label(mask); nat0 = np.where(g_nat > -999, g_nat, 65)
        for c in range(1, nc + 1):
            comp = labc == c; ring_c = comp & open_in
            if ring_c.sum() < 4: ring_c = comp & (g_base > -999)
            if ring_c.sum() == 0: continue
            dy = int(np.clip(round(float(np.median(nat0[comp])) - float(np.median(g_base[ring_c]))), -40, 40)); lift[comp & (g_base > -999)] = dy
        print(f"lift: {nc} kept components, {int((lift != 0).sum()):,} columns shifted, dy {lift[mask].min()}..{lift[mask].max()}")
        g_base = np.where(mask, g_base + lift, g_base)
    print(f"mask: {int(mask.sum()):,} columns kept ({int((man & inside).sum()):,} man-made), {int((restore & inside).sum()):,} footprint + {int((restore & ~inside).sum()):,} margin columns restored to the local landscape")
    # ---- height targets for the restored columns: the landscape, bent to the build's floor over `band` blocks at the mask
    nat = np.where(g_nat > -999, g_nat, 65).astype(np.float32)
    target = nat.copy()
    d_in = ndimage.distance_transform_edt(mask)
    ring = open_in & (d_in <= 6)
    if cfg["mode"] == "plate": ring &= g_base > 40
    if ring.sum() == 0: ring = mask & (d_in <= 2)
    _, ridx = ndimage.distance_transform_edt(~ring, return_indices=True)
    h_edge = np.where(ring, g_base, 0)[ridx[0], ridx[1]].astype(np.float32)
    d_mask = ndimage.distance_transform_edt(~mask)
    s = smoothstep(d_mask / cfg["band"])
    target = h_edge * (1 - s) + target * s
    # kept columns outside the mask (other builds in the margin) anchor the landscape too: keep their current ground within 24 blocks
    anchor = ~inside & keep & (g_base > -999)
    if anchor.any():
        d_a, aidx = ndimage.distance_transform_edt(~anchor, return_indices=True)
        h_a = np.where(anchor, g_base, 0)[aidx[0], aidx[1]].astype(np.float32); s_a = smoothstep(d_a / 24)
        target = h_a * (1 - s_a) + target * s_a
    blend = ((s > 0.08) & (s < 0.92)) | (np.abs(target - nat) > 0.5)
    target = target + value_noise((H, Wd), 24, 1.7, 7) * blend + value_noise((H, Wd), 8, 0.5, 11) * blend
    target = np.round(target).astype(np.int32)
    chg = restore & (g_nat > -999) & (target != g_nat)
    print(f"targets: {int(chg.sum()):,} restored columns change height (mean |d| {np.abs(target - g_nat)[chg].mean() if chg.any() else 0:.1f}), edge floor {h_edge[mask].min():.0f}..{h_edge[mask].max():.0f}, band {cfg['band']}")
    save_preview(sid, mask, man & inside, restore, target, ax0, az0)
    if dry: return
    # ---- pass 2: write every chunk of the analysis area whose columns change
    written = 0; by_region = {}
    for (cx, cz), (ent, name, root, ids, pal, tmpl, nroot, nids, npal, ntmpl, has_fresh, in_fp) in chunks.items():
        bx, bz = cx * 16 - ax0, cz * 16 - az0
        zs, xs = slice(max(bz, 0), min(bz + 16, H)), slice(max(bx, 0), min(bx + 16, Wd))
        lzs, lxs = slice(zs.start - bz, zs.stop - bz), slice(xs.start - bx, xs.stop - bx)
        k16 = np.ones((16, 16), bool); t16 = np.full((16, 16), -999, np.int32); l16 = np.zeros((16, 16), np.int32)
        gn16 = np.full((16, 16), -999, np.int32); gb16 = np.full((16, 16), -999, np.int32)
        k16[lzs, lxs] = keep[zs, xs]; t16[lzs, lxs] = target[zs, xs]; l16[lzs, lxs] = lift[zs, xs]; gn16[lzs, lxs] = g_nat[zs, xs]; gb16[lzs, lxs] = g_base[zs, xs]
        if k16.all() and not l16.any() and not in_fp: continue                           # margin chunk with nothing to restore
        mpal, ma, mb = merge_palettes(pal, npal)
        out = np.where(k16[None], ma[np.where(ids < 0, len(pal), ids)], mb[np.where(nids < 0, len(npal), nids)])
        out[(k16[None] & (ids < 0)) | (~k16[None] & (nids < 0))] = -1
        pindex = {key_of(e): i for i, e in enumerate(mpal)}
        def pid(n):
            if (n, ()) not in pindex: pindex[(n, ())] = len(mpal); mpal.append({"Name": (T_STRING, n)})
            return pindex[(n, ())]
        DIRT_I, GRASS_I = pid("minecraft:dirt"), pid("minecraft:grass_block")
        names = np.array([e["Name"][1] for e in mpal] + ["minecraft:air"], dtype=object)
        for lz in range(16):
            for lx in range(16):
                if k16[lz, lx]:
                    dy = int(l16[lz, lx])
                    if dy: relief_column_shift(out[:, lz, lx], int(gb16[lz, lx]) - dy + 64 - 3, dy)   # the component's floor before the lift
                    continue
                g = int(gn16[lz, lx]); t = int(t16[lz, lx])
                if g <= -999 or t <= -999 or t == g: continue
                col = out[:, lz, lx]
                if t > g:
                    col[g + 65:] = -1; col[g + 65:t + 64] = DIRT_I; col[t + 64] = GRASS_I
                else:
                    col[t + 65:] = -1; col[t + 64] = GRASS_I
                    for yy in range(t + 61, t + 64):
                        if names[col[yy] if col[yy] >= 0 else -1] not in AIRS: col[yy] = DIRT_I
        kept = []
        for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
            lx, lz = be["x"][1] - cx * 16, be["z"][1] - cz * 16
            if k16[lz, lx]:
                if l16[lz, lx]: be["y"] = (be["y"][0], be["y"][1] + int(l16[lz, lx]))
                kept.append(be)
        if nroot is not None:
            for be in nroot.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
                lx, lz = be["x"][1] - cx * 16, be["z"][1] - cz * 16
                if not k16[lz, lx] and t16[lz, lx] == gn16[lz, lx]: kept.append(be)
        root["block_entities"] = (T_LIST, (T_COMPOUND, kept))
        encode_chunk(root, out, mpal, ntmpl if (in_fp and nroot is not None) else tmpl)
        root["Status"] = (8, "minecraft:full")
        by_region.setdefault(region_of(cx, cz), {})[slot_of(cx, cz)] = (ent[0], 2, NbtW().root(name, root)); written += 1
    for (rx, rz), slots in by_region.items():
        p = build / "region" / f"r.{rx}.{rz}.mca"; reg = read_region_raw(p); reg.update(slots); write_region(p, reg)
        poi = build / "poi" / f"r.{rx}.{rz}.mca"
        if poi.exists(): poi.unlink()
    print(f"{written} chunks written to {build} in {time.time()-t0:.0f}s ({len(by_region)} region files)")


def save_preview(sid, mask, man, restore, target, ax0, az0):
    from PIL import Image
    H, Wd = mask.shape
    im = np.zeros((H, Wd, 3), np.uint8)
    t = np.clip((target - 55) * 12, 0, 255).astype(np.uint8)
    im[..., 1] = t; im[restore] = np.stack([t, t, t], -1)[restore] // 2 + np.array([40, 90, 40], np.uint8)
    im[mask] = (200, 190, 140); im[man] = (150, 40, 170)
    out = CENSUS / f"integrate_{sid}_preview.png"; Image.fromarray(im).save(out)
    print("->", out, f"(origin {ax0},{az0}; purple man-made, tan kept apron, green restored landscape shaded by target height)")
    np.savez_compressed(CENSUS / f"integrate_{sid}_mask.npz", mask=mask, man=man, target=target, origin=np.array([ax0, az0]))


if __name__ == "__main__":
    main(sys.argv)
