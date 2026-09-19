#!/usr/bin/env python3
"""The Act I chests bound to their building's loot table (system doc 2026-09-13 §7 build 4; loot doc §3, §8: bound by
LootTable NBT at world build, the LootEvents hook deferred).

    python chests.py <world dir>            -> tools/chests.json: every container in the compound and the square, with the
                                               table its rectangle gives it, and the console command that binds it
    python chests.py <world dir> --apply    -> also runs the commands on the local server over RCON (forceloaded; the
                                               container becomes a Lootr chest with the table, per player, unchanged blocks
                                               otherwise)
    NOTE: --place only WRITES the placements into the record; nothing reaches a server without --apply (2026-09-18: a
    run of --place alone was reported as 'chests placed' and was not).
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
    ((-786, -752, -902, -876), "workshop"),    # the big hall (the walled compound, owner 2026-09-17)
    ((-746, -730, -905, -872), "garage"),      # the brick works, east
    ((-844, -836, -911, -904), "office"),      # the shed by the north gate
    ((-792, -774, -884, -874), "apartment"),   # the annex south of the hall
    ((-900, -720, -920, -835), "apartment"),   # the rest of the compound
    ((-966, -930, -1060, -1020), "hospital"),  # the clinic, in the north complex
    ((-865, -698, -1312, -1242), "hospital"),  # the hospital strongpoint
]
SQUARE = (-966, -914, -1000, -958)
CLINIC = (-966, -930, -1060, -1020)   # the north complex's clinic (camp.py's Tony rectangle), x0, x1, z0, z1
HOSPITAL = (-865, -698, -1312, -1242)   # the strongpoint's own box (gscraft_sites/hospital.json): it held no container at all (slice review 2026-09-19)
ROAD_A = (-870, -760, -1140, -1045)   # the way north, its southern half: the streets between the mast's field and the hospital held no container (slice review 2026-09-19)
ROAD_B = (-870, -760, -1241, -1141)   # and its northern half, up to the hospital's box
BOXES = [(-900, -720, -920, -835), SQUARE, CLINIC, HOSPITAL, ROAD_A, ROAD_B]
# chests placed per rectangle when --place (the hall, the block, the sheds, the annex; the square's buildings share one budget)
PLACE = {"hall": 8, "block": 6, "sheds": 4, "annex": 4, "square": 14, "clinic": 0, "hospital": 20, "road_a": 10, "road_b": 10}   # the clinic already holds 31 barrels of its own: none placed (2026-09-18)
NAMED = {"hall": ((-786, -752, -902, -876), "workshop"), "block": ((-746, -730, -905, -872), "garage"), "sheds": ((-844, -836, -911, -904), "office"),
         "annex": ((-792, -774, -884, -874), "apartment"), "square": (SQUARE, None),
         "clinic": (CLINIC, "hospital"), "hospital": (HOSPITAL, "hospital"), "road_a": (ROAD_A, None), "road_b": (ROAD_B, None)}   # T2's med kits need the hospital table (itemflow, 2026-09-18)
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
    for rx0, rx1, rz0, rz1 in (ROAD_A, ROAD_B):
        if rx0 <= x <= rx1 and rz0 <= z <= rz1:
            return "office" if ((x + 870) // 12) % 2 == 0 else "apartment"
    return None


def scan(world):
    found = []
    chunks = set()
    for x0, x1, z0, z1 in BOXES:
        for cx in range(x0 >> 4, (x1 >> 4) + 1):
            for cz in range(z0 >> 4, (z1 >> 4) + 1):
                chunks.add((cx, cz))
    blocks, skipped = None, []
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
            if eid.startswith("minecraft:"):
                # a container of the map's own, not yet bound. Two are left alone (2026-09-19, the hospital and the road north:
                # the map's barrels there are FURNITURE - a table under a flower pot, a cabinet under a trapdoor):
                # one that HOLDS something is somebody's (two hold a written book; binding is a setblock and would destroy it),
                # and one no hand can reach (no air beside it or above it) would be a search that cannot be made.
                items = unwrap(e.get("Items"))
                items = unwrap(items) if isinstance(items, tuple) else items
                if items:
                    skipped.append((x, y, z, "holds items"))
                    continue
                blocks = blocks or Blocks(world)
                if not any(blocks.air(x + dx, y + dy, z + dz) for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0))):
                    skipped.append((x, y, z, "out of reach"))
                    continue
            # the container's OWN table is the truth when it is one of ours: recomputing it from the position disagreed with
            # what place() had assigned (by order, not by x) and would have dropped the road's chests from the record (2026-09-19)
            own = unwrap(e.get("LootTable"))
            t = own.split("gscraft:building/", 1)[1] if isinstance(own, str) and own.startswith("gscraft:building/") else table_for(x, z)
            if t is None:
                continue
            block = "lootr:lootr_barrel" if "barrel" in eid else "lootr:lootr_chest"
            found.append({"x": x, "y": y, "z": z, "was": eid, "table": t, "command": f'setblock {x} {y} {z} {block}{{LootTable:"gscraft:building/{t}"}}'})
    if skipped:
        why = {}
        for *_, w in skipped:
            why[w] = why.get(w, 0) + 1
        print(f"  the map's own containers left alone: {why}")
    return found


class Blocks:
    """block names by world coordinate, cached by chunk"""
    def __init__(self, world):
        from camp_ruins import Ground
        self.g = Ground(world)
        self.tops = {}

    def get(self, x, y, z):
        c = self.g.chunk(x >> 4, z >> 4)
        return c.get(x & 15, y, z & 15) if c else "minecraft:air"

    def solid(self, x, y, z):
        n = self.get(x, y, z)
        return n not in SOLID_SKIP and not n.endswith("_button") and not n.endswith("_pressure_plate") and "sign" not in n

    def air(self, x, y, z):
        return self.get(x, y, z) in ("minecraft:air", "minecraft:cave_air")

    def top(self, x, z):
        """the highest laid or natural block of a column that is not a tree"""
        k = (x, z)
        if k not in self.tops:
            self.tops[k] = next((y for y in range(130, 30, -1) if self.solid(x, y, z) and "leaves" not in self.get(x, y, z) and "_log" not in self.get(x, y, z)), 30)
        return self.tops[k]

    def above_ground(self, x, y, z):
        """a floor at or over street level: within ten blocks some column's surface is no higher than this floor's"""
        return any(self.top(x + dx, z + dz) <= y + 1 for dx in range(-10, 11, 2) for dz in range(-10, 11, 2))


NATURAL = ("grass_block", "dirt", "podzol", "mud", "sand", "gravel", "stone", "andesite", "diorite", "granite", "deepslate", "tuff", "clay", "moss_block",
           "leaves", "_log", "_wood", "mushroom", "bone_block", "snow_block", "ice")


ODD = ("_stairs", "cauldron", "composter", "chain", "iron_bars", "_fence", "_wall", "_trapdoor", "lantern", "_carpet", "_bed")   # no floor for a chest, no roof either


FLOORS = ("planks", "brick", "concrete", "terracotta", "_slab", "polished_", "smooth_", "cobble", "tiles", "quartz")   # what a room's floor is laid in; a vine, a fern and a beehive all passed for 'solid'


def built(name):
    """a block somebody laid: not the ground, not a tree. `stone` must not catch stone_bricks"""
    n = name.split(":", 1)[1]
    return not any(n == k or n.endswith(k) or (k in ("leaves", "_log", "_wood", "mushroom") and k in n) for k in NATURAL)


def interior_spots(b, rect, budget, taken):
    """floor cells inside the rectangle under a roof, against a wall where possible, spaced four apart.
    2026-09-19, the hospital and the road north: the first cut took the LOWEST floor of a column under ANY solid block, which
    north of the wall meant the crawlspace under a raised building, the grass under a spruce and a bone block's shadow. A spot
    is now a laid floor (not ground, not a tree) with two of air over it and a laid roof within ten, at any storey."""
    x0, x1, z0, z1 = rect
    cands = []
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            for y in range(45, 100):
                if not (any(k in b.get(x, y, z) for k in FLOORS) and not b.get(x, y, z).endswith(ODD) and b.air(x, y + 1, z) and b.air(x, y + 2, z)):
                    continue
                roof = next((yy for yy in range(y + 3, y + 11) if b.solid(x, yy, z)), None)
                if roof is None or not built(b.get(x, roof, z)) or b.get(x, roof, z).endswith(ODD):
                    continue
                wall = sum(1 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if b.solid(x + dx, y + 1, z + dz))
                if wall >= 3:
                    continue   # a crawlspace or a column gap
                cands.append((-wall, y, x, z))
    cands.sort()
    out = []
    for _, y, x, z in cands:
        if any(abs(x - ox) < 4 and abs(z - oz) < 4 for ox, _, oz in out + taken):
            continue
        if not b.above_ground(x, y, z):
            continue   # a cellar or a sewer: the second cut put fifteen of twenty-two down there
        out.append((x, y + 1, z))
        if len(out) >= budget:
            break
    return out


def place(world, found):
    b = Blocks(world)
    taken = [(f["x"], f["y"], f["z"]) for f in found]
    placed = []
    for name, (rect, table) in NAMED.items():
        # only the SHORTFALL is placed: a chest applied on an earlier run is on disk now and comes back from the scan, so placing
        # the full budget again would double every building (2026-09-19). The square's budget counts its whole box.
        x0, x1, z0, z1 = rect
        standing = sum(1 for f in found if x0 <= f["x"] <= x1 and z0 <= f["z"] <= z1 and "lootr" in f.get("command", ""))
        need = max(0, PLACE[name] - standing)
        spots = interior_spots(b, rect, need, taken)[:need] if need > 0 else []   # the finder adds a spot before it checks its budget: 0 meant 1 (2026-09-18)
        for i, (x, y, z) in enumerate(spots):
            t = table or ("office" if i % 2 == 0 else "apartment")
            placed.append({"x": x, "y": y, "z": z, "was": "air (placed)", "table": t, "building": name,
                           "command": f'setblock {x} {y} {z} lootr:lootr_chest{{LootTable:"gscraft:building/{t}"}}'})
            taken.append((x, y, z))
        print(f"  {name:12} {standing} standing, {len(spots)} new of a budget of {PLACE[name]}")
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
        # every box the record covers, not a fixed rectangle: the old one was the south compound's and missed the walled
        # compound and the clinic after the move (found 2026-09-18). One forceload per box keeps each under the 256-chunk cap.
        for x0, x1, z0, z1 in BOXES:
            r.cmd(f"forceload add {x0 - 2} {z0 - 2} {x1 + 2} {z1 + 2}", timeout=30)
        time.sleep(4)
        ok = 0
        for f in found:
            out = r.cmd(f["command"], timeout=30) or ""
            ok += "Changed" in out
        for x0, x1, z0, z1 in BOXES:
            r.cmd(f"forceload remove {x0 - 2} {z0 - 2} {x1 + 2} {z1 + 2}", timeout=30)
        r.close()
        print(f"applied: {ok} of {len(found)} changed")


if __name__ == "__main__":
    main(sys.argv)
