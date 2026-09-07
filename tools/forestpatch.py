"""Plant patches of Skadowsky's forest across the cell's empty land.

The v8 cell is 73 % bare grass. Skadowsky's own woods are the only forest with any character in the
world - spruce, close-grown, with grass and fern under them - so this tool lifts that forest column by
column and stamps it into the open ground, in irregular patches rather than as a blanket.

    forestpatch.py <world dir> [--coverage F] [--seed N] [--limit N] [--dry-run]

`--coverage` is the fraction of eligible open land to plant, 0.12 by default. `--limit` stops after N
patches, which is what the preview renders are made with.

Eligible land, all of which is checked per column before anything is written:
  * the surface is grass, dirt or their plants, and there is no water in the column
  * nothing man-made anywhere in the column (the census `built` flag)
  * nothing already growing there
  * 48 blocks clear of every sector rectangle in sectors_v8.json - the placed builds, the camp,
    the farmsteads - so no patch ever crowds a build
  * 12 blocks clear of every road and bridge mask
  * inside the world border
  * locally flat: the ground varies by no more than 3 blocks in a 5 x 5 window, so a tree lifted from
    flat ground does not end up sheared across a step

A patch is a disc of radius 24 to 72 wobbled by low-frequency noise, so its edge is ragged. Each patch
picks a random window in the source forest and tiles it, which keeps the source's own clumping and
spacing instead of scattering trees at even density.

Edited chunks lose their Heightmaps and `isLightOn`, so the server recomputes both when it next loads
them - the same contract every other terrain tool here uses. Leaves darken what is under them, so the
stored light would otherwise be too bright.
"""
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of  # noqa: E402
from applyheight import decode_chunk, encode_chunk, T_STRING  # noqa: E402

CENSUS = Path(r"G:/GSCraft/incoming/census/v8_cell_pass16_inspect.npz")
LIB = HERE / "forest_lib.json"
SECTORS = HERE.parent / "buildmap" / "plan_v8" / "sectors_v8.json"
MASKS = Path(r"G:/GSCraft/incoming/census")
X0, Z0 = -3900, -3900

BUILD_KEEP = 48          # blocks clear of any sector rectangle
ROAD_KEEP = 12           # blocks clear of any road or bridge
FLAT_TOL = 3             # ground range allowed in a 5 x 5 window
R_MIN, R_MAX = 24, 72    # patch radius
AIR = "minecraft:air"


def eligible():
    """The mask of columns a tree may be planted on, plus the ground height array."""
    d = np.load(CENSUS, allow_pickle=True)
    sy = d["sy"].astype(np.int32); gy = d["gy"].astype(np.int32)
    wt = d["wtop"].astype(np.int32); built = d["built"]; sn = d["sname"]
    names = list(d["names"])
    H, Wd = sy.shape

    def ids(pred):
        return np.array([i for i, n in enumerate(names) if pred(n.split(":")[-1])], np.int32)

    open_ground = np.isin(sn, ids(lambda k: k in (
        "grass_block", "grass", "short_grass", "tall_grass", "fern", "large_fern",
        "dead_bush", "dirt", "coarse_dirt", "podzol")))
    growing = np.isin(sn, ids(lambda k: k.endswith("_leaves") or k.endswith("_log")
                              or k in ("mushroom_stem", "brown_mushroom_block", "red_mushroom_block",
                                       "cactus", "bamboo", "sugar_cane")))

    m = open_ground & ~growing & ~built & (wt <= -999)

    S = json.load(open(SECTORS, encoding="utf-8"))
    sect = np.zeros((H, Wd), bool)
    for s in S["sectors"]:
        z0, z1 = max(s["z0"] - Z0, 0), min(s["z1"] - Z0, H - 1)
        x0, x1 = max(s["x0"] - X0, 0), min(s["x1"] - X0, Wd - 1)
        if z0 <= z1 and x0 <= x1:
            sect[z0:z1 + 1, x0:x1 + 1] = True

    road = np.zeros((H, Wd), bool)
    for f in sorted(MASKS.glob("road_*_mask.npz")) + sorted(MASKS.glob("bridge_*_mask.npz")):
        z = np.load(f); mk = z["mask"]; ox, oz = (int(v) for v in z["origin"])
        r0, c0 = oz - Z0, ox - X0
        r1, c1 = min(r0 + mk.shape[0], H), min(c0 + mk.shape[1], Wd)
        if r0 < H and c0 < Wd and r1 > 0 and c1 > 0:
            road[max(r0, 0):r1, max(c0, 0):c1] |= mk[max(0, -r0):r1 - r0, max(0, -c0):c1 - c0]

    m &= ~ndimage.binary_dilation(sect, np.ones((3, 3)), iterations=BUILD_KEEP // 2)
    m &= ~ndimage.binary_dilation(road, np.ones((3, 3)), iterations=ROAD_KEEP // 2)

    bx0, bz0, bx1, bz1 = S["border"]
    inside = np.zeros((H, Wd), bool)
    inside[max(bz0 - Z0, 0):min(bz1 - Z0, H - 1) + 1, max(bx0 - X0, 0):min(bx1 - X0, Wd - 1) + 1] = True
    m &= inside

    g = np.where(gy > -999, gy, 0)
    flat = (ndimage.maximum_filter(g, 5) - ndimage.minimum_filter(g, 5)) <= FLAT_TOL
    m &= flat & (gy > -999)
    return m, sy, gy


def patches(m, coverage, seed, limit):
    """Irregular blobs over the eligible mask, until `coverage` of it is covered."""
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)
    H, Wd = m.shape
    target = int(m.sum() * coverage)
    # only start a patch well inside open ground
    core = ndimage.binary_erosion(m, np.ones((3, 3)), iterations=12)
    ys, xs = np.nonzero(core[::8, ::8])
    order = nprng.permutation(len(xs))
    taken = np.zeros((H // 8 + 1, Wd // 8 + 1), bool)
    out, area = [], 0
    for k in order:
        if area >= target or (limit and len(out) >= limit):
            break
        gx, gz = int(xs[k]), int(ys[k])
        if taken[gz, gx]:
            continue
        r = rng.randint(R_MIN, R_MAX)
        cx, cz = gx * 8, gz * 8
        # a disc wobbled by four low-frequency lobes so the edge is never a circle
        ph = [rng.uniform(0, 6.28) for _ in range(4)]
        amp = [rng.uniform(0.10, 0.30) for _ in range(4)]
        out.append((cx, cz, r, ph, amp))
        area += int(3.14 * r * r * 0.85)
        rr = (r + 24) // 8
        taken[max(gz - rr, 0):gz + rr + 1, max(gx - rr, 0):gx + rr + 1] = True
    return out, area


def blob_cols(cx, cz, r, ph, amp, m):
    """Column indices inside one wobbled disc that are eligible."""
    H, Wd = m.shape
    z0, z1 = max(cz - r, 0), min(cz + r, H - 1)
    x0, x1 = max(cx - r, 0), min(cx + r, Wd - 1)
    zz, xx = np.mgrid[z0:z1 + 1, x0:x1 + 1]
    dx = xx - cx; dz = zz - cz
    dist = np.sqrt(dx * dx + dz * dz)
    ang = np.arctan2(dz, dx)
    wob = np.ones_like(dist)
    for k, (p, a) in enumerate(zip(ph, amp)):
        wob = wob + a * np.sin((k + 2) * ang + p)
    keep = (dist <= r * np.clip(wob, 0.45, 1.15) * 0.92) & m[z0:z1 + 1, x0:x1 + 1]
    zi, xi = np.nonzero(keep)
    return xi + x0, zi + z0


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    world = Path(argv[1])
    cov = float(argv[argv.index("--coverage") + 1]) if "--coverage" in argv else 0.12
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 20260907
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 0
    dry = "--dry-run" in argv

    t0 = time.time()
    lib = json.load(open(LIB, encoding="utf-8"))
    # each window's extent is read back from the keys, so adding a source window needs no code change
    wins = {}
    for key in lib:
        w, off = key.split("|")
        dx, dz = (int(v) for v in off.split(","))
        a = wins.setdefault(w, [0, 0])
        a[0] = max(a[0], dx + 1); a[1] = max(a[1], dz + 1)
    win_names = sorted(wins)
    print("source: {:,} forest columns in {} windows ({})".format(
        len(lib), len(win_names), ", ".join(f"{w} {wins[w][0]}x{wins[w][1]}" for w in win_names)))

    m, sy, gy = eligible()
    print(f"eligible open land: {int(m.sum()):,} columns ({time.time()-t0:.0f}s)")

    ps, area = patches(m, cov, seed, limit)
    print(f"{len(ps)} patches planned, about {area:,} columns ({100*area/max(int(m.sum()),1):.1f}% of the open land)")

    # collect every write, keyed by chunk
    rng = random.Random(seed)
    per_chunk = {}
    cols = 0
    for cx_, cz_, r, ph, amp in ps:
        xs, zs = blob_cols(cx_, cz_, r, ph, amp, m)
        if len(xs) == 0:
            continue
        wname = rng.choice(win_names)
        ww, hh = wins[wname]
        ox, oz = rng.randrange(ww), rng.randrange(hh)
        for xi, zi in zip(xs, zs):
            X, Z = xi + X0, zi + Z0
            sxk = f"{wname}|{(X - cx_ + ox) % ww},{(Z - cz_ + oz) % hh}"
            stack = lib.get(sxk)
            if not stack:
                continue
            per_chunk.setdefault((X >> 4, Z >> 4), []).append((X, Z, int(gy[zi, xi]), stack))
            cols += 1
    blocks = sum(sum(1 for b in st if b) for v in per_chunk.values() for *_, st in v)
    print(f"{cols:,} columns to plant in {len(per_chunk):,} chunks; {blocks:,} blocks")
    if dry:
        print(f"dry run, nothing written ({time.time()-t0:.0f}s)")
        return

    by_region = {}
    for (cx, cz), items in per_chunk.items():
        by_region.setdefault(region_of(cx, cz), []).append((cx, cz, items))
    written = 0
    for rk, chunks in sorted(by_region.items()):
        p = world / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        if not p.exists():
            continue
        reg = read_region_raw(p); out = {}
        for cx, cz, items in chunks:
            e = reg.get(slot_of(cx, cz))
            if not e:
                continue
            name, root = R(e[2]).root()
            try:
                ids, pal, tmpl = decode_chunk(root)
            except Exception:
                continue
            names = [x["Name"][1] for x in pal]
            index = {}

            def idx(n):
                if n in index:
                    return index[n]
                for i, nn in enumerate(names):
                    if nn == n and not pal[i].get("Properties"):
                        index[n] = i
                        return i
                pal.append({"Name": (T_STRING, n)}); names.append(n)
                index[n] = len(pal) - 1
                return index[n]

            touched = False
            for X, Z, g, stack in items:
                lx, lz = X & 15, Z & 15
                for k, b in enumerate(stack):
                    if b is None:
                        continue
                    y = g + 1 + k
                    if not (-64 <= y < 320):
                        continue
                    if str(names[ids[y + 64, lz, lx]]) not in ("minecraft:air", "minecraft:cave_air", "minecraft:void_air"):
                        continue
                    ids[y + 64, lz, lx] = idx(b)
                    touched = True
            if not touched:
                continue
            encode_chunk(root, ids, pal, tmpl)
            root.pop("Heightmaps", None)
            root.pop("isLightOn", None)
            out[slot_of(cx, cz)] = (e[0], 2, NbtW().root(name, root))
            written += 1
        if out:
            reg.update(out); write_region(p, reg)
    print(f"{written:,} chunks written in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv)
