"""Phase 6 of the enemy work, on the LOCAL server: the strongpoint loop in the mod (fold-in review step 2, design
section 6). Needs a ticking world and no player; the clocks are set free for the test and the deadlines jumped.
Run war_phase5.py, war_phase4b.py, war_phase4.py, war_phase3.py and war_phase2.py after it.

1. The sites and the camp loaded.
2. The ladder: no rung is skipped; scouted and looted set their stages.
3. The assault: the marker starts it, wave 1 enters from the hospital's edges dressed as The Infected; a second
   site's marker is refused while the first is contested.
4. Held: the assault's end sets the stage, summons the site guard at the anchor, starts the fortify clock, and
   the site's ambient hostiles stop.
5. The counterattack: the clock's end sends the first wave at the north approach.
6. Lost: five attackers in the camp square for thirty seconds; the wave withdraws, the site stays held, another
   clock runs.
7. Defended: three waves sent and beaten; the guard doubles; the contested slot clears.
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


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


HOSP = "x=-881,y=-64,z=-1328,dx=200,dy=400,dz=103"
NORTH = "x=-900,y=-64,z=-1140,dx=60,dy=400,dz=60"
LOADS = [(-881, -1328, -682, -1226), (-900, -1140, -840, -1080), (-975, -1010, -905, -950)]


def cleanup():
    for s in ("hospital", "switchyard"):
        c(f"gscraft site {s} set unknown")
    c("kill @e[tag=gs_wave]")
    c("gscraft clock online")
    for x0, z0, x1, z1 in LOADS:
        c(f"forceload remove {x0} {z0} {x1} {z1}")


for x0, z0, x1, z1 in LOADS:
    c(f"forceload add {x0} {z0} {x1} {z1}")
time.sleep(6)
c("gscraft clock free")
cleanup_needed = True
c("gscraft site hospital set unknown")
c("gscraft site switchyard set unknown")

# 1. loaded
sites = c("gscraft sites")
check("the sites and the camp loaded", all(s in sites for s in ("hospital", "intake", "turbine", "switchyard")) and "online clock" in sites, sites.replace("\n", " | ")[:300])

# 2. the ladder
skip = c("gscraft site hospital set held")
c("gscraft site hospital set scouted")
looted = c("gscraft site hospital set looted")
stages = c("gscraft stages")
check("no rung is skipped; scouted and looted set their stages", "next rung is scouted" in skip and "hospital_scouted" in stages and "hospital_looted" in stages,
      f"{skip}; {looted}; stages {stages}")

# 3. the assault
c("gscraft site switchyard set scouted")
c("gscraft site switchyard set looted")
begin = c("gscraft site hospital set held")
time.sleep(4)
wave = count(f"@e[tag=gs_wave_hospital,{HOSP}]")
infected = count(f'@e[tag=gs_wave_hospital,name="The Infected",{HOSP}]')
info = c("gscraft site hospital")
refused = c("gscraft site switchyard set held")
check("the marker starts the assault; wave 1 enters as The Infected; a second marker is refused",
      "assault begins" in begin and wave >= 3 and infected == wave and "assault" in info and "still contested" in refused,
      f"{begin}; wave 1 {wave} ({infected} Infected); {info}; switchyard: {refused}")

# 4. held
c("gscraft site hospital clock 0")
time.sleep(4)
info = c("gscraft site hospital")
guard = count(f"@e[tag=gscraft_siteguard_hospital,{HOSP}]")
recruits = count(f"@e[type=recruits:recruit,tag=gscraft_siteguard_hospital,{HOSP}]") + count(f"@e[type=recruits:bowman,tag=gscraft_siteguard_hospital,{HOSP}]") \
    + count(f"@e[type=recruits:recruit_shieldman,tag=gscraft_siteguard_hospital,{HOSP}]")
guards = count(f"@e[type=guardvillagers:guard,tag=gscraft_siteguard_hospital,{HOSP}]")
stages = c("gscraft stages")
SITE = "x=-865,y=-64,z=-1312,dx=167,dy=400,dz=70"
c(f"kill @e[tag=gs_director,{SITE}]")
ambient = c("gscraft director pass -800 -1290 40")
placed = count(f"@e[tag=gs_director,{SITE}]")      # the pass ring reaches outside the site; only the site is suppressed
check("held: the stage, the site guard at the anchor, the fortify clock, no ambient hostiles",
      ": held" in info and "fortify clock" in info and guard == 6 and recruits == 4 and guards == 2 and "hospital_held" in stages and placed == 0,
      f"{info}; guard {guard} ({recruits} recruits, {guards} guards); {ambient}; placed inside the site {placed}")

# 5. the counterattack
c("kill @e[tag=gs_wave]")
c("gscraft site hospital clock 0")
time.sleep(4)
info = c("gscraft site hospital")
north = count(f"@e[tag=gs_wave_hospital,{NORTH}]")
check("the clock's end sends the first wave at the north approach", "counterattack wave 1 of 3" in info and north >= 3, f"{info}; at the approach {north}")

# 6. lost
for i in range(5):
    c(f'summon minecraft:zombie {-940 + i} 66 -979 {{NoAI:1b,Tags:["gs_placed","gs_wave","gs_wave_hospital"]}}')
time.sleep(34)
info = c("gscraft site hospital")
left = count("@e[tag=gs_wave_hospital]")
stages = c("gscraft stages")
check("five attackers in the square for thirty seconds: lost, the wave withdraws, the site stays held, another clock",
      "lost once" in info and ": held" in info and "fortify clock" in info and left == 0 and "hospital_lost" in stages, f"{info}; wave left {left}")

# 7. defended
for i in range(3):                      # the clock's end, then waves 2 and 3
    c("gscraft site hospital clock 0")
    time.sleep(3)
info3 = c("gscraft site hospital")
c("kill @e[tag=gs_wave_hospital]")
time.sleep(4)
info = c("gscraft site hospital")
guard = count(f"@e[tag=gscraft_siteguard_hospital,{HOSP}]")
stages = c("gscraft stages")
sites = c("gscraft sites")
check("three waves beaten: defended, the guard doubles, the contested slot clears",
      "wave 3 of 3" in info3 and ": defended" in info and "guard 12 of 12" in info and guard == 12 and "hospital_defended" in stages and "contested: none" in sites,
      f"{info3}; {info}; guard standing {guard}")

cleanup()
r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors in the log", not bad, f"{len(bad)} lines")
for l in bad[:10]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
