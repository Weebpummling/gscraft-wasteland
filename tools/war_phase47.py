"""Phase 47, NOTHING LEFT UNDONE (owner, 2026-09-19: "make sure every part of the gameplay that is available is designed and
checked") on the LOCAL server. Needs no player. The completeness audit's findings, held as checks: each was a promise the
game made and did not keep.

1. EVERY strongpoint can be climbed by play, not only the hospital: for each site with no alias, a fresh site refuses the
   marker, presence scouts it, six searches of containers the record holds inside its box loot it, and the marker then
   starts the assault. (The switchyard, the intake works and the turbine hall held no container at all.) No `site set`.
2. Each of them has at least twice the loot goal in containers bound to ITS site table.
3. The med kit is a medicine: it heals, and The Hordes takes it for an infection cure. (Its tooltip said "Heals a wound",
   three quests paid in med kits, and the item did nothing; the notebook promised a cure nothing gave.)
4. No player-facing text names the map wall, the board or a car's bay: gone, or never were. (Tony's cure was on this list until Medical 1 made it true.)
5. Every stage a quest sets is registered; every function a quest or the code runs exists in the datapack; every line a
   survivor is told to say exists.
5b. Every stage a quest WAITS for is set by something (two strikes were gated on stages nothing set).
6. Every order's tool is an item the hand-tools card makes or a table holds, and every card's orders show in its tooltip data.
7. No gscraft errors.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402
import stages as ST  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "mod/src/main/resources"
LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
record = json.loads((ROOT / "tools/chests.json").read_text(encoding="utf-8"))
sites = {}
for f in sorted((RES / "data/gscraft/gscraft_sites").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    if "box" in d and d.get("alias") is None:
        sites[f.stem] = d


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


goal = int(re.search(r"= (\d+)", c("gscraft settings site.loot_goal")).group(1))
c("gscraft director pause")
c("gscraft reset quests")
c("gscraft clock free")

# 1, 2
bad, thin, told = [], [], []
for sid, d in sites.items():
    x0, x1, z0, z1 = d["box"]
    mine = [e for e in record if x0 <= e["x"] <= x1 and z0 <= e["z"] <= z1 and e["table"] == f"sites/{sid}"]
    if len(mine) < 2 * goal:
        thin.append(f"{sid}: {len(mine)} containers of sites/{sid}, the goal is {goal}")
    if len(mine) < goal:
        bad.append(f"{sid}: cannot be looted, {len(mine)} containers")
        continue
    xs, zs = [e["x"] for e in mine], [e["z"] for e in mine]
    c(f"forceload add {min(xs) - 2} {min(zs) - 2} {max(xs) + 2} {max(zs) + 2}")
    time.sleep(4)
    refused = c(f"gscraft site {sid} marker")
    if "assault begins" in refused or "unknown" not in c(f"gscraft site {sid}"):
        bad.append(f"{sid}: a fresh site took the marker [{refused[:50]}]")
    c(f"gscraft site {sid} presence 5")
    if "scouted" not in c(f"gscraft site {sid}"):
        bad.append(f"{sid}: presence did not scout it")
    outs = [c(f"gscraft site {sid} search {e['x']} {e['y']} {e['z']}") for e in mine[:goal]]
    state = c(f"gscraft site {sid}")
    if "looted" not in state:
        bad.append(f"{sid}: {goal} searches did not loot it; the last said [{outs[-1][:60]}]; state [{state[:40]}]")
    started = c(f"gscraft site {sid} marker")
    if "assault begins" not in started:
        bad.append(f"{sid}: the marker after looting: [{started[:70]}]")
    told.append(f"{sid}: {len(mine)} containers, {started[:34]}")
    c(f"gscraft site {sid} set unknown")
    c("kill @e[tag=gs_wave]")
    c(f"forceload remove {min(xs) - 2} {min(zs) - 2} {max(xs) + 2} {max(zs) + 2}")
c("gscraft reset quests")
check(f"every strongpoint climbs by play: refused, scouted, looted by {goal} searches, claimed ({len(sites)} sites)", not bad, bad[:4] or told)
check("each strongpoint holds at least twice the loot goal in containers of its own site table", not thin, thin or f"{len(sites)} sites, at least {2 * goal} each")

# 3
items = c("gscraft items")
med = items[items.find("medicine:"):]
check("the med kit heals and is The Hordes' cure", "med_kit(heals 12, cures a bite: true)" in med, med[:120])

# 4
texts = []
for f in (RES / "assets/gscraft/patchouli_books").rglob("*.json"):
    texts.append((f.name, f.read_text(encoding="utf-8")))
texts.append(("quests.json", (ROOT / "tools/quests.json").read_text(encoding="utf-8")))
texts.append(("en_us.json", (RES / "assets/gscraft/lang/en_us.json").read_text(encoding="utf-8")))
# "Tony cures" and "clinic cures" left this list on 2026-09-19: with Medical 1 they are true (world/Upgrades)
GONE = ("map wall", "the board", "in its bay", "a car carries", "Cars come with", "white banner", "Nothing else does")
stale = [(n, w) for n, t in texts for w in GONE if w.lower() in t.lower()]
check("no player-facing text promises what is gone or never was", not stale, stale or f"{len(texts)} files read")

# 5
quests = json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))["quests"]
lang = json.loads((RES / "assets/gscraft/lang/en_us.json").read_text(encoding="utf-8"))
registry = set(ST.registry())
unreg = sorted({rw["stage"] for q in quests for rw in q["rewards"] if rw.get("type") == "stage"} - registry)
unknown = [s for s in sorted({rw["stage"] for q in quests for rw in q["rewards"] if rw.get("type") == "stage"}) if "UNKNOWN" in c(f"gscraft stage check {s}")]
fn_have = {p.stem for p in Path("G:/GSCraft/server/wasteland-v8/datapacks/gscraft/data/gscraft/functions").glob("*.mcfunction")}
java = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (ROOT / "mod/src/main/java").rglob("*.java"))
fn_want = set(re.findall(r"function gscraft:([a-z0-9_]+)", java + json.dumps(quests)))
says = [f"gscraft.say.{rw['npc']}.{rw['key']}" for q in quests for rw in q["rewards"] if rw.get("type") == "say"]
check("every stage set is registered and known to the server; every function run is in the world's datapack; every line exists",
      not unreg and not unknown and not (fn_want - fn_have) and all(s in lang for s in says),
      f"unregistered {unreg}; unknown to the server {unknown}; functions missing from the world {sorted(fn_want - fn_have)}; lines missing {[s for s in says if s not in lang]}")

# 5b: every stage a quest WAITS for is one something sets. `gun_fired` and `radio_2` gated Fire for effect and Air support and
# nothing in the game set either: two strikes nobody could ever earn (found by reading the quest texts, 2026-09-19)
waits = {t["stage"] for q in quests for t in q["tasks"] if t.get("stage")}
set_by_quest = {rw["stage"] for q in quests for rw in q["rewards"] if rw.get("type") == "stage"}
ladder = {f"{sid}_{rung}" for sid in ST.STRONGPOINTS for rung in ST.RUNGS}
in_code = {w for w in waits if f'"{w}"' in java}
by_pattern = {w for w in waits if w.startswith(("seen_", "note_")) or w == "joined"}
never = sorted(waits - set_by_quest - ladder - in_code - by_pattern)
check("every stage a quest waits for is set by a quest, the site ladder or the code", not never, never or f"{len(waits)} stages waited for")

# 6
orders = json.loads((RES / "data/gscraft/gscraft_recipes/recipes.json").read_text(encoding="utf-8"))["orders"]
made = {o["out"] for o in orders}
tools = {o["tool"] for o in orders if o.get("tool")}
tabled = (ROOT / "tools/loot.py").read_text(encoding="utf-8")
lost = [t for t in tools if t not in made and t.split(":")[1] not in tabled]
check("every order's tool can be made at the station or found in a table", not lost, lost or sorted(t.split(":")[1] for t in tools))

c("gscraft clock online")
c("gscraft director resume")
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
