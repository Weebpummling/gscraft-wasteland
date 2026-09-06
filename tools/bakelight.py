"""Bake heightmaps and lighting into freshly written chunks, on the hosted server, before anyone flies into them.

Every tool in this repo that edits chunks (transplant, integrate, roads, river, underground, reskin) drops the
Heightmaps tag and clears `isLightOn`, because the game recomputes both correctly and writing them by hand is not worth
it. That is fine for a few hundred chunks. It is not fine for a contiguous block of thousands: on 2026-09-06 the
expanded desert city went up with 6,098 unbaked chunks, a player flew into it, and the server thread blocked inside a
collision sweep waiting on chunk loads until the watchdog killed the tick at 60 s. It did that on every reconnect.

Chunky does not help here: it skips chunks that already have status `full`, so it reported 8,175 chunks in four seconds
and relit none of them. What does work is force-loading the area in blocks with no player online, which takes the chunks
through a real load, computes the heightmaps and the light, and saves them.

usage: bakelight.py <x0> <z0> <x1> <z1> [--step 256] [--dwell 30] [--dry-run]
       bakelight.py -3568 -1008 -2385 700

Run it with the server up and nobody online. 256 blocks is the forceload limit of 16 x 16 chunks per command; `--dwell`
is how long each block is held before saving, and it is the number to raise if a check afterwards still finds unlit
chunks. Verify with `bisectpanel.py get /wasteland-v8/region/r.<rx>.<rz>.mca` and count `isLightOn`.
"""
import os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cmd(c, dry=False):
    if dry:
        print("  >", c); return
    subprocess.run([sys.executable, str(HERE / "bisectpanel.py"), "cmd", c],
                   capture_output=True, text=True, env={**os.environ, "MSYS_NO_PATHCONV": "1"})


def main(a):
    if len(a) < 5: sys.exit(__doc__)
    x0, z0, x1, z1 = (int(v) for v in a[1:5])
    step = int(a[a.index("--step") + 1]) if "--step" in a else 256
    dwell = int(a[a.index("--dwell") + 1]) if "--dwell" in a else 30
    dry = "--dry-run" in a
    blocks = [(x, z, min(x + step - 1, x1), min(z + step - 1, z1))
              for x in range(x0, x1 + 1, step) for z in range(z0, z1 + 1, step)]
    chunks = ((x1 - x0) // 16 + 1) * ((z1 - z0) // 16 + 1)
    print(f"{len(blocks)} blocks of up to {(step//16)**2} chunks, about {chunks:,} chunks, "
          f"{len(blocks) * (dwell + 8) / 60:.0f} minutes at {dwell}s dwell")
    t0 = time.time()
    for k, (a0, b0, a1, b1) in enumerate(blocks, 1):
        cmd(f"forceload add {a0} {b0} {a1} {b1}", dry)
        if not dry: time.sleep(dwell)
        cmd("save-all", dry)
        if not dry: time.sleep(6)
        cmd("forceload remove all", dry)
        if not dry: time.sleep(2)
        print(f"  {k}/{len(blocks)}  {time.time()-t0:.0f}s", flush=True)
    cmd("save-all flush", dry)
    print(f"bake done in {time.time()-t0:.0f}s; check a region's isLightOn count before letting anyone in")


if __name__ == "__main__":
    main(sys.argv)
