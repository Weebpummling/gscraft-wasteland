"""Phase 26, the building takes cut down (system doc 2026-09-13 §6, slice build 0) on the LOCAL server. Needs a ticking
world and no player. A building take is its alias stage and nothing else.

1. The five building sites load beside the four strongpoints.
2. `square_taken` set: the square is held (its stage `square_held` with it), the torch placed by its held function, no
   guard, no clock or counterattack, the zone at the square camp_square; the Dead still come and no soldier
   (keep_ambient, the thin pool). Nothing else moves.
3. `square_taken` unset: the square is lost - unknown, `square_held` down, the zone the front's again; set again, held again.
4. `gatehouse_taken` set: Marshall summoned by its held function (a named, no-AI villager tagged gscraft_npc_marshall).
5. No gscraft errors.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
SQUARE = "x=-966,y=40,z=-1000,dx=52,dy=80,dz=42"
POCKET = "x=-1000,y=40,z=-1120,dx=140,dy=80,dz=290"


def c(cmd, t=90):
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


def clear_hostiles(area):
    for t in ("minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:cave_spider", "gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "gscraft:bloater", "gscraft:rider"):
        c(f"kill @e[type={t},{area}]")
    c(f"kill @e[tag=gs_director,{area}]")
    c(f"kill @e[tag=gs_wave,{area}]")


c("gscraft director pause")
c("gscraft director phantom clear")
c("gscraft clock free")   # the loop ticks with nobody online only on the free clock
c("forceload add -1000 -1120 -860 -830")
time.sleep(4)
for s in ("square_taken", "gatehouse_taken", "clinic_taken", "crossing_taken", "mast_taken"):
    c(f"gscraft stage remove {s}")
time.sleep(1.5)
for s in ("square", "gatehouse", "north", "crossing", "mast"):
    c(f"gscraft site {s} set unknown")
c("kill @e[type=minecraft:villager,tag=gscraft_npc_marshall]")
clear_hostiles(POCKET)
c("setblock -940 67 -979 minecraft:air")
c("fill -941 66 -980 -939 66 -978 minecraft:air")
time.sleep(1)

# 1. the sites load
sites = c("gscraft sites")
check("the five building sites load beside the strongpoints", all(s in sites for s in ("square", "gatehouse", "north", "crossing", "mast", "hospital", "switchyard")), sites.replace("\n", " | ")[:200])

# 2. the take by the stage alone
before = c("gscraft site square")
mark = LOG.stat().st_size
c("gscraft stage add square_taken")
time.sleep(3)
held = c("gscraft site square")
stages = c("gscraft stages")
torch = "passed" in c("execute if block -940 67 -979 magnumtorch:diamond_magnum_torch").lower()
guard = count(f"@e[tag=gscraft_siteguard_square,{SQUARE}]")
zone = c("gscraft zone -940 -979")
quiet = "clock" not in held and "counterattack" not in held and "gs_wave_square" not in c("execute if entity @e[tag=gs_wave_square]")
check("square_taken set: held, its stage, the torch by its function, no guard, no clock, camp_square",
      ": unknown" in before and ": held" in held and "square_held" in stages and torch and guard == 0 and quiet and "camp_square" in zone,
      f"[{before[:20]}] -> [{held[:40]}]; square_held {'square_held' in stages}; torch {torch}; guard {guard}; quiet {quiet}; zone [{zone[:28]}]")
c("kill @e[tag=gs_director]")
time.sleep(1)
ambient = c("gscraft director ambient -940 66 -979 6")
placed = int((re.search(r"placed (\d+)", ambient) or [0, 0])[1])
soldiers = count(f"@e[type=gscraft:nato_soldier,{SQUARE}]") + count(f"@e[type=gscraft:ruaf_soldier,{SQUARE}]")   # the placement lands up to 70 from the point: only the taken box is the thin pool
check("the Dead still come to the taken square, no soldier inside it", placed > 0 and soldiers == 0, f"placed {placed}, soldiers {soldiers}")
clear_hostiles(POCKET)

# 3. the loss by the stage alone, and the retake
c("gscraft stage remove square_taken")
time.sleep(3)
lost = c("gscraft site square")
stages = c("gscraft stages")
zone_lost = c("gscraft zone -940 -979")
c("gscraft stage add square_taken")
time.sleep(3)
again = c("gscraft site square")
check("square_taken unset: lost (unknown, square_held down, the front's ground); set again: held again",
      ": unknown" in lost and "square_held" not in stages and "camp_square" not in zone_lost and ": held" in again,
      f"lost [{lost[:20]}]; square_held {'square_held' in stages}; zone [{zone_lost[:20]}]; again [{again[:20]}]")

# 4. the gatehouse's survivor
c("gscraft stage add gatehouse_taken")
time.sleep(3)
held = c("gscraft site gatehouse")
marshall = count("@e[type=minecraft:villager,tag=gscraft_npc_marshall]")
name = c("data get entity @e[type=minecraft:villager,tag=gscraft_npc_marshall,limit=1] CustomName")
noai = c("data get entity @e[type=minecraft:villager,tag=gscraft_npc_marshall,limit=1] NoAI")
check("gatehouse_taken set: Marshall summoned by its held function", ": held" in held and marshall == 1 and "Marshall" in name and "1b" in noai,
      f"[{held[:30]}]; marshall {marshall}; name [{name[-24:]}]; NoAI [{noai[-4:]}]")

# tidy
for s in ("square_taken", "gatehouse_taken"):
    c(f"gscraft stage remove {s}")
time.sleep(2)
for s in ("square", "gatehouse", "north", "crossing", "mast"):
    c(f"gscraft site {s} set unknown")
c("kill @e[type=minecraft:villager,tag=gscraft_npc_marshall]")
c("setblock -940 67 -979 minecraft:air")
c("fill -941 66 -980 -939 66 -978 minecraft:air")
c("setblock -966 70 -947 minecraft:air")
c("fill -967 69 -948 -965 69 -946 minecraft:air")
clear_hostiles(POCKET)
c("gscraft clock online")
c("forceload remove -1000 -1120 -860 -830")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
