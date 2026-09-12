"""Phase 21, armour V6 on the LOCAL server (design 2026-09-11 §3, waves and bosses). Needs a ticking world and no
player. The wave path is driven by `/gscraft director wave <x> <y> <z> <tx> <tz> <vehicle> <boss|none>`, the same
routine the site loop calls for a wave entry naming a vehicle.

1. A wave vehicle is placed at the wave point (a road stand where there is one) and drives to the target, where it
   stops and holds.
2. A wave vehicle is kept by the director's sweep (a wave is the point).
3. A boss is placed named, holds where it is, and its destruction sets the stage test_<boss>.
4. No gscraft errors.
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
AREA = f"x={X - 100},y={Y - 10},z={Z - 60},dx=200,dy=40,dz=120"
ROAD = "furenikusroads:road_block_standard_1"
HP = 'Health:20000f,Attributes:[{Name:"minecraft:generic.max_health",Base:20000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier"):
        c(f"kill @e[type={t},{AREA}]")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def vpos(t):
    st = c(f"gscraft vehicle status @e[type={t},limit=1]")
    return num(st, r"at ([-\d.]+) "), num(st, r"at [-\d.]+ [-\d.]+ ([-\d.]+)"), st


c("gscraft director pause")
c("gscraft director phantom clear")
c("gscraft stage remove test_gatekeeper")
c(f"forceload add {X - 100} {Z - 60} {X + 100} {Z + 60}")
time.sleep(5)
clear()
L.fill(r, X - 90, Y - 1, Z - 50, X + 90, Y + 5, Z + 50, "minecraft:air")
L.fill(r, X - 90, Y - 1, Z - 50, X + 90, Y - 1, Z + 50, "minecraft:stone")
L.fill(r, X - 80, Y - 1, Z - 2, X + 80, Y - 1, Z + 2, ROAD)
time.sleep(1)

# 1. the wave vehicle drives to the target and holds
out = c(f"gscraft director wave {X - 70} {Y} {Z} {X + 40} {Z} superbwarfare:bradley none")
time.sleep(2)
x0, z0, st0 = vpos("superbwarfare:bradley")
mark = LOG.stat().st_size
arrived = False
for i in range(45):
    time.sleep(1)
    if "reached waypoint 1 of 1" in log_since(mark):
        arrived = True
        break
time.sleep(3)
x1, z1, st1 = vpos("superbwarfare:bradley")
holds = x1 is not None and abs(x1 - (X + 40)) < 14.0 and "inputs f- b-" in st1
check("a wave vehicle is placed on the wave point and drives to the target, where it holds", "placed" in out and arrived and holds,
      f"{out[:30]}; from x {x0} to x {x1} in {i + 1} s; arrived {arrived}; holding {holds}")

# 2. the sweep leaves a wave vehicle
c(f"gscraft director phantom set {X + 300} {Y} {Z}")
c("gscraft director bench 2")
kept = (count(f"@e[type=superbwarfare:bradley,{AREA}]"), count(f"@e[type=gscraft:crew,{AREA}]"))
c("gscraft director phantom clear")
check("the sweep leaves a wave vehicle and its crew", kept[0] == 1 and kept[1] >= 1, f"after two far passes (vehicles, crews) {kept}")
clear()

# 3. the boss: named, holding, its stage on death
out = c(f"gscraft director wave {X} {Y} {Z} {X + 60} {Z} superbwarfare:m_1a_2 gatekeeper")
time.sleep(3)
x2, z2, st2 = vpos("superbwarfare:m_1a_2")
named = "The gatekeeper" in c("data get entity @e[type=superbwarfare:m_1a_2,limit=1] CustomName")
time.sleep(4)
x3, z3, _ = vpos("superbwarfare:m_1a_2")
stayed = x2 is not None and x3 is not None and abs(x3 - x2) < 3.0
c(f'summon gscraft:ruaf_soldier {X} {Y} {Z + 20} {{Tags:["p21k"],NoAI:1b,GscraftRank:"RUAF Rifleman",{HP}}}')
time.sleep(1)
before = c("gscraft stages")
c("gscraft vehicle hit @e[type=superbwarfare:m_1a_2,limit=1] minecraft:explosion 3000 @e[tag=p21k,limit=1]")
time.sleep(3)
after = c("gscraft stages")
check("a boss is named, holds its ground, and its death sets the stage", "placed" in out and named and stayed and "test_gatekeeper" not in before and "test_gatekeeper" in after,
      f"named {named}; moved {abs(x3 - x2) if x2 is not None and x3 is not None else '?'} blocks in 4 s; stages before [{before[:40]}] after [{after[:60]}]")

c("gscraft stage remove test_gatekeeper")
clear()
L.fill(r, X - 90, Y - 1, Z - 50, X + 90, Y + 5, Z + 50, "minecraft:air")
c(f"forceload remove {X - 100} {Z - 60} {X + 100} {Z + 60}")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
