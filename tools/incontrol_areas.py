"""Write In Control's areas.json from the design's own extents.

`Area` reads flat `x`, `y`, `z` plus `dimx`, `dimy`, `dimz`. Two things about that were got wrong before
and are worth stating, because neither produces an error:

  1. a `center: {x,y,z}` object parses as valid JSON and then fails at bind time with
     "Area '<name>' has no x!", followed by "Cannot find area '<name>'!" wherever a rule uses it. The
     area silently does not exist.
  2. `dim*` is a **half-extent**, not the full width. Measured 2026-09-09: with `plant` written as
     centre x 25 / dimx 2350, a pillager at x -2000 was still inside it - 2,000 blocks from a box meant
     to end at -1150. Every area written as a full width is twice its intended size, which is worse than
     it sounds, because the areas overlap and the first matching rule wins.

So the boxes below are given as the design's real extents and halved here, once, in one place.

    incontrol_areas.py [--dry-run]
"""
import json
import sys
from pathlib import Path

AREAS = Path(r"G:/GSCraft/server/config/incontrol/areas.json")

# name: (x0, x1, z0, z1, source)
BOXES = {
    "plant":   (-1150, 1200, -400, 700, "poi-coordinates §2, the power station complex"),
    "hub":     (-3568, -2385, -1008, 700, "sectors_v8, Novo Expograd - the Machines', deferred"),
    "farbank": (-1050, -600, -1000, -380, "the east-bank spine, derived in militia_rules.py"),
    "camp":    (-978, -770, -1060, -845, "sectors_v8, defined only to keep enemies out of it"),
}
Y0, Y1 = -64, 320          # the whole world column


def main(argv):
    out = []
    for name, (x0, x1, z0, z1, why) in BOXES.items():
        out.append({
            "name": name,
            "dimension": "minecraft:overworld",
            "type": "box",
            "x": (x0 + x1) // 2, "y": (Y0 + Y1) // 2, "z": (z0 + z1) // 2,
            # half-extents, not widths
            "dimx": (x1 - x0) // 2, "dimy": (Y1 - Y0) // 2, "dimz": (z1 - z0) // 2,
        })
        print(f"  {name:8s} x {x0:6d}..{x1:<6d} z {z0:6d}..{z1:<6d}  {why}")
    if "--dry-run" in argv:
        print("DRY RUN, nothing written")
        return 0
    AREAS.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    print(f"written to {AREAS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
