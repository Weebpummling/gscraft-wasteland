"""Phase 2 step 7: one site's wave table, and the rule that selects it, as the proof of the mechanism.

Three things are being proven at once, because they have to work together and there is no point writing
nine more tables against a shape that does not:

  1. the table format itself loads (E9)
  2. a table can be pinned to a site - hordes:comparison over hordes:player_pos, which is the geofence
     In Control spawner rules turned out not to have
  3. a rank can be dressed through nbt, and its gear kept from dropping, in the table rather than in a
     script - which is D4's fix path for wave mobs

The content is deliberately thin. This is the mechanism proof; the real roster is entities-v8 section 5.

Skadowsky is the site because it is the starting zone and one of the three the routing rule still points
quests at. Its box is x -1088..-625, z -1488..-737 from sectors_v8.json.
"""
import json
from pathlib import Path

H = Path(r"G:/GSCraft/server/config/hordes/data/hordes/horde_data")
SKAD = dict(x0=-1088, x1=-625, z0=-1488, z1=-737)

# --- the table. Object form throughout so the nbt is visible and the shorthand's "-" delimiter trap
# (no negative numbers, no hyphen in an id) never applies.
dressed = ("{ArmorItems:[{},{},{id:iron_chestplate,Count:1b},{id:iron_helmet,Count:1b}],"
           "ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f],"
           "HandItems:[{id:iron_sword,Count:1b},{}],"
           "CustomName:'{\"text\":\"Scavenger\"}'}")
table = [
    {"entity": "minecraft:zombie", "weight": 20, "first_day": 0, "last_day": 0},
    {"entity": "minecraft:zombie", "weight": 10, "first_day": 0, "last_day": 0, "nbt": dressed},
    {"entity": "minecraft:husk", "weight": 5, "first_day": 0, "last_day": 0},
]
out = H / "tables" / "gscraft_skad.json"
out.write_text(json.dumps(table, indent=1), encoding="utf-8", newline="")
print(f"wrote {out.name}: {len(table)} entries, one of them dressed with drops suppressed")


def pos(axis):
    # PosGetter's axis field is "value" (a string ValueGetter), not "axis" - "axis" is only a local
    # name inside get(). Using it produced "Incorrect parameters for condition hordes:comparison".
    return {"type": "hordes:player_pos", "value": axis}


def cmp_(axis, op, v):
    # operation is atlas's ComparableOperation: EQUALS, NOT_EQUALS, GREATER_THAN, GREATER_OR_EQUAL,
    # LESS_THAN, LESS_OR_EQUAL
    # ComparisonCondition.deserialize reads four keys: type, operation, value1, value2. "type" is the
    # atlas DataType (byte/short/int/long/float/double/string/boolean, lowercase) and omitting it is
    # what "Incorrect parameters for condition hordes:comparison" means. A player position is a double.
    return {"name": "hordes:comparison",
            "value": {"type": "double", "operation": op,
                      "value1": pos(axis), "value2": float(v)}}


# --- the selection rule: inside Skadowsky's box, use the site's table
script = H / "scripts" / "default.json"
rules = json.loads(script.read_text(encoding="utf-8"))
rules = [r for r in rules if "gscraft_skad" not in json.dumps(r)]      # idempotent
rules.append({
    "function": "hordes:set_spawntable",
    "value": ["hordes:gscraft_skad"],
    "conditions": [cmp_("x", "GREATER_OR_EQUAL", SKAD["x0"]), cmp_("x", "LESS_OR_EQUAL", SKAD["x1"]),
                   cmp_("z", "GREATER_OR_EQUAL", SKAD["z0"]), cmp_("z", "LESS_OR_EQUAL", SKAD["z1"])],
})
script.write_text(json.dumps(rules, indent=1), encoding="utf-8", newline="")
print(f"default.json: {len(rules)} rules, the last one pins Skadowsky to its table")
