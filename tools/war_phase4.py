"""Phase 4 of the enemy review, on the LOCAL server (127.0.0.1): the director. Needs a ticking world and no player,
so it drives the director through /gscraft director pass (placement at a point, ignoring the cap) and
/gscraft garrison <zone> force. Run war_phase3.py and war_phase2.py after it as the regression.

1. The zone map loaded: 40 zones.
2. Zone lookup at known ground: the camp and KROT excluded; the hospital, the reactor hall, the Woods, an outpost.
3. Nothing is ever placed in a build: a pass inside KROT places nothing.
4. The town draws RUAF and the Dead; the hospital draws only the Dead, dressed as The Infected; the reactor hall's
   Dead are Plant Workers and Containment Crew.
5. A Magnum Torch stops the director the way it stops natural spawns: nothing placed beside a diamond torch, and
   placement resumes once the torch is gone.
6. A garrison fills to strength, is persistent and bound to its post, and tops back up after losses.
7. The fog man is admitted to the Woods at night, and only one.
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
FIGHTERS = ["gscraft:nato_soldier", "gscraft:ruaf_soldier", "gscraft:scavenger", "minecraft:zombie",
            "minecraft:husk", "minecraft:drowned", "man:manfromthefog"]


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


class Site:
    """forceload a square around a point for the length of a test, and clear what the director left there"""

    def __init__(self, x, z, radius=64):
        self.x, self.z, self.rad = x, z, radius

    def area(self, extra=""):
        # a full-height box, not a sphere: a sphere is centred at the command source's height, and the director
        # stands the Dead on whatever is there - the reactor hall's roof is at y 198, far outside a sphere at 65
        r = self.rad + 16
        return f"x={self.x - r},y=-64,z={self.z - r},dx={2 * r},dy=400,dz={2 * r}{extra}"

    def __enter__(self):
        c(f"forceload add {self.x - self.rad} {self.z - self.rad} {self.x + self.rad} {self.z + self.rad}")
        time.sleep(6)
        self.clear()
        return self

    def clear(self):
        for t in FIGHTERS:
            c(f"kill @e[type={t},{self.area()}]")

    def __exit__(self, *exc):
        self.clear()
        c(f"forceload remove {self.x - self.rad} {self.z - self.rad} {self.x + self.rad} {self.z + self.rad}")


def placed(reply):
    m = re.search(r"placed (\d+) of (\d+)", reply)
    return int(m.group(1)) if m else -1


out = c("gscraft zones")
check("zone map loaded", "40 zones" in out, out)

lookups = {(-870, -950): "camp (excluded)", (-3233, -1185): "krot (excluded)", (-782, -1277): "sk_hosp",
           (-642, 518): "pl_react", (-2000, -600): "woods", (-840, -540): "out_e1", (400, -3000): "open"}
bad = []
for (x, z), want in lookups.items():
    got = c(f"gscraft zone {x} {z}")
    name = want.split(" ")[0]
    if not got.startswith(f"zone {name}") or ("excluded" in want) != ("(excluded)" in got):
        bad.append(f"{x},{z}: {got[:60]}")
check("zone lookup at known ground", not bad, bad or f"{len(lookups)} places as expected")

with Site(-3233, -1185) as s:
    reply = c("gscraft director pass -3233 -1185 20")
    check("nothing placed inside KROT", placed(reply) == 0 and count(f"@e[tag=gs_director,{s.area()}]") == 0, reply)

with Site(-2380, -2975) as s:
    reply = c("gscraft director pass -2380 -2975 30")
    ruaf = count(f"@e[type=gscraft:ruaf_soldier,tag=gs_director,{s.area()}]")
    dead = count(f"@e[type=minecraft:zombie,{s.area()}]") + count(f"@e[type=minecraft:husk,{s.area()}]")
    nato = count(f"@e[type=gscraft:nato_soldier,{s.area()}]")
    check("the town draws RUAF and the Dead, never NATO", ruaf > 0 and dead > 0 and nato == 0,
          f"{reply}; RUAF {ruaf}, Dead {dead}, NATO {nato}")

with Site(-800, -1290) as s:
    reply = c("gscraft director pass -800 -1290 20")
    infected = count(f'@e[name="The Infected",{s.area()}]')
    soldiers = count(f"@e[type=gscraft:nato_soldier,{s.area()}]") + count(f"@e[type=gscraft:ruaf_soldier,{s.area()}]")
    check("the hospital's Dead are The Infected, and no soldiers", infected > 0 and soldiers == 0,
          f"{reply}; The Infected {infected}, soldiers {soldiers}")

with Site(-642, 518) as s:
    reply = c("gscraft director pass -642 518 20")
    workers = count(f'@e[name="Plant Worker",{s.area()}]') + count(f'@e[name="Containment Crew",{s.area()}]')
    check("the reactor hall's Dead are Plant Workers and Containment Crew", workers > 0, f"{reply}; dressed {workers}")

with Site(-2000, -600) as s:
    torch_at = "execute positioned -2000 0 -600 positioned over motion_blocking_no_leaves run "
    c(torch_at + "setblock ~ ~ ~ magnumtorch:diamond_magnum_torch")
    time.sleep(2)
    reply = c("gscraft director pass -2000 -600 20")
    # the torch reaches 64 blocks; placement now reaches 72, so only the Dead inside the torch's radius count
    near = "x=-2000,y=64,z=-600,distance=..64"
    hostile = count(f"@e[type=minecraft:zombie,{near}]") + count(f"@e[type=minecraft:husk,{near}]")
    check("a diamond Magnum Torch stops the director's Dead", hostile == 0, f"{reply}; Dead placed inside its 64 blocks: {hostile}")
    c(torch_at + "execute if block ~ ~-1 ~ magnumtorch:diamond_magnum_torch run setblock ~ ~-1 ~ air")
    c(torch_at + "execute if block ~ ~ ~ magnumtorch:diamond_magnum_torch run setblock ~ ~ ~ air")
    time.sleep(2)
    s.clear()
    reply = c("gscraft director pass -2000 -600 20")
    check("placement resumes once the torch is gone", placed(reply) > 0, reply)

with Site(-840, -540) as s:
    tag = "gs_garrison_out_e1"
    first = c("gscraft garrison out_e1 force")
    time.sleep(2)
    n1 = count(f"@e[tag={tag}]")
    persistent = c(f"data get entity @e[tag={tag},limit=1] PersistenceRequired")
    home = c(f"data get entity @e[tag={tag},limit=1] GscraftHomeRadius")
    again = c("gscraft garrison out_e1 force")
    n2 = count(f"@e[tag={tag}]")
    check("a garrison fills to strength, persistent and posted",
          n1 == 4 and n2 == 4 and persistent.endswith("1b") and "has the following" in home,
          f"{first}; then {again}; members {n1} -> {n2}; persistent {persistent[-3:]}; home {home[-4:]}")
    c(f"kill @e[tag={tag},limit=2]")
    time.sleep(1)
    refill = c("gscraft garrison out_e1 force")
    n3 = count(f"@e[tag={tag}]")
    check("the garrison tops back up after losses", n3 == 4, f"{refill}; members {n3}")
    c(f"kill @e[tag={tag}]")

day = re.search(r"(\d+)\s*$", c("time query daytime"))
with Site(-2000, -600) as s:
    c("time set 18000")
    time.sleep(1)
    first = c("gscraft director horrors -2000 66 -600")
    second = c("gscraft director horrors -2000 66 -600")
    men = count(f"@e[type=man:manfromthefog,{s.area()}]")
    check("the fog man is admitted to the Woods at night, once", men == 1, f"{first}; {second}; fog men {men}")
    c(f"kill @e[type=man:manfromthefog,{s.area()}]")
    if day:
        c(f"time set {day.group(1)}")

def mean_tick():
    m = re.search(r"overworld\)?: Mean tick time: ([\d.]+) ms", c("forge tps minecraft:overworld"))
    return float(m.group(1)) if m else None


def sampled(seconds=20):
    vals = []
    for _ in range(seconds // 5):
        time.sleep(5)
        v = mean_tick()
        if v is not None:
            vals.append(v)
    return sum(vals) / len(vals) if vals else None


# the review's budget (section 8): what a live fight costs the tick, measured on a ticking world
with Site(-2380, -2975, radius=80) as s:
    base = sampled(15)
    c("gscraft director pass -2380 -2975 40")
    time.sleep(3)
    fighting = count(f"@e[tag=gs_director,{s.area()}]")
    load = sampled(20)
    shots = None
    check("a 40-strong fight keeps the tick under 50 ms (20 TPS)", load is not None and load < 50.0,
          f"mean tick {base and round(base, 2)} ms empty -> {load and round(load, 2)} ms with {fighting} placed "
          f"({load and base and round((load - base) / max(fighting, 1), 3)} ms each)")

print("  info ", c("gscraft director stats"))
r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if "gscraft" in l.lower()
       and re.search(r"ERROR|invalid|not registered|not a loaded|unknown entity|Exception", l)]
check("no gscraft errors in the log", not bad, f"{len(bad)} lines")
for l in bad[:8]:
    print("     ", l[:180])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
