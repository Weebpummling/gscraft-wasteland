"""Phase 22, the armour damage pass and the bail-out on the LOCAL server (owner 2026-09-12). Needs a ticking world,
no player, and the override datapack installed (tools/armour_override.py --install, then /reload).

1. The light list: a Superb Warfare rocket's direct hit (projectile_hit 450) takes a BMP-2 down by about 160 (the
   mod then scales by the angle: 0.85 from the front, more from behind), so two finish it; a TACZ bullet type does
   nothing.
2. The heavy list: the same on a T-90A takes about 125; a Javelin's type on it is by the heavy share.
3. The bail-out: a BMP-2 hit down under a tenth of its health loses its crew - a crewman soldier appears beside it
   in the crewman's kit (no helmet, a pistol), the crew entity is out of the seat, the message is logged - and
   the driver still reports the wreck (destroyed, loot) when the hull is finished.
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
AREA = f"x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120"
HP = 'Health:20000f,Attributes:[{Name:"minecraft:generic.max_health",Base:20000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier"):
        c(f"kill @e[type={t},tag=!p22k,{AREA}]")
    time.sleep(1)
    c(f"kill @e[type=minecraft:item,{AREA}]")   # a killed vehicle's loot lands a tick later


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def health(t):
    return num(c(f"gscraft vehicle status @e[type={t},limit=1]"), r"health ([-\d.]+)/")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


c("gscraft director pause")
c(f"forceload add {X - 60} {Z - 60} {X + 60} {Z + 60}")
time.sleep(4)
clear()
L.fill(r, X - 50, Y - 1, Z - 50, X + 50, Y + 5, Z + 50, "minecraft:air")
L.fill(r, X - 50, Y - 1, Z - 50, X + 50, Y - 1, Z + 50, "minecraft:stone")
c(f'summon gscraft:ruaf_soldier {X} {Y} {Z + 20} {{Tags:["p22k"],NoAI:1b,GscraftRank:"RUAF Rifleman",{HP}}}')
time.sleep(1)

# 1. light
c(f"gscraft vehicle spawn superbwarfare:bmp_2 ruaf {X} {Y} {Z}")
time.sleep(2)
h0 = health("superbwarfare:bmp_2")
c("gscraft vehicle hit @e[type=superbwarfare:bmp_2,limit=1] superbwarfare:projectile_hit 450 @e[tag=p22k,limit=1]")
time.sleep(1)
h1 = health("superbwarfare:bmp_2")
c("gscraft vehicle hit @e[type=superbwarfare:bmp_2,limit=1] tacz:bullet 450 @e[tag=p22k,limit=1]")
time.sleep(1)
h2 = health("superbwarfare:bmp_2")
rocket = h0 is not None and h1 is not None and 125 <= h0 - h1 <= 185   # 450 x 0.35, then the mod's own angle factor (0.85 from the front)
bullet = h1 is not None and h2 is not None and abs(h1 - h2) < 0.5
check("light: an SW rocket's hit takes about 160 (less from the front), a TACZ bullet type nothing", rocket and bullet, f"health {h0} -> {h1} -> {h2}")
clear()

# 2. heavy
c(f"gscraft vehicle spawn superbwarfare:t_90a ruaf {X} {Y} {Z}")
time.sleep(2)
h0 = health("superbwarfare:t_90a")
c("gscraft vehicle hit @e[type=superbwarfare:t_90a,limit=1] superbwarfare:projectile_hit 450 @e[tag=p22k,limit=1]")
time.sleep(1)
h1 = health("superbwarfare:t_90a")
check("heavy: the same hit takes about 125", h0 is not None and h1 is not None and 80 <= h0 - h1 <= 170, f"health {h0} -> {h1}")
clear()

# 3. the bail-out
c(f"gscraft vehicle spawn superbwarfare:bmp_2 nato {X} {Y} {Z}")
time.sleep(2)
crews0 = count(f"@e[type=gscraft:crew,{AREA}]")
mark = LOG.stat().st_size
c("gscraft vehicle hit @e[type=superbwarfare:bmp_2,limit=1] superbwarfare:projectile_hit 950 @e[tag=p22k,limit=1]")
time.sleep(3)
h = health("superbwarfare:bmp_2")
st = c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]")
crewmen = count(f"@e[type=gscraft:nato_soldier,{AREA}]")
kit = c("data get entity @e[type=gscraft:nato_soldier,limit=1] HandItems[0].tag.GunId")   # every TACZ gun is one item; the gun is in its tag
helmet = c("data get entity @e[type=gscraft:nato_soldier,limit=1] ArmorItems[3].id")   # an empty slot has no id
rank = c("data get entity @e[type=gscraft:nato_soldier,limit=1] CustomName")
bailed = "bails out" in log_since(mark)
seat_empty = "passengers 0" in st
check("a BMP-2 under a tenth of health loses its crew: a crewman with a pistol and no helmet, the seat empty, told",
      h is not None and 0 < h <= 30 and crewmen >= 1 and "glock" in kit and ("air" in helmet.lower() or "no elements" in helmet.lower()) and "Crewman" in rank and bailed and seat_empty,
      f"health {h}; crews before {crews0}; crewmen {crewmen}; gun [{kit[-24:]}]; helmet [{helmet[-30:]}]; rank [{rank[-30:]}]; bailed {bailed}; seat empty {seat_empty}")
mark2 = LOG.stat().st_size
c("gscraft vehicle hit @e[type=superbwarfare:bmp_2,limit=1] minecraft:explosion 3000 @e[tag=p22k,limit=1]")
time.sleep(3)
new = log_since(mark2)
items = count(f"@e[type=minecraft:item,{AREA}]")
check("the bailed driver still reports the wreck and drops its loot", "destroyed" in new and items > 0, f"destroyed logged {'destroyed' in new}; items {items}")

c("kill @e[tag=p22k]")
clear()
L.fill(r, X - 50, Y - 1, Z - 50, X + 50, Y + 5, Z + 50, "minecraft:air")
c(f"forceload remove {X - 60} {Z - 60} {X + 60} {Z + 60}")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
