"""Phase 19, armour V4 on the LOCAL server: what the players are told (design §4; owner: no hit numbers, only a module
that breaks). Headless, so the log copy of each line is what is checked.

1. A module breaking is reported: the turret (set through the entity data), then the engine.
2. The withdrawal is reported when the crew withdraws.
3. Destruction is reported, with the killer's name.
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
AREA = f"x={X - 40},y={Y - 10},z={Z - 40},dx=80,dy=40,dz=80"
HP = 'Health:20000f,Attributes:[{Name:"minecraft:generic.max_health",Base:20000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:t_90a", "gscraft:crew", "gscraft:nato_soldier"):
        c(f"kill @e[type={t},{AREA}]")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def reported(mark, word):
    return any("armour:" in l and word in l for l in log_since(mark).splitlines())


c(f"forceload add {X - 40} {Z - 40} {X + 40} {Z + 40}")
time.sleep(4)
clear()
L.fill(r, X - 30, Y - 1, Z - 30, X + 30, Y + 4, Z + 30, "minecraft:air")
L.fill(r, X - 30, Y - 1, Z - 30, X + 30, Y - 1, Z + 30, "minecraft:stone")
c(f"execute positioned {X} {Y} {Z} rotated -90 0 run gscraft vehicle spawn superbwarfare:t_90a ruaf")
time.sleep(2)
T = "@e[type=superbwarfare:t_90a,limit=1]"

# 1. modules
mark = LOG.stat().st_size
c(f"data merge entity {T} {{TurretHealth:0f,TurretDamaged:1b}}")
time.sleep(1.5)
turret = reported(mark, "turret")
c(f"data merge entity {T} {{MainEngineHealth:0f,MainEngineDamaged:1b}}")
time.sleep(1.5)
engine = reported(mark, "engine")
check("a turret and then an engine breaking are each reported once", turret and engine and log_since(mark).count("armour:") == 2,
      f"turret {turret}, engine {engine}, lines {log_since(mark).count('armour:')}")

# 2. the withdrawal (a fresh tank, a target in view, a blast below a third)
clear()
c(f"execute positioned {X} {Y} {Z} rotated -90 0 run gscraft vehicle spawn superbwarfare:t_90a ruaf")
time.sleep(1.5)
c(f'summon gscraft:nato_soldier {X + 30} {Y} {Z} {{Tags:["p19t"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(5)
mark = LOG.stat().st_size
for k in range(5):   # the list is not linear: hit until below a third
    out = c(f"gscraft vehicle hit {T} minecraft:explosion 500 @e[tag=p19t,limit=1]")
    hp = re.search(r"-> ([\d.\-]+)", out)
    if hp and float(hp.group(1)) < 165.0:
        break
    time.sleep(0.3)
print("   ", out[:120])
for i in range(8):
    time.sleep(1)
    if reported(mark, "withdrawing"):
        break
check("the withdrawal is reported", reported(mark, "withdrawing"), f"after {i + 1} s")

# 3. destruction with the killer's name
mark = LOG.stat().st_size
print("   ", c(f"gscraft vehicle hit {T} minecraft:explosion 3000 @e[tag=p19t,limit=1]")[:140])
time.sleep(2.5)
lines = [l for l in log_since(mark).splitlines() if "armour:" in l and "destroyed" in l]
check("destruction is reported with the killer", len(lines) == 1 and "destroyed_by" in lines[0], f"{[l[l.find('armour:'):] for l in lines]}")

clear()
L.fill(r, X - 30, Y - 1, Z - 30, X + 30, Y + 4, Z + 30, "minecraft:air")
c(f"forceload remove {X - 40} {Z - 40} {X + 40} {Z + 40}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
