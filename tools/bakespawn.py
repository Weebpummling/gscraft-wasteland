"""Bake heightmaps and lighting into a region of the world offline, by walking the world spawn across it.

Why not the obvious ways. `/forceload add` calls getChunkBlocking on the server thread; in an area whose chunks
still need their heightmaps and light computed, that call never returns and the watchdog kills the tick, so it
crashes the server instead of baking it (2026-09-06, six crashes). Chunky skips chunks that already have status
`full`, so it reports the whole area processed in seconds and relights nothing. A player walking in triggers the
same blocking load through the collision code.

What does work is the server's own startup path: `prepareLevels` loads an 11-chunk radius around the world spawn
through the normal asynchronous chunk pipeline, prints its progress, and saves the result. So: set the spawn, boot
the server, wait for "Done", stop, move the spawn, repeat. 441 chunks per pass, stepping 16 chunks so the passes
overlap.

usage: bakespawn.py <server dir> <x0> <z0> <x1> <z1> [--step 16] [--restore-spawn X Z] [--dry-run]
       bakespawn.py G:/GSCraft/server -3568 -1008 -2385 700 --restore-spawn -2555 -2539

Run it with the hosted server's copy of the world staged into <server dir>, then upload the region files that
changed. The real world spawn is put back at the end.
"""
import gzip, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import R, W as NbtW

BOOT_PAT = re.compile(r'Done \(')
FAIL_PAT = re.compile(r"Watchdog|Encountered an unexpected exception|Failed to start")


def set_spawn(level: Path, x: int, z: int, y: int = 80):
    name, root = R(gzip.decompress(level.read_bytes())).root()
    d = root["Data"][1]
    for k, v in (("SpawnX", x), ("SpawnY", y), ("SpawnZ", z)):
        d[k] = (d[k][0], v)
    level.write_bytes(gzip.compress(NbtW().root(name, root)))


def run_once(server: Path, timeout: int):
    """Boot the server, wait for Done, stop it. Returns (ok, seconds, last lines)."""
    java = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot\bin\java.exe"
    args = [java, "@user_jvm_args.txt",
            "@libraries/net/minecraftforge/forge/1.20.1-47.4.23/win_args.txt", "nogui"]
    t0 = time.time(); tail = []
    p = subprocess.Popen(args, cwd=str(server), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, errors="replace", bufsize=1)
    ok = False
    try:
        for line in p.stdout:
            tail.append(line.rstrip()[-160:]); tail[:] = tail[-12:]
            if BOOT_PAT.search(line): ok = True; break
            if FAIL_PAT.search(line): break
            if time.time() - t0 > timeout: break
    except Exception:
        pass
    try:
        p.stdin.write("stop\n"); p.stdin.flush()
    except Exception:
        pass
    try:
        p.wait(timeout=180)
    except subprocess.TimeoutExpired:
        p.kill(); p.wait()
    return ok, time.time() - t0, tail


def main(a):
    if len(a) < 6: sys.exit(__doc__)
    server = Path(a[1]); x0, z0, x1, z1 = (int(v) for v in a[2:6])
    step = int(a[a.index("--step") + 1]) if "--step" in a else 16          # chunks between spawn points
    dry = "--dry-run" in a
    level = server / (re.search(r"level-name=(.+)", (server / "server.properties").read_text()).group(1).strip()) / "level.dat"
    def seq(a, b):
        # spawn points 176 blocks inside each edge, stepping `step` chunks, with the far edge always covered
        v = list(range(a + 176, b - 175, step * 16))
        if not v or v[-1] < b - 176: v.append(b - 176)
        return v
    pts = [(x, z) for x in seq(x0, x1) for z in seq(z0, z1)]
    print(f"{len(pts)} spawn points, 441 chunks each, over x {x0}..{x1} z {z0}..{z1}")
    print(f"level.dat: {level}")
    if dry:
        for p in pts[:6]: print("   ", p)
        return
    backup = level.with_suffix(".dat.bakespawn.bak")
    if not backup.exists(): shutil.copy2(level, backup); print(f"  level.dat backed up as {backup.name}")
    t0 = time.time(); good = bad = 0
    for i, (x, z) in enumerate(pts, 1):
        set_spawn(level, x, z)
        ok, secs, tail = run_once(server, timeout=900)
        good += ok; bad += (not ok)
        print(f"  {i:3d}/{len(pts)}  spawn ({x:6d},{z:6d})  {'ok' if ok else 'FAILED'}  {secs:5.0f}s   total {time.time()-t0:.0f}s", flush=True)
        if not ok:
            for l in tail: print("        ", l)
    if "--restore-spawn" in a:
        i = a.index("--restore-spawn"); set_spawn(level, int(a[i + 1]), int(a[i + 2]))
        print(f"  world spawn restored to ({a[i+1]}, {a[i+2]})")
    print(f"{good} passes ok, {bad} failed, {time.time()-t0:.0f}s total")


if __name__ == "__main__":
    main(sys.argv)
