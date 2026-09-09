"""Comprehensive spawn probe: one mob per (faction, area) pair, checked by name."""
import subprocess, sys
P = [  # tag, mob, x, z, expected
 ("mil_fb",   "minecraft:pillager", -825,  -690,  "Militia Rifleman"),
 ("mil_plant","minecraft:pillager",  400,   590,  "Militia Rifleman"),
 ("scav_wood","minecraft:pillager", -2000, -600,  "Scavenger"),
 ("scav_vind","minecraft:vindicator",-2000,-600,  "Scavenger"),
 ("dead_skad","minecraft:zombie",   -800, -1200,  "Worker"),
 ("dead_plnt","minecraft:zombie",    400,   590,  "Worker"),
 ("dead_town","minecraft:zombie",  -2800, -2500,  "The Dead"),
 ("dead_farm","minecraft:zombie",  -2100,  -900,  "The Dead"),
 ("spid_wood","minecraft:spider",  -2000, -600,  ""),
 ("spid_mega","minecraft:spider",    500, -1800,  None),
 ("no_krot",  "minecraft:zombie",  -3200, -1200,  None),
 ("no_mega",  "minecraft:pillager",  500, -1800,  None),
 ("no_camp",  "minecraft:zombie",   -870,  -950,  None),
 ("no_lib",   "minecraft:zombie",  -2430, -3760,  None),
]
args = [sys.executable, "G:/GSCraft/repo/tools/localtest.py"]
for tag, mob, x, z, _ in P:
    args.append(f"forceload add {x-8} {z-8} {x+8} {z+8}")
for tag, mob, x, z, _ in P:
    args.append(f'summon {mob} {x} 100 {z} {{PersistenceRequired:1b,Tags:["{tag}"]}}')
for tag, mob, x, z, _ in P:
    args.append(f"data get entity @e[tag={tag},limit=1] CustomName")
r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
out = r.stdout
ok = bad = 0
for tag, mob, x, z, want in P:
    seg = out.split(f"> data get entity @e[tag={tag},limit=1] CustomName")
    got = seg[1].splitlines()[1].strip() if len(seg) > 1 and len(seg[1].splitlines()) > 1 else "?"
    if want is None:
        good = "Found no elements" in got or "No entity" in got or got == ""
        shown = "denied" if good else got[:44]
    else:
        good = want in got
        shown = want if good else got[:44]
    ok, bad = ok + good, bad + (not good)
    print(f"  {'PASS' if good else 'FAIL'}  {tag:10s} {mob.split(':')[1]:12s} at {x:6d},{z:6d}  -> {shown}")
print(f"\n{ok} pass, {bad} fail")
