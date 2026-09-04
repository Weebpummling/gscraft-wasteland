#!/usr/bin/env python3
"""Magnum torches for the camp: one diamond magnum torch (hostile-spawn suppression, 64-block
ellipsoid on the hosted config) at each NPC pad, at the gate, and on a ring around the crater, so
the camp's neutral ground is a thing the players can see. Heights are read from the built world.

    python camp_torches.py <world dir>     -> functions/camp_torches.mcfunction, tools/camp_torches.json

Each torch stands on a 3x3 cobblestone plinth one block above ground. Coverage: the camp outline
is 384x384 and the torch radius 64, so the nine positions below leave no gap wider than the radius.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from camp_ruins import Ground  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FN = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft" / "functions" / "camp_torches.mcfunction"
TORCH = "magnumtorch:diamond_magnum_torch"

# name -> (x, z); pads from tools/pads_camp.json centres, the gate, and four ring points
SPOTS = {
    "walker": (80, 95), "michael": (-24, 111), "marshall": (162, 8), "tony": (-90, -92),
    "tune": (48, -112), "james": (-146, -146),
    "ring_west": (-120, 20), "ring_south": (20, 150), "ring_north": (-40, -40), "ring_east": (110, -70),
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
