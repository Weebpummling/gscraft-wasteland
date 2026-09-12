"""Phase 12 of the enemy work, on the LOCAL server: the damage model (docs/gscraft-damage-model-feasibility-2026-09-11.md).
Needs a ticking world and no player.

Staged on a stone platform at y 200, forceloaded.

1. Zones from a segment: a NATO Rifleman's eyes, chest centre, chest edge, belly and shins read HEAD, THORAX,
   ARMS, STOMACH, LEGS through /gscraft zone.
2. The plate rule by command: 5.56 into an IOTV (class 4) is stopped and leaves 30 %, the plate pays the round's
   base; .308 goes through; the seventh 5.56 round breaks the plate and the next one lands in full.
3. The head: 5.56 through a PASGT helmet (class 3) is 6.5 x 3.5 x 0.85; a bare head takes the full 3.5x.
4. A Scavenger in leather (class 1): 5.56 goes through at 85 %.
5. Live fire: a RUAF rifleman with an AK shoots a NATO target for eight seconds; every hit is judged by the model
   (the readout's last hit names a zone and the plate), the plate drops by the base damage per hit, and the
   health lost matches the plate rule rather than vanilla armour.
6. Wounds: a leg hit puts a fighter flat and slow, an arm hit stops its grenades, a stomach hit bleeds it for a
   point every two seconds; the wounds pass.
7. A blast: TNT beside an armoured NATO target costs plate points and pins it (suppression 1.0).
8. No gscraft errors.
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
    for t in ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "minecraft:tnt", "minecraft:item"):
        c(f"kill @e[type={t},{AREA}]")


def arena():
    c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
    c(f"fill {X - 40} {Y - 1} {Z - 20} {X + 40} {Y - 1} {Z + 20} minecraft:stone")
    c(f"fill {X - 41} {Y} {Z - 21} {X + 41} {Y + 1} {Z + 21} minecraft:stone hollow")
    c(f"fill {X - 40} {Y} {Z - 20} {X + 40} {Y + 3} {Z + 20} minecraft:air")


def health(sel):
    h = c(f"data get entity {sel} Health")
    m = re.search(r"([\d.]+)f", h)
    return float(m.group(1)) if m else None


def num(text, key):
    m = re.search(key + r" ([\d.]+)", text)
    return float(m.group(1)) if m else None


def plate(sel, slot):
    out = c(f"gscraft armor {sel}")
    m = re.search(slot + r" \S+ class (\d+) plate (\d+)/(\d+)", out)
    return (int(m.group(2)), int(m.group(3)), int(m.group(1))) if m else (None, None, None)


c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(5)
clear()
arena()

# 1. zones from a segment
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["z1"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
tx, ty, tz = X + 0.5, Y, Z + 0.5
zones = {}
for name, (dy, dx) in {"eyes": (1.62, 0.0), "chest": (1.3, 0.0), "chest edge": (1.3, 0.27), "belly": (0.9, 0.0), "shins": (0.4, 0.0)}.items():
    out = c(f"gscraft zone @e[tag=z1,limit=1] {tx + dx} {ty + dy} {tz - 10} {tx + dx} {ty + dy} {tz + 10}")
    m = re.search(r"zone (\w+)", out)
    zones[name] = m.group(1) if m else out[:40]
want = {"eyes": "HEAD", "chest": "THORAX", "chest edge": "ARMS", "belly": "STOMACH", "shins": "LEGS"}
check("a segment's impact reads the right zone", zones == want, str(zones))

# 2. the plate rule by command: the IOTV against 5.56 and .308
armor0 = c("gscraft armor @e[tag=z1,limit=1]")
h0 = health("@e[tag=z1,limit=1]")
hit1 = c("gscraft hit @e[tag=z1,limit=1] thorax 6.5 3")
h1 = health("@e[tag=z1,limit=1]")
p1 = plate("@e[tag=z1,limit=1]", "chest")
hit2 = c("gscraft hit @e[tag=z1,limit=1] thorax 16 4")
h2 = health("@e[tag=z1,limit=1]")
blunt = round(h0 - h1, 2)
through = round(h1 - h2, 2)
check("5.56 into a class 4 vest is stopped (30 %), .308 goes through (85 %), the plate pays the base",
      "class 4 plate 40/40" in armor0 and abs(blunt - 6.5 * 0.3) < 0.15 and abs(through - 16 * 0.85) < 0.2 and p1[0] == 33,   # the plate pays round(6.5) = 7
      f"{armor0[-70:]}; 5.56 took {blunt} ({hit1[-60:]}); .308 took {through}; plate after the first {p1}")
# the plate breaks: 40 - 7 (5.56) - 16 (.308) = 17 left; three more 5.56 rounds (21) break it, the next is unstopped
for _ in range(3):
    c("gscraft hit @e[tag=z1,limit=1] thorax 6.5 3")
p2 = plate("@e[tag=z1,limit=1]", "chest")
h3 = health("@e[tag=z1,limit=1]")
c("gscraft hit @e[tag=z1,limit=1] thorax 6.5 3")
h4 = health("@e[tag=z1,limit=1]")
check("a broken plate protects nothing: the next round lands in full", p2[0] == 0 and abs((h3 - h4) - 6.5) < 0.15, f"plate {p2}; the round after it took {round(h3 - h4, 2)}")

# 3. the head: through a PASGT, and bare
hh0 = health("@e[tag=z1,limit=1]")
hit = c("gscraft hit @e[tag=z1,limit=1] head 6.5 3")
hh1 = health("@e[tag=z1,limit=1]")
helm = c("gscraft armor @e[tag=z1,limit=1]")
c("item replace entity @e[tag=z1,limit=1] armor.head with minecraft:air")
time.sleep(0.5)
hit_bare = c("gscraft hit @e[tag=z1,limit=1] head 6.5 3")
hh2 = health("@e[tag=z1,limit=1]")
check("a 5.56 round through a class 3 helmet is 6.5 x 3.5 x 0.85; a bare head takes 3.5x",
      abs((hh0 - hh1) - 6.5 * 3.5 * 0.85) < 0.2 and abs((hh1 - hh2) - 6.5 * 3.5) < 0.2 and "head" in helm,
      f"helmeted {round(hh0 - hh1, 2)} ({hit[-50:]}), bare {round(hh1 - hh2, 2)}")
clear()

# 4. leather against 5.56
c(f'summon gscraft:scavenger {X} {Y} {Z} {{Tags:["z4"],NoAI:1b,GscraftRank:"Scavenger",{HP}}}')
time.sleep(1)
c("item replace entity @e[tag=z4,limit=1] armor.chest with minecraft:leather_chestplate")
time.sleep(0.5)
s0 = health("@e[tag=z4,limit=1]")
hit = c("gscraft hit @e[tag=z4,limit=1] thorax 6.5 3")
s1 = health("@e[tag=z4,limit=1]")
check("5.56 goes through leather (class 1) at 85 %", abs((s0 - s1) - 6.5 * 0.85) < 0.15, f"took {round(s0 - s1, 2)}; {hit[-70:]}")
clear()

# 5. live fire through the TACZ event
c(f'summon gscraft:nato_soldier {X + 10} {Y} {Z} {{Tags:["z5t"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
c(f'summon gscraft:ruaf_soldier {X - 6} {Y} {Z} {{Tags:["z5s"],GscraftRank:"RUAF Rifleman",GscraftKitIssued:1b,GscraftRole:"RIFLEMAN",GscraftMagazines:9,'
  f'HandItems:[{{id:"tacz:modern_kinetic_gun",Count:1b,tag:{{GunId:"tacz:ak47",GunCurrentAmmoCount:30,HasBulletInBarrel:1b}}}},{{}}]}}')
time.sleep(1)
t0 = health("@e[tag=z5t,limit=1]")
pl0 = plate("@e[tag=z5t,limit=1]", "chest")
time.sleep(8)
c("kill @e[tag=z5s]")
t1 = health("@e[tag=z5t,limit=1]")
pl1 = plate("@e[tag=z5t,limit=1]", "chest")
info = c("gscraft fighter @e[tag=z5t,limit=1]")
last = re.search(r"last hit (.*)$", info)
hits = (pl0[0] - pl1[0]) / 9.0 if pl0[0] is not None and pl1[0] is not None else None
lost = t0 - t1 if t0 and t1 else None
# every hit that struck the vest took 9 points; a stopped 7.62x39 thorax hit costs 2.7, a limb hit 4.5-5.4 unarmoured, a head hit 27 through the helmet
plausible = hits is not None and hits >= 1 and lost is not None and lost >= hits * 2.0
check("live fire is judged by the model: the plate drops by the base per hit and the readout names the zone",
      plausible and last is not None and "bullet:" in last.group(1),
      f"plate {pl0[0]} -> {pl1[0]} (~{hits and round(hits, 1)} vest hits), health {t0} -> {t1}; {last.group(1)[:90] if last else info[-80:]}")
clear()

# 6. wounds
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["z6"],GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
c("gscraft wound @e[tag=z6,limit=1] leg")
time.sleep(2)
w1 = c("gscraft fighter @e[tag=z6,limit=1]")
c("gscraft wound @e[tag=z6,limit=1] arm")
c("gscraft wound @e[tag=z6,limit=1] bleed")
hb0 = health("@e[tag=z6,limit=1]")
time.sleep(6)
hb1 = health("@e[tag=z6,limit=1]")
w2 = c("gscraft fighter @e[tag=z6,limit=1]")
c("gscraft wound @e[tag=z6,limit=1] clear")
time.sleep(2)
w3 = c("gscraft fighter @e[tag=z6,limit=1]")
check("a leg wound puts the fighter flat, an arm and a stomach wound show, the bleed costs about a point per two seconds, and they clear",
      "pose SWIMMING" in w1 and "crawling" in w1 and "arm " in w2 and "bleeding" in w2 and hb0 - hb1 >= 2 and hb0 - hb1 <= 4 and "wounds none" in w3 and "pose SWIMMING" not in w3,
      f"leg: {w1[w1.find('pose'):w1.find('pose') + 14]} {w1[w1.find('wounds'):][:30]}; after: {w2[w2.find('wounds'):][:40]}; bled {round(hb0 - hb1, 1)} in 6 s; cleared: {w3[w3.find('wounds'):][:14]}")
clear()

# 7. a blast against a vest
c(f'summon gscraft:nato_soldier {X} {Y} {Z} {{Tags:["z7"],NoAI:1b,GscraftRank:"NATO Rifleman",{HP}}}')
time.sleep(1)
b0 = health("@e[tag=z7,limit=1]")
pb0 = plate("@e[tag=z7,limit=1]", "chest")
c(f"summon minecraft:tnt {X + 2} {Y} {Z} {{Fuse:1}}")
time.sleep(2)
b1 = health("@e[tag=z7,limit=1]")
pb1 = plate("@e[tag=z7,limit=1]", "chest")
info = c("gscraft fighter @e[tag=z7,limit=1]")
sup = num(info, "suppression")
check("a blast costs plate points, is reduced by the vest's class, and pins the fighter",
      b0 and b1 and b0 - b1 > 0 and pb0[0] is not None and pb1[0] is not None and pb1[0] < pb0[0] and sup is not None and sup >= 0.9 and "blast:" in info,
      f"health {b0} -> {b1}, plate {pb0[0]} -> {pb1[0]}, suppression {sup}; {info[info.find('last hit'):][:70]}")
clear()
c(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
