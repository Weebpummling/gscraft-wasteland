"""Phase 17, armour V2 on the LOCAL server (design 2026-09-11 §7): a BMP-2 with a crew of ours drives a road loop by
itself. Needs a ticking world and no player. Staged on a long stone platform at y 200.

1. `/gscraft vehicle spawn superbwarfare:bmp_2 ruaf` places a whole, fuelled BMP-2 with a crew in the seat.
2. Given a four-corner route it reaches at least three waypoints inside ninety seconds, on its own.
3. The crew cannot be hurt and is not seen; it goes when the vehicle goes.
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
AREA = f"x={X - 80},y={Y - 10},z={Z - 50},dx=160,dy=40,dz=100"


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


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


c(f"forceload add {X - 80} {Z - 48} {X + 80} {Z + 48}")
time.sleep(5)
clear()
c(f"fill {X - 70} {Y - 1} {Z - 40} {X + 70} {Y + 6} {Z + 40} minecraft:air")
c(f"fill {X - 70} {Y - 1} {Z - 40} {X + 70} {Y - 1} {Z + 40} minecraft:stone")
c(f"fill {X - 71} {Y} {Z - 41} {X + 71} {Y + 2} {Z + 41} minecraft:stone hollow")
c(f"fill {X - 70} {Y} {Z - 40} {X + 70} {Y + 5} {Z + 40} minecraft:air")

# 1. the spawn
out = c(f"execute positioned {X - 40} {Y} {Z - 20} run gscraft vehicle spawn superbwarfare:bmp_2 ruaf")
time.sleep(1.5)
st = c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]")
crews = count(f"@e[type=gscraft:crew,{AREA}]")
whole = "damaged false" in st and re.search(r"health ([\d.]+)/\1", st) is not None and "energy 0/" not in st
check("the spawn places a whole, fuelled BMP-2 with a crew in the seat", "placed BMP-2" in out and crews == 1 and whole, f"{out[:50]}; crews {crews}; {st[:150]}")

# 2. the loop
for x, z in ((X + 40, Z - 20), (X + 40, Z + 20), (X - 40, Z + 20), (X - 40, Z - 20)):
    c(f"gscraft vehicle route @e[type=superbwarfare:bmp_2,limit=1] add {x} {z}")
print("   ", c("gscraft vehicle route @e[type=superbwarfare:bmp_2,limit=1] show"))
mark = LOG.stat().st_size
reached = []
trail = []
for i in range(90):
    time.sleep(1)
    reached = re.findall(r"reached waypoint (\d) of 4", log_since(mark))
    if i % 10 == 0:
        m = re.search(r"at ([-\d.]+) [-\d.]+ ([-\d.]+)", c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]"))
        trail.append(f"{float(m.group(1)):.0f},{float(m.group(2)):.0f}" if m else "?")
    if len(reached) >= 4:
        break
gave_up = log_since(mark).count("gives up on waypoint")
check("with a four-corner route the crew drives the loop by itself", len(reached) >= 3 and gave_up == 0, f"waypoints reached {reached} in {i + 1} s, gave up {gave_up}; trail {' '.join(trail)}")

# 3. the crew: unhittable, and gone with the vehicle
hit = c(f"damage @e[type=gscraft:crew,{AREA},limit=1] 50 minecraft:generic")
alive = count(f"@e[type=gscraft:crew,{AREA}]")
c(f"kill @e[type=superbwarfare:bmp_2,{AREA}]")
time.sleep(3.5)
after = count(f"@e[type=gscraft:crew,{AREA}]")
check("the crew cannot be hurt, and it is gone three seconds after its vehicle", "invulnerable" in hit.lower() and alive == 1 and after == 0, f"damage: {hit[:50]}; crews before {alive}, after the vehicle's death {after}")

clear()
c(f"fill {X - 71} {Y - 1} {Z - 41} {X + 71} {Y + 6} {Z + 41} minecraft:air")
c(f"forceload remove {X - 80} {Z - 48} {X + 80} {Z + 48}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
