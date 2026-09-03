"""Post-transplant cleanup: spawners pointing at mobs from cut mods become zombie spawners;
entity records from cut mods are dropped. Rewrites only region/entity files that changed.

usage: fixspawners.py <world dir> [--dry-run]
"""
import ast, json, sys
from pathlib import Path
from transplant import R, W, read_region_raw, write_region, T_COMPOUND, T_STRING, T_LIST

HERE = Path(__file__).parent
FALLBACK = "minecraft:zombie"


def keep_set():
    tree = ast.parse((HERE / "planblocks.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "KEEP":
            return set(ast.literal_eval(node.value))
    raise SystemExit("KEEP not found in planblocks.py")


def ns(s): return s.split(":", 1)[0]


CITY = "lostcities:chests/lostcitychest"
DUNGEON = "minecraft:chests/simple_dungeon"
VILLAGE = "minecraft:chests/village/village_plains_house"
LOOT_EXACT = {
    "chaoszpack_lc_loot:chests/ammo": "keerdm_zombie_essentials:chests/tacz_ammochest",
    "spore:chests/equipment_chest": "keerdm_zombie_essentials:chests/tacz_gunchest",
    "revampedvillages:treasure": "minecraft:chests/village/village_temple",
    "revampedvillages:professions/cartographer_librarian": "minecraft:chests/village/village_cartographer",
    "revampedvillages:professions/weaponsmith": "minecraft:chests/village/village_weaponsmith",
    "revampedvillages:professions/shepherd": "minecraft:chests/village/village_shepherd",
    "revampedvillages:professions/leatherworker": "minecraft:chests/village/village_tannery",
    "revampedvillages:professions/fletcher": "minecraft:chests/village/village_fletcher",
    "revampedvillages:professions/toolsmith": "minecraft:chests/village/village_toolsmith",
    "revampedvillages:professions/mason": "minecraft:chests/village/village_mason",
    "revampedvillages:professions/butcher": "minecraft:chests/village/village_butcher",
    "revampedvillages:professions/armorer": "minecraft:chests/village/village_armorer",
    "realmrpg_quests:chests/fish_barrel": "minecraft:chests/village/village_fisher",
    "chefsdelight:chests/cooker": "minecraft:chests/village/village_butcher",
    "irons_spellbooks:chests/generic_magic_treasure": "minecraft:chests/ancient_city",
    "minecraft:chests/trial_chambers/reward": "minecraft:chests/ancient_city",
    "minecraft:chests/trial_chambers/corridor": DUNGEON,
    "minecraft:chests/trial_chambers/entrance": DUNGEON,
    "minecraft:chests/trial_chambers/intersection_barrel": DUNGEON,
    "minecraft:dispensers/trial_chambers/chamber": DUNGEON,
}
LOOT_NS = {
    "chaoszpack_lc_loot": CITY, "survival_instinct": CITY, "modern_structures": CITY,
    "modern_structure": CITY, "spore": CITY,
    "irons_spellbooks": DUNGEON, "betterdungeons": DUNGEON,
    "alexscaves": "minecraft:chests/abandoned_mineshaft",
    "realmrpg_quests": VILLAGE, "revampedvillages": VILLAGE, "chefsdelight": VILLAGE,
}


def fix_loot(be, keep, hits):
    lt = be.get("LootTable")
    if not lt or lt[0] != T_STRING:
        return False
    lid = lt[1]
    new = LOOT_EXACT.get(lid)
    if new is None:
        if ns(lid) in keep:
            return False
        new = LOOT_NS.get(ns(lid), CITY)
        if ns(lid) not in LOOT_NS:
            hits["UNPLANNED " + lid] = hits.get("UNPLANNED " + lid, 0) + 1
    be["LootTable"] = (T_STRING, new)
    k = "loot " + lid + " -> " + new
    hits[k] = hits.get(k, 0) + 1
    return True


def fix_spawner_entity(ent, keep, hits):
    """ent is the compound dict holding the entity id; returns True if changed."""
    eid = ent.get("id", (T_STRING, ""))[1]
    if not eid or ns(eid) in keep:
        return False
    hits[eid] = hits.get(eid, 0) + 1
    ent.clear(); ent["id"] = (T_STRING, FALLBACK)
    return True


def fix_region_chunk(root, keep, hits):
    changed = False
    # legacy in-chunk entity list (migrated by the game on load; cut-mod mobs log "Skipping Entity")
    if fix_entities_chunk(root, keep, hits, key="entities"):
        changed = True
    for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
        if fix_loot(be, keep, hits):
            changed = True
        if be.get("id", (T_STRING, ""))[1] != "minecraft:mob_spawner":
            continue
        sd = be.get("SpawnData")
        if sd and sd[0] == T_COMPOUND:
            ent = sd[1].get("entity")
            if ent and ent[0] == T_COMPOUND and fix_spawner_entity(ent[1], keep, hits):
                changed = True
        sp = be.get("SpawnPotentials")
        if sp and sp[0] == T_LIST:
            for pot in sp[1][1]:
                d = pot.get("data") if isinstance(pot, dict) else None
                if d and d[0] == T_COMPOUND:
                    ent = d[1].get("entity")
                    if ent and ent[0] == T_COMPOUND and fix_spawner_entity(ent[1], keep, hits):
                        changed = True
    return changed


def fix_entities_chunk(root, keep, dropped, key="Entities"):
    lst = root.get(key)
    if not lst or lst[0] != T_LIST:
        return False
    et, items = lst[1]
    kept = []
    for ent in items:
        eid = ent.get("id", (T_STRING, ""))[1]
        if eid and ns(eid) not in keep:
            dropped[eid] = dropped.get(eid, 0) + 1
            continue
        kept.append(ent)
    if len(kept) == len(items):
        return False
    root[key] = (T_LIST, (et, kept))
    return True


def process(dirpath, fixer, keep, tally, dry):
    touched = []
    for f in sorted(dirpath.glob("*.mca")):
        chunks = read_region_raw(f)
        out = {}; changed = False
        for slot, (ts, comp, raw) in chunks.items():
            name, root = R(raw).root()
            if fixer(root, keep, tally):
                changed = True
                raw = W().root(name, root)
            out[slot] = (ts, comp, raw)
        if changed:
            touched.append(f.name)
            if not dry:
                write_region(f, out)
    return touched


def main(argv):
    world = Path(argv[1]); dry = "--dry-run" in argv
    keep = keep_set()
    spawner_hits, dropped = {}, {}
    reg = process(world / "region", lambda r, k, t: fix_region_chunk(r, k, t), keep, spawner_hits, dry)
    ent = process(world / "entities", lambda r, k, t: fix_entities_chunk(r, k, t), keep, dropped, dry)
    print("spawner entities remapped to", FALLBACK, ":", json.dumps(spawner_hits, indent=1))
    print("entity records dropped:", json.dumps(dropped, indent=1))
    print("region files changed:", len(reg), reg)
    print("entity files changed:", len(ent), ent)
    (world / "fixspawners_touched.json").write_text(json.dumps({"region": reg, "entities": ent}, indent=1))
    print("DRY RUN - nothing written" if dry else "written")


if __name__ == "__main__":
    main(sys.argv)
