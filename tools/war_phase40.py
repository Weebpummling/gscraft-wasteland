"""Phase 40, fighters keep off the hulls (owner, 2026-09-13: they kept running into vehicles) on the LOCAL server. Needs
a ticking world and no player. Against a target riding a hull a fighter holds off at the standoff and backs away inside
the backoff, never melees it; inside any hull's clearance box a fighter steps out. What a headless test can prove: a
squad of riflemen set on a holding BMP's crew keeps its distance over twenty seconds - none inside the backoff, none
against the hull; a fighter placed against a hull with nothing to fight steps clear within a few seconds.

1. Three riflemen sent against a holding BMP stay outside the backoff for twenty seconds, and none touches the hull.
2. A rifleman placed against the hull with nothing to fight is clear of it within five seconds.
3. No gscraft errors.
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


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def within(d):
    """riflemen within d of the hull"""
    return count(f"@e[type=gscraft:nato_soldier,tag=p40,distance=..{d}]".replace("@e[", f"@e[x={X},y={Y},z={Z},"))


def clear():
    c(f"execute as @e[type=superbwarfare:bmp_2,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120] run data modify entity @s Health set value -99999f")
    c(f"kill @e[type=gscraft:crew,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120]")
    c(f"kill @e[type=gscraft:nato_soldier,x={X - 60},y=-64,z={Z - 60},dx=120,dy=384,dz=120]")


c("gscraft director pause")
c(f"forceload add {X - 48} {Z - 48} {X + 48} {Z + 48}")
time.sleep(3)
c(f"fill {X - 40} {Y - 1} {Z - 40} {X + 40} {Y - 1} {Z + 40} minecraft:stone")
c(f"fill {X - 40} {Y} {Z - 40} {X + 40} {Y + 6} {Z + 40} minecraft:air")
clear()
out = c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 0")
time.sleep(2)
# 1. a squad sent against the crew, from 30 blocks ahead (the crew sees them and fights back; their health is huge)
for i in range(3):
    c(f'summon gscraft:nato_soldier {X - 3 + 3 * i} {Y} {Z + 30} {{Tags:["p40"],GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(2)
closest, touching = 99, 0
for _ in range(20):
    time.sleep(1)
    if within(4) > 0:
        touching += 1
    for d in (6, 8, 10, 12, 14):
        if within(d) > 0:
            closest = min(closest, d)
            break
check("three riflemen against a holding BMP stay outside the backoff and never touch the hull", touching == 0 and closest > 12, f"closest band {closest}; seconds with one against the hull {touching}; alive {count('@e[tag=p40]')}")
c("kill @e[tag=p40]")

# 2. a fighter against the hull with nothing to fight steps clear
c(f'summon gscraft:nato_soldier {X + 1} {Y} {Z} {{Tags:["p40b"],GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(5)
m = re.search(r"\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]", c("data get entity @e[tag=p40b,limit=1] Pos"))
dist = ((float(m.group(1)) - (X + 0.5)) ** 2 + (float(m.group(3)) - (Z + 0.5)) ** 2) ** 0.5 if m else None
check("a rifleman placed against the hull steps clear within five seconds", dist is not None and dist >= 3.5, f"distance from the hull's centre {dist and round(dist, 1)}")

c("kill @e[tag=p40b]")
clear()
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
