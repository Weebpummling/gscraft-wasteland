"""Phase 24, the riders' dismount on the LOCAL server (owner 2026-09-12: riders "don't dismount until much later even
in active combat"). Needs a ticking world and no player.

1. A BMP-2 with four riders aboard is hit (the crew's alert): the riders are out within two seconds.
2. A BMP-2 with four riders aboard and no threat in reach keeps them; a rider hit in the bay puts the bay out at
   once.
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
AREA = f"x={X - 60},y={Y - 10},z={Z - 60},dx=120,dy=40,dz=120"
HP = 'Health:20000f,Attributes:[{Name:"minecraft:generic.max_health",Base:20000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier"):
        c(f"kill @e[type={t},tag=!p24k,{AREA}]")
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2"):
        c(f"execute as @e[type={t},{AREA}] run data modify entity @s Health set value -9999f")
    time.sleep(1)
    c(f"kill @e[type=minecraft:item,{AREA}]")


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def riders():
    return num(c("gscraft vehicle status @e[type=superbwarfare:bmp_2,limit=1]"), r"riders (\d+)")


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
c(f'summon gscraft:nato_soldier {X} {Y} {Z + 40} {{Tags:["p24k"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)

# 1. the hull is hit: the bay comes out
c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 4")
time.sleep(3)
aboard0 = riders()
mark = LOG.stat().st_size
c("gscraft vehicle hit @e[type=superbwarfare:bmp_2,limit=1] superbwarfare:projectile_hit 100 @e[tag=p24k,limit=1]")
out_in = None
for i in range(8):
    time.sleep(0.5)
    if riders() == 0:
        out_in = (i + 1) * 0.5
        break
told = "dismount" in log_since(mark)
check("a hit on the hull puts the riders out within two seconds", aboard0 is not None and aboard0 >= 3 and out_in is not None and out_in <= 2.0 and told,
      f"aboard before {aboard0}; out after {out_in} s; dismount logged {told}")
c("kill @e[tag=p24k]")   # a hostile soldier in reach is a threat of its own: the crew's cone sweeps it when the hull turns at the road's end
clear()

# 2. no threat: they stay; a rider hit: the bay comes out
c(f"gscraft director armour {X} {Y} {Z} superbwarfare:bmp_2 4")
time.sleep(3)
aboard0 = riders()
time.sleep(4)
aboard1 = riders()
c(f"execute as @e[type=gscraft:ruaf_soldier,{AREA},limit=1] run damage @s 1 minecraft:generic")
time.sleep(1)
aboard2 = riders()
check("with no threat the riders stay aboard; a rider hit in the bay puts the bay out", aboard0 is not None and aboard0 >= 3 and aboard1 == aboard0 and aboard2 == 0,
      f"aboard {aboard0} -> {aboard1} after 4 s -> {aboard2} after a rider was hit")

c("kill @e[tag=p24k]")
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
