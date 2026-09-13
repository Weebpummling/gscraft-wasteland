"""Phase 26, the building takes (next-steps plan 2026-09-12 §2) on the LOCAL server. Needs a ticking world and no
player; the director's phantom stands in for the player.

1. The five building sites load beside the four strongpoints.
2. The square: unknown until someone is inside (scouted); a clear of site.clear_ticks with the phantom inside and no
   hostile in the box makes it takeable (`square_cleared`); the quest's word - the stage `square_taken`, set by hand
   here - takes it: held, the torch placed by the held function, no site guard, the zone at the square now
   camp_square; the Dead still spawn there (keep_ambient). (Owner: territory capture is tied to quests.)
3. The gatehouse taken by its stage alone (the quest's first word needs no clear) summons Marshall (a named, no-AI
   villager tagged gscraft_npc_marshall).
4. The loss of a building: the counterattack's wave at the approach walks for the gate; five attackers in the
   compound for thirty seconds put the square back to scouted, its stages down; the zone is the front's again; the
   clear alone retakes it (the quest has had its say).
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
GATEHOUSE = "x=-982,y=40,z=-960,dx=32,dy=80,dz=24"
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


clear_ticks = int(re.search(r"site.clear_ticks = (\d+)", c("gscraft settings site.clear_ticks")).group(1))
c("gscraft director pause")
c("gscraft director phantom clear")
c("gscraft clock free")
c("forceload add -1000 -1120 -860 -830")
time.sleep(4)
for s in ("square", "gatehouse", "north", "crossing", "mast"):
    c(f"gscraft site {s} set unknown")
for s in ("square_taken", "gatehouse_taken", "clinic_taken", "crossing_taken", "mast_taken"):
    c(f"gscraft stage remove {s}")
c("kill @e[type=minecraft:villager,tag=gscraft_npc]")
clear_hostiles(POCKET)
c("setblock -940 67 -979 minecraft:air")
c("fill -941 66 -980 -939 66 -978 minecraft:air")
time.sleep(1)

# 1. the sites load
sites = c("gscraft sites")
check("the five building sites load beside the strongpoints", all(s in sites for s in ("square", "gatehouse", "north", "crossing", "mast", "hospital", "switchyard")), sites.replace("\n", " | ")[:200])

# 2. the square's take
before = c("gscraft site square")
c("gscraft director phantom set -940 66 -979")
time.sleep(3)
scouted = c("gscraft site square")
clear_hostiles(POCKET)
mark = LOG.stat().st_size
waited = 0
held = ""
cleared = ""
while waited < clear_ticks / 20 + 25:
    time.sleep(5)
    waited += 5
    clear_hostiles(SQUARE)   # the front's ambient pass is paused, but a stray wanderer would restart the clear
    cleared = c("gscraft stages")
    if "square_cleared" in cleared:
        break
still = c("gscraft site square")   # cleared is takeable, not taken: the quest's word is the stage
c("gscraft stage add square_taken")   # the quest's command reward, by hand until Phase C
time.sleep(3)
held = c("gscraft site square")
stages = c("gscraft stages")
torch = "passed" in c("execute if block -940 67 -979 magnumtorch:diamond_magnum_torch").lower()
guard = count(f"@e[tag=gscraft_siteguard_square,{SQUARE}]")
zone = c("gscraft zone -940 -979")
check("the square: scouted on entry, cleared (takeable) after the clear, held by the quest's stage, its torch, no guard, camp_square",
      ": unknown" in before and ": scouted" in scouted and "square_cleared" in cleared and ": scouted" in still and ": held" in held and "square_taken" in stages and torch and guard == 0 and "camp_square" in zone,
      f"[{before[:24]}] -> [{scouted[:24]}] -> cleared in {waited} s, still [{still[:20]}] -> [{held[:40]}]; torch {torch}; guard {guard}; zone [{zone[:30]}]")
ambient = c("gscraft director ambient -940 66 -979 6")
placed = int((re.search(r"placed (\d+)", ambient) or [0, 0])[1])
soldiers = count(f"@e[type=gscraft:nato_soldier,{SQUARE}]") + count(f"@e[type=gscraft:ruaf_soldier,{SQUARE}]")
check("the Dead still come to the taken square, no soldiers", placed > 0 and soldiers == 0, f"placed {placed}, soldiers {soldiers}")
clear_hostiles(POCKET)

# 3. the gatehouse's survivor
c("gscraft director phantom set -966 70 -947")
time.sleep(3)
waited = 0
held = ""
c("gscraft stage add gatehouse_taken")   # the quest's word without a clear: the first take is the quest's to give
while waited < 30:
    time.sleep(3)
    waited += 3
    held = c("gscraft site gatehouse")
    if ": held" in held:
        break
marshall = count("@e[type=minecraft:villager,tag=gscraft_npc_marshall]")
name = c("data get entity @e[type=minecraft:villager,tag=gscraft_npc_marshall,limit=1] CustomName")
noai = c("data get entity @e[type=minecraft:villager,tag=gscraft_npc_marshall,limit=1] NoAI")
check("the gatehouse taken by the quest's stage alone summons Marshall by its held function", ": held" in held and marshall == 1 and "Marshall" in name and "1b" in noai,
      f"[{held[:40]}] in {waited} s; marshall {marshall}; name [{name[-24:]}]; NoAI [{noai[-4:]}]")
c("gscraft director phantom clear")

# 4. the loss of the square
c("gscraft site square clock 0")
time.sleep(5)
info = c("gscraft site square")
wave = count("@e[tag=gs_wave_square]")
for i in range(5):
    c(f'summon minecraft:zombie {-956 + i} 65 -876 {{NoAI:1b,Tags:["gs_placed","gs_wave","gs_wave_square"]}}')
time.sleep(34)
after = c("gscraft site square")
stages = c("gscraft stages")
zone = c("gscraft zone -940 -979")
check("the square lost: the wave came, five in the compound put it back to scouted, its stages down, the front's ground again",
      "counterattack" in info and wave >= 3 and ": scouted" in after and "square_taken" not in stages and "square_held" not in stages and "square_cleared" not in stages and "camp_square" not in zone,
      f"[{info[:50]}] wave {wave}; after [{after[:30]}]; stages has square_taken {'square_taken' in stages}; zone [{zone[:24]}]")
# the retake: the quest has had its say once, so the clear alone takes it back
c("kill @e[tag=gs_wave]")
c("gscraft director phantom set -940 66 -979")
waited = 0
retaken = ""
while waited < clear_ticks / 20 + 25:
    time.sleep(5)
    waited += 5
    clear_hostiles(SQUARE)
    retaken = c("gscraft site square")
    if ": held" in retaken:
        break
c("gscraft director phantom clear")
check("lost once, the clear alone retakes it", ": held" in retaken, f"[{retaken[:40]}] in {waited} s")

# tidy
c("kill @e[tag=gs_wave]")
for s in ("square", "gatehouse", "north", "crossing", "mast"):
    c(f"gscraft site {s} set unknown")
for s in ("square_taken", "gatehouse_taken"):
    c(f"gscraft stage remove {s}")
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
