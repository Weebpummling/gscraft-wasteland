"""Chunky pre-generation of every transplanted rectangle plus a 2-chunk margin, merged.
usage: pregen.py <plan.json> [--plan-only]
Writes the rectangle list to pregen_rects.json and drives Chunky through the panel console.
"""
import json, subprocess, sys, time, re
from pathlib import Path

MARGIN = 2
HERE = Path(__file__).parent


def target_rects(plan):
    out = []
    for r in plan:
        x1, z1, x2, z2 = r["chunks"]; dx, dz = r["offset"]
        out.append([x1 + dx - MARGIN, z1 + dz - MARGIN, x2 + dx + MARGIN, z2 + dz + MARGIN])
    return out


def merge(rects):
    rects = [list(r) for r in rects]
    changed = True
    while changed:
        changed = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if a[0] <= b[2] + 1 and b[0] <= a[2] + 1 and a[1] <= b[3] + 1 and b[1] <= a[3] + 1:
                    rects[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del rects[j]; changed = True; break
            if changed: break
    return sorted(rects, key=lambda r: (r[2]-r[0]+1)*(r[3]-r[1]+1), reverse=True)


def panel(*args):
    return subprocess.run([sys.executable, str(HERE / "bisectpanel.py"), *args], capture_output=True, text=True).stdout


def finished_count():
    log = panel("cat", "/logs/latest.log")
    return len(re.findall(r"\[Chunky\] Task finished", log)), log


def main(argv):
    plan = json.load(open(argv[1]))
    rects = merge(target_rects(plan))
    total = sum((r[2]-r[0]+1)*(r[3]-r[1]+1) for r in rects)
    json.dump(rects, open(HERE / "pregen_rects.json", "w"), indent=1)
    print(f"{len(rects)} rectangles, {total} chunks (incl. existing)")
    for r in rects: print("  chunks", r, "=", (r[2]-r[0]+1)*(r[3]-r[1]+1))
    if "--plan-only" in argv: return
    panel("cmd", "chunky quiet 30")
    panel("cmd", "chunky world wasteland")
    panel("cmd", "chunky shape rectangle")
    for n, r in enumerate(rects, 1):
        bx1, bz1, bx2, bz2 = r[0]*16, r[1]*16, r[2]*16+15, r[3]*16+15
        before, _ = finished_count()
        panel("cmd", f"chunky corners {bx1} {bz1} {bx2} {bz2}")
        panel("cmd", "chunky start")
        t0 = time.time(); print(f"[{n}/{len(rects)}] started {r} at {time.strftime('%H:%M:%S')}", flush=True)
        while True:
            time.sleep(20)
            now, log = finished_count()
            if now > before: break
            if "already running" in log[-2000:]:
                pass
            if time.time() - t0 > 3 * 3600:
                print("TIMEOUT on", r, flush=True); return
        print(f"[{n}/{len(rects)}] finished in {int(time.time()-t0)} s", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv)
