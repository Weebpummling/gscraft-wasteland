"""Phase 42, the journal (owner, 2026-09-17: "not very intuitive to grasp") on the LOCAL server. NEEDS ONE PLAYER ONLINE
(FTB Quests keeps progress per team, and a pin is per player): launch the WarTest client first -
    prismlauncher --launch GSCraft-WarTest --server localhost:9150
and this waits up to six minutes for the join. It resets that player's quest progress.

What it proves, headless: FTB Quests' API is reachable by reflection; a fresh player has exactly the hub's Wake up to
start and the mod pins it; ticking Wake up makes the six Meet quests available and the mod pins the first three; a field
note writes once, its entry's advancement granted; pins off clears the mod's pins and on brings them back; the notebook
is in the kit. What it cannot see: the pinned overlay and the pages on screen - the owner's check.

1. The API is reachable; 75 stage advancements include the five notes; the book has nine chapters.
2. A fresh player: Wake up completes itself (its task is the `joined` advancement), so the six Meets are what there is to start.
3. The first three Meets are pinned by the mod.
4. A field note writes once (second write refused) and shows in the status; the advancement is granted.
5. Pins off -> none by the mod; on -> three again.
6. The kit lists six entries, the notebook among them.
7. No gscraft or ftbquests errors.
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


def status(player):
    out = c(f"gscraft journal status {player}")
    m = re.search(r"available (\d+) \[(.*?)\]; pinned by the mod (\d+)( \(pins off\))?; notes \[(.*?)\]", out)
    return (int(m.group(1)), m.group(2), int(m.group(3)), bool(m.group(4)), m.group(5)) if m else (None, out, None, None, None)


player = None
for i in range(360):
    m = re.search(r"online: (\S+)", c("list"))
    if m:
        player = m.group(1).rstrip(",")
        break
    time.sleep(1)
if not player:
    print("  no player joined within six minutes: launch the WarTest client and rerun")
    sys.exit(2)
print(f"  player {player} after {i} s")
time.sleep(8)

record = json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))
wake = next(q["id"] for q in record["quests"] if q["key"] == "wake")
advs = list((ROOT / "mod/src/main/resources/data/gscraft/advancements/stage").glob("*.json"))
notes = [a.stem for a in advs if a.stem.startswith("note_")]
api = c("gscraft journal check")
check("the API is reachable; the notes' advancements and the ninth chapter exist", "reachable" in api and "NOT" not in api and len(notes) == 5 and len(record["chapters"]) == 9,
      f"[{api[:60]}]; {len(advs)} advancements, notes {sorted(notes)}; chapters {len(record['chapters'])}")

# 2. a fresh player
c(f"ftbquests change_progress {player} reset 1")
c(f"gscraft journal pins {player} on")
for k in ("death", "bulky", "vehicle", "infected", "warning"):
    c(f"tag {player} remove note_{k}")
    c(f"advancement revoke {player} only gscraft:stage/note_{k}")
time.sleep(3)
# Wake up's one task is the per-player `joined` advancement, which a joined player holds: after the reset FTB must find it
# again on its own (no command completes it here) - the point of the change is that nobody has to find a checkmark
done_wake = None
for _ in range(20):
    time.sleep(2)
    n, names, pinned, off, _ = status(player)
    if n is not None and "compound/Wake up" not in (names or ""):
        done_wake = True
        break
meets = (names or "").count("compound/Meet ")
check("a fresh player: Wake up completes itself, the six Meets are what there is to start", done_wake and n == 6 and meets == 6, f"available {n} [{names}]")
check("the first three Meets are pinned by the mod", pinned == 3, f"pinned {pinned}")

# 4. a field note
first = c(f"gscraft journal note {player} bulky")
second = c(f"gscraft journal note {player} bulky")
_, _, _, _, written = status(player)
granted = c(f"execute if entity @a[name={player},advancements={{gscraft:stage/note_bulky=true}}]")
check("a field note writes once and its advancement is granted", "written" in first and "already" in second and "bulky" in (written or "") and "passed" in granted,
      f"[{first}] [{second}]; notes [{written}]; advancement [{granted[:30]}]")

# 5. pins off and on
c(f"gscraft journal pins {player} off")
_, _, p_off, off_flag, _ = status(player)
c(f"gscraft journal pins {player} on")
_, _, p_on, _, _ = status(player)
check("pins off clears the mod's pins, on brings them back", p_off == 0 and off_flag and p_on == 3, f"off {p_off} (flag {off_flag}); on {p_on}")

# 6. the kit
kit = re.search(r"(\d+) kit entries", LOG.read_text(encoding="utf-8", errors="replace"))
surv = json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_survivors/survivors.json").read_text(encoding="utf-8"))
book = [k for k in surv["first_join"]["kit"] if k.get("item") == "patchouli:guide_book"]
counts = re.findall(r"(\d+) kit entries", LOG.read_text(encoding="utf-8", errors="replace"))   # logged on each data load; absent only before the first
check("the kit has six entries, the notebook among them", len(surv["first_join"]["kit"]) == 6 and (not counts or counts[-1] == "6") and book and "gscraft:notebook" in book[0].get("nbt", ""),
      f"kit entries in the data {len(surv['first_join']['kit'])}; the server's last count {counts[-1] if counts else 'not logged yet'}; notebook {bool(book)}")

# leave the player as a fresh one
c(f"ftbquests change_progress {player} reset 1")
c(f"tag {player} remove note_bulky")
c(f"advancement revoke {player} only gscraft:stage/note_bulky")
r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and re.search(r"gscraft|ftbquests", l, re.I)]
check("no gscraft or ftbquests errors", not bad, f"error lines {len(bad)}")
for l in bad[:6]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
