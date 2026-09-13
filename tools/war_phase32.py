"""Phase 32, the station (system doc 2026-09-13 §7 build 5; crafting §3-§4, interface §3.3/§4.3) on the LOCAL server.
Needs a ticking world and no player. The station is a block entity in the mod; the console drives it through
`/gscraft station show|bind|load|take|clear|list`, which read and write the same slots a player's screen does. What a
headless test can prove: the card and the parts start the order and the readout counts down from 2:00; the kit lands
in the output at the end with the block lit until it is taken; a missing tool and missing parts are named; the quick
recipes run with no card; a stranger's readout is the refusal; the bp_* advancements exist for every card. The screen,
the slot refusal against a second player's cursor, the chime and the lit texture are the owner's in-game check.

1. A card and its parts start the order; the readout says FASTENER KIT — 2:00 and counts down; nothing is left in the inputs.
2. The kit is in the output at the end, the block lit; taking it unlights it.
3. A steel frame without the torch says `needs: welding torch`; with the torch and too little scrap, `2 more metal scrap`.
4. Cloth is quick and needs no card (4 string, ~20 s); sandbags likewise (2 cloth + 4 sand → 4).
5. A stranger's readout is the refusal; the owner's is not.
6. Every card has its bp_* advancement.
7. No gscraft errors.
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
X, Y, Z = -2000, 200, -600
P = f"{X} {Y} {Z}"


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def show(viewer=None):
    return c(f"gscraft station show {P}" + (f" {viewer}" if viewer else ""))


def readout(viewer=None):
    return show(viewer).split(" | ")[0]


def wait_until(pred, limit, step=2):
    t0 = time.time()
    while time.time() - t0 < limit:
        s = show()
        if pred(s):
            return s, time.time() - t0
        time.sleep(step)
    return show(), time.time() - t0


c(f"forceload add {X - 16} {Z - 16} {X + 16} {Z + 16}")
time.sleep(3)
c(f"fill {X - 3} {Y - 1} {Z - 3} {X + 3} {Y - 1} {Z + 3} minecraft:stone")
c(f"fill {X - 3} {Y} {Z - 3} {X + 3} {Y + 3} {Z + 3} minecraft:air")
c(f"setblock {P} gscraft:station")
time.sleep(1)
c(f"gscraft station bind {P} Alice")

# 1. the fastener kit: card and parts in, the countdown from 2:00
c(f"gscraft station load {P} 0 gscraft:card_fastener_kit")
c(f"gscraft station load {P} 3 gscraft:bolt 4")
c(f"gscraft station load {P} 4 gscraft:nut 4")
c(f"gscraft station load {P} 5 gscraft:screw 4")
c(f"gscraft station load {P} 6 gscraft:nail 4")
t_start = time.time()
s, _ = wait_until(lambda s: "order fastener_kit" in s, 8, 0.5)
m = re.search(r"FASTENER KIT — (\d+:\d\d)", s)
first = m.group(1) if m else None
inputs_left = re.findall(r" ([3-9]|1[01])=", s.split(" | ")[-1])
check("card and parts start the order; the readout counts from 2:00; inputs consumed",
      first is not None and first in ("2:00", "1:59", "1:58") and not inputs_left, f"readout [{s.split(' | ')[0]}]; inputs left {inputs_left}")

# 2. the kit out at the end, lit until taken
s, took = wait_until(lambda s: "order null" in s and "2=gscraft:fastener_kit" in s, 150)
elapsed = time.time() - t_start
lit_done = "lit true" in s and "FASTENER KIT — done" in s
c(f"gscraft station take {P}")
time.sleep(1.5)
after = show()
check("the kit is in the output at the end, lit until taken", "2=gscraft:fastener_kit" in s and lit_done and "lit false" in after and 100 <= elapsed <= 135,
      f"{elapsed:.0f} s; [{s.split(' | ')[0]}]; after take lit {'true' in after.split('lit ')[1][:4]}")

# 3. the steel frame: the tool named, then the count
c(f"gscraft station clear {P}")
c(f"gscraft station load {P} 0 gscraft:card_steel_frame")
c(f"gscraft station load {P} 3 gscraft:metal_scrap 6")
c(f"gscraft station load {P} 4 gscraft:fastener_kit 1")
time.sleep(2.5)
no_tool = readout()
c(f"gscraft station load {P} 1 gscraft:welding_torch")
c(f"gscraft station load {P} 3 gscraft:metal_scrap 4")
time.sleep(2.5)
short = readout()
check("a missing tool is named, then the missing count", "steel frame — needs: welding torch" in no_tool and "2 more metal scrap" in short, f"[{no_tool}] [{short}]")

# 4. quick recipes need no card
c(f"gscraft station clear {P}")
c(f"gscraft station load {P} 3 minecraft:string 4")
s, t_cloth = wait_until(lambda s: "2=gscraft:clothx1" in s, 40)
cloth_ok = "2=gscraft:clothx1" in s and t_cloth <= 30
c(f"gscraft station clear {P}")
c(f"gscraft station load {P} 3 gscraft:cloth 2")
c(f"gscraft station load {P} 4 minecraft:sand 4")
s, t_bags = wait_until(lambda s: "2=superbwarfare:sandbagx4" in s, 40)
check("cloth and sandbags are quick and need no card", cloth_ok and "2=superbwarfare:sandbagx4" in s, f"cloth {t_cloth:.0f} s; sandbags {t_bags:.0f} s [{s.split(' | ')[-1]}]")

# 5. a stranger is refused, the owner is not
stranger = readout("Bob")
owner = readout("Alice")
check("a stranger's readout is the refusal, the owner's is not", "this one is Alice's" in stranger and "ALICE'S STATION" in stranger and "this one is" not in owner, f"[{stranger}] [{owner}]")

# 6. every card's advancement
recipes = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_recipes/recipes.json").read_text(encoding="utf-8"))
cards = sorted({o["card"].removeprefix("card_") for o in recipes["orders"] if o.get("card")})
unknown = [cd for cd in cards if "UNKNOWN" in c(f"gscraft stage check bp_{cd}")]
check("every card has its bp_* advancement", cards and not unknown, f"{len(cards)} cards; unknown {unknown}")

c(f"gscraft station clear {P}")
c(f"setblock {P} minecraft:air")
c(f"kill @e[type=minecraft:item,x={X - 4},y={Y - 2},z={Z - 4},dx=8,dy=6,dz=8]")
c(f"fill {X - 3} {Y - 1} {Z - 3} {X + 3} {Y + 3} {Z + 3} minecraft:air")
c(f"forceload remove {X - 16} {Z - 16} {X + 16} {Z + 16}")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
