"""Phase 38, the fire missions (owner, 2026-09-13; docs/gscraft-strikes-2026-09-13.md) on the LOCAL server. Needs a
ticking world and no player. `/gscraft strike <kind> <x y z>` makes the call the grenade would (no thrower from the
console, so the rounds have no owner); the rounds are Superb Warfare's shells and rockets spawned in flight; the Cobra
is DragonRise's AH-1F moved as a prop. What a headless test can prove: the three grenades and the shell card are
items; the mortar's spotting round comes at fifteen seconds and its barrage after, as shells in the air; a second call
during the cooldown is refused; the guns' barrage lands; the Cobra appears within thirty-five seconds, fires rockets
and rounds, and is gone within the minute; nothing of it is left. The grenade's throw, the smoke, the lines and the
sounds are the owner's in-game check (`/give @s gscraft:strike_mortar`).

1. The three strike items and the shell card are registered; the shell order exists.
2. Mortar: the spotting round at ~15 s, the barrage of six after; mortar shells seen in the air; the call refused meanwhile.
3. Artillery (after a reset): cannon shells seen; the barrage of eight logged; a bare BMP on the smoke wrecked.
4. Air (after a reset): the Cobra seen within 25 s at full power with the rotor turning, rockets and gun rounds seen, off station within 60 s, none left.
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


def near(t, d=200):
    return count(f"@e[type={t},x={X - d},y=-64,z={Z - d},dx={2 * d},dy=384,dz={2 * d}]")


ids = ["gscraft:strike_mortar", "gscraft:strike_artillery", "gscraft:strike_air", "gscraft:card_mortar_shell"]
unknown = [i for i in ids if "registered" not in c(f"gscraft item {i}")]
orders = c("gscraft station list")
check("the strike items and the shell card are registered; the shell order exists", not unknown and re.search(r"(\d+) orders", orders) and int(re.search(r"(\d+) orders", orders).group(1)) >= 20, f"unknown {unknown}; [{orders[-60:]}]")

c(f"forceload add {X - 80} {Z - 80} {X + 80} {Z + 80}")   # under vanilla's 256-chunk cap; the run force-loads under the Cobra itself
time.sleep(4)
c(f"fill {X - 24} {Y - 1} {Z - 24} {X + 24} {Y - 1} {Z + 24} minecraft:stone")
c(f"fill {X - 24} {Y} {Z - 24} {X + 24} {Y + 6} {Z + 24} minecraft:air")
c("gscraft strike reset")

# 2. the mortar
mark = LOG.stat().st_size
t0 = time.time()
out = c(f"gscraft strike mortar {X} {Y} {Z}")
refused = c(f"gscraft strike mortar {X} {Y} {Z}")
guns_ready = "ready" in c("gscraft strike status").split("artillery")[1].split(";")[0]   # its own clock: a mortar call leaves the guns ready
spotted, seen, barrage = None, 0, False
while time.time() - t0 < 40:
    time.sleep(1)
    seen = max(seen, near("superbwarfare:mortar_shell"))
    new = log_since(mark)
    if spotted is None and "mortar spotting round" in new:
        spotted = time.time() - t0
    if "mortar barrage of" in new:
        barrage = True
        break
check("mortar: the spotting round at ~15 s, the barrage after, shells in the air; a second call refused",
      "called" in out and "hot" in refused and guns_ready and spotted is not None and 13 <= spotted <= 19 and barrage and seen >= 1,
      f"[{out}] [{refused[:40]}]; guns ready {guns_ready}; spotting at {spotted and round(spotted, 1)} s; barrage {barrage}; shells seen {seen}")

# 3. the guns
c("gscraft strike reset")
mark = LOG.stat().st_size
t0 = time.time()
c(f"kill @e[type=superbwarfare:bmp_2,x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120]")
c(f"gscraft vehicle spawn superbwarfare:bmp_2 ruaf {X} {Y} {Z}")   # a bare hull on the smoke: the guns must wreck it (owner: the strike did no proper damage)
time.sleep(1)
c(f"gscraft strike artillery {X} {Y} {Z}")
seen, barrage = 0, False
while time.time() - t0 < 50:
    time.sleep(1)
    seen = max(seen, near("superbwarfare:cannon_shell"))
    if "artillery barrage of" in log_since(mark):
        barrage = True
        break
time.sleep(3)
st = c(f"gscraft vehicle status @e[type=superbwarfare:bmp_2,x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120,limit=1]")
hp = re.search(r"health ([-\d.]+)/", st)
wrecked = "No entity" in st or "wreck true" in st or (hp is not None and float(hp.group(1)) < 120)
check("artillery: cannon shells in the air, the barrage of eight logged, the hull on the smoke wrecked", barrage and seen >= 1 and wrecked, f"barrage {barrage}; shells seen {seen}; hull [{st[:60]}]")
c(f"execute as @e[type=superbwarfare:bmp_2,x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120] run data modify entity @s Health set value -99999f")

# 4. the Cobra
c("gscraft strike reset")
mark = LOG.stat().st_size
t0 = time.time()
c(f"gscraft strike air {X} {Y} {Z}")
heli_at, rockets, rounds, off, power, rotor, alt = None, 0, 0, False, None, None, None
while time.time() - t0 < 95:
    time.sleep(1)
    h = near("dragonrise_reforge:ah1f", 400)
    if h and heli_at is None:
        heli_at = time.time() - t0
    if h and time.time() - t0 - (heli_at or 0) >= 3 and power is None:
        # the engine: power held at full, the rotor turning (the mod's synched rotor lerps to the power)
        nbt = c(f"data get entity @e[type=dragonrise_reforge:ah1f,x={X - 400},y=-64,z={Z - 400},dx=800,dy=384,dz=800,limit=1] Power")
        rot = c(f"data get entity @e[type=dragonrise_reforge:ah1f,x={X - 400},y=-64,z={Z - 400},dx=800,dy=384,dz=800,limit=1] PropellerRot")
        power = (re.search(r"([\d.]+)f", nbt) or [None, None])[1]
        posn = c(f"data get entity @e[type=dragonrise_reforge:ah1f,x={X - 400},y=-64,z={Z - 400},dx=800,dy=384,dz=800,limit=1] Pos")
        alt = (re.search(r"d, (-?[\d.]+)d, ", posn) or [None, None])[1]
        rotor = (re.search(r"([\d.]+)f", rot) or [None, None])[1]
    rockets = max(rockets, near("superbwarfare:medium_rocket", 400))
    rounds = max(rounds, near("superbwarfare:projectile", 400))
    if "off station" in log_since(mark):
        off = time.time() - t0
        break
time.sleep(2)
left = near("dragonrise_reforge:ah1f", 400)
check("air: the Cobra within 35 s at full power with the rotor turning, rockets and rounds seen, off station within 60 s, none left",
      heli_at is not None and heli_at <= 25 and power is not None and float(power) >= 0.9 and rotor is not None and float(rotor) >= 0.5 and alt is not None and abs(float(alt) - (Y + 55)) <= 4 and rockets >= 1 and rounds >= 1 and off and off <= 65 and left == 0,
      f"heli at {heli_at and round(heli_at, 1)} s; power {power}; rotor {rotor}; height {alt} (want {Y + 55}); rockets {rockets}; rounds {rounds}; off at {off and round(off, 1)} s; left {left}")

c("gscraft strike reset")
c(f"kill @e[type=superbwarfare:mortar_shell]")
c(f"kill @e[type=superbwarfare:cannon_shell]")
c(f"kill @e[type=superbwarfare:medium_rocket]")
c(f"kill @e[type=superbwarfare:projectile]")
c(f"fill {X - 24} {Y - 1} {Z - 24} {X + 24} {Y + 6} {Z + 24} minecraft:air")
c(f"forceload remove {X - 80} {Z - 80} {X + 80} {Z + 80}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
