"""Phase 25, the start (next-steps plan 2026-09-12 §1) on the LOCAL server. Needs a ticking world and no player.

1. Zone growth by stage: the yard is camp_compound (always); the square is the front's ground until `square_taken`
   is set, and camp_square once it is; the stage removed, it is the front's again.
2. The director places nothing inside the compound; on the square it places the front's military until
   `square_taken` is set and the Dead and scavengers only after (owner: a taken building keeps those).
3. The gate datum: a NATO counterattack's wave (soldiers) leaves the south approach for the gate at (-948, -893).
4. The torches: `gscraft:camp_torches` places the two of the start; `gscraft:torch_square` places its own, twice
   without harm; the test takes the square's back down.
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
COMPOUND = "x=-980,y=40,z=-897,dx=60,dy=80,dz=79"
SQUARE = "x=-966,y=40,z=-1000,dx=52,dy=80,dz=42"
GATE = (-948, -893)
NORTH = (-870, -1108)


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def zone(x, z):
    return c(f"gscraft zone {x} {z}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def wave_positions(tag):
    """the x,z of every wave fighter, from the short data outputs"""
    out = []
    n = count(f"@e[tag={tag}]")
    for i in range(min(n, 12)):
        pos = c(f"data get entity @e[tag={tag},limit=1,sort=arbitrary] Pos")   # arbitrary is stable enough for a mean
        m = re.findall(r"(-?\d+\.\d+)d", pos)
        if len(m) >= 3:
            out.append((float(m[0]), float(m[2])))
    return out


c("gscraft director pause")
c("gscraft director phantom clear")
c("forceload add -1000 -1120 -860 -830")
time.sleep(4)
for s in ("square_taken", "gatehouse_taken", "clinic_taken", "crossing_taken", "skadowsky_held"):
    c(f"gscraft stage remove {s}")
c("kill @e[tag=gs_director,x=-1000,y=40,z=-1120,dx=140,dy=80,dz=290]")
time.sleep(1.5)

# 1. the zones by stage
yard = zone(-829, -893)   # the walled compound's yard (2026-09-17)
square_before = zone(-940, -979)
c("gscraft stage add square_taken")
time.sleep(1.5)
square_after = zone(-940, -979)
c("gscraft stage remove square_taken")
time.sleep(1.5)
square_again = zone(-940, -979)
check("the yard is camp_compound; the square is camp_square only while square_taken is set",
      "camp_compound" in yard and "camp_square" not in square_before and "camp_square" in square_after and "camp_square" not in square_again,
      f"yard [{yard[:40]}]; square [{square_before[:30]}] -> [{square_after[:30]}] -> [{square_again[:30]}]")

# 2. the director's denial: the ambient placement at a point (the pass's own routine) - in the yard nothing; on the
# square a group while it is the sector's ground, nothing once square_taken is set
c("kill @e[tag=gs_director]")   # the sector zone's cap counts every director creature in it, wherever
time.sleep(1)
c("gscraft director ambient -829 71 -893 6")
in_compound = count(f"@e[tag=gs_director,{COMPOUND}]")
c("kill @e[tag=gs_director,x=-1000,y=40,z=-1120,dx=140,dy=80,dz=290]")
time.sleep(1)
c("kill @e[tag=gs_director]")
time.sleep(1)
open_reply = c("gscraft director ambient -940 66 -979 6")
on_square_open = count(f"@e[tag=gs_director,{SQUARE}]")
c("kill @e[tag=gs_director,x=-1000,y=40,z=-1120,dx=140,dy=80,dz=290]")
time.sleep(1)
c("gscraft stage add square_taken")
time.sleep(1.5)
c("kill @e[tag=gs_director]")
time.sleep(1)
taken_reply = c("gscraft director ambient -940 66 -979 6")
on_square_taken = count(f"@e[tag=gs_director,{SQUARE}]")
c("gscraft stage remove square_taken")
c("kill @e[tag=gs_director,x=-1000,y=40,z=-1120,dx=140,dy=80,dz=290]")
placed_open = int((re.search(r"placed (\d+)", open_reply) or [0, 0])[1])
placed_taken = int((re.search(r"placed (\d+)", taken_reply) or [0, 0])[1])
soldiers_taken = count(f"@e[type=gscraft:nato_soldier,{SQUARE}]") + count(f"@e[type=gscraft:ruaf_soldier,{SQUARE}]")   # inside the taken box only: the placement lands up to 70 from the point
check("nothing is placed in the compound; the square places the front's military until square_taken, then the Dead and scavengers only",
      in_compound == 0 and placed_open > 0 and placed_taken > 0 and soldiers_taken == 0,
      f"in the compound {in_compound}; at the square open: placed {placed_open}, taken: placed {placed_taken} with {soldiers_taken} soldiers")

# 3. the gate: the switchyard's (NATO) counterattack from the south approach heads for the gate
c("kill @e[tag=gs_wave]")
c("gscraft clock free")
c("gscraft site switchyard set unknown")
c("gscraft site switchyard set scouted")
c("gscraft site switchyard set looted")
c("gscraft site switchyard set held")
time.sleep(3)
info = ""
for attempt in range(3):   # the clock lands on the phase the loop is in; the fortify phase starts a tick after the set
    c("gscraft site switchyard clock 0")
    time.sleep(4)
    info = c("gscraft site switchyard")
    if "counterattack" in info:
        break
p0 = wave_positions("gs_wave_switchyard")
time.sleep(30)
p1 = wave_positions("gs_wave_switchyard")


def mean_dist(points, to):
    if not points:
        return None
    return sum(((x - to[0]) ** 2 + (z - to[1]) ** 2) ** 0.5 for x, z in points) / len(points)


d0, d1 = mean_dist(p0, GATE), mean_dist(p1, GATE)
check("the counterattack's wave leaves the south approach for the gate",
      "counterattack wave 1" in info and d0 is not None and d1 is not None and d1 < d0 - 15.0,
      f"{info[:60]}; mean distance to the gate {d0 and round(d0)} -> {d1 and round(d1)} in 30 s ({len(p1)} fighters)")
c("kill @e[tag=gs_wave]")
c("gscraft site switchyard set unknown")
c("gscraft clock online")

# 4. the torches
c("function gscraft:camp_torches")
time.sleep(1)
yard_t = "passed" in c("execute if block -957 66 -862 magnumtorch:diamond_magnum_torch").lower()
gap_t = "passed" in c("execute if block -947 66 -890 magnumtorch:diamond_magnum_torch").lower()
c("function gscraft:torch_square")
c("function gscraft:torch_square")
time.sleep(1)
sq_t = "passed" in c("execute if block -940 67 -979 magnumtorch:diamond_magnum_torch").lower()
c("setblock -940 67 -979 minecraft:air")
c("fill -941 66 -980 -939 66 -978 minecraft:air")
check("camp_torches places the yard and gap torches; torch_square places its own, twice without harm",
      yard_t and gap_t and sq_t, f"yard {yard_t}, gap {gap_t}, square {sq_t} (taken down again)")

c("forceload remove -1000 -1120 -860 -830")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
