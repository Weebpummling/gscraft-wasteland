"""Phase 5 of the enemy work, on the LOCAL server: the first fold-in (docs/gscraft-fold-in-review-2026-09-10.md
step 1). The hold, the locks, the mech griefing rule, the Dead's drops and the projectile sweep live in the mod;
In Control is gone. Needs a ticking world and no player. Run war_phase4b.py, war_phase4.py, war_phase3.py and
war_phase2.py after it.

1. In Control is not loaded; the mod's own data loaded (locks, drops).
2. The hold: an untagged hostile is refused, a tagged one and a mod body pass, and the hold can be switched off.
3. The lock: an explosion inside the mast field takes no block; the same charge outside does. A piston inside
   does not extend; outside it does.
4. The drops: the Dead's rules loaded for every type In Control had.
5. The projectile sweep: a gun-mod projectile older than the sweep's age is retired.
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


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def block_is(x, y, z, block):
    return "passed" in c(f"execute if block {x} {y} {z} {block}")


# 1. what is loaded
boot = LOG.read_text(encoding="utf-8", errors="replace")
m = re.search(r"Loading (\d+) mods:((?:\n.*?- .*)+)", boot)
loaded = m.group(2) if m else ""
check("In Control is not loaded", m is not None and "incontrol" not in loaded.lower(), f"{m.group(1) if m else 'no'} mods in the boot log")
check("locks and drops loaded", "locks loaded: [tower_compound]" in boot and "drops loaded: 65 rules for 5 entity types" in boot,
      f"{'locks ok' if 'locks loaded' in boot else 'no locks line'}; {'drops ok' if 'drops loaded' in boot else 'no drops line'}")

# 2. the hold
X, Z = -2000, -600
c(f"forceload add {X - 32} {Z - 32} {X + 32} {Z + 32}")
time.sleep(5)
area = f"x={X - 40},y=-64,z={Z - 40},dx=80,dy=400,dz=80"
for t in ("minecraft:zombie", "minecraft:skeleton", "gscraft:scavenger", "minecraft:creeper"):
    c(f"kill @e[type={t},{area}]")
c(f"summon minecraft:zombie {X} 80 {Z} {{NoAI:1b,Tags:[\"h_bare\"]}}")
c(f"summon minecraft:zombie {X + 2} 80 {Z} {{NoAI:1b,Tags:[\"gs_placed\",\"h_tag\"]}}")
c(f"summon gscraft:scavenger {X + 4} 80 {Z} {{NoAI:1b,Tags:[\"h_mod\"]}}")
c(f"summon minecraft:skeleton {X + 6} 80 {Z} {{NoAI:1b,Tags:[\"h_skel\"]}}")
time.sleep(1)
bare, tag, mod, skel = count("@e[tag=h_bare]"), count("@e[tag=h_tag]"), count("@e[tag=h_mod]"), count("@e[tag=h_skel]")
status = c("gscraft hold status")
check("the hold refuses a bare hostile and passes a tagged one and a mod body", bare == 0 and skel == 0 and tag == 1 and mod == 1,
      f"bare zombie {bare}, bare skeleton {skel}, tagged zombie {tag}, scavenger {mod}; {status}")
c("gscraft hold off")
c(f"summon minecraft:zombie {X} 80 {Z} {{NoAI:1b,Tags:[\"h_off\"]}}")
time.sleep(1)
off = count("@e[tag=h_off]")
c("gscraft hold on")
c(f"summon minecraft:zombie {X} 80 {Z} {{NoAI:1b,Tags:[\"h_on\"]}}")
time.sleep(1)
on = count("@e[tag=h_on]")
check("the hold switches off and on", off == 1 and on == 0, f"with the hold off {off}, on again {on}")
for t in ("minecraft:zombie", "minecraft:skeleton", "gscraft:scavenger"):
    c(f"kill @e[type={t},{area}]")
c(f"forceload remove {X - 32} {Z - 32} {X + 32} {Z + 32}")

# 3. the lock: the mast field x -840..-770 z -1040..-960, all heights; the test works high in the air on its own platform
def blast(x, z, tag):
    y = 220
    c(f"fill {x - 2} {y - 1} {z - 2} {x + 2} {y - 1} {z + 2} minecraft:stone")
    c(f"summon minecraft:tnt {x} {y} {z} {{Fuse:10s,Tags:[\"{tag}\"]}}")
    time.sleep(2)
    gone = sum(0 if block_is(x + dx, y - 1, z + dz, "minecraft:stone") else 1 for dx in (-1, 0, 1) for dz in (-1, 0, 1))
    c(f"fill {x - 2} {y - 1} {z - 2} {x + 2} {y - 1} {z + 2} minecraft:air")
    return gone


def push(x, z):
    y = 220
    c(f"setblock {x} {y} {z} minecraft:piston[facing=up]")
    c(f"setblock {x + 1} {y} {z} minecraft:redstone_block")
    time.sleep(1)
    extended = block_is(x, y, z, "minecraft:piston[extended=true]")
    c(f"fill {x} {y} {z} {x + 1} {y + 1} {z} minecraft:air")
    return extended


inside, outside = (-805, -1000), (-805, -900)
for x, z in (inside, outside):
    c(f"forceload add {x - 16} {z - 16} {x + 16} {z + 16}")
time.sleep(4)
gone_in, gone_out = blast(*inside, "l_in"), blast(*outside, "l_out")
check("an explosion inside the lock takes no block; outside it does", gone_in == 0 and gone_out > 0,
      f"stone lost inside {gone_in}, outside {gone_out} of 9")
ext_in, ext_out = push(*inside), push(*outside)
check("a piston inside the lock does not extend; outside it does", not ext_in and ext_out, f"extended inside {ext_in}, outside {ext_out}")
for x, z in (inside, outside):
    c(f"forceload remove {x - 16} {z - 16} {x + 16} {z + 16}")

# 4. the drops
rules = {t: c(f"gscraft drops minecraft:{t}") for t in ("zombie", "zombie_villager", "husk", "drowned", "zombified_piglin")}
counts = {t: int(m.group(1)) if (m := re.match(r"(\d+) drop rules", v)) else -1 for t, v in rules.items()}
check("the Dead's drop rules are loaded for every type In Control had", all(n == 13 for n in counts.values()), str(counts))

# 5. the projectile sweep: with nobody online there is no ring around a player, so only the age rule applies. Every
#    Superb Warfare projectile removes itself inside 30 s (bullet 2 s, smoke 21 s), so the age is lowered for the test
c(f"forceload add {X - 32} {Z - 32} {X + 32} {Z + 32}")
time.sleep(4)
before = int(re.search(r"(\d+) retired", c("gscraft sweep")).group(1))
reply = c(f"summon superbwarfare:smoke_decoy {X} 90 {Z} {{Tags:[\"p_sweep\"]}}")
time.sleep(2)
young = count("@e[tag=p_sweep]")
c("gscraft sweep age 60")
time.sleep(3)
left = count("@e[tag=p_sweep]")
after = int(re.search(r"(\d+) retired", c("gscraft sweep")).group(1))
c("gscraft sweep age 600")
check("a gun-mod projectile is retired once it is older than the sweep's age", "Summoned" in reply and young == 1 and left == 0 and after == before + 1,
      f"{reply}; after two seconds {young}; with the age at three seconds, gone {left == 0}; retired by the sweep {after - before}")
c("kill @e[tag=p_sweep]")
c(f"forceload remove {X - 32} {Z - 32} {X + 32} {Z + 32}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors in the log", not bad, f"{len(bad)} lines")
for l in bad[:10]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
