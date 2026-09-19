"""Phase 49, THE UPGRADES AS SYSTEMS (owner, 2026-09-19: "apply the upgrade system to just system based and skip the upgrade
visuals") on the LOCAL server. Needs no player. Each camp function level is a stage a survivor's quest sets; each now
changes a rule (world/Upgrades.java). What a server alone can prove:

1. With nothing earned, no rule is changed: station factor 1.0, no extra margin, the warning unheard, no countdown;
   PlayerRevive is reachable for the clinic.
2. Workshop 1 then Workshop 2: a two-minute order starts at 1:42 and then at 1:24.
3. Generator 1: a spot 40 blocks from the compound's wall may be placed at before it and may not after.
4. Radio 1: a held site's ten-minute warning goes unheard without it and is heard with it (the log says which).
5. Radio 2: set by Tune's U3 in the book, and the rule reads it.
6. Every function stage a quest sets is one the upgrades read, or the backpack's: none is a flag with no rule.
7. The quest reset takes every level back.
8. No gscraft errors.
What needs a player and is NOT proven here: the clinic's cure and revive, clean water's mending, Medical 2's respawn.
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
X, Y, Z = -2000, 215, -600
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


def order_starts_at():
    c(f"setblock {P} minecraft:air")
    c(f"setblock {P} gscraft:station")
    c(f"gscraft station bind {P} Alice")
    c(f"gscraft station load {P} 0 gscraft:card_fastener_kit")
    c(f"gscraft station load {P} 1 gscraft:wrench")
    for slot, item in enumerate(("bolt", "nut", "screw", "nail"), start=3):
        c(f"gscraft station load {P} {slot} gscraft:{item} 4")
    for _ in range(8):
        time.sleep(0.5)
        m = re.search(r"remaining (\d+)", c(f"gscraft station show {P}"))
        if m and int(m.group(1)) > 0:
            return int(m.group(1))
    return None


c("gscraft director pause")
c("gscraft reset quests")
c(f"forceload add {X - 16} {Z - 16} {X + 16} {Z + 16}")
time.sleep(3)
c(f"fill {X - 2} {Y - 1} {Z - 2} {X + 2} {Y - 1} {Z + 2} minecraft:stone")

# 1
up = c("gscraft upgrades")
check("with nothing earned no rule is changed, and PlayerRevive is reachable", "station factor 1.0;" in up and "margin +0;" in up and "warning heard false" in up and "countdown shown false" in up
      and "[x]" not in up and "PlayerRevive reachable: true" in up, up.splitlines()[-1] + " | " + next((l for l in up.splitlines() if "medical_1" in l), "")[-40:])

# 2
t0 = order_starts_at()
c("gscraft stage add workshop_1")
t1 = order_starts_at()
c("gscraft stage add workshop_2")
t2 = order_starts_at()
check("Workshop 1 then 2: a two-minute order starts at 2:00, 1:42, 1:24", t0 and t1 and t2 and 2360 <= t0 <= 2400 and 2000 <= t1 <= 2040 and 1640 <= t2 <= 1680, f"ticks remaining at the start: {t0}, {t1}, {t2}")

# 3: the compound's north wall is z -920; its margin is 32, so z -960 is 40 out: allowed, then refused with +16
before = c("gscraft upgrades at -830 70 -960")
c("gscraft stage add generator_1")
after = c("gscraft upgrades at -830 70 -960")
far = c("gscraft upgrades at -830 70 -975")
check("Generator 1: 40 blocks from the wall is allowed before it and refused after; 55 is still allowed", "allowed" in before and "REFUSED" in after and "allowed" in far, f"[{before[-30:]}] -> [{after[-40:]}]; 55 out [{far[-24:]}]")

# 4
def warned(with_radio):
    c("gscraft site hospital set unknown")
    c("gscraft clock free")
    for rung in ("scouted", "looted", "held"):
        c(f"gscraft site hospital set {rung}")
    time.sleep(1)
    c("gscraft site hospital clock 0")     # the assault's end, if `held` started one
    time.sleep(3)
    mark = LOG.stat().st_size
    c("gscraft site hospital clock 500")   # inside the ten-minute warning
    time.sleep(4)
    lines = [l for l in log_since(mark).splitlines() if "ten-minute warning" in l]
    return lines[-1][lines[-1].find("[gscraft]"):] if lines else "no warning line"


c("forceload add -881 -1328 -682 -1226")
time.sleep(3)
unheard = warned(False)
c("gscraft stage add radio_1")
heard = warned(True)
check("Radio 1: the ten-minute warning goes unheard without it and is heard with it", "goes unheard" in unheard and "is heard" in heard, f"[{unheard[:70]}] then [{heard[:70]}]")
c("gscraft site hospital set unknown")
c("kill @e[tag=gs_wave]")
c("forceload remove -881 -1328 -682 -1226")

# 5
quests = {q["key"]: q for q in json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))["quests"]}
u3 = [rw.get("stage") for rw in quests["U3"]["rewards"]]
c("gscraft stage add radio_2")
up = c("gscraft upgrades")
check("Radio 2 is Tune's U3, and the rule reads it", "radio_2" in u3 and "countdown shown true" in up, f"U3 sets {u3}; {up.splitlines()[-1][-60:]}")

# 6
read = {"workshop_1", "workshop_2", "medical_1", "medical_2", "generator_1", "water_1", "radio_1", "radio_2"}
functions = {rw["stage"] for q in quests.values() for rw in q["rewards"] if rw.get("type") == "stage" and re.fullmatch(r"(workshop|storage|medical|generator|water|radio|intel|garage|walls|farm)_\d", rw["stage"])}
idle = sorted(functions - read - {"storage_1"})
listed = all(f"{s}:" in up for s in read)
check("every function level a quest sets has a rule (storage_1 is the backpack)", not idle and listed, f"quests set {sorted(functions)}; with no rule {idle}")

# 7
c("gscraft reset quests")
up = c("gscraft upgrades")
check("the quest reset takes every level back", "[x]" not in up and "station factor 1.0;" in up, up.splitlines()[-1])

c(f"setblock {P} minecraft:air")
c(f"fill {X - 2} {Y - 1} {Z - 2} {X + 2} {Y - 1} {Z + 2} minecraft:air")
c(f"forceload remove {X - 16} {Z - 16} {X + 16} {Z + 16}")
c("gscraft clock online")
c("gscraft director resume")
r.close()
errs = [l for l in log_since(log_start).splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not errs, f"error lines {len(errs)}")
for l in errs[:6]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
