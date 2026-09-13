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
3. Forty seconds for a phantom on the square: placements within 120, none within 30, none inside the margin.
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
YARD = (-956, 65, -876)
SQUARE = (-940, 64, -979)
BOX = (-980, -920, -897, -818)
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


def near(p, d):
    m = re.search(r"count: (\d+)", c(f"execute positioned {p[0]} {p[1]} {p[2]} if entity @e[tag=gs_director,distance=..{d}]"))
    return int(m.group(1)) if m else 0


def run(p, seconds):
    c(f"kill @e[tag=gs_director]")
    c(f"gscraft director phantom set {p[0]} {p[1]} {p[2]}")
    c("gscraft director resume")
    c("gscraft clock free")
    worst_margin, worst_near, most = 0, 0, 0
    for _ in range(seconds // 10):
        time.sleep(10)
        worst_margin = max(worst_margin, in_margin())
        worst_near = max(worst_near, near(p, 30))
        most = max(most, near(p, 120))
    c("gscraft director pause")
    c("gscraft director phantom clear")
    c("gscraft clock online")
    return worst_margin, worst_near, most


hidden = re.search(r"director.hidden_from = (\d+)", c("gscraft settings director.hidden_from"))
minr = re.search(r"env.indoor.min_r = (\d+)", c("gscraft settings env.indoor.min_r"))
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
