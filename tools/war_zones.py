"""Write the director's zone data for the GSCraft War mod: mod/src/main/resources/data/gscraft/gscraft_zones/map.json.

The boxes are the measured ones in incontrol_areas.py (imported, not re-typed, so they cannot drift apart); what this
adds is what the director does on each: who is placed on open ground, inside buildings and underground, how many may
stand near a player, how the Dead are dressed, which outposts keep a standing garrison, which zone keeps a unique
creature in its lair, and where each horror is admitted.

The creatures per place follow gscraft-entities-v8.md §3-§4 and gscraft-enemies.md §3, re-cut by the enemy review:
Runners among the Dead everywhere; Bloaters on the plant's Act III ground; the Matron in the hospital; Riders on the
fields and the east bank at night; the Drowned along the river and in the cooling water; cave spiders with the Dead in
the bunkers under the farmsteads and the Woods (the map's spawner blocks put zombies and cave spiders there too); the
Knocker in the hospital and the town's cellars; the Eyes in the dark beyond the camp and in the turbine hall; the fog
man in the Woods.

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

ENTITY = {
    "nato": "gscraft:nato_soldier", "ruaf": "gscraft:ruaf_soldier", "scav": "gscraft:scavenger",
    "dead": "minecraft:zombie", "drowned": "minecraft:drowned", "bloater": "gscraft:bloater",
    "spider": "minecraft:cave_spider", "rider": "gscraft:rider",
}
NIGHT_ONLY = {"rider"}
FOG, KNOCKER, EYES = "man:manfromthefog", "the_knocker:knocker", "eyesinthedarkness:eyes"


def pool(**weights):
    out = []
    for key, w in weights.items():
        if not w:
            continue
        entry = {"entity": ENTITY[key], "weight": w}
        if key in NIGHT_ONLY:
            entry["night"] = True
        out.append(entry)
    return out


def horror(entity, chance, *envs, night=True):
    h = {"entity": entity, "night": night, "chance": chance}
    if envs:
        h["envs"] = list(envs)
    return h


def army(side, count):
    return {"entity": ENTITY[side], "count": count, "refill_minutes": 10}


EYES_DARK = horror(EYES, 0.015, "open")
KNOCKER_CELLARS = horror(KNOCKER, 0.02, "indoor", "underground")

# name -> dict(cap, open, indoor, underground, dead, garrison, lair, horrors). Caps follow the retired area spawner's,
# which the owner judged on the ground; the kind of ground then scales them (Env: 0.75 open, 1.5 indoors and below).
PLACES = {
    # the outposts hold a standing garrison; Skadowsky's are smaller, because Skadowsky introduces the game
    "sk_out_w": dict(cap=5, open=pool(ruaf=5, dead=2), indoor=pool(ruaf=4, dead=2), garrison=army("ruaf", 3)),
    "sk_out_e": dict(cap=5, open=pool(nato=5, dead=2), indoor=pool(nato=4, dead=2), garrison=army("nato", 3)),
    "out_w1": dict(cap=5, open=pool(ruaf=5, dead=2), garrison=army("ruaf", 4)),
    "out_w2": dict(cap=5, open=pool(ruaf=5, dead=2), garrison=army("ruaf", 4)),
    "out_e1": dict(cap=5, open=pool(nato=5, dead=2), garrison=army("nato", 4)),
    "out_e2": dict(cap=5, open=pool(nato=5, dead=2), garrison=army("nato", 4)),
    # the fronts: each bank's patrols, the Dead between them, the Drowned in the river's shallows
    "front_wn": dict(cap=5, open=pool(ruaf=5, dead=2, drowned=2), underground=pool(dead=5, spider=1)),
    "front_ws": dict(cap=5, open=pool(ruaf=5, dead=2, drowned=2)),
    "front_en": dict(cap=5, open=pool(nato=5, dead=2, drowned=2)),
    "front_es": dict(cap=5, open=pool(nato=5, dead=2, drowned=2)),
    # Skadowsky, from the built-block density scan
    "sk_hosp": dict(cap=6, open=pool(dead=5), dead=["The Infected", "Runner"],
                    lair={"entity": "gscraft:matron", "count": 1, "refill_minutes": 120},
                    horrors=[horror(KNOCKER, 0.03, "indoor", "underground")]),
    "sk_town": dict(cap=7, open=pool(dead=5, scav=2), indoor=pool(dead=6, scav=1), dead=["Runner", "The Dead"],
                    horrors=[EYES_DARK]),
    "sk_south": dict(cap=7, open=pool(dead=5, scav=2), dead=["Yard Hand", "Runner", "The Dead"], horrors=[EYES_DARK]),
    # the plant, from its measured structures: Act III ground, so the Bloaters are here
    "pl_react": dict(cap=6, open=pool(dead=5, bloater=1), dead=["Containment Crew", "Plant Worker"]),
    "pl_turb": dict(cap=6, open=pool(dead=5, nato=2, bloater=1), indoor=pool(dead=6, bloater=1),
                    dead=["Plant Worker"], horrors=[horror(EYES, 0.02, "indoor")]),
    "pl_admin": dict(cap=6, open=pool(dead=5, bloater=1), dead=["Plant Worker"]),
    "pl_switch": dict(cap=6, open=pool(dead=5, nato=2, bloater=1), dead=["Plant Worker"]),
    "pl_intake": dict(cap=6, open=pool(drowned=5, dead=2), dead=["The Drowned"]),
    # the town: the Dead's floor under RUAF, the Knocker in the cellars
    "tw_stad": dict(cap=6, open=pool(dead=5, ruaf=1), underground=pool(dead=5, spider=1),
                    dead=["Peacekeeper", "Runner", "The Dead"], horrors=[KNOCKER_CELLARS]),
    "tw_centre": dict(cap=6, open=pool(dead=5, ruaf=2), indoor=pool(dead=6, ruaf=1), underground=pool(dead=5, spider=1),
                      dead=["Peacekeeper", "Runner", "The Dead"], horrors=[KNOCKER_CELLARS]),
    "tw_slabs": dict(cap=6, open=pool(dead=5, ruaf=2), indoor=pool(dead=6, ruaf=1), underground=pool(dead=5, spider=1),
                     dead=["Peacekeeper", "Runner", "The Dead"], horrors=[KNOCKER_CELLARS]),
    "tw_blocks": dict(cap=7, open=pool(dead=5, ruaf=2, scav=1), indoor=pool(dead=6, scav=1), underground=pool(dead=5, spider=1),
                      dead=["Peacekeeper", "Runner", "The Dead"], horrors=[KNOCKER_CELLARS]),
    "tw_bridge": dict(cap=6, open=pool(drowned=5), dead=["Drowned Patrol"]),
    # the big grounds
    "skad": dict(cap=7, open=pool(dead=5, scav=2), dead=["Runner", "The Dead"], horrors=[EYES_DARK]),
    "plant": dict(cap=7, open=pool(nato=5, dead=5, bloater=1), underground=pool(dead=4, spider=2),
                  dead=["Plant Worker", "The Dead"]),
    "town": dict(cap=8, open=pool(ruaf=5, dead=5, scav=1), indoor=pool(dead=6, ruaf=2), underground=pool(dead=5, spider=1),
                 dead=["Peacekeeper", "Runner", "The Dead"], horrors=[KNOCKER_CELLARS]),
    "woods": dict(cap=7, open=pool(scav=4, dead=5), underground=pool(spider=4, dead=3), dead=["Runner", "The Dead"],
                  horrors=[horror(FOG, 0.02, "open")]),
    "farm": dict(cap=7, open=pool(dead=5, scav=2, rider=1), dead=["Runner", "The Dead"]),
    "farbank": dict(cap=5, open=pool(nato=3, dead=3, drowned=2, rider=1), dead=["The Dead"]),
}
# patrol routes (feasibility C2): a squad leader idle in the zone walks the nearest one and loops; x/z only
PATROLS = {
    "front_wn": [[[-1200, -1230], [-1200, -960], [-1200, -720]]],
    "front_en": [[[-940, -720], [-940, -960], [-940, -1230]]],
    "town": [[[-2450, -3050], [-2300, -3050], [-2300, -2900], [-2450, -2900]]],
    "pl_switch": [[[-950, 50], [-720, 50], [-720, 170], [-950, 170]]],
}

# the rare armour patrol (armour design §3): the chance per director pass for a player in open ground here, and the
# group - NATO zones the Bradley and the M1A2, RUAF zones the BMP-2 and the T-90A; the open roads a thin mix of both
def armour(side, chance=0.06):
    apc, tank = ("superbwarfare:bmp_2", "superbwarfare:t_90a") if side == "ruaf" else ("superbwarfare:bradley", "superbwarfare:m_1a_2")
    return {"chance": chance, "compositions": [
        {"weight": 6, "vehicles": [apc], "infantry": 4},
        {"weight": 3, "vehicles": [tank], "infantry": 0},
        {"weight": 1, "vehicles": [tank, apc], "infantry": 4},
        {"weight": 1, "vehicles": [apc, apc], "infantry": 6}]}


ARMOUR = {
    "front_wn": armour("ruaf"), "front_ws": armour("ruaf"), "out_w1": armour("ruaf"), "out_w2": armour("ruaf"), "town": armour("ruaf", 0.04),
    "front_en": armour("nato"), "front_es": armour("nato"), "out_e1": armour("nato"), "out_e2": armour("nato"), "plant": armour("nato", 0.04),
    "farbank": armour("nato", 0.04),
}
OPEN_ARMOUR = {"chance": 0.03, "compositions": armour("ruaf")["compositions"][:2] + armour("nato")["compositions"][:2]}

ORDER = (list(BUILDS)
         + ["sk_out_w", "sk_out_e", "out_w1", "out_w2", "out_e1", "out_e2",
            "front_wn", "front_ws", "front_en", "front_es",
            "sk_hosp", "sk_town", "sk_south",
            "pl_react", "pl_turb", "pl_admin", "pl_switch", "pl_intake",
            "tw_stad", "tw_centre", "tw_slabs", "tw_blocks", "tw_bridge",
            "skad", "plant", "town", "farm", "woods", "farbank"])
# the open ground between everything: the roads, the fields, and the bunkers under the farmsteads
OPEN = {"name": "open", "cap": 4, "spawns": pool(dead=5, scav=2, rider=1),
        "underground_spawns": pool(spider=3, dead=4), "dead_ranks": ["Runner", "The Dead"]}


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
            p = PLACES[name]
            zone.update({"cap": p["cap"], "spawns": p["open"]})
            if name in PATROLS:
                zone["patrols"] = PATROLS[name]
            if name in ARMOUR:
                zone["armour"] = ARMOUR[name]
            for key, field in (("indoor", "indoor_spawns"), ("underground", "underground_spawns"),
                               ("dead", "dead_ranks"), ("garrison", "garrison"), ("lair", "lair"), ("horrors", "horrors")):
                if p.get(key):
                    zone[field] = p[key]
        zones.append(zone)
    zones.append(dict(OPEN, armour=OPEN_ARMOUR))
    count = lambda key: sum(1 for z in zones if key in z)  # noqa: E731
    print(f"{len(zones)} zones: {len(BUILDS)} excluded, {count('garrison')} garrisons, {count('lair')} lairs, "
          f"{count('indoor_spawns')} with indoor pools, {count('underground_spawns')} with underground pools, "
          f"{count('horrors')} with horrors")
    if "--dry-run" in argv:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"zones": zones}, indent=1) + "\n", encoding="utf-8", newline="")
    print(f"written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
