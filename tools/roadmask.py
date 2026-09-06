"""The road protect mask: every carriageway laid by roads.py / roadpatch.py, plus the bridge decks.

Written because the terrain passes of v8 ran after the roads and wiped 4% of them (v8 road review, finding 2.2):
`smoothcliffs.py` guessed roads from the surface-name array, and `river.py`, `shoreline.py` and `lakefill.py` had no
road mask at all. `roads.py build` now writes `road_<name>_mask.npz` next to `bridge.py`'s `bridge_<name>_mask.npz`,
and every terrain tool takes `--protect-roads [dilate]` to load all of them.

    from roadmask import RoadMask
    keep = RoadMask.from_args(sys.argv)      # None when --protect-roads is absent
    if keep and keep(x, z): continue         # or: array = keep.array(shape, X0, Z0)
"""
import sys
from pathlib import Path
import numpy as np
from scipy import ndimage

CENSUS = Path(r"G:/GSCraft/incoming/census")
X0, Z0 = -3900, -3900


class RoadMask:
    """Union of every road_*_mask.npz and bridge_*_mask.npz, on the census grid."""

    def __init__(self, dilate=2, patterns=("road_*_mask.npz", "bridge_*_mask.npz"), shape=(4601, 5101)):
        self.m = np.zeros(shape, bool); self.n = 0
        for pat in patterns:
            for f in sorted(CENSUS.glob(pat)):
                d = np.load(f); mk = d["mask"]; ox, oz = map(int, d["origin"])
                i0, j0 = oz - Z0, ox - X0
                i1, j1 = i0 + mk.shape[0], j0 + mk.shape[1]
                si0, sj0 = max(i0, 0), max(j0, 0); si1, sj1 = min(i1, shape[0]), min(j1, shape[1])
                if si0 >= si1 or sj0 >= sj1: continue
                self.m[si0:si1, sj0:sj1] |= mk[si0 - i0:si1 - i0, sj0 - j0:sj1 - j0]
                self.n += 1
        if dilate: self.m = ndimage.binary_dilation(self.m, iterations=int(dilate))
        self.dilate = dilate

    def __call__(self, x, z):
        i, j = z - Z0, x - X0
        return 0 <= i < self.m.shape[0] and 0 <= j < self.m.shape[1] and bool(self.m[i, j])

    def array(self):
        return self.m

    @staticmethod
    def from_args(argv):
        if "--protect-roads" not in argv: return None
        i = argv.index("--protect-roads")
        d = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 2
        r = RoadMask(d)
        print(f"  road protect mask: {r.n} masks, {int(r.m.sum()):,} columns (dilated {d})")
        return r


def masks_from_routes(files, names=None):
    """Back-fill road_<name>_mask.npz for roads that were built before roads.py wrote masks, from their polylines."""
    import json
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from roads import densify
    made = 0
    for f in files:
        for r in json.load(open(f)):
            if not r.get("polyline") or (names and r["name"] not in names): continue
            half = max(r.get("width", 7) // 2, 2) + 1
            pts = densify(r["polyline"])
            xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
            ox, oz = min(xs) - half - 2, min(zs) - half - 2
            m = np.zeros((max(zs) - oz + half + 3, max(xs) - ox + half + 3), bool)
            for (x, z) in pts: m[z - oz - half:z - oz + half + 1, x - ox - half:x - ox + half + 1] = True
            np.savez_compressed(CENSUS / f"road_{r['name']}_mask.npz", mask=m, origin=np.array([ox, oz]))
            made += 1
    return made


if __name__ == "__main__":
    if "--from-routes" in sys.argv:
        i = sys.argv.index("--from-routes")
        only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
        files = [x for x in sys.argv[i + 1:] if not x.startswith("--") and x not in (only or ())]
        print(f"{masks_from_routes(files, only)} masks written from {len(files)} route files")
    r = RoadMask(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2)
    print(f"{r.n} masks, {int(r.m.sum()):,} protected columns")
