"""Phase 34, the first quests (system doc 2026-09-13 §7 build 7; quests §2-§7, start-compound §5) on the LOCAL server.
Needs a ticking world and no player. The book is `tools/chapters.py`'s seven chapter files, installed in
config/ftbquests/quests and read by FTB Quests at start (or `/ftbquests reload`); `tools/quests.json` is the record the
test reads. What a headless test can prove: every hand-in and reward item is a registered item; every stage a reward
sets or a task reads is in the registry with its advancement; every dependency exists and the graph is acyclic; every
line a reward speaks has its lang text; every location is a site's box; the takes' rewards run (a stage set lights the
torch, phase 26); FTB Quests reloaded the files without error. The chain played from the yard to Marshall's line is
the owner's in-game check (WarTest, `/gscraft reset all`, then play).

1. Seven chapter files installed; FTB Quests reloads them with no error.
2. Every item in a task or reward is registered.
3. Every stage in a reward or an advancement task is in the registry and known to the server.
4. Dependencies resolve and the graph is acyclic; the five introductions gate Marshall; the takes follow the gap.
5. Every spoken reward has its line.
6. Every location task is one of the sites' boxes.
7. No gscraft errors.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402
import stages  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("G:/GSCraft/server/logs/latest.log")
SERVER = Path("G:/GSCraft/server/config/ftbquests/quests")
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


record = json.loads((ROOT / "tools/quests.json").read_text(encoding="utf-8"))
quests = record["quests"]
chapters = record["chapters"]

files = sorted(p.name for p in (SERVER / "chapters").glob("*.snbt")) if SERVER.exists() else []
mark = LOG.stat().st_size
out = c("ftbquests reload")
new = log_since(mark)
errs = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l)]
check("seven chapter files installed; FTB Quests reloads them with no error", len(files) == 7 and all(f"{ch['tag']}.snbt" in files for ch in chapters) and not errs,
      f"files {len(files)}; reload [{out[:60]}]; errors {len(errs)}")
for l in errs[:4]:
    print("     ", l[:200])

items = sorted({t["item"] for d in quests for t in d["tasks"] if t["type"] == "item"} | {rw["item"] for d in quests for rw in d["rewards"] if rw["type"] == "item"})
unknown = [i for i in items if "registered" not in c(f"gscraft item {i}")]
check("every item in a task or reward is registered", items and not unknown, f"{len(items)} items; unknown {unknown}")

registry = set(stages.registry())
used = sorted({rw["stage"] for d in quests for rw in d["rewards"] if rw["type"] == "stage"} | {t["stage"] for d in quests for t in d["tasks"] if t["type"] == "advancement"})
missing = [s for s in used if s not in registry or "UNKNOWN" in c(f"gscraft stage check {s}")]
check("every stage set or read is in the registry and known", used and not missing, f"{len(used)} stages; missing {missing}")

keys = {d["key"]: d for d in quests}
bad_dep = [(d["key"], k) for d in quests for k in d["deps"] if k not in keys]


def cyclic():
    state = {}

    def visit(k):
        if state.get(k) == 1:
            return True
        if state.get(k) == 2:
            return False
        state[k] = 1
        if any(visit(x) for x in keys[k]["deps"]):
            return True
        state[k] = 2
        return False
    return any(visit(k) for k in keys)


intro = {"W1", "T1", "M1", "U1", "J1"}
takes_after_gap = all("R0" in keys[k]["deps"] or "square" in keys[k]["deps"] or k == "mast" for k in ("square", "gatehouse", "clinic", "crossing", "mast"))
check("dependencies resolve, acyclic; the introductions gate Marshall; the takes follow the gap",
      not bad_dep and not cyclic() and set(keys["R1"]["deps"]) == intro and takes_after_gap and set(keys["mast"]["deps"]) == {"gatehouse", "clinic", "crossing"},
      f"bad {bad_dep}; R1 deps {keys['R1']['deps']}")

spoken = [(rw["npc"], rw["key"]) for d in quests for rw in d["rewards"] if rw["type"] == "say"]
silent = [(n, k) for n, k in spoken if c(f"gscraft say {n} {k}").endswith(f"gscraft.say.{n}.{k}")]
check("every spoken reward has its line", spoken and not silent, f"{len(spoken)} lines; missing {silent}")

boxes = {f.stem: json.loads(f.read_text(encoding="utf-8")).get("box") for f in (ROOT / "mod/src/main/resources/data/gscraft/gscraft_sites").glob("*.json")}
locs = [t for d in quests for t in d["tasks"] if t["type"] == "location"]
off = [t["name"] for t in locs if t["box"] not in boxes.values()]
check("every location task is a site's box", locs and not off, f"{len(locs)} locations; off {off}")

r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
