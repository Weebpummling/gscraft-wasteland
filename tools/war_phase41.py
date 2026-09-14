"""Phase 41, block destruction for wooden blocks only (owner, 2026-09-13: on for vehicles and artillery rounds, not
bullets) on the LOCAL server. Needs a ticking world; the strike items' cooldowns are reset. A mortar fire mission lands
on a platform of oak planks ringed and floored with stone: the planks go, the stone stays. What a headless test can
prove: after the barrage some planks are gone and no stone block is; the server config carries the flags; the
soft-collision tag the vehicles use is ours. A vehicle crushing a fence on screen is the owner's in-game check.

1. The server config: explosion_destroy on, projectile glass off, collision soft on / normal, hard, beastly off.
2. The world datapack's soft-collision tag is the wooden tag alone.
3. A mortar mission on a plank platform: planks gone, stone untouched.
4. No gscraft errors.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
CONFIG = Path("G:/GSCraft/server/config/superbwarfare-server.toml")
TAG = Path("G:/GSCraft/server/wasteland-v8/datapacks/gscraft_armour/data/superbwarfare/tags/blocks/soft_collision.json")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
X, Y, Z = -2000, 200, -400


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


# 1. the config flags
flags = dict(re.findall(r"^\s*(\w+) = (true|false)\s*$", CONFIG.read_text(encoding="utf-8"), re.M))
want = {"explosion_destroy": "true", "allow_projectile_destroy_glass": "false", "collision_destroy_soft_blocks": "true",
        "collision_destroy_normal_blocks": "false", "collision_destroy_hard_blocks": "false", "collision_destroy_blocks_beastly": "false"}
bad = {k: flags.get(k) for k, v in want.items() if flags.get(k) != v}
check("the server config carries the block destruction flags", not bad, f"off {bad}" if bad else "all six as wanted")

# 2. the tag
tag = json.loads(TAG.read_text(encoding="utf-8")) if TAG.exists() else {}
check("the soft-collision tag is the wooden tag alone", tag.get("replace") is True and tag.get("values") == ["#gscraft:wooden"], str(tag)[:80])

# 3. the mission on the platform: stone floor at Y-1, a 9x9 plank slab at Y with a stone ring around it at Y
c("gscraft director pause")
c(f"forceload add {X - 32} {Z - 32} {X + 32} {Z + 32}")
time.sleep(2)
c(f"fill {X - 14} {Y - 1} {Z - 14} {X + 14} {Y - 1} {Z + 14} minecraft:stone")
c(f"fill {X - 14} {Y} {Z - 14} {X + 14} {Y + 8} {Z + 14} minecraft:air")
c(f"fill {X - 6} {Y} {Z - 6} {X + 6} {Y} {Z + 6} minecraft:stone")
c(f"fill {X - 4} {Y} {Z - 4} {X + 4} {Y} {Z + 4} minecraft:oak_planks")
c(f"fill {X - 4} {Y + 1} {Z - 4} {X + 4} {Y + 1} {Z + 4} minecraft:oak_fence")


SWAP = {"minecraft:oak_planks": "minecraft:barrel", "minecraft:oak_fence": "minecraft:ladder", "minecraft:stone": "minecraft:cobblestone"}


def tally(block):
    """blocks of a kind at Y-1..Y+1 in the 29x29 box: swapped for a stand-in and back (fill counts the blocks it changed)"""
    out = c(f"fill {X - 14} {Y - 1} {Z - 14} {X + 14} {Y + 1} {Z + 14} {SWAP[block]} replace {block}")
    c(f"fill {X - 14} {Y - 1} {Z - 14} {X + 14} {Y + 1} {Z + 14} {block} replace {SWAP[block]}")
    m = re.search(r"(\d+) block", out)
    return int(m.group(1)) if m else 0


planks0, fences0, stone0 = tally("minecraft:oak_planks"), tally("minecraft:oak_fence"), tally("minecraft:stone")
c("gscraft strike reset")
mark = LOG.stat().st_size
out = c(f"gscraft strike mortar {X} {Y + 1} {Z}")
for _ in range(50):
    time.sleep(1)
    if "barrage" in log_since(mark) and "complete" in log_since(mark):
        break
time.sleep(3)
planks1, fences1, stone1 = tally("minecraft:oak_planks"), tally("minecraft:oak_fence"), tally("minecraft:stone")
check("a mortar mission on a plank platform: wood gone, stone untouched", "mortar" in out.lower() and (planks1 < planks0 or fences1 < fences0) and stone1 == stone0,
      f"[{out[:40]}] planks {planks0} -> {planks1}, fences {fences0} -> {fences1}, stone {stone0} -> {stone1}")

c(f"kill @e[type=item,x={X - 20},y={Y - 5},z={Z - 20},dx=40,dy=20,dz=40]")
c(f"fill {X - 14} {Y - 1} {Z - 14} {X + 14} {Y + 8} {Z + 14} minecraft:air")
c(f"forceload remove {X - 32} {Z - 32} {X + 32} {Z + 32}")
c("gscraft director resume")
r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
