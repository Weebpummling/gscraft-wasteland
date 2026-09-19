"""NEVER RUN. Written 2026-09-19 and stopped by the owner before the client had started ("no need to test anything"): every
line below is untried, the click helper included. It is kept as the way to prove these things if that is ever wanted.

Phase 45, A PLAYER'S HANDS (owner, 2026-09-19: no live session - prove it here) on the LOCAL server. NEEDS ONE PLAYER
ONLINE: what phase 44 could only stand in for, done to a real player. Launch the WarTest client first -
    prismlauncher --launch GSCraft-WarTest --server localhost:9150
(options.txt pauseOnLostFocus:false, or the unfocused client sits in its pause menu and its player never ticks).
It wipes that player's inventory and quest progress, kills them three times, and leaves them in the yard.

1. The kit reaches a real inventory: Superb Warfare's Glock 17 with GunData.Ammo 17, 34 handgun rounds, no TACZ.
2. A death (keepInventory off): the respawn gives the pistol, loaded, and the notebook, and nothing else; the log says so.
3. A death carrying them (keepInventory on): nothing is given twice.
4. Walking in: a CREATIVE player in the hospital's grounds for eight seconds scouts nothing; in survival the same eight
   seconds scout it and set the stage. The player's own tick did it, not a console stand-in.
5. The quest rewards arrive: R0 completed gives a Marlin and 32 rifle rounds and bars the gate; the junction gives the
   vest and two plates.
6. Canned goods: a hungry survival player holding one... is the client's to eat. Checked here: the stack is edible
   (FoodProperties on the item the player holds), which is all a server can see.
7. ONE REAL RIGHT-CLICK (tools/click_client.ps1 focuses the client and clicks): facing a Lootr container in the
   hospital, the search counts "1 of 6". If the window cannot be driven this check says so and is not a failure of the game.
8. No gscraft errors.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402
from chapters import hex_id  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
hosp = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_sites/hospital.json").read_text(encoding="utf-8"))
AX, AZ = hosp["anchor"]
X0, X1, Z0, Z1 = hosp["box"]
record = [c for c in json.loads((ROOT / "tools/chests.json").read_text(encoding="utf-8")) if X0 <= c["x"] <= X1 and Z0 <= c["z"] <= Z1 and c["was"].startswith("air")]


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


def inv(p):
    """item id -> (count, tag text) over the whole inventory"""
    out = c(f"data get entity {p} Inventory")
    found = {}
    for m in re.finditer(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', out[out.find("["):]):
        t = m.group(0)
        i = re.search(r'id: "([^"]+)"', t)
        n = re.search(r"Count: (\d+)b", t)
        if i and n:
            k = i.group(1)
            found[k] = (found.get(k, (0, ""))[0] + int(n.group(1)), t)
    return found


player = None
for i in range(420):
    m = re.search(r"online: (\S+)", c("list"))
    if m:
        player = m.group(1).rstrip(",")
        break
    time.sleep(1)
if not player:
    print("  no player joined within seven minutes: launch the WarTest client and rerun")
    sys.exit(2)
print(f"  player {player} after {i} s")
P = player
time.sleep(8)
c("gscraft director pause")
c("gscraft reset quests")
c(f"effect give {P} minecraft:resistance 3600 255 true")
c(f"gamemode survival {P}")
c("gamerule doImmediateRespawn true")
c("gamerule keepInventory false")

# 1
c(f"clear {P}")
c(f"gscraft kit {P}")
time.sleep(1)
have = inv(P)
gun = have.get("superbwarfare:glock_17", (0, ""))
check("the kit in a real inventory: the Glock 17 with 17 in it, 34 rounds, no TACZ",
      gun[0] == 1 and re.search(r"Ammo: 17", gun[1]) and have.get("superbwarfare:handgun_ammo", (0, ""))[0] == 34 and not any(k.startswith("tacz:") for k in have),
      f"{ {k: v[0] for k, v in have.items()} }; gun tag [{gun[1][gun[1].find('tag'):][:70]}]")

# 2 (the death is far from the yard: a body that falls at the spawn point is picked up again on the way out of bed)
c(f"execute positioned -600 0 -893 positioned over motion_blocking_no_leaves run tp {P} ~ ~ ~")
time.sleep(3)
mark = LOG.stat().st_size
c(f"kill {P}")
time.sleep(6)
have = inv(P)
gun = have.get("superbwarfare:glock_17", (0, ""))
said = [l for l in log_since(mark).splitlines() if "[gscraft] respawn:" in l]
check("a death: the respawn gives the pistol, loaded, and the notebook, and nothing else; the log says so",
      set(have) == {"superbwarfare:glock_17", "patchouli:guide_book"} and gun[0] == 1 and re.search(r"Ammo: 17", gun[1]) and len(said) == 1,
      f"{ {k: v[0] for k, v in have.items()} }; log [{said[-1][said[-1].find('[gscraft]'):][:70] if said else 'no respawn line'}]")

# 3
c("gamerule keepInventory true")
mark = LOG.stat().st_size
c(f"kill {P}")
time.sleep(6)
have = inv(P)
said = [l for l in log_since(mark).splitlines() if "[gscraft] respawn:" in l]
check("a death carrying them (keepInventory on): nothing is given twice",
      have.get("superbwarfare:glock_17", (0, ""))[0] == 1 and have.get("patchouli:guide_book", (0, ""))[0] == 1 and not said,
      f"{ {k: v[0] for k, v in have.items()} }; respawn lines {len(said)}")
c("gamerule keepInventory false")
c(f"effect give {P} minecraft:resistance 3600 255 true")

# 4
c("gscraft site hospital set unknown")
c(f"gamemode creative {P}")
c(f"execute positioned {AX} 0 {AZ} positioned over motion_blocking_no_leaves run tp {P} ~ ~ ~")
time.sleep(9)
as_creative = c("gscraft site hospital")
c(f"gamemode survival {P}")
c(f"effect give {P} minecraft:resistance 3600 255 true")
time.sleep(9)
as_survivor = c("gscraft site hospital")
check("walking in: creative scouts nothing in eight seconds; survival scouts it and sets the stage",
      "unknown" in as_creative and "scouted" in as_survivor and "hospital_scouted" in c("gscraft stages"), f"creative [{as_creative[:40]}]; survival [{as_survivor[:40]}]")

# 7 (here, while the player stands in the hospital): one real right-click on a Lootr container
clicked = "not tried"
spot = None
for ch in record:
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        x, y, z = ch["x"] + dx, ch["y"], ch["z"] + dz
        if all("passed" in c(f"execute if block {x} {y + k} {z} minecraft:air") for k in (0, 1)) and "passed" not in c(f"execute if block {x} {y - 1} {z} minecraft:air"):
            spot = (ch, (x, y, z))
            break
    if spot:
        break
if spot:
    ch, (x, y, z) = spot
    c(f"tp {P} {x + 0.5} {y} {z + 0.5} facing {ch['x'] + 0.5} {ch['y'] + 0.4} {ch['z'] + 0.5}")
    time.sleep(2)
    ps = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "tools/click_client.ps1")], capture_output=True, text=True, timeout=60)
    clicked = (ps.stdout or ps.stderr).strip().splitlines()[-1] if (ps.stdout or ps.stderr).strip() else "no output"
    time.sleep(2)
    after = c(f"gscraft site hospital search {ch['x']} {ch['y']} {ch['z']}")   # a repeat now means the click was counted
    check("one real right-click on a Lootr container in the hospital is a search", "already" in after, f"at {ch['x']} {ch['y']} {ch['z']}; the click: [{clicked[:60]}]; asked again: [{after[:60]}]")
else:
    check("one real right-click on a Lootr container in the hospital is a search", False, "no placed container with standing room beside it")

# 5
c(f"execute positioned -829 0 -893 positioned over motion_blocking_no_leaves run tp {P} ~ ~ ~")
time.sleep(2)
c(f"clear {P}")
for key in ("R0", "square"):
    c(f"ftbquests change_progress {P} complete {hex_id('quest:' + key)}")
time.sleep(4)
have = inv(P)
bags = sum("passed" in c(f"execute if block {x} {y} -912 superbwarfare:sandbag") for x in (-835, -834, -831, -830) for y in (71, 72))
check("the rewards arrive: a Marlin and 32 rifle rounds and the gate barred; the vest and two plates",
      have.get("superbwarfare:marlin", (0, ""))[0] == 1 and have.get("superbwarfare:rifle_ammo", (0, ""))[0] == 32 and bags == 8
      and have.get("superbwarfare:ru_chest_6b43", (0, ""))[0] == 1 and have.get("superbwarfare:armor_plate", (0, ""))[0] == 2,
      f"{ {k: v[0] for k, v in have.items()} }; sandbags {bags}")

# 6
c(f"clear {P}")
c(f"give {P} gscraft:canned_goods 1")
time.sleep(1)
edible = c("gscraft items")
check("canned goods in a player's hands are food", "canned_goods(6)" in edible and inv(P).get("gscraft:canned_goods", (0, ""))[0] == 1, edible[edible.find("edible"):][:40])

# the bench put back
c("gscraft reset quests")
c(f"clear {P}")
c(f"effect clear {P}")
c(f"gamemode creative {P}")
c("gamerule doImmediateRespawn false")
c("gamerule keepInventory false")
c("gscraft director resume")
r.close()
bad = [l for l in log_since(log_start).splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:6]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
