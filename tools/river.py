"""Carve a natural-looking river along a planned line (v8: connect the lake to the Skadowsky sector's river).

usage: river.py build  <world dir> <rivers.json> [--dry-run]
       river.py mouths <world dir> x0 z0 x1 z1            list water columns on the edges of a footprint (river mouths)

rivers.json: a list of jobs. A river job:
  {"name": "...", "points": [[x, z], ...],            the planned line; t runs 0..1 from the first point to the last
   "width": [16, 26],                                  channel width varies along the river between these
   "levels": [[0.0, 53], [0.08, 54], [0.16, 55], [0.26, 56], [0.38, 57]],   water surface from that t on; each step is a 1-block rapid
   "depth": 3,                                         bed under the surface (deeper where wider)
   "meander": {"amp": 18, "wavelength": 220, "amp2": 7, "wavelength2": 90, "seed": 3},
   "bank_slope": [2.5, 4.5],                           blocks of bank per block of rise, varies per side along the river
   "restore": [[x, z], ...], "restore_reach": 52,      an earlier channel's line: its corridor goes back to the natural land
   "protect": "integrate_skad_mask.npz",               columns kept by integrate.py are never touched
   "lake_rect": [x0, z0, x1, z1]}                      existing water inside this box is left alone
A shore job grades a bank down to an existing water body from a straight edge:
  {"shore": "...", "rect": [x0, z0, x1, z1], "water": "E", "level": 53, "width": 36}
The natural land height is the relief plan (census ground + heightplan), so the corridor's grading returns the land to the
designed relief instead of a flat level. Banks follow a smoothstep profile (concave at the water, convex at the top) with
low-frequency noise; the first two blocks from the water are sand/gravel beach; built columns are never touched; trees on
columns whose height changes are removed, the others stay.
"""
import sys, json, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, column_is_built, AIR, LIQUID, PLANT
from roads import densify

CENSUS = Path(r"G:/GSCraft/incoming/census"); CX0, CZ0 = -3900, -3900


def smoothstep(s):
    s = np.clip(s, 0, 1); return s * s * (3 - 2 * s)


def value_noise(shape, cell, amp, seed):
    rng = np.random.default_rng(seed)
    g = rng.uniform(-1, 1, (shape[0] // cell + 3, shape[1] // cell + 3))
    return ndimage.zoom(g, cell, order=3)[:shape[0], :shape[1]] * amp


class Land:
    """Natural land height per column: the relief design (heightplan) where the census saw open land, else the census ground."""
    def __init__(self):
        cls = np.load(CENSUS / "classes.npy"); gnd = np.load(CENSUS / "ground_y.npy").astype(np.int32); tgt = np.load(CENSUS / "heightplan" / "height.npy").astype(np.int32)
        self.h = np.where(np.isin(cls, (1, 2, 3, 4, 7)), gnd, tgt)
    def at(self, x, z):
        i, j = z - CZ0, x - CX0
        if 0 <= i < self.h.shape[0] and 0 <= j < self.h.shape[1]: return int(self.h[i, j])
        return None


class Protect:
    def __init__(self, spec):
        self.m = None
        if spec:
            d = np.load(CENSUS / spec); self.m = d["mask"]; self.ox, self.oz = map(int, d["origin"])
    def __call__(self, x, z):
        if self.m is None: return False
        i, j = z - self.oz, x - self.ox
        return 0 <= i < self.m.shape[0] and 0 <= j < self.m.shape[1] and bool(self.m[i, j])


def centerline(points, meander):
    pts = np.array(densify([tuple(p) for p in points]), np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
    # smoothed tangents
    k = 12; tan = np.zeros_like(pts)
    for i in range(len(pts)):
        a, b = max(i - k, 0), min(i + k, len(pts) - 1); d = pts[b] - pts[a]; n = np.hypot(*d) or 1; tan[i] = d / n
    nor = np.stack([-tan[:, 1], tan[:, 0]], 1)
    if meander:
        rng = np.random.default_rng(meander.get("seed", 3)); p1, p2 = rng.uniform(0, 2 * math.pi, 2)
        off = meander.get("amp", 18) * np.sin(2 * math.pi * s / meander.get("wavelength", 220) + p1) + meander.get("amp2", 7) * np.sin(2 * math.pi * s / meander.get("wavelength2", 90) + p2)
        off *= smoothstep(np.minimum(s, L - s) / 80.0)               # the ends stay where they were planned
        pts = pts + nor * off[:, None]
    return pts, s / max(L, 1), tan


def level_at(levels, t):
    lv = levels[0][1]
    for tt, l in levels:
        if t >= tt: lv = l
    return lv


def column_op(world, x, z, want, top_block, dry_count):
    """Bring the column's ground to `want` with dirt below and `top_block` on top; clears water, plants and trees above."""
    g = world.ground(x, z)
    if g is None: return 0
    top, _ = world.top(x, z)
    if want == g:
        if world.get(x, g, z) != top_block: world.set(x, g, z, top_block)
        yy = g + 1
        while top is not None and yy <= top + 1 and world.get(x, yy, z) in LIQUID:      # standing water on land goes
            world.set(x, yy, z, "minecraft:air"); yy += 1
        return 1
    world.clear_column(x, z, min(g, want) + 1)
    if want > g:
        for yy in range(g + 1, want): world.set(x, yy, z, "minecraft:dirt")
        world.set(x, want, z, top_block)
    else:
        world.set(x, want, z, top_block)
        for yy in range(want - 2, want):
            if world.get(x, yy, z) not in AIR: world.set(x, yy, z, "minecraft:dirt")
    return 1


def carve(world, job, land, dry):
    pts, tt, tan = centerline(job["points"], job.get("meander"))
    wmin, wmax = job.get("width", [16, 26]); levels = job.get("levels", [[0, job.get("level", 63)]]); depth0 = job.get("depth", 3)
    smin, smax = job.get("bank_slope", [2.5, 4.5]); protect = Protect(job.get("protect")); lake = job.get("lake_rect")
    rng = np.random.default_rng(job.get("meander", {}).get("seed", 3) + 11)
    n = len(pts)
    width = wmin + (wmax - wmin) * (0.5 + 0.5 * np.sin(2 * math.pi * tt * n / 140.0 + rng.uniform(0, 6)))       # ~140-block rhythm
    slope_l = smin + (smax - smin) * (0.5 + 0.5 * np.sin(2 * math.pi * tt * n / 260.0 + rng.uniform(0, 6)))
    slope_r = smin + (smax - smin) * (0.5 + 0.5 * np.sin(2 * math.pi * tt * n / 310.0 + rng.uniform(0, 6)))
    lev = np.array([level_at(levels, t) for t in tt])
    tree = cKDTree(pts)
    # corridor bounding box: the new line's reach plus the old line's restore corridor
    reach = wmax / 2 + 20 * smax + 6
    x0, z0 = int(pts[:, 0].min() - reach), int(pts[:, 1].min() - reach); x1, z1 = int(pts[:, 0].max() + reach), int(pts[:, 1].max() + reach)
    old = None
    if job.get("restore"):
        old = np.array(densify([tuple(p) for p in job["restore"]]), np.float64); oreach = job.get("restore_reach", 52); otree = cKDTree(old)
        x0, z0 = min(x0, int(old[:, 0].min() - oreach)), min(z0, int(old[:, 1].min() - oreach)); x1, z1 = max(x1, int(old[:, 0].max() + oreach)), max(z1, int(old[:, 1].max() + oreach))
    H, W = z1 - z0 + 1, x1 - x0 + 1
    noise = value_noise((H, W), 18, 1.2, job.get("meander", {}).get("seed", 3) + 5) + value_noise((H, W), 6, 0.4, 17)
    xs, zs = np.meshgrid(np.arange(x0, x1 + 1), np.arange(z0, z1 + 1))
    d, idx = tree.query(np.stack([xs.ravel(), zs.ravel()], 1)); d = d.reshape(H, W); idx = idx.reshape(H, W)
    dold = otree.query(np.stack([xs.ravel(), zs.ravel()], 1))[0].reshape(H, W) if old is not None else np.full((H, W), 1e9)
    # side of the line: sign of the cross product with the tangent at the nearest sample
    rel = np.stack([xs - pts[idx, 0], zs - pts[idx, 1]], -1); side = np.sign(tan[idx, 0] * rel[..., 1] - tan[idx, 1] * rel[..., 0])
    stats = dict(channel=0, bank=0, restored=0, skipped=0)
    for iz in range(H):
        for ix in range(W):
            x, z = x0 + ix, z0 + iz; i = idx[iz, ix]; dist = d[iz, ix]
            half = width[i] / 2.0; level = int(lev[i]); slope = slope_l[i] if side[iz, ix] >= 0 else slope_r[i]
            nat = land.at(x, z)
            if nat is None: continue
            nat = max(nat, level + 1)
            bank_w = (nat - level) * slope
            in_new = dist <= half + bank_w + 1
            in_old = dold[iz, ix] <= (job.get("restore_reach", 52) if old is not None else -1)
            if not (in_new or in_old): continue
            mouth = dist <= half and tt[i] < job.get("mouth_t", 0.0)                   # the channel may cut through protected terrain at its mouth
            if (protect(x, z) and not mouth) or column_is_built(world, x, z): stats["skipped"] += 1; continue
            if lake and lake[0] <= x <= lake[2] and lake[1] <= z <= lake[3]:
                ty, tb = world.top(x, z)
                if tb in LIQUID and dist > half: stats["skipped"] += 1; continue
            g = world.ground(x, z)
            if g is None: continue
            if dist <= half:                                                          # channel
                depth = depth0 + (1 if half > (wmin + wmax) / 4 else 0)
                bed = level - depth
                world.clear_column(x, z, bed + 1)
                if g < bed:
                    for yy in range(g + 1, bed + 1): world.set(x, yy, z, "minecraft:dirt")
                world.set(x, bed, z, "minecraft:gravel" if (x * 7 + z * 13) % 5 else "minecraft:sand")
                for yy in range(bed + 1, level + 1): world.set(x, yy, z, "minecraft:water")
                stats["channel"] += 1
            elif dist <= half + bank_w:                                                # bank
                u = (dist - half) / max(bank_w, 1)
                want = level + (nat - level) * float(smoothstep(u)) + (noise[iz, ix] if 0.12 < u < 0.88 else 0)
                want = int(round(min(max(want, level + 1), nat)))
                beach = dist <= half + 2 or want <= level + 1
                top = ("minecraft:sand" if (x * 3 + z * 5) % 4 else "minecraft:gravel") if beach else "minecraft:grass_block"
                stats["bank"] += column_op(world, x, z, want, top, None)
            else:                                                                     # old corridor: back to the natural land
                if in_old and g != nat: stats["restored"] += column_op(world, x, z, nat, "minecraft:grass_block", None)
                elif in_old:
                    ty, tb = world.top(x, z)
                    if tb in LIQUID: column_op(world, x, z, nat, "minecraft:grass_block", None); stats["restored"] += 1
    files, chunks = world.save(dry)
    print(f"river {job['name']}: {n} m, width {wmin}-{wmax}, levels {[l for _, l in levels]}: {stats}, {chunks} chunks, {len(files)} files{' (dry)' if dry else ''}")


def shore(world, job, land, dry):
    x0, z0, x1, z1 = job["rect"]; level = job["level"]; width = job.get("width", 36); protect = Protect(job.get("protect"))
    H, W = z1 - z0 + 1, x1 - x0 + 1
    noise = value_noise((H, W), 18, 1.2, 23) + value_noise((H, W), 6, 0.4, 29)
    changed = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            dist = {"E": x1 - x, "W": x - x0, "S": z1 - z, "N": z - z0}[job["water"]]
            if protect(x, z) or column_is_built(world, x, z): continue
            ty, tb = world.top(x, z)
            if tb in LIQUID and ty is not None and ty <= level: continue
            nat = land.at(x, z)
            if nat is None: continue
            nat = max(nat, level + 1)
            u = dist / float(width)
            if u > 1.0: continue
            end = min(z - z0, z1 - z) if job["water"] in "EW" else min(x - x0, x1 - x)      # taper at the rect's ends so no step forms there
            u = u + (1 - u) * (1 - float(smoothstep(end / 24.0)))
            want = level + 1 + (nat - level - 1) * float(smoothstep(u)) + (noise[z - z0, x - x0] if 0.12 < u < 0.88 else 0)
            want = int(round(min(max(want, level + 1), nat)))
            top = ("minecraft:sand" if (x * 3 + z * 5) % 4 else "minecraft:gravel") if dist <= 2 else "minecraft:grass_block"
            changed += column_op(world, x, z, want, top, None)
    files, chunks = world.save(dry)
    print(f"shore {job['shore']}: {changed} columns graded to the water at y {level}, {chunks} chunks{' (dry)' if dry else ''}")


def mouths(world, x0, z0, x1, z1):
    out = []
    for x in range(x0, x1 + 1):
        for z, sd in ((z0, "N"), (z1, "S")):
            y, b = world.top(x, z)
            if b in LIQUID: out.append((sd, x, z, y))
    for z in range(z0, z1 + 1):
        for x, sd in ((x0, "W"), (x1, "E")):
            y, b = world.top(x, z)
            if b in LIQUID: out.append((sd, x, z, y))
    groups = {}
    for sd, x, z, y in out: groups.setdefault(sd, []).append((x, z, y))
    for sd, lst in groups.items():
        lst.sort(); prev = lst[0]; run = [lst[0]]
        for p in lst[1:] + [None]:
            if p is not None and abs(p[0] - prev[0]) + abs(p[1] - prev[1]) <= 2: run.append(p); prev = p; continue
            mid = run[len(run) // 2]; print(f"  {sd} mouth at ({mid[0]}, {mid[1]}) water y {mid[2]}, {len(run)} columns wide")
            if p is not None: run = [p]; prev = p


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    if a[1] == "mouths":
        mouths(World(Path(a[2])), *map(int, a[3:7])); return
    world = World(Path(a[2])); jobs = json.load(open(a[3])); dry = "--dry-run" in a; land = Land()
    for j in jobs:
        if "shore" in j: shore(world, j, land, dry)
        else: carve(world, j, land, dry)


if __name__ == "__main__":
    main(sys.argv)
