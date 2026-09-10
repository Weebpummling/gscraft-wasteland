"""Write the director's zone data for the GSCraft War mod: mod/src/main/resources/data/gscraft/gscraft_zones/map.json.

The boxes are the measured ones in incontrol_areas.py (imported, not re-typed, so they cannot drift apart); what this
adds is what the director does on each: who is placed, how many may stand near a player, how the Dead are dressed,
which outposts keep a standing garrison and where each horror is admitted.

Order is the rule, because the first zone containing a point wins: builds first (nothing, ever), then the small
places (outposts, fronts, the sub-zones of Skadowsky, the plant and the town), then the big grounds, then the open
ground, which has no box and catches everything else.

    war_zones.py [--dry-run]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from incontrol_areas import BOXES, BUILDS  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "mod/src/main/resources/data/gscraft/gscraft_zones/map.json"

NATO, RUAF, SCAV = "gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger"
ZOMBIE, DROWNED = "minecraft:zombie", "minecraft:drowned"
FOG, KNOCKER, EYES = "man:manfromthefog", "the_knocker:knocker", "eyesinthedarkness:eyes"


def spawns(**weights):
    names = {"nato": NATO, "ruaf": RUAF, "scav": SCAV, "dead": ZOMBIE, "drowned": DROWNED}
    return [{"entity": names[k], "weight": w} for k, w in weights.items() if w]


# name -> (cap, spawns, dead ranks, garrison, horrors). Caps follow the retired area spawner's, which the owner
# judged on the ground (2026-09-09: "the density is way too high" before they were halved).
PLACES = {
    # the outposts hold a standing garrison; Skadowsky's are smaller, because Skadowsky introduces the game
    "sk_out_w": (5, spawns(ruaf=5, dead=2), [], {"entity": RUAF, "count": 3, "refill_minutes": 10}, []),
    "sk_out_e": (5, spawns(nato=5, dead=2), [], {"entity": NATO, "count": 3, "refill_minutes": 10}, []),
    "out_w1": (5, spawns(ruaf=5, dead=2), [], {"entity": RUAF, "count": 4, "refill_minutes": 10}, []),
    "out_w2": (5, spawns(ruaf=5, dead=2), [], {"entity": RUAF, "count": 4, "refill_minutes": 10}, []),
    "out_e1": (5, spawns(nato=5, dead=2), [], {"entity": NATO, "count": 4, "refill_minutes": 10}, []),
    "out_e2": (5, spawns(nato=5, dead=2), [], {"entity": NATO, "count": 4, "refill_minutes": 10}, []),
    # the fronts: patrols of each bank, the Dead between them
    "front_wn": (5, spawns(ruaf=5, dead=2), [], None, []),
    "front_ws": (5, spawns(ruaf=5, dead=2), [], None, []),
    "front_en": (5, spawns(nato=5, dead=2), [], None, []),
    "front_es": (5, spawns(nato=5, dead=2), [], None, []),
    # Skadowsky, from the built-block density scan
    "sk_hosp": (6, spawns(dead=5), ["The Infected"], None, [{"entity": KNOCKER, "night": True, "chance": 0.03}]),
    "sk_town": (7, spawns(dead=5, scav=2), ["The Dead"], None, []),
    "sk_south": (7, spawns(dead=5, scav=2), ["Yard Hand", "The Dead"], None, []),
    # the plant, from its measured structures
    "pl_react": (6, spawns(dead=5), ["Containment Crew", "Plant Worker"], None, []),
    "pl_turb": (6, spawns(dead=5, nato=2), ["Plant Worker"], None, [{"entity": EYES, "night": True, "chance": 0.02}]),
    "pl_admin": (6, spawns(dead=5), ["Plant Worker"], None, []),
    "pl_switch": (6, spawns(dead=5, nato=2), ["Plant Worker"], None, []),
    "pl_intake": (6, spawns(drowned=5, dead=2), ["The Drowned"], None, []),
    # the town
    "tw_stad": (6, spawns(dead=5, ruaf=1), ["Peacekeeper", "The Dead"], None, []),
    "tw_centre": (6, spawns(dead=5, ruaf=2), ["Peacekeeper", "The Dead"], None, []),
    "tw_slabs": (6, spawns(dead=5, ruaf=2), ["Peacekeeper", "The Dead"], None, []),
    "tw_blocks": (7, spawns(dead=5, ruaf=2, scav=1), ["Peacekeeper", "The Dead"], None, []),
    "tw_bridge": (6, spawns(drowned=5), ["Drowned Patrol"], None, []),
    # the big grounds
    "skad": (7, spawns(dead=5, scav=2), ["The Dead"], None, []),
    "plant": (7, spawns(nato=5, dead=5), ["Plant Worker", "The Dead"], None, []),
    "town": (8, spawns(ruaf=5, dead=5, scav=1), ["Peacekeeper", "The Dead"], None, []),
    "woods": (7, spawns(scav=4, dead=5), ["The Dead"], None, [{"entity": FOG, "night": True, "chance": 0.02}]),
    "farm": (7, spawns(dead=5, scav=2), ["The Dead"], None, []),
    "farbank": (5, spawns(nato=3, dead=3), ["The Dead"], None, []),
}
ORDER = (list(BUILDS)
         + ["sk_out_w", "sk_out_e", "out_w1", "out_w2", "out_e1", "out_e2",
            "front_wn", "front_ws", "front_en", "front_es",
            "sk_hosp", "sk_town", "sk_south",
            "pl_react", "pl_turb", "pl_admin", "pl_switch", "pl_intake",
            "tw_stad", "tw_centre", "tw_slabs", "tw_blocks", "tw_bridge",
            "skad", "plant", "town", "woods", "farm", "farbank"])
OPEN = {"name": "open", "cap": 4, "spawns": spawns(dead=5, scav=2), "dead_ranks": ["The Dead"]}


def main(argv):
    missing = [n for n in ORDER if n not in BOXES]
    unplaced = [n for n in BOXES if n not in ORDER]
    if missing or unplaced:
        raise SystemExit(f"zones out of step with incontrol_areas.BOXES: missing {missing}, unplaced {unplaced}")
    zones = []
    for name in ORDER:
        x0, x1, z0, z1, why = BOXES[name]
        zone = {"name": name, "box": [x0, x1, z0, z1], "note": why}
        if name in BUILDS:
            zone["exclude"] = True
        else:
            cap, sp, dead, garrison, horrors = PLACES[name]
            zone.update({"cap": cap, "spawns": sp})
            if dead:
                zone["dead_ranks"] = dead
            if garrison:
                zone["garrison"] = garrison
            if horrors:
                zone["horrors"] = horrors
        zones.append(zone)
    zones.append(OPEN)
    print(f"{len(zones)} zones: {len(BUILDS)} excluded, {sum(1 for z in zones if 'garrison' in z)} garrisons, "
          f"{sum(1 for z in zones if 'horrors' in z)} with horrors")
    if "--dry-run" in argv:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"zones": zones}, indent=1) + "\n", encoding="utf-8", newline="")
    print(f"written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
