"""Extend a transplanted bridge across the river it now has to cross (v8: the Skadowsky highway viaduct, whose far bank
was off the source map, over the widened river to the new west bank).

usage: bridge.py <world dir> <bridge.json> [--dry-run]
bridge.json: [{"name": "...", "template_x": -1030, "z0": -958, "z1": -933, "y0": 44, "y1": 95, "deck_y": 66,
               "start_x": -1089, "dx": -1, "pier_every": 12, "max_len": 120, "abutment": 6}]
The cross-section at template_x (every block with its properties, z0..z1, y0..y1) is stamped column by column from start_x
in direction dx until the ground under the centre line has risen to the deck's underside for three columns in a row, then
`abutment` more columns onto the bank. Under the deck: template columns that are solid down to the bed (the source's earth
median) become piers every `pier_every` columns and open water/air elsewhere; on the bank nothing below the deck is touched.
Prints the end column (the road stub for roads.py) and writes it to <bridge.json>.stubs.json.
"""
import sys, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terrain import World, AIR, LIQUID, NATURAL
from anvil import block_index

SOLID_GROUND = {"minecraft:stone", "minecraft:dirt", "minecraft:grass_block", "minecraft:coarse_dirt", "minecraft:gravel", "minecraft:cobblestone", "minecraft:andesite"}


def get_state(world, x, y, z):
    c = world.chunk(x >> 4, z >> 4)
    if not c: return None, None
    s = c[2].secs.get(y >> 4)
    if not s: return "minecraft:air", None
    sec, names, pal, idx, _ = s
    e = pal[idx[block_index(x & 15, y & 15, z & 15)]]
    props = {k: v[1] for k, v in e.get("Properties", (0, {}))[1].items()} or None
    return e["Name"][1], props


def build(world, job, dry):
    tx, z0, z1, y0, y1 = job["template_x"], job["z0"], job["z1"], job["y0"], job["y1"]
    deck, sx, dx = job.get("deck_y", 66), job["start_x"], job.get("dx", -1)
    every, max_len, abut = job.get("pier_every", 12), job.get("max_len", 120), job.get("abutment", 6)
    zc = (z0 + z1) // 2
    tmpl = {}
    for z in range(z0, z1 + 1):
        col = [get_state(world, tx, y, z) for y in range(y0, y1 + 1)]
        solid_base = all(n in SOLID_GROUND for n, _ in col[:deck - y0 - 4])          # the source's earth median: solid from the bed to under the deck
        tmpl[z] = (col, solid_base)
    x = sx; on_bank = 0; stamped = 0; end_x = None
    for k in range(max_len):
        g = world.ground(x, zc)
        if g is None: break
        bank = g is not None and g >= deck - 1
        on_bank = on_bank + 1 if bank else 0
        pier = (k % every) == 0
        for z in range(z0, z1 + 1):
            col, solid_base = tmpl[z]
            gz = world.ground(x, z) or -64
            for i, (n, props) in enumerate(col):
                y = y0 + i
                if y < deck:
                    if gz >= deck - 1: continue                                           # on the bank: the ground stays
                    if solid_base and not pier:
                        want = "minecraft:water" if y <= job.get("water_y", 53) else "minecraft:air"
                    elif solid_base and pier:
                        want = "minecraft:stone" if y > gz else None
                    else:
                        want = n if n not in LIQUID else ("minecraft:water" if y <= job.get("water_y", 53) else "minecraft:air")
                        if want in AIR and y <= job.get("water_y", 53) and gz < y: want = "minecraft:water"
                    if want is None or y <= gz: continue
                    if world.get(x, y, z) != want: world.set(x, y, z, want)
                else:
                    if world.get(x, y, z) != n or props: world.set(x, y, z, n, props)
        stamped += 1; end_x = x
        if on_bank >= 3 + abut: break
        x += dx
    files, chunks = world.save(dry)
    print(f"bridge {job['name']}: {stamped} columns stamped from x {sx} towards {'west' if dx < 0 else 'east'}, ends at x {end_x} (bank reached: {on_bank >= 3}), {chunks} chunks{' (dry)' if dry else ''}")
    return {"name": job["name"], "x": end_x + dx, "z": zc, "y": deck + 2, "side": "W" if dx < 0 else "E", "width": z1 - z0 - 4}


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world = World(Path(a[1])); jobs = json.load(open(a[2])); dry = "--dry-run" in a
    stubs = [build(world, j, dry) for j in jobs]
    json.dump(stubs, open(a[2] + ".stubs.json", "w"), indent=1); print("road stubs ->", a[2] + ".stubs.json", stubs)


if __name__ == "__main__":
    main(sys.argv)
