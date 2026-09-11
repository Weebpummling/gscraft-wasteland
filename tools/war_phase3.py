"""Phase 3 of the enemy review, on the LOCAL server (127.0.0.1): ranks as data, roles, finite ammunition, hearing.
Needs a ticking world and no player. Run war_phase2.py after it as the regression.

1. Rank data loaded: /gscraft ranks lists NATO 5, RUAF 5, Scavengers 6.
2. Every NATO and RUAF rank, pinned by GscraftRank, carries its role's gun (and the Shield its shield).
3. Finite ammunition: a rifleman with no spare magazine empties his gun and closes to melee.
4. Reloading spends a spare magazine.
5. The Marksman holds his distance and still lands shots at 30 blocks.
6. Hearing: a RUAF soldier beyond sight range walks toward NATO gunfire.
In person, not here: the Shield's block, the Gunner's suppression, the Sergeant calling targets.
"""
import math
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
X, Z = -2000, -600
AREA = f"x={X},z={Z},distance=..90"
HELMET = 'ArmorItems:[{},{},{},{id:"minecraft:leather_helmet",Count:1b}]'
CLEAR = ["minecraft:zombie", "gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger"]
EXPECT = {   # each rank's allowed guns (a rank may vary its weapon) and the offhand it must carry
    "NATO Rifleman": ({"tacz:m4a1", "tacz:hk416d", "tacz:m16a4"}, None),
    "NATO Sergeant": ({"tacz:m4a1", "tacz:hk416d", "tacz:scar_l"}, None),
    "NATO Marksman": ({"tacz:mk14", "tacz:m700", "tacz:spr15hb"}, None),
    "NATO Gunner": ({"tacz:m249"}, None),
    "NATO Shield": ({"tacz:m9a4", "tacz:glock_17", "tacz:p320"}, "minecraft:shield"),
    "RUAF Rifleman": ({"tacz:ak47", "cib:ak105", "cib:ak103"}, None), "RUAF Sergeant": ({"tacz:ak47", "cib:ak105", "cib:asval"}, None),
    "RUAF Marksman": ({"tacz:sks_tactical", "cib:svd", "tacz:kar98"}, None), "RUAF Gunner": ({"tacz:rpk", "cib:pkp"}, None),
    "RUAF Shield": ({"tacz:cz75", "tacz:glock_17"}, "minecraft:shield"),
}

r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size


def c(cmd, t=30):
    return (r.cmd(cmd, timeout=t) or "").strip()


def val(sel, path):
    out = c(f"data get entity {sel} {path}")
    return out.split("entity data: ", 1)[1].strip() if "entity data: " in out else None


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def pos(sel):
    v = val(sel, "Pos")
    if not v:
        return None
    nums = [float(n) for n in re.findall(r"-?[\d.]+(?=d)", v)]
    return nums if len(nums) == 3 else None


def dist(a, b):
    pa, pb = pos(a), pos(b)
    return math.dist((pa[0], pa[2]), (pb[0], pb[2])) if pa and pb else None


def num(sel, path):
    v = val(sel, path)
    m = re.search(r"-?[\d.]+", v or "")
    return float(m.group(0)) if m else None


def at(dx, dz):
    return f"execute positioned {X + dx} 0 {Z + dz} positioned over motion_blocking_no_leaves run "


def zombie(tag, hp):
    return (f'summon minecraft:zombie ~ ~ ~ {{NoAI:1b,Tags:["gs_placed","{tag}"],Health:{hp}f,'
            f'Attributes:[{{Name:"minecraft:generic.max_health",Base:{hp}d}}],{HELMET}}}')


def pinned_gun(entity, tag, rank, role, mags, gun, ammo):
    return (f'summon {entity} ~ ~ ~ {{Tags:["{tag}"],GscraftKitIssued:1b,GscraftRank:"{rank}",GscraftRole:"{role}",'
            f'GscraftMagazines:{mags},HandItems:[{{id:"tacz:modern_kinetic_gun",Count:1b,'
            f'tag:{{GunId:"{gun}",GunCurrentAmmoCount:{ammo},HasBulletInBarrel:1b}}}},{{}}]}}')


def clear():
    for t in CLEAR:
        c(f"kill @e[type={t},{AREA}]")
    time.sleep(1)


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


out = c("gscraft ranks")
counts = {f: len(re.findall(r"\(", seg)) for f, seg in re.findall(r"(\w+):((?:\s[^:]+?\(\w+, \d+\))+)", out)}
check("rank data loaded", counts.get("nato") == 5 and counts.get("ruaf") == 5 and counts.get("scavengers") == 6, counts)

c(f"forceload add {X - 90} {Z - 90} {X + 90} {Z + 90}", 60)
time.sleep(6)
clear()

# 2. every rank carries its role's gun
for i, (rank, (gun, off)) in enumerate(EXPECT.items()):
    entity = "gscraft:nato_soldier" if rank.startswith("NATO") else "gscraft:ruaf_soldier"
    c(at(-20 + 4 * (i % 10), -20) + f'summon {entity} ~ ~ ~ {{NoAI:1b,Tags:["p3r{i}"],GscraftRank:"{rank}"}}')
time.sleep(3)
bad = []
for i, (rank, (gun, off)) in enumerate(EXPECT.items()):
    got = (val(f"@e[tag=p3r{i},limit=1]", "HandItems[0].tag.GunId") or "").strip('"')
    got_off = (val(f"@e[tag=p3r{i},limit=1]", "HandItems[1].id") or "").strip('"') or None
    role = (val(f"@e[tag=p3r{i},limit=1]", "GscraftRole") or "").strip('"')
    if got not in gun or (off and got_off != off):
        bad.append(f"{rank}: gun {got}, offhand {got_off}, role {role}")
check("each rank carries its role's gun", not bad, bad or f"{len(EXPECT)} ranks as specified")
clear()

# 3. finite ammunition: three rounds, no spare magazine, then melee
c(at(0, 0) + pinned_gun("gscraft:nato_soldier", "p3a", "NATO Rifleman", "RIFLEMAN", 0, "tacz:m4a1", 3))
c(at(12, 0) + zombie("p3z", 100))
d = None
for _ in range(12):
    time.sleep(3)
    d = dist("@e[tag=p3a,limit=1]", "@e[tag=p3z,limit=1]")
    if d is not None and d < 3.5:
        break
ammo = num("@e[tag=p3a,limit=1]", "HandItems[0].tag.GunCurrentAmmoCount")
oob = val("@e[tag=p3a,limit=1]", "GscraftOutOfAmmo")
check("out of ammunition, the rifleman closes to melee", d is not None and d < 3.5 and ammo == 0 and oob == "1b",
      f"distance {d and round(d, 1)}, rounds left {ammo}, out of ammo {oob}")
clear()

# 4. a reload spends a spare magazine
c(at(0, 0) + pinned_gun("gscraft:nato_soldier", "p3b", "NATO Rifleman", "RIFLEMAN", 1, "tacz:m4a1", 2))
c(at(10, 0) + zombie("p3y", 300))
mags = None
for _ in range(10):
    time.sleep(3)
    mags = num("@e[tag=p3b,limit=1]", "GscraftMagazines")
    if mags == 0:
        break
check("a reload spends a spare magazine", mags == 0, f"spare magazines now {mags}")
clear()

# 5. the Marksman holds distance and lands shots
c(at(0, 0) + 'summon gscraft:nato_soldier ~ ~ ~ {Tags:["p3m"],GscraftRank:"NATO Marksman"}')
c(at(30, 0) + zombie("p3x", 200))
time.sleep(25)
d = dist("@e[tag=p3m,limit=1]", "@e[tag=p3x,limit=1]")
hp = num("@e[tag=p3x,limit=1]", "Health")
check("the Marksman holds his distance and hits", d is not None and d > 24 and hp is not None and hp < 200,
      f"distance {d and round(d, 1)}, target health {hp}")
clear()

# 6. hearing: RUAF beyond its 48-block sight range walks toward NATO gunfire
c(at(0, 0) + pinned_gun("gscraft:nato_soldier", "p3n", "NATO Rifleman", "RIFLEMAN", 9, "tacz:m4a1", 30))
c(at(8, 0) + zombie("p3w", 400))
c(at(0, 58) + 'summon gscraft:ruaf_soldier ~ ~ ~ {Tags:["p3u"],GscraftRank:"RUAF Rifleman"}')
time.sleep(3)
shooter = pos("@e[tag=p3n,limit=1]")
ruaf0 = pos("@e[tag=p3u,limit=1]")
time.sleep(20)
ruaf1 = pos("@e[tag=p3u,limit=1]")
nato_alive, ruaf_alive = count("@e[tag=p3n]"), count("@e[tag=p3u]")
# measured from where the shot was fired, not from the shooter: a RUAF soldier that closes in and kills him has
# passed, and the first run of this test failed exactly that way (distance to a dead shooter reads None)
d0 = math.dist((shooter[0], shooter[2]), (ruaf0[0], ruaf0[2])) if shooter and ruaf0 else None
d1 = math.dist((shooter[0], shooter[2]), (ruaf1[0], ruaf1[2])) if shooter and ruaf1 else None
moved = d0 is not None and (ruaf_alive == 0 or (d1 is not None and d0 - d1 >= 8))
check("a RUAF soldier walks toward NATO gunfire", moved,
      f"distance to the shot {d0 and round(d0, 1)} -> {d1 and round(d1, 1)} "
      f"(NATO alive {nato_alive}, RUAF alive {ruaf_alive})")
clear()

c(f"forceload remove {X - 90} {Z - 90} {X + 90} {Z + 90}", 60)
r.close()

with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
heard = re.findall(r"\[gscraft\] shot by (\S+) heard by (\d+)", new)
check("the log records the shot being heard", heard, heard[:3])
bad = [l for l in new.splitlines() if "gscraft" in l.lower()
       and re.search(r"ERROR|invalid|not registered|not a loaded|Exception|unknown role", l)]
check("no gscraft errors, missing items or unloaded guns", not bad, f"{len(bad)} lines")
for l in bad[:8]:
    print("     ", l[:180])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
