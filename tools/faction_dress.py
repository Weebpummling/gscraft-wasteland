"""Dress the factions, and stop Improved Mobs contesting the slots (E7b, §3.1, §3.2).

Order is the whole design here. In Control takes the first matching rule, so:

    1  camp                      nothing hostile is dressed or spawned in the player's camp
    2-4 Militia gating           the three IE ids in farbank and plant, denied everywhere else
    5-6 Militia Rifleman         a pillager in farbank or plant is dressed as line infantry
    7  Scavenger                 any *other* pillager is dressed as a wastelander

so a pillager on the spine or in the plant is a soldier and one anywhere else is a scavenger, which is
what §3.2 means by "the Militia matches, the Scavengers do not" - the contrast is the design, and it is
readable at fifty metres for the price of equipment fields.

Everything runs at `onjoin`, not `finalize`: `finalize` never fires for a `/summon` or for a mob a horde
wave adds, and the design places most of its enemies that way.

E7b then keeps Improved Mobs off the same slots. Measured before it was applied: a correctly dressed
Rifleman was still handed a diamond pickaxe in the offhand. The entry form is
`id|REVERSE|ARMOR|HELDITEMS` - the flag list after an id is the set *not* applied, so without REVERSE the
entry means "everything except armour and held items", which leaves exactly the contest it is meant to
stop. The angle brackets in the config's own examples are documentation delimiters, not part of the
value: the file says "Examples (without <>)", and writing them makes the mod's config load throw during
ConfigTracker.loadConfigs, which fails the whole server boot with no message naming the file.

Note the reach of that: Improved Mobs is configured per entity type, In Control per rule and area, so
"pillagers in farbank only" cannot be expressed there. Exempting `minecraft:pillager` exempts every
pillager - which is why the Scavenger rule below exists. Without it, exempted pillagers would be bare.

    faction_dress.py [--dry-run]
"""
import json
import sys
from pathlib import Path

IC = Path(r"G:/GSCraft/server/config/incontrol")
IM = Path(r"G:/GSCraft/server/config/improvedmobs/common.toml")

PK = "pomkotsmechs:"
SBW = "superbwarfare:"
IE = "immersiveengineering:"
MILITIA = [IE + "commando", IE + "fusilier", IE + "bulwark"]

# nothing an enemy carries ever drops (E7a)
NO_DROPS = "{ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f]}"

SCAVENGER = {
    "dimension": "minecraft:overworld", "when": "onjoin",
    "mob": ["minecraft:pillager"], "result": "allow",
    # the pack's only non-military soft kit: a face wrap and a jacket. A wastelander, not a soldier.
    "armorhelmet": {"item": PK + "wandererarmorhelmet"},
    "armorchest": {"item": PK + "wandererarmorchestplate"},
    "helditem": {"item": SBW + "steel_pipe"},
    "customname": "Scavenger",
    "nbt": NO_DROPS,
}

# these are the ids In Control now dresses; Improved Mobs must not touch their gear
EXEMPT = ["minecraft:pillager"] + MILITIA


def main(argv):
    dry = "--dry-run" in argv

    # ---- the Scavenger rule, after the Militia rules so the areas win
    spawn = json.loads((IC / "spawn.json").read_text(encoding="utf-8"))
    spawn = [r for r in spawn if r.get("customname") != "Scavenger"]
    last = max((i for i, r in enumerate(spawn) if r.get("customname") == "Militia Rifleman"),
               default=-1)
    spawn.insert(last + 1, SCAVENGER)
    print(f"spawn.json: Scavenger rule at index {last + 1}, {len(spawn)} rules")

    # ---- E7b
    toml = IM.read_text(encoding="utf-8")
    line = next(l for l in toml.splitlines() if l.strip().startswith('"Entity Configs"'))
    current = json.loads(line.split("=", 1)[1].strip())
    added = [f"{i}|REVERSE|ARMOR|HELDITEMS" for i in EXEMPT
             if not any(i in c and "REVERSE" in c for c in current)]
    if added:
        merged = current + added
        new_line = '\t"Entity Configs" = ' + json.dumps(merged)
        toml = toml.replace(line, new_line, 1)
    print(f"improvedmobs: {len(added)} exemptions added -> {added}")

    if dry:
        print("DRY RUN, nothing written")
        return 0
    (IC / "spawn.json").write_text(json.dumps(spawn, indent=1), encoding="utf-8", newline="")
    if added:
        IM.write_text(toml, encoding="utf-8", newline="")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
