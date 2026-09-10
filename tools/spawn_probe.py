"""Summon one mob per (rank, site) and check what it comes out as.

The point is that In Control's rule order is not readable by inspection: the first matching rule consumes
the mob, and every mistake in that order is silent. So the check is empirical - stand a mob at a
coordinate inside each area and read its name back.

Run against the LOCAL server. With the hold lifted every dressed probe should pass; with the hold in
place every probe returns "denied", which is itself the check that the hold works.

    spawn_probe.py
"""
import subprocess
import sys
from pathlib import Path

LOCALTEST = Path(__file__).resolve().parent / "localtest.py"

# tag, entity, x, z, expected name (None = should not exist at all)
PROBES = [
    # the Militia, by rank, on the spine
    ("mil_shield", "immersiveengineering:bulwark",  -825, -690, "Militia Shield"),
    ("mil_gunner", "immersiveengineering:fusilier", -825, -690, "Militia Gunner"),
    ("mil_troop",  "immersiveengineering:commando", -825, -690, ("Militia Trooper", "Militia Sergeant")),
    ("mil_rifle",  "minecraft:pillager",            -825, -690, "Militia Rifleman"),
    ("mil_plant",  "minecraft:pillager",             400,  590, "Militia Rifleman"),

    # the Dead, by site
    ("dead_swit", "minecraft:zombie",  -815,   105, "Plant Worker"),
    ("dead_reac", "minecraft:zombie",  -642,   518, ("Plant Worker", "Containment Crew")),
    ("dead_turb", "minecraft:zombie",   400,   590, "Plant Worker"),
    ("dead_hosp", "minecraft:zombie",  -782, -1277, "The Infected"),
    ("dead_yard", "minecraft:zombie",  -850,  -800, "Yard Hand"),
    ("dead_stad", "minecraft:zombie", -2395, -3482, ("The Dead", "Peacekeeper")),
    ("dead_blok", "minecraft:zombie", -2100, -2000, "The Dead"),
    ("dead_farm", "minecraft:zombie", -2100,  -900, "The Dead"),

    # the drowned, where there is water
    ("drwn_intk", "minecraft:drowned",  893,   156, "The Drowned"),
    ("drwn_brdg", "minecraft:drowned", -904, -2200, "Drowned Patrol"),

    # the Scavengers, four looks
    # a pillager can roll the rare Scrapper or Captain variant, so any Scavenger-family name passes
    ("scav_pill", "minecraft:pillager",   -2000,  -600, ("Scavenger", "Scrapper", "Scavenger Captain")),
    ("scav_raid", "minecraft:vindicator", -2000,  -600, "Scavenger Raider"),
    ("scav_eldr", "minecraft:evoker",     -2000,  -600, "Scavenger Elder"),
    ("scav_road", "minecraft:pillager",   -1500, -2500, ("Scavenger", "Scrapper", "Scavenger Captain")),

    # builds: nothing at all
    ("no_krot", "minecraft:zombie",   -3200, -1200, None),
    ("no_mega", "minecraft:pillager",   500, -1800, None),
    ("no_camp", "minecraft:zombie",    -870,  -950, None),
    ("no_lib",  "minecraft:zombie",   -2430, -3760, None),
]


def main():
    args = [sys.executable, str(LOCALTEST)]
    for tag, mob, x, z, _ in PROBES:
        args.append(f"forceload add {x - 8} {z - 8} {x + 8} {z + 8}")
    for tag, mob, x, z, _ in PROBES:
        args.append(f'summon {mob} {x} 100 {z} {{PersistenceRequired:1b,Tags:["{tag}"]}}')
    for tag, mob, x, z, _ in PROBES:
        args.append(f"data get entity @e[tag={tag},limit=1] CustomName")

    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout
    ok = bad = 0
    for tag, mob, x, z, want in PROBES:
        seg = out.split(f"> data get entity @e[tag={tag},limit=1] CustomName")
        lines = seg[1].splitlines() if len(seg) > 1 else []
        got = lines[1].strip() if len(lines) > 1 else "?"
        if want is None:
            good = "Found no elements" in got or "No entity" in got or got == ""
            shown = "denied" if good else got[:40]
        else:
            wants = want if isinstance(want, tuple) else (want,)
            good = any(f'"{w}"' in got for w in wants)
            shown = next((w for w in wants if f'"{w}"' in got), got[:40])
        ok, bad = ok + good, bad + (not good)
        print(f"  {'PASS' if good else 'FAIL'}  {tag:10s} {mob.split(':')[-1]:12s} "
              f"{x:6d},{z:6d}  -> {shown}")
    print(f"\n{ok} pass, {bad} fail")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
