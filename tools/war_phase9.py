"""Phase 9 of the enemy work, on the LOCAL server: sharper fighters, step C of the feasibility review - squads with
slots and formations (C1), patrol routes (C2), bounding overwatch (C3), the fall-back (C4). Needs a ticking world
and no player. Run war_phase8.py and the rest after it.

Staged on a fenced stone platform at y 200, forceloaded.

1. A squad of four holds its wedge behind the leader; a line spreads it abreast.
2. The leader walks a route: two waypoints reached in order, the members following.
3. Bounding: against a target 50 blocks off the squad closes in alternating teams - over the approach some members
   advance while others hold, and the squad's distance to the target shrinks.
4. Fall-back: with two of four killed the leader calls the squad back and the squad's distance to the target grows.
5. The director's groups arrive as squads.
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
AREA = f"x={X - 70},y={Y - 10},z={Z - 70},dx=140,dy=40,dz=140"
HP = 'Health:2000f,Attributes:[{Name:"minecraft:generic.max_health",Base:2000}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def val(sel, path):
    out = c(f"data get entity {sel} {path}")
    return out.split("entity data: ", 1)[1].strip() if "entity data: " in out else None


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "superbwarfare:hand_grenade", "minecraft:zombie", "minecraft:husk"):
        c(f"kill @e[type={t},{AREA}]")


def arena():
    c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
    c(f"fill {X - 40} {Y - 1} {Z - 20} {X + 40} {Y - 1} {Z + 20} minecraft:stone")
    c(f"fill {X - 41} {Y} {Z - 21} {X + 41} {Y + 1} {Z + 21} minecraft:stone hollow")
    c(f"fill {X - 40} {Y} {Z - 20} {X + 40} {Y + 3} {Z + 20} minecraft:air")


def pos_of(sel):
    p = val(sel, "Pos") or ""
    n = re.findall(r"-?[\d.]+(?=d)", p)
    return (float(n[0]), float(n[1]), float(n[2])) if len(n) == 3 else None


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def squad(tags, x0=X - 30):
    """summon a Sergeant and three Riflemen, tag them s0..s3, form the squad; returns the leader selector"""
    c(f'summon gscraft:nato_soldier {x0} {Y} {Z} {{GscraftRank:"NATO Sergeant",Tags:["{tags}","{tags}0"]}}')
    for i in (1, 2, 3):
        c(f'summon gscraft:nato_soldier {x0 + i} {Y} {Z + i} {{GscraftRank:"NATO Rifleman",Tags:["{tags}","{tags}{i}"]}}')
    time.sleep(0.5)
    return c(f"gscraft squad @e[tag={tags}0,limit=1] form")


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()

# 1. formation: the leader advances 30 blocks east; the members end up in their wedge slots, then a line
arena()
formed = squad("q1")
c(f"gscraft fighter @e[tag=q10,limit=1] advance {X} {Y} {Z} now")
time.sleep(14)
lead = pos_of("@e[tag=q10,limit=1]")
members = [pos_of(f"@e[tag=q1{i},limit=1]") for i in (1, 2, 3)]
info = c("gscraft squad @e[tag=q11,limit=1]")
behind = sum(1 for m in members if m and lead and m[0] < lead[0] - 0.5 and dist(m, lead) <= 7.0)
c("gscraft squad @e[tag=q10,limit=1] formation line")
time.sleep(8)
lead2 = pos_of("@e[tag=q10,limit=1]")
members2 = [pos_of(f"@e[tag=q1{i},limit=1]") for i in (1, 2, 3)]
abreast = sum(1 for m in members2 if m and lead2 and abs(m[0] - lead2[0]) <= 2.5 and 1.0 <= abs(m[2] - lead2[2]) <= 9.0)
check("a squad holds its wedge behind the leader, then a line abreast", "squad formed: 4" in formed and behind >= 2 and abreast >= 2 and "slot 1 of 4" in info,
      f"{formed}; wedge: {behind} of 3 behind and near; line: {abreast} of 3 abreast; {info[:120]}")
clear()

# 2. the patrol: two waypoints in order, the squad following (a patrol walks only with someone within 96: a phantom stands in)
arena()
c(f"gscraft director phantom set {X} {Y} {Z}")
formed = squad("q2")
c(f"gscraft squad @e[tag=q20,limit=1] route {X} {Z + 12} {X + 25} {Z - 12}")
# the leader passes a waypoint at up to 2.5 blocks a second, so a once-a-second position sample can miss the arrival;
# the goal's own route index (in the squad readout) says which waypoint it is on, and it moves 0 -> 1 -> 0 round the loop
reached = []
t0 = time.time()
last_at = "0"
while time.time() - t0 < 40 and len(reached) < 2:
    time.sleep(1)
    m = re.search(r"route 2 points at (\d)", c("gscraft squad @e[tag=q20,limit=1]"))
    if m is None:
        break
    if m.group(1) != last_at:
        p = pos_of("@e[tag=q20,limit=1]")
        wp = [(X, Y, Z + 12), (X + 25, Y, Z - 12)][len(reached)]
        reached.append((round(time.time() - t0), round(dist(p, wp), 1) if p else None))
        last_at = m.group(1)
lead = pos_of("@e[tag=q20,limit=1]")
near = sum(1 for i in (1, 2, 3) if (m := pos_of(f"@e[tag=q2{i},limit=1]")) and lead and dist(m, lead) <= 10.0)
check("the leader walks its route waypoint by waypoint and the squad follows", len(reached) == 2 and all(d is not None and d <= 5.0 for _, d in reached) and near >= 2,
      f"waypoints reached at (s, blocks off) {reached}; members within 10 of the leader at the end: {near} of 3")
c("gscraft director phantom clear")
clear()

# 3. bounding overwatch toward a target 45 blocks off (past the Rifleman's hold of 24 x 1.2, within the follow range of 64)
arena()
c(f'summon gscraft:ruaf_soldier {X + 15} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["q3t"],{HP}}}')
formed = squad("q3")
c(f"tag @e[tag=q3] add q3all")
start = [pos_of(f"@e[tag=q3{i},limit=1]") for i in range(4)]
mixed_samples = 0
prev = start
for i in range(16):
    time.sleep(1)
    now = [pos_of(f"@e[tag=q3{i},limit=1]") for i in range(4)]
    moved = [a and b and dist(a, b) > 0.8 for a, b in zip(prev, now)]
    if any(moved) and not all(moved):
        mixed_samples += 1
    prev = now
target = pos_of("@e[tag=q3t,limit=1]")
before = sum(dist(p, target) for p in start if p) / max(1, sum(1 for p in start if p))
after = sum(dist(p, target) for p in prev if p) / max(1, sum(1 for p in prev if p))
orders = c("gscraft squad @e[tag=q31,limit=1]")
check("the squad bounds toward a distant target: some move while others hold, and it closes",
      mixed_samples >= 3 and after < before - 6.0, f"mixed samples {mixed_samples} of 16; mean distance {before:.1f} -> {after:.1f}; {orders[-40:]}; at {[tuple(round(v) for v in p) if p else None for p in prev]}")
clear()

# 4. the fall-back: two of four killed under fire
arena()
c(f'summon gscraft:ruaf_soldier {X + 30} {Y} {Z} {{NoAI:1b,GscraftRank:"RUAF Rifleman",Tags:["q4t"],{HP}}}')
formed = squad("q4", X - 10)
time.sleep(3)
c("kill @e[tag=q42]")
c("kill @e[tag=q43]")
start = [pos_of(f"@e[tag=q4{i},limit=1]") for i in (0, 1)]
target = pos_of("@e[tag=q4t,limit=1]")
fell = None
for i in range(12):
    time.sleep(1)
    o = c("gscraft squad @e[tag=q40,limit=1]")
    if "ADVANCE (squad)" in o or "HOLD (squad)" in o:
        fell = o
    now = [pos_of(f"@e[tag=q4{i},limit=1]") for i in (0, 1)]
before = sum(dist(p, target) for p in start if p) / 2
after = sum(dist(p, target) for p in now if p) / max(1, sum(1 for p in now if p))
check("under half strength the leader calls the fall-back and the squad withdraws", fell is not None and after > before + 5.0,
      f"mean distance to the target {before:.1f} -> {after:.1f}; {(fell or o)[-60:]}")
clear()
c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")

# 5. the director's groups are squads: passes at the western outpost (out_w1: RUAF 5, the Dead 2 - the switchyard's
# mix is mostly the Dead, which are no squad, and six passes there missed a fighter group one run in five)
OX, OZ = -1500, -1060
OUT = f"x={OX - 100},y=-64,z={OZ - 100},dx=200,dy=400,dz=200"
c(f"forceload add {OX - 64} {OZ - 64} {OX + 64} {OZ + 64}")
time.sleep(10)
c(f'execute positioned {OX} 0 {OZ} positioned over motion_blocking_no_leaves run summon minecraft:armor_stand ~ ~ ~ {{Tags:["ymark9"],Invisible:1b}}')
oy_text = c("data get entity @e[tag=ymark9,limit=1] Pos")
c("kill @e[tag=ymark9]")
oy_n = re.findall(r"-?[\d.]+(?=d)", oy_text)
oy = int(float(oy_n[1])) if len(oy_n) == 3 else 66
c(f"kill @e[tag=gs_director,{OUT}]")
c(f"kill @e[tag=gs_garrison_out_w1,{OUT}]")
placed, info, reply = 0, "none placed", ""
for attempt in range(6):
    reply = c(f"gscraft director ambient {OX} {oy} {OZ} 1")
    time.sleep(1)
    for t in ("nato_soldier", "ruaf_soldier", "scavenger"):
        placed = count(f"@e[type=gscraft:{t},tag=gs_director,{OUT}]")
        if placed:
            info = c(f"gscraft squad @e[type=gscraft:{t},tag=gs_director,{OUT},limit=1]")
            break
    if placed:
        break
    c(f"kill @e[tag=gs_director,{OUT}]")
check("the director's groups arrive as squads", placed >= 2 and "squad " in info and "slot" in info, f"{reply[:70]}; placed {placed}; {info[:140]}")
# ...and are walking: the leader has a route and the squad moves once someone is near (the outpost has no patrol route of its own)
c(f"gscraft director phantom set {OX} {oy} {OZ}")
sel = None
for t in ("nato_soldier", "ruaf_soldier", "scavenger"):
    if count(f"@e[type=gscraft:{t},tag=gs_director,{OUT}]"):
        sel = f"@e[type=gscraft:{t},tag=gs_director,{OUT},sort=arbitrary,limit=1]"
        break
walk_info = c(f"gscraft squad {sel}") if sel else "none"
w0 = pos_of(sel) if sel else None
time.sleep(10)
w1 = pos_of(sel) if sel else None
moved = dist(w0, w1) if w0 and w1 else None
c("gscraft director phantom clear")
check("a placed squad is on a walk of its own and moving", "route " in walk_info and moved is not None and moved > 4.0,
      f"{walk_info[walk_info.find('route'):][:30] if 'route' in walk_info else walk_info[:60]}; a member moved {moved and round(moved, 1)} blocks in 10 s")
c(f"kill @e[tag=gs_director,{OUT}]")
c(f"forceload remove {OX - 64} {OZ - 64} {OX + 64} {OZ + 64}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
fell_lines = [l for l in new.splitlines() if "falls back" in l]
check("the fall-back was logged and no gscraft errors", fell_lines and not bad, f"fall-back lines {len(fell_lines)}, error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
