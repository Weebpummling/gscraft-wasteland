#!/usr/bin/env python3
"""Furnish a site that came across without containers: pick enclosed interior floor spots spread
through the site rectangle and write a datapack function that places loot chests there.

    python furnish.py <world dir> <site> <count> <loot table>
        e.g.  furnish.py ../../server/wasteland-v6 novo 12 gscraft:sites/novo

Writes build/datapacks/gscraft/data/gscraft/functions/furnish_<site>.mcfunction and appends the
spots to tools/furnish.json. Spots are at least 12 blocks apart, on solid floors with three air
above and a roof within 14, preferring upper floors, never inside the dossier chest's own room.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import R, read_region_raw, region_of, slot_of  # noqa: E402
from anvil import Chunk  # noqa: E402
import dossiers as D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
AIRS = {"minecraft:air", "minecraft:cave_air"}


class World:
    def __init__(self, path):
        self.path = Path(path); self.cache = {}

    def chunk(self, cx, cz):
        if (cx, cz) not in self.cache:
            rx, rz = region_of(cx, cz)
            raw = read_region_raw(self.path / "region" / f"r.{rx}.{rz}.mca").get(slot_of(cx, cz))
            self.cache[(cx, cz)] = Chunk(R(raw[2]).root()[1]) if raw else None
        return self.cache[(cx, cz)]

    def block(self, x, y, z):
        c = self.chunk(x >> 4, z >> 4)
        return c.get(x & 15, y, z & 15) if c else "minecraft:air"


def interior_spots(w, rect, ymin, ymax, step=3):
    x0, z0, x1, z1 = rect
    out = []
    for x in range(x0 + 2, x1 - 1, step):
        for z in range(z0 + 2, z1 - 1, step):
            col = [w.block(x, y, z) for y in range(ymin, ymax + 1)]
            for i in range(1, len(col) - 4):
                if col[i - 1] not in AIRS and col[i] in AIRS and col[i + 1] in AIRS and col[i + 2] in AIRS:
                    roof = next((k for k in range(i + 3, min(i + 15, len(col))) if col[k] not in AIRS), None)
                    if roof is not None:
                        out.append((ymin + i, x, z, col[i - 1], roof - i))
    return out


def main(argv):
    if len(argv) != 5:
        sys.exit(__doc__)
    world, site, count, table = World(argv[1]), argv[2], int(argv[3]), argv[4]
    rect = D.SITES[site]
    dossier = json.loads((ROOT / "tools" / "dossiers.json").read_text(encoding="utf-8")).get(site)
    spots = interior_spots(world, rect, 60, 140)
    rng = random.Random(hash(site) & 0xFFFF)
    rng.shuffle(spots)
    spots.sort(key=lambda s: -s[0])                    # upper floors first, then the shuffle decides ties
    chosen = []
    for y, x, z, floor, roof in spots:
        if dossier and abs(x - dossier["x"]) < 10 and abs(z - dossier["z"]) < 10:
            continue
        if any(abs(x - c[1]) < 12 and abs(z - c[2]) < 12 for c in chosen):
            continue
        chosen.append((y, x, z, floor, roof))
        if len(chosen) == count:
            break
    lines = [f"setblock {x} {y} {z} minecraft:chest[facing=north]{{LootTable:\"{table}\"}} keep" for y, x, z, _, _ in chosen]
    fn = ROOT / "build/datapacks/gscraft/data/gscraft/functions" / f"furnish_{site}.mcfunction"
    fn.write_text("\n".join(lines) + "\n", encoding="utf-8")
    jp = ROOT / "tools" / "furnish.json"
    data = json.loads(jp.read_text(encoding="utf-8")) if jp.exists() else {}
    data[site] = {"table": table, "chests": [{"x": x, "y": y, "z": z, "floor": f} for y, x, z, f, _ in chosen]}
    jp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{site}: {len(spots)} enclosed spots, {len(chosen)} chests -> {fn.name}")
    for y, x, z, f, r in chosen:
        print(f"   ({x:6}, {y:3}, {z:6}) on {f.split(':')[-1]:24} roof +{r}")


if __name__ == "__main__":
    main(sys.argv)
