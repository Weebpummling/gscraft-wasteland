"""Put a rectangle of open land back on the relief plan (undo a mis-carved feature): every column that is not built and not
in a protect mask, whose ground is off the plan height by more than `tol`, is set to the plan height with dirt below and grass
on top (water and trees above it removed). usage: regrade.py <world> x0 z0 x1 z1 [--tol 1] [--protect mask.npz] [--dry-run]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from terrain import World, column_is_built
from river import Land, column_op, Protect

def main(a):
    world = World(Path(a[1])); x0, z0, x1, z1 = map(int, a[2:6]); tol = int(a[a.index("--tol") + 1]) if "--tol" in a else 1
    protect = Protect(a[a.index("--protect") + 1] if "--protect" in a else None); dry = "--dry-run" in a; land = Land(); n = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            nat = land.at(x, z); g = world.ground(x, z)
            if nat is None or g is None or abs(g - nat) <= tol or protect(x, z) or column_is_built(world, x, z): continue
            n += column_op(world, x, z, nat, "minecraft:grass_block", None)
    files, chunks = world.save(dry)
    print(f"regrade: {n} columns back on the plan, {chunks} chunks{' (dry)' if dry else ''}")

if __name__ == "__main__":
    main(sys.argv)
