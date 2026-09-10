"""Phase 4b of the enemy review, on the LOCAL server: each area's own creatures, equipment variety, and placement by
the kind of ground (open / indoor / underground). Needs a ticking world and no player. Run war_phase4.py,
war_phase3.py and war_phase2.py after it as the regression.

1. The Dead's own bodies stand up: the Bloater and the Matron.
2. The hospital keeps the Matron in its lair: one, persistent, not doubled.
3. Runners among the town's Dead are faster than the rest.
4. The plant's Act III ground draws Bloaters.
5. Riders come out on the collective farm's fields at night.
6. A bunker draws cave spiders with its Dead.
7. Scavengers never match; soldiers of one rank wear one uniform and vary only the rifle.
8. The sweep: at surface, indoor and underground reference points, where the first version's placement landed
   against the layered one - same ground as the player, height from the player, visible, walkable.
"""
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
CLEAR = ["gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "gscraft:bloater", "gscraft:matron",
         "minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:zombie_horse", "minecraft:cave_spider",
         "man:manfromthefog", "the_knocker:knocker", "eyesinthedarkness:eyes"]


def c(cmd, t=90):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def val(sel, path):
    out = c(f"data get entity {sel} {path}")
    return out.split("entity data: ", 1)[1].strip() if "entity data: " in out else None


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


class Site:
    def __init__(self, x, z, radius=64):
        self.x, self.z, self.rad = x, z, radius

    def area(self, extra=""):
        r_ = self.rad + 16
        return f"x={self.x - r_},y=-64,z={self.z - r_},dx={2 * r_},dy=400,dz={2 * r_}{extra}"

    def __enter__(self):
        c(f"forceload add {self.x - self.rad} {self.z - self.rad} {self.x + self.rad} {self.z + self.rad}")
        time.sleep(6)
        self.clear()
        return self

    def clear(self):
        for t in CLEAR:
            c(f"kill @e[type={t},{self.area()}]")

    def __exit__(self, *exc):
        self.clear()
        c(f"forceload remove {self.x - self.rad} {self.z - self.rad} {self.x + self.rad} {self.z + self.rad}")


def surface_y(x, z):
    c(f'execute positioned {x} 0 {z} positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {{Tags:["ysurf"]}}')
    pos = val("@e[tag=ysurf,limit=1]", "Pos") or ""
    c("kill @e[tag=ysurf]")
    nums = re.findall(r"-?[\d.]+(?=d)", pos)
    return int(float(nums[1])) if len(nums) == 3 else 64


def loadout(sel):
    armour = val(sel, "ArmorItems") or ""
    hands = val(sel, "HandItems") or ""
    ids = re.findall(r'id: "([^"]+)"', armour) + re.findall(r'id: "([^"]+)"', hands) + re.findall(r'GunId: "([^"]+)"', hands)
    return tuple(ids)


# 1. the new bodies
with Site(-2000, -600) as s:
    y = surface_y(-2000, -600)
    c(f"summon gscraft:bloater -2000 {y} -600")
    c(f"summon gscraft:matron -1996 {y} -600")
    time.sleep(3)
    b, m = count(f"@e[type=gscraft:bloater,{s.area()}]"), count(f"@e[type=gscraft:matron,{s.area()}]")
    hb = val(f"@e[type=gscraft:bloater,{s.area()},limit=1]", "Health")
    hm = val(f"@e[type=gscraft:matron,{s.area()},limit=1]", "Health")
    check("the Bloater and the Matron stand up", b == 1 and m == 1, f"bloater {b} ({hb}), matron {m} ({hm})")

# 2. the Matron's lair
with Site(-825, -1292) as s:
    first = c("gscraft garrison sk_hosp force")
    time.sleep(2)
    n1 = count("@e[type=gscraft:matron,tag=gs_lair_sk_hosp]")
    persistent = val("@e[type=gscraft:matron,tag=gs_lair_sk_hosp,limit=1]", "PersistenceRequired")
    again = c("gscraft garrison sk_hosp force")
    n2 = count("@e[type=gscraft:matron,tag=gs_lair_sk_hosp]")
    check("the hospital keeps one Matron in its lair", n1 == 1 and n2 == 1 and persistent == "1b",
          f"{first}; then {again}; matrons {n1} -> {n2}; persistent {persistent}")
    c("kill @e[type=gscraft:matron,tag=gs_lair_sk_hosp]")

# 3. Runners in the town
with Site(-2380, -2975) as s:
    reply = c("gscraft director pass -2380 -2975 60")
    runners = count(f'@e[name="Runner",{s.area()}]')
    speed = c(f'attribute @e[name="Runner",{s.area()},limit=1] minecraft:generic.movement_speed get') if runners else ""
    m_ = re.search(r"is ([\d.]+)", speed)
    sp = float(m_.group(1)) if m_ else 0.0
    check("Runners among the town's Dead, faster than the rest", runners > 0 and sp > 0.26,
          f"{reply}; runners {runners}, speed {sp:.3f} (a zombie is 0.230)")

# 4. Bloaters at the plant
with Site(450, 480) as s:
    reply = c("gscraft director pass 450 480 60")
    bloaters = count(f"@e[type=gscraft:bloater,{s.area()}]")
    check("the plant's Act III ground draws Bloaters", bloaters > 0, f"{reply}; bloaters {bloaters}")

# 5. Riders at night on the farm
day = re.search(r"(\d+)\s*$", c("time query daytime"))
with Site(-2110, -900) as s:
    c("time set 18000")
    time.sleep(2)                      # the day flag follows the clock on the next tick
    reply = c("gscraft director pass -2110 -900 60")
    riders = count(f'@e[type=minecraft:zombie,name="Rider",{s.area()}]')
    mounted = count(f"@e[type=minecraft:zombie_horse,{s.area()},nbt={{Passengers:[{{}}]}}]")
    check("Riders on the farm's fields at night", riders > 0 and mounted > 0, f"{reply}; riders {riders}, mounted horses {mounted}")
    if day:
        c(f"time set {day.group(1)}")

# 6. a bunker draws cave spiders
with Site(-2350, 20) as s:
    reply = c("gscraft director passat -2350 -13 20 40")
    spiders = count(f"@e[type=minecraft:cave_spider,{s.area()}]")
    dead = count(f"@e[type=minecraft:zombie,{s.area()}]")
    check("the Woods bunker draws cave spiders with its Dead", spiders > 0, f"{reply}; cave spiders {spiders}, Dead {dead}")

# 7. Scavengers never match; soldiers wear one uniform per rank
with Site(-2000, -600) as s:
    c("gscraft director pass -2000 -600 80")
    n = min(count(f"@e[type=gscraft:scavenger,{s.area()}]"), 20)
    looks = []
    for i in range(n):
        c(f"tag @e[type=gscraft:scavenger,tag=!sv,{s.area()},limit=1] add sv{i}")
        c(f"tag @e[tag=sv{i}] add sv")
        looks.append(loadout(f"@e[tag=sv{i},limit=1]"))
    distinct = len(set(looks))
    check("Scavengers never match", n >= 8 and distinct >= 0.7 * n, f"{distinct} different loadouts among {n} Scavengers")

with Site(450, 480) as s:
    c("gscraft director pass 450 480 80")
    n = min(count(f'@e[name="NATO Rifleman",{s.area()}]'), 12)
    chests, guns = Counter(), Counter()
    for i in range(n):
        c(f'tag @e[name="NATO Rifleman",tag=!nr,{s.area()},limit=1] add nr{i}')
        c(f"tag @e[tag=nr{i}] add nr")
        chests[(val(f"@e[tag=nr{i},limit=1]", "ArmorItems[2].id") or "").strip('"')] += 1
        guns[(val(f"@e[tag=nr{i},limit=1]", "HandItems[0].tag.GunId") or "").strip('"')] += 1
    check("NATO Riflemen wear one uniform and vary the rifle",
          n >= 4 and list(chests) == ["superbwarfare:us_chest_iotv"] and set(guns) <= {"tacz:m4a1", "tacz:hk416d", "tacz:m16a4"},
          f"{n} riflemen; chests {dict(chests)}; rifles {dict(guns)}")

with Site(-2000, -2600) as s:
    c("gscraft director pass -2000 -2600 80")
    n = min(count(f'@e[name="RUAF Rifleman",{s.area()}]'), 12)
    chests, guns = Counter(), Counter()
    for i in range(n):
        c(f'tag @e[name="RUAF Rifleman",tag=!rr,{s.area()},limit=1] add rr{i}')
        c(f"tag @e[tag=rr{i}] add rr")
        chests[(val(f"@e[tag=rr{i},limit=1]", "ArmorItems[2].id") or "").strip('"')] += 1
        guns[(val(f"@e[tag=rr{i},limit=1]", "HandItems[0].tag.GunId") or "").strip('"')] += 1
    sy = surface_y(-2000, -2600)
    sergeant = c(f"summon gscraft:ruaf_soldier -2000 {sy} -2600 {{GscraftRank:\"RUAF Sergeant\",Tags:[\"rsgt\"]}}")
    time.sleep(1)
    sgt_chest = (val("@e[tag=rsgt,limit=1]", "ArmorItems[2].id") or "").strip('"')
    check("RUAF Riflemen wear one uniform and vary the rifle; the Sergeant is not dressed as NATO's",
          n >= 4 and list(chests) == ["superbwarfare:ru_chest_6b43"]
          and set(guns) <= {"tacz:ak47", "cib:ak105", "cib:ak103"} and len(guns) >= 2
          and sgt_chest == "dragonrise_reforge:msv_chest",
          f"{n} riflemen; chests {dict(chests)}; rifles {dict(guns)}; sergeant's chest {sgt_chest}")

# 8. the sweep: first version against layered, by the kind of ground
print("\n  sweep: where placement lands, by reference point")
refs = [("town centre, street", -2380, None, -2975), ("Skadowsky, street", -820, None, -1120),
        ("the Woods, ground", -2000, None, -600), ("the plant, yard", 450, None, 480)]
for label, x, z in (("RUAF post, inside", -752, -1124), ("Skadowsky, inside", -820, -1120),
                    ("hospital, inside", -825, -1292), ("town centre, inside", -2380, -2975)):
    with Site(x, z):
        m = re.search(r"room at (-?\d+) (-?\d+) (-?\d+)", c(f"gscraft director room {x} {z} 48"))
    if m:
        refs.append((label, int(m.group(1)), int(m.group(2)), int(m.group(3))))
    else:
        print(f"  - {label}: no ground-floor room within 48 blocks")
refs += [("Woods bunker", -2350, -13, 20), ("Woods bunker 2", -2308, -18, 18), ("town cellar", -2666, 33, -2743),
         ("west-front dungeon", -1290, 4, -846), ("farmstead bunker", -1460, 25, -277)]
layered_same = []
for label, x, y, z in refs:
    with Site(x, z):
        if y is None:
            y = surface_y(x, z)
        out = c(f"gscraft director survey {x} {y} {z} 150")
    lines = out.split("\n") if "\n" in out else re.split(r"(?=first version:|layered:)", out)
    head = next((l for l in lines if l.startswith("survey")), out[:120])
    first = next((l for l in lines if l.startswith("first version")), "")
    layer = next((l for l in lines if l.startswith("layered")), "")
    print(f"  - {label} ({x} {y} {z}): {head.split(', zone ')[-1] if ', zone ' in head else head}")
    print(f"      {first}")
    print(f"      {layer}")
    same = re.search(r"same ground as you (\d+)%", layer)
    found = re.search(r"found (\d+) of", layer)
    if same and found and int(found.group(1)) > 0:
        layered_same.append(int(same.group(1)))
check("layered placement stays on the player's kind of ground", layered_same and min(layered_same) >= 90,
      f"same-ground share per reference {layered_same}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if "gscraft" in l.lower()
       and re.search(r"ERROR|invalid|not registered|not a loaded|unknown entity|Exception", l)]
check("no gscraft errors, missing items or unloaded guns", not bad, f"{len(bad)} lines")
for l in bad[:10]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
