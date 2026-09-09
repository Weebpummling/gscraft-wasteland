"""The Militia's ground, and the Rifleman rank (F1, ruled 2026-09-09).

Where they stand is not invented - the design says it in three places and this only turns it into boxes:

  enemies §3.3      "The Militia never spawns ambient outside the east-bank spine - the rail yard and
                     the road south to the plant's outer works - and the plant complex's gates and
                     inside. They are a *place*, not a weather."
  entities-v8 §164  farbank: "the east-bank spine: the rail line and yard, and the road south to the
                     plant's outer works", Troopers 3 and Shields 1, a patrol between the yard and the
                     plant's outer works.
  objectives §111   the rail yard is "in the Skadowsky sector, on the rail corridor east of the camp".

So the spine runs from the rail yard, which is inside Skadowsky east of the camp, south down the bank to
the plant. Two bounds fix it: the camp ends at x -770 (sectors_v8), and skadowsky_river runs south
through x -1080 at z -800 and x -1200 at z -200 (rivers_v8), so staying east of x -1050 keeps the box on
the east bank. The plant's own area already exists and starts at z -400.

  farbank   x -1050..-600, z -1000..-380
  camp      x -978..-770, z -1060..-845   (sectors_v8, defined only so the Militia can be kept out of it)

The camp sits inside the farbank box and In Control areas are boxes with no subtraction, so the camp deny
is written first and first match wins.

The Rifleman is `minecraft:pillager` dressed at finalize inside those two areas. A pillager is also the
Scavengers' base entity, but the factions hold different ground - the Scavengers have the roads and the
Woods - so a pillager on the spine or in the plant is a Militia rifleman and one anywhere else is not.

Key names, checked against the jar rather than assumed:
  - `helditem` is right, and §3.1 was right to say so. RuleBase registers both ACTION_HELDITEM and
    ACTION_SETHELDITEM, but SpawnRule accepts only the first - `sethelditem` is reported as an invalid
    keyword for spawn.json. (An earlier note here claimed the opposite; it was wrong.)
  - the NBT action's JSON key is `nbt`, though its field is named ACTION_MOBNBT. `mobnbt` is rejected.
  - a TACZ gun is the item `tacz:modern_kinetic_gun` carrying `GunId` NBT. `tacz:type_81` is a gun
    definition, not an item.

The rules are inserted *after* the unconditional hostile deny that currently holds hostiles off, so they
change nothing until that hold is lifted, and sit ahead of the other faction rules when it is.

    militia_rules.py [--dry-run]
"""
import json
import sys
from pathlib import Path

IC = Path(r"G:/GSCraft/server/config/incontrol")
IE = "immersiveengineering:"
MILITIA = [IE + "commando", IE + "fusilier", IE + "bulwark"]
RIFLE = "tacz:type_81"          # the design's first choice; tacz:ak47 is the alternate

# Area.class reads flat x/y/z plus dimx/dimy/dimz. A `center` object parses as JSON and then fails at
# bind time with "Area '<name>' has no x!", which is easy to miss because it is not a parse error.
AREAS = [
    {"name": "farbank", "dimension": "minecraft:overworld", "type": "box",
     "x": -825, "y": 128, "z": -690, "dimx": 450, "dimy": 384, "dimz": 620},
    {"name": "camp", "dimension": "minecraft:overworld", "type": "box",
     "x": -874, "y": 128, "z": -952, "dimx": 208, "dimy": 384, "dimz": 215},
]


def rifleman(area):
    """A pillager dressed as the Militia's line infantry, with a real rifle."""
    return {
        "dimension": "minecraft:overworld", "when": "finalize", "area": area,
        "mob": ["minecraft:pillager"], "result": "allow",
        "armorhelmet": {"item": "superbwarfare:us_helmet_pasgt"},
        "armorchest": {"item": "superbwarfare:us_chest_iotv"},
        # the nbt here is a JSON object, not an SNBT string - a string is reported as
        # "Error parsing json '"{GunId:\"tacz:type_81\"}"'"
        "helditem": {"item": "tacz:modern_kinetic_gun", "nbt": {"GunId": RIFLE}},
        "customname": "Militia Rifleman",
        # nothing an enemy carries ever drops (E7a); the rifle above is the reason this matters
        "nbt": "{ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f]}",
    }


def main(argv):
    dry = "--dry-run" in argv

    areas = json.loads((IC / "areas.json").read_text(encoding="utf-8"))
    have = {a["name"] for a in areas}
    for a in AREAS:
        if a["name"] not in have:
            areas.append(a)
    print(f"areas: {[a['name'] for a in areas]}")

    spawn = json.loads((IC / "spawn.json").read_text(encoding="utf-8"))
    spawn = [r for r in spawn if "Militia" not in json.dumps(r) and
             not (r.get("mob") == MILITIA)]                      # idempotent

    new = [
        # never in the player's camp, whatever the box below says
        {"dimension": "minecraft:overworld", "when": "onjoin", "area": "camp",
         "mob": MILITIA + ["minecraft:pillager"], "result": "deny"},
        {"dimension": "minecraft:overworld", "when": "onjoin", "area": "farbank",
         "mob": MILITIA, "result": "default",
         "maxcount": {"amount": 6, "mob": MILITIA, "perplayer": False}},
        {"dimension": "minecraft:overworld", "when": "onjoin", "area": "plant",
         "mob": MILITIA, "result": "default",
         "maxcount": {"amount": 8, "mob": MILITIA, "perplayer": False}},
        # a place, not a weather
        {"dimension": "minecraft:overworld", "when": "onjoin", "mob": MILITIA, "result": "deny"},
        rifleman("farbank"),
        rifleman("plant"),
    ]

    # after the unconditional hostile deny that holds hostiles off, ahead of the other faction rules
    at = next((i for i, r in enumerate(spawn)
               if r.get("hostile") and r.get("result") == "deny" and "mob" not in r), len(spawn)) + 1
    spawn[at:at] = new
    print(f"spawn.json: {len(new)} rules inserted at index {at}, {len(spawn)} total")
    for r in new:
        print(f"   {r.get('when'):8s} {r.get('area','(anywhere)'):8s} {r['result']:8s} "
              f"{'dressed' if 'helditem' in r else ''}")

    if dry:
        print("DRY RUN, nothing written")
        return 0
    (IC / "areas.json").write_text(json.dumps(areas, indent=1), encoding="utf-8", newline="")
    (IC / "spawn.json").write_text(json.dumps(spawn, indent=1), encoding="utf-8", newline="")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
