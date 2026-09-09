"""The whole In Control faction rule block, generated in one place and in one order.

This replaces `militia_rules.py` and `faction_dress.py`, which each owned a slice of `spawn.json` and
inserted into it independently. In Control takes the **first matching rule**, so a rule block assembled
by several tools that each choose their own insertion point is a bug waiting to happen - and was one
twice: rules appended past a generic pillager rule never ran, and a deny anchored on the wrong rule put
the hold behind the factions it was meant to suppress. One tool, one order, rebuilt from scratch each
run.

Order, and every line of it is load-bearing:

    1  builds        every hostile denied inside anything the designers built or transplanted
    2  hold          every hostile denied, unconditionally - the switch that keeps all of this off
    3  Machines      pomkotsmechs at the plant; denied everywhere else
    4  Militia       the east-bank spine and the plant; denied everywhere else
    5  the Dead      Skadowsky, the town, the farm; spiders share it and the Woods' bunkers
    6  Scavengers    the Woods, and the roads between - the fallback for anything left
    each rule gates and dresses at once - see dressed()

**Builds are no-spawn ground (owner, 2026-09-09).** KROT is a work in progress and the same applies to
every other player-built and transplanted site; the places enemies belong are the base map's own - the
Pripyat town, the plant, the Woods, Skadowsky's streets and the fields. So rule 1 denies hostiles inside
the camp, KROT, the mega-base, the industrial district, the library, the runway pad and the whole desert
city complex, and it sits ahead of the hold so it holds whatever else changes.

Dressing runs at `onjoin`, never `finalize`: `finalize` does not fire for a `/summon` or for a mob a
horde wave adds, and this design places most of its enemies that way.

Not included, deliberately:

  - the Torch and the Chemist (§3.5) need Improved Mobs' item use, which is switched off while mob block
    destruction is held off (`griefing_off.py`). Burning a palisade is the block destruction the hold
    exists to prevent. They come back with it.
  - the Horrors have no rules here: the Knocker, the Eyes and the fog man are governed by their own
    configs, as `gscraft-enemies.md` §3.4 says.
  - the hub's Machines and every deferred site stay denied with their site.

    spawn_rules.py [--dry-run]
"""
import json
import sys
from pathlib import Path

IC = Path(r"G:/GSCraft/server/config/incontrol")
OVERWORLD = "minecraft:overworld"

IE = "immersiveengineering:"
SBW = "superbwarfare:"
PK = "pomkotsmechs:"

MECHS = [PK + "pms01", PK + "pms03"]
MILITIA = [IE + "commando", IE + "fusilier", IE + "bulwark"]
DEAD = ["minecraft:zombie", "minecraft:zombie_villager", "minecraft:husk", "minecraft:drowned"]
SCAV_ILLAGER = ["minecraft:vindicator", "minecraft:evoker", "minecraft:illusioner",
                "minecraft:witch", "minecraft:ravager"]
# spiders are the Dead's too - "the bunkers; the sewers are deferred" (enemies §3.1). They hold no
# equipment, so they are gated with the Dead but never dressed.
SPIDERS = ["minecraft:spider", "minecraft:cave_spider"]

# every build: nothing hostile spawns inside one
BUILDS = ["camp", "krot", "mega", "indu", "lib", "runway", "hub", "plaza", "novo", "biogen"]

# nothing an enemy carries ever drops (E7a)
NO_DROPS = "{ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f]}"


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


def hands(main=None):
    """Both hands, written through the nbt action.

    The `helditem` action sets the main hand and leaves the off hand to Improved Mobs, which kept putting
    something in it - a diamond pickaxe, flint and steel, an ender pearl, a lava bucket, across
    successive runs. Neither the ARMOR/HELDITEMS exemption nor USEITEM in the Flag Blacklist nor the Item
    Use Blacklist stopped it. Writing HandItems as NBT sets both slots at once and leaves nothing for
    anything else to fill.
    """
    off = "{}"
    return f"HandItems:[{main or '{}'},{off}]"


def dressed(mob, area, name, helm, chest, hand, n):
    """Gate and dress in one rule.

    These have to be the same rule. In Control stops at the first match, so a gating rule that only says
    "default" for a faction in its area consumes the match and every dressing rule after it never runs -
    which is what a first attempt at this did. Actions apply whenever a rule matches, whatever the
    result, so `default` keeps vanilla's own spawn logic and still dresses what it lets through.
    """
    # Two rules, not one. A maxcount on the dressing rule means that past the cap the rule stops
    # matching and the mob falls through to whatever is next - which made three of six pillagers at the
    # Militia's own centre come out as Scavengers. The cap has to deny, and the dressing has to be
    # unconditional, so the surplus is refused rather than re-factioned.
    over = rule(mob=mob, area=area, result="deny", mincount=cap(n, mob))
    r = rule(mob=mob, area=area, result="default",
             customname=name, nbt="{" + hands(hand) + "," + NO_DROPS.strip("{}") + "}")
    if helm:
        r["armorhelmet"] = {"item": helm}
    if chest:
        r["armorchest"] = {"item": chest}
    return [over, r]


PASGT, IOTV = SBW + "us_helmet_pasgt", SBW + "us_chest_iotv"
RIFLE = '{id:"tacz:modern_kinetic_gun",Count:1b,tag:{GunId:"tacz:type_81"}}'
FARADAY_H, FARADAY_C = IE + "armor_faraday_helmet", IE + "armor_faraday_chestplate"
WRAP, JACKET = PK + "wandererarmorhelmet", PK + "wandererarmorchestplate"
PILL = ["minecraft:pillager"]


def build():
    out = []

    # ---- 1. builds are no-spawn ground
    for a in BUILDS:
        out.append(rule(area=a, result="deny", hostile=True))

    # ---- 2. the hold: every hostile denied until this rule is removed
    out.append(rule(result="deny", hostile=True))

    # ---- 3. the Machines. The hub is theirs in the design but is a build and deferred, so the plant is
    # the only ground they hold today.
    out.append(rule(mob=MECHS, area="plant", result="default", maxcount=cap(4, MECHS)))
    out.append(rule(mob=MECHS, result="deny"))

    # ---- 4. the Militia: "a place, not a weather" (enemies §3.3). The three IE ranks and the Rifleman.
    for a in ("farbank", "plant"):
        out.extend(dressed(MILITIA, a, "Militia", PASGT, IOTV, None, 6))
    for a in ("farbank", "plant"):
        out.extend(dressed(PILL, a, "Militia Rifleman", PASGT, IOTV, RIFLE, 4))
    out.append(rule(mob=MILITIA, result="deny"))

    # ---- 5. the Dead. Workers where people worked; the town's own carry nothing (§3.3).
    for a in ("plant", "skad"):
        out.extend(dressed(DEAD, a, "Worker", FARADAY_H, FARADAY_C,
                           '{id:"' + SBW + 'crowbar",Count:1b}', 14))
    for a in ("town", "farm"):
        out.extend(dressed(DEAD, a, "The Dead", None, None, None, 14))
    out.append(rule(mob=DEAD, result="deny"))

    # spiders share the Dead's ground and the Woods' bunkers, and wear nothing
    for a in ("skad", "town", "woods"):
        out.append(rule(mob=SPIDERS, area=a, result="default", maxcount=cap(8, SPIDERS)))
    out.append(rule(mob=SPIDERS, result="deny"))

    # ---- 6. the Scavengers hold the Woods and the roads between things, so the Woods is explicit and
    # everything not already claimed falls to them rather than being denied. Looted, never issued (§3.2).
    out.extend(dressed(PILL + SCAV_ILLAGER, "woods", "Scavenger", WRAP, JACKET,
                       '{id:"' + SBW + 'steel_pipe",Count:1b}', 10))
    out.extend(dressed(PILL + SCAV_ILLAGER, None, "Scavenger", WRAP, JACKET,
                       '{id:"' + SBW + 'steel_pipe",Count:1b}', 8))
    return out


def main(argv):
    dry = "--dry-run" in argv
    spawn = json.loads((IC / "spawn.json").read_text(encoding="utf-8"))

    # keep only rules this tool does not own, so a re-run rebuilds the block cleanly
    def ours(r):
        if r.get("customname") in ("Militia Rifleman", "Scavenger", "Worker", "The Dead"):
            return True
        if r.get("hostile") and r.get("result") == "deny" and "mob" not in r \
                and "mincount" not in r and "spawner" not in r:
            return True
        mob = r.get("mob") or []
        return bool(mob) and all(m in MECHS + MILITIA + DEAD + SPIDERS + SCAV_ILLAGER + ["minecraft:pillager"]
                                 for m in mob)

    keep = [r for r in spawn if not ours(r)]
    block = build()
    out = block + keep
    print(f"{len(block)} faction rules + {len(keep)} kept = {len(out)}")
    for i, r in enumerate(block):
        mob = r.get("mob")
        mob = ",".join(m.split(":")[-1] for m in mob)[:30] if mob else "(any hostile)"
        print(f"  {i:2d} {mob:32s} {r.get('area', '-'):8s} {r['result']:8s} {r.get('customname', '')}")
    if dry:
        print("DRY RUN, nothing written")
        return 0
    (IC / "spawn.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
