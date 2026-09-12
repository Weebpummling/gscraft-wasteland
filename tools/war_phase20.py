"""Phase 20, armour V5 on the LOCAL server (design 2026-09-11 §3): the armour patrol as the director places it.
Needs a ticking world and no player. A road strip of the road mod's block is laid on the platform at y 200.

1. `/gscraft director armour <x> <y> <z> superbwarfare:bmp_2 3` places a BMP-2 on the road with a crew and three
   infantry formed as a squad; nothing is placed where there is no road.
2. The vehicle drives the road both ways (its route is the road's two ends) with the infantry riding in its bay;
   a hostile beside the road halts it and the riders dismount with their AI back.
3. The vehicle counts as four against the ceilings (the director's count).
4. The sweep: with nobody within 128 the vehicle, its crew and its infantry are taken back on the second pass.
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
AREA = f"x={X - 100},y={Y - 10},z={Z - 60},dx=200,dy=40,dz=120"
ROAD = "furenikusroads:road_block_standard_1"


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:bmp_2", "superbwarfare:t_90a", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier"):
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


def vpos():
    st = c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]")
    return num(st, r"at ([-\d.]+) "), num(st, r"at [-\d.]+ [-\d.]+ ([-\d.]+)")


c("gscraft director pause")
c("gscraft director phantom clear")
c(f"forceload add {X - 100} {Z - 60} {X + 100} {Z + 60}")
time.sleep(5)
clear()
L.fill(r, X - 90, Y - 1, Z - 50, X + 90, Y + 5, Z + 50, "minecraft:air")
L.fill(r, X - 90, Y - 1, Z - 50, X + 90, Y - 1, Z + 50, "minecraft:stone")
L.fill(r, X - 80, Y - 1, Z - 2, X + 80, Y - 1, Z + 2, ROAD)   # the road: 160 long, 5 wide, along x
time.sleep(1)
road_ok = "passed" in c(f"execute if block {X} {Y - 1} {Z} {ROAD}")

# 1. placement on the road, none off it
out = c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 3")
time.sleep(2)
vehicles = count(f"@e[type=superbwarfare:bmp_2,{AREA}]")
crews = count(f"@e[type=gscraft:crew,{AREA}]")
soldiers = count(f"@e[type=gscraft:ruaf_soldier,{AREA}]")
riders = int(num(c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]"), r"riders (\d+)") or 0)
vx, vz = vpos()
on_road = vx is not None and abs(vz - Z) <= 3.0
off = c(f"gscraft director armour {X} {Y} {Z + 60} superbwarfare:bmp_2 0")
check("the forced roll places a crewed BMP-2 on the road with three infantry in a squad, and nothing off the road",
      road_ok and vehicles == 1 and crews == 1 and soldiers == 3 and riders == 3 and on_road and "no road stand" in off,
      f"road block {road_ok}; {out[:40]}; vehicles {vehicles}, crews {crews}, soldiers {soldiers}, riding {riders}, at z {vz}; off the road: {off[:30]}")
print("    status:", c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]")[:160])

# 2. the drive along the road and the escort behind
route = c("gscraft vehicle route @e[type=superbwarfare:bmp_2,limit=1] show")
x0, z0 = vpos()
time.sleep(20)
x1, z1 = vpos()
moved = abs(x1 - x0) if x0 is not None and x1 is not None else 0.0
orders = [c(f"execute as @e[type=gscraft:ruaf_soldier,limit=1,sort=nearest,x={int(x1) if x1 else X},y={Y},z={Z}] run gscraft fighter @s")]
following = count(f"@e[type=gscraft:ruaf_soldier,x={int(x1) - 30 if x1 else X},y={Y - 5},z={Z - 20},dx=60,dy=10,dz=40]") if x1 else 0
check("the vehicle drives the road at the infantry's pace and they follow it", moved >= 12.0 and following >= 2 and "waypoint" in route,
      f"{route[:70]}; moved {moved:.0f} blocks in 20 s; infantry within 30 of it {following}; leader: {re.search(r'order [A-Z]+[^,]*', orders[0]).group(0) if re.search(r'order [A-Z]+', orders[0]) else '?'}")

# 2b. the dismount: a hostile ahead on the road (inside the driver's cone), the hull halts and the riders come out with their AI
# the hull loops the road at a sprint with its riders aboard: the target waits beside the waypoint it is heading for, head-on and in the cone
rs = c("gscraft vehicle route @e[type=superbwarfare:bmp_2,limit=1] show")
wi = int(num(rs, r"waypoint (\d+) of") or 1) - 1
wps = re.findall(r"(-?\d+),(-?\d+)", rs)
ax, az = (int(wps[wi][0]), int(wps[wi][1])) if wps else (X, Z)
c(f'summon gscraft:nato_soldier {ax} {Y} {az - 5} {{Tags:["p20t"],NoAI:1b,GscraftRank:"NATO Rifleman",Health:20000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:20000}}]}}')
mark = LOG.stat().st_size
out_ok = False
for i in range(30):
    time.sleep(1)
    if "dismount" in log_since(mark):
        out_ok = True
        break
riding_now = int(num(c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]"), r"riders (\d+)") or 0)
noai = c("data get entity @e[type=gscraft:ruaf_soldier,limit=1] NoAI")
ai_back = "0b" in noai or "no elements" in noai.lower()   # NoAI false is not written to NBT
check("when the crew halts to fight the riders dismount beside the hull with their AI back", out_ok and riding_now == 0 and ai_back, f"dismount reported {out_ok} ({i + 1} s); still riding {riding_now}; NoAI {noai[-3:]}")
c("kill @e[tag=p20t]")
time.sleep(1)

# 3. the count: 4 for the vehicle + 3 infantry (a full pass from a phantom beside it)
c(f"gscraft director phantom set {X} {Y} {Z}")
c("gscraft director bench 1")
now = num(c("gscraft director stats"), r"(\d+) creatures now")
check("a vehicle counts as four against the ceilings", now is not None and now >= 7, f"creatures now {now} (expected 4 + 3 or more)")

# 4. the sweep: the only presence 300 blocks away, two passes
c(f"gscraft director phantom set {X + 300} {Y} {Z}")
c("gscraft director bench 1")
one = (count(f"@e[type=superbwarfare:bmp_2,{AREA}]"), count(f"@e[type=gscraft:crew,{AREA}]"), count(f"@e[type=gscraft:ruaf_soldier,{AREA}]"))
c("gscraft director bench 1")
time.sleep(2)
left = (count(f"@e[type=superbwarfare:bmp_2,{AREA}]"), count(f"@e[type=gscraft:crew,{AREA}]"), count(f"@e[type=gscraft:ruaf_soldier,{AREA}]"))
check("the sweep takes the vehicle, its crew and its infantry back on the second pass", one == (1, 1, 3) and left == (0, 0, 0), f"after one pass {one}, after two {left}")
c("gscraft director phantom clear")

c("gscraft director pause")
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
