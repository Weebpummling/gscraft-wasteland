"""Phase 37, Skadowsky's streets as roads and the withdrawal of a holding vehicle (owner, 2026-09-13) on the LOCAL
server. Needs a ticking world and no player. Roads are `gscraft_armour/roads.json`: the road mod's surfaces anywhere,
and inside the `skad` zone the vanilla stone work the streets are built of. A vehicle placed on the square patrols;
one placed on the stone test pad far outside the sector holds. A holding vehicle hit below the retreat share (a third)
withdraws from the hitter even with nothing engaged (Crew.tick on a health drop).

1. Armour placed on the square is "patrolling the road" (a route of two ends).
2. Armour placed on the test pad (stone, outside the sector) holds.
3. The holding vehicle, hit under the disabled share by a nearby fighter, withdraws: the log says so and it has backed off within four seconds.
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
SQ = (-940, 64, -979)
X, Y, Z = -2000, 200, -600


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def clear(x, z, rad):
    # a box the full height: a withdrawn hull that drove off the pad lies far below it
    c(f"execute as @e[type=superbwarfare:bmp_2,x={x - rad},y=-64,z={z - rad},dx={2 * rad},dy=384,dz={2 * rad}] run data modify entity @s Health set value -99999f")
    c(f"kill @e[type=gscraft:crew,x={x - rad},y=-64,z={z - rad},dx={2 * rad},dy=384,dz={2 * rad}]")
    c(f"kill @e[type=#minecraft:zombies,x={x - rad},y=-64,z={z - rad},dx={2 * rad},dy=384,dz={2 * rad}]")
    c(f"kill @e[type=gscraft:nato_soldier,x={x - rad},y=-64,z={z - rad},dx={2 * rad},dy=384,dz={2 * rad}]")


def pos(sel):
    m = re.search(r"\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]", c(f"data get entity {sel} Pos"))
    return (float(m.group(1)), float(m.group(2)), float(m.group(3))) if m else None


# 1. the square
c(f"forceload add {SQ[0] - 40} {SQ[2] - 40} {SQ[0] + 40} {SQ[2] + 40}")
time.sleep(3)
clear(SQ[0], SQ[2], 60)
out = c(f"gscraft director armour {SQ[0]} {SQ[1]} {SQ[2]} superbwarfare:bmp_2 0")
check("armour on the square patrols the road", "patrolling the road" in out, f"[{out[:120]}]")
time.sleep(2)
clear(SQ[0], SQ[2], 80)
time.sleep(1)
clear(SQ[0], SQ[2], 80)
c(f"forceload remove {SQ[0] - 40} {SQ[2] - 40} {SQ[0] + 40} {SQ[2] + 40}")

# 2. the pad: holding
c(f"forceload add {X - 56} {Z - 56} {X + 56} {Z + 56}")
time.sleep(3)
c(f"fill {X - 40} {Y - 1} {Z - 40} {X + 40} {Y - 1} {Z + 40} minecraft:stone")   # wide: the withdrawal reverses a good way
c(f"fill {X - 40} {Y} {Z - 40} {X + 40} {Y + 6} {Z + 40} minecraft:air")
clear(X, Z, 40)
out = c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 0")
check("armour on the pad outside the sector holds", "holding" in out, f"[{out[:120]}]")

# 3. hit while holding: withdraws
V = f"@e[type=superbwarfare:bmp_2,x={X - 20},y={Y - 5},z={Z - 20},dx=40,dy=12,dz=40,limit=1]"
before = pos(V)
c(f"summon gscraft:nato_soldier {X + 10} {Y} {Z} {{Tags:[\"p37_hitter\"],NoAI:1b}}")
time.sleep(2)
mark = LOG.stat().st_size
for _ in range(6):   # the mod's own explosion: the damage list makes 90 into 36; six take 300 to 84 (28 %), under the third. A vanilla explosion type ejects the crew instead
    c(f"gscraft vehicle hit {V} superbwarfare:custom_explosion 90 @e[tag=p37_hitter,limit=1]")
    time.sleep(0.5)
time.sleep(4)   # it backs out at ~7 blocks a second: read it before it leaves the pad
after = pos(f"@e[type=superbwarfare:bmp_2,x={X - 60},y={Y - 5},z={Z - 60},dx=120,dy=12,dz=120,limit=1]")
new = log_since(mark)
moved = before and after and ((after[0] - before[0]) ** 2 + (after[2] - before[2]) ** 2) ** 0.5 >= 3
check("a holding vehicle hit below a third withdraws", "withdraws" in new and moved, f"withdraws in log {'withdraws' in new}; before {before and tuple(round(v) for v in before)} after {after and tuple(round(v) for v in after)}")

clear(X, Z, 90)
c(f"kill @e[tag=p37_hitter]")
c(f"fill {X - 40} {Y - 1} {Z - 40} {X + 40} {Y + 6} {Z + 40} minecraft:air")
c(f"forceload remove {X - 56} {Z - 56} {X + 56} {Z + 56}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
