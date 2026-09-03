"""Renders for the v6 layout: the whole 10 km box at 1 px per 8 blocks, and a 1 px per block crop of
every planned site (pads_v6.json + transplant_plan_v6.json destination rects, with a margin), so the
pad levels and the dry/wet check can be read off the pre-generated terrain.

usage: renderv6.py <world region dir> <out dir> [--scale N]
Also prints, per site, the terrain height statistics (min / median / max of the top block) and the
share of water columns inside the rect + margin - the numbers the pad level is set from.
"""
import sys, json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import R, read_region_raw, region_of, slot_of
from anvil import Chunk

MARGIN = 64


def site_stats(region: Path, blocks, label):
    x1, z1, x2, z2 = blocks
    x1 -= MARGIN; z1 -= MARGIN; x2 += MARGIN; z2 += MARGIN
    cache = {}; heights = []; water = 0; cols = 0; missing = 0
    for cx in range(x1 >> 4, (x2 >> 4) + 1):
        for cz in range(z1 >> 4, (z2 >> 4) + 1):
            rx, rz = region_of(cx, cz)
            if (rx, rz) not in cache:
                f = region / f"r.{rx}.{rz}.mca"; cache[(rx, rz)] = read_region_raw(f) if f.exists() else {}
            raw = cache[(rx, rz)].get(slot_of(cx, cz))
            if not raw: missing += 1; continue
            c = Chunk(R(raw[2]).root()[1])
            for x in range(0, 16, 4):
                for z in range(0, 16, 4):
                    y, name = c.top(x, z, ignore={"minecraft:air", "minecraft:cave_air", "minecraft:void_air"})
                    cols += 1; heights.append(y)
                    if name == "minecraft:water": water += 1
    if not heights:
        print(f"  {label:<14} no chunks generated yet"); return None
    h = np.array(heights)
    print(f"  {label:<14} top y min {h.min():>3} p10 {int(np.percentile(h, 10)):>3} median {int(np.median(h)):>3} p90 {int(np.percentile(h, 90)):>3} max {h.max():>3}"
          f" | water {100 * water / max(1, cols):4.1f}% of columns | chunks missing {missing}")
    return {"min": int(h.min()), "p10": int(np.percentile(h, 10)), "median": int(np.median(h)), "p90": int(np.percentile(h, 90)),
            "max": int(h.max()), "water_pct": round(100 * water / max(1, cols), 1), "missing": missing}


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    region, out = Path(a[1]), Path(a[2]); out.mkdir(parents=True, exist_ok=True)
    scale = int(a[a.index("--scale") + 1]) if "--scale" in a else 8
    pads = json.load(open(HERE / "pads_v6.json"))
    plan = json.load(open(HERE.parent / "buildmap" / "transplant_plan_v6.json"))
    sites = [(p["name"], p["blocks"]) for p in pads] + [(r["source"], r["dest_blocks"]) for r in plan]
    print("terrain under every planned site (rect + 64-block margin):")
    stats = {}
    for name, blocks in sites:
        s = site_stats(region, blocks, name)
        if s: stats[name] = s
    json.dump(stats, open(out / "v6_site_terrain.json", "w"), indent=1)
    print("overview render ...", flush=True)
    subprocess.run([sys.executable, str(HERE / "topdown.py"), str(region), str(out / "v6_box_overview.png"), "--scale", str(scale),
                    "--chunks", str(-3100 >> 4), str(-3750 >> 4), str(6900 >> 4), str(6250 >> 4)], check=False)
    for name, blocks in sites:
        x1, z1, x2, z2 = blocks
        subprocess.run([sys.executable, str(HERE / "topdown.py"), str(region), str(out / f"v6_site_{name}.png"),
                        "--chunks", str((x1 - MARGIN) >> 4), str((z1 - MARGIN) >> 4), str((x2 + MARGIN) >> 4), str((z2 + MARGIN) >> 4)], check=False)
    print("done ->", out)


if __name__ == "__main__":
    main(sys.argv)
