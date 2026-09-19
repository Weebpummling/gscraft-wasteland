"""Phase 31, Act I's loot (system doc 2026-09-13 §7 build 4; loot doc §3, §8) on the LOCAL server. Needs a ticking world.
The five building tables are the mod's data; the compound's and the square's containers are Lootr chests bound to them
by `tools/chests.py --place --apply` (tools/chests.json is the record). What a headless test can prove: each table rolls
its items (`/loot spawn`), the bound containers stand where the record says, and the record covers the four
introductions' hand-in lists. A player's own instanced contents are the owner's in-game check.

1. Each of the five tables rolls its own items and nothing else.
2. The bound containers stand (a sample of the record), at least thirty of them.
3. The tables cover W1, T1, M1 and U1's hand-ins (bolt, nut, bandage, painkillers, wire spool, power cord, water filter,
   circuit board, capacitor, broken radio) and W3's metal scrap.
4. No gscraft errors.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
X, Y, Z = -2000, 200, -600
PAD = f"x={X - 6},y={Y - 2},z={Z - 6},dx=12,dy=8,dz=12"


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def roll(table, n=12):
    """items spawned by n rolls of the table on the test pad, as id -> count"""
    c(f"kill @e[type=minecraft:item,{PAD}]")
    for _ in range(n):
        c(f"loot spawn {X} {Y + 1} {Z} loot gscraft:building/{table}")
    time.sleep(1)
    seen = {}
    for _ in range(60):
        item = c(f"data get entity @e[type=minecraft:item,{PAD},limit=1,sort=nearest] Item.id")
        m = re.search(r'"([a-z_:]+)"', item)
        if not m:
            break
        seen[m.group(1)] = seen.get(m.group(1), 0) + 1
        c(f"kill @e[type=minecraft:item,{PAD},limit=1,sort=nearest]")
    return seen


c(f"forceload add {X - 16} {Z - 16} {X + 16} {Z + 16}")
time.sleep(3)
c(f"fill {X - 6} {Y - 1} {Z - 6} {X + 6} {Y - 1} {Z + 6} minecraft:stone")
c(f"fill {X - 6} {Y} {Z - 6} {X + 6} {Y + 5} {Z + 6} minecraft:air")
TABLES = json.loads((ROOT / "tools/chests.json").read_text(encoding="utf-8"))
expect = {"apartment": "gscraft:canned_goods", "garage": "gscraft:bolt", "workshop": "gscraft:nail", "office": "gscraft:wire_spool", "hospital": "gscraft:syringe"}
rolled = {t: roll(t) for t in expect}
own = all(expect[t] in rolled[t] for t in expect)
# "its own items" means the table's own entries, read from the table: a hand-kept allow-list went stale when the fire
# missions put the mortar's shell in the garage and its three parts in the workshop (f1cf9e0, 2026-09-13; the phase was red
# from then until 2026-09-18), and would flake besides - a weight-2 part shows up in some samples and not others
ENTRIES = {t: {e["name"] for p in json.loads((ROOT / f"mod/src/main/resources/data/gscraft/loot_tables/building/{t}.json").read_text(encoding="utf-8"))["pools"] for e in p["entries"] if e.get("name")} for t in expect}   # an "empty" entry has no name (the garage's second pool, 2026-09-19)
foreign = {t: [k for k in rolled[t] if k not in ENTRIES[t]] for t in expect}
check("each of the five tables rolls its own items", own and not any(foreign.values()), f"{ {t: len(v) for t, v in rolled.items()} } distinct; foreign {foreign}")

# the record's own extent, by area (each under the 256-chunk cap): the old fixed rectangle was the south compound's and,
# after the move, the check passed only because the spawn chunks keep the walled compound loaded - and never saw the clinic
AREAS = [(-902, -922, -718, -833), (-968, -1002, -912, -956), (-968, -1062, -928, -1018)]   # the compound, the junction, the clinic
for a in AREAS:
    c(f"forceload add {a[0]} {a[1]} {a[2]} {a[3]}")
time.sleep(3)
by_area = [[ch for ch in TABLES if a[0] <= ch["x"] <= a[2] and a[1] <= ch["z"] <= a[3]] for a in AREAS]
sample = [ch for group in by_area for ch in group[:: max(1, len(group) // 3)][:3]]   # three from each area, not six from wherever
standing = sum(1 for ch in sample if "passed" in c(f"execute if block {ch['x']} {ch['y']} {ch['z']} #lootr:containers").lower() or "passed" in c(f"execute if block {ch['x']} {ch['y']} {ch['z']} lootr:lootr_chest").lower() or "passed" in c(f"execute if block {ch['x']} {ch['y']} {ch['z']} lootr:lootr_barrel").lower())
for a in AREAS:
    c(f"forceload remove {a[0]} {a[1]} {a[2]} {a[3]}")
check("the bound containers stand, at least thirty", len(TABLES) >= 30 and standing == len(sample) and all(by_area),
      f"record {len(TABLES)} ({[len(g) for g in by_area]} by area); sample {standing} of {len(sample)} standing")

pools = {}
for t in expect:
    d = json.loads((ROOT / f"mod/src/main/resources/data/gscraft/loot_tables/building/{t}.json").read_text(encoding="utf-8"))
    pools[t] = {e["name"] for p in d["pools"] for e in p["entries"] if e.get("name")}   # an "empty" entry has no name
covered = set().union(*pools.values())
need = ["gscraft:bolt", "gscraft:nut", "gscraft:bandage", "gscraft:painkillers", "gscraft:wire_spool", "gscraft:power_cord", "gscraft:water_filter", "gscraft:circuit_board", "gscraft:capacitor", "gscraft:broken_radio", "gscraft:metal_scrap"]
missing = [n for n in need if n not in covered]
check("the tables cover the introductions' hand-ins", not missing, f"missing {missing}")

c(f"kill @e[type=minecraft:item,{PAD}]")
c(f"fill {X - 6} {Y - 1} {Z - 6} {X + 6} {Y + 5} {Z + 6} minecraft:air")
c(f"forceload remove {X - 16} {Z - 16} {X + 16} {Z + 16}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
