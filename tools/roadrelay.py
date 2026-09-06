"""Re-lay the stretches of a built road that a later terrain pass wiped (v8 road review, step 2).

`roads.py build` ran before the strait, the river, the shorelines and the cliff smoothing, and those passes took 4% of
the carriageway back to grass or water, mostly where a road meets the lake. This walks each route's centre line, finds
the contiguous spans whose surface is no longer a road, and re-lays the ones that are on dry land, in the material and
width of the surviving road on either side of the span (roadpatch.profile). A span that is now under water is reported
and left alone: there the road correctly ends at a bank or a bridge abutment, and a causeway would dam the water.

usage: roadrelay.py <world dir> <routes.json,...> [--only name,name] [--min 3] [--pad 4] [--dry-run]
Run `roadmask.py --from-routes` afterwards, or rely on the mask this writes per repaired span.
"""
import sys, json, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import roads, roadpatch
from roads import densify
from roadpatch import is_road, is_surface, profile, style_from, stamp, surface_y
from terrain import World, LIQUID


def spans(world, pts, min_len, pad):
    """Contiguous runs of centre-line steps whose surface is not a road, padded and then merged so two
    runs a few blocks apart become one repair rather than overlapping stamps."""
    bad = [not is_road(world.top(x, z)[1]) for (x, z) in pts]
    raw = []; i = 0
    while i < len(pts):
        if not bad[i]: i += 1; continue
        j = i
        while j + 1 < len(pts) and bad[j + 1]: j += 1
        if j - i + 1 >= min_len: raw.append((max(i - pad, 0), min(j + pad, len(pts) - 1)))
        i = j + 1
    out = []
    for s in raw:
        if out and s[0] <= out[-1][1] + 1: out[-1] = (out[-1][0], max(out[-1][1], s[1]))
        else: out.append(s)
    return out


def wet_col(world, x, z, lat=2):
    """Water on the column or within `lat` blocks of it: a road may not be re-laid here, it would dam the water."""
    for dx in range(-lat, lat + 1):
        for dz in range(-lat, lat + 1):
            if world.top(x + dx, z + dz)[1] in LIQUID: return True
    return False


def dry_runs(world, seg, min_len, lat=2):
    """Split a span into the stretches that are clear of water; the wet ones are where the road ends at a
    bank or a bridge abutment and must be left alone."""
    wet = [wet_col(world, x, z, lat) for (x, z) in seg]
    runs = []; i = 0
    while i < len(seg):
        if wet[i]: i += 1; continue
        j = i
        while j + 1 < len(seg) and not wet[j + 1]: j += 1
        if j - i + 1 >= min_len: runs.append((i, j))
        i = j + 1
    return runs, sum(wet)


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world = World(Path(a[1])); dry = "--dry-run" in a
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    min_len = int(a[a.index("--min") + 1]) if "--min" in a else 3
    pad = int(a[a.index("--pad") + 1]) if "--pad" in a else 4
    routes = []
    for f in a[2].split(","):
        for r in json.load(open(f)):
            if r.get("polyline") and (only is None or r["name"] in only): routes.append(r)
    total = 0; wet_total = 0; fixed = 0
    for r in routes:
        pts = densify(r["polyline"])
        for (i0, j0) in spans(world, pts, min_len, pad):
            runs, wet = dry_runs(world, pts[i0:j0 + 1], min_len)
            if wet:
                wet_total += 1
                print(f"  {r['name']:14s} {j0-i0+1:4d} m at {tuple(pts[i0])}..{tuple(pts[j0])}  {wet} m on or beside water: left to the bank or the abutment")
            for (a0, b0) in runs:
                i, j = i0 + a0, i0 + b0; seg = pts[i:j + 1]
                # material and width from the road that survives on both sides of the span
                c = collections.Counter(); kerb = 0
                for end in (max(i - 24, 0), min(j + 24, len(pts) - 1)):
                    cc, kk = profile(world, *pts[end], 12); c += cc; kerb += kk
                if not c:
                    print(f"  {r['name']:14s} {len(seg):4d} m at {tuple(seg[0])}: no surviving road nearby, skipped"); continue
                roads._style = style_from(c, kerb)
                width = min(r.get("width", 7), 11)
                ya = surface_y(world, *pts[max(i - 6, 0)]); yb = surface_y(world, *pts[min(j + 6, len(pts) - 1)])
                hs = []
                for k, (x, z) in enumerate(seg):
                    h = round(ya + (yb - ya) * k / max(len(seg) - 1, 1)) if ya is not None and yb is not None else surface_y(world, x, z)
                    g = surface_y(world, x, z)
                    hs.append(max(h, g) if g is not None and abs(g - h) > 2 else h)
                n = stamp(world, f"relay_{r['name']}_{i}", seg, hs, width // 2, dry)
                mix = ", ".join(f"{m.split(':')[-1]} {w}%" for m, w in roads._style["road"])
                print(f"  {r['name']:14s} {len(seg):4d} m at {tuple(seg[0])}..{tuple(seg[-1])}  re-laid {n:5d} columns, width {width}   {mix}")
                total += n; fixed += 1
    files, chunks = world.save(dry)
    print(f"{fixed} spans re-laid ({total} columns), {wet_total} left under water, {chunks} chunks{' (dry)' if dry else ''}")


if __name__ == "__main__":
    main(sys.argv)
