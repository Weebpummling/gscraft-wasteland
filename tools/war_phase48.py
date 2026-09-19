"""Phase 48, EVERY ORDER RUNS (the completeness audit, 2026-09-19) on the LOCAL server. Needs no player. Phase 32 proves
the station with a handful of orders; the loot design added five and gave four more a tool, and none of those had ever been
started. Here every order in recipes.json is loaded into a real station - its card, its tool, its inputs (a tag as one
concrete item) - and must START; without its tool it must say what it needs; and the quick ones must deliver their output.

1. Every order starts when its card, tool and inputs are in the station.
2. Every order that wants a tool refuses without it and names the tool.
3. Every quick order delivers: the output slot holds what the order says, in the count it says.
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
X, Y, Z = -2000, 210, -600
P = f"{X} {Y} {Z}"
TAGS = {"#minecraft:wool": "minecraft:white_wool", "#minecraft:sand": "minecraft:sand", "#minecraft:planks": "minecraft:oak_planks"}
rec = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_recipes/recipes.json").read_text(encoding="utf-8"))
orders, classes = rec["orders"], rec["classes"]


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def show():
    return c(f"gscraft station show {P}")


def load(o, with_tool=True):
    # a FRESH station for every load: `station clear` empties the slots and leaves a running order running, so after the
    # first two-minute order nothing else could start (the phase's first run, 2026-09-19)
    c(f"setblock {P} minecraft:air")
    c(f"setblock {P} gscraft:station")
    c(f"gscraft station bind {P} Alice")
    if o.get("card"):
        c(f"gscraft station load {P} 0 gscraft:{o['card']}")
    if o.get("tool") and with_tool:
        c(f"gscraft station load {P} 1 {o['tool']}")
    for slot, (item, n) in enumerate(o["in"].items(), start=3):
        c(f"gscraft station load {P} {slot} {TAGS.get(item, item)} {n}")


c(f"forceload add {X - 16} {Z - 16} {X + 16} {Z + 16}")
time.sleep(3)
c(f"fill {X - 3} {Y - 1} {Z - 3} {X + 3} {Y - 1} {Z + 3} minecraft:stone")
c(f"fill {X - 3} {Y} {Z - 3} {X + 3} {Y + 3} {Z + 3} minecraft:air")
c(f"setblock {P} gscraft:station")
time.sleep(1)
c(f"gscraft station bind {P} Alice")

started, refused, delivered = [], [], []
for o in orders:
    if o.get("tool"):
        load(o, with_tool=False)
        time.sleep(1.5)
        s = show()
        tool_name = o["tool"].split(":")[1].replace("_", " ")
        if f"order {o['id']}" in s or tool_name not in s.lower():
            refused.append(f"{o['id']}: without its {tool_name} the station said [{s[:80]}]")
    load(o)
    s = ""
    for _ in range(8):
        time.sleep(1)
        s = show()
        if f"order {o['id']}" in s:
            break
    if f"order {o['id']}" not in s:
        started.append(f"{o['id']}: [{s[:110]}]")
        continue
    if o["class"] == "quick":
        out_name = o["out"]
        got = ""
        for _ in range(classes["quick"] + 12):
            time.sleep(1)
            got = show()
            if f" 2={out_name}x{o['count']}" in got:   # slot 2 is the output: `<slot>=<id>x<count>` (StationEvents.show)
                break
        if f" 2={out_name}x{o['count']}" not in got:
            delivered.append(f"{o['id']}: wanted {o['count']} {out_name}, the station shows [{got[:140]}]")
c(f"gscraft station clear {P}")
quick = [o for o in orders if o["class"] == "quick"]
check(f"every order starts with its card, tool and inputs ({len(orders)} orders)", not started, started[:5] or "all of them")
check(f"every order that wants a tool refuses without it and names it ({sum(1 for o in orders if o.get('tool'))} orders)", not refused, refused[:5] or "all of them")
check(f"every quick order delivers what it says ({len(quick)} orders)", not delivered, delivered[:5] or "all of them")

c(f"setblock {P} minecraft:air")
c(f"fill {X - 3} {Y - 1} {Z - 3} {X + 3} {Y - 1} {Z + 3} minecraft:air")
c(f"forceload remove {X - 16} {Z - 16} {X + 16} {Z + 16}")
r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
errs = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not errs, f"error lines {len(errs)}")
for l in errs[:6]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
