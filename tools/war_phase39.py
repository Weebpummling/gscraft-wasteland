"""Phase 39, the crew's visual scan (owner, 2026-09-13: crews had trouble acquiring) on the LOCAL server. Needs a
ticking world and no player. With nothing engaged the driver crew sweeps the turret slowly across the arc either side
of the hull's heading and the detection cone rides on it; a hit turns the sweep onto the hitter's bearing and the crew
makes its mind up twice as fast. What a headless test can prove: the turret yaw of a holding BMP changes over a few
seconds with nothing about; a rifleman straight behind it is not seen by the sweep alone; a hit from him turns the
turret onto his bearing and the crew engages him. The turret turning on screen is the owner's in-game check.

1. A holding BMP with nothing about sweeps its turret: the yaw read three seconds apart differs.
2. A rifleman straight behind the hull, out of the sweep's reach, is not engaged in eight seconds.
3. Hit from him, the crew engages him within eight seconds and the turret lays toward his bearing.
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
HP = 'Health:20000f,Attributes:[{Name:"minecraft:generic.max_health",Base:20000}]'


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


V = f"@e[type=superbwarfare:bmp_2,x={X - 30},y={Y - 5},z={Z - 30},dx=60,dy=12,dz=60,limit=1]"


def turret():
    m = re.search(r"turret yaw (-?[\d.]+)", c(f"gscraft vehicle status {V}"))
    return float(m.group(1)) if m else None


def hull():
    m = re.search(r"body yaw (-?[\d.]+)", c(f"gscraft vehicle status {V}"))
    return float(m.group(1)) if m else None


def clear():
    c(f"execute as @e[type=superbwarfare:bmp_2,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120] run data modify entity @s Health set value -99999f")
    c(f"kill @e[type=gscraft:crew,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120]")
    c(f"kill @e[type=gscraft:nato_soldier,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120]")
    c(f"kill @e[type=#minecraft:zombies,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120]")


c("gscraft director pause")
c(f"forceload add {X - 48} {Z - 48} {X + 48} {Z + 48}")
time.sleep(3)
c(f"fill {X - 40} {Y - 1} {Z - 40} {X + 40} {Y - 1} {Z + 40} minecraft:stone")
c(f"fill {X - 40} {Y} {Z - 40} {X + 40} {Y + 6} {Z + 40} minecraft:air")
clear()
out = c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 0")
time.sleep(3)
t0 = turret()
time.sleep(3)
t1 = turret()
time.sleep(3)
t2 = turret()
moved = t0 is not None and t1 is not None and t2 is not None and (abs(t1 - t0) > 2 or abs(t2 - t1) > 2)
check("a holding BMP with nothing about sweeps its turret", "placed" in out and moved, f"[{out[:50]}]; turret yaw {t0} -> {t1} -> {t2}; hull {hull()}")

# 2. straight behind, out of the sweep's reach: the hull faces +z (yaw 0), behind is -z
mark = LOG.stat().st_size
c(f'summon gscraft:nato_soldier {X} {Y} {Z - 24} {{Tags:["p39"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(8)
unseen = "engages" not in log_since(mark)
check("a rifleman straight behind the hull is not engaged by the sweep alone", unseen, f"engaged {not unseen}; turret {turret()}")

# 3. hit from him: the scan turns onto his bearing and the crew engages
mark = LOG.stat().st_size
c(f"gscraft vehicle hit {V} superbwarfare:custom_explosion 12 @e[tag=p39,limit=1]")
engaged_at, yaw_at = None, None
for i in range(16):
    time.sleep(0.5)
    if "engages" in log_since(mark):
        engaged_at = (i + 1) * 0.5
        time.sleep(1.5)
        yaw_at = turret()
        break
toward = yaw_at is not None and abs(((yaw_at - 180) + 180) % 360 - 180) <= 60
check("hit from behind, the crew engages within eight seconds and the turret lays toward him", engaged_at is not None and toward, f"engaged at {engaged_at} s; turret yaw {yaw_at} (his bearing 180)")

clear()
c("kill @e[tag=p39]")
c(f"fill {X - 40} {Y - 1} {Z - 40} {X + 40} {Y + 6} {Z + 40} minecraft:air")
c(f"forceload remove {X - 48} {Z - 48} {X + 48} {Z + 48}")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
