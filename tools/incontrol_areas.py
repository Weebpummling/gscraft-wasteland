"""Write In Control's areas.json: the builds enemies are kept out of, and the ground they hold.

Two things about the schema were got wrong before and neither produces an error:

  1. a `center: {x,y,z}` object parses as valid JSON and then fails at bind time with
     "Area '<name>' has no x!", followed by "Cannot find area '<name>'!" wherever a rule uses it - the
     area silently does not exist. `Area` reads flat `x`, `y`, `z`.
  2. `dim*` is a **half-extent**, not the full width. Measured 2026-09-09: with `plant` written as
     centre x 25 / dimx 2350, a pillager at x -2000 was still inside it, two thousand blocks from a box
     meant to end at -1150. Every area written as a full width is twice its size, and because areas
     overlap and the first matching rule wins, an oversized one quietly steals mobs from every rule
     after it.

So the boxes below are the design's real extents, halved here, once.

**Builds are no-spawn ground (owner, 2026-09-09):** KROT is a work in progress and the same applies to
every other player-built and transplanted site. Enemies belong in the base map's own places - the town,
the plant, the Woods, Skadowsky's streets and the fields between them.

KROT's box is the one number here that is known to be wrong: `sectors_v8.json` still carries the old
320 x 320 footprint against a site the owner says is massively expanded. As a *deny* area that error is
in the safe direction - it under-covers, so some of the new ground is unprotected - but it needs
re-measuring before anything else is anchored on it.

    incontrol_areas.py [--dry-run]
"""
import json
import sys
from pathlib import Path

AREAS = Path(r"G:/GSCraft/server/config/incontrol/areas.json")
Y0, Y1 = -64, 320                      # the whole world column

# name: (x0, x1, z0, z1, what it is)
BOXES = {
    # ---- builds: nothing hostile spawns inside these
    "camp":    (-978, -770, -1060, -845, "the camp in Skadowsky (sectors_v8)"),
    "krot":    (-3392, -3073, -1344, -1025, "KROT - WIP, extent known stale, see the docstring"),
    "mega":    (368, 751, -2128, -1601, "the mega-base (sectors_v8)"),
    "indu":    (336, 799, -1376, -1105, "the industrial district (sectors_v8)"),
    "lib":     (-2480, -2385, -3808, -3713, "the library (sectors_v8)"),
    "runway":  (-2064, -1553, -3792, -3601, "the runway pad (sectors_v8)"),
    "hub":     (-3568, -2385, -1008, 700, "Novo Expograd, the desert city - deferred"),
    "plaza":   (-2352, -2193, -1008, -865, "Financial Plaza and sewers - deferred"),
    "novo":    (-2352, -2209, -832, -673, "Novo Industrial Zone - deferred"),
    "biogen":  (-2352, -2289, -640, -529, "Bio Gen offices - deferred"),

    # ---- the base map: where enemies belong
    "town":    (-3750, -1800, -3750, -1400, "Pripyat, the ruin field (poi-coordinates §2)"),
    "woods":   (-2450, -1600, -1350, 100, "standing forest (poi-coordinates §2)"),
    "plant":   (-1150, 1200, -400, 700, "the power station complex (poi-coordinates §2)"),
    "skad":    (-1088, -625, -1488, -737, "the Skadowsky sector (sectors_v8); the camp inside is denied"),
    "farbank": (-1050, -600, -1000, -380, "the east-bank spine, derived in the design review §4c"),
    "farm":    (-2200, -2020, -990, -800, "the collective farm's fields, around the farmstead at -2112,-896"),
}

BUILDS = ("camp", "krot", "mega", "indu", "lib", "runway", "hub", "plaza", "novo", "biogen")


def main(argv):
    out = []
    for name, (x0, x1, z0, z1, why) in BOXES.items():
        out.append({
            "name": name,
            "dimension": "minecraft:overworld",
            "type": "box",
            "x": (x0 + x1) // 2, "y": (Y0 + Y1) // 2, "z": (z0 + z1) // 2,
            "dimx": (x1 - x0) // 2, "dimy": (Y1 - Y0) // 2, "dimz": (z1 - z0) // 2,
        })
        kind = "no-spawn" if name in BUILDS else "spawn   "
        print(f"  {kind} {name:8s} x {x0:6d}..{x1:<6d} z {z0:6d}..{z1:<6d}  {why}")
    print(f"{len(out)} areas, {len(BUILDS)} of them no-spawn")
    if "--dry-run" in argv:
        print("DRY RUN, nothing written")
        return 0
    AREAS.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    print(f"written to {AREAS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
