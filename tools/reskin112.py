"""Re-skin a 1.12.2 transplant in place, from the original save, onto the decoration mods the pack actually ships.

The 1.12 sources (the desert city, the Financial Plaza, the sewers, Novo, Bio Gen) were upgraded with `remap112.json`
before there was a 1.20.1 Chisel in the pack, so 665 k modded blocks were mapped to plain vanilla lookalikes: every
Chisel factory panel became one flat `factory_blocks:factory`, every Fureniku road block became black concrete, every
antiblock became vanilla concrete. Only 2.7 % actually fell through to the grey placeholder; the rest are there but
featureless.

This does not re-transplant. For every position it reads the ORIGINAL 1.12 block, works out what the old table turned
it into, and replaces it only if the destination still holds exactly that block. Anything integrate, the roads, the
rivers or a player changed is left alone, so the terrain blending and everything built since are safe.

usage: reskin112.py <1.12 save> <dest world> <plan.json> <source name> [--dry-run] [--limit N]
       reskin112.py "G:/GSCraft/incoming/Maps/world" G:/GSCraft/scratch/worlds/v8-build \
                    ../buildmap/plan_v8/transplant_plan_v8_fresh.json hub

The plan entry supplies the source chunk rectangle, the chunk offset and the y shift, so the lookup is exact.
"""
import sys, json, time, collections
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from anvil112 import read_level, registry, decode_section
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, T_STRING
from makeremap112 import resolve as old_resolve

COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
           "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
# Antiblocks Rechiseled ships nine flat "bright" colours; the rest keep vanilla concrete, which is the closer match
BRIGHT = {"white", "orange", "magenta", "yellow", "cyan", "blue", "green", "red", "black"}
# Chisel 1.20.1 names blocks <pattern>/<base block>; these are the industrial patterns the 1.12 city used
FACTORY = ["chisel:plates/iron_block", "chisel:rivets/iron_block", "chisel:vents/iron_block", "chisel:gears/iron_block",
           "chisel:dent/light_gray_concrete", "chisel:tiles_small/light_gray_concrete", "chisel:cut/gray_concrete",
           "chisel:array/gray_concrete", "chisel:panel/light_gray_concrete", "chisel:crate_dark/iron_block",
           "chisel:plates/gold_block", "chisel:rivets/gold_block", "chisel:dent/gray_concrete",
           "chisel:tiles_medium/light_gray_concrete", "chisel:panel/gray_concrete", "chisel:array/light_gray_concrete"]
TECHNICAL = ["chisel:panel/light_gray_concrete", "chisel:rivets/iron_block", "chisel:plates/iron_block",
             "chisel:vents/iron_block", "chisel:dent/light_gray_concrete", "chisel:cut/light_gray_concrete"]
ROADS = {0: "chisel:road/black_concrete", 1: "chisel:road/gray_concrete", 2: "chisel:road/light_gray_concrete",
         3: "chisel:road/black_concrete"}

IMPROVED = {}
IMPROVED.update({f"chisel:antiblock[{i}]": (f"antiblocksrechiseled:bright_{c}" if c in BRIGHT else f"minecraft:{c}_concrete")
                 for i, c in enumerate(COLOURS)})
IMPROVED.update({f"chisel:factory[{i}]": FACTORY[i] for i in range(16)})
IMPROVED.update({f"chisel:factory1[{i}]": FACTORY[(i + 8) % 16] for i in range(16)})
IMPROVED.update({f"chisel:technical[{i}]": TECHNICAL[i % len(TECHNICAL)] for i in range(16)})
IMPROVED.update({f"chisel:technical1[{i}]": TECHNICAL[(i + 2) % len(TECHNICAL)] for i in range(16)})
IMPROVED.update({f"chisel:technicalnew[{i}]": TECHNICAL[(i + 4) % len(TECHNICAL)] for i in range(16)})
IMPROVED.update({f"furenikusroads:generic_blocks[{m}]": t for m, t in ROADS.items()})
IMPROVED.update({f"furenikusroads:road_block_standard[{m}]": "chisel:road/black_concrete" for m in range(16)})
IMPROVED.update({f"furenikusroads:street_block_b[{m}]": "chisel:road/gray_concrete" for m in range(16)})
IMPROVED.update({f"furenikusroads:street_block_a[{m}]": "chisel:road/light_gray_concrete" for m in range(16)})
IMPROVED.update({
    "chisel:laboratory": "chisel:tiles_small/white_concrete",
    "chisel:concrete_lightgray1": "chisel:array/light_gray_concrete",
    "chisel:concrete_gray1": "chisel:array/gray_concrete",
    "chisel:concrete_white1": "chisel:array/white_concrete",
    "chisel:concrete_black1": "chisel:array/black_concrete",
    "chisel:glass": "chisel:screen/glass",
    "chisel:glass1": "chisel:steelframe/glass",
    "chisel:hexplating": "chisel:plates/iron_block",
    "chisel:futura": "chisel:array/light_blue_concrete",
    "hbm:deco_steel": "chisel:rivets/iron_block",
    "hbm:brick_concrete": "chisel:cut/gray_concrete",
    "hbm:machine_tower_small": "chisel:vents/iron_block",
    "srparasites:infestremain": "minecraft:sculk",
})


def new_resolve(name, meta):
    return IMPROVED.get(f"{name}[{meta}]") or IMPROVED.get(name)


def plain(n):
    return n.split("[")[0]


def props_of(n):
    if "[" not in n: return {}
    return dict(kv.split("=") for kv in n[n.index("[") + 1:-1].split(","))


def main(a):
    if len(a) < 5: sys.exit(__doc__)
    save, dest, planp, want = Path(a[1]), Path(a[2]), a[3], a[4]
    dry = "--dry-run" in a
    entry = next(e for e in json.load(open(planp)) if e["source"] == want)
    cx0, cz0, cx1, cz1 = entry["chunks"]; ox, oz = entry["offset"]; dy = entry.get("dy", 0)
    print(f"{want}: source chunks x {cx0}..{cx1} z {cz0}..{cz1}, offset {ox},{oz}, dy {dy}")
    reg = registry(read_level(save))
    names = {i: n for i, n in reg.items()}
    # per (id, meta) target tables
    lut_old = {}; lut_new = {}
    for i, n in names.items():
        if n.startswith("minecraft:"): continue
        for m in range(16):
            o = old_resolve(n, m); o = o[0] if isinstance(o, tuple) else o
            nw = new_resolve(n, m)
            if nw and o and plain(nw) != plain(o):
                lut_old[(i, m)] = plain(o); lut_new[(i, m)] = nw
    print(f"{len(lut_new)} (block, meta) pairs have a better target; "
          f"{len({v for v in lut_new.values()})} distinct 1.20 blocks")
    src_regions = {}
    def src_chunk(cx, cz):
        rk = (cx >> 5, cz >> 5)
        if rk not in src_regions:
            p = save / "region" / f"r.{rk[0]}.{rk[1]}.mca"
            src_regions[rk] = read_region_raw(p) if p.exists() else {}
        ent = src_regions[rk].get(slot_of(cx, cz))
        if not ent: return None
        try: _, root = R(ent[2]).root()
        except Exception: return None
        return root.get("Level", (0, None))[1]

    dst_regions = {}
    def dst_region(cx, cz):
        rk = region_of(cx, cz)
        if rk not in dst_regions:
            p = dest / "region" / f"r.{rk[0]}.{rk[1]}.mca"
            dst_regions[rk] = read_region_raw(p) if p.exists() else {}
        return dst_regions[rk], rk

    t0 = time.time(); by_region = {}; changed_total = 0; hits = collections.Counter(); done = 0
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            level = src_chunk(cx, cz)
            if not level: continue
            dcx, dcz = cx + ox, cz + oz
            dreg, rk = dst_region(dcx, dcz); dent = dreg.get(slot_of(dcx, dcz))
            if not dent: continue
            try:
                dname, droot = R(dent[2]).root(); dids, dpal, dtmpl = decode_chunk(droot)
            except Exception:
                continue
            dnames = [e["Name"][1] for e in dpal]
            want_old = {}; want_new = {}
            for sec in level.get("Sections", (0, (0, [])))[1][1]:
                sy = sec["Y"][1]
                if "Blocks" not in sec: continue
                ids, meta = decode_section(sec)
                key = ids.astype(np.int32) * 16 + meta
                uniq = np.unique(key)
                for k in uniq:
                    bid, m = int(k) // 16, int(k) % 16
                    if (bid, m) not in lut_new: continue
                    pos = np.nonzero(key == k)[0]
                    ys = sy * 16 + pos // 256 + dy + 64
                    zs = (pos // 16) % 16; xs = pos % 16
                    good = (ys >= 0) & (ys < 384)
                    want_old.setdefault(k, []).append((ys[good], zs[good], xs[good]))
            if not want_old: continue
            pindex = {n: i for i, n in enumerate(dnames)}
            def pid(n):
                if n not in pindex:
                    pindex[n] = len(dpal)
                    e = {"Name": (T_STRING, plain(n))}
                    p = props_of(n)
                    if p: e["Properties"] = (10, {k: (T_STRING, v) for k, v in p.items()})
                    dpal.append(e); dnames.append(plain(n))
                return pindex[n]
            nchanged = 0
            for k, groups in want_old.items():
                bid, m = int(k) // 16, int(k) % 16
                old_n, new_n = lut_old[(bid, m)], lut_new[(bid, m)]
                tgt = pid(new_n)
                for ys, zs, xs in groups:
                    cur = dids[ys, zs, xs]
                    if cur.size == 0: continue
                    ok = (cur >= 0) & np.array([dnames[c] == old_n if c >= 0 else False for c in cur], dtype=bool)
                    if not ok.any(): continue
                    dids[ys[ok], zs[ok], xs[ok]] = tgt
                    n = int(ok.sum()); nchanged += n; hits[new_n] += n
            if nchanged == 0: continue
            encode_chunk(droot, dids, dpal, dtmpl)
            by_region.setdefault(rk, {})[slot_of(dcx, dcz)] = (dent[0], 2, NbtW().root(dname, droot))
            changed_total += nchanged; done += 1
            if limit and done >= limit: break
        if limit and done >= limit: break
    print(f"\n{changed_total:,} blocks re-skinned in {done} chunks, {len(by_region)} region files; {time.time()-t0:.0f}s")
    for n, c in hits.most_common(14): print(f"   {c:9,d}  {n}")
    if dry: print("DRY RUN, nothing written"); return
    for rk, slots in by_region.items():
        p = dest / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        reg2 = dst_regions[rk]; reg2.update(slots); write_region(p, reg2)
        poi = dest / "poi" / f"r.{rk[0]}.{rk[1]}.mca"
        if poi.exists(): poi.unlink()
    print(f"{len(by_region)} region files written")


if __name__ == "__main__":
    main(sys.argv)
