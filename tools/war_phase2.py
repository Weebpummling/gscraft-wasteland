"""Phase 2 of the enemy review, on the LOCAL server (127.0.0.1). Needs a ticking world
(hordes-common.toml pauseEventServer = false locally) and no player.

1. The faction data loaded: /gscraft factions lists all six.
2. The Dead hunt soldiers: a zombie closes on a NoAI RUAF soldier and hurts it (the soldier cannot shoot back).
3. The Dead hunt Scavengers: the same against a NoAI Scavenger.
4. A Scavenger kills the Dead: a live Scavenger against two zombies.
5. The armies hunt Scavengers: a soldier shoots a NoAI Scavenger and takes nothing back.
6. The Converted: a NoAI soldier killed by zombies rises as a zombie tagged gs_converted, wearing its helmet.
7. A Scavenger ignores a player until struck: needs a player - in person, not here.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
X, Z = -2000, -600
AREA = f"x={X},z={Z},distance=..60"
ZOMBIE = 'minecraft:zombie ~ ~ ~ {Tags:["gs_placed","p2"],ArmorItems:[{},{},{},{id:"minecraft:leather_helmet",Count:1b}]}'
CLEAR = ["minecraft:zombie", "minecraft:husk", "gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger"]

r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []


def c(cmd, t=30):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def health(sel):
    m = re.search(r"([\d.]+)f?\s*$", c(f"data get entity {sel} Health"))
    return float(m.group(1)) if m else None


def at(dx, dz):
    return f"execute positioned {X + dx} 0 {Z + dz} positioned over motion_blocking_no_leaves run "


def clear():
    for t in CLEAR:
        c(f"kill @e[type={t},{AREA}]")
    time.sleep(1)


def check(name, ok, detail):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


g0 = int(re.search(r"(\d+)\s*$", c("time query gametime")).group(1))
time.sleep(3)
g1 = int(re.search(r"(\d+)\s*$", c("time query gametime")).group(1))
print(f"world ticking: {g1 - g0 > 30} ({g0} -> {g1})")

out = c("gscraft factions")
names = sorted(set(re.findall(r"(\w+): players", out)))
check("faction data loaded", set(names) >= {"nato", "ruaf", "scavengers", "dead", "camp", "machines"}, names)

c(f"forceload add {X - 60} {Z - 60} {X + 60} {Z + 60}", 60)
time.sleep(5)
clear()

# 2. the Dead hunt soldiers
c(at(0, 0) + 'summon gscraft:ruaf_soldier ~ ~ ~ {NoAI:1b,Tags:["p2s"]}')
c(at(8, 0) + "summon " + ZOMBIE)
time.sleep(15)
hp = health("@e[tag=p2s,limit=1]")
alive = count("@e[tag=p2s]")
check("the Dead hunt soldiers", alive == 0 or (hp is not None and hp < 24.0), f"soldier alive {alive}, health {hp}")
clear()

# 3. the Dead hunt Scavengers
c(at(0, 0) + 'summon gscraft:scavenger ~ ~ ~ {NoAI:1b,Tags:["p2v"]}')
c(at(8, 0) + "summon " + ZOMBIE)
time.sleep(15)
hp = health("@e[tag=p2v,limit=1]")
alive = count("@e[tag=p2v]")
check("the Dead hunt Scavengers", alive == 0 or (hp is not None and hp < 20.0), f"scavenger alive {alive}, health {hp}")
clear()

# 4. a Scavenger goes after the Dead on its own. The zombies have no AI, so any damage they take is the Scavenger
# starting the fight; they wear a helmet so the sun cannot kill them instead. The loadout is pinned
# (GscraftKitIssued) so a rank roll cannot decide the test. A lone melee Scavenger against two LIVE zombies loses
# on Hard - measured 2026-09-10 - which is balance, not wiring.
HELMET = 'ArmorItems:[{},{},{},{id:"minecraft:leather_helmet",Count:1b}]'
NOAI_ZOMBIE = 'minecraft:zombie ~ ~ ~ {NoAI:1b,Tags:["gs_placed","p2"],' + HELMET + '}'


def pinned_scavenger(hand, tag):
    return ('summon gscraft:scavenger ~ ~ ~ {Tags:["' + tag + '"],GscraftKitIssued:1b,HandItems:['
            + hand + ',{}]}')


c(at(0, 0) + pinned_scavenger('{id:"superbwarfare:crowbar",Count:1b}', "p2k"))
c(at(7, 3) + "summon " + NOAI_ZOMBIE)
c(at(7, -3) + "summon " + NOAI_ZOMBIE)
z = 2
for _ in range(10):
    time.sleep(3)
    z = count(f"@e[type=minecraft:zombie,tag=p2,{AREA}]")
    if z == 0:
        break
check("a Scavenger starts the fight with the Dead", z == 0, f"zombies left {z} of 2 after up to 30s")
clear()

# 4b. the Scrapper's issued knife lands a blow (the cardboard sword it replaced dealt none)
c(at(0, 0) + pinned_scavenger('{id:"superbwarfare:knife",Count:1b}', "p2j"))
c(at(5, 0) + "summon " + NOAI_ZOMBIE)
hz = None
for _ in range(6):
    time.sleep(3)
    hz = health(f"@e[type=minecraft:zombie,tag=p2,{AREA},limit=1]")
    if hz is None or hz < 20.0:
        break
check("the Scrapper's knife deals damage", hz is None or hz < 20.0, f"zombie health {hz}")
clear()

# 5. the armies hunt Scavengers (owner, 2026-09-10); a Scavenger only fights a soldier that struck it, so the
#    NoAI Scavenger here never answers and the soldier stays whole
c(at(-6, 0) + 'summon gscraft:nato_soldier ~ ~ ~ {Tags:["p2n"]}')
c(at(6, 0) + 'summon gscraft:scavenger ~ ~ ~ {NoAI:1b,Tags:["p2m"]}')
time.sleep(15)
hn, hm = health("@e[tag=p2n,limit=1]"), health("@e[tag=p2m,limit=1]")
alive = count("@e[tag=p2m]")
check("a soldier hunts a Scavenger", (alive == 0 or (hm is not None and hm < 20.0)) and hn == 24.0, f"NATO {hn}, Scavenger alive {alive}, health {hm}")
clear()

# 6. the Converted
c(at(0, 0) + 'summon gscraft:ruaf_soldier ~ ~ ~ {NoAI:1b,Tags:["p2c"],Health:4.0f}')
for dx in (5, -5, 0):
    c(at(dx, 5) + "summon " + ZOMBIE)
risen = 0
for _ in range(15):
    time.sleep(3)
    risen = count(f"@e[type=minecraft:zombie,tag=gs_converted,{AREA}]")
    if risen:
        break
helmet = c(f"data get entity @e[type=minecraft:zombie,tag=gs_converted,{AREA},limit=1] ArmorItems[3].id") if risen else ""
check("the Converted rise in their kit", risen == 1 and ("6b47" in helmet or "fast_helmet" in helmet),
      f"risen {risen}, helmet {helmet.split('data: ')[-1] if helmet else '-'}")
clear()

c(f"forceload remove {X - 60} {Z - 60} {X + 60} {Z + 60}", 60)
r.close()

log = LOG.read_text(encoding="utf-8", errors="replace")
bad = [l for l in log.splitlines() if "gscraft" in l.lower() and re.search(r"ERROR|invalid|not registered|Exception", l)]
check("no gscraft errors or missing kit items in the log", not bad, f"{len(bad)} lines")
for l in bad[:8]:
    print("     ", l[:180])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
