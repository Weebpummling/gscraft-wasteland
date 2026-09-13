"""Phase 35, the hospital as the first strongpoint with the marker and the board (system doc 2026-09-13 §7 build 8;
map-design §6.1, camp spec §2, interface §3.3) on the LOCAL server. Needs a ticking world and no player; the loop ticks
headless on `gscraft clock free`. The board is `tools/board.py --apply`'s blocks on the hall's wall and the mod's
board.json; the marker is `/gscraft site <id> marker` here (the item does the same on a right-click). What a headless
test can prove: the board follows the site's state; the marker is refused before looted; the marker starts the assault,
plants the banner, lights the lamp; with nobody inside at the end the assault is lost - the site stays looted, the
banner is gone, the lamp is out; the console's claim (no marker) still holds as before. The right-click, Marshall's
lines and the look-at readout are the owner's in-game check.

1. The board is loaded and its hospital column stands; unknown → scouted → looted recolour it.
2. The marker is refused on an unscouted site (no banner).
3. The marker on the looted site starts the assault: the banner at the anchor, the lamp lit, the site contested.
4. Nobody inside at the end: the assault is lost, the site looted, the banner gone, the lamp out, the column orange.
5. The console's claim (no marker) still ends held; the column light blue.
6. No gscraft errors.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
board = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_board/board.json").read_text(encoding="utf-8"))
hosp = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_sites/hospital.json").read_text(encoding="utf-8"))
OX, OY, OZ = board["origin"]
AX, AZ = board["along"]
LX, LY, LZ = board["lamp"]
AXX, AZZ = hosp["anchor"]


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def column_is(block):
    i = board["columns"].index("hospital") * board["width"]
    return "passed" in c(f"execute if block {OX + AX * i} {OY} {OZ + AZ * i} minecraft:{block}").lower()


def lamp_lit():
    return "passed" in c(f"execute if block {LX} {LY} {LZ} minecraft:redstone_lamp[lit=true]").lower()


def banner():
    for y in range(55, 90):
        if "passed" in c(f"execute if block {AXX} {y} {AZZ} #minecraft:banners").lower():
            return y
    return None


def state():
    return c("gscraft site hospital")


c(f"forceload add {OX - 8} {OZ - 8} {OX + 8} {OZ + 8}")
c(f"forceload add {AXX - 16} {AZZ - 16} {AXX + 16} {AZZ + 16}")
c("gscraft clock free")
time.sleep(3)
c("gscraft site hospital set unknown")
time.sleep(1.5)
b_unknown = column_is("black_concrete")
c("gscraft site hospital set scouted")
time.sleep(1.5)
b_scouted = column_is("yellow_concrete")
c("gscraft site hospital set looted")
time.sleep(1.5)
b_looted = column_is("orange_concrete")
check("the board is loaded; unknown, scouted, looted recolour the hospital's column", "board at" in c("gscraft board") and b_unknown and b_scouted and b_looted,
      f"black {b_unknown} yellow {b_scouted} orange {b_looted}; [{c('gscraft board')[:70]}]")

c("gscraft site hospital set unknown")
time.sleep(1)
refused = c("gscraft site hospital marker")
check("the marker is refused on an unscouted site", "next rung" in refused and banner() is None, f"[{refused[:80]}]")

c("gscraft site hospital set scouted")
c("gscraft site hospital set looted")
time.sleep(1)
started = c("gscraft site hospital marker")
time.sleep(2)
by = banner()
check("the marker starts the assault: the banner at the anchor, the lamp lit, the site contested",
      "the assault begins" in started and by is not None and lamp_lit() and "assault" in state(), f"[{started[:90]}]; banner y {by}; lamp {lamp_lit()}")

c("gscraft site hospital clock 8")
time.sleep(14)
st = state()
check("nobody inside at the end: lost, the site looted, the banner gone, the lamp out, the column orange",
      "looted" in st and "assault" not in st and banner() is None and not lamp_lit() and column_is("orange_concrete"), f"[{st[:100]}]; banner {banner()}; lamp {lamp_lit()}")

c("gscraft site hospital set held")
c("gscraft site hospital clock 8")
time.sleep(14)
st = state()
check("the console's claim still ends held; the column light blue", "held" in st and column_is("light_blue_concrete") and not lamp_lit(), f"[{st[:100]}]")

c("gscraft site hospital set unknown")
c("gscraft clock online")
c(f"forceload remove {OX - 8} {OZ - 8} {OX + 8} {OZ + 8}")
c(f"forceload remove {AXX - 16} {AZZ - 16} {AXX + 16} {AZZ + 16}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
