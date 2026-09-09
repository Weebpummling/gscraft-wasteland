"""E3: put the pack's real wardrobe into the infection ladder, so military kit is worth taking a site for.

`gscraft-enemy-design-2026-09-08.md` §3.4 makes infection resistance the reason to want military gear,
and §2.1 lists a full military wardrobe sitting unused while the ladder knows only leather, chainmail,
iron, gold, diamond and netherite. This writes the §2.1 items into
`config/hordes/data/hordes/infection/wearables_protection.json`.

Where each rung sits, and why:

  0.08  scavenger soft kit      rags. Below iron on purpose - E3 says military kit goes *above* iron,
                                and a bandana that beat a steel helmet would say the opposite
  0.12  insulated rubber        IE faraday. Sealed against one thing, not against spores
  0.15  military helmets/vests  level with diamond. The point of §3.4: the best ordinary protection in
                                the game, obtainable by taking a site rather than by mining
  0.20  copper backtank         a sealed air supply, worn on the chest
  0.25  copper diving helmet    a sealed head
  0.30  gas mask                the only true respirator in the pack, and so the single best item

A full sealed suit is mask + backtank = 0.50, which is the answer the design wants to exist and the one
thing that beats wearing an army's kit.

Every id was checked against the shipped jars before being written here; all 28 resolve.

    infection_ladder.py [--dry-run]
"""
import json
import sys
from pathlib import Path

LADDER = Path(r"G:/GSCraft/server/config/hordes/data/hordes/infection/wearables_protection.json")

SBW = "superbwarfare:"
DR = "dragonrise_reforge:"
PK = "pomkotsmechs:"
IE = "immersiveengineering:"

RUNGS = [
    (0.08, [PK + "wandererarmorhelmet", PK + "pomkotsarmorhelmet",
            PK + "wandererarmorchestplate", PK + "pomkotsarmorchestplate"]),
    (0.12, [IE + "armor_faraday_helmet", IE + "armor_faraday_chestplate"]),
    (0.15, [SBW + "us_helmet_pasgt", SBW + "us_chest_iotv",
            SBW + "ru_helmet_6b47", SBW + "ru_chest_6b43", SBW + "ge_helmet_m_35",
            DR + "fast_helmet", DR + "t21_helmet", DR + "kr06_helmet",
            DR + "sniper21_helmet", DR + "aljin_helmet", DR + "un_helmet",
            DR + "kr06_chest", DR + "msv_chest", DR + "med21_chest",
            DR + "cnjustchest", DR + "cnchest",
            DR + "desert07_chest", DR + "ocean07_chest", DR + "gorka3"]),
    (0.20, ["create:copper_backtank"]),
    (0.25, ["create:copper_diving_helmet"]),
    (0.30, ["createbigcannons:gas_mask"]),
]


def main(argv):
    dry = "--dry-run" in argv
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    known = {e["item"] for e in ladder}
    added = 0
    for protection, items in RUNGS:
        for item in items:
            if item in known:                      # idempotent: leave an existing rung alone
                continue
            ladder.append({"item": item, "protection": protection,
                           "operation": "add_multiplied_total"})
            known.add(item)
            added += 1
    print(f"{len(ladder) - added} rungs before, {added} added, {len(ladder)} now")
    for protection, items in RUNGS:
        print(f"   {protection:.2f}  {len(items):2d} items  {items[0].split(':')[0]}...")
    if dry:
        print("DRY RUN, nothing written")
        return 0
    LADDER.write_text(json.dumps(ladder, indent=1), encoding="utf-8", newline="")
    print(f"written to {LADDER}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
