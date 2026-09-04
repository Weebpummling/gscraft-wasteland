"""World build v7, step 1: carve a copy of the pre-generated world down to the chunks we built, so the
pre-generation driver regenerates everything else with the structure override active.

usage: carve_regen.py <pregen world dir> <out world dir> [--dry-run]

Kept (copied as they are): every destination rectangle of buildmap/transplant_plan.json (the v5 player
district and the 29 old-world sites) and the camp (chunks -11..12 x -11..12). Everything else: the chunk
slot is dropped from its region file (and from the entities file), so Chunky sees a missing chunk and
generates it again from the same seed - identical terrain and Lost Cities, but with the pruned structure
sets silent. poi/ is not copied (the game rebuilds it). level.dat, data/ and datapacks/ are copied; put
build/datapacks/gscraft_worldgen into <out>/datapacks before the first boot.
"""
import json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region

CAMP = (-11, -11, 12, 12)


def kept_rects():
    plan = json.load(open(HERE.parent / "buildmap" / "transplant_plan.json"))
    rects = [CAMP]
    for r in plan:
        x1, z1, x2, z2 = r["chunks"]; dx, dz = r["offset"]
        rects.append((x1 + dx, z1 + dz, x2 + dx, z2 + dz))
    return rects


def inside(cx, cz, rects):
    return any(a <= cx <= c and b <= cz <= d for a, b, c, d in rects)


def carve_dir(src: Path, dst: Path, rects, dry, label):
    kept = dropped = 0; files = 0
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("r.*.mca")):
        rx, rz = map(int, f.stem.split(".")[1:3])
        raw = read_region_raw(f)
        keep = {}
        for slot, entry in raw.items():
            cx, cz = rx * 32 + (slot & 31), rz * 32 + (slot >> 5)
            if inside(cx, cz, rects): keep[slot] = entry; kept += 1
            else: dropped += 1
        if keep and not dry:
            write_region(dst / f.name, keep); files += 1
    print(f"  {label}: kept {kept:,} chunks in {files} files, dropped {dropped:,}")
    return kept, dropped


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    src, dst, dry = Path(a[1]), Path(a[2]), "--dry-run" in a
    if "--drop-rect" in a:
        # the Woods mode: drop only the chunks INSIDE the given block rectangle, keep everything else
        i = a.index("--drop-rect"); x0, z0, x1, z1 = map(int, a[i + 1:i + 5])
        drop = (x0 >> 4, z0 >> 4, x1 >> 4, z1 >> 4)
        global inside
        _inside = inside
        inside = lambda cx, cz, rects: not _inside(cx, cz, [drop])
        rects = [drop]
        print(f"dropping chunks inside blocks {x0} {z0} {x1} {z1} (chunks {drop}); keeping the rest")
    else:
        rects = kept_rects()
        print(f"keeping {len(rects)} rectangles (camp + {len(rects) - 1} v5 transplant rects)")
    if not dry:
        if dst.exists(): shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for name in ("level.dat", "level.dat_old"):
            if (src / name).exists(): shutil.copy2(src / name, dst / name)
        for name in ("data", "datapacks", "serverconfig"):
            if (src / name).exists(): shutil.copytree(src / name, dst / name)
    carve_dir(src / "region", dst / "region", rects, dry, "region")
    if (src / "entities").exists(): carve_dir(src / "entities", dst / "entities", rects, dry, "entities")
    print("DRY RUN - nothing written" if dry else f"-> {dst}  (now drop build/datapacks/gscraft_worldgen into {dst / 'datapacks'} and run localpregen.py)")


if __name__ == "__main__":
    main(sys.argv)
