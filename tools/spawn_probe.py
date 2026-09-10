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
    # the Militia, east of the river
    ("mil_plant", "minecraft:pillager",             400,   590, "NATO Grenadier"),
    ("mil_out",   "immersiveengineering:bulwark",  -840,  -540, "NATO Shield"),
    ("mil_front", "immersiveengineering:fusilier", -930, -1150, "NATO Gunner"),
    ("mil_skad",  "minecraft:pillager",            -710,  -900, "NATO Grenadier"),

    # the Column, west of the river
    ("col_town",  "minecraft:pillager",           -2400, -2900, "RUAF Grenadier"),
    ("col_out",   "immersiveengineering:bulwark", -1500, -1060, "RUAF Shield"),
    ("col_front", "immersiveengineering:fusilier",-1200, -1000, "RUAF Marksman"),
    ("col_skad",  "minecraft:pillager",           -1035,  -960, "RUAF Grenadier"),

    # the Dead: ambient everywhere, and by site where a site claims them
    ("dead_swit", "minecraft:zombie",  -815,   105, "Plant Worker"),
    ("dead_reac", "minecraft:zombie",  -642,   518, ("Plant Worker", "Containment Crew")),
    ("dead_hosp", "minecraft:zombie",  -782, -1277, "The Infected"),
    ("dead_yard", "minecraft:zombie",  -850,  -800, "Yard Hand"),
    ("dead_stad", "minecraft:zombie", -2395, -3482, ("The Dead", "Peacekeeper")),
    ("dead_road", "minecraft:zombie", -1500, -2500, "The Dead"),
    ("dead_wood", "minecraft:zombie", -2000,  -600, "The Dead"),
    ("dead_far",  "minecraft:zombie",   900, -3000, "The Dead"),

    ("drwn_intk", "minecraft:drowned",  893,   156, "The Drowned"),
    ("drwn_brdg", "minecraft:drowned", -904, -2200, "Drowned Patrol"),

    # the Scavengers hold whatever neither army does
    ("scav_wood", "minecraft:vindicator", -2000, -600, "Scavenger Raider"),
    ("scav_road", "minecraft:pillager",   -1500, -2500,
     ("Scavenger", "Scrapper", "Scavenger Captain")),

    # vanilla's own Dead: an untagged zombie is refused everywhere, which is what keeps density in the
    # area spawner's hands
    ("wild_town", "minecraft:zombie",  -2800, -2500, None),
    ("wild_skad", "minecraft:zombie",   -850, -1100, None),

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
        # Probes stand in for the area spawner, so they carry its gs_placed tag - without it In Control
        # now refuses the Dead, correctly, and the probe would report a failure that is not one. A tag
        # starting "wild_" is left untagged on purpose, to prove the refusal itself.
        tags = f'"{tag}"' if tag.startswith("wild_") else f'"{tag}","gs_placed"'
        args.append(f'summon {mob} {x} 100 {z} {{PersistenceRequired:1b,Tags:[{tags}]}}')
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
