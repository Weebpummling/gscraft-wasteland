#!/usr/bin/env python3
"""THE LOOT TABLES, as data (loot design 2026-09-19, docs/gscraft-loot-design-2026-09-19.md). One source of truth:

    python loot.py            -> writes every table under mod/src/main/resources/data/gscraft/loot_tables/
                                 (building/* x9, sites/* x5) and prints each table's pools
    python loot.py --doc      -> the same tables as markdown rows, for the design doc

An entry is (item, weight) or (item, weight, min, max). A site table rolls one of its BASE building tables whole and then
its signature pool - "a building type first and a site second" (the first loot doc's rule 2, kept). A `once` pool holds
the things a quest needs exactly one of: every chest of that table gives one of them (or, with `empty`, sometimes none).
Nothing here may name an item nothing uses: tools/itemflow.py --gate fails the build if one does.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mod/src/main/resources/data/gscraft/loot_tables"
G = "gscraft:"
SW = "superbwarfare:"
PISTOL = (SW + "handgun_ammo", 4, 10)
RIFLE = (SW + "rifle_ammo", 4, 10)
ONCE = [(SW + "mortar_barrel", 1), (SW + "mortar_bipod", 1), (SW + "mortar_base_plate", 1), (G + "welding_torch", 1)]

BUILDING = {
    "apartment": {"rolls": (2, 4), "pool": [(G + "bandage", 15, 1, 2), (G + "painkillers", 8), (G + "canned_goods", 20, 1, 3), (G + "bleach", 6), (G + "water_filter", 5),
                                            (G + "cloth", 8, 1, 2), (G + "light_bulb", 6), (G + "duct_tape", 5), (G + "gas_mask_filter", 3), (PISTOL[0], 8, 4, 10)]},
    "office": {"rolls": (2, 4), "pool": [(G + "wire_spool", 20, 1, 2), (G + "power_cord", 10), (G + "capacitor", 12, 1, 2), (G + "circuit_board", 10), (G + "relay", 8),
                                         (G + "computer_parts", 5), (G + "hard_drive", 6), (G + "folder_of_documents", 8), (G + "broken_radio", 4), (PISTOL[0], 8, 4, 10)]},
    "garage": {"rolls": (3, 5), "pool": [(G + "bolt", 15, 2, 4), (G + "nut", 15, 2, 4), (G + "screw", 10, 2, 4), (G + "metal_scrap", 20, 2, 4), (G + "duct_tape", 8),
                                         (G + "silicone_tube", 10), (G + "spark_plug", 8), (G + "motor_oil", 10), (G + "car_battery", 6), (G + "wrench", 2), (G + "hand_drill", 1),
                                         (G + "damaged_pistol", 2), (PISTOL[0], 6, 4, 10), (G + "solvent", 6), (SW + "mortar_shell", 4, 1, 2)],
               "once": ONCE, "once_empty": 4},
    "workshop": {"rolls": (4, 6), "pool": [(G + "metal_scrap", 20, 2, 4), (G + "nail", 15, 2, 4), (G + "screw", 15, 2, 4), (G + "insulating_tape", 8), (G + "pliers", 3),
                                           (G + "screwdriver_set", 3), (G + "pressure_gauge", 6), (G + "corrugated_hose", 8), (G + "bolt", 12, 2, 4), (G + "nut", 12, 2, 4),
                                           (G + "solvent", 4), (G + "silicone_tube", 5), (G + "spark_plug", 5), (G + "motor_oil", 5), (G + "car_battery", 4)],
                 "once": ONCE},
    "hospital": {"rolls": (2, 4), "pool": [(G + "bandage", 20, 1, 3), (G + "painkillers", 15), (G + "syringe", 12), (G + "antiseptic", 12), (G + "blood_bag", 4),
                                           (G + "gas_mask_filter", 4), (G + "damaged_pistol", 1)]},
    "store": {"rolls": (3, 5), "pool": [(G + "canned_goods", 25, 1, 3), (G + "bleach", 8), (G + "solvent", 8), (G + "water_filter", 8), (G + "bandage", 8, 1, 2),
                                        (G + "duct_tape", 8), (G + "cloth", 6, 1, 2), (G + "light_bulb", 5), (PISTOL[0], 6, 4, 10)]},
    "factory": {"rolls": (3, 5), "pool": [(G + "metal_scrap", 25, 2, 5), (G + "corrugated_hose", 8), (G + "pressure_gauge", 6), (G + "silicone_tube", 6),
                                          ("minecraft:gunpowder", 6, 1, 3), (G + "solvent", 6), (G + "motor_oil", 5), (G + "relay", 4), (RIFLE[0], 5, 4, 10), (G + "welding_torch", 1)]},
    "military": {"rolls": (2, 4), "pool": [(RIFLE[0], 12, 6, 14), (PISTOL[0], 8, 6, 12), ("minecraft:gunpowder", 8, 1, 3), (G + "damaged_pistol", 4), (G + "gas_mask_filter", 6),
                                           (G + "hard_drive", 3), (SW + "armor_plate", 4), (SW + "mortar_shell", 4, 1, 2), (SW + "medium_rocket_he", 3, 1, 2),
                                           (SW + "large_shell_he", 2, 1, 2), (G + "metal_scrap", 10, 2, 4)]},
    "library": {"rolls": (2, 3), "pool": [(G + "folder_of_documents", 15), (G + "hard_drive", 4), (G + "broken_radio", 6), (G + "capacitor", 8, 1, 2), (G + "computer_parts", 4),
                                          (G + "canned_goods", 4)]},
}

# the five strongpoints (ruling R1): bases are building tables, each rolled whole; the signature pool is the site's own
SITES = {
    "hospital": {"bases": [("hospital", 2), ("apartment", 1)], "sig_rolls": (1, 2),
                 "sig": [(G + "blood_bag", 12), (G + "syringe", 12), (G + "antiseptic", 10), (G + "painkillers", 8)]},
    "krot": {"bases": [("garage", 1), ("factory", 1)], "sig_rolls": (1, 2),
             "sig": [(G + "spark_plug", 15), (G + "motor_oil", 12), (G + "bolt", 10, 2, 4), (G + "nut", 10, 2, 4), (G + "car_battery", 4)]},
    "switchyard": {"bases": [("office", 1), ("military", 1)], "sig_rolls": (1, 2),
                   "sig": [(G + "circuit_board", 15), (G + "computer_parts", 12), (G + "hard_drive", 8), (G + "relay", 8)]},
    "turbine": {"bases": [("military", 1), ("office", 1)], "sig_rolls": (1, 2),
                "sig": [(G + "relay", 12), (G + "car_battery", 6), (G + "circuit_board", 8), (G + "capacitor", 8, 1, 2)]},
    "intake": {"bases": [("factory", 1), ("workshop", 1)], "sig_rolls": (1, 2),
               "sig": [(G + "corrugated_hose", 15), (G + "pressure_gauge", 10), (G + "water_filter", 8), (G + "solvent", 6)]},
}


def rolls(r):
    return r if isinstance(r, int) else {"min": r[0], "max": r[1]}


def entry(e):
    item, weight = e[0], e[1]
    out = {"type": "minecraft:item", "name": item, "weight": weight}
    if len(e) == 4 and (e[2], e[3]) != (1, 1):
        out["functions"] = [{"function": "minecraft:set_count", "count": {"min": e[2], "max": e[3]}}]
    return out


def building(name, d):
    pools = [{"rolls": rolls(d["rolls"]), "entries": [entry(e) for e in d["pool"]]}]
    if d.get("once"):
        entries = [entry(e) for e in d["once"]]
        if d.get("once_empty"):
            entries.append({"type": "minecraft:empty", "weight": d["once_empty"]})
        pools.append({"rolls": 1, "entries": entries})
    return {"type": "minecraft:chest", "pools": pools}


def site(name, d):
    return {"type": "minecraft:chest", "pools": [
        {"rolls": 1, "entries": [{"type": "minecraft:loot_table", "name": f"gscraft:building/{b}", "weight": w} for b, w in d["bases"]]},
        {"rolls": rolls(d["sig_rolls"]), "entries": [entry(e) for e in d["sig"]]}]}


def short(e):
    n = e[0].split(":")[1]
    return f"{n} {e[1]}" + (f" (x{e[2]}-{e[3]})" if len(e) == 4 and (e[2], e[3]) != (1, 1) else "")


def main(argv):
    doc = "--doc" in argv
    for name, d in BUILDING.items():
        if not doc:
            p = OUT / "building" / f"{name}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(building(name, d), indent=1) + "\n", encoding="utf-8")
        once = ("; **one of** " + ", ".join(e[0].split(":")[1] for e in d["once"]) + (f" (or nothing, {d['once_empty']} in {d['once_empty'] + len(d['once'])})" if d.get("once_empty") else "")) if d.get("once") else ""
        print(f"| `building/{name}` | {d['rolls'][0]}-{d['rolls'][1]} | " + ", ".join(short(e) for e in d["pool"]) + once + " |")
    for name, d in SITES.items():
        if not doc:
            p = OUT / "sites" / f"{name}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(site(name, d), indent=1) + "\n", encoding="utf-8")
        print(f"| `sites/{name}` | one of " + ", ".join(f"{b} ({w})" for b, w in d["bases"]) + f", whole | + {d['sig_rolls'][0]}-{d['sig_rolls'][1]} of: " + ", ".join(short(e) for e in d["sig"]) + " |")
    if not doc:
        print(f"{len(BUILDING)} building tables and {len(SITES)} site tables written under {OUT}")


if __name__ == "__main__":
    main(sys.argv)
