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

    # ---- the base map: where enemies belong. The broad areas first, then the sub-zones inside them,
    # because a spawn pass that puts the Dead "in the buildings" needs to know which ground is buildings.
    "town":    (-3750, -1800, -3750, -1400, "Pripyat, the ruin field (poi-coordinates §2)"),
    "woods":   (-2450, -1600, -1350, 100, "standing forest (poi-coordinates §2)"),
    "plant":   (-1150, 1200, -400, 700, "the power station complex (poi-coordinates §2)"),
    "skad":    (-1088, -625, -1488, -737, "the Skadowsky sector (sectors_v8); the camp inside is denied"),
    # Deliberately overlaps Skadowsky's southern third. The design puts the spine's head at the rail
    # yard, which is inside the sector (objectives §111, entities-v8 §164), and the owner's ruling is
    # that a varied starting zone is wanted - so the Militia reach the yard rather than stopping at the
    # sector line.
    "farbank": (-1050, -600, -1000, -380, "the east-bank spine, from the rail yard south"),
    "farm":    (-2200, -2020, -990, -800, "the collective farm's fields, around the farmstead"),

    # Skadowsky, from a built-block density scan of the sector (2026-09-09): three clusters, north to
    # south, with the camp sitting inside the southern one and denied separately.
    "sk_hosp":  (-960, -690, -1344, -1240, "the hospital cluster; design gives x -865..-698, z -1312..-1242"),
    "sk_town":  (-980, -660, -1240, -1000, "the central streets between the hospital and the camp"),
    "sk_south": (-980, -660, -1000, -760, "the southern cluster: the station, the yard and the rail"),

    # the power station, boxes from the measured centres and sizes in poi-coordinates §3
    "pl_react": (-743, -541, 337, 699, "the confinement hall over the reactor, 202 x 362"),
    "pl_turb":  (-13, 824, 546, 634, "the turbine hall, 837 x 88"),
    "pl_admin": (-199, 375, 36, 372, "administration and workshop block, 574 x 336"),
    "pl_switch": (-957, -708, 37, 184, "the four low halls: switchyard and storage bays"),
    "pl_intake": (606, 1180, -101, 413, "cooling-water intake works, 573 x 514"),

    # the town, likewise
    "tw_stad":  (-2503, -2287, -3584, -3381, "the stadium, running track and grandstand"),
    "tw_centre": (-2540, -2220, -3105, -2845, "the park, the radiating avenues and the roundabout"),
    "tw_slabs": (-3650, -2900, -3255, -2710, "the long slab blocks of the west and north-west quarters"),
    "tw_blocks": (-2400, -1890, -2350, -1730, "the microdistrict and courtyard blocks, south-east"),
    "tw_bridge": (-926, -882, -2353, -2051, "the rail bridge over the water, south approach"),

    # ---- the front. skadowsky_river runs from (-740,-1720) south to (-1350,700), so it bisects the
    # cell: the town, the Woods, the farm and KROT are west of it; Skadowsky and the plant are east.
    # The river is diagonal and an area is a box, so each bank takes two boxes rather than one, north
    # and south, each kept clear of the water itself.
    "front_wn": (-1290, -1100, -1250, -700, "west bank, north reach - the river runs x -1080 here"),
    "front_ws": (-1380, -1210, -700, -200, "west bank, south reach - the river bends out to x -1200"),
    # starts east of sk_out_w (which ends at -1000): the Column's bridgehead is on this bank, and the
    # Militia rules are evaluated first, so an overlap here would fly the wrong flag over the crossing.
    "front_en": (-995, -880, -1250, -700, "east bank, north reach"),
    "front_es": (-1060, -900, -700, -200, "east bank, south reach"),

    # ---- outposts, pushed out from each heartland toward the middle
    "out_w1": (-1560, -1440, -1120, -1000, "western outpost, north: east of the Woods toward the river"),
    "out_w2": (-1500, -1380, -600, -480, "western outpost, south: the open ground above the farm road"),
    "out_e1": (-900, -780, -600, -480, "eastern outpost, south: between the river and the plant's west gate"),
    "out_e2": (-700, -580, -1150, -1030, "eastern outpost, north: the ground above the rail corridor"),

    # ---- the two outposts at Skadowsky, which is where the player meets both armies. The south-west
    # bridge (x -1104..-981, deck z -957..-936) is the only crossing on this side, so the western army
    # holds a bridgehead on the near bank and the eastern army sits on the rail yard opposite it.
    # Widened 2026-09-09: at 70 x 80 and 100 x 100 a player had to stand inside the box to meet either
    # garrison, so Skadowsky read as empty of both armies. Still clear of the camp and of each other.
    "sk_out_w": (-784, -720, -1148, -1100, "RUAF's post inside Skadowsky: the brick and stone block between the camp and the hospital (owner, 2026-09-10); was the bridgehead at the river's edge"),
    "sk_out_e": (-768, -640, -1000, -820, "the rail yard outpost, east of the camp"),
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
    if "--retired-ok" not in __import__("sys").argv:
        raise SystemExit("RETIRED 2026-09-09: the enemy system lives in mod/ (GSCraft War). This tool rewrites the "
                         "local server's In Control / KubeJS spawn files. Pass --retired-ok to run it anyway.")
    sys.exit(main(sys.argv))
