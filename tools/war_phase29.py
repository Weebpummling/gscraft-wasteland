"""Phase 29, the drop tables (system doc 2026-09-13 §7 build 2; enemy review §7: materials, never products; dog tags from
NATO and RUAF, not scavengers) on the LOCAL server. Needs a ticking world and no player. A drop lands only on a kill by
a player, so the headless test rolls the tables through `/gscraft drops roll <entity> <n>`; the kill itself is the
owner's in-game check.

1. NATO and RUAF soldiers roll dog tags, ammunition and materials; never a gun.
2. Scavengers roll materials and a little ammunition; never a dog tag, never a gun.
3. The Dead roll materials only: no ender pearls, no ammunition boxes.
4. The armour drop chance is a setting (drops.armour_chance) and is low.
5. No gscraft errors.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def roll(entity, n=300):
    out = c(f"gscraft drops roll {entity} {n}")
    return {k: int(v) for k, v in re.findall(r"([a-z_:]+)=(\d+)", out)}, out


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


nato, out_n = roll("gscraft:nato_soldier")
ruaf, out_r = roll("gscraft:ruaf_soldier")
GUN = lambda k: "kinetic_gun" in k or k.startswith("tacz:") or (k.startswith("superbwarfare:") and not k.endswith(("_ammo", "dog_tag", "armor_plate")))   # a gun item, not gunpowder or handgun ammo
guns = sum(v for k, v in list(nato.items()) + list(ruaf.items()) if GUN(k))
check("NATO and RUAF soldiers roll dog tags, ammunition and materials, never a gun",
      nato.get("superbwarfare:dog_tag", 0) > 0 and ruaf.get("superbwarfare:dog_tag", 0) > 0 and nato.get("superbwarfare:rifle_ammo", 0) > 0 and guns == 0,
      f"nato tags {nato.get('superbwarfare:dog_tag', 0)}, rifle ammo {nato.get('superbwarfare:rifle_ammo', 0)}, nuggets {nato.get('minecraft:iron_nugget', 0)}; ruaf tags {ruaf.get('superbwarfare:dog_tag', 0)}; guns {guns}")

scav, out_s = roll("gscraft:scavenger")
check("scavengers roll materials and a little ammunition, never a dog tag or a gun",
      scav and scav.get("superbwarfare:dog_tag", 0) == 0 and not any(GUN(k) for k in scav) and scav.get("gscraft:metal_scrap", 0) > 0 and scav.get("minecraft:iron_nugget", 0) == 0,   # the scrap is the economy's own since 2026-09-18 (itemflow): a nugget fed nothing
      f"{dict(list(scav.items())[:6])}")

dead, out_d = roll("minecraft:zombie")
check("the Dead roll materials only: no ender pearls, no ammunition boxes",
      dead and dead.get("minecraft:ender_pearl", 0) == 0 and not any(k.endswith("_ammo_box") for k in dead) and dead.get("minecraft:rotten_flesh", 0) > 0,
      f"{dict(list(dead.items())[:6])}")

setting = c("gscraft settings drops.armour_chance")
m = re.search(r"drops.armour_chance = ([\d.]+)", setting)
check("the armour drop chance is a low setting", m is not None and 0.0 < float(m.group(1)) <= 0.1, f"[{setting[-60:]}]")

r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
