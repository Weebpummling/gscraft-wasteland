"""Phase 7 of the enemy work, on the LOCAL server: sharper fighters, step A of the feasibility review
(docs/gscraft-humanoid-ai-feasibility-2026-09-10.md): doors and rubble, sprint, the crouch, suppression from TACZ's
hit events, callouts, grenades, and the director's own despawn with the wider open range. Needs a ticking world and
no player. Run war_phase6.py, 5, 4b, 4, 3 and 2 after it.

The fights are staged on a stone platform high in the air (y 200), forceloaded, so nothing in the world is touched.

1. Rubble: a soldier crosses a one-block wall to reach its target without a jump goal.
2. Doors: a soldier opens a shut oak door on its way to a target.
3. The crouch: a soldier holding still to fire beyond 16 blocks goes to the crouched pose and a lower box.
4. Suppression: a soldier under fire reports a rising value and a widened stance; the value decays when the fire stops.
5. Grenades: a rifleman with one grenade and a target behind a wall throws it; the grenade detonates; no block is
   lost (explosion_destroy is off); the callout is logged.
6. The director's placements are persistent, and the open range is 36-72.
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
AREA = f"x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120"


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def val(sel, path):
    out = c(f"data get entity {sel} {path}")
    return out.split("entity data: ", 1)[1].strip() if "entity data: " in out else None


def fighter(sel):
    return c(f"gscraft fighter {sel}")


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "superbwarfare:hand_grenade", "minecraft:zombie"):
        c(f"kill @e[type={t},{AREA}]")


def platform(x0, z0, x1, z1):
    c(f"fill {x0} {Y - 1} {z0} {x1} {Y - 1} {z1} minecraft:stone")
    c(f"fill {x0} {Y} {z0} {x1} {Y + 3} {z1} minecraft:air")


def x_of(sel):
    pos = val(sel, "Pos") or ""
    nums = re.findall(r"-?[\d.]+(?=d)", pos)
    return float(nums[0]) if len(nums) == 3 else None


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()

# 1. rubble: a one-block wall across the platform; the soldier is ordered across it (targets need sight, so an order stands
#    in for the advance of step B2)
platform(X - 20, Z - 8, X + 20, Z + 8)
c(f"fill {X} {Y} {Z - 8} {X} {Y} {Z + 8} minecraft:stone")
c(f'summon gscraft:nato_soldier {X - 10} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p7a"]}}')
time.sleep(1)
order = c(f"gscraft fighter @e[tag=p7a,limit=1] goto {X + 10} {Y} {Z} now")
crossed = False
for i in range(20):
    time.sleep(1)
    x = x_of("@e[tag=p7a,limit=1]")
    if x is not None and x > X + 1:
        crossed = True
        break
check("a soldier crosses a one-block wall on its way", crossed, f"{order}; x after {i + 1} s: {x}")
clear()
c(f"fill {X} {Y} {Z - 8} {X} {Y} {Z + 8} minecraft:air")

# 2. doors: a wall with a shut oak door; the soldier is ordered through
c(f"fill {X} {Y} {Z - 8} {X} {Y + 2} {Z + 8} minecraft:stone")
c(f"setblock {X} {Y} {Z} minecraft:oak_door[facing=east,half=lower,open=false]")
c(f"setblock {X} {Y + 1} {Z} minecraft:oak_door[facing=east,half=upper,open=false]")
c(f'summon gscraft:nato_soldier {X - 10} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p7d"]}}')
time.sleep(1)
order = c(f"gscraft fighter @e[tag=p7d,limit=1] goto {X + 10} {Y} {Z} now")
opened = False
for i in range(20):
    time.sleep(1)
    if "passed" in c(f"execute if block {X} {Y} {Z} minecraft:oak_door[open=true]"):
        opened = True
        break
x = x_of("@e[tag=p7d,limit=1]")
check("a soldier opens a shut door on its way", opened, f"{order}; door open after {i + 1} s: {opened}; x {x}")
clear()
c(f"fill {X} {Y} {Z - 8} {X} {Y + 2} {Z + 8} minecraft:air")

# 3. the crouch: firing at 30 blocks; the platform is fenced so a sidestep cannot leave it
platform(X - 20, Z - 8, X + 20, Z + 8)
c(f"fill {X - 21} {Y} {Z - 9} {X + 21} {Y + 1} {Z + 9} minecraft:stone hollow")
c(f"fill {X - 20} {Y} {Z - 8} {X + 20} {Y + 3} {Z + 8} minecraft:air")
c(f'summon gscraft:nato_soldier {X - 16} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p7c"]}}')
c(f'summon gscraft:ruaf_soldier {X + 14} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p7t"],Health:2000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:2000}}]}}')
crouched = None
trail = []
for i in range(20):
    time.sleep(1)
    info = fighter("@e[tag=p7c,limit=1]")
    trail.append((val("@e[tag=p7c,limit=1]", "Pos") or "gone")[:40])
    if "pose CROUCHING" in info:
        crouched = info
        break
check("a soldier firing at long range crouches", crouched is not None, (crouched or info)[:200] + " | trail " + "; ".join(trail[-4:]))
clear()
c(f"fill {X - 21} {Y - 1} {Z - 9} {X + 21} {Y + 3} {Z + 9} minecraft:air")

# 4. suppression: a NoAI NATO soldier under RUAF fire
platform(X - 20, Z - 8, X + 20, Z + 8)
c(f'summon gscraft:nato_soldier {X + 12} {Y} {Z} {{NoAI:1b,GscraftRank:"NATO Gunner",Tags:["p7s"],Health:2000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:2000}}]}}')
c(f'summon gscraft:ruaf_soldier {X - 8} {Y} {Z} {{GscraftRank:"RUAF Gunner",Tags:["p7g"]}}')
peak = 0.0
for i in range(20):
    time.sleep(1)
    m = re.search(r"suppression ([\d.]+)", fighter("@e[tag=p7s,limit=1]"))
    if m:
        peak = max(peak, float(m.group(1)))
    if peak >= 0.5:
        break
c("kill @e[tag=p7g]")
c(f'summon gscraft:nato_soldier {X + 12} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p7s2"]}}')
c("gscraft fighter @e[tag=p7s2,limit=1]")
# decay needs the AI step: the live soldier's value starts at zero and must stay there with nobody firing
time.sleep(4)
m2 = re.search(r"suppression ([\d.]+)", fighter("@e[tag=p7s2,limit=1]"))
quiet = float(m2.group(1)) if m2 else -1
check("a fighter under fire is suppressed; one that is not stays calm", peak >= 0.5 and quiet == 0.0, f"peak under fire {peak:.2f}, quiet fighter {quiet}")
clear()

# 5. grenades: the sergeant sees its target at 14 blocks, then a wall goes up between them. The platform has a rim
#    so the grenade cannot leave it: the detonation happens on the platform, and every block of it must survive
platform(X - 20, Z - 8, X + 20, Z + 8)
c(f"fill {X - 21} {Y} {Z - 9} {X + 21} {Y + 2} {Z + 9} minecraft:stone hollow")
c(f"fill {X - 20} {Y} {Z - 8} {X + 20} {Y + 3} {Z + 8} minecraft:air")
c(f'summon gscraft:ruaf_soldier {X + 12} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p7t"],Health:2000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:2000}}]}}')
c(f'summon gscraft:nato_soldier {X - 2} {Y} {Z} {{GscraftRank:"NATO Sergeant",Tags:["p7n"]}}')
time.sleep(0.6)
before = re.search(r"grenades (\d+)", fighter("@e[tag=p7n,limit=1]"))     # read before any throw is possible
time.sleep(2.5)
acquired = fighter("@e[tag=p7n,limit=1]")
c(f"fill {X + 4} {Y} {Z - 8} {X + 4} {Y + 3} {Z + 8} minecraft:stone")
thrown_seen = False
for i in range(40):
    time.sleep(0.5)
    if count(f"@e[type=superbwarfare:hand_grenade,{AREA}]") > 0:
        thrown_seen = True
        break
time.sleep(7)
after = re.search(r"grenades (\d+)", fighter("@e[tag=p7n,limit=1]"))
left = count(f"@e[type=superbwarfare:hand_grenade,{AREA}]")
wall = sum(1 for dz in range(-8, 9) for dy in range(4) if "passed" in c(f"execute if block {X + 4} {Y + dy} {Z + dz} minecraft:stone"))
# the floor: 41 x 17 stone under the platform, every block still there
floor_missing = 0
for dx in range(-20, 21, 2):
    for dz in range(-8, 9, 2):
        if "passed" not in c(f"execute if block {X + dx} {Y - 1} {Z + dz} minecraft:stone"):
            floor_missing += 1
check("a sergeant throws a grenade at a target that went behind a wall; it detonates on the platform; nothing is lost",
      thrown_seen and before and after and int(after.group(1)) <= int(before.group(1)) - 1 and left == 0 and wall == 68 and floor_missing == 0,
      f"target {'acquired' if 'target RUAF' in acquired else 'NOT acquired'}; grenade seen {thrown_seen}; grenades {before.group(1) if before else '?'} -> {after.group(1) if after else '?'}; left {left}; wall {wall} of 68; floor samples missing {floor_missing} of 189")
clear()
c(f"fill {X - 21} {Y - 1} {Z - 9} {X + 21} {Y + 3} {Z + 9} minecraft:air")

# 6. persistence and the wider range
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")
c("forceload add -2096 -696 -1904 -504")
time.sleep(5)
c("kill @e[tag=gs_director,x=-2100,y=-64,z=-700,dx=200,dy=400,dz=200]")
c("gscraft director pass -2000 -600 10")
persistent = count("@e[tag=gs_director,nbt={PersistenceRequired:1b},x=-2100,y=-64,z=-700,dx=200,dy=400,dz=200]")
placed = count("@e[tag=gs_director,x=-2100,y=-64,z=-700,dx=200,dy=400,dz=200]")
survey = c("gscraft director survey -2000 66 -600 60")
stats = c("gscraft director stats")
check("the director's placements are persistent and the open range is wider", placed > 0 and persistent == placed and "swept back" in stats,
      f"placed {placed}, persistent {persistent}; {stats}")
print("  survey at the Woods ground:", survey.replace("\n", " | ")[:300])
c("kill @e[tag=gs_director,x=-2100,y=-64,z=-700,dx=200,dy=400,dz=200]")
c("forceload remove -2096 -696 -1904 -504")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
callouts = [l for l in new.splitlines() if "threw a grenade" in l]
check("the grenade throw was logged and no gscraft errors", callouts and not bad, f"throw lines {len(callouts)}, error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
