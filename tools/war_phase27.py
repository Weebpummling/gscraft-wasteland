"""Phase 27, the stage gates and the placed bosses (next-steps plan 2026-09-12 §3) on the LOCAL server. Needs a
ticking world and no player.

1. A composition's stage: the west front's roll (RUAF, tanks gated on `switchyard_scouted`) picks no tank until the
   stage is set, and picks tanks once it is.
2. A wave entry's stage: the hospital's last counterattack wave carries its RUAF APC only with `line_depot` set.
3. The boss block: the switchyard scouted places the gatekeeper (a named T-90A) once, holding; a `/reload` does not
   place a second; the site's reset takes it away.
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


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def picks(x, z, n=400):
    out = c(f"gscraft director armourpick {x} {z} {n}")
    return {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", out)}, out


c("gscraft director pause")
c("gscraft director phantom clear")
c("gscraft clock free")
for s in ("switchyard_scouted", "line_depot"):
    c(f"gscraft stage remove {s}")
c("kill @e[tag=gs_wave]")
c("gscraft site hospital set unknown")
c("gscraft site switchyard set unknown")
time.sleep(1.5)

# 1. the composition stage (front_wn: x -1290..-1100, z -1250..-700)
gated, out0 = picks(-1200, -1000)
c("gscraft stage add switchyard_scouted")
time.sleep(1.5)
opened, out1 = picks(-1200, -1000)
c("gscraft stage remove switchyard_scouted")
time.sleep(1.5)
check("a composition with a stage rolls only once the stage is set (the west front's tanks)",
      gated.get("bmp_2", 0) > 0 and gated.get("t_90a", 0) == 0 and opened.get("t_90a", 0) > 0,
      f"gated {gated}; opened {opened}")

# 2. the wave entry's stage: the hospital's third counterattack wave
HOSP_APPROACH = "x=-930,y=40,z=-1170,dx=120,dy=80,dz=120"


def third_wave():
    c("kill @e[tag=gs_wave]")
    c("gscraft site hospital set unknown")
    c("gscraft site hospital set scouted")
    c("gscraft site hospital set looted")
    c("gscraft site hospital set held")
    time.sleep(3)
    info = ""
    for attempt in range(6):
        c("gscraft site hospital clock 0")
        time.sleep(3)
        info = c("gscraft site hospital")
        if "wave 3 of 3" in info or "defended" in info:
            break
    time.sleep(2)
    return count("@e[type=superbwarfare:bmp_2,tag=gs_wave_hospital]"), count(f"@e[tag=gs_wave_hospital,{HOSP_APPROACH}]"), info


c("forceload add -940 -1180 -800 -1040")
time.sleep(3)
apc0, wave0, info0 = third_wave()
c("gscraft stage add line_depot")
time.sleep(1.5)
apc1, wave1, info1 = third_wave()
crew = c("data get entity @e[type=gscraft:crew,tag=gs_wave_hospital,limit=1] GscraftFaction")
c("gscraft stage remove line_depot")
c("kill @e[tag=gs_wave]")
c("gscraft site hospital set unknown")
c("forceload remove -940 -1180 -800 -1040")
check("a wave entry with a stage is sent only once the stage is set (the sector's APC on line_depot), with its own crew faction",
      apc0 == 0 and wave0 > 0 and apc1 == 1 and "ruaf" in crew,
      f"without: {apc0} APC of {wave0} placed [{info0[:40]}]; with: {apc1} APC [{info1[:40]}]; crew faction [{crew[-16:]}]")

# 3. the boss: the switchyard's gatekeeper
c("forceload add -900 0 -760 120")
time.sleep(4)
c("kill @e[type=superbwarfare:t_90a,x=-830,y=0,z=60,dy=200,distance=..80]")
c("kill @e[type=gscraft:crew,x=-830,y=0,z=60,dy=200,distance=..80]")
mark = LOG.stat().st_size
c("gscraft site switchyard set scouted")
time.sleep(4)
tanks = count("@e[type=superbwarfare:t_90a,tag=gs_wave_switchyard]")
named = "The gatekeeper" in c("data get entity @e[type=superbwarfare:t_90a,tag=gs_wave_switchyard,limit=1] CustomName")
c("reload")
time.sleep(6)
tanks_after = count("@e[type=superbwarfare:t_90a,tag=gs_wave_switchyard]")
c("gscraft site switchyard set unknown")
time.sleep(2)
tanks_reset = count("@e[type=superbwarfare:t_90a,tag=gs_wave_switchyard]")
logged = "boss gatekeeper" in log_since(mark)
check("the boss is placed once on scouted, named and holding; a reload places no second; the reset takes it",
      tanks == 1 and named and tanks_after == 1 and tanks_reset == 0 and logged,
      f"placed {tanks} (named {named}); after reload {tanks_after}; after reset {tanks_reset}; logged {logged}")
c("forceload remove -900 0 -760 120")

c("gscraft clock online")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
