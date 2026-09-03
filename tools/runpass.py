"""Full terrain pass on a local world copy: strongpoint pads, starting-area clear, transplant-edge
smoothing, pad ramps, starting-area outline, then a gap re-survey and height-line checks.

usage: runpass.py <world dir> <transplant_plan.json> <strongpoints.json> <start x1> <start z1> <start x2> <start z2>
Assumes the world copy is the pristine post-pregen pull (restore from pull/region.zip first).
"""
import json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).parent


def run(*a):
    out = subprocess.run([sys.executable, str(HERE / "terrain.py"), *a], check=True, capture_output=True, text=True).stdout
    print(out.strip(), flush=True)
    return out


def main(argv):
    w, plan, spfile = argv[1], argv[2], argv[3]
    sx1, sz1, sx2, sz2 = argv[4:8]
    crater = ["-16", "-16", "47", "47"]
    tower = ["64", "-144", "191", "-17"]          # the radio tower compound in the camp: never cleared or smoothed over
    sps = json.load(open(spfile))
    t = time.time(); ys = {}
    for p in sps:
        x1, z1, x2, z2 = map(str, p["blocks"])
        print(f"=== pad {p['name']} ===", flush=True)
        out = run("pad", w, x1, z1, x2, z2, "--label", p["name"])
        ys[p["name"]] = int(out.split("at y=")[1].split(":")[0])
    print("=== clear starting area ===", flush=True)
    run("pad", w, sx1, sz1, sx2, sz2, "--protect", *crater, *tower, "--label", "starting_area", "--clear-only")
    print("=== smooth ===", flush=True); run("smooth", w, plan)
    for p in sps:
        x1, z1, x2, z2 = map(str, p["blocks"])
        print(f"=== ramp {p['name']} ===", flush=True)
        run("ramp", w, x1, z1, x2, z2, "--y", str(ys[p["name"]]), "--label", p["name"])
    print("=== outline starting area ===", flush=True); run("outline", w, sx1, sz1, sx2, sz2, "--label", "starting_area")
    json.dump(ys, open(HERE / "pad_heights.json", "w"), indent=1)
    print(f"edits done in {int(time.time() - t)} s", flush=True)
    print("=== gaps after ===", flush=True)
    out = subprocess.run([sys.executable, str(HERE / "terrain.py"), "gaps", w, plan], check=True, capture_output=True, text=True).stdout
    lines = out.splitlines(); hist = {}
    for ln in lines:
        if ln.startswith("  ") and ":" in ln and ln.strip()[0] in "+-":
            k, v = ln.split(":"); hist[int(k)] = int(v)
    lo = sum(v for k, v in hist.items() if k < -9); hi = sum(v for k, v in hist.items() if k > 9)
    mid = sum(v for k, v in hist.items() if -9 <= k <= 9)
    print(lines[0]); print(f"gap <-9: {lo}   -9..9: {mid}   >9: {hi}")
    print([ln for ln in lines if ln.startswith("columns with")][0])
    sys.path.insert(0, str(HERE))
    from terrain import World
    wd = World(w)
    print("=== spawn line z=16, x -200..-8 ===")
    for x in range(-200, -7, 8):
        g = wd.ground(x, 16); y, b = wd.top(x, 16); print(f"  x={x:5d} ground={g} top={y} {b}")
    for p in sps:
        x1, z1, x2, z2 = p["blocks"]; zm = (z1 + z2) // 2
        print(f"=== {p['name']} west edge z={zm}, x {x1 - 60}..{x1 + 10} ===")
        for x in range(x1 - 60, x1 + 11, 7):
            g = wd.ground(x, zm); y, b = wd.top(x, zm); print(f"  x={x:5d} ground={g} top={y} {b}")
    print("PASS DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv)
