"""Put the transplants' underground back (v8, 2026-09-06).

`integrate.py` rebuilt every column it did not classify as build, top to bottom, so the sewers, basements, bunkers and
mine workings that sat under open ground inside a footprint were replaced by the relief plan. Only the Financial Plaza
had `keep_underground=True`, and it kept 99% of its subsurface build; the hempcrete compound kept 34% and most
farmsteads under 20%.

This applies that same rule retroactively, from the clean transplants that are still on disk: below the shallower of the
two ground levels minus `--margin`, the source column is taken back. Block entities below the cut come with it, so a
restored chest is still a chest with its contents. Nothing above the cut is touched, so the graded terrain, the roads,
the rivers and the shorelines all stay as they are.

usage: underground.py <source world> <dest world> <sectors.json> [--only id,id] [--margin 6] [--dry-run]
       underground.py G:/GSCraft/scratch/worlds/fresh_sectors G:/GSCraft/scratch/worlds/v8-build \
                      ../buildmap/plan_v8/sectors_v8.json

Guards: sectors of group `removed` and the camp are skipped, they were meant to go. Water carved after the transplant
(the river, the lake, the strait) and a road's own embankment push the cut further down instead of skipping the column,
so a deep structure under a new lake still comes back while the bed and the carriageway above it are left alone.
"""
import sys, json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, key_of, T_LIST, T_COMPOUND
from integrate import merge_palettes
from roadmask import RoadMask

AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
WATER = {"minecraft:water", "minecraft:lava", "minecraft:ice", "minecraft:bubble_column"}


def ground_index(ids, names):
    """Index into the 384-tall column of the highest block that is neither air nor liquid, per (z, x)."""
    solid = np.array([(n not in AIRS and n not in WATER) for n in names] + [False])
    s = solid[np.where(ids < 0, len(names), ids)]
    any_ = s.any(0)
    top = np.where(any_, s.shape[0] - 1 - np.argmax(s[::-1], 0), 0)
    return top.astype(np.int32), any_


def water_index(ids, names):
    """Index of the lowest liquid block per column, or 384 when the column has none."""
    liq = np.array([n in WATER for n in names] + [False])
    w = liq[np.where(ids < 0, len(names), ids)]
    any_ = w.any(0)
    return np.where(any_, np.argmax(w, 0), 384).astype(np.int32)


class Regions:
    def __init__(self, world):
        self.w = Path(world); self.r = {}

    def get(self, cx, cz):
        rk = region_of(cx, cz)
        if rk not in self.r:
            p = self.w / "region" / f"r.{rk[0]}.{rk[1]}.mca"
            self.r[rk] = read_region_raw(p) if p.exists() else {}
        return self.r[rk], rk


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    src, dst = Regions(a[1]), Regions(a[2])
    sectors = json.load(open(a[3]))["sectors"]
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    margin = int(a[a.index("--margin") + 1]) if "--margin" in a else 6
    dry = "--dry-run" in a
    roads = RoadMask(1)
    print(f"road/bridge protect mask: {roads.n} masks, {int(roads.array().sum()):,} columns")
    t0 = time.time(); grand = 0; by_region = {}
    for p in sectors:
        if p.get("group") == "removed" or p["id"] == "camp": continue
        if only and p["id"] not in only: continue
        cx0, cz0, cx1, cz1 = p["x0"] >> 4, p["z0"] >> 4, p["x1"] >> 4, p["z1"] >> 4
        moved = cols = chunks = 0
        for cx in range(cx0, cx1 + 1):
            for cz in range(cz0, cz1 + 1):
                sreg, _ = src.get(cx, cz); sent = sreg.get(slot_of(cx, cz))
                if not sent: continue
                dreg, rk = dst.get(cx, cz); dent = dreg.get(slot_of(cx, cz))
                if not dent: continue
                try:
                    sname, sroot = R(sent[2]).root(); sids, spal, _ = decode_chunk(sroot)
                    dname, droot = R(dent[2]).root(); dids, dpal, dtmpl = decode_chunk(droot)
                except Exception:
                    continue
                snames = [e["Name"][1] for e in spal]; dnames = [e["Name"][1] for e in dpal]
                sg, shas = ground_index(sids, snames)
                dg, dhas = ground_index(dids, dnames)
                cut = np.minimum(sg, dg) - margin                       # index, not y
                # a carved river or lake bed, and a road's own embankment fill, push the cut down rather than
                # skipping the column: the structures deeper than they are still come back
                cut = np.minimum(cut, water_index(dids, dnames) - margin)
                bx, bz = cx * 16, cz * 16
                road = np.zeros((16, 16), bool)
                for lz in range(16):
                    for lx in range(16):
                        road[lz, lx] = roads(bx + lx, bz + lz)
                cut = np.where(road, cut - 10, cut)
                ok = shas & dhas & (cut > 0)
                if not ok.any(): continue
                pal, ma, mb = merge_palettes(spal, dpal)
                s_m = ma[np.where(sids < 0, len(spal), sids)]; s_m[sids < 0] = -1
                d_m = mb[np.where(dids < 0, len(dpal), dids)]; d_m[dids < 0] = -1
                below = np.arange(384)[:, None, None] < cut[None]
                take = below & ok[None]
                if not take.any(): continue
                out = np.where(take, s_m, d_m)
                changed = int((out != d_m).sum())
                if changed == 0: continue
                # block entities: keep the destination's above the cut, bring the source's from below it
                def keep(be, arr, cutv):
                    lx, lz = be["x"][1] - bx, be["z"][1] - bz
                    if not (0 <= lx < 16 and 0 <= lz < 16): return False
                    return arr(lx, lz, be["y"][1] + 64)
                dbe = droot.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]
                sbe = sroot.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]
                kept = [b for b in dbe if keep(b, lambda lx, lz, y: not (ok[lz, lx] and y < cut[lz, lx]), None)]
                brought = [b for b in sbe if keep(b, lambda lx, lz, y: ok[lz, lx] and y < cut[lz, lx], None)]
                droot["block_entities"] = (T_LIST, (T_COMPOUND, kept + brought))
                encode_chunk(droot, out, pal, dtmpl)
                by_region.setdefault(rk, {})[slot_of(cx, cz)] = (dent[0], 2, NbtW().root(dname, droot))
                moved += changed; cols += int(ok.sum()); chunks += 1
        grand += moved
        if chunks: print(f"  {p['id']:9s} {str(p.get('group')):10s} {chunks:4d} chunks, {cols:6,d} columns, {moved:9,d} blocks restored")
    print(f"\n{grand:,} blocks restored in {len(by_region)} region files; {time.time()-t0:.0f}s")
    if dry: print("DRY RUN, nothing written"); return
    for rk, slots in by_region.items():
        p = Path(a[2]) / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        reg = dst.r[rk]; reg.update(slots); write_region(p, reg)
        poi = Path(a[2]) / "poi" / f"r.{rk[0]}.{rk[1]}.mca"
        if poi.exists(): poi.unlink()
    print(f"{len(by_region)} region files written")


if __name__ == "__main__":
    main(sys.argv)
