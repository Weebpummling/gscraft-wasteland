"""Set the world border in level.dat so it contains the built cell.

The v8 world inherited Pripyat's border (centre 1900.5, 1250.5, size 10000), whose west edge falls at x -3099.5 and whose
north edge falls at z -3749.5. That is the invisible wall the owner walked into near (-3100, 583); it also left the
Financial Plaza, farmsteads 14 and 26 wholly outside the playable area and cut the desert-city hub, the hempcrete
compound, the library, the runway and farmstead 19.

usage: worldborder.py <world dir> [--centre X Z] [--size N] [--show]
Defaults cover the v8 cell (x -3900..1200, z -3900..700) with a 50-block margin: centre (-1350, -1600), size 5200.
A backup of level.dat is written next to it once, as level.dat.border.bak.
"""
import sys, gzip, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import R, W as NbtW

CENTRE = (-1350.5, -1600.5)
SIZE = 5200.0


def show(data):
    c = (data["BorderCenterX"][1], data["BorderCenterZ"][1]); s = data["BorderSize"][1]
    print(f"  centre ({c[0]}, {c[1]})  size {s}")
    print(f"  x {c[0]-s/2:.1f} .. {c[0]+s/2:.1f}   z {c[1]-s/2:.1f} .. {c[1]+s/2:.1f}")


def main(a):
    if len(a) < 2: sys.exit(__doc__)
    world = Path(a[1]); p = world / "level.dat"
    name, root = R(gzip.open(p, "rb").read()).root()
    data = root["Data"][1]
    print("world border before:"); show(data)
    if "--show" in a: return
    cx, cz = CENTRE; size = SIZE
    if "--centre" in a: i = a.index("--centre"); cx, cz = float(a[i + 1]), float(a[i + 2])
    if "--size" in a: size = float(a[a.index("--size") + 1])
    bak = world / "level.dat.border.bak"
    if not bak.exists(): shutil.copy2(p, bak); print(f"  backup -> {bak.name}")
    t = data["BorderCenterX"][0]
    data["BorderCenterX"] = (t, cx); data["BorderCenterZ"] = (t, cz)
    for k in ("BorderSize", "BorderSizeLerpTarget"): data[k] = (data[k][0], size)
    data["BorderSizeLerpTime"] = (data["BorderSizeLerpTime"][0], 0)
    gzip.open(p, "wb").write(NbtW().root(name, root))
    print("world border after:"); show(data)


if __name__ == "__main__":
    main(sys.argv)
