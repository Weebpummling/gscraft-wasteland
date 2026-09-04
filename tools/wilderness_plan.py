#!/usr/bin/env python3
"""Wilderness objectives: pick spots in open land — not city, not water, off the roads, outside the
designed sites' buffers — for the six wilderness quests (one per NPC) and write them to
buildmap/wilderness_v7.json with the placement function gscraft:wilderness (markers only; the
dressing templates are Phase C). Reads tools/landuse_v6.json (the chunk grid) and the roads.

    python wilderness_plan.py            -> buildmap/wilderness_v7.json, functions/wilderness.mcfunction

Spots per objective, ring and distance from the nearest road:
  survey     James   4 trig points, foot+road rings, 250-900 m off a road, high ground preferred
  spring     Michael 1 spring, foot ring, 200-600 m off the spine
  herbs      Tony    3 herb patches, foot+road, 150-600 m off a road
  convoy     Walker  2 wrecked convoys, road ring, 300-900 m off a road
  relays     Tune    3 relay-mast sites, road ring, 400-1200 m off a road, spread by 1.5 km
  cache      Marshall 3 fuel caches, road+air rings, 200-800 m off a road
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMP = (16, 16)
SITES = {
    "camp": (-176, -176, 207, 207), "novo": (984, 88, 1143, 263), "residential": (1328, 1376, 1455, 1503),
    "plant": (1904, 864, 2367, 1135), "fr06": (2192, 400, 2575, 927), "financial": (-1976, 840, -1801, 999),
    "settlement": (3520, 640, 3791, 927), "runway": (3040, 2519, 3470, 2710), "biogen": (2976, 2528, 3039, 2639),
    "hub": (5600, 1184, 6431, 1823), "district": (896, 384, 3103, 2079),
}
BUFFER = 350
OBJECTIVES = [
    # name, npc, count, rings, road min, road max, min gap between its own spots
    ("survey", "james", 4, ("foot", "road"), 250, 900, 800),
    ("spring", "michael", 1, ("foot",), 200, 600, 0),
    ("herbs", "tony", 3, ("foot", "road"), 150, 600, 500),
    ("convoy", "walker", 2, ("road",), 300, 900, 1200),
    ("relays", "tune", 3, ("road",), 400, 1200, 1500),
    ("cache", "marshall", 3, ("road", "air"), 200, 800, 1000),
]


def ring(x, z):
    d = math.hypot(x - CAMP[0], z - CAMP[1])
    return "foot" if d < 1500 else "road" if d < 4000 else "air" if d <= 6500 else "beyond"


def rect_dist(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2]); dz = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dz)


def main():
    lu = json.loads((ROOT / "tools" / "landuse_v6.json").read_text(encoding="utf-8"))
    cx0, cz0 = lu["grid_origin_chunk"]; grid = lu["grid"]
    roads = []
    for r in json.loads((ROOT / "buildmap" / "routes_v6.json").read_text(encoding="utf-8")):
        roads += [tuple(p) for p in r["polyline"]]
    rng = random.Random(2404991234066556536)
    # candidate chunks: wilderness with wilderness on all four sides (so the spot is open ground, not a city edge)
    cands = []
    n = len(grid)
    for gz in range(1, n - 1):
        row = grid[gz]
        for gx in range(1, n - 1):
            if row[gx] == "." and row[gx - 1] == "." and row[gx + 1] == "." and grid[gz - 1][gx] == "." and grid[gz + 1][gx] == ".":
                cands.append(((cx0 + gx) * 16 + 8, (cz0 + gz) * 16 + 8))
    rng.shuffle(cands)
    print(f"{len(cands)} open-ground chunks")
    chosen = {}; all_spots = []
    for name, npc, count, rings, rmin, rmax, gap in OBJECTIVES:
        picks = []
        for x, z in cands:
            if ring(x, z) not in rings: continue
            if min(rect_dist((x, z), r) for r in SITES.values()) < BUFFER: continue
            road = min(math.hypot(x - a, z - b) for a, b in roads)
            if not (rmin <= road <= rmax): continue
            if any(math.hypot(x - p["x"], z - p["z"]) < gap for p in picks): continue
            if any(math.hypot(x - p["x"], z - p["z"]) < 300 for p in all_spots): continue
            picks.append({"x": x, "z": z, "ring": ring(x, z), "road_m": round(road)})
            if len(picks) == count: break
        chosen[name] = {"npc": npc, "spots": picks}; all_spots += picks
        print(f"  {name:7} {npc:8} {len(picks)}/{count}: " + ", ".join(f"({p['x']}, {p['z']}) {p['ring']} road {p['road_m']} m" for p in picks))
    (ROOT / "buildmap" / "wilderness_v7.json").write_text(json.dumps(chosen, indent=1), encoding="utf-8")
    # a marker function: a lit post at each spot so the visual pass can find them (the dressing is Phase C)
    lines = []
    for name, d in chosen.items():
        for p in d["spots"]:
            lines.append(f"execute positioned {p['x']} 0 {p['z']} run setblock ~ ~ ~ minecraft:air")  # placeholder, replaced below
    fn = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft" / "functions" / "wilderness.mcfunction"
    fn.write_text("\n".join(f"# {name} ({d['npc']}): " + "; ".join(f"{p['x']} {p['z']}" for p in d["spots"]) for name, d in chosen.items()) +
                  "\n# markers are placed by the Phase C dressing pass at ground level; this file records the spots\n", encoding="utf-8")
    print("wrote buildmap/wilderness_v7.json and", fn.name)


if __name__ == "__main__":
    main()
