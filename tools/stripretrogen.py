"""Strip the `below_zero_retrogen` marker from chunks in a rectangle.

The 1.12 saves were brought forward with the vanilla upgrader, which tags chunks for below-zero retrogen: the marker
tells a modern server to re-run world generation for the part of the chunk under y 0 the next time it is loaded. On a
handful of chunks that is invisible. On the 6,098 chunks of the expanded desert city it is not: the retrogen runs
through the Lost Cities generator, the chunk pipeline never finishes, and the server hangs until the watchdog kills
the tick. It reproduced on the local server too, with 20 GB of heap and nobody connected: 18 minutes stuck on
"Preparing spawn area" and no "Done".

The marker is on 80% of the expanded city's chunks and on none of the chunks in the areas that have always worked
(the Pripyat cell, Skadowsky), which is what identified it. `blending_data` is present in both and is left alone.

usage: stripretrogen.py <world dir> <x0> <z0> <x1> <z1> [--dry-run]
       stripretrogen.py G:/GSCraft/server/wasteland-v8 -3616 -1056 -2337 748
"""
import sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of

TAGS = ("below_zero_retrogen",)


def main(a):
    if len(a) < 6: sys.exit(__doc__)
    world = Path(a[1]); x0, z0, x1, z1 = (int(v) for v in a[2:6]); dry = "--dry-run" in a
    cx0, cz0, cx1, cz1 = x0 >> 4, z0 >> 4, x1 >> 4, z1 >> 4
    regions = {}
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            regions.setdefault(region_of(cx, cz), []).append((cx, cz))
    t0 = time.time(); total = touched = 0
    for rk, chunks in sorted(regions.items()):
        p = world / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        if not p.exists(): continue
        reg = read_region_raw(p); out = {}
        for cx, cz in chunks:
            e = reg.get(slot_of(cx, cz))
            if not e: continue
            total += 1
            name, root = R(e[2]).root()
            if not any(t in root for t in TAGS): continue
            for t in TAGS: root.pop(t, None)
            out[slot_of(cx, cz)] = (e[0], 2, NbtW().root(name, root)); touched += 1
        if out and not dry:
            reg.update(out); write_region(p, reg)
        if out: print(f"  r.{rk[0]}.{rk[1]}: {len(out)} chunks stripped", flush=True)
    print(f"{touched} of {total} chunks carried the marker; {time.time()-t0:.0f}s{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main(sys.argv)
