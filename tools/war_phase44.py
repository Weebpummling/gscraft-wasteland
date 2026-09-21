"""Phase 44, THE CHAIN PLAYED (slice review 2026-09-19: every build had a green phase and the slice could not be finished,
because each phase proved its build with the operator's hand on the scale) on the LOCAL server. Needs no player.

THE RULE OF THIS PHASE: it never moves the game with an operator's command. No `/gscraft site <id> set`, no
`/gscraft stage add`. It may only do what stands in for a player's feet and hands, through the same code the events call:
    /gscraft site <id> presence <s>     a player on foot inside the box for s seconds      (SitePlay.presence)
    /gscraft site <id> search <pos>     a player opening the Lootr container at pos         (SitePlay.searched)
    /gscraft site <id> marker           a player planting the claim marker                  (Loop.claim, as the item does)
    /function gscraft:gate_close        the reward command the quest book runs for R0
Resets (`/gscraft reset quests`) and clocks (`clock free`, `site <id> clock`) are the test's bench, not the game's moves.

1. A fresh hospital is unknown, and the marker is refused there: the wall the review found.
2. Presence short of the time does nothing; the full time scouts it, and sets the stage the quest watches.
3. Searching: a block that is not a container is refused; a container outside the box is refused; six different
   containers in the hospital loot it, a repeat does not count, and the stage is set.
4. The marker now starts the assault.
5. Nobody inside at the end: lost, the site stays looted, and THE MARKER LIES WHERE IT STOOD to be planted again.
6. The gate: R0's reward bars the opening with sandbags and a fence gate; the quest reset opens it again, takes the
   hospital back to unknown and forgets the searches.
7. What a player needs is in the data the game loaded: canned goods can be eaten; the marker's order is five minutes;
   Marshall's three hospital quests watch the three stages; R0 runs the gate.
8. The kit is a Superb Warfare Glock 17, loaded, and 34 rounds of what bodies and rooms give; a death gives back the pistol
   and the notebook and nothing else.
9. The gate's quest gives the rifle, the junction's the vest and plates; the server knows the items.
10. No gscraft errors.
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
hosp = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_sites/hospital.json").read_text(encoding="utf-8"))
X0, X1, Z0, Z1 = hosp["box"]
AX, AZ = hosp["anchor"]
record = json.loads((ROOT / "tools/chests.json").read_text(encoding="utf-8"))
inside = [c for c in record if X0 <= c["x"] <= X1 and Z0 <= c["z"] <= Z1]
outside = next(c for c in record if not (X0 <= c["x"] <= X1 and Z0 <= c["z"] <= Z1))


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def state():
    return c("gscraft site hospital")


def stage(name):
    return name in c("gscraft stages")


if len(inside) < 7:
    print(f"  the record holds {len(inside)} containers inside the hospital's box: run tools/chests.py <world> --place --apply first")
    sys.exit(2)

c("gscraft director pause")
c("gscraft reset quests")
c(f"forceload add {X0} {Z0} {X0 + 120} {Z1}")
c(f"forceload add {X0 + 121} {Z0} {X1} {Z1}")
c(f"forceload add {outside['x'] - 8} {outside['z'] - 8} {outside['x'] + 8} {outside['z'] + 8}")
c("forceload add -840 -916 -826 -908")
time.sleep(4)

# 1
refused = c("gscraft site hospital marker")
check("a fresh hospital is unknown and the marker is refused", "unknown" in state() and ("scouted" in refused or "refused" in refused.lower()) and "assault begins" not in refused, f"[{state()[:50]}] marker: [{refused[:70]}]")

# 2
short = c("gscraft site hospital presence 2")
still = "unknown" in state()
full = c("gscraft site hospital presence 3")
check("presence short of the time does nothing; the full time scouts it and sets the stage", still and "scouted" in state() and stage("hospital_scouted"),
      f"[{short[:40]}] then [{full[:40]}]; state [{state()[:40]}]; stage set {stage('hospital_scouted')}")

# 3
floor = c(f"gscraft site hospital search {inside[0]['x']} {inside[0]['y'] - 1} {inside[0]['z']}")
away = c(f"gscraft site hospital search {outside['x']} {outside['y']} {outside['z']}")
outs = [c(f"gscraft site hospital search {ch['x']} {ch['y']} {ch['z']}") for ch in inside[:5]]
repeat = c(f"gscraft site hospital search {inside[0]['x']} {inside[0]['y']} {inside[0]['z']}")
before_sixth = "scouted" in state() and not stage("hospital_looted")
sixth = c(f"gscraft site hospital search {inside[5]['x']} {inside[5]['y']} {inside[5]['z']}")
check("searching: not a container refused, outside the box refused, a repeat not counted, the sixth loots it",
      "nothing to search" in floor and "no strongpoint" in away and "already" in repeat and before_sixth and "looted" in state() and stage("hospital_looted"),
      f"floor [{floor[:34]}] away [{away[:30]}] fifth [{outs[-1][:30]}] repeat [{repeat[:36]}] sixth [{sixth[:34]}]; state [{state()[:36]}]")

# 4
c("gscraft clock free")
c(f"kill @e[type=minecraft:item,x={AX - 12},y=-64,z={AZ - 12},dx=24,dy=384,dz=24]")   # a marker another phase's lost assault left lying (35 loses one too)
started = c("gscraft site hospital marker")
check("the marker now starts the assault", "assault begins" in started and "assault" in state(), f"[{started[:80]}]")

# 5
c("gscraft site hospital clock 4")
lost = False
for _ in range(20):
    time.sleep(1)
    if "assault" not in state():
        lost = True
        break
time.sleep(1)
m = re.search(r"count: (\d+)", c(f"execute if entity @e[type=minecraft:item,nbt={{Item:{{id:\"gscraft:claim_marker\"}}}},x={AX - 12},y=-64,z={AZ - 12},dx=24,dy=384,dz=24]"))
fallen = int(m.group(1)) if m else 0
check("nobody inside: lost, the site stays looted, and the marker lies where it stood", lost and "looted" in state() and fallen == 1, f"lost {lost}; state [{state()[:40]}]; markers on the ground {fallen}")
c(f"kill @e[type=minecraft:item,x={AX - 12},y=-64,z={AZ - 12},dx=24,dy=384,dz=24]")

# 6
c("function gscraft:gate_close")
time.sleep(1)
bags = sum("passed" in c(f"execute if block {x} {y} -912 superbwarfare:sandbag") for x in (-835, -834, -831, -830) for y in (71, 72))
gates = sum("passed" in c(f"execute if block {x} 71 -912 minecraft:oak_fence_gate") for x in (-833, -832))
reset = c("gscraft reset quests")
time.sleep(1)
opened = sum("passed" in c(f"execute if block {x} 71 -912 minecraft:air") for x in (-835, -833, -832, -831, -830))
again = c("gscraft site hospital presence 5")
forgot = c(f"gscraft site hospital search {inside[0]['x']} {inside[0]['y']} {inside[0]['z']}")
check("the gate: eight sandbags and two fence gates; the reset opens it, and the hospital starts over with its searches forgotten",
      bags == 8 and gates == 2 and opened == 5 and "scouted" in again and "1 of" in forgot, f"sandbags {bags}, gates {gates}; after the reset open cells {opened} of 5; [{again[:30]}] [{forgot[:34]}]")
c("gscraft reset quests")

# 7
items = c("gscraft items")
orders = {o["id"]: o for o in json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_recipes/recipes.json").read_text(encoding="utf-8"))["orders"]}
quests = {q["key"]: q for q in json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))["quests"]}
watch = {k: [t.get("stage") for t in quests[k]["tasks"]] for k in ("H1", "H2", "H3") if k in quests}
gate_reward = any("gate_close" in json.dumps(rw) for rw in quests["R0"]["rewards"])
check("canned goods can be eaten; the marker's order is five minutes; Marshall's three quests watch the three stages; R0 runs the gate",
      "canned_goods(6)" in items and orders["claim_marker"]["class"] == "equipment" and watch == {"H1": ["hospital_scouted"], "H2": ["hospital_looted"], "H3": ["hospital_held"]} and gate_reward,
      f"[{items[items.find('edible'):][:40]}]; marker class {orders['claim_marker']['class']}; {watch}; gate reward {gate_reward}")

# 8: the fight and the death (owner's decisions, 2026-09-19: Superb Warfare for the player's guns; the pistol again on respawn)
kit = c("gscraft kit")
back = c("gscraft kit respawn")
drops = json.dumps([json.loads(f.read_text(encoding="utf-8")) for f in (ROOT / "mod/src/main/resources/data/gscraft/gscraft_drops").glob("*.json")])
tables = {t: (ROOT / f"mod/src/main/resources/data/gscraft/loot_tables/building/{t}.json").read_text(encoding="utf-8") for t in ("apartment", "office", "garage")}
check("the kit's gun is Superb Warfare's, loaded, with rounds the world gives back; no TACZ in it; a death returns the pistol and the notebook",
      "superbwarfare:glock_17" in kit and "Ammo:17" in kit and "superbwarfare:ak_47" in kit and "Ammo:30" in kit and "tacz" not in kit
      and sum(int(n) for n in re.findall(r"(\d+) superbwarfare:rifle_ammo", kit)) == 150 and sum(int(n) for n in re.findall(r"(\d+) superbwarfare:handgun_ammo", kit)) == 68
      # the respawn is the BASIC GEAR (owner, 2026-09-20): both guns loaded, 60 rifle and 17 pistol rounds, the vest, the helmet, a bandage, the notebook - never the station
      and "superbwarfare:glock_17" in back and "superbwarfare:ak_47" in back and "patchouli:guide_book" in back and "60 superbwarfare:rifle_ammo" in back and "17 superbwarfare:handgun_ammo" in back
      and "ge_helmet_m_35" in back and "msv_chest" in back and "station" not in back
      and drops.count("superbwarfare:handgun_ammo") >= 4 and all("superbwarfare:handgun_ammo" in v for v in tables.values()),
      f"kit [{kit[:150]}]; back [{back[:120]}]; drop rules with rounds {drops.count('superbwarfare:handgun_ammo')}; tables with rounds {[t for t, v in tables.items() if 'handgun_ammo' in v]}")

# 9: one step up before each fight (slice review, step 2): the rifle with the gate, the vest with the junction - and the game knows the items
step = {"R0": ["superbwarfare:rifle_ammo"], "square": ["superbwarfare:ru_chest_6b43", "superbwarfare:armor_plate"]}
missing = [f"{k}:{i}" for k, items in step.items() for i in items if i not in json.dumps(quests[k]["rewards"])]
unknown = [i for items in step.values() for i in items + ["superbwarfare:glock_17", "superbwarfare:handgun_ammo", "superbwarfare:ak_47", "superbwarfare:ge_helmet_m_35", "dragonrise_reforge:msv_chest"] if "Unknown item" in c(f"clear @a {i} 0")]
check("the gate's quest gives the rifle and its rounds, the junction's the vest and two plates; the server knows every one of those items",
      not missing and not unknown, f"missing from the rewards {missing}; unknown to the server {unknown}")

c("gscraft clock online")
c("forceload remove all")
c("gscraft director resume")
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
