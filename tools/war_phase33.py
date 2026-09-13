"""Phase 33, the survivors as the book (system doc 2026-09-13 §7 build 6; onboarding §2/§8, interface §3.4) on the
LOCAL server. Needs a ticking world and no player. What a headless test can prove: the six survivors load with a hello
line, a chapter file and a seen_* advancement each; Tune's join lines and the kit resolve (the pistol with its ammo);
the radio line renders in its shape; the re-issued summons stand with their professions and no trades; the joined
advancement exists; FTB Quests raised no error over the chapter files. The book opening on a right-click, the title
and the lines on a first join are the owner's in-game check (WarTest: a fresh account, or `/gscraft join @s`).

1. Six survivors, each complete (hello line, chapter file, seen advancement); three join lines, none missing; the kit resolves.
2. The kit holds the station, a loaded glock with a spare magazine of its ammo, the flashlight, a battery and a bandage.
3. `/gscraft say tune join_1` renders as ♪ [TUNE]  You're up...
4. The summons put each survivor up with the profession from survivors.json, level 2 and no offers.
5. The joined advancement is known.
6. No gscraft errors, no ftbquests errors.
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


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


survivors = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_survivors/survivors.json").read_text(encoding="utf-8"))
out = c("gscraft survivors")
m = re.search(r"(\d+) survivors, (\d+) complete; title (\w+); join lines (\d+), missing \[([^\]]*)\]; kit (\d+) stacks of (\d+) entries", out)
check("six survivors complete; three join lines; the kit resolves",
      m and m.group(1) == "6" and m.group(2) == "6" and m.group(3) == "WASTELAND" and m.group(4) == "3" and not m.group(5).strip() and int(m.group(6)) >= 6,
      f"[{out[-160:]}]")

kit = c("gscraft kit")
check("the kit: station, loaded glock + a magazine, flashlight, battery, bandage",
      "gscraft:station" in kit and "tacz:modern_kinetic_gun" in kit and 'GunId:"tacz:glock_17"' in kit and re.search(r"(\d+) tacz:ammo", kit) and "flashlight:flashlight" in kit and "flashlight:battery" in kit and "gscraft:bandage" in kit,
      f"[{kit[:200]}]")

line = c("gscraft say tune join_1")
check("the radio line renders in its shape", line.startswith("♪ [TUNE]  ") and "You're up" in line, f"[{line}]")

c("forceload add -1000 -1070 -880 -840")
time.sleep(3)
c("function gscraft:camp_npcs")
time.sleep(2)
bad = []
for d in survivors["survivors"]:
    sel = f"@e[type=minecraft:villager,tag={ 'gscraft_npc_' + d['id']},limit=1]"
    vd = c(f"data get entity {sel} VillagerData")
    offers = c(f"data get entity {sel} Offers.Recipes")
    if d["profession"] not in vd or "level: 2" not in vd or not re.search(r"Recipes: \[\]|Found no elements matching Offers", offers):
        bad.append((d["id"], vd[-80:], offers[-40:]))
c("forceload remove -1000 -1070 -880 -840")
check("the summons stand with their professions, level 2, no offers", not bad, f"{bad[:2]}")

joined = c("gscraft stage check joined")
check("the joined advancement is known", "known" in joined and "UNKNOWN" not in joined, f"[{joined[:60]}]")

# 6. the test resets run clean with nobody on: a stage set is gone after `reset quests`; `reset all` reports
c("gscraft stage add square_taken")
c("gscraft stage add bp_fastener_kit")
rq = c("gscraft reset quests")
ra = c("gscraft reset all")
mark = LOG.stat().st_size
c("gscraft stage add square_taken")
new = log_since(mark)
check("reset quests clears the stages; reset all runs", "2 stages cleared" in rq and "reset all" in ra and "stage square_taken set" in new, f"[{rq[:80]}] [{ra[-60:]}]")
c("gscraft stage remove square_taken")

r.close()
new = log_since(log_start)
whole = LOG.read_text(encoding="utf-8", errors="replace")
gs = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
fq = [l for l in whole.splitlines() if re.search(r"ERROR|Exception", l) and "ftbquests" in l.lower()]
check("no gscraft errors, no ftbquests errors", not gs and not fq, f"gscraft {len(gs)}, ftbquests {len(fq)}")
for l in (gs + fq)[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
