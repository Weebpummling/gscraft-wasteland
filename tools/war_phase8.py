"""Phase 8 of the enemy work, on the LOCAL server: sharper fighters, step B of the feasibility review - cover and
peeking (B1), hold and advance orders (B2), the Marksman flat at range (A3). Needs a ticking world and no player.
Run war_phase7.py and the rest after it.

The fights are staged on a fenced stone platform high in the air (y 200), forceloaded, so the world is untouched.

1. Cover: a rifleman under fire from a target 22 blocks off, with a wall segment to one side, ends up behind it -
   hidden from the target's eyes - and keeps firing from the lean (the target still takes damage).
2. Hold: an ordered fighter fires at a visible target without leaving its point.
3. Advance: an ordered fighter reaches a point 24 blocks away with a target in view.
4. Squad order: a Sergeant's hold reaches the riflemen within twenty blocks.
5. The Marksman goes flat to fire beyond 32 blocks.
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
HP = 'Health:2000f,Attributes:[{Name:"minecraft:generic.max_health",Base:2000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def val(sel, path):
    out = c(f"data get entity {sel} {path}")
    return out.split("entity data: ", 1)[1].strip() if "entity data: " in out else None


def fighter(sel):
    return c(f"gscraft fighter {sel}")


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "superbwarfare:hand_grenade"):
        c(f"kill @e[type={t},{AREA}]")


def arena():
    c(f"fill {X - 31} {Y - 1} {Z - 15} {X + 31} {Y + 4} {Z + 15} minecraft:air")
    c(f"fill {X - 30} {Y - 1} {Z - 14} {X + 30} {Y - 1} {Z + 14} minecraft:stone")
    c(f"fill {X - 31} {Y} {Z - 15} {X + 31} {Y + 1} {Z + 15} minecraft:stone hollow")
    c(f"fill {X - 30} {Y} {Z - 14} {X + 30} {Y + 3} {Z + 14} minecraft:air")


def pos_of(sel):
    p = val(sel, "Pos") or ""
    n = re.findall(r"-?[\d.]+(?=d)", p)
    return (float(n[0]), float(n[1]), float(n[2])) if len(n) == 3 else None


def health(sel):
    h = val(sel, "Health")
    return float(h[:-1]) if h and h.endswith("f") else None


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()

# 1. cover: the target at +11, the rifleman at -11 with a 4-wide, 3-high wall 5 blocks to its side (at x -6, z +4..+7)
arena()
c(f"fill {X - 6} {Y} {Z + 4} {X - 6} {Y + 2} {Z + 7} minecraft:stone")
c(f'summon gscraft:ruaf_soldier {X + 11} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p8t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 11} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p8c"]}}')
hidden_samples, seen_cover, trail = 0, "none", []
for i in range(24):
    time.sleep(1)
    info = fighter("@e[tag=p8c,limit=1]")
    m = re.search(r"cover (\S+ \S+ \S+|none), hidden from target (true|false)", info)
    if m:
        if m.group(1) != "none":
            seen_cover = m.group(1)
        if m.group(2) == "true":
            hidden_samples += 1
    trail.append((m.group(1)[:18] + "/" + m.group(2)) if m else "?")
hp = health("@e[tag=p8t,limit=1]")
check("a rifleman under fire takes cover behind the wall and keeps firing from the lean",
      seen_cover != "none" and hidden_samples >= 6 and hp is not None and hp < 2000.0,   # the pause counts down behind cover now, so the lean comes sooner and the hidden share is lower
      f"cover chosen {seen_cover}; hidden in {hidden_samples} of 24 samples; target health {hp}; trail {' '.join(trail[-8:])}")
clear()

# 2. hold: the fighter fires from its point and does not chase
arena()
c(f'summon gscraft:ruaf_soldier {X + 20} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p8t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 20} {Y} {Z} {{GscraftRank:"NATO Rifleman",Tags:["p8h"]}}')
time.sleep(0.5)
order = c(f"gscraft fighter @e[tag=p8h,limit=1] hold {X - 20} {Y} {Z} now")
far = 0.0
for i in range(15):
    time.sleep(1)
    p = pos_of("@e[tag=p8h,limit=1]")
    if p:
        far = max(far, ((p[0] - (X - 20 + 0.5)) ** 2 + (p[2] - (Z + 0.5)) ** 2) ** 0.5)
hp = health("@e[tag=p8t,limit=1]")
info = fighter("@e[tag=p8h,limit=1]")
check("a holding fighter fires at a target 40 blocks off without leaving its point", "order HOLD" in info and far <= 4.0 and hp is not None and hp < 2000.0,
      f"{order}; furthest from the point {far:.1f} blocks; target health {hp}")
clear()

# 3. advance: the fighter reaches the ordered point with a target in view
arena()
c(f'summon gscraft:ruaf_soldier {X + 26} {Y} {Z + 10} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p8t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 20} {Y} {Z - 10} {{GscraftRank:"NATO Rifleman",Tags:["p8a"]}}')
time.sleep(0.5)
order = c(f"gscraft fighter @e[tag=p8a,limit=1] advance {X + 4} {Y} {Z - 10} now")
arrived = None
for i in range(25):
    time.sleep(1)
    p = pos_of("@e[tag=p8a,limit=1]")
    if p and ((p[0] - (X + 4.5)) ** 2 + (p[2] - (Z - 9.5)) ** 2) ** 0.5 <= 3.0:
        arrived = i + 1
        break
info = fighter("@e[tag=p8a,limit=1]")
check("an advancing fighter reaches its point and holds there", arrived is not None and "order HOLD" in info, f"{order}; arrived after {arrived} s; {info[-60:]}")
clear()

# 4. a Sergeant's order reaches the squad
arena()
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{GscraftRank:"NATO Sergeant",Tags:["p8s"]}}')
c(f'summon gscraft:nato_soldier {X + 6} {Y} {Z + 3} {{GscraftRank:"NATO Rifleman",Tags:["p8m"]}}')
c(f'summon gscraft:nato_soldier {X - 6} {Y} {Z - 3} {{GscraftRank:"NATO Rifleman",Tags:["p8m"]}}')
time.sleep(0.5)
order = c(f"gscraft fighter @e[tag=p8s,limit=1] squadhold {X} {Y} {Z + 8} now")
time.sleep(1)
c(f"tag @e[tag=p8m,limit=1,sort=nearest,x={X + 6},y={Y},z={Z + 3}] add p8m1")
ordered = sum(1 for sel in ("@e[tag=p8s,limit=1]", "@e[tag=p8m1,limit=1]", "@e[tag=p8m,tag=!p8m1,limit=1]") if "order HOLD" in fighter(sel))
check("a Sergeant's hold reaches the riflemen within twenty blocks", re.search(r"([3-9]) ordered", order) is not None and ordered == 3, f"{order}; holding {ordered} of 3")
clear()

# 5. the Marksman flat beyond 32 blocks
arena()
c(f'summon gscraft:ruaf_soldier {X + 20} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["p8t"],{HP}}}')
c(f'summon gscraft:nato_soldier {X - 20} {Y} {Z} {{GscraftRank:"NATO Marksman",Tags:["p8k"]}}')
flat = None
for i in range(20):
    time.sleep(1)
    info = fighter("@e[tag=p8k,limit=1]")
    if "pose SWIMMING" in info:
        flat = info
        break
check("the Marksman goes flat to fire beyond 32 blocks", flat is not None, (flat or info)[:160])
clear()
c(f"fill {X - 31} {Y - 1} {Z - 15} {X + 31} {Y + 4} {Z + 15} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors in the log", not bad, f"{len(bad)} lines")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
