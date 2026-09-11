"""Phase 10 of the enemy work, on the LOCAL server: resource handling (owner, 2026-09-11). Needs a ticking world and
no player; the director's phantoms stand in for players.

1. A garrison does not count against the ambient cap of its zone.
2. The player ceiling: with twelve director creatures around a point, nothing more is placed there.
3. The sweep's grace: a placement 150 blocks from the only phantom survives one pass and goes on the second; one at
   100 stays.
4. A garrison with nobody within 256 for three passes is taken back, and refills at once when someone returns.
5. A site's assault with nobody within 128 freezes its clock and takes the wave back after a minute; the next wave
   comes when someone is back.
6. A patrol leader waits with nobody within 96 and walks when a phantom is there.
7. The bench: the cost of one director pass for one player, four together, and four spread out; the creature
   totals stay under the ceilings.
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
X, Z = -2000, -600
CAMP_AREA = f"x={X - 120},y=-64,z={Z - 120},dx=240,dy=400,dz=240"
OUTPOST = (-1500, -1060)                  # out_w1: RUAF garrison of four
OUT_AREA = f"x={OUTPOST[0] - 100},y=-64,z={OUTPOST[1] - 100},dx=200,dy=400,dz=200"
HOSP = "x=-881,y=-64,z=-1328,dx=200,dy=400,dz=103"
LOADS = [(-881, -1328, -682, -1226), (-900, -1140, -840, -1080), (-975, -1010, -905, -950)]
ANCHOR = (-782, -1277)


def c(cmd, t=120):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def surface_y(x, z):
    c(f'execute positioned {x} 0 {z} positioned over motion_blocking_no_leaves run summon minecraft:armor_stand ~ ~ ~ {{Tags:["ymark"],Invisible:1b}}')
    p = c("data get entity @e[tag=ymark,limit=1] Pos")
    c("kill @e[tag=ymark]")
    n = re.findall(r"-?[\d.]+(?=d)", p)
    return int(float(n[1])) if len(n) == 3 else 64


def pos_of(sel):
    p = c(f"data get entity {sel} Pos")
    n = re.findall(r"-?[\d.]+(?=d)", p)
    return tuple(float(v) for v in n) if len(n) == 3 else None


def kill_director(area):
    c(f"kill @e[tag=gs_director,{area}]")


def counted(reply):
    m = re.search(r"counted here (\d+) of cap (\d+)", reply)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


c("gscraft director phantom clear")
c("gscraft director pause")   # the bench runs the passes; the director's own tick would run with the phantoms too
c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
c(f"forceload add {OUTPOST[0] - 64} {OUTPOST[1] - 64} {OUTPOST[0] + 64} {OUTPOST[1] + 64}")
time.sleep(8)
kill_director(CAMP_AREA)
kill_director(OUT_AREA)
c(f"kill @e[tag=gs_garrison_out_w1,{OUT_AREA}]")

# 1. the garrison is not ambient
oy = surface_y(*OUTPOST)
c("gscraft garrison out_w1 force")
time.sleep(1)
garrison = count(f"@e[tag=gs_garrison_out_w1,{OUT_AREA}]")
reply = c(f"gscraft director ambient {OUTPOST[0]} {oy} {OUTPOST[1]} 1")
n, cap = counted(reply)
group = count(f"@e[tag=gs_director,{OUT_AREA}]") - garrison
check("a garrison does not count against its zone's ambient cap", garrison >= 3 and n is not None and n <= 4 and group >= 2,
      f"garrison {garrison}; ambient placed a group of {group}; {reply[:110]}")
kill_director(OUT_AREA)
c(f"kill @e[tag=gs_garrison_out_w1,{OUT_AREA}]")

# 2. the player ceiling
cy = surface_y(X, Z)
c(f"gscraft director pass {X} {Z} 12")
time.sleep(1)
around = count(f"@e[tag=gs_director,{CAMP_AREA}]")
reply = c(f"gscraft director ambient {X} {cy} {Z} 3")
after = count(f"@e[tag=gs_director,{CAMP_AREA}]")
check("at the player ceiling nothing more is placed", around >= 12 and after == around, f"{around} around, then {after} after three ambient passes; {reply[:90]}")
kill_director(CAMP_AREA)

# 3. the sweep's grace, measured from a phantom
c(f"gscraft director phantom set {X} {cy} {Z}")
c(f"forceload add {X + 100} {Z - 16} {X + 170} {Z + 16}")   # the far column is outside the camp's loaded square
time.sleep(4)
c(f'summon gscraft:nato_soldier {X + 150} {surface_y(X + 150, Z)} {Z} {{Tags:["gs_director","gs_placed","sw_far"],GscraftRank:"NATO Rifleman",NoAI:1b}}')
c(f'summon gscraft:nato_soldier {X + 100} {surface_y(X + 100, Z)} {Z} {{Tags:["gs_director","gs_placed","sw_near"],GscraftRank:"NATO Rifleman",NoAI:1b}}')
time.sleep(0.5)
zero = (count("@e[tag=sw_far]"), count("@e[tag=sw_near]"))
c("gscraft director bench 1")
one = (count("@e[tag=sw_far]"), count("@e[tag=sw_near]"))
c("gscraft director bench 1")
two = (count("@e[tag=sw_far]"), count("@e[tag=sw_near]"))
check("the sweep takes a far placement on the second pass and leaves a near one", zero == (1, 1) and one == (1, 1) and two == (0, 1), f"far/near before {zero}, after one pass {one}, after two {two}")
kill_director(CAMP_AREA)
c("kill @e[tag=sw_far]")
c(f"forceload remove {X + 100} {Z - 16} {X + 170} {Z + 16}")

# 4. a garrison rests when nobody is within 256, and refills at once when someone returns
c("gscraft garrison out_w1 force")
time.sleep(1)
before = count(f"@e[tag=gs_garrison_out_w1,{OUT_AREA}]")
c(f"gscraft director phantom set {X} {cy} {Z}")          # the camp, 640 blocks from the outpost
c("gscraft director bench 3")
rested = count(f"@e[tag=gs_garrison_out_w1,{OUT_AREA}]")
c(f"gscraft director phantom set {OUTPOST[0]} {oy} {OUTPOST[1]}")
c("gscraft director bench 1")
back = count(f"@e[tag=gs_garrison_out_w1,{OUT_AREA}]")
check("a garrison with nobody within 256 for three passes rests, and refills on return", before >= 3 and rested == 0 and back >= 3,
      f"garrison {before} -> {rested} after three passes with everyone 640 away -> {back} one pass after a return")
kill_director(OUT_AREA)
c(f"kill @e[tag=gs_garrison_out_w1,{OUT_AREA}]")
c(f"forceload remove {OUTPOST[0] - 64} {OUTPOST[1] - 64} {OUTPOST[0] + 64} {OUTPOST[1] + 64}")

# 5. the assault with nobody near: the clock waits, the wave is taken back, the next comes on return
for x0, z0, x1, z1 in LOADS:
    c(f"forceload add {x0} {z0} {x1} {z1}")
time.sleep(6)
for s in ("hospital", "switchyard"):
    c(f"gscraft site {s} set unknown")
c("kill @e[tag=gs_wave]")
c("gscraft clock free")
ay = surface_y(*ANCHOR)
c(f"gscraft director phantom set {ANCHOR[0]} {ay} {ANCHOR[1]}")
c("gscraft site switchyard set scouted")
c("gscraft site switchyard set looted")
c("gscraft site hospital set scouted")
c("gscraft site hospital set looted")
begin = c("gscraft site hospital set held")
time.sleep(4)
wave1 = count(f"@e[tag=gs_wave_hospital,{HOSP}]")
clock_near = re.findall(r"(\d+:\d\d)", c("gscraft site hospital"))
c(f"gscraft director phantom set {ANCHOR[0]} {ay} {ANCHOR[1] + 400}")
time.sleep(66)
wave_gone = count(f"@e[tag=gs_wave_hospital,{HOSP}]")
clock_away = re.findall(r"(\d+:\d\d)", c("gscraft site hospital"))
c(f"gscraft director phantom set {ANCHOR[0]} {ay} {ANCHOR[1]}")
time.sleep(50)
wave2 = count(f"@e[tag=gs_wave_hospital,{HOSP}]")


def secs(mmss):
    m, s = mmss.split(":")
    return int(m) * 60 + int(s)


frozen = bool(clock_near and clock_away) and abs(secs(clock_near[0]) - secs(clock_away[0])) <= 8
check("an assault with nobody within 128 freezes its clock, takes the wave back after a minute, and resumes on return",
      wave1 >= 3 and wave_gone == 0 and frozen and wave2 >= 3,
      f"{begin[:40]}; wave 1 {wave1}; clock {clock_near[:1]} near, {clock_away[:1]} after 66 s away; wave {wave_gone} while away; {wave2} back 50 s after return")
for s in ("hospital", "switchyard"):
    c(f"gscraft site {s} set unknown")
c("kill @e[tag=gs_wave]")
c("gscraft clock online")
for x0, z0, x1, z1 in LOADS:
    c(f"forceload remove {x0} {z0} {x1} {z1}")
c("gscraft director phantom clear")

# 6. a patrol waits for someone near
PY = 200
c(f"fill {X - 41} {PY - 1} {Z - 21} {X + 41} {PY + 4} {Z + 21} minecraft:air")
c(f"fill {X - 40} {PY - 1} {Z - 20} {X + 40} {PY - 1} {Z + 20} minecraft:stone")
c(f"fill {X - 41} {PY} {Z - 21} {X + 41} {PY + 1} {Z + 21} minecraft:stone hollow")
c(f"fill {X - 40} {PY} {Z - 20} {X + 40} {PY + 3} {Z + 20} minecraft:air")
c(f'summon gscraft:nato_soldier {X - 30} {PY} {Z} {{GscraftRank:"NATO Sergeant",Tags:["pt0"]}}')
c(f'summon gscraft:nato_soldier {X - 29} {PY} {Z + 1} {{GscraftRank:"NATO Rifleman",Tags:["pt1"]}}')
time.sleep(0.5)
c("gscraft squad @e[tag=pt0,limit=1] form")
c(f"gscraft squad @e[tag=pt0,limit=1] route {X + 20} {Z} {X - 30} {Z}")
p0 = pos_of("@e[tag=pt0,limit=1]")
time.sleep(10)
p1 = pos_of("@e[tag=pt0,limit=1]")
c(f"gscraft director phantom set {X} {PY} {Z}")
time.sleep(10)
p2 = pos_of("@e[tag=pt0,limit=1]")
c("gscraft director phantom clear")


def d(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5 if a and b else None


# an idle leader still strolls at random, so the measure is progress toward the first waypoint, not distance moved
wp = (X + 20, PY, Z)
alone = d(p0, wp) - d(p1, wp) if p0 and p1 else None
walked = d(p1, wp) - d(p2, wp) if p1 and p2 else None
check("a patrol leader waits with nobody within 96 and walks once a phantom is there", alone is not None and alone < 12 and walked is not None and walked > 15,
      f"closer to the first waypoint by {alone and round(alone, 1)} blocks alone in 10 s, then by {walked and round(walked, 1)} with a phantom")
c(f"kill @e[type=gscraft:nato_soldier,x={X - 70},y={PY - 10},z={Z - 70},dx=140,dy=40,dz=140]")
c(f"fill {X - 41} {PY - 1} {Z - 21} {X + 41} {PY + 4} {Z + 21} minecraft:air")

# 7. the bench
kill_director(CAMP_AREA)
SPREAD = [(X, Z), (X + 250, Z), (X, Z + 250), (X + 250, Z + 250)]
for sx, sz in SPREAD[1:]:
    c(f"forceload add {sx - 64} {sz - 64} {sx + 64} {sz + 64}")
time.sleep(10)
rows = []


def bench(label, phantoms):
    c("gscraft director phantom clear")
    for px, pz in phantoms:
        c(f"gscraft director phantom add {px} {surface_y(px, pz)} {pz}")
    for px, pz in phantoms:
        kill_director(f"x={px - 140},y=-64,z={pz - 140},dx=280,dy=400,dz=280")
    c("gscraft director bench 6")                     # fill up first: the steady state is what a tick costs
    out = c("gscraft director bench 20")
    m = re.search(r"([\d.]+) ms mean, ([\d.]+) min, ([\d.]+) max per pass; creatures (\d+) -> (\d+)", out)
    # the creatures around the first player (the ceiling's own box) and around all of them; the server total also
    # holds whatever other tests left elsewhere
    px, pz = phantoms[0]
    around = count(f"@e[tag=gs_director,x={px - 80},y=-64,z={pz - 80},dx=160,dy=400,dz=160]")
    everyone = sum(count(f"@e[tag=gs_director,x={qx - 80},y=-64,z={qz - 80},dx=160,dy=400,dz=160]") for qx, qz in phantoms) if len(phantoms) > 1 and phantoms[1][0] - phantoms[0][0] > 100 else around
    rows.append((label, len(phantoms)) + (tuple(float(v) for v in m.groups()[:3]) if m else (None,) * 3) + (around, everyone))
    print(f"    {label}: {out}; around the first {around}, around all {everyone}")


bench("one player", [(X, Z)])
bench("four together", [(X, Z), (X + 6, Z), (X, Z + 6), (X + 6, Z + 6)])
bench("four spread 250 apart", SPREAD)
ok = all(row[2] is not None and row[2] < 20.0 and row[6] <= 96 for row in rows)
together = rows[1][5]
spread = rows[2][6]
check("a director pass is cheap and the totals respect the ceilings: four together share one box, four apart get their own",
      ok and together <= 12 and spread > together, "; ".join(f"{l}: {ms} ms mean, {mx} max, {n0} around the first, {n1} around all" for l, _, ms, mn, mx, n0, n1 in rows if ms is not None))
c("gscraft director phantom clear")
for sx, sz in SPREAD:
    kill_director(f"x={sx - 140},y=-64,z={sz - 140},dx=280,dy=400,dz=280")
for sx, sz in SPREAD[1:]:
    c(f"forceload remove {sx - 64} {sz - 64} {sx + 64} {sz + 64}")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")
print("  stats:", c("gscraft director stats"))
c("gscraft director resume")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
rest = [l for l in new.splitlines() if "rests:" in l]
away = [l for l in new.splitlines() if "wave is taken back" in l]
check("the rest and the away were logged and no gscraft errors", rest and away and not bad, f"rest lines {len(rest)}, away lines {len(away)}, error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
