"""Phase 36, nothing in front of the players and nothing at the compound (owner, 2026-09-13) on the LOCAL server. Needs a
ticking world and no player. The director places for a phantom; the compound's box is excluded and carries a 32-block
margin (map.json), so nothing ambient lands within 32 of its wall; a placement a player could see is refused
(`director.hidden_from`, which a phantom cannot exercise - the in-game check); the survivors are never a target
(LivingChangeTargetEvent). What a headless test can prove: the margin holds over many passes, from the yard (whose
whole ring lies inside the margin, so nothing is placed) and from the square (whose ring crosses the margin's edge);
nothing lands closer than the open ring's inner edge; the settings are in force. Short count queries only: the RCON
client loses sync on long multi-entity replies.

1. The settings: director.hidden_from 64, env.indoor.min_r 10.
2. Forty seconds of passes for a phantom in the yard place nothing within the compound's box + 32.
3. Forty seconds for a phantom on the square: placements within 120, none PLACED within 28 (first seen, sampled each
   second: a squad walks from its first second), none inside the margin.
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
YARD = (-829, 71, -893)   # the walled compound's yard (2026-09-17)
SQUARE = (-940, 64, -979)
BOX = (-900, -720, -920, -835)   # the walled compound (it was still the south compound's box after the move: found by the suite, 2026-09-19)
M = 32


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def in_margin():
    return count(f"@e[tag=gs_director,x={BOX[0] - M},y=-64,z={BOX[2] - M},dx={BOX[1] - BOX[0] + 2 * M},dy=384,dz={BOX[3] - BOX[2] + 2 * M}]")


def new_in_margin():
    m = M - 6
    return count(f"@e[tag=gs_director,tag=!p36_seen,x={BOX[0] - m},y=-64,z={BOX[2] - m},dx={BOX[1] - BOX[0] + 2 * m},dy=384,dz={BOX[3] - BOX[2] + 2 * m}]")


def near(p, d):
    m = re.search(r"count: (\d+)", c(f"execute positioned {p[0]} {p[1]} {p[2]} if entity @e[tag=gs_director,distance=..{d}]"))
    return int(m.group(1)) if m else 0


def run(p, seconds):
    c(f"kill @e[tag=gs_director]")
    time.sleep(2)   # a killed body is still an entity for a second, and one lying in the margin was counted as placed there
    c("tag @e[tag=gs_director] add p36_seen")
    c(f"gscraft director phantom set {p[0]} {p[1]} {p[2]}")
    c("gscraft director resume")
    c("gscraft clock free")
    # "none within 30" is about where a creature is PLACED, not where it walks to: every placed squad walks a loop of up to
    # squads.walk_radius (28) from the first second, so a position sampled every ten seconds caught walkers 28 out and called
    # them placements (found by the suite, 2026-09-19). Each second, whatever is new is counted once, where it first stands.
    worst_margin, close_new, most = 0, 0, 0
    for i in range(seconds):
        time.sleep(1)
        m = re.search(r"count: (\d+)", c(f"execute positioned {p[0]} {p[1]} {p[2]} if entity @e[tag=gs_director,tag=!p36_seen,distance=..28]"))
        close_new += int(m.group(1)) if m else 0
        # the margin the same way: what is NEW and already inside it (less SIX blocks: a squad placed a block outside the margin walks from its first tick, and a
        # sample is a second and a few console calls late - two blocks of slack still went red one full run in two). Positions sampled every ten seconds counted a zombie that wandered one block in
        # as a placement, and the third full suite went red on it (2026-09-19)
        n_new = new_in_margin()
        if n_new:   # say WHAT it was: red in two full runs and green alone, so the run itself must name the offender
            m_ = M - 6
            sel = f"@e[tag=gs_director,tag=!p36_seen,x={BOX[0] - m_},y=-64,z={BOX[2] - m_},dx={BOX[1] - BOX[0] + 2 * m_},dy=384,dz={BOX[3] - BOX[2] + 2 * m_},limit=1]"
            print(f"      in the margin at {i + 1} s: [{c(f'data get entity {sel} Pos')[-90:]}] tags [{c(f'data get entity {sel} Tags')[-200:]}]")
        worst_margin += n_new
        c("tag @e[tag=gs_director,tag=!p36_seen] add p36_seen")
        if i % 10 == 9:
            most = max(most, near(p, 120))
    worst_near = close_new
    c("gscraft director pause")
    c("gscraft director phantom clear")
    c("gscraft clock online")
    return worst_margin, worst_near, most


hidden = re.search(r"director.hidden_from = (\d+)", c("gscraft settings director.hidden_from"))
minr = re.search(r"env.indoor.min_r = (\d+)", c("gscraft settings env.indoor.min_r"))
# the margin itself, asked directly: it was wiped at every load until 2026-09-19 (Zones.apply cleared the map after filling it)
near_wall, clear_of = c("gscraft upgrades at -830 70 -930"), c("gscraft upgrades at -830 70 -990")
check("the compound's margin is in force: ten blocks from the wall is refused, seventy is not", "REFUSED" in near_wall and "allowed" in clear_of, f"[{near_wall[-44:]}] [{clear_of[-30:]}]")
# the soldiers' ring (owner, 2026-09-20: "make the soldiers spawn further out from the compound"): 70 blocks north of the wall the Dead
# may be placed and a soldier may not; 130 out both may. And no garrison's box reaches inside it.
ring_in, ring_out = c("gscraft upgrades at -830 70 -990"), c("gscraft upgrades at -830 70 -1050")
import json as _json
_zones = _json.loads((Path(__file__).resolve().parents[1] / "mod/src/main/resources/data/gscraft/gscraft_zones/map.json").read_text(encoding="utf-8"))["zones"]
# a garrison's HOME is its box's centre; its members are never placed inside the ring (Director.groundIn refuses), so it is the home that must be outside
_near = [z["name"] for z in _zones if z.get("garrison") and "soldier" in z["garrison"]["entity"]
         and BOX[0] - 120 <= (z["box"][0] + z["box"][1]) // 2 <= BOX[1] + 120 and BOX[2] - 120 <= (z["box"][2] + z["box"][3]) // 2 <= BOX[3] + 120]
check("the soldiers' ring: 70 blocks out the margins allow and soldiers are refused, 130 out both are allowed; no soldier garrison is homed inside it",
      "allowed by the margins; soldiers REFUSED" in ring_in and "soldiers allowed" in ring_out and not _near, f"[{ring_in[-52:]}] [{ring_out[-40:]}]; garrisons inside {_near}")
check("the settings: hidden_from 64, indoor min_r 10", hidden and hidden.group(1) == "64" and minr and minr.group(1) == "10", f"hidden {hidden and hidden.group(1)}; indoor min_r {minr and minr.group(1)}")

c(f"forceload add {SQUARE[0] - 100} {SQUARE[2] - 100} {SQUARE[0] + 100} {YARD[2] + 100}")
time.sleep(3)
c("time set night")
margin, close, seen = run(YARD, 40)
check("forty seconds from the yard place nothing within the compound's box + 32", margin == 0, f"in the margin {margin}; within 30 {close}; within 120 {seen}")

margin, close, seen = run(SQUARE, 40)
check("forty seconds from the square: placements within 120, none within 30, none in the margin", seen > 0 and close == 0 and margin == 0, f"within 120 {seen}; within 30 {close}; in the margin {margin}")

c("kill @e[tag=gs_director]")
c(f"forceload remove {SQUARE[0] - 100} {SQUARE[2] - 100} {SQUARE[0] + 100} {YARD[2] + 100}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
