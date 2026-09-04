"""Place the kept generated sites into a world whose chunks already exist, in small batches, on the local server.

usage: place_kept.py <server dir> [--plan buildmap/structure_plan_v7.json] [--batch 6] [--wait 25]
       place_kept.py <server dir> --test "apotheosis:tower_sand,-300,-900" "underground_bunkers:underground_bunker,-600,-700" ...

`place structure` refuses chunks that are not loaded, and a whole-world force-load makes the server generate or
load hundreds of chunks at once (watchdog). So: boot the server, then per batch of sites: `forceload add` a 3x3
chunk area around each, wait for them to load, `place structure` each, `forceload remove all`. Save and stop.
Then `--verify` (default on) probes each site for blocks the structure type is made of and prints the result.
Run this on a world whose chunks exist (after localpregen.py), never on a fresh world.
"""
import subprocess, sys, time, json, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
JAVA = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot\bin\java.exe"
MARK = {"apotheosis:tower": ("quartz", "glass_pane", "iron_bars", "spruce_planks", "sandstone_slab"),
        "minecraft:village": ("planks", "dirt_path", "hay_block", "bell", "composter", "cobblestone"),
        "underground_bunkers:underground_bunker": ("concrete", "iron_door", "chain", "stone_bricks", "iron_bars"),
        "man:house": ("planks", "glass", "door", "cobblestone"), "minecraft:pillager_outpost": ("dark_oak", "cobblestone", "fence"),
        "minecraft:ancient_city": ("deepslate_tile", "sculk", "soul"), "minecraft:trail_ruins": ("terracotta", "gravel", "brick"),
        "minecraft:igloo": ("snow_block", "ice"), "minecraft:desert_pyramid": ("sandstone", "terracotta"),
        "minecraft:jungle_pyramid": ("cobblestone", "mossy"), "minecraft:monument": ("prismarine", "sea_lantern"),
        "minecraft:stronghold": ("stone_bricks", "iron_bars"), "minecraft:mansion": ("dark_oak", "cobblestone", "birch")}


def type_of(sid):
    if sid.startswith("apotheosis:tower"): return "apotheosis:tower"
    if sid.startswith("minecraft:village"): return "minecraft:village"
    return sid


# force-load radius in blocks around a site: `place structure` refuses if ANY chunk of the structure's
# bounding box is unloaded, and bunkers, villages, cities and mansions span far more than 3x3 chunks
BIG = {"underground_bunkers:underground_bunker", "minecraft:village", "minecraft:ancient_city", "minecraft:mansion",
       "minecraft:stronghold", "minecraft:monument", "minecraft:pillager_outpost", "minecraft:trail_ruins"}


def radius_of(sid):
    return 112 if type_of(sid) in BIG else 40


def sites_from(a):
    if "--test" in a:
        out = []
        for spec in a[a.index("--test") + 1:]:
            if spec.startswith("--"): break
            sid, x, z = spec.split(","); out.append({"id": sid, "x": int(x), "z": int(z)})
        return out
    plan = Path(a[a.index("--plan") + 1]) if "--plan" in a else HERE.parent / "buildmap" / "structure_plan_v7.json"
    p = json.load(open(plan)); return [e for entries in p["keep"].values() for e in entries]


def run_server(sdir: Path, sites, batch, wait):
    stamp = time.strftime("%Y%m%d-%H%M%S"); logf = sdir / f"console-place-{stamp}.log"; con = open(logf, "w", encoding="utf-8")
    p = subprocess.Popen([JAVA, "@user_jvm_args.txt", "@libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt", "nogui"],
                         cwd=sdir, stdin=subprocess.PIPE, stdout=con, stderr=subprocess.STDOUT, text=True)
    def tail(): return logf.read_text(encoding="utf-8", errors="replace")
    def send(c):
        try: p.stdin.write(c + "\n"); p.stdin.flush(); return True
        except OSError: return False
    t0 = time.time()
    while "Done (" not in tail():
        if p.poll() is not None: print("server exited before Done; see", logf); return 1
        if time.time() - t0 > 1200: p.kill(); print("boot timeout"); return 1
        time.sleep(3)
    print(f"Done after {int(time.time() - t0)} s; {len(sites)} sites in batches of {batch}", flush=True)
    # big structures go two at a time (a 112-block radius is 15x15 chunks each), small ones in the given batch
    order = sorted(sites, key=lambda e: type_of(e["id"]) in BIG)
    batches = []
    small = [e for e in order if type_of(e["id"]) not in BIG]; big = [e for e in order if type_of(e["id"]) in BIG]
    batches += [small[i:i + batch] for i in range(0, len(small), batch)]
    batches += [big[i:i + 2] for i in range(0, len(big), 2)]
    for i, b in enumerate(batches):
        for e in b:
            r = radius_of(e["id"]); send(f"forceload add {e['x'] - r} {e['z'] - r} {e['x'] + r} {e['z'] + r}")
        time.sleep(wait if not any(type_of(e["id"]) in BIG for e in b) else wait * 2)
        for e in b: send(f"place structure {e['id']} {e['x']} 64 {e['z']}"); time.sleep(1)
        time.sleep(3); send("forceload remove all"); time.sleep(2)
        if p.poll() is not None: print("server exited during placement; see", logf); return 1
        print(f"  batch {i // batch + 1}: {', '.join(e['id'].split(':')[1] + '@' + str(e['x']) + ',' + str(e['z']) for e in b)}", flush=True)
    time.sleep(5); send("save-all flush"); time.sleep(5); send("stop")
    try: p.wait(timeout=600)
    except subprocess.TimeoutExpired: p.kill(); print("stop timed out; killed")
    txt = tail(); print(f"server exit {p.returncode}; ERROR lines {len([l for l in txt.splitlines() if '/ERROR]' in l])}; log {logf}")
    return 0


def verify(world: Path, sites):
    from terrain import World
    w = World(world); ok = 0
    for e in sites:
        marks = MARK.get(type_of(e["id"]), ()); found = collections.Counter(); gen = False
        for dx in range(-20, 21, 4):
            for dz in range(-20, 21, 4):
                if w.top(e["x"] + dx, e["z"] + dz)[0] is None: continue
                gen = True
                for y in range(-40, 300):
                    n = w.get(e["x"] + dx, y, e["z"] + dz)
                    if n and n != "minecraft:air" and any(m in n for m in marks): found[n] += 1
        good = bool(found)
        ok += good
        print(f"  {'ok     ' if good else 'MISSING'} {e['id']} at {e['x']},{e['z']} generated={gen} {dict(found.most_common(3))}")
    print(f"placed sites with their blocks present: {ok}/{len(sites)}")
    return ok == len(sites)


def main(a):
    if len(a) < 2: sys.exit(__doc__)
    sdir = Path(a[1]).resolve(); sites = sites_from(a)
    batch = int(a[a.index("--batch") + 1]) if "--batch" in a else 6
    wait = int(a[a.index("--wait") + 1]) if "--wait" in a else 25
    level = next((l.split("=", 1)[1].strip() for l in (sdir / "server.properties").read_text().splitlines() if l.startswith("level-name=")), "world")
    (sdir / level / "session.lock").unlink(missing_ok=True)
    rc = run_server(sdir, sites, batch, wait)
    if rc == 0 and "--no-verify" not in a: verify(sdir / level, sites)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
