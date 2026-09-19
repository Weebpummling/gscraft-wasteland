#!/usr/bin/env python3
"""RETIRED 2026-09-18 (owner: "remove the board... too much space for too little information"). The board is gone from
the world (`function gscraft:board_remove`), the mod runs without `gscraft_board/board.json`, and `/gscraft board` prints the
same one line per strongpoint as text. Kept for the record and for whatever display replaces it; do not run it.

The strongpoint board on the hall's ground floor (camp spec §2, ruling R4; system doc 2026-09-13 §7 build 8).

    python board.py <world dir>            -> finds a wall inside the hall for a 13 x 4 board (six 2-wide columns of
                                              concrete three high, the contested lamp at the end, a sign row in front),
                                              writes mod/.../gscraft_board/board.json (the geometry the mod reads) and
                                              build/datapacks/gscraft/data/gscraft/functions/board_*.mcfunction:
                                              board_<site>_<state> (36), board_lamp_on/off, board_place (everything unknown)
    python board.py <world dir> --apply    -> also copies the functions into the world's datapack, `/reload`s the local
                                              server and runs board_place (a world edit by commands, no upload)

The wall: the longest run of solid wall at y 65-68 inside the hall (start-compound §3: x -979..-937, z -858..-834,
floor y 64) with open floor in front of it inside the room. The board replaces the wall's own blocks, flush.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chests import Blocks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FN = ROOT / "build/datapacks/gscraft/data/gscraft/functions"
DATA = ROOT / "mod/src/main/resources/data/gscraft/gscraft_board/board.json"
WORLD_FN = "datapacks/gscraft/data/gscraft/functions"

HALL = (-786, -752, -902, -876)   # x0, x1, z0, z1: the walled compound's big hall (owner 2026-09-17; floor block 70)
Y0, ROWS = 71, 3                  # the concrete rows; the sign row is in front at Y0 + ROWS
COLUMNS = ["hospital", "krot", "switchyard", "turbine", "intake", "woods_outpost"]
NAMES = {"hospital": "HOSPITAL", "krot": "KROT", "switchyard": "SWITCHYARD", "turbine": "TURBINE HALL", "intake": "INTAKE WORKS", "woods_outpost": "THE WOODS"}
STATES = {"unknown": "black_concrete", "scouted": "yellow_concrete", "looted": "orange_concrete", "held": "light_blue_concrete",
          "defended": "lime_concrete", "lost": "red_concrete", "contested": "light_blue_concrete"}
WIDTH = 2
LENGTH = len(COLUMNS) * WIDTH + 1   # + the lamp


def plane_ok(b, cells, front):
    """every cell solid, and the three blocks in front of each cell open air with a floor under the first"""
    for (x, y, z) in cells:
        if not b.solid(x, y, z):
            return False
    for (x, y, z) in front:
        if not b.air(x, y, z):
            return False
    return True


def find_wall(b):
    x0, x1, z0, z1 = HALL
    best = None
    # walls running along x (facing +z or -z)
    for z in range(z0, z1 + 1):
        for sign in (1, -1):
            for xs in range(x0, x1 - LENGTH + 2):
                cells = [(xs + i, Y0 + r, z) for i in range(LENGTH) for r in range(ROWS + 1)]
                front = [(xs + i, Y0 + r, z + sign * d) for i in range(LENGTH) for r in range(ROWS + 1) for d in (1, 2, 3)]
                if not (z0 <= z + sign * 3 <= z1):
                    continue
                floor = all(b.solid(xs + i, Y0 - 1, z + sign) for i in range(LENGTH))
                if floor and plane_ok(b, cells, front):
                    depth = 3
                    while depth < 12 and all(b.air(xs + i, Y0, z + sign * (depth + 1)) for i in range(LENGTH)) and z0 <= z + sign * (depth + 1) <= z1:
                        depth += 1
                    cand = (depth, (xs, Y0, z), (1, 0), (0, sign))
                    if best is None or cand[0] > best[0]:
                        best = cand
    # walls running along z (facing +x or -x)
    for x in range(x0, x1 + 1):
        for sign in (1, -1):
            for zs in range(z0, z1 - LENGTH + 2):
                cells = [(x, Y0 + r, zs + i) for i in range(LENGTH) for r in range(ROWS + 1)]
                front = [(x + sign * d, Y0 + r, zs + i) for i in range(LENGTH) for r in range(ROWS + 1) for d in (1, 2, 3)]
                if not (x0 <= x + sign * 3 <= x1):
                    continue
                floor = all(b.solid(x + sign, Y0 - 1, zs + i) for i in range(LENGTH))
                if floor and plane_ok(b, cells, front):
                    depth = 3
                    while depth < 12 and all(b.air(x + sign * (depth + 1), Y0, zs + i) for i in range(LENGTH)) and x0 <= x + sign * (depth + 1) <= x1:
                        depth += 1
                    cand = (depth, (x, Y0, zs), (0, 1), (sign, 0))
                    if best is None or cand[0] > best[0]:
                        best = cand
    if best is None:
        best = free_standing(b)
    return best


FREE = (-842, -816, -906, -880)   # x0, x1, z0, z1: the yard west of the hall - a free-standing board facing west, its front the open yard


def free_standing(b):
    """no wall in the hall fit the board (the walled compound's hall has windows and pillars): a board on its own in the
    yard, its concrete rows the wall, facing east or west - the line's cells and three in front open air over a solid floor;
    the deepest open front wins"""
    x0, x1, z0, z1 = FREE
    best = None
    for x in range(x0, x1 + 1):
        for sign in (-1, 1):
            for zs in range(z0, z1 - LENGTH + 2):
                cells = [(x, Y0 + r, zs + i) for i in range(LENGTH) for r in range(ROWS + 1)]
                front = [(x + sign * d, Y0 + r, zs + i) for i in range(LENGTH) for r in range(ROWS + 1) for d in (1, 2, 3)]
                floor = all(b.solid(x + sign * d, Y0 - 1, zs + i) for i in range(LENGTH) for d in (0, 1))
                if floor and all(b.air(*c) for c in cells) and all(b.air(*c) for c in front):
                    depth = 3
                    while depth < 12 and all(b.air(x + sign * (depth + 1), Y0, zs + i) for i in range(LENGTH)):
                        depth += 1
                    cand = (depth, (x, Y0, zs), (0, 1), (sign, 0))
                    if best is None or cand[0] > best[0]:
                        best = cand
    return best


def facing(front):
    fx, fz = front
    return {(0, 1): "south", (0, -1): "north", (1, 0): "east", (-1, 0): "west"}[(fx, fz)]


def write(origin, along, front):
    ox, oy, oz = origin
    ax, az = along
    fx, fz = front
    FN.mkdir(parents=True, exist_ok=True)

    def cell(i, r):
        return ox + ax * i, oy + r, oz + az * i

    def sign_pos(i):
        x, y, z = cell(i, ROWS)
        return x + fx, y, z + fz

    lamp = cell(LENGTH - 1, 1)
    for ci, site in enumerate(COLUMNS):
        for state, block in STATES.items():
            lines = []
            for i in range(ci * WIDTH, ci * WIDTH + WIDTH):
                for r in range(ROWS):
                    x, y, z = cell(i, r)
                    lines.append(f"setblock {x} {y} {z} minecraft:{block}")
            (FN / f"board_{site}_{state}.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (FN / "board_lamp_on.mcfunction").write_text(f"setblock {lamp[0]} {lamp[1]} {lamp[2]} minecraft:redstone_lamp[lit=true]\n", encoding="utf-8")
    (FN / "board_lamp_off.mcfunction").write_text(f"setblock {lamp[0]} {lamp[1]} {lamp[2]} minecraft:redstone_lamp[lit=false]\n", encoding="utf-8")
    place = [f"function gscraft:board_{site}_unknown" for site in COLUMNS] + ["function gscraft:board_lamp_off"]
    for ci, site in enumerate(COLUMNS):
        x, y, z = sign_pos(ci * WIDTH)
        text = NAMES[site].split(" ")
        msgs = [f"'{{\"text\":\"{text[0]}\"}}'", f"'{{\"text\":\"{text[1] if len(text) > 1 else ''}\"}}'", "'{\"text\":\"\"}'", "'{\"text\":\"\"}'"]
        place.append(f"setblock {x} {y} {z} minecraft:oak_wall_sign[facing={facing(front)}]{{front_text:{{messages:[{','.join(msgs)}]}}}}")
    (FN / "board_place.mcfunction").write_text("\n".join(place) + "\n", encoding="utf-8")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps({"__comment": "the strongpoint board's geometry (tools/board.py): origin = the first column's bottom block, along = the wall's direction, front = the side the room is on",
                                "origin": [ox, oy, oz], "along": [ax, az], "front": [fx, fz], "width": WIDTH, "height": ROWS, "columns": COLUMNS, "lamp": list(lamp)}, indent=1) + "\n", encoding="utf-8")
    return len(COLUMNS) * len(STATES) + 3


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    world = Path(argv[1])
    b = Blocks(world)
    found = find_wall(b)
    if not found:
        sys.exit("no wall for the board inside the hall")
    depth, origin, along, front = found
    n = write(origin, along, front)
    print(f"board at {origin} along {along} facing {facing(front)}, {depth} open in front; {n} functions written; {DATA.name}")
    if "--apply" in argv:
        import shutil
        import time
        import localtest as L
        target = world / WORLD_FN
        target.mkdir(parents=True, exist_ok=True)
        for f in FN.glob("board_*.mcfunction"):
            shutil.copy(f, target / f.name)
        r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
        print(r.cmd("reload", timeout=120))
        time.sleep(3)
        print(r.cmd(f"forceload add {origin[0] - 8} {origin[2] - 8} {origin[0] + 8} {origin[2] + 8}"))
        time.sleep(2)
        print(r.cmd("function gscraft:board_place"))
        print(r.cmd(f"forceload remove {origin[0] - 8} {origin[2] - 8} {origin[0] + 8} {origin[2] + 8}"))
        r.close()
        print("placed")


if __name__ == "__main__":
    main(sys.argv)
