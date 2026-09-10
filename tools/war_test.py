"""Phase 1 soldier test on the LOCAL server (127.0.0.1), no player needed.

1. A RUAF soldier summoned plain goes through finalizeSpawn and is dressed: rank name, armour, TACZ gun.
2. It fires that gun at zombies: "[gscraft] ... shoot ->" lines in the log, and the zombies die.
3. A NATO and a RUAF soldier fight each other; two RUAF soldiers side by side do not.

Armour visibility cannot be proven from here - that is the in-person check in the test instance.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
X, Z = -2000, -600
AREA = f"x={X},z={Z},distance=..60"
CLEAR = ["minecraft:zombie", "minecraft:husk", "minecraft:zombie_villager", "gscraft:nato_soldier",
         "gscraft:ruaf_soldier", "minecraft:pillager", "minecraft:vindicator", "dragonrise_reforge:terrorist",
         "immersiveengineering:commando", "immersiveengineering:fusilier", "immersiveengineering:bulwark"]

r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")


def c(cmd, t=30):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def at(dx, dz):
    return f"execute positioned {X + dx} 0 {Z + dz} positioned over motion_blocking_no_leaves run "


def clear():
    for t in CLEAR:
        c(f"kill @e[type={t},{AREA}]")


def health(sel):
    out = c(f"data get entity {sel} Health")
    m = re.search(r"([\d.]+)f?$", out)
    return m.group(1) if m else out[:60]


log_start = LOG.stat().st_size
c(f"forceload add {X - 60} {Z - 60} {X + 60} {Z + 60}", 60)
time.sleep(5)
clear()

print("== 1. dressing (plain summon, finalizeSpawn path)")
print("  ", c(at(0, 0) + "summon gscraft:ruaf_soldier ~ ~ ~"))
time.sleep(2)
soldier = f"@e[type=gscraft:ruaf_soldier,{AREA},limit=1]"
for field in ("CustomName", "ArmorItems", "HandItems"):
    print(f"   {field}: {c(f'data get entity {soldier} {field}')[:420]}")

print("\n== 2. RUAF soldier against three zombies 14 blocks off")
for i in range(3):
    c(at(14, -4 + 4 * i) + 'summon minecraft:zombie ~ ~ ~ {Tags:["gs_placed"],'
      'ArmorItems:[{},{},{},{id:"minecraft:leather_helmet",Count:1b}]}')
time.sleep(1)
print(f"   placed: zombies {count(f'@e[type=minecraft:zombie,{AREA}]')}")
waited = 0
for mark in (10, 20, 35, 50):
    time.sleep(mark - waited)
    waited = mark
    z = count(f"@e[type=minecraft:zombie,{AREA}]")
    s = count(f"@e[type=gscraft:ruaf_soldier,{AREA}]")
    print(f"   t+{mark:2d}s  zombies alive {z}  soldier alive {s}  soldier health {health(soldier) if s else '-'}")
    if z == 0:
        break
clear()

print("\n== 3a. NATO against RUAF, 20 blocks apart")
c(at(-10, 0) + "summon gscraft:nato_soldier ~ ~ ~")
c(at(10, 0) + "summon gscraft:ruaf_soldier ~ ~ ~")
waited = 0
for mark in (10, 25, 45):
    time.sleep(mark - waited)
    waited = mark
    n = count(f"@e[type=gscraft:nato_soldier,{AREA}]")
    u = count(f"@e[type=gscraft:ruaf_soldier,{AREA}]")
    nh = health(f"@e[type=gscraft:nato_soldier,{AREA},limit=1]") if n else "-"
    uh = health(f"@e[type=gscraft:ruaf_soldier,{AREA},limit=1]") if u else "-"
    print(f"   t+{mark:2d}s  NATO {n} (hp {nh})  RUAF {u} (hp {uh})")
    if n == 0 or u == 0:
        break
clear()

print("\n== 3b. two RUAF soldiers side by side for 15s (should not fight)")
c(at(-3, 0) + "summon gscraft:ruaf_soldier ~ ~ ~")
c(at(3, 0) + "summon gscraft:ruaf_soldier ~ ~ ~")
time.sleep(15)
hp = [health(f"@e[type=gscraft:ruaf_soldier,{AREA},limit=1,sort=nearest]"),
      health(f"@e[type=gscraft:ruaf_soldier,{AREA},limit=1,sort=furthest]")]
print(f"   RUAF alive {count(f'@e[type=gscraft:ruaf_soldier,{AREA}]')}  health {hp}")
clear()

c(f"forceload remove {X - 60} {Z - 60} {X + 60} {Z + 60}", 60)
r.close()

print("\n== log lines from gscraft during the test")
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
lines = [l for l in new.splitlines() if "gscraft" in l.lower() and ("shoot" in l or "kit" in l or "ERROR" in l or "Exception" in l)]
seen = set()
for l in lines:
    key = re.sub(r"^\[[^\]]*\]\s*", "", l)
    if key not in seen:
        seen.add(key)
        print("  ", l[:200])
print(f"   ({len(lines)} matching lines, {len(seen)} distinct)")
