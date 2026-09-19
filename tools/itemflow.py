#!/usr/bin/env python3
"""The item economy audited (owner, 2026-09-18: "work on the items and drop tables now"): every place an item comes FROM
and every place one is ASKED FOR, read from the data the game actually loads, and the gaps between them.

    python tools/itemflow.py            -> the report
    python tools/itemflow.py --json     -> the same as JSON (tools/itemflow.json), for a diff after a change
    python tools/itemflow.py --gate     -> exit 1 unless the economy CLOSES (loot design 2026-09-19): nothing asked for without a
                                           reachable source, nothing sourced that nothing uses (any namespace), no id that is not
                                           registered, no dead weight in any table, nothing the quests need in total that the
                                           start area's chests do not hold (unless bodies drop it), and every thing needed once
                                           found by one player nine times in ten (unless dropped or rewarded)

Sources: the building loot tables (loot_tables/building/*.json), the body and wreck drop tables (gscraft_drops/*.json),
station orders' outputs (gscraft_recipes/recipes.json), quest item rewards (tools/quests.json), the first-join kit.
Sinks:   quest hand-ins and shows, station orders' inputs (and the card an order needs).

It reports: asked for with NO source (a quest or an order nobody can finish); a source only behind a locked order
(fine, but worth seeing); sourced but never asked for (dead weight in a table); registered but appearing nowhere; ids
referenced that are not registered (typos); and, per building table, what share of its weight is dead weight. Tags
(`#minecraft:wool`) are listed, not resolved. It reads data only - it proves nothing about what a player meets in play.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "mod/src/main/resources/data/gscraft"

items = {"gscraft:" + i["id"]: i for i in json.loads((RES / "gscraft_items/items.json").read_text(encoding="utf-8"))["items"]}
# blocks and items the mod registers in code, not in items.json
CODE_ITEMS = {"gscraft:station", "gscraft:bandage"} | {f"gscraft:{e}_spawn_egg" for e in ("bloater", "matron", "nato_soldier", "ruaf_soldier", "scavenger")}   # ModItems.java

sources = defaultdict(list)   # item -> [where from]
sinks = defaultdict(list)     # item -> [where asked for]

# the loot tables: building/* by their bare name (what tools/chests.json records), sites/* as "sites/<id>"
tables = {}
TABLE_FILES = {}
for f in sorted((RES / "loot_tables/building").glob("*.json")) + sorted((RES / "loot_tables/sites").glob("*.json")):
    name = f.stem if f.parent.name == "building" else f"sites/{f.stem}"
    TABLE_FILES[name] = f
    lt = json.loads(f.read_text(encoding="utf-8"))
    weights = {}
    for pool in lt["pools"]:
        for e in pool["entries"]:
            if e.get("type") == "minecraft:item":
                weights[e["name"]] = weights.get(e["name"], 0) + e.get("weight", 1)
                sources[e["name"]].append(f"table:{name}")
    tables[name] = weights

# body and wreck drops
for f in sorted((RES / "gscraft_drops").glob("*.json")):
    for d in json.loads(f.read_text(encoding="utf-8"))["drops"]:
        if "item" in d:
            sources[d["item"]].append(f"drop:{f.stem}")

# station orders
orders = json.loads((RES / "gscraft_recipes/recipes.json").read_text(encoding="utf-8"))["orders"]
made_by = {}
for o in orders:
    made_by[o["out"]] = o
    sources[o["out"]].append(f"order:{o['id']}" + (" (card)" if o.get("card") else ""))
    for k in o["in"]:
        sinks[k].append(f"order:{o['id']}")
    if o.get("card"):
        sinks["gscraft:" + o["card"]].append(f"order:{o['id']} needs it")
    if o.get("tool"):
        sinks[o["tool"]].append(f"order:{o['id']} (tool)")

# quests
quests = json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))["quests"]
for q in quests:
    for t in q.get("tasks", []):
        if t.get("type") == "item":
            sinks[t["item"]].append(f"quest:{q['key']}" + ("" if t.get("consume", True) else " (show)"))
    for rw in q.get("rewards", []):
        if rw.get("type") == "item":
            sources[rw["item"]].append(f"reward:{q['key']}")

# the kit
kit = json.loads((RES / "gscraft_survivors/survivors.json").read_text(encoding="utf-8"))["first_join"]["kit"]
for k in kit:
    if k.get("item"):
        sources[k["item"]].append("kit")

known = set(items) | CODE_ITEMS


def found_in_world(item):
    """a source a player can reach without already owning the thing: a table or a drop, a reward, the kit"""
    return [s for s in sources.get(item, []) if not s.startswith("order:")]


def reachable(item, seen=()):
    """can it be had at all: found, or made by an order whose every input is reachable (tags assumed findable)"""
    if item.startswith("#") or found_in_world(item):
        return True
    o = made_by.get(item)
    if not o or item in seen:
        return False
    return all(reachable(k, seen + (item,)) for k in o["in"])


# what a player USES UP is a use too (2026-09-19): food, and the rounds of the kit's gun. Without this the audit called canned
# goods and pistol rounds dead weight in every table that stocks them.
for it in json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_items/items.json").read_text(encoding="utf-8")).get("items", []):
    if isinstance(it, dict) and it.get("food"):
        sinks["gscraft:" + it["id"]].append("eaten")
for k in json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_survivors/survivors.json").read_text(encoding="utf-8"))["first_join"]["kit"]:
    if "ammo" in k.get("item", ""):
        sinks[k["item"]].append("the kit gun's rounds")
# what is used by being PLACED, WORN, FIRED or READ - a use the data cannot show (loot design 2026-09-19). Each line is a claim
# about the game and is checked when it is written, not by this script.
USED = {
    "gscraft:station": "placed: the station", "gscraft:claim_marker": "planted at a strongpoint",
    "superbwarfare:rifle_ammo": "the Marlin's rounds (R0's reward)",
    "superbwarfare:handgun_ammo": "the kit gun's rounds", "superbwarfare:heavy_ammo": "a captured vehicle's guns", "superbwarfare:armor_plate": "refills a worn vest",
    "superbwarfare:marlin": "a gun", "superbwarfare:glock_17": "a gun", "superbwarfare:ru_chest_6b43": "worn", "superbwarfare:sandbag": "placed, and R0",
    "sophisticatedbackpacks:backpack": "worn", "minecraft:compass": "held", "minecraft:map": "held", "flashlight:flashlight": "held", "flashlight:battery": "the flashlight's",
    "patchouli:guide_book": "read", "minecraft:bread": "eaten", "minecraft:rotten_flesh": "eaten, badly", "minecraft:dried_kelp": "eaten",
    "superbwarfare:small_shell_he": "a captured vehicle's gun", "superbwarfare:medium_anti_ground_missile": "a captured vehicle's launcher",
}
for k, why in USED.items():
    if k in sources:
        sinks[k].append(why)

report = {"no_source": [], "unreachable": [], "order_only": [], "no_sink": [], "nowhere": [], "unregistered": [], "tables": {}, "tags": []}
for item in sorted(sinks):
    if item.startswith("#"):
        report["tags"].append({"tag": item, "asked_by": sinks[item]})
        continue
    if not sources.get(item):
        report["no_source"].append({"item": item, "asked_by": sinks[item]})
    elif not reachable(item):
        report["unreachable"].append({"item": item, "asked_by": sinks[item], "sources": sources[item]})
    elif not found_in_world(item):
        report["order_only"].append({"item": item, "made_by": sources[item]})
for item in sorted(sources):
    if item not in sinks and items.get(item, {}).get("role") != "strike":   # every namespace: another mod's item in a table is dead weight too
        report["no_sink"].append({"item": item, "from": sorted(set(sources[item]))})
for item in sorted(known):
    if item not in sources and item not in sinks and not item.endswith("_spawn_egg"):   # the eggs are the operator's
        report["nowhere"].append(item)
for item in sorted(set(sources) | set(sinks)):
    if item.startswith("gscraft:") and item not in known:
        report["unregistered"].append({"item": item, "in": sorted(set(sources.get(item, []) + sinks.get(item, [])))})
for name, weights in tables.items():
    total = sum(weights.values())
    dead = sum(w for i, w in weights.items() if i not in sinks)
    report["tables"][name] = {"entries": len(weights), "weight": total, "dead_weight_share": round(dead / total, 2) if total else 0,
                              "dead": sorted(i for i in weights if i not in sinks)}

# ---- scarcity: can ONE player fill the quests' asks from the chests that exist in the start area? Lootr chests are per
# player, so each placed chest (tools/chests.json: its table) yields its table's expectation once per player.
yields = {}   # table -> item -> expected count per chest


def table_name(ref):
    """gscraft:building/x -> x, gscraft:sites/x -> sites/x"""
    path = ref.split(":", 1)[1]
    return path.split("/", 1)[1] if path.startswith("building/") else path


def yield_of(name):
    if name in yields:
        return yields[name]
    per = defaultdict(float)
    for pool in json.loads(TABLE_FILES[name].read_text(encoding="utf-8"))["pools"]:
        rolls = pool.get("rolls", 1)
        r = (rolls["min"] + rolls["max"]) / 2 if isinstance(rolls, dict) else rolls
        total = sum(e.get("weight", 1) for e in pool["entries"])
        for e in pool["entries"]:
            share = r * e.get("weight", 1) / total
            if e.get("type") == "minecraft:loot_table":
                for k, v in yield_of(table_name(e["name"])).items():
                    per[k] += share * v
            if e.get("type") != "minecraft:item":
                continue
            cnt = 1.0
            for fn in e.get("functions", []):
                if fn.get("function") == "minecraft:set_count":
                    c = fn["count"]
                    cnt = (c["min"] + c["max"]) / 2 if isinstance(c, dict) else c
            per[e["name"]] += share * cnt
    yields[name] = dict(per)
    return yields[name]


for name in TABLE_FILES:
    yield_of(name)
placed = defaultdict(int)
chests_file = ROOT / "tools/chests.json"
if chests_file.exists():
    for c in json.loads(chests_file.read_text(encoding="utf-8")):
        placed[c["table"]] += 1
available = defaultdict(float)
for table, n in placed.items():
    for item, y in yields.get(table, {}).items():
        available[item] += n * y


def miss_in(table, item):
    """P(one chest of this table holds none of the item): it misses every roll of every pool; a base table rolled whole is
    its own miss, weighted by how often it is the base picked"""
    f = TABLE_FILES.get(table)
    if not f:
        return 1.0
    chest_miss = 1.0
    for pool in json.loads(f.read_text(encoding="utf-8"))["pools"]:
        rolls = pool.get("rolls", 1)
        r = (rolls["min"] + rolls["max"]) / 2 if isinstance(rolls, dict) else rolls
        total = sum(e.get("weight", 1) for e in pool["entries"])
        per_roll = 0.0   # P(this roll misses)
        for e in pool["entries"]:
            share = e.get("weight", 1) / total
            if e.get("type") == "minecraft:loot_table":
                per_roll += share * miss_in(table_name(e["name"]), item)
            elif e.get("name") == item:
                per_roll += 0.0
            else:
                per_roll += share
        chest_miss *= per_roll ** r
    return chest_miss


def chance_of_one(item):
    """P(at least one) for one player over every bound chest"""
    miss = 1.0
    for table, n in placed.items():
        miss *= miss_in(table, item) ** n
    return 1 - miss


def lootable(item):
    """found by opening or killing something: a table, a drop, the kit - NOT a quest's reward (that is not a way to get
    what the quest itself asks for)"""
    return [x for x in sources.get(item, []) if x.startswith(("table:", "drop:", "kit"))]


def renewable(item):
    return any(x.startswith("drop:") for x in sources.get(item, []))


def raw_need(item, count, need, depth=0):
    """an ask broken down to what must be FOUND. Through an order when the item cannot be looted at all, or when the
    start area's chests do not hold enough of it and an order can make it"""
    o = made_by.get(item)
    short = available.get(item, 0.0) < count and not renewable(item)
    if o and depth < 6 and (not lootable(item) or short):
        batches = -(-count // o["count"])
        for k, v in o["in"].items():
            raw_need(k, v * batches, need, depth + 1)
    else:
        need[item] += count


report["scarcity"] = []
total_need = defaultdict(int)
for q in quests:
    need = defaultdict(int)
    for t in q.get("tasks", []):
        if t.get("type") == "item" and t.get("consume", True):
            raw_need(t["item"], t.get("count", 1), need)
    for item, n in need.items():
        if item.startswith("#"):
            continue
        if not q.get("repeat"):
            total_need[item] += n
        have = available.get(item, 0.0)
        report["scarcity"].append({"quest": q["key"], "item": item, "need": n, "start_area_expects": round(have, 1),
                                   "ratio": round(have / n, 2) if n else None, "renewable": renewable(item)})
unique = {}
for o in orders:
    if o.get("tool"):
        unique[o["tool"]] = f"the tool of order {o['id']}"
for q in quests:
    for t in q.get("tasks", []):
        if t.get("type") == "item" and not t.get("consume", True):
            unique[t["item"]] = unique.get(t["item"], "") + f" shown to {q['key']}"
for i, n in total_need.items():
    if n == 1:
        unique.setdefault(i, "needed once")
report["unique"] = sorted(({"item": i, "why": w.strip(), "chance_one_player_finds_one": round(chance_of_one(i), 3), "renewable": renewable(i),
                            "rewarded": any(x.startswith("reward:") for x in sources.get(i, []))} for i, w in unique.items()), key=lambda x: x["chance_one_player_finds_one"])
report["cumulative"] = sorted(({"item": i, "all_quests_need": n, "start_area_expects": round(available.get(i, 0.0), 1),
                                "ratio": round(available.get(i, 0.0) / n, 2), "renewable": renewable(i)} for i, n in total_need.items()), key=lambda x: x["ratio"])

if "--json" in sys.argv:
    (ROOT / "tools/itemflow.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
print(f"{len(items)} registered items; {len(orders)} orders; {len(quests)} quests; {len(tables)} building tables; {sum(len(v) for v in sources.values())} sources, {sum(len(v) for v in sinks.values())} asks\n")


def show(title, rows, fmt):
    print(f"{title}: {len(rows)}")
    for r in rows:
        print("   " + fmt(r))
    print()


show("ASKED FOR WITH NO SOURCE AT ALL (nobody can finish these)", report["no_source"], lambda r: f"{r['item']:40} asked by {', '.join(r['asked_by'])}")
show("HAS A SOURCE BUT CANNOT BE REACHED (made only by an order whose inputs cannot be had)", report["unreachable"], lambda r: f"{r['item']:40} asked by {', '.join(r['asked_by'])}; sources {r['sources']}")
show("Only ever made at the station (fine if the order's card is earnable)", report["order_only"], lambda r: f"{r['item']:40} {', '.join(r['made_by'])}")
show("SOURCED BUT NEVER ASKED FOR (dead weight)", report["no_sink"], lambda r: f"{r['item']:40} from {', '.join(r['from'])}")
show("Registered but appearing nowhere", report["nowhere"], lambda r: r)
show("REFERENCED BUT NOT REGISTERED (typos)", report["unregistered"], lambda r: f"{r['item']:40} in {', '.join(r['in'])}")
show("Tags asked for (not resolved here)", report["tags"], lambda r: f"{r['tag']:40} {', '.join(r['asked_by'])}")
print("Building tables: share of roll weight nothing asks for")
for name, t in report["tables"].items():
    print(f"   {name:10} {t['entries']:2} entries, weight {t['weight']:3}, dead {int(t['dead_weight_share'] * 100):3}%   {', '.join(x.split(':')[1] for x in t['dead'])}")

print()
print(f"Scarcity - what ONE player expects from the {sum(placed.values())} chests bound in the start area {dict(placed)} (Lootr: per player).")
print("   Chests only: an item bodies or wrecks drop is marked 'drops' (renewable), not short. An order's product counts as its inputs.")
print("   CUMULATIVE - every non-repeatable quest's needs added up, against that one pool:")
for r_ in report["cumulative"]:
    flag = "drops" if r_["renewable"] else ("SHORT" if r_["ratio"] < 1 else ("tight" if r_["ratio"] < 2 else ""))
    print(f"      {r_['item']:34} all quests need {r_['all_quests_need']:3}   expect {r_['start_area_expects']:6}   x{r_['ratio']:<5} {flag}")
print("   NEEDED ONCE - a tool, a thing to show, a single part: the chance ONE player finds at least one in the start area")
for u in report["unique"]:
    flag = "drops" if u["renewable"] else ("rewarded" if u["rewarded"] else ("COIN FLIP" if u["chance_one_player_finds_one"] < 0.8 else ("risky" if u["chance_one_player_finds_one"] < 0.95 else "")))
    print(f"      {u['item']:34} {u['why'][:44]:44} {u['chance_one_player_finds_one'] * 100:5.1f}%  {flag}")
print("   PER QUEST (each against the whole pool, so the cumulative rows above are the truer picture):")
for r_ in sorted(report["scarcity"], key=lambda x: (x["ratio"] is None, x["ratio"])):
    if r_["ratio"] is not None and r_["ratio"] >= 2:
        continue
    flag = "drops" if r_["renewable"] else ("SHORT" if r_["ratio"] < 1 else "tight")
    print(f"      {r_['quest']:16} {r_['item']:34} need {r_['need']:3}  expect {r_['start_area_expects']:6}  x{r_['ratio']:<5} {flag}")

if "--gate" in sys.argv:
    why = []
    for key, label in (("no_source", "asked for with no source"), ("unreachable", "cannot be reached"), ("no_sink", "sourced and never used"), ("unregistered", "not registered")):
        for r_ in report[key]:
            why.append(f"{label}: {r_['item']}")
    for name, t in report["tables"].items():
        for i in t["dead"]:
            why.append(f"dead weight in {name}: {i}")
    for r_ in report["cumulative"]:
        if r_["ratio"] < 1.5 and not r_["renewable"]:   # an expectation EQUAL to the need is a coin flip for a lone player: half again, at least
            why.append(f"the start area is SHORT of {r_['item']}: the quests need {r_['all_quests_need']}, one player expects {r_['start_area_expects']} (wanted: half again)")
    for u in report["unique"]:
        ordered = u["item"] in made_by and reachable(u["item"])   # a tool the station makes from what can be found is not a find at all
        if u["chance_one_player_finds_one"] < 0.9 and not u["renewable"] and not u["rewarded"] and not ordered:
            why.append(f"needed once and a coin flip: {u['item']} {u['chance_one_player_finds_one'] * 100:.0f}%")
    print()
    print("GATE:", "the economy closes" if not why else f"{len(why)} faults")
    for w in why:
        print("   " + w)
    sys.exit(1 if why else 0)
