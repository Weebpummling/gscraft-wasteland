"""Author the map's relief from the step-2 zones over the Pripyat cell (docs/gscraft-map-plan-v8.md section 2).

usage: heightplan.py <census dir> <out dir> [--seed N]
  <census dir> holds classes.npy (uint8 surface classes, see incoming/census/classraster.py) and surface_y.npy for the
  cell x -3900..1200 z -3900..700 (one cell per block). Writes:
    height.npy        int16 target surface height per block (the spine's terrain)
    height16.png      the same as a 16-bit PNG (WorldPainter / GIS friendly, value = y)
    height_preview.png  shaded, coloured preview with the fixed areas hatched
    height_stats.txt  how much ground moves, by zone

Rules: every road, rail, water and building column keeps its surface (fixed); fixed areas carry a 24-block apron that
also stays; from there the relief blends in over 64 blocks (smoothstep). Zones (blocks, from the plan):
  A camp plateau 84-90 with a basin cut to 63 at its centre (radius 90, rim at 84);
  B west ridge 95-105; D / D2 rolling fields 65-72. (The Woods is a named area on the existing forest, owner 2026-09-04.) Elsewhere 65 with folds of +-1.
Noise is layered gaussian-smoothed random fields so folds are 2-4 blocks over 100 m, never spiky.
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

X0, Z0, X1, Z1 = -3900, -3900, 1200, 700
BASE = 65.0
ZONES = {  # name: (polygon in blocks, lo, hi)
    "A_plateau": ([(-2250, -2800), (-1350, -2850), (-1150, -2400), (-1350, -1950), (-2150, -1900)], 84, 90),
    "B_ridge": ([(-3900, -2600), (-3550, -2600), (-3450, -1600), (-3650, -600), (-3400, 300), (-3500, 700), (-3900, 700)], 95, 105),
    "D_fields": ([(-1500, -2000), (-500, -2150), (-300, -1500), (-1100, -1100), (-1500, -1300)], 65, 72),
    "D2_fields": ([(-3300, -3900), (-2600, -3900), (-2700, -3400), (-3200, -3300)], 65, 72),
}
BASIN = ((-1750, -2380), 90, 63)     # centre, radius, floor: the camp's crater lake
FIXED_CLASSES = (1, 2, 3, 4)         # road, rail, water, building
APRON, BLEND = 24, 64


def smoothstep(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def noise(shape, rng, scales=((400, 1.0), (150, 0.5), (60, 0.25))):
    out = np.zeros(shape, np.float32)
    for sigma, amp in scales:
        f = ndimage.gaussian_filter(rng.standard_normal(shape).astype(np.float32), sigma / 4, truncate=3)  # noise on a 4x grid below
        f /= (np.abs(f).max() + 1e-6); out += amp * f
    return out / sum(a for _, a in scales)


def main(a):
    cdir, out = Path(a[1]), Path(a[2]); out.mkdir(parents=True, exist_ok=True)
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 7
    cls = np.load(cdir / "classes.npy"); sy = np.load(cdir / "surface_y.npy").astype(np.float32)
    H, W = cls.shape; assert (H, W) == (Z1 - Z0 + 1, X1 - X0 + 1), cls.shape
    rng = np.random.default_rng(seed)
    # work on a 4-block grid for the smooth fields, upsample at the end
    h4, w4 = (H + 3) // 4, (W + 3) // 4
    fixed = np.isin(cls, FIXED_CLASSES)
    fixed4 = ndimage.zoom(fixed.astype(np.float32), (h4 / H, w4 / W), order=1) > 0.05
    fixed4 = ndimage.binary_dilation(fixed4, iterations=APRON // 4)
    dist4 = ndimage.distance_transform_edt(~fixed4) * 4          # blocks to the nearest fixed apron
    w_relief = smoothstep(dist4 / BLEND)
    # zone target offsets
    def rasterise(poly):
        im = Image.new("L", (w4, h4), 0); d = ImageDraw.Draw(im)
        d.polygon([((x - X0) / 4, (z - Z0) / 4) for x, z in poly], fill=255)
        return np.array(im) > 0
    sy4 = ndimage.zoom(np.where(fixed, np.nan, sy), (h4 / H, w4 / W), order=1)
    sy4 = np.where(np.isnan(sy4), BASE, sy4); sy4 = ndimage.gaussian_filter(sy4, 4)   # the existing natural surface, smoothed
    target4 = sy4 + 1.0 * noise((h4, w4), rng, ((300, 1.0), (120, 0.5)))
    zone_id = np.zeros((h4, w4), np.uint8)
    for k, (name, (poly, lo, hi)) in enumerate(ZONES.items(), 1):
        m = rasterise(poly)
        # soften the zone edge over 96 blocks so a zone never has a lip
        soft = smoothstep(ndimage.distance_transform_edt(m) * 4 / 96)
        n = (noise((h4, w4), rng) + 1) / 2                      # 0..1
        level = np.maximum(sy4, lo + (hi - lo) * n)      # zones raise the ground, never lower an existing hill
        target4 = np.where(m, target4 + (level - target4) * soft, target4)
        zone_id[m] = k
    # the camp basin
    (bx, bz), r, floor = BASIN
    yy, xx = np.mgrid[0:h4, 0:w4]; d = np.hypot(xx * 4 + X0 - bx, yy * 4 + Z0 - bz)
    bowl = smoothstep((d - r) / 60)                              # 0 at the lake edge, 1 at r+60
    target4 = np.where(d < r + 60, floor + (target4 - floor) * bowl, target4)
    target4[d < r] = floor
    # blend to the fixed surface
    final4 = sy4 + (target4 - sy4) * w_relief
    final = ndimage.zoom(final4, (H / h4, W / w4), order=1)[:H, :W]
    final = np.where(fixed, sy, final)
    final = np.round(final).astype(np.int16)
    np.save(out / "height.npy", final)
    Image.fromarray(final.astype(np.uint16), "I;16").save(out / "height16.png")
    # stats
    delta = final.astype(np.int32) - np.round(sy).astype(np.int32)
    lines = [f"cell {W}x{H} blocks; fixed columns {int(fixed.sum()):,} ({fixed.mean():.1%}); moved columns {int((delta != 0).sum()):,}",
             f"raise: {int((delta > 0).sum()):,} columns, {int(delta[delta > 0].sum()):,} blocks of fill; cut: {int((delta < 0).sum()):,} columns, {int(-delta[delta < 0].sum()):,} blocks",
             f"final height: min {final.min()} p5 {np.percentile(final, 5):.0f} median {np.median(final):.0f} p95 {np.percentile(final, 95):.0f} max {final.max()}"]
    zid = ndimage.zoom(zone_id, (H / h4, W / w4), order=0)[:H, :W]
    for k, name in enumerate(ZONES, 1):
        m = (zid == k) & ~fixed
        if m.any(): lines.append(f"  {name}: {int(m.sum()):,} columns, height {final[m].min()}..{final[m].max()}, mean {final[m].mean():.1f}")
    # max slope check (per 8 blocks)
    g = np.maximum(np.abs(np.diff(final.astype(np.int16), axis=0, prepend=final[:1])), np.abs(np.diff(final.astype(np.int16), axis=1, prepend=final[:, :1])))
    lines.append(f"steps >= 3 between neighbouring columns (outside fixed): {int(((g >= 3) & ~fixed).sum()):,}")
    (out / "height_stats.txt").write_text("\n".join(lines), encoding="utf-8"); print("\n".join(lines))
    # preview
    lo, hi = 60, 110
    t = np.clip((final - lo) / (hi - lo), 0, 1)
    rgb = np.stack([255 * t, 255 * (1 - np.abs(t - 0.5) * 2), 255 * (1 - t)], -1)
    shade = 1 + 0.5 * np.clip((np.roll(final, 1, 0) - final + np.roll(final, 1, 1) - final) / 6, -1, 1)[..., None]
    rgb = np.clip(rgb * shade, 0, 255)
    rgb[cls == 3] = (40, 80, 190); rgb[cls == 4] = (110, 100, 100); rgb[cls == 1] = (30, 30, 30); rgb[cls == 2] = (230, 140, 40); rgb[cls == 5] = rgb[cls == 5] * 0.6
    im = Image.fromarray(rgb.astype(np.uint8)).resize((W // 3, H // 3), Image.BOX)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.width, 16], fill=(0, 0, 0))
    d.text((6, 3), f"height plan (seed {seed}): colour 60..110, shaded; black roads, orange rail, blue water, grey buildings; 1 px = 3 blocks", fill=(255, 255, 255))
    im.save(out / "height_preview.png"); print("->", out)


if __name__ == "__main__":
    main(sys.argv)
