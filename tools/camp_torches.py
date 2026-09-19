#!/usr/bin/env python3
"""Magnum torches for the camp: one diamond magnum torch (hostile-spawn suppression, 64-block
ellipsoid on the hosted config) at the gate, the square and each building complex, so the camp's
neutral ground is a thing the players can see. Heights are read from the built world.

    python camp_torches.py <world dir>     -> functions/camp_torches.mcfunction (the two of the start),
                                              functions/torch_<name>.mcfunction (each of the six), tools/camp_torches.json

Each torch stands on a 3x3 cobblestone plinth one block above ground.

Coverage is deliberately partial. Five torches cover the pocket and the two building complexes at
64-block radius; they do NOT cover the Skadowsky sector, and they do not reach the mast's field.
Extending suppression to the whole sector is the reward for `skadowsky_held`, and the mast's field
becoming camp ground is part of the same payout (docs/gscraft-skadowsky-camp.md sections 3 and 5).
The count was ten on the plateau, where the camp was a 400 x 400 box with a ring around a crater.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from camp_ruins import Ground  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FN = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft" / "functions" / "camp_torches.mcfunction"
TORCH = "magnumtorch:diamond_magnum_torch"

# name -> (x, z), world coordinates in the Skadowsky camp (start-compound doc §4; skadowsky-camp §3 for the rest).
# START are placed by camp_torches at the deploy; the rest each have their own function torch_<name>, run by the site
# loop when that building is taken (next-steps plan §1d, §2c).
SPOTS = {
    "yard": (-838, -895),           # the walled compound's yard, west of the hall (owner 2026-09-17)
    "gap": (-826, -904),            # just inside the north gate, east of the road (the compound's one opening)
    "square": (-940, -979),         # the paved junction
    "gatehouse": (-966, -947),      # the bridge's east end, Marshall
    "clinic": (-948, -1026),        # the north complex, Tony (on its own paving, not the trees north of it)
    "crossing": (-890, -975),       # the rail embankment's level crossing, the east gate, James
}
START = ("yard", "gap")
MORTAR = (-826, -881)   # the yard's tube, on the paving


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    g = Ground(Path(argv[1]))
    lines, placed = [], {}
    for name, (x, z) in SPOTS.items():
        y, top = g.top(x, z)
        if y is None:
            print("no ground at", name); continue
        base = y + 1
        own = [f"fill {x-1} {base} {z-1} {x+1} {base} {z+1} minecraft:cobblestone", f"setblock {x} {base+1} {z} {TORCH}"]
        (FN.parent / f"torch_{name}.mcfunction").write_text("\n".join(own) + "\n", encoding="utf-8")
        if name in START:
            lines += own
        placed[name] = {"x": x, "y": base + 1, "z": z, "ground": top, "start": name in START}
        print(f"  {name:11} ({x:5}, {base+1:3}, {z:5}) on {top.split(':')[-1]}{'  (start)' if name in START else ''}")
    FN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # the yard's mortar: THE TUBE'S REWARD AND NOTHING ELSE. Never run yard_mortar at a deploy (2026-09-19: it had been,
    # at both live pushes and locally, so the tube stood before anyone built it). Tagged, so yard_mortar_clear - which
    # `/gscraft reset quests` runs - takes it down; the box kills catch the untagged ones the old function summoned.
    mx, mz = MORTAR
    my, mtop = g.top(mx, mz)
    clear = ["kill @e[type=superbwarfare:mortar,tag=gscraft_yard_mortar]",
             f"kill @e[type=superbwarfare:mortar,x={mx - 10},y={my - 9},z={mz - 10},dx=20,dy=20,dz=20]",
             "kill @e[type=superbwarfare:mortar,x=-956,y=55,z=-878,dx=20,dy=20,dz=20]"]
    (FN.parent / "yard_mortar_clear.mcfunction").write_text("\n".join(clear) + "\n", encoding="utf-8")
    (FN.parent / "yard_mortar.mcfunction").write_text("\n".join(clear + [
        f"summon superbwarfare:mortar {mx} {my + 1} {mz} {{Tags:[\"gscraft_yard_mortar\"]}}"]) + "\n", encoding="utf-8")
    print(f"  mortar      ({mx:5}, {my + 1:3}, {mz:5}) on {mtop.split(':')[-1]}")
    (ROOT / "tools" / "camp_torches.json").write_text(json.dumps(placed, indent=1), encoding="utf-8")
    print("wrote", FN.name, len(placed), "torches")


if __name__ == "__main__":
    main(sys.argv)
