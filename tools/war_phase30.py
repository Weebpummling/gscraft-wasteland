"""Phase 30, the items (system doc 2026-09-13 §7 build 3) on the LOCAL server. Needs a ticking world. What a headless test
can prove: every id in items.json is a registered item (`/gscraft items`), the count matches, the bandage the mod already
had is still there, and the lang file names every one. The textures and tooltips on screen, and the bulky rule on a
player, are the owner's in-game check (WarTest: `/give @s gscraft:claim_marker`).

1. Every listed item is registered, and nothing listed is missing.
2. Every listed item has a name and a tooltip line in the lang file.
3. No gscraft errors.
"""
import json
import re
import sys
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


listed = [i["id"] for i in json.loads((ROOT / "mod/src/main/resources/data/gscraft/gscraft_items/items.json").read_text(encoding="utf-8"))["items"]]
out = c("gscraft items")
registered = int((re.search(r"(\d+) items registered", out) or [0, 0])[1])
listed_known = int((re.search(r"(\d+) of (\d+) listed", out) or [0, 0, 0])[1])
missing = re.search(r"missing: \[([^\]]*)\]", out)
check("every listed item is registered, nothing missing", registered >= len(listed) + 1 and listed_known == len(listed) and (missing is None or not missing.group(1).strip()),
      f"registered {registered}; listed known {listed_known} of {len(listed)}; [{out[:80]}]")

lang = json.loads((ROOT / "mod/src/main/resources/assets/gscraft/lang/en_us.json").read_text(encoding="utf-8"))
unnamed = [i for i in listed if f"item.gscraft.{i}" not in lang]
untipped = [i for i in listed if f"item.gscraft.{i}.tip" not in lang]
check("every listed item has a name and a tooltip line", not unnamed and not untipped, f"unnamed {unnamed[:4]}; untipped {untipped[:4]}")

r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
