"""Phase 23, armour against armour on the LOCAL server (owner 2026-09-12: "the APCs seem not to engage each other").
Needs a ticking world and no player.

1. A RUAF BMP-2 and a NATO Bradley placed 50 blocks apart, facing each other, engage: within 30 s one of them has
   lost health, both crews logged the engagement, and neither ever left the cannon (the missile's magazine of one
   never reloads for a mob).
2. The chat setting is off by default (armour.chat 0) and the lines still reach the log.
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


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2", "gscraft:crew", "gscraft:nato_soldier", "gscraft:ruaf_soldier"):
        c(f"kill @e[type={t},{AREA}]")
    # a wreck ignores /kill and burns down on its own: its health set under minus the maximum removes it next tick
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley", "superbwarfare:t_90a", "superbwarfare:m_1a_2"):
        c(f"execute as @e[type={t},{AREA}] run data modify entity @s Health set value -9999f")
    time.sleep(1)
    c(f"kill @e[type=minecraft:item,{AREA}]")


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def status(t):
    return c(f"gscraft vehicle status @e[type={t},limit=1]")


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
time.sleep(1)

# 1. the duel: a BMP-2 at x-25 facing +x (yaw -90), a Bradley at x+25 facing -x (yaw 90)
mark = LOG.stat().st_size
c(f"execute positioned {X - 25} {Y} {Z} rotated -90 0 run gscraft vehicle spawn superbwarfare:bmp_2 ruaf")
c(f"execute positioned {X + 25} {Y} {Z} rotated 90 0 run gscraft vehicle spawn superbwarfare:bradley nato")
time.sleep(2)
h_bmp0 = num(status("superbwarfare:bmp_2"), r"health ([-\d.]+)/")
h_brad0 = num(status("superbwarfare:bradley"), r"health ([-\d.]+)/")
weapons = set()
for i in range(30):
    time.sleep(1)
    for t in ("superbwarfare:bmp_2", "superbwarfare:bradley"):
        w = num(status(t), r"weapon (\d+)")
        if w is not None:
            weapons.add(int(w))
st_bmp = status("superbwarfare:bmp_2")
st_brad = status("superbwarfare:bradley")
h_bmp1 = num(st_bmp, r"health ([-\d.]+)/")
h_brad1 = num(st_brad, r"health ([-\d.]+)/")
new = log_since(mark)
engaged = new.count("engages entity.gscraft.crew")
lost = 0.0
for a, b in ((h_bmp0, h_bmp1), (h_brad0, h_brad1)):
    if a is not None and b is not None:
        lost = max(lost, a - b)
check("two APCs 50 blocks apart engage: one has lost health within 30 s, both engaged, the cannon throughout",
      lost >= 30.0 and engaged >= 2 and weapons <= {0},
      f"BMP-2 {h_bmp0} -> {h_bmp1}, Bradley {h_brad0} -> {h_brad1}; engage lines {engaged}; weapons seen {sorted(weapons)}")
print("    ", st_bmp[:150])
print("    ", st_brad[:150])

# 2. the chat setting
settings = c("gscraft settings armour.chat")
check("the chat lines are off by default and the log still has them", "armour.chat = 0" in settings and ("dismount" in new or "engages" in new), f"[{settings[-60:]}]")

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
