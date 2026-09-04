"""World build v7: the structure override datapack and the kept-structure placement function.

usage: structure_override.py            -> build/datapacks/gscraft_worldgen/** and
                                            build/datapacks/gscraft/data/gscraft/functions/place_kept_structures.mcfunction

Reads buildmap/structure_plan_v7.json. For every structure set whose structures are pruned (design:
docs/gscraft-structure-plan.md), writes an override with the same `structures` list and a placement of
type random_spread with frequency 0.0, so the set never places anywhere; world generation is otherwise
untouched (same seed, same terrain, same Lost Cities). Sets covered: Apotheosis towers (4), Man From The
Fog house, Underground Bunkers, and the vanilla sets villages (which Lukis Grand Capitals overrides -
the world datapack outranks both), pillager_outposts, ancient_cities, trail_ruins, igloos, desert_pyramids,
jungle_temples, ocean_monuments, woodland_mansions, strongholds. Background sets (mineshafts, shipwrecks,
ocean ruins, ruined portals, buried treasure, swamp huts) are left alone, as the plan says.

The placement function puts the 67 kept sites back with `place structure <id> <x> <y> <z>` at their census
coordinates; jigsaw structures project themselves to the surface, bunkers and ancient cities choose their
own depth, so y is a nominal 64. Run it once on the regenerated world (localconsole.py), then check the
sites on the flight.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "buildmap" / "structure_plan_v7.json"
DP = ROOT / "build" / "datapacks" / "gscraft_worldgen"
FUNC = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft" / "functions" / "place_kept_structures.mcfunction"

# namespace -> set name -> structures list (as shipped), copied so the override keeps the same entries
SETS = {
    "apotheosis": {
        "tower_main": ["apotheosis:tower_main"], "tower_leaf": ["apotheosis:tower_leaf"],
        "tower_sand": ["apotheosis:tower_sand"], "tower_spruce": ["apotheosis:tower_spruce"],
    },
    "man": {"house": ["man:house"]},
    "underground_bunkers": {"minor_structures": ["underground_bunkers:underground_bunker"]},
    "minecraft": {
        "villages": ["minecraft:village_plains", "minecraft:village_desert", "minecraft:village_taiga",
                     "minecraft:village_savanna", "minecraft:village_snowy"],
        "pillager_outposts": ["minecraft:pillager_outpost"],
        "ancient_cities": ["minecraft:ancient_city"],
        "trail_ruins": ["minecraft:trail_ruins"],
        "igloos": ["minecraft:igloo"],
        "desert_pyramids": ["minecraft:desert_pyramid"],
        "jungle_temples": ["minecraft:jungle_pyramid"],
        "ocean_monuments": ["minecraft:monument"],
        "woodland_mansions": ["minecraft:mansion"],
        "strongholds": ["minecraft:stronghold"],
    },
}
APOTHEOSIS_CONDITION = [{"type": "apotheosis:module", "module": "adventure"}]


def write_datapack():
    (DP / "data").mkdir(parents=True, exist_ok=True)
    (DP / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15,
        "description": "GSCraft v7: pruned structure sets never place (frequency 0); kept sites are placed by function"}}, indent=1))
    n = 0
    for ns, sets in SETS.items():
        d = DP / "data" / ns / "worldgen" / "structure_set"; d.mkdir(parents=True, exist_ok=True)
        for name, structs in sets.items():
            body = {"structures": [{"structure": s, "weight": 1} for s in structs],
                    "placement": {"type": "minecraft:random_spread", "spacing": 100, "separation": 50, "salt": 20260904, "frequency": 0.0}}
            if ns == "apotheosis": body = {"forge:conditions": APOTHEOSIS_CONDITION, **body}
            (d / f"{name}.json").write_text(json.dumps(body, indent=1)); n += 1
    return n


FORCE = FUNC.with_name("forceload_kept_structures.mcfunction")
UNFORCE = FUNC.with_name("unforceload_kept_structures.mcfunction")


def write_function(plan):
    """place_kept_structures needs its chunks LOADED (the command refuses unloaded ones, and a function
    counts refused commands as executed), so three functions: force-load the 3x3 chunks around every
    site, place (after the chunks have loaded - give it a minute), then release the force-loads."""
    place = ["# GSCraft v7: the 67 kept generated sites, at their census coordinates (structure_plan_v7.json)",
             "# run gscraft:forceload_kept_structures first and wait ~60 s for the chunks to load"]
    force = ["# GSCraft v7: force-load a 3x3 chunk area around every kept site so place_kept_structures can run"]
    for typ, entries in plan["keep"].items():
        for e in entries:
            place.append(f"place structure {e['id']} {e['x']} 64 {e['z']}")
            force.append(f"forceload add {e['x'] - 16} {e['z'] - 16} {e['x'] + 16} {e['z'] + 16}")
    FUNC.parent.mkdir(parents=True, exist_ok=True)
    FUNC.write_text("\n".join(place) + "\n")
    FORCE.write_text("\n".join(force) + "\n")
    UNFORCE.write_text("# GSCraft v7: release the force-loads after place_kept_structures\nforceload remove all\n")
    return len(place) - 2


def main():
    plan = json.load(open(PLAN))
    n = write_datapack(); k = write_function(plan)
    print(f"override datapack: {n} structure sets at frequency 0 -> {DP}")
    print(f"placement function: {k} kept sites -> {FUNC}")


if __name__ == "__main__":
    main()
