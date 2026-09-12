"""Phase 18, armour V3 on the LOCAL server (design 2026-09-11 §7): a T-90A with a crew stops, lays and fires at a
fighter, holds fire for an ally in the line, resumes its route when the target is gone, withdraws when hurt, and is
immune to both gun mods' rounds while every explosive still hurts. Needs a ticking world and no player; installs the
armour override datapack at the start.

1. Spawned with a route, the T-90A (driver + gunner) halts and fires at a NATO soldier 30 blocks off its road, after the acquire time.
1b. A target straight behind the halted hull is outside the driver's cone until a hit on the hull alerts the crew.
2. An ally walked into the line of fire holds it.
3. The target dead, the crew resumes the route.
4. Blasted below a third of its health with a target in view, it withdraws away from the target (a 900 blast: 1800 kills it).
5. Superb Warfare gunfire and TACZ rounds are worth nothing; a blast and a grenade still are.
6. No gscraft errors.
"""
import re
import subprocess
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
AREA = f"x={X - 80},y={Y - 10},z={Z - 50},dx=160,dy=40,dz=100"
HP = 'Health:2000f,Attributes:[{Name:"minecraft:generic.max_health",Base:2000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:t_90a", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier", "superbwarfare:projectile", "superbwarfare:cannon_shell"):
        c(f"kill @e[type={t},{AREA}]")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def health(sel):
    return num(c(f"data get entity {sel} Health"), r"([\d.]+)f")


def tank():
    return c("gscraft vehicle status @e[type=superbwarfare:t_90a,limit=1]")


def tank_pos():
    st = tank()
    return num(st, r"at ([-\d.]+) "), num(st, r"at [-\d.]+ [-\d.]+ ([-\d.]+)")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


subprocess.run([sys.executable, str(Path(__file__).parent / "armour_override.py"), "--install"], capture_output=True, text=True)
c("reload", t=120)
time.sleep(3)
c(f"forceload add {X - 80} {Z - 48} {X + 80} {Z + 48}")
time.sleep(5)
clear()
L.fill(r, X - 70, Y - 1, Z - 40, X + 70, Y + 6, Z + 40, "minecraft:air")
L.fill(r, X - 70, Y - 1, Z - 40, X + 70, Y - 1, Z + 40, "minecraft:stone")
L.fill(r, X - 71, Y, Z - 41, X + 71, Y + 2, Z + 41, "minecraft:stone", "hollow")
L.fill(r, X - 70, Y, Z - 40, X + 70, Y + 5, Z + 40, "minecraft:air")

# 1. halt and fire
c(f"execute positioned {X - 50} {Y} {Z} rotated -90 0 run gscraft vehicle spawn superbwarfare:t_90a ruaf")
time.sleep(1.5)
crews = count(f"@e[type=gscraft:crew,{AREA}]")
c(f"gscraft vehicle route @e[type=superbwarfare:t_90a,limit=1] add {X + 50} {Z}")
c(f"gscraft vehicle route @e[type=superbwarfare:t_90a,limit=1] add {X - 50} {Z}")
time.sleep(2)
c(f'summon gscraft:nato_soldier {X - 20} {Y} {Z - 30} {{Tags:["p18t"],NoAI:1b,GscraftRank:"NATO Rifleman",Health:20000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:20000}}]}}')
mark = LOG.stat().st_size
engaged = False
halted = False
h_first = None
for i in range(25):
    time.sleep(1)
    h = health("@e[tag=p18t,limit=1]")
    if h is None or h < 20000.0:
        h_first = h if h is not None else "dead"
    st = tank()
    if "engages" in log_since(mark):
        engaged = True
        if "inputs f- b-" in st:
            halted = True
    if h_first is not None and halted:
        break
check("the crew halts the tank and fires at a fighter 30 blocks off its road", crews == 2 and engaged and halted and h_first is not None,   # damaged or dead
      f"crews {crews}; engaged {engaged}; halted {halted}; target health after {i + 1} s: {h_first}; {re.search(r'turret target [^,]*', st).group(0) if re.search(r'turret target [^,]*', st) else '?'}")

# 1b. the cone and the alert: a second target straight behind the halted hull is not engaged by the driver; a hit on the hull opens the cone
tx, tz = tank_pos()
yaw = num(tank(), r"body yaw ([-\d.]+)") or -90.0
import math
bx, bz = tx + 30 * math.sin(math.radians(yaw)), tz - 30 * math.cos(math.radians(yaw))   # behind: minus the forward vector (-sin, cos)
c("kill @e[tag=p18t]")
c("gscraft vehicle route @e[type=superbwarfare:t_90a,limit=1] clear")   # the hull stays put for the cone check
time.sleep(1.5)
tx, tz = tank_pos()
yaw = num(tank(), r"body yaw ([-\d.]+)") or -90.0
bx, bz = tx + 30 * math.sin(math.radians(yaw)), tz - 30 * math.cos(math.radians(yaw))
c(f'summon gscraft:nato_soldier {bx:.1f} {Y} {bz:.1f} {{Tags:["p18b"],NoAI:1b,GscraftRank:"NATO Rifleman",Health:20000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:20000}}]}}')
mark_b = LOG.stat().st_size
time.sleep(6)
before_hit = [l for l in log_since(mark_b).splitlines() if "(driver) engages" in l]
print("   ", c(f"gscraft vehicle hit @e[type=superbwarfare:t_90a,limit=1] superbwarfare:custom_explosion 60 @e[tag=p18b,limit=1]")[:110])
engaged_after = False
for i in range(8):
    time.sleep(1)
    if any("(driver) engages" in l for l in log_since(mark_b).splitlines()):
        engaged_after = True
        break
check("a target behind the hull is outside the driver's cone until a hit on the hull alerts the crew", not before_hit and engaged_after,
      f"engaged before the hit: {len(before_hit)}; after the hit: {engaged_after} ({i + 1} s); hull yaw {yaw}")
c("kill @e[tag=p18b]")
c(f"gscraft vehicle route @e[type=superbwarfare:t_90a,limit=1] add {X + 50} {Z}")
c(f"gscraft vehicle route @e[type=superbwarfare:t_90a,limit=1] add {X - 50} {Z}")
time.sleep(1)
c(f'summon gscraft:nato_soldier {X - 20} {Y} {Z - 30} {{Tags:["p18t"],NoAI:1b,GscraftRank:"NATO Rifleman",Health:20000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:20000}}]}}')
time.sleep(5)

# 2. an ally in the line holds fire (once the halted hull has stopped coasting: the line moves with it)
tx, tz = tank_pos()
for i in range(10):
    time.sleep(1)
    nx, nz = tank_pos()
    if abs(nx - tx) < 0.2 and abs(nz - tz) < 0.2:
        break
    tx, tz = nx, nz
bx, bz = tx + (X - 20 - tx) * 0.5, tz + (Z - 30 - tz) * 0.5
c(f'summon gscraft:ruaf_soldier {bx:.1f} {Y} {bz:.1f} {{Tags:["p18a"],NoAI:1b,GscraftRank:"RUAF Rifleman",{HP}}}')
time.sleep(1.5)
h0 = health("@e[tag=p18t,limit=1]")
mark2 = LOG.stat().st_size
time.sleep(5)
h1 = health("@e[tag=p18t,limit=1]")
held = "holds fire" in log_since(mark2) or "holds fire" in log_since(mark)
c("kill @e[tag=p18a]")
check("an ally in the line of fire holds it", held and h0 is not None and h1 is not None and h0 - h1 < 30.0, f"held {held}; target health over five seconds {h0} -> {h1}")

# 3. the target gone, the route resumes
c("kill @e[tag=p18t]")
mark3 = LOG.stat().st_size
resumed = False
for i in range(30):
    time.sleep(1)
    if "reached waypoint" in log_since(mark3):
        resumed = True
        break
check("with the target dead the crew resumes its route", resumed, f"waypoint reached after {i + 1} s: {resumed}")

# 4. the withdrawal
tx, tz = tank_pos()
c(f'summon gscraft:nato_soldier {tx:.1f} {Y} {tz - 30:.1f} {{Tags:["p18r"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(3)
d0 = num(c("execute as @e[type=superbwarfare:t_90a,limit=1] run gscraft vehicle status @s"), r"at ([-\d.]+) [-\d.]+ ([-\d.]+)")
tx0, tz0 = tank_pos()
print("   ", c(f"gscraft vehicle hit @e[type=superbwarfare:t_90a,limit=1] minecraft:explosion 900 @e[tag=p18r,limit=1]")[:120])
mark4 = LOG.stat().st_size
withdrew = False
for i in range(12):
    time.sleep(1)
    if "withdraws" in log_since(mark4):
        withdrew = True
tx1, tz1 = tank_pos()
dist0 = ((tx0 - tx0) ** 2 + (tz0 - (tz - 30)) ** 2) ** 0.5
dist1 = ((tx1 - tx0) ** 2 + (tz1 - (tz - 30)) ** 2) ** 0.5
st = tank()
hp_now = num(st, r"health (-?[\d.]+)")
check("blasted below a third of its health it withdraws away from the target", withdrew and dist1 > dist0 + 6.0,
      f"withdrew {withdrew}; distance to the target {dist0:.1f} -> {dist1:.1f}; health {hp_now}")
c("kill @e[tag=p18r]")

# 5. both gun mods worth nothing, the explosives not
c(f'summon gscraft:nato_soldier {X} {Y} {Z + 30} {{Tags:["p18h"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
taken = {}
for dtype, amt in (("superbwarfare:gunfire", 40.0), ("superbwarfare:gunfire_headshot", 80.0), ("superbwarfare:gunfire_absolute", 40.0), ("tacz:bullet", 42.0), ("tacz:bullet_ignore_armor", 42.0),
                   ("minecraft:explosion", 100.0), ("superbwarfare:custom_explosion", 120.0), ("superbwarfare:projectile_explosion", 200.0)):
    out = c(f"gscraft vehicle hit @e[type=superbwarfare:t_90a,limit=1] {dtype} {amt} @e[tag=p18h,limit=1]")
    taken[dtype.split(':')[1]] = num(out, r"\(([\d.\-]+) taken\)")
guns = [taken[k] for k in ("gunfire", "gunfire_headshot", "gunfire_absolute", "bullet", "bullet_ignore_armor")]
blasts = [taken[k] for k in ("explosion", "custom_explosion", "projectile_explosion")]
check("Superb Warfare and TACZ rounds are worth nothing; TACZ's blast (minecraft:explosion), a grenade and a rocket still hurt",
      all(g is not None and abs(g) < 0.01 for g in guns) and all(b is not None and b > 1.0 for b in blasts), f"taken {taken}")

clear()
L.fill(r, X - 71, Y - 1, Z - 41, X + 71, Y + 6, Z + 41, "minecraft:air")
c(f"forceload remove {X - 80} {Z - 48} {X + 80} {Z + 48}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
