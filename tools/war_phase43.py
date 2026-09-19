"""Phase 43, the survivors where the owner puts them (owner, 2026-09-18: "I am just going to manually place them") on the
LOCAL server. Needs no player: the same `/gscraft npc place` the owner runs standing on the spot is driven here with
explicit coordinates. It leaves the world as it found it (records cleared, the datapack's computed layout re-issued).

1. `npc place walker start <x y z yaw>`: exactly one Walker, standing on that block's centre.
2. The Java summon is the datapack's villager: no AI, invulnerable, and ONE offer with maxUses 0 - the placeholder that
   stops the autosave generating trades (a cartographer's map search hung the server, 2026-09-13).
3. The datapack path still ends at the owner's spot: `function gscraft:camp_npcs` summons Walker at tools/camp.py's
   computed spot and the join hook moves him to the saved one; a survivor with no record stays where the function put him.
4. The building slot: saved while its stage is unset without moving anyone; in force once the stage is set; start again
   when the stage is removed.
4b. NO DUPLICATES: placed twice, a copy summoned by hand, respawn and the function re-run, and a stale copy arriving from an
    unloaded chunk - there is always exactly one Walker.
5. `npc clear` gives the computed spot back.
6. No gscraft errors.
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
computed = json.loads((ROOT / "tools/camp_npcs.json").read_text(encoding="utf-8"))
W = computed["buildings"]["walker"]          # tools/camp.py's spot for Walker
MINE = (-828, 71, -895)                      # the "owner's" spot for the test, in the yard
GATE = (-966, 70, -945)                      # a building spot for Marshall, by the gatehouse


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def count(npc, at=None, box=1):
    sel = f"type=minecraft:villager,tag=gscraft_npc_{npc}"
    if at:
        sel += f",x={at[0] - box},y={at[1] - 2},z={at[2] - box},dx={2 * box},dy=4,dz={2 * box}"
    m = re.search(r"count: (\d+)", c(f"execute if entity @e[{sel}]"))
    return int(m.group(1)) if m else 0


c("forceload add -1000 -960 -720 -830")
time.sleep(3)
for npc in ("walker", "marshall"):
    for slot in ("start", "building"):
        c(f"gscraft npc clear {npc} {slot}")
c("gscraft stage remove gatehouse_taken")
c("function gscraft:camp_npcs")
time.sleep(1)

# 1
out = c(f"gscraft npc place walker start {MINE[0]} {MINE[1]} {MINE[2]} 90")
time.sleep(1)
check("place walker start: exactly one Walker, on that spot", "standing there now" in out and count("walker") == 1 and count("walker", MINE) == 1,
      f"[{out[:70]}]; walkers {count('walker')}; on the spot {count('walker', MINE)}")

# 2
sel = "@e[type=minecraft:villager,tag=gscraft_npc_walker,limit=1]"
offers = c(f"data get entity {sel} Offers.Recipes")
noai, inv = c(f"data get entity {sel} NoAI"), c(f"data get entity {sel} Invulnerable")
one_disabled = offers.count("maxUses") == 1 and "maxUses: 0" in offers
check("the Java summon carries one disabled placeholder trade, no AI, invulnerable", one_disabled and noai.endswith("1b") and inv.endswith("1b"),
      f"offers with maxUses {offers.count('maxUses')}, disabled {'maxUses: 0' in offers}; NoAI [{noai[-3:]}] Invulnerable [{inv[-3:]}]")

# 3
c("function gscraft:camp_npcs")
time.sleep(1)
check("the datapack's camp_npcs still ends at the owner's spot; an unplaced survivor stays computed",
      count("walker") == 1 and count("walker", MINE) == 1 and count("walker", (W["x"], W["y"], W["z"])) == 0 and count("michael", (computed["buildings"]["michael"]["x"], computed["buildings"]["michael"]["y"], computed["buildings"]["michael"]["z"])) == 1,
      f"Walker on mine {count('walker', MINE)}, on the computed {count('walker', (W['x'], W['y'], W['z']))}; Michael on his computed {count('michael', (computed['buildings']['michael']['x'], computed['buildings']['michael']['y'], computed['buildings']['michael']['z']))}")

# 4
start_m = computed["start"]["marshall"]
out_b = c(f"gscraft npc place marshall building {GATE[0]} {GATE[1]} {GATE[2]} 180")
time.sleep(1)
unset_ok = "saved; it takes effect when gatehouse_taken is set" in out_b and count("marshall", GATE) == 0
c("gscraft stage add gatehouse_taken")
c("gscraft npc respawn marshall")
time.sleep(1)
set_ok = count("marshall") == 1 and count("marshall", GATE) == 1
c("gscraft stage remove gatehouse_taken")
c("gscraft npc respawn marshall")
time.sleep(1)
back_ok = count("marshall") == 1 and count("marshall", (start_m["x"], start_m["y"], start_m["z"])) == 1
check("the building slot: saved unset, in force with the stage, the start again without it", unset_ok and set_ok and back_ok, f"unset {unset_ok} [{out_b[:60]}]; with the stage {set_ok}; after {back_ok}")

# 4b: NO DUPLICATES (owner, 2026-09-19: "make sure no duplicates will exist"). Four ways a second Walker could appear:
SUMMON = ('summon minecraft:villager {x} {y} {z} {{NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,Tags:["gscraft_npc","gscraft_npc_walker"]}}')
c(f"gscraft npc place walker start {MINE[0]} {MINE[1]} {MINE[2]} 90")
time.sleep(1)
# (a) placed again somewhere else: the first is gone
c(f"gscraft npc place walker start {MINE[0] + 3} {MINE[1]} {MINE[2]} 90")
time.sleep(1)
a = (count("walker"), count("walker", (MINE[0] + 3, MINE[1], MINE[2])))
# (b) a second copy summoned by hand while one stands: refused on arrival
c(SUMMON.format(x=MINE[0] - 6, y=MINE[1], z=MINE[2]))
time.sleep(1)
b = count("walker")
# (c) respawn, and the datapack's function, each run twice: still one
for cmd in ("gscraft npc respawn walker", "gscraft npc respawn", "function gscraft:camp_npcs", "function gscraft:camp_npcs"):
    c(cmd)
    time.sleep(0.5)
time.sleep(1)
cc = count("walker")
# (d) THE REAL ONE: a stale copy in an UNLOADED chunk. It is made while no record and no other Walker exists, its chunk is let
#     go, the owner places Walker, and then the stale chunk loads: the copy must be refused, and must not come back on a reload
FAR = (-2000, 120, -1500)
c("gscraft npc clear walker start")
c("kill @e[type=minecraft:villager,tag=gscraft_npc_walker]")
time.sleep(2)
c(f"forceload add {FAR[0]} {FAR[2]}")
time.sleep(3)
c(f"setblock {FAR[0]} {FAR[1] - 1} {FAR[2]} minecraft:stone")
c(SUMMON.format(x=FAR[0], y=FAR[1], z=FAR[2]))
time.sleep(1)
stale_made = count("walker")
c("save-all flush")
time.sleep(3)
c(f"forceload remove {FAR[0]} {FAR[2]}")
for _ in range(40):                       # until the far chunk has really unloaded and taken the copy with it
    time.sleep(1)
    if count("walker") == 0:
        break
unloaded = count("walker") == 0
c(f"gscraft npc place walker start {MINE[0]} {MINE[1]} {MINE[2]} 90")
time.sleep(1)
c(f"forceload add {FAR[0]} {FAR[2]}")
time.sleep(4)
d_loaded = (count("walker"), count("walker", MINE), count("walker", FAR, 3))
c(f"forceload remove {FAR[0]} {FAR[2]}")
time.sleep(12)
c(f"forceload add {FAR[0]} {FAR[2]}")
time.sleep(4)
d_again = (count("walker"), count("walker", FAR, 3))
listing = c("gscraft npc list")
c(f"setblock {FAR[0]} {FAR[1] - 1} {FAR[2]} minecraft:air")
c(f"forceload remove {FAR[0]} {FAR[2]}")
check("no duplicates: placed twice, summoned by hand, respawned and re-run, and a stale copy from an unloaded chunk - always ONE Walker",
      a == (1, 1) and b == 1 and cc == 1 and stale_made == 1 and unloaded and d_loaded == (1, 1, 0) and d_again == (1, 0) and "COPIES" not in listing,
      f"placed twice {a}; hand-summoned {b}; respawn/function x2 {cc}; stale copy made {stale_made}, unloaded {unloaded}; on its chunk loading (total, at the spot, at the far place) {d_loaded}; after a reload {d_again}")
c("gscraft npc clear walker start")
c("function gscraft:camp_npcs")
time.sleep(1)

# 5
c("gscraft npc clear walker start")
c("gscraft npc clear marshall building")
c("function gscraft:camp_npcs")
time.sleep(1)
lst = c("gscraft npc list")
check("clear gives the computed spot back", count("walker", (W["x"], W["y"], W["z"])) == 1 and count("walker", MINE) == 0 and "walker: start (computed)" in lst,
      f"Walker on the computed {count('walker', (W['x'], W['y'], W['z']))}, on mine {count('walker', MINE)}")

c("forceload remove -1000 -960 -720 -830")
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
