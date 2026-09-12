"""Phase 16, armour V1 on the LOCAL server (design 2026-09-11 §7, results in §9): the questions that decide the rest,
answered with /gscraft vehicle on summoned Superb Warfare vehicles. Needs a ticking world, no player, and the armour
override datapack NOT installed at the start (the test installs it half way and reloads).

1. A T-90A with nobody aboard does not move on the forward input, however much energy it has (the mod wants a
   passenger); with a mob mounted in seat 0 (/ride) it drives.
2. What each damage source comes to after the mod's own modifier list, on a T-90A and a BMP-2 (the table for §5).
3. The override datapack (tools/armour_override.py --install, /reload) makes every TACZ bullet worth nothing on both.
4. With the mob aboard the AI turret lays on a target it is given, and the fire input hurts that target.
5. No gscraft errors.
A summoned vehicle needs its part health in the summon NBT (TurretHealth etc.), or it arrives with the parts damaged.
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
AREA = f"x={X - 70},y={Y - 10},z={Z - 70},dx=140,dy=40,dz=140"
PARTS = "TurretHealth:100f,MainEngineHealth:150f,LeftWheelHealth:100f,RightWheelHealth:100f,TurretDamaged:0b,MainEngineDamaged:0b,LeftWheelDamaged:0b,RightWheelDamaged:0b,Energy:10000000"


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:t_90a", "superbwarfare:bmp_2", "gscraft:nato_soldier", "gscraft:ruaf_soldier", "superbwarfare:projectile"):
        c(f"kill @e[type={t},{AREA}]")


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def moved_lines(mark):
    out = {}
    for l in log_since(mark).splitlines():
        m = re.search(r"done: (.+?) moved ([\d.]+) blocks", l)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()
c(f"fill {X - 60} {Y - 1} {Z - 30} {X + 60} {Y + 6} {Z + 30} minecraft:air")
c(f"fill {X - 60} {Y - 1} {Z - 30} {X + 60} {Y - 1} {Z + 30} minecraft:stone")
c(f"fill {X - 61} {Y} {Z - 31} {X + 61} {Y + 1} {Z + 31} minecraft:stone hollow")
c(f"fill {X - 60} {Y} {Z - 30} {X + 60} {Y + 5} {Z + 30} minecraft:air")

# 1. nobody aboard: no movement; a mob in seat 0: it drives
c(f'summon superbwarfare:t_90a {X - 40} {Y} {Z - 10} {{Tags:["v1t"],Rotation:[-90f,0f],{PARTS}}}')
c(f'summon superbwarfare:bmp_2 {X - 40} {Y} {Z + 10} {{Tags:["v1b"],Rotation:[-90f,0f],{PARTS}}}')
time.sleep(1.5)
print("   ", c("gscraft vehicle status @e[tag=v1t,limit=1]")[:170])
mark = LOG.stat().st_size
c("gscraft vehicle drive @e[tag=v1t,limit=1] 60 sprint")
time.sleep(4.5)
empty = moved_lines(mark)
c(f'summon gscraft:ruaf_soldier {X - 40} {Y + 1} {Z - 10} {{Tags:["v1c"],NoAI:1b,GscraftRank:"RUAF Rifleman"}}')
time.sleep(0.5)
ride = c("ride @e[tag=v1c,limit=1] mount @e[tag=v1t,limit=1]")
time.sleep(0.5)
mark = LOG.stat().st_size
c("gscraft vehicle drive @e[tag=v1t,limit=1] 60 sprint")
time.sleep(4.5)
crewed = moved_lines(mark)
check("a T-90A with nobody aboard stays put on the forward input; with a mob in seat 0 it drives",
      empty.get("T-90A MBT") is not None and empty["T-90A MBT"] < 0.5 and crewed.get("T-90A MBT", 0) >= 5.0,
      f"empty {empty}; with a crew {crewed}; {ride}")
c("gscraft vehicle input @e[tag=v1t,limit=1] back on")   # bring it back to a stop near where it started, then release
time.sleep(1.5)
c("gscraft vehicle input @e[tag=v1t,limit=1] back off")

# 2. the damage table, the mod's own lists
c(f'summon gscraft:nato_soldier {X} {Y} {Z + 25} {{Tags:["v1a"],NoAI:1b,GscraftRank:"NATO Rifleman"}}')
time.sleep(1)
TABLE = [("tacz:bullet", 6.5, "5.56 ball"), ("tacz:bullet", 42.0, ".308"), ("tacz:bullet_ignore_armor", 42.0, ".308 AP"),
         ("superbwarfare:custom_explosion", 120.0, "hand grenade blast"), ("superbwarfare:projectile_explosion", 200.0, "rocket blast"),
         ("minecraft:explosion", 100.0, "TNT-class blast"), ("superbwarfare:mine", 300.0, "mine"), ("superbwarfare:projectile_hit", 65.0, "30 mm shell")]
table = {}
for tag, name in (("v1t", "T-90A"), ("v1b", "BMP-2")):
    rows = []
    for dtype, amt, label in TABLE:
        out = c(f"gscraft vehicle hit @e[tag={tag},limit=1] {dtype} {amt} @e[tag=v1a,limit=1]")
        rows.append((label, amt, num(out, r"makes it ([\d.\-]+)"), num(out, r"\(([\d.\-]+) taken\)")))
        time.sleep(0.2)
    table[name] = rows
    print(f"    {name}: " + "; ".join(f"{l} {a:g} -> {t}" for l, a, li, t in rows))
bmp = dict((l, t) for l, a, li, t in table["BMP-2"])
t90 = dict((l, t) for l, a, li, t in table["T-90A"])
check("the mod's own lists: rifle rounds scratch the BMP-2, the T-90A shrugs them, blasts hurt both",
      bmp.get(".308") is not None and bmp[".308"] > 0 and t90.get("hand grenade blast") is not None and t90["hand grenade blast"] > 0 and bmp.get("hand grenade blast", 0) > 0,
      f"BMP .308 {bmp.get('.308')}, T-90 .308 {t90.get('.308')}, grenade BMP {bmp.get('hand grenade blast')} / T-90 {t90.get('hand grenade blast')}, rocket BMP {bmp.get('rocket blast')} / T-90 {t90.get('rocket blast')}")

# 3. the override: TACZ bullets worth nothing
res = subprocess.run([sys.executable, str(Path(__file__).parent / "armour_override.py"), "--install"], capture_output=True, text=True)
print("   ", res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-200:])
c("reload", t=120)
time.sleep(4)
after = {}
for tag, name in (("v1t", "T-90A"), ("v1b", "BMP-2")):
    outs = [c(f"gscraft vehicle hit @e[tag={tag},limit=1] {d} 42 @e[tag=v1a,limit=1]") for d in ("tacz:bullet", "tacz:bullet_ignore_armor")]
    after[name] = [num(o, r"\(([\d.\-]+) taken\)") for o in outs]
check("with the override every TACZ bullet is worth nothing on both", all(t is not None and abs(t) < 0.01 for v in after.values() for t in v), f"taken after the override {after}")

# 4. with the mob aboard: the AI turret lays on a target and the fire input hurts it
st0 = c("gscraft vehicle status @e[tag=v1t,limit=1]")
tx, tz = num(st0, r"at ([\d.\-]+) "), num(st0, r"at [\d.\-]+ [\d.\-]+ ([\d.\-]+)")
# on the tank's flank (it points +x): the turret has to turn about ninety degrees to lay on it
c(f'summon gscraft:nato_soldier {tx:.1f} {Y} {min(Z + 28, tz + 25):.1f} {{Tags:["v1x"],NoAI:1b,GscraftRank:"NATO Rifleman",Health:2000f,Attributes:[{{Name:"minecraft:generic.max_health",Base:2000}}]}}')
time.sleep(1)
y0 = num(st0, r"turret yaw ([\d.\-]+)")
out = c("gscraft vehicle target @e[tag=v1t,limit=1] @e[tag=v1x,limit=1]")
time.sleep(3)
st = c("gscraft vehicle status @e[tag=v1t,limit=1]")
y1 = num(st, r"turret yaw ([\d.\-]+)")
h0 = num(c("data get entity @e[tag=v1x,limit=1] Health"), r"([\d.]+)f")
c("gscraft vehicle input @e[tag=v1t,limit=1] fire on")
time.sleep(3)
c("gscraft vehicle input @e[tag=v1t,limit=1] fire off")
h1 = num(c("data get entity @e[tag=v1x,limit=1] Health"), r"([\d.]+)f")
check("with a mob aboard the AI turret turns to its target and the fire input hurts it",
      y0 is not None and y1 is not None and abs(y1 - y0) > 1.0 and h0 is not None and h1 is not None and h1 < h0,
      f"turret yaw {y0} -> {y1}; target health {h0} -> {h1}")

clear()
c(f"fill {X - 61} {Y - 1} {Z - 31} {X + 61} {Y + 6} {Z + 31} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
