#!/usr/bin/env python3
"""
runplan.py - execute (or dry-run) every rectangle in a transplant plan.

    python runplan.py --plan transplant_plan.json --live <live world dir> --old <old world dir> \
        --dst <new world dir> --remap remap_full.json [--dry-run]

<world dir> is the folder that contains region/, entities/ and poi/. In a dry run nothing is
written; the namespaces found in every rectangle are aggregated and anything outside the
rebuilt pack's namespace set is reported, which is the check that the remap is complete.
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import transplant as tp  # noqa: E402
from planblocks import KEEP  # noqa: E402


def stack_into(existing_raw, name, root, below_y):
    """Merge only the sections of `root` below block y `below_y` into the chunk already at the destination
    (existing_raw: decompressed NBT bytes or None). Block entities follow the same split."""
    cut = below_y // 16
    if existing_raw is None:
        return tp.W().root(name, root)
    ename, eroot = tp.R(existing_raw).root()
    esecs = [sec for sec in eroot.get("sections", (tp.T_LIST, (tp.T_COMPOUND, [])))[1][1] if sec["Y"][1] >= cut]
    nsecs = [sec for sec in root.get("sections", (tp.T_LIST, (tp.T_COMPOUND, [])))[1][1] if sec["Y"][1] < cut]
    eroot["sections"] = (tp.T_LIST, (tp.T_COMPOUND, sorted(esecs + nsecs, key=lambda s: s["Y"][1])))
    ebes = [be for be in eroot.get("block_entities", (tp.T_LIST, (tp.T_COMPOUND, [])))[1][1] if be.get("y", (0, 0))[1] >= below_y]
    nbes = [be for be in root.get("block_entities", (tp.T_LIST, (tp.T_COMPOUND, [])))[1][1] if be.get("y", (0, 0))[1] < below_y]
    eroot["block_entities"] = (tp.T_LIST, (tp.T_COMPOUND, ebes + nbes))
    eroot.pop("Heightmaps", None); eroot["isLightOn"] = (tp.T_BYTE, 0)
    return tp.W().root(ename, eroot)


def run_rect(src_world: Path, dst_world: Path, rect, offset, remap, dry, agg: Counter, dy=0, sections_below_y=None):
    src = src_world / "region"
    dst = dst_world / "region"
    x1, z1, x2, z2 = rect
    dx, dz = offset
    by_dst = {}
    moved = 0
    for cx in range(x1, x2 + 1):
        for cz in range(z1, z2 + 1):
            rx, rz = tp.region_of(cx, cz)
            cache = tp.transplant.cache.setdefault((src, rx, rz), tp.read_region_raw(src / f"r.{rx}.{rz}.mca"))
            entry = cache.get(tp.slot_of(cx, cz))
            if not entry:
                continue
            ts, comp, raw = entry
            name, root = tp.R(raw).root()
            ns = tp.shift_chunk(name, root, dx, dz, remap, {}, dy)
            agg.update(ns)
            if not dry:
                ncx, ncz = cx + dx, cz + dz
                if sections_below_y is not None:
                    by_dst.setdefault(tp.region_of(ncx, ncz), {})[tp.slot_of(ncx, ncz)] = (ts, name, root)   # stacked later
                else:
                    by_dst.setdefault(tp.region_of(ncx, ncz), {})[tp.slot_of(ncx, ncz)] = (ts, 2, tp.W().root(name, root))
            moved += 1
    if not dry:
        for (rx, rz), slots in by_dst.items():
            path = dst / f"r.{rx}.{rz}.mca"
            existing = tp.read_region_raw(path)
            if sections_below_y is not None:
                slots = {slot: (ts, 2, stack_into(existing[slot][2] if slot in existing else None, name, root, sections_below_y))
                         for slot, (ts, name, root) in slots.items()}
            existing.update(slots)
            tp.write_region(path, existing)
            poi = dst_world / "poi" / f"r.{rx}.{rz}.mca"
            if poi.exists():
                poi.unlink()
        esrc, edst = src_world / "entities", dst_world / "entities"
        if esrc.is_dir():
            by_e = {}
            for cx in range(x1, x2 + 1):
                for cz in range(z1, z2 + 1):
                    rx, rz = tp.region_of(cx, cz)
                    cache = tp.transplant.cache.setdefault((esrc, rx, rz), tp.read_region_raw(esrc / f"r.{rx}.{rz}.mca"))
                    entry = cache.get(tp.slot_of(cx, cz))
                    if not entry:
                        continue
                    ts, comp, raw = entry
                    name, root = tp.R(raw).root()
                    tp.shift_entities_chunk(root, dx, dz, dy)
                    ncx, ncz = cx + dx, cz + dz
                    by_e.setdefault(tp.region_of(ncx, ncz), {})[tp.slot_of(ncx, ncz)] = (ts, 2, tp.W().root(name, root))
            for (rx, rz), slots in by_e.items():
                path = edst / f"r.{rx}.{rz}.mca"
                existing = tp.read_region_raw(path)
                existing.update(slots)
                tp.write_region(path, existing)
    return moved


def main(argv):
    a = dict(zip(argv[1::2], argv[2::2]))
    dry = "--dry-run" in argv
    plan = json.loads(Path(a["--plan"]).read_text(encoding="utf-8"))
    remap = {k: v for k, v in json.loads(Path(a["--remap"]).read_text(encoding="utf-8")).items() if not k.startswith("_")}
    worlds = {"live": Path(a["--live"]), "old": Path(a["--old"])} if "--live" in a else {}
    dst = Path(a.get("--dst", "")) if not dry else Path(".")
    agg = Counter()
    total = 0
    for i, r in enumerate(plan, 1):
        src_world = Path(r["source_dir"]) if r.get("source_dir") else worlds[r["source"]]   # source_dir: any world folder
        n = run_rect(src_world, dst, r["chunks"], r["offset"], remap, dry, agg, r.get("dy", 0), r.get("sections_below_y"))
        total += n
        print(f"[{i:>2}/{len(plan)}] {r['source']:<12} {r['chunks']} offset {r['offset']} dy {r.get('dy', 0)} -> {n} chunks {'(dry)' if dry else 'written'}")
    print(f"\nchunks {'inspected' if dry else 'written'}: {total}")
    print("palette namespaces after remap:")
    outside = []
    for ns, n in agg.most_common():
        mark = "" if ns in KEEP else "   <-- NOT IN THE NEW PACK"
        if ns not in KEEP:
            outside.append(ns)
        print(f"  {n:>8}  {ns}{mark}")
    print("\nRESULT:", "clean - every block resolves in the new pack" if not outside else f"UNMAPPED namespaces: {outside}")
    return 0 if not outside else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
