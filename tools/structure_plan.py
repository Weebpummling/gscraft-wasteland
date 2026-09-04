#!/usr/bin/env python3
"""Curate the generated structures: from the census (tools/structures_v6.json), the site rectangles,
the camp and the roads, decide which generated sites the design keeps and which are pruned, by
range and by role, and draw the map.

    python structure_plan.py            -> buildmap/structure_plan_v7.json, docs/renders/structures_v6.png

Rules (design §2.3 and gscraft-structure-plan.md):
  - nothing generated within 350 m of a strongpoint, a loot site, the camp outline or the tower;
  - kept sites are at least MIN_GAP apart per type, chosen greedily by distance from a road
    (near a road first: the players will actually find it);
  - per-type caps per range ring (foot < 1.5 km, road 1.5-4 km, air 4.5-6.5 km, beyond: none).
Everything else is on the prune list, with its start chunk, for the regeneration or the in-place cut.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "tools" / "structures_v6.json"
OUT = ROOT / "buildmap" / "structure_plan_v7.json"
PNG = ROOT / "docs" / "renders" / "structures_v6.png"
CAMP = (16, 16)
CENTRE = (1900, 1250)              # border centre; the box is +-5000
# site rectangles (blocks x0 z0 x1 z1) from the layout sheet, plus the camp and the tower
SITES = {
    "camp": (-176, -176, 207, 207), "novo": (984, 88, 1143, 263), "residential": (1328, 1376, 1455, 1503),
    "plant": (1904, 864, 2367, 1135), "fr06": (2192, 400, 2575, 927), "financial": (-1976, 840, -1801, 999),
    "settlement": (3520, 640, 3791, 927), "runway": (3040, 2519, 3470, 2710), "biogen": (2976, 2528, 3039, 2639),
    "hub": (5600, 1184, 6431, 1823), "district": (896, 384, 3103, 2079),
}
BUFFER = 350
# type -> (min gap between kept sites, caps per ring: foot, road, air)
POLICY = {
    "underground_bunkers:underground_bunker": (600, (2, 6, 6)),
    "apotheosis:tower": (900, (0, 5, 6)),              # all four tower variants pooled
    "minecraft:village": (1200, (0, 4, 6)),            # Lukis capitals, hostile
    "minecraft:pillager_outpost": (1000, (1, 3, 3)),
    "minecraft:ancient_city": (1500, (0, 1, 3)),
    "minecraft:mansion": (1, (0, 1, 1)),
    "minecraft:stronghold": (1, (0, 0, 2)),
    "minecraft:monument": (1500, (0, 1, 2)),
    "man:house": (800, (1, 3, 3)),
    "minecraft:trail_ruins": (1000, (1, 2, 2)),
    "minecraft:igloo": (1500, (0, 1, 1)),
    "minecraft:desert_pyramid": (1500, (0, 1, 1)),
    "minecraft:jungle_pyramid": (1500, (0, 1, 1)),
}
POOL = {"apotheosis:tower_main": "apotheosis:tower", "apotheosis:tower_sand": "apotheosis:tower",
        "apotheosis:tower_spruce": "apotheosis:tower", "apotheosis:tower_leaf": "apotheosis:tower",
        "minecraft:village_plains": "minecraft:village", "minecraft:village_desert": "minecraft:village",
        "minecraft:village_savanna": "minecraft:village", "minecraft:village_snowy": "minecraft:village",
        "minecraft:village_taiga": "minecraft:village"}
LEFT_ALONE = {"minecraft:mineshaft", "minecraft:mineshaft_mesa", "minecraft:shipwreck", "minecraft:shipwreck_beached",
              "minecraft:ocean_ruin_cold", "minecraft:ocean_ruin_warm", "minecraft:buried_treasure",
              "minecraft:ruined_portal", "minecraft:ruined_portal_ocean", "minecraft:ruined_portal_mountain",
              "minecraft:ruined_portal_desert", "minecraft:ruined_portal_jungle", "minecraft:ruined_portal_swamp",
              "minecraft:swamp_hut"}                # underground, underwater or trivial: background, not sites


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def rect_dist(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2]); dz = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dz)


def ring(p):
    d = dist(p, CAMP)
    if d < 1500: return 0
    if d < 4000: return 1
    if 4500 <= d <= 6500: return 2
    return None


def load_roads():
    pts = []
    for r in json.loads((ROOT / "buildmap" / "routes_v6.json").read_text(encoding="utf-8")):
        pts += [tuple(p) for p in r["polyline"]]
    return pts


def main():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    roads = load_roads()
    pooled = {}
    for name, pts in census["positions"].items():
        key = POOL.get(name, name)
        pooled.setdefault(key, []).extend((x, z, name) for x, z in pts)
    plan = {"rules": {"buffer_m": BUFFER, "policy": {k: {"min_gap": g, "caps_foot_road_air": c} for k, (g, c) in POLICY.items()}},
            "keep": {}, "prune": {}, "left_alone": {k: census["counts"][k] for k in LEFT_ALONE if k in census["counts"]}, "summary": {}}
    for key, pts in pooled.items():
        if key in LEFT_ALONE:
            continue
        if key not in POLICY:
            plan["prune"][key] = [{"x": x, "z": z, "id": n, "why": "no role"} for x, z, n in pts]
            plan["summary"][key] = {"total": len(pts), "keep": 0}
            continue
        gap, caps = POLICY[key]
        cands = []
        for x, z, n in pts:
            p = (x, z)
            too_close = min(rect_dist(p, r) for r in SITES.values())
            rg = ring(p)
            road = min(dist(p, q) for q in roads)
            cands.append({"x": x, "z": z, "id": n, "ring": rg, "site_m": round(too_close), "road_m": round(road)})
        cands.sort(key=lambda c: c["road_m"])
        kept, used = [], [0, 0, 0]
        for c in cands:
            if c["ring"] is None or c["site_m"] < BUFFER or used[c["ring"]] >= caps[c["ring"]]:
                continue
            if any(dist((c["x"], c["z"]), (k["x"], k["z"])) < gap for k in kept):
                continue
            kept.append(c); used[c["ring"]] += 1
        keep_ids = {(k["x"], k["z"]) for k in kept}
        pruned = []
        for c in cands:
            if (c["x"], c["z"]) in keep_ids:
                continue
            why = ("outside the ranges" if c["ring"] is None else "inside a site buffer" if c["site_m"] < BUFFER else "over the cap or too close to a kept one")
            pruned.append({**c, "why": why})
        plan["keep"][key] = kept; plan["prune"][key] = pruned
        plan["summary"][key] = {"total": len(pts), "keep": len(kept), "by_ring": used}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print(f"{'type':40} {'total':>6} {'keep':>5}  foot/road/air")
    for key, s in sorted(plan["summary"].items(), key=lambda kv: -kv[1]["total"]):
        print(f"{key:40} {s['total']:6} {s['keep']:5}  {s.get('by_ring', '-')}")
    tk = sum(s["keep"] for s in plan["summary"].values()); tp = sum(len(v) for v in plan["prune"].values())
    print(f"\nkeep {tk}, prune {tp}, left alone {sum(plan['left_alone'].values())} background structures")
    draw(plan, roads)


def draw(plan, roads):
    from PIL import Image, ImageDraw
    S = 0.16                                            # px per block; 10 km -> 1600 px
    W = int(10000 * S) + 40
    img = Image.new("RGB", (W, W), (232, 230, 224)); d = ImageDraw.Draw(img)
    def px(x, z): return (int((x - CENTRE[0] + 5000) * S) + 20, int((z - CENTRE[1] + 5000) * S) + 20)
    for i in range(1, 7):
        r = int(i * 1000 * S); c = px(*CAMP); d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(200, 196, 186))
    for a, b in zip(roads, roads[1:]):
        if dist(a, b) < 40: d.line([px(*a), px(*b)], fill=(90, 90, 90), width=2)
    for name, r in SITES.items():
        d.rectangle([px(r[0], r[1]), px(r[2], r[3])], outline=(40, 40, 40), width=2)
        d.text(px(r[0], r[1] - 40), name, fill=(40, 40, 40))
    colours = {"underground_bunkers:underground_bunker": (200, 120, 30), "apotheosis:tower": (150, 40, 160),
               "minecraft:village": (30, 110, 200), "minecraft:pillager_outpost": (190, 30, 30), "minecraft:ancient_city": (20, 80, 80)}
    for key, pts in plan["prune"].items():
        col = colours.get(key, (150, 150, 150))
        for p in pts:
            x, y = px(p["x"], p["z"]); d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=tuple(int(c * 0.35 + 170) for c in col))
    for key, pts in plan["keep"].items():
        col = colours.get(key, (60, 60, 60))
        for p in pts:
            x, y = px(p["x"], p["z"]); d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=col, outline=(0, 0, 0))
    y = 30
    for key, col in colours.items():
        d.rectangle([W - 260, y, W - 246, y + 14], fill=col); d.text((W - 240, y), key.split(":")[1] + "  (bold = kept)", fill=(30, 30, 30)); y += 18
    PNG.parent.mkdir(parents=True, exist_ok=True); img.save(PNG); print("map:", PNG)


if __name__ == "__main__":
    main()
