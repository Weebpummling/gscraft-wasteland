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
DIVE_H, BACKTANK = CR + "copper_diving_helmet", CR + "copper_backtank"


def item(i):
    return '{id:"' + i + '",Count:1b}'


RIFLE = '{id:"tacz:modern_kinetic_gun",Count:1b,tag:{GunId:"tacz:type_81"}}'
CROWBAR, PIPE, SHOVEL = item(SBW + "crowbar"), item(SBW + "steel_pipe"), item(SBW + "military_shovel")

# mobs, areas, rank name, head, chest, main hand, cap per area.
# an area of None means "anywhere not already claimed by a rule above".
KITS = [
    # ---- the Militia. One army; the ranks are not interchangeable.
    ([BULWARK],  ["farbank", "plant"], "Militia Shield",   PASGT,    STEEL_CHEST, None,    3),
    ([FUSILIER], ["farbank", "plant"], "Militia Gunner",   MARKSMAN, IOTV,        None,    3),
    ([COMMANDO], ["farbank", "plant"], "Militia Trooper",  PASGT,    IOTV,        None,    6),
    (PILL,       ["farbank", "plant"], "Militia Rifleman", PASGT,    IOTV,        RIFLE,   4),

    # ---- the Dead, wearing what they died in
    (DEAD, ["pl_switch", "pl_admin", "pl_turb", "pl_react"],
     "Plant Worker", FARADAY_H, FARADAY_C, CROWBAR, 10),
    (DEAD, ["sk_hosp"], "The Infected", None, MEDIC, None, 12),
    (DEAD, ["sk_south"], "Yard Hand", None, GORKA, SHOVEL, 8),
    (DEAD, ["sk_town", "tw_stad", "tw_centre", "tw_slabs", "tw_blocks", "town", "skad", "farm"],
     "The Dead", None, None, None, 14),
    (DROWNED, ["pl_intake", "tw_bridge", "plant"], "The Drowned", DIVE_H, BACKTANK, None, 8),

    # ---- the Scavengers: looted, never issued, and never twice the same (§3.2)
    (PILL,        ["woods", None], "Scavenger",        WRAP,    JACKET, PIPE,    10),
    (SCAV_AXE,    ["woods", None], "Scavenger Raider", WW2,     GORKA,  CROWBAR, 6),
    (SCAV_CASTER, ["woods", None], "Scavenger Elder",  BANDANA, RAGS,   None,    3),
    (SCAV_REST,   ["woods", None], "Scavenger",        None,    None,   None,    4),
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
    return {"amount": n, "mob": mob, "perplayer": False}


def dressed(mob, area, name, helm, chest, hand, n):
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
    out = [rule(mob=mob, area=area, result="deny", mincount=cap(n, mob))]
    r = rule(mob=mob, area=area, result="default", customname=name, nbt=nbt)
    if helm:
        r["armorhelmet"] = {"item": helm}
    if chest:
        r["armorchest"] = {"item": chest}
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
    for mobs, areas, name, helm, chest, hand, n in KITS:
        for a in areas:
            out.extend(dressed(mobs, a, name, helm, chest, hand, n))

    # ---- "a place, not a weather": each faction denied outside the ground claimed above
    out.append(rule(mob=MILITIA, result="deny"))
    out.append(rule(mob=DEAD + DROWNED, result="deny"))

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
