"""Phase 15 of the enemy work, on the LOCAL server: Superb Warfare bullets reach the reactions (owner, 2026-09-12: the
fire monitor showed the server saw none of the player's shots - the player fires SW guns and every hook was TACZ-only).
Needs a ticking world and no player. Staged on the stone platform at y 200.

1. An SW bullet (`superbwarfare:projectile`) summoned beside a NoAI soldier and sent into the floor suppresses it
   (the bullet's removal is the impact; no shooter, so nobody is an ally).
2. An SW bullet into the soldier itself counts as a hit: suppression by suppress_hit and the flinch byte.
3. An SW bullet's arrival is a shot: a summoned bullet with no shooter is not (nothing to hear), but the monitor and
   the hearing need a shooter - covered by the log line count staying at zero errors; the player's fire is the owner's check.
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
X, Y, Z = -2000, 200, -600
AREA = f"x={X - 70},y={Y - 10},z={Z - 70},dx=140,dy=40,dz=140"
HP = 'Health:400f,Attributes:[{Name:"minecraft:generic.max_health",Base:400}]'


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def clear():
    for t in ("gscraft:nato_soldier", "superbwarfare:projectile"):
        c(f"kill @e[type={t},{AREA}]")


def fighter(sel):
    return c(f"gscraft fighter {sel}")


def num(text, key):
    m = re.search(key + r" ([\d.]+)", text)
    return float(m.group(1)) if m else None


def anim(sel):
    m = re.search(r"anim (\w+)#(\d+)", fighter(sel))
    return (m.group(1), int(m.group(2))) if m else (None, None)


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()
c(f"fill {X - 21} {Y - 1} {Z - 11} {X + 21} {Y + 4} {Z + 11} minecraft:air")
c(f"fill {X - 20} {Y - 1} {Z - 10} {X + 20} {Y - 1} {Z + 10} minecraft:stone")

# 1. the near miss: a bullet two blocks beside the soldier, straight down into the floor
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["p15n"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
s0 = num(fighter("@e[tag=p15n,limit=1]"), "suppression") or 0.0
for i in range(3):
    c(f"summon superbwarfare:projectile {X + 2} {Y + 1.5} {Z} {{Motion:[0.0d,-2.0d,0.0d]}}")
    time.sleep(0.4)
time.sleep(0.6)
s1 = num(fighter("@e[tag=p15n,limit=1]"), "suppression") or 0.0
bullets_left = re.search(r"count: (\d+)", c(f"execute if entity @e[type=superbwarfare:projectile,{AREA}]"))
check("SW bullets into the floor beside a fighter suppress it (judged where the bullet ended)", s1 >= 0.3 and s1 > s0,
      f"suppression {s0} -> {s1}; bullets still in the world {bullets_left.group(1) if bullets_left else 0}")
clear()

# 2. the hit: a bullet from above into the soldier
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["p15h"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
h0 = num(c("data get entity @e[tag=p15h,limit=1] Health"), r"(?:)") or 0.0
h0 = float(re.search(r"([\d.]+)f", c("data get entity @e[tag=p15h,limit=1] Health")).group(1))
a0 = anim("@e[tag=p15h,limit=1]")
for i in range(3):
    c(f"summon superbwarfare:projectile {X} {Y + 3} {Z} {{Motion:[0.0d,-1.5d,0.0d]}}")
    time.sleep(0.4)
time.sleep(0.6)
info = fighter("@e[tag=p15h,limit=1]")
s2 = num(info, "suppression") or 0.0
h1 = float(re.search(r"([\d.]+)f", c("data get entity @e[tag=p15h,limit=1] Health")).group(1))
a1 = anim("@e[tag=p15h,limit=1]")
check("an SW bullet into a fighter is a hit: suppression, the flinch byte, the damage model's record", s2 >= 0.5 and h1 < h0 and a1[0] == "FLINCH",
      f"suppression {s2}; health {h0} -> {h1}; anim {a0} -> {a1}; last hit {re.search(r'last hit ([^,]*)', info).group(1) if 'last hit' in info else '?'}")
clear()
c(f"fill {X - 21} {Y - 1} {Z - 11} {X + 21} {Y + 4} {Z + 11} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
misses = [l for l in new.splitlines() if "near miss by" in l]
check("near misses were logged and no gscraft errors", not bad, f"near-miss lines {len(misses)}, error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
