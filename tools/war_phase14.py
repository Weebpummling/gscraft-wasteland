"""Phase 14 of the enemy work, on the LOCAL server: the synced tactical moves (animation research A2, owner
2026-09-12). Needs a ticking world and no player. Staged on the stone platform at y 200. The clips themselves are
client-side and only an eye can judge them; this checks that the server tells the clients the right move at the
right moment, through the `anim` field of the fighter readout (move#sequence).

1. Going flat plays the dive: a leg wound lays a rifleman down and the byte reads DIVE.
2. A grenade throw plays the throw (the phase 7 setup: target seen at 14 blocks, then a wall between).
3. Rounds into a standing fighter play the flinch (a NoAI body, so it never lies down and every hit shows).
4. A fighter with a wall beside it slides into cover and leans out (the phase 8 cover setup, the target NoAI so
   nothing pins the fighter first).
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
X, Y, Z = -2000, 200, -600
AREA = f"x={X - 70},y={Y - 10},z={Z - 70},dx=140,dy=40,dz=140"
HP = 'Health:2000f,Attributes:[{Name:"minecraft:generic.max_health",Base:2000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "superbwarfare:hand_grenade", "superbwarfare:rgo_grenade"):
        c(f"kill @e[type={t},{AREA}]")


def arena():
    c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
    c(f"fill {X - 40} {Y - 1} {Z - 20} {X + 40} {Y - 1} {Z + 20} minecraft:stone")
    c(f"fill {X - 41} {Y} {Z - 21} {X + 41} {Y + 1} {Z + 21} minecraft:stone hollow")
    c(f"fill {X - 40} {Y} {Z - 20} {X + 40} {Y + 3} {Z + 20} minecraft:air")


def fighter(sel):
    return c(f"gscraft fighter {sel}")


def anim(sel):
    m = re.search(r"anim (\w+)#(\d+)", fighter(sel))
    return (m.group(1), int(m.group(2))) if m else (None, None)


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()
arena()

# 1. the dive on going flat
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["p14d"],GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
a0 = anim("@e[tag=p14d,limit=1]")
c("gscraft wound @e[tag=p14d,limit=1] leg")
time.sleep(1)
a1 = anim("@e[tag=p14d,limit=1]")
pose = re.search(r"pose (\w+)", fighter("@e[tag=p14d,limit=1]"))
check("a leg wound lays the fighter flat and the byte reads the dive", a0[0] == "NONE" and a1[0] == "DIVE" and pose and pose.group(1) == "SWIMMING",
      f"before {a0}, after {a1}, pose {pose.group(1) if pose else '?'}")
clear()

# 2. the throw
c(f'summon gscraft:ruaf_soldier {X + 12} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p14t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 2} {Y} {Z} {{GscraftRank:"NATO Sergeant",Tags:["p14s"]}}')
time.sleep(3)
c(f"fill {X + 4} {Y} {Z - 20} {X + 4} {Y + 3} {Z + 20} minecraft:stone")
throw_seen, grenade_seen = None, False
for i in range(40):
    time.sleep(0.5)
    a = anim("@e[tag=p14s,limit=1]")
    if a[0] == "THROW":
        throw_seen = a
    if count(f"@e[type=superbwarfare:hand_grenade,{AREA}]") > 0:
        grenade_seen = True
    if throw_seen and grenade_seen:
        break
time.sleep(6)
check("a grenade throw plays the throw", throw_seen is not None and grenade_seen, f"throw byte {throw_seen}; grenade seen {grenade_seen}")
clear()
c(f"fill {X + 4} {Y} {Z - 20} {X + 4} {Y + 3} {Z + 20} minecraft:air")

# 3. the flinch: a rifleman fires at a standing NoAI soldier 16 blocks off (no AI, so it never lies down: every hit is a flinch)
c(f'summon gscraft:nato_soldier {X + 16} {Y} {Z} {{NoAI:1b,GscraftRank:"NATO Rifleman",Tags:["p14f"],{HP}}}')
c(f'summon gscraft:ruaf_soldier {X} {Y} {Z} {{GscraftRank:"RUAF Rifleman",GscraftKitIssued:1b,GscraftRole:"RIFLEMAN",GscraftMagazines:9,Tags:["p14r"],{HP},'
  f'HandItems:[{{id:"tacz:modern_kinetic_gun",Count:1b,tag:{{GunId:"tacz:ak47",GunCurrentAmmoCount:30,HasBulletInBarrel:1b}}}},{{}}]}}')
flinch = []
for i in range(16):
    time.sleep(0.5)
    a = anim("@e[tag=p14f,limit=1]")
    if a[0] == "FLINCH":
        flinch.append(a[1])
hp = re.search(r"([\d.]+)f", c("data get entity @e[tag=p14f,limit=1] Health"))
check("rounds into a standing fighter play the flinch, one per hit", len(flinch) >= 1 and (len(set(flinch)) >= 2 or len(flinch) >= 1),
      f"flinch sequences seen {sorted(set(flinch))}; target health {hp.group(1) if hp else '?'}")
clear()

# 4. the slide and the lean: the phase 8 cover setup - a NoAI target at +11, the rifleman at -11 with a wall 5 blocks to its side
c(f"fill {X - 6} {Y} {Z + 4} {X - 6} {Y + 2} {Z + 7} minecraft:stone")
c(f'summon gscraft:ruaf_soldier {X + 11} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p14t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 11} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p14c"],{HP}}}')
seen = {}
trail = []
for i in range(40):
    time.sleep(0.5)
    a = anim("@e[tag=p14c,limit=1]")
    if a[0]:
        seen.setdefault(a[0], set()).add(a[1])
    trail.append(f"{a[0]}#{a[1]}")
slid = len(seen.get("SLIDE", ()))
leans = len(seen.get("LEAN_LEFT", ())) + len(seen.get("LEAN_RIGHT", ()))
check("a fighter with a wall beside it slides into cover and leans out of it",
      slid >= 1 and leans >= 1,
      f"slides {slid}, leans {leans} ({', '.join(k for k in seen if k.startswith('LEAN'))}); trail {' '.join(trail[::2])}")
c(f"fill {X - 6} {Y} {Z + 4} {X - 6} {Y + 2} {Z + 7} minecraft:air")
clear()
c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
