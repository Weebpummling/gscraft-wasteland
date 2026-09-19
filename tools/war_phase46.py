"""Phase 46, THE LOOT SYSTEM, WHOLE (owner, 2026-09-19: "verify that the entire loot system functions") on the LOCAL
server. Needs no player. It checks the design against the GAME, not against itself: what the server rolls, knows and holds.

 1. The economy closes on paper: tools/itemflow.py --gate (nothing asked for without a source, nothing sourced that nothing
    uses, no dead weight, the start area feeds its quests, every needed-once thing a nine-in-ten find or better).
 2. The server has exactly the design's tables: nine building, five site. No stale one from a datapack.
 3. Every building table, rolled 4000 times by the server: every entry the design lists comes out, NOTHING else does, and
    each item's total is within a third of what its weight says (where that is 60 or more).
 4. Every site table, rolled 4000 times: every signature item comes out, every base table's items come out, nothing else.
 5. Every foreign chest table the world scan found becomes a design table: `loot remap` says so, and 600 rolls of it give
    only items of the design (no diamond, no TACZ gun, no backpack: the global loot modifiers are gone too).
 6. What must NOT be touched is not: a block's drops, an entity's drops, the jungle temple's dispenser.
 7. Every body and wreck rule rolls for real: for each entity in gscraft_drops, 3000 rolls give every rule's item and no other.
 8. The server knows every item id the loot system names anywhere: tables, drops, orders (in, out, tool, card), quest tasks
    and rewards, the kit.
 9. The station has every order, and every order's card is an item a quest gives or an order needs none.
10. A table fills a real container: `loot insert` of a site table into a chest puts stacks in it.
11. Every container in the record stands in the world as a Lootr container bound to the table the record says; the
    hospital's are bound to sites/hospital.
12. Lootr refreshes gscraft tables (config), and the quest book reloads with every new quest's items known.
13. No gscraft errors.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402
import loot as D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "mod/src/main/resources/data/gscraft"
LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
N = 4000


def c(cmd, t=120):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def roll(table, n):
    out = c(f"gscraft loot roll {table} {n}", 300)
    return {k: int(v) for k, v in re.findall(r"(\S+:\S+?)=(\d+)", out.split(":", 2)[-1] if " x" in out else out)}, "NO SUCH TABLE" in out


def mean_rolls(rr):
    return (rr[0] + rr[1]) / 2


def expect_building(name):
    d = D.BUILDING[name]
    total = sum(e[1] for e in d["pool"])
    exp = {}
    for e in d["pool"]:
        cnt = (e[2] + e[3]) / 2 if len(e) == 4 else 1
        exp[e[0]] = exp.get(e[0], 0) + mean_rolls(d["rolls"]) * e[1] / total * cnt
    if d.get("once"):
        tot = sum(e[1] for e in d["once"]) + d.get("once_empty", 0)
        for e in d["once"]:
            exp[e[0]] = exp.get(e[0], 0) + e[1] / tot
    return exp


# 1
gate = subprocess.run([sys.executable, str(ROOT / "tools/itemflow.py"), "--gate"], capture_output=True, text=True, encoding="utf-8", errors="replace")
tail = gate.stdout[gate.stdout.find("GATE:"):].strip().splitlines()
check("the economy closes on paper (itemflow --gate)", gate.returncode == 0, " | ".join(tail[:6]))

# 2
out = c("gscraft loot tables")
have = set(re.findall(r"((?:building|sites)/\w+)", out))
want = {f"building/{k}" for k in D.BUILDING} | {f"sites/{k}" for k in D.SITES}
check("the server has exactly the design's tables: nine building, five site", have == want, f"missing {sorted(want - have)}; extra {sorted(have - want)}")

# 3
bad = []
for name in D.BUILDING:
    got, missing_table = roll(f"gscraft:building/{name}", N)
    exp = expect_building(name)
    if missing_table:
        bad.append(f"{name}: no such table")
        continue
    for item in exp:
        if got.get(item, 0) == 0:
            bad.append(f"{name}: {item} never came out")
    for item in got:
        if item not in exp:
            bad.append(f"{name}: {item} is not in the design")
    for item, e in exp.items():
        if e * N >= 60 and not (0.67 * e * N <= got.get(item, 0) <= 1.33 * e * N):
            bad.append(f"{name}: {item} {got.get(item, 0)} against {e * N:.0f} expected")
check(f"nine building tables rolled {N} times each: every entry, nothing else, totals within a third", not bad, bad[:6] or "as designed")

# 4
bad = []
for name, d in D.SITES.items():
    got, missing_table = roll(f"gscraft:sites/{name}", N)
    allowed = {e[0] for e in d["sig"]}
    for b, _ in d["bases"]:
        allowed |= set(expect_building(b))
    if missing_table:
        bad.append(f"{name}: no such table")
        continue
    for e in d["sig"]:
        if got.get(e[0], 0) == 0:
            bad.append(f"{name}: signature {e[0]} never came out")
    for b, _ in d["bases"]:
        for item, e in expect_building(b).items():
            if e * N / len(d["bases"]) >= 40 and got.get(item, 0) == 0:
                bad.append(f"{name}: {item} of base {b} never came out")
    for item in got:
        if item not in allowed:
            bad.append(f"{name}: {item} is not in the design")
check(f"five site tables rolled {N} times each: the signature, the bases, nothing else", not bad, bad[:6] or "as designed")

# 5
FOREIGN = ["minecraft:chests/simple_dungeon", "underground_bunkers:chests/underground_bunker/underground_bunker_supply", "underground_bunkers:chests/underground_bunker/underground_bunker_normal",
           "underground_bunkers:chests/underground_bunker/underground_bunker_treasure", "keerdm_zombie_essentials:chests/tacz_gunchest", "keerdm_zombie_essentials:chests/tacz_ammochest",
           "keerdm_zombie_essentials:chests/abandoned_car_basic_vics", "keerdm_zombie_essentials:chests/abandoned_car_emergency_tacz", "lostcities:chests/lostcitychest",
           "lostcities:chests/raildungeonchest", "minecraft:chests/ancient_city", "minecraft:chests/village/village_plains_house", "minecraft:chests/abandoned_mineshaft",
           "minecraft:chests/village/village_cartographer", "minecraft:chests/village/village_weaponsmith", "apotheosis:chests/spawner_swarm", "apotheosis:chests/chest_valuable",
           "minecraft:chests/shipwreck_supply", "minecraft:chests/desert_pyramid", "minecraft:chests/stronghold_library", "minecraft:chests/spawn_bonus_chest", "minecraft:chests/end_city_treasure"]
bad, went = [], {}
for fid in FOREIGN:
    m = re.search(r"-> (gscraft:building/(\w+))", c(f"gscraft loot remap {fid}"))
    if not m:
        bad.append(f"{fid}: not remapped")
        continue
    went[fid.split("/")[-1]] = m.group(2)
    got, missing_table = roll(fid, 600)
    allowed = set(expect_building(m.group(2)))
    if missing_table:
        bad.append(f"{fid}: the server has no such table (its mod is not installed?)")
    if not got:
        bad.append(f"{fid}: rolled nothing")
    for item in got:
        if item not in allowed:
            bad.append(f"{fid} -> {m.group(2)}: {item} leaked in")
check(f"{len(FOREIGN)} foreign chest tables become design tables and roll nothing but the design", not bad, bad[:6] or str(went)[:300])

# 6
alone = [c(f"gscraft loot remap {i}") for i in ("minecraft:blocks/stone", "minecraft:entities/zombie", "minecraft:chests/jungle_temple_dispenser", "gscraft:building/office")]
stone, _ = roll("minecraft:blocks/stone", 1)
check("what must not be touched is not: a block's drops, an entity's, the jungle dispenser, our own", all("left alone" in a for a in alone), [a[-40:] for a in alone])

# 7
bad, n_rules = [], 0
for f in sorted((RES / "gscraft_drops").glob("*.json")):
    by = {}
    for rule in json.loads(f.read_text(encoding="utf-8"))["drops"]:
        if "item" in rule:
            by.setdefault(rule["entity"], set()).add(rule["item"])
            n_rules += 1
    for entity, items in by.items():
        out = c(f"gscraft drops roll {entity} 3000", 300)
        got = set(re.findall(r"([a-z0-9_]+:[a-z0-9_/]+)=\d+", out)) - {entity}
        for i in items:
            if i not in out:
                bad.append(f"{f.stem} {entity}: {i} never dropped")
        for g in got:
            if g not in items and not g.startswith(("superbwarfare:us_", "superbwarfare:ru_", "superbwarfare:ge_", "dragonrise_reforge:")):   # worn armour at drops.armour_chance
                bad.append(f"{f.stem} {entity}: {g} is not a rule")
check(f"every body and wreck rule rolls ({n_rules} rules)", not bad, bad[:6] or "every rule's item dropped, and no other")

# 8
ids = set()
for d in list(D.BUILDING.values()):
    ids |= {e[0] for e in d["pool"]} | {e[0] for e in d.get("once", [])}
for d in D.SITES.values():
    ids |= {e[0] for e in d["sig"]}
for f in (RES / "gscraft_drops").glob("*.json"):
    ids |= {x["item"] for x in json.loads(f.read_text(encoding="utf-8"))["drops"] if "item" in x}
orders = json.loads((RES / "gscraft_recipes/recipes.json").read_text(encoding="utf-8"))["orders"]
for o in orders:
    ids |= {o["out"]} | {k for k in o["in"] if not k.startswith("#")} | ({o["tool"]} if o.get("tool") else set()) | ({"gscraft:" + o["card"]} if o.get("card") else set())
quests = json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))["quests"]
for q in quests:
    ids |= {t["item"] for t in q["tasks"] if t.get("item")} | {x["item"] for x in q["rewards"] if x.get("item")}
ids |= {k["item"] for k in json.loads((RES / "gscraft_survivors/survivors.json").read_text(encoding="utf-8"))["first_join"]["kit"] if k.get("item")}
unknown = [i for i in sorted(ids) if "Unknown item" in c(f"clear @a {i} 0")]
check(f"the server knows every item the loot system names ({len(ids)} ids)", not unknown, unknown or "all known")

# 9
boot = LOG.read_text(encoding="utf-8", errors="replace")
console = LOG.with_name("console-detached.log")
if console.exists():
    boot += console.read_text(encoding="utf-8", errors="replace")
m = re.findall(r"station: (\d+) orders, (\d+) cards", boot)
cards = {o["card"] for o in orders if o.get("card")}
given = {x["item"].split(":")[1] for q in quests for x in q["rewards"] if x.get("item", "").startswith("gscraft:card_")}
check("the station has every order, and every card is one a quest gives", bool(m) and int(m[-1][0]) == len(orders) and int(m[-1][1]) == len(cards) and cards <= given,
      f"the server loaded {m[-1] if m else '?'}; the data has {len(orders)} orders, {len(cards)} cards; cards no quest gives: {sorted(cards - given)}")

# 10
X, Y, Z = -2000, 250, -600
c(f"forceload add {X} {Z}")
time.sleep(2)
c(f"setblock {X} {Y} {Z} minecraft:chest")
ins = c(f"loot insert {X} {Y} {Z} loot gscraft:sites/hospital")
stacks = len(re.findall(r"Slot:", c(f"data get block {X} {Y} {Z} Items")))
c(f"setblock {X} {Y} {Z} minecraft:air")
c(f"forceload remove {X} {Z}")
check("a site table fills a real container", stacks >= 2, f"[{ins[:50]}]; stacks in the chest {stacks}")

# 11
import chests as CH  # noqa: E402
record = json.loads((ROOT / "tools/chests.json").read_text(encoding="utf-8"))
for x0, x1, z0, z1 in CH.BOXES:
    c(f"forceload add {x0 - 2} {z0 - 2} {x1 + 2} {z1 + 2}")
time.sleep(6)
bad = []
for e in record:
    at = f"{e['x']} {e['y']} {e['z']}"
    if not any("passed" in c(f"execute if block {at} lootr:{b}") for b in ("lootr_chest", "lootr_barrel", "lootr_trapped_chest")):
        bad.append(f"{at}: not a Lootr container")
        continue
    out = c(f"data get block {at} LootTable")
    if f'"{CH.table_id(e["table"])}"' not in out:
        bad.append(f"{at}: wants {e['table']}, the block says [{out[-60:]}]")
hosp = [e for e in record if e["table"] == "sites/hospital"]
for x0, x1, z0, z1 in CH.BOXES:
    c(f"forceload remove {x0 - 2} {z0 - 2} {x1 + 2} {z1 + 2}")
check(f"all {len(record)} recorded containers stand, Lootr, bound to their table; the hospital's {len(hosp)} to its site table", not bad and len(hosp) >= 12, bad[:4] or "every one")

# 12
lootr = Path("G:/GSCraft/server/config/lootr-common.toml").read_text(encoding="utf-8", errors="replace")
reload_out = c("ftbquests reload", 180)
errs = [l for l in LOG.read_text(encoding="utf-8", errors="replace")[-20000:].splitlines() if "ftbquests" in l.lower() and re.search(r"ERROR|Exception", l)]
check("Lootr refreshes gscraft tables, and the quest book reloads clean", re.search(r'refresh_modids\s*=\s*\[[^\]]*"gscraft"', lootr) and not errs, f"reload [{reload_out[:50]}]; ftbquests error lines {len(errs)}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:6]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
