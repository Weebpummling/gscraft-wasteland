#!/usr/bin/env python3
"""Find the dossier container for each strongpoint: every chest and barrel inside the site rectangle
of the built world, ranked so a person can pick one (highest floor first, then nearest the centre),
and write the choice to tools/dossiers.json for the scout quests and the datapack.

    python dossiers.py <world dir> [--pick]     list candidates per site; --pick writes the top one

The world is the v6 build (server/wasteland-v6 or the pristine set). Block entities are read straight
from the region files; nothing is written to the world.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import R, read_region_raw, region_of, slot_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# site -> (x0, z0, x1, z1) blocks, from docs/gscraft-map-layout-v6.md §3; the residential block has
# no rectangle in the sheet, so it takes a 128x128 window from its anchor (1328, 1376).
SITES = {
    "novo": (992, 96, 1135, 255),
    "residential": (1328, 1376, 1455, 1503),
    "plant": (1904, 864, 2367, 1135),
    "fr06": (2192, 400, 2575, 927),
    "financial": (-1952, 848, -1793, 991),
}
CONTAINERS = {"minecraft:chest", "minecraft:trapped_chest", "minecraft:barrel", "lootr:lootr_chest",
              "lootr:lootr_barrel", "lootr:lootr_trapped_chest"}
# the quest text names a room per site; the pick is the container that best fits it
ROOM = {"novo": "the gatehouse office", "residential": "the caretaker's flat", "plant": "the control room",
        "fr06": "the hangar office", "financial": "the vault anteroom"}


def containers_in(world: Path, rect):
    x0, z0, x1, z1 = rect
    out = []
    seen = set()
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            rx, rz = region_of(cx, cz)
            rp = world / "region" / f"r.{rx}.{rz}.mca"
            if rp not in seen:
                seen.add(rp)
                chunks = read_region_raw(rp)
                for (ccx, ccz) in [(a, b) for a in range(rx * 32, rx * 32 + 32) for b in range(rz * 32, rz * 32 + 32)]:
                    if not (x0 >> 4 <= ccx <= x1 >> 4 and z0 >> 4 <= ccz <= z1 >> 4):
                        continue
                    raw = chunks.get(slot_of(ccx, ccz))
                    if not raw:
                        continue
                    _, root = R(raw[2]).root()
                    for be in root.get("block_entities", (9, (10, [])))[1][1]:
                        bid = be.get("id", (8, ""))[1]
                        if bid not in CONTAINERS:
                            continue
                        x, y, z = be["x"][1], be["y"][1], be["z"][1]
                        if not (x0 <= x <= x1 and z0 <= z <= z1):
                            continue
                        items = len(be.get("Items", (9, (10, [])))[1][1])
                        out.append({"x": x, "y": y, "z": z, "id": bid, "items": items})
    return out


def rank(cands, rect):
    x0, z0, x1, z1 = rect
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    for c in cands:
        c["dist"] = round(((c["x"] - cx) ** 2 + (c["z"] - cz) ** 2) ** 0.5)
    # highest floor first (an office is upstairs), then closest to the centre
    return sorted(cands, key=lambda c: (-c["y"], c["dist"]))


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    world = Path(argv[1])
    pick = "--pick" in argv
    result = {}
    for site, rect in SITES.items():
        cands = rank(containers_in(world, rect), rect)
        ys = sorted({c["y"] for c in cands})
        print(f"\n== {site}  rect {rect}  {len(cands)} containers, floors y {ys[:3]}..{ys[-3:] if ys else ''}")
        for c in cands[:8]:
            print(f"   y {c['y']:4}  ({c['x']:6}, {c['z']:6})  {c['id']:28} items {c['items']:2}  {c['dist']:4} m from centre")
        if cands:
            top = cands[0]
            result[site] = {"room": ROOM[site], "x": top["x"], "y": top["y"], "z": top["z"], "id": top["id"],
                            "rect": list(rect), "candidates": len(cands)}
    if pick:
        out = ROOT / "tools" / "dossiers.json"
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print("\nwrote", out)


if __name__ == "__main__":
    main(sys.argv)
