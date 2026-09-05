"""Remove a road laid by roads.py and put the land back (v8 fix-ups: a connector routed to the wrong target).

usage: unroad.py <world dir> <routes.json> <road name> [--reach 12] [--dry-run]
Every column within `reach` of the route's polyline whose surface is a road/kerb/fill material (or anything non-natural
standing on the old shoulders) is brought back to the relief plan height with dirt below and grass on top; water and
buildings not laid by the road are left alone. Uses river.Land for the natural height.
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, NATURAL, PLANT, LIQUID, AIR
from roads import densify
from river import Land, column_op
from stubs import is_road

ROADISH = {"minecraft:terracotta", "minecraft:gray_concrete", "minecraft:black_concrete", "minecraft:andesite_wall", "minecraft:stone_brick_wall",
           "minecraft:cobblestone_wall", "minecraft:polished_andesite", "minecraft:stone", "minecraft:andesite", "minecraft:gravel"}


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    world = World(Path(a[1])); routes = json.load(open(a[2])); name = a[3]; dry = "--dry-run" in a
    reach = int(a[a.index("--reach") + 1]) if "--reach" in a else 12
    r = next(x for x in routes if x["name"] == name)
    pts = np.array(densify([tuple(p) for p in r["polyline"]]), np.float64); tree = cKDTree(pts); land = Land()
    x0, z0 = int(pts[:, 0].min() - reach), int(pts[:, 1].min() - reach); x1, z1 = int(pts[:, 0].max() + reach), int(pts[:, 1].max() + reach)
    changed = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            d, _ = tree.query((x, z))
            if d > reach: continue
            ty, tb = world.top(x, z)
            if tb is None or tb in LIQUID: continue
            nat = land.at(x, z)
            if nat is None: continue
            # strip the road: everything non-natural or road-ish from the top down to the natural height
            y = ty
            while y > nat and (world.get(x, y, z) in ROADISH or is_road(world.get(x, y, z)) or world.get(x, y, z) not in NATURAL):
                y -= 1
            g = world.ground(x, z)
            if g is None: continue
            if y != ty or g != nat or world.get(x, nat, z) != "minecraft:grass_block":
                world.clear_column(x, z, min(nat, g, y) + 1)
                changed += column_op(world, x, z, nat, "minecraft:grass_block", None)
    files, chunks = world.save(dry)
    print(f"unroad {name}: {changed} columns restored to the relief plan, {chunks} chunks{' (dry)' if dry else ''}")


if __name__ == "__main__":
    main(sys.argv)
