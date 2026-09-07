#!/usr/bin/env python3
"""Magnum torches for the camp: one diamond magnum torch (hostile-spawn suppression, 64-block
ellipsoid on the hosted config) at the gate, the square and each building complex, so the camp's
neutral ground is a thing the players can see. Heights are read from the built world.

    python camp_torches.py <world dir>     -> functions/camp_torches.mcfunction, tools/camp_torches.json

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

# name -> (x, z), world coordinates in the Skadowsky camp (docs/gscraft-skadowsky-camp.md section 3)
SPOTS = {
    "gatehouse": (-966, -947),      # the bridge's east end, Marshall
    "square": (-940, -979),         # the paved junction, the world spawn
    "clinic": (-948, -1026),        # the north complex, Tony (on its own paving, not the trees north of it)
    "yard": (-957, -862),           # the south complex, Walker and Michael
    "crossing": (-890, -975),       # the rail embankment's level crossing, the east gate, James
}


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
        lines.append(f"fill {x-1} {base} {z-1} {x+1} {base} {z+1} minecraft:cobblestone")
        lines.append(f"setblock {x} {base+1} {z} {TORCH}")
        placed[name] = {"x": x, "y": base + 1, "z": z, "ground": top}
        print(f"  {name:11} ({x:5}, {base+1:3}, {z:5}) on {top.split(':')[-1]}")
    FN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "tools" / "camp_torches.json").write_text(json.dumps(placed, indent=1), encoding="utf-8")
    print("wrote", FN.name, len(placed), "torches")


if __name__ == "__main__":
    main(sys.argv)
