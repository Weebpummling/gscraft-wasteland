"""The whole In Control faction rule block, generated in one place and in one order.

In Control takes the **first matching rule**, so the order below is the design. Areas come from
`tools/incontrol_areas.py`; this file only decides who stands in them and what they are wearing.

    1  builds        every hostile denied inside anything the designers built or transplanted
    2  hold          every hostile denied, unconditionally - the switch that keeps all of this off
    3  Machines      pomkotsmechs at the reactor hall and the plant; denied everywhere else
    4  Militia       the east-bank spine and the plant; denied everywhere else
    5  the Dead      by site: the hospital, the streets, the yard, the plant's halls, the town
    6  Scavengers    the Woods, and the roads between - the fallback for anything left

**Builds are no-spawn ground (owner, 2026-09-09).** KROT is a work in progress and the same goes for
every other player-built and transplanted site; enemies belong in the base map's own places.

**Kit is by rank and by site, not one uniform for everyone.** §2.1 lists a wardrobe of about forty
pieces, and an earlier pass put a PASGT helmet and an IOTV vest on everything that could hold one -
which wastes the wardrobe and flattens the read at fifty metres. So:

  - the **Militia** match, because they are an army that never stood down, but the ranks do not. The
    Bulwark carries IE steel on the chest because he is the shield; the Fusilier wears a marksman's
    helmet because he holds the longest line; the Trooper and the Rifleman are the line, in US kit.
  - the **Dead wear what they died in**, which is the whole of §3.3: plant workers in insulated rubber
    with a crowbar, the hospital's dead in a medic's vest, the yard's labourers in a Gorka jacket with a
    shovel, and the town's residents in nothing at all, because they were civilians.
  - the **drowned** at the intake works and under the rail bridge get the sealed kit, a copper diving
    helmet and a backtank. They are the only enemy in the pack that reads as equipped for the water.
  - the **Scavengers do not match, and that is the point** (§3.2). Four looks across the illager ranks:
    a face wrap, a looted WW2 shell over a Gorka jacket, a bandana, and nothing. None of it issued.

Two traps from §2.1 respected: Dragon Rising ships no boots, so nobody is given any, and `cn21`/`cnfast`
give zero armour on the head, so they are not used as protection.

Not included, deliberately:

  - the Torch and the Chemist (§3.5) need Improved Mobs' item use, which is off while mob block
    destruction is held off (`griefing_off.py`). Burning a palisade is the block destruction the hold
    exists to prevent. They come back with it.
  - the Horrors have no rules here: the Knocker, the Eyes and the fog man are governed by their own
    configs (`gscraft-enemies.md` §3.4).
  - skeletons are "background" (`entities-v8` §2) and keep their existing rules.

    spawn_rules.py [--dry-run]
"""
import json
import sys
from pathlib import Path

IC = Path(r"G:/GSCraft/server/config/incontrol")
OVERWORLD = "minecraft:overworld"

IE = "immersiveengineering:"
SBW = "superbwarfare:"
DR = "dragonrise_reforge:"
PK = "pomkotsmechs:"
CR = "create:"

MECHS = [PK + "pms01", PK + "pms03"]
COMMANDO, FUSILIER, BULWARK = IE + "commando", IE + "fusilier", IE + "bulwark"
MILITIA = [COMMANDO, FUSILIER, BULWARK]
PILL = ["minecraft:pillager"]
DEAD = ["minecraft:zombie", "minecraft:zombie_villager", "minecraft:husk"]
DROWNED = ["minecraft:drowned"]
SPIDERS = ["minecraft:spider", "minecraft:cave_spider"]
SCAV_AXE = ["minecraft:vindicator"]
SCAV_CASTER = ["minecraft:evoker", "minecraft:illusioner"]
SCAV_REST = ["minecraft:witch", "minecraft:ravager"]

BUILDS = ["camp", "krot", "mega", "indu", "lib", "runway", "hub", "plaza", "novo", "biogen"]
NO_DROPS = "ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f]"

# ---- the wardrobe actually used, by what it reads as (§2.1)
PASGT, IOTV = SBW + "us_helmet_pasgt", SBW + "us_chest_iotv"
MARKSMAN = DR + "sniper21_helmet"
STEEL_CHEST = IE + "armor_steel_chestplate"
FARADAY_H, FARADAY_C = IE + "armor_faraday_helmet", IE + "armor_faraday_chestplate"
MEDIC = DR + "med21_chest"
GORKA = DR + "gorka3"
WRAP, JACKET = PK + "wandererarmorhelmet", PK + "wandererarmorchestplate"
BANDANA, RAGS = PK + "pomkotsarmorhelmet", PK + "pomkotsarmorchestplate"
WW2 = SBW + "ge_helmet_m_35"
DIVE_H, BACKTANK, DIVE_B = CR + "copper_diving_helmet", CR + "copper_backtank", CR + "copper_diving_boots"
# legs and feet, from the registry dump: Superb Warfare has no legs at all and Dragon Rising no boots,
# but DR does ship six leggings and Pomkots ships complete four-slot sets. Nobody wears bare legs now.
TAC_LEGS = DR + "kr06_pants"
GORKA_LEGS = DR + "gorka3_leggings"
FARADAY_L, FARADAY_B = IE + "armor_faraday_leggings", IE + "armor_faraday_boots"
STEEL_L, STEEL_B = IE + "armor_steel_leggings", IE + "armor_steel_boots"
WAND_L, WAND_B = PK + "wandererarmorleggings", PK + "wandererarmorboots"
RAGS_L, RAGS_B = PK + "pomkotsarmorleggings", PK + "pomkotsarmorboots"
# the second detachment, the sealed, the peacekeepers, the junk-armoured and the captain's one good vest
RU_H, RU_C = SBW + "ru_helmet_6b47", SBW + "ru_chest_6b43"
MSV_C, MSV_L = DR + "msv_chest", DR + "msv_pants"
SGT_H, SGT_C = DR + "fast_helmet", DR + "kr06_chest"
CAPT_H = DR + "kr06_helmet"
UN_H = DR + "un_helmet"
OCEAN_H, OCEAN_C, OCEAN_L = DR + "ocean07_helmet", DR + "ocean07_chest", DR + "ocean07_pants"
GASMASK = "createbigcannons:gas_mask"
CARD_H, CARD_C = CR + "cardboard_helmet", CR + "cardboard_chestplate"
CARD_L, CARD_B = CR + "cardboard_leggings", CR + "cardboard_boots"


def item(i):
    return '{id:"' + i + '",Count:1b}'


# The rifle matches the kit. A Type 81 is a Chinese rifle and read wrong on a US-kitted trooper; the
# spine carries an M4, the plant's Russian-kitted garrison an AK. Both are in TACZ's 54.
RIFLE = '{id:"tacz:modern_kinetic_gun",Count:1b,tag:{GunId:"tacz:m4a1"}}'
CROWBAR, PIPE, SHOVEL = item(SBW + "crowbar"), item(SBW + "steel_pipe"), item(SBW + "military_shovel")
CARD_SWORD = item(CR + "cardboard_sword")
AK47 = '{id:"tacz:modern_kinetic_gun",Count:1b,tag:{GunId:"tacz:ak47"}}'

# mobs, areas, rank, head, chest, legs, feet, hand, cap, chance
#   areas   None means "anywhere not already claimed by a rule above"
#   chance  None is always; a number is In Control's `random`, so the rank is a rare variant and must be
#           listed BEFORE the common rank it varies, because the first matching rule wins
# The two armies hold ground; the Dead are everywhere underneath them.
#
#   the Militia    US kit, an M4. Heartland the plant, east of the river. Outposts out_e1/out_e2, the
#                  east bank of the front, and the rail yard at Skadowsky.
#   the Column     Russian kit, an AK. Heartland the town, west of the river. Outposts out_w1/out_w2,
#                  the west bank, and the bridgehead at Skadowsky.
#
# The river is the front and the south-west bridge is the only crossing on this side, which is why both
# armies keep an outpost at Skadowsky: it is where the player meets each of them for the first time,
# facing each other across the one crossing.
#
# The Dead are ambient everywhere and are listed last, with no denial after them. Their site variants
# come first so a corpse at the switchyard is a plant worker and one in the hospital is a patient; the
# plain rank at the end catches every other piece of ground in the cell.
MIL_AREAS = ["plant", "out_e1", "out_e2", "front_en", "front_es", "sk_out_e"]
COL_AREAS = ["town", "out_w1", "out_w2", "front_wn", "front_ws", "sk_out_w"]

KITS = [
    # ---- the Militia: the unit that never stood down, holding the plant and the east bank
    ([COMMANDO], MIL_AREAS, "Militia Sergeant", SGT_H,    SGT_C,       TAC_LEGS, None,    None,  3, 0.12),
    ([BULWARK],  MIL_AREAS, "Militia Shield",   PASGT,    STEEL_CHEST, STEEL_L,  STEEL_B, None,  8, None),
    ([FUSILIER], MIL_AREAS, "Militia Gunner",   MARKSMAN, IOTV,        TAC_LEGS, None,    None,  8, None),
    ([COMMANDO], MIL_AREAS, "Militia Trooper",  PASGT,    IOTV,        TAC_LEGS, None,    None, 18, None),
    (PILL,       MIL_AREAS, "Militia Rifleman", PASGT,    IOTV,        TAC_LEGS, None,    RIFLE,14, None),

    # ---- the Column: the second army, in the kit it arrived in, stopped in the town
    ([COMMANDO], COL_AREAS, "Column Sergeant", SGT_H,    SGT_C,       MSV_L,   None,    None, 3, 0.12),
    ([BULWARK],  COL_AREAS, "Column Shield",   RU_H,     STEEL_CHEST, STEEL_L, STEEL_B, None, 8, None),
    ([FUSILIER], COL_AREAS, "Column Marksman", MARKSMAN, RU_C,        MSV_L,   None,    None, 8, None),
    ([COMMANDO], COL_AREAS, "Column Soldier",  RU_H,     RU_C,        MSV_L,   None,    None,18, None),
    (PILL,       COL_AREAS, "Column Rifleman", RU_H,     RU_C,        MSV_L,   None,    AK47,14, None),

    # ---- the Scavengers: looted, never issued, and never twice the same (§3.2). They hold the Woods and
    # the roads between everything, which is whatever neither army has claimed.
    (PILL, ["woods", None], "Scavenger Captain", CAPT_H, MSV_C, GORKA_LEGS, WAND_B, CROWBAR, 2, 0.06),
    (PILL, ["woods", None], "Scrapper", CARD_H, CARD_C, CARD_L, CARD_B, CARD_SWORD, 5, 0.18),
    (PILL,        ["woods", None], "Scavenger",        WRAP,    JACKET, WAND_L,     WAND_B, PIPE,    22, None),
    (SCAV_AXE,    ["woods", None], "Scavenger Raider", WW2,     GORKA,  GORKA_LEGS, WAND_B, CROWBAR, 12, None),
    (SCAV_CASTER, ["woods", None], "Scavenger Elder",  BANDANA, RAGS,   RAGS_L,     RAGS_B, None,     6, None),
    (SCAV_REST,   ["woods", None], "Scavenger",        None,    None,   None,       None,   None,     8, None),

    # ---- the Dead: the ambient threat, everywhere, wearing what they died in
    (DEAD, ["pl_react"], "Containment Crew", GASMASK, FARADAY_C, FARADAY_L, FARADAY_B, CROWBAR, 4, 0.35),
    (DEAD, ["pl_switch", "pl_admin", "pl_turb", "pl_react"],
     "Plant Worker", FARADAY_H, FARADAY_C, FARADAY_L, FARADAY_B, CROWBAR, 16, None),
    (DEAD, ["sk_hosp"], "The Infected", None, MEDIC, None, None, None, 12, None),
    (DEAD, ["sk_south"], "Yard Hand", None, GORKA, GORKA_LEGS, None, SHOVEL, 8, None),
    (DEAD, ["tw_stad", "tw_centre", "tw_slabs", "tw_blocks", "town"],
     "Peacekeeper", UN_H, MSV_C, MSV_L, None, None, 3, 0.08),
    # no area and no denial after it: this is the floor the whole cell stands on
    (DEAD, [None], "The Dead", None, None, None, None, None, None, None),
    (DROWNED, ["pl_intake", "plant"], "The Drowned", DIVE_H, BACKTANK, None, DIVE_B, None, 8, None),
    (DROWNED, ["tw_bridge"], "Drowned Patrol", OCEAN_H, OCEAN_C, OCEAN_L, None, None, 6, None),
    (DROWNED, [None], "The Drowned", DIVE_H, BACKTANK, None, DIVE_B, None, None, None),
]


def rule(mob=None, area=None, result="deny", when="onjoin", **extra):
    r = {"dimension": OVERWORLD, "when": when}
    if area:
        r["area"] = area
    if mob:
        r["mob"] = mob
    r["result"] = result
    r.update(extra)
    return r


def cap(n, mob):
    """A population ceiling.

    Note what this counts: In Control's count is **world-wide**, not per area. There is no way to scope
    it to the rule's own area, so a rank listed in six areas with a cap of 4 gets four across the whole
    map, not four in each. Every number below is therefore a world total, and the ambient ranks carry no
    cap at all - vanilla's own mob cap is the limit there, and a ceiling of fourteen zombies would have
    left the entire cell empty.
    """
    return {"amount": n, "mob": mob, "perplayer": False}


def dressed(mob, area, name, helm, chest, legs, feet, hand, n, chance=None):
    """Gate and dress, as two rules.

    They have to be two. A `maxcount` on the dressing rule means that past the cap the rule stops
    matching and the mob falls through to whatever is next, which turned three of six pillagers at the
    Militia's own centre into Scavengers. The cap denies; the dressing is unconditional.

    They also have to be in this order. A gating rule that only says "default" consumes the match and
    every dressing rule after it never runs. Actions apply whenever a rule matches, whatever the result,
    so `default` keeps vanilla's own spawn logic and still dresses what it lets through.

    Hands go through the nbt action, not `helditem`: `helditem` sets the main hand and leaves the off
    hand to Improved Mobs, which filled it with a diamond pickaxe, then flint and steel, then an ender
    pearl, then a lava bucket across successive runs. Writing HandItems sets both slots at once.
    """
    nbt = "{HandItems:[" + (hand or "{}") + ",{}]," + NO_DROPS + "}"
    out = []
    r = rule(mob=mob, area=area, result="default", customname=name, nbt=nbt)
    if chance is None:
        # a common rank: the cap denies the surplus, and the dressing itself is unconditional. A
        # maxcount here instead would make the overflow fall through and come out as another faction.
        # n of None means no ceiling, which is what the ambient ranks want.
        if n is not None:
            out.append(rule(mob=mob, area=area, result="deny", mincount=cap(n, mob)))
    else:
        # a rare variant: the chance sets how often it appears and the maxcount holds the ceiling.
        # Falling through past the cap is right here - what is beyond the ceiling should simply be the
        # ordinary rank listed below, not a denial, so a full site is not an empty one.
        r["random"] = chance
        r["maxcount"] = cap(n, mob)
    if helm:
        r["armorhelmet"] = {"item": helm}
    if chest:
        r["armorchest"] = {"item": chest}
    if legs:
        r["armorlegs"] = {"item": legs}
    if feet:
        r["armorboots"] = {"item": feet}
    out.append(r)
    return out


def build():
    out = []

    # ---- 1. builds are no-spawn ground
    for a in BUILDS:
        out.append(rule(area=a, result="deny", hostile=True))

    # ---- 2. the hold
    out.append(rule(result="deny", hostile=True))

    # ---- 3. the Machines. The hub is theirs in the design but is a build and deferred, so the plant is
    # the only ground they hold today, and the reactor hall is where the Overseer stands.
    out.append(rule(mob=MECHS, area="pl_react", result="default", maxcount=cap(2, MECHS)))
    out.append(rule(mob=MECHS, area="plant", result="default", maxcount=cap(4, MECHS)))
    out.append(rule(mob=MECHS, result="deny"))

    # ---- 4 to 6, by site
    for mobs, areas, name, helm, chest, legs, feet, hand, n, chance in KITS:
        for a in areas:
            out.extend(dressed(mobs, a, name, helm, chest, legs, feet, hand, n, chance))

    # ---- "a place, not a weather": each faction denied outside the ground claimed above
    # the Militia and the Column are the same three IE entities, so a single denial covers both: outside
    # the ground either army holds, no soldier stands up at all. The Dead have no such rule - they are
    # the ambient threat and their last rule is an unrestricted one.
    out.append(rule(mob=MILITIA, result="deny"))

    # spiders share the Dead's ground and the Woods' bunkers, and wear nothing
    for a in ("skad", "town", "woods"):
        out.append(rule(mob=SPIDERS, area=a, result="default", maxcount=cap(8, SPIDERS)))
    out.append(rule(mob=SPIDERS, result="deny"))
    return out


OWNED_NAMES = {k[2] for k in KITS}
OWNED_MOBS = set(MECHS + MILITIA + DEAD + DROWNED + SPIDERS + PILL +
                 SCAV_AXE + SCAV_CASTER + SCAV_REST)


def main(argv):
    dry = "--dry-run" in argv
    spawn = json.loads((IC / "spawn.json").read_text(encoding="utf-8"))

    def ours(r):
        if r.get("customname") in OWNED_NAMES:
            return True
        if r.get("hostile") and r.get("result") == "deny" and "mob" not in r \
                and "mincount" not in r and "spawner" not in r:
            return True
        mob = r.get("mob") or []
        return bool(mob) and all(m in OWNED_MOBS for m in mob)

    keep = [r for r in spawn if not ours(r)]
    block = build()
    out = block + keep
    print(f"{len(block)} faction rules + {len(keep)} kept = {len(out)}")
    seen = set()
    for r in block:
        nm = r.get("customname")
        key = (nm, r.get("area"))
        if nm and key not in seen:
            seen.add(key)
            print(f"   {nm:17s} {r.get('area', '(anywhere)'):10s} "
                  f"{r.get('armorhelmet', {}).get('item', '-').split(':')[-1]:20s} "
                  f"{r.get('armorchest', {}).get('item', '-').split(':')[-1]}")
    if dry:
        print("DRY RUN, nothing written")
        return 0
    (IC / "spawn.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
