#!/usr/bin/env python3
"""The Act I chests bound to their building's loot table (system doc 2026-09-13 §7 build 4; loot doc §3, §8: bound by
LootTable NBT at world build, the LootEvents hook deferred).

    python chests.py <world dir>            -> tools/chests.json: every container in the compound and the square, with the
                                               table its rectangle gives it, and the console command that binds it
    python chests.py <world dir> --apply    -> also runs the commands on the local server over RCON (forceloaded; the
                                               container becomes a Lootr chest with the table, per player, unchanged blocks
                                               otherwise)
    python chests.py <world dir> --place    -> the buildings held almost no containers (eight in the compound and the square
                                               together, 2026-09-13), so this also PLACES Lootr chests on interior floor
                                               spots: a solid floor, two air above, a roof somewhere over it, against a wall
                                               where it can, spaced four apart, up to PLACE[table] per rectangle

The rectangles are the compound doc's (§2) and the square's site box: the hall is apartments, the brick block a garage,
the west sheds a workshop, the annex an office; the square's buildings alternate office and apartment by column. First
cut for the visual pass, like every other rectangle. The clinic (hospital) comes with the north complex, later.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import R, read_region_raw  # noqa: E402
from camp_ruins import region_of, slot_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONTAINERS = {"minecraft:chest", "minecraft:trapped_chest", "minecraft:barrel", "lootr:lootr_chest", "lootr:lootr_barrel", "lootr:lootr_trapped_chest"}
# (x0, x1, z0, z1) -> table, first match wins
RECTS = [
    ((-979, -937, -858, -834), "apartment"),   # the hall
    ((-938, -924, -869, -831), "garage"),      # the brick block
    ((-973, -958, -895, -858), "workshop"),    # the west sheds
    ((-960, -937, -834, -820), "office"),      # the annex
    ((-980, -920, -897, -818), "apartment"),   # the rest of the compound
]
SQUARE = (-966, -914, -1000, -958)
BOXES = [(-980, -920, -897, -818), SQUARE]
# chests placed per rectangle when --place (the hall, the block, the sheds, the annex; the square's buildings share one budget)
PLACE = {"hall": 8, "block": 6, "sheds": 4, "annex": 4, "square": 14}
NAMED = {"hall": ((-979, -937, -858, -834), "apartment"), "block": ((-938, -924, -869, -831), "garage"), "sheds": ((-973, -958, -895, -858), "workshop"),
         "annex": ((-960, -937, -834, -820), "office"), "square": (SQUARE, None)}
SOLID_SKIP = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:water", "minecraft:lava", "minecraft:grass", "minecraft:tall_grass", "minecraft:fern",
              "minecraft:dead_bush", "minecraft:snow", "minecraft:torch", "minecraft:wall_torch", "minecraft:rail"}


def unwrap(v):
    return v[1] if isinstance(v, tuple) else v


def table_for(x, z):
    for (x0, x1, z0, z1), t in RECTS:
        if x0 <= x <= x1 and z0 <= z <= z1:
            return t
    if SQUARE[0] <= x <= SQUARE[1] and SQUARE[2] <= z <= SQUARE[3]:
        return "office" if ((x + 966) // 12) % 2 == 0 else "apartment"
    return None


def scan(world):
    found = []
    chunks = set()
    for x0, x1, z0, z1 in BOXES:
        for cx in range(x0 >> 4, (x1 >> 4) + 1):
            for cz in range(z0 >> 4, (z1 >> 4) + 1):
                chunks.add((cx, cz))
    for cx, cz in sorted(chunks):
        rx, rz = region_of(cx, cz)
        raw = read_region_raw(world / "region" / f"r.{rx}.{rz}.mca").get(slot_of(cx, cz))
        if not raw:
            continue
        d = R(raw[2]).root()[1]
        be = unwrap(d.get("block_entities"))
        entries = unwrap(be) if isinstance(be, tuple) else be
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            eid = unwrap(e.get("id"))
            if eid not in CONTAINERS:
                continue
            x, y, z = unwrap(e.get("x")), unwrap(e.get("y")), unwrap(e.get("z"))
            t = table_for(x, z)
            if t is None:
                continue
            block = "lootr:lootr_barrel" if "barrel" in eid else "lootr:lootr_chest"
            found.append({"x": x, "y": y, "z": z, "was": eid, "table": t, "command": f'setblock {x} {y} {z} {block}{{LootTable:"gscraft:building/{t}"}}'})
    return found


class Blocks:
    """block names by world coordinate, cached by chunk"""
    def __init__(self, world):
        from camp_ruins import Ground
        self.g = Ground(world)

    def get(self, x, y, z):
        c = self.g.chunk(x >> 4, z >> 4)
        return c.get(x & 15, y, z & 15) if c else "minecraft:air"

    def solid(self, x, y, z):
        n = self.get(x, y, z)
        return n not in SOLID_SKIP and not n.endswith("_button") and not n.endswith("_pressure_plate") and "sign" not in n

    def air(self, x, y, z):
        return self.get(x, y, z) in ("minecraft:air", "minecraft:cave_air")


def interior_spots(b, rect, budget, taken):
    """floor cells inside the rectangle under a roof, against a wall where possible, spaced four apart"""
    x0, x1, z0, z1 = rect
    cands = []
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            for y in range(56, 100):
                if not (b.solid(x, y, z) and b.air(x, y + 1, z)):
                    continue
                roof = any(b.solid(x, yy, z) for yy in range(y + 2, y + 40))   # a two-high shed counts
                if not roof:
                    continue
                wall = sum(1 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if b.solid(x + dx, y + 1, z + dz))
                if wall >= 3:
                    continue   # a crawlspace or a column gap
                cands.append((-wall, y, x, z))
                break   # the lowest floor of the column only
    cands.sort()
    out = []
    for _, y, x, z in cands:
        if any(abs(x - ox) < 4 and abs(z - oz) < 4 for ox, _, oz in out + taken):
            continue
        out.append((x, y + 1, z))
        if len(out) >= budget:
            break
    return out


def place(world, found):
    b = Blocks(world)
    taken = [(f["x"], f["y"], f["z"]) for f in found]
    placed = []
    for name, (rect, table) in NAMED.items():
        spots = interior_spots(b, rect, PLACE[name], taken)
        for i, (x, y, z) in enumerate(spots):
            t = table or ("office" if i % 2 == 0 else "apartment")
            placed.append({"x": x, "y": y, "z": z, "was": "air (placed)", "table": t, "building": name,
                           "command": f'setblock {x} {y} {z} lootr:lootr_chest{{LootTable:"gscraft:building/{t}"}}'})
            taken.append((x, y, z))
        print(f"  {name:6} {len(spots)} of {PLACE[name]} spots")
    return placed


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    found = scan(Path(argv[1]))
    if "--place" in argv:
        found += place(Path(argv[1]), found)
    (ROOT / "tools" / "chests.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    by = {}
    for f in found:
        by[f["table"]] = by.get(f["table"], 0) + 1
    print(f"{len(found)} containers: {by}")
    if "--apply" in argv:
        import time
        import localtest as L
        r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
        r.cmd("forceload add -1000 -1010 -900 -810", timeout=30)
        time.sleep(4)
        ok = 0
        for f in found:
            out = r.cmd(f["command"], timeout=30) or ""
            ok += "Changed" in out
        r.cmd("forceload remove -1000 -1010 -900 -810", timeout=30)
        r.close()
        print(f"applied: {ok} of {len(found)} changed")


if __name__ == "__main__":
    main(sys.argv)
