"""Smooth the hard edges of the open land over the whole cell (owner: "from an overall point of view, smooth out the hard
edges on the map - terrain related only, not buildings").

Two treatments, terrain only (built columns, roads, water and the Skadowsky map's own terrain are never touched):
  1. cliffs - wherever two neighbouring open-land columns differ by 3+ blocks, the ground within 12 blocks is replaced by a
     smoothed height field (normalised gaussian over open land, sigma 3), so a step becomes a slope;
  2. shores - open land next to a lake or river more than 1 block above the water surface is graded down to water + 1 over
     14 blocks (smoothstep), the first two blocks as sand/gravel beach.
Heights come from a render_inspect.py npz of the cell; changed columns are rewritten chunk by chunk (dirt below, grass or
sand on top, everything above the old ground cleared - trees on a reshaped column go, the others stay).

usage: smoothcliffs.py <world dir> <inspect.npz> [--protect integrate_skad_mask.npz,...] [--dry-run]
"""
import sys, time, json
from pathlib import Path
import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, key_of, T_STRING, T_LIST, T_COMPOUND
from integrate import smoothstep, value_noise

CENSUS = Path(r"G:/GSCraft/incoming/census"); X0, Z0 = -3900, -3900
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world = Path(a[1]); dry = "--dry-run" in a; t0 = time.time()
    d = np.load(a[2], allow_pickle=True); gy = d["gy"].astype(np.int32); built = d["built"]; wt = d["wtop"].astype(np.int32); names = list(d["names"]); sn = d["sname"]
    H, W = gy.shape
    road_ids = np.array([i for i, n in enumerate(names) if any(k in n for k in ("concrete", "andesite", "gravel", "stone", "cobble", "terracotta", "path")) and "grass" not in n], np.int32)
    roadish = np.isin(sn, road_ids)
    protect = np.zeros((H, W), bool)
    if "--protect" in a:
        for f in a[a.index("--protect") + 1].split(","):
            m = np.load(CENSUS / f); ox, oz = map(int, m["origin"]); mk = m["mask"]
            protect[oz - Z0:oz - Z0 + mk.shape[0], ox - X0:ox - X0 + mk.shape[1]] |= mk
    water = wt > -999
    open_ = (~built) & (~water) & (gy > -999) & (~protect) & (~roadish)
    # keep roads and their shoulders as they are (8 blocks)
    open_ &= ~ndimage.binary_dilation(roadish | built, iterations=6)
    g = gy.astype(np.float32)
    # ---- 1. shores
    dw, widx = ndimage.distance_transform_edt(~water, return_indices=True)
    wl = np.where(water, wt, 0)[widx[0], widx[1]].astype(np.float32)
    near = open_ & (dw <= 14) & (g > wl + 1)
    s = smoothstep(dw / 14.0)
    shore_t = wl + 1 + (g - wl - 1) * s
    target = np.where(near, shore_t, g)
    beach = near & (dw <= 2.5)
    # ---- 2. cliffs (on the shore-corrected field)
    o = open_.astype(np.float32)
    num = ndimage.gaussian_filter(target * o, 3, truncate=3.0); den = ndimage.gaussian_filter(o, 3, truncate=3.0)
    smooth = np.where(den > 1e-3, num / np.maximum(den, 1e-3), target)
    tz = np.abs(np.diff(target, axis=0)) >= 3; tx = np.abs(np.diff(target, axis=1)) >= 3
    cliff = np.zeros((H, W), bool)
    cliff[:-1, :] |= tz & open_[:-1, :] & open_[1:, :]; cliff[1:, :] |= tz & open_[:-1, :] & open_[1:, :]
    cliff[:, :-1] |= tx & open_[:, :-1] & open_[:, 1:]; cliff[:, 1:] |= tx & open_[:, :-1] & open_[:, 1:]
    dc = ndimage.distance_transform_edt(~cliff)
    wgt = 1 - smoothstep(dc / 12.0)
    target = target * (1 - wgt) + smooth * wgt
    target = target + value_noise((H, W), 9, 0.45, 31) * (wgt > 0.05)
    target = np.round(target).astype(np.int32)
    change = open_ & (target != gy) & (np.abs(target - gy) <= 40)
    print(f"cliff columns {int(cliff.sum()):,}, shore columns graded {int(near.sum()):,}; {int(change.sum()):,} columns change (mean |d| {np.abs(target - gy)[change].mean() if change.any() else 0:.2f}); {time.time()-t0:.0f}s")
    if dry: return
    # ---- write, chunk by chunk
    per_chunk = np.add.reduceat(np.add.reduceat(change.astype(np.int32), np.arange(0, H, 16), axis=0), np.arange(0, W, 16), axis=1) > 0
    cz_idx, cx_idx = np.nonzero(per_chunk)
    chunks = set(zip((cx_idx * 16 + X0) >> 4, (cz_idx * 16 + Z0) >> 4))
    regions = {}; written = 0; by_region = {}
    for (cx, cz) in sorted(chunks):
        rk = region_of(cx, cz)
        if rk not in regions:
            p = world / "region" / f"r.{rk[0]}.{rk[1]}.mca"; regions[rk] = read_region_raw(p) if p.exists() else {}
        ent = regions[rk].get(slot_of(cx, cz))
        if not ent: continue
        name, root = R(ent[2]).root()
        if "sections" not in root: continue
        ids, pal, tmpl = decode_chunk(root)
        pindex = {key_of(e): i for i, e in enumerate(pal)}
        def pid(n):
            if (n, ()) not in pindex: pindex[(n, ())] = len(pal); pal.append({"Name": (T_STRING, n)})
            return pindex[(n, ())]
        DIRT, GRASS, SAND, GRAVEL = pid("minecraft:dirt"), pid("minecraft:grass_block"), pid("minecraft:sand"), pid("minecraft:gravel")
        pnames = [e["Name"][1] for e in pal]
        bx, bz = cx * 16 - X0, cz * 16 - Z0; touched = False
        for lz in range(16):
            for lx in range(16):
                iz, ix = bz + lz, bx + lx
                if not (0 <= iz < H and 0 <= ix < W) or not change[iz, ix]: continue
                g0 = int(gy[iz, ix]); t = int(target[iz, ix]); col = ids[:, lz, lx]
                top = GRASS if not beach[iz, ix] else (SAND if (ix * 3 + iz * 5) % 4 else GRAVEL)
                if t > g0:
                    col[g0 + 65:] = -1; col[g0 + 65:t + 64] = DIRT; col[t + 64] = top
                else:
                    col[t + 65:] = -1; col[t + 64] = top
                    for yy in range(t + 61, t + 64):
                        if col[yy] >= 0 and pnames[col[yy]] not in AIRS: col[yy] = DIRT
                touched = True
        if not touched: continue
        kept = [be for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]
                if not change[be["z"][1] - Z0, be["x"][1] - X0] or be["y"][1] <= min(gy[be["z"][1] - Z0, be["x"][1] - X0], target[be["z"][1] - Z0, be["x"][1] - X0])]
        root["block_entities"] = (T_LIST, (T_COMPOUND, kept))
        encode_chunk(root, ids, pal, tmpl)
        by_region.setdefault(rk, {})[slot_of(cx, cz)] = (ent[0], 2, NbtW().root(name, root)); written += 1
    for rk, slots in by_region.items():
        p = world / "region" / f"r.{rk[0]}.{rk[1]}.mca"; reg = regions[rk]; reg.update(slots); write_region(p, reg)
        poi = world / "poi" / f"r.{rk[0]}.{rk[1]}.mca"
        if poi.exists(): poi.unlink()
    print(f"{written} chunks written in {len(by_region)} region files; {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv)
