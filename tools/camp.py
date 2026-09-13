#!/usr/bin/env python3
"""The camp's survivors as datapack functions (camp spec §1, cut to what the building takes need - next-steps plan §2d).

    python camp.py <world dir>   -> functions/camp_npc_<npc>.mcfunction (six), functions/camp_npcs.mcfunction, tools/camp_npcs.json

Each `camp_npc_<npc>` kills the survivor by tag and summons it again on its spot: a villager with no AI, invulnerable,
persistent, silent, named, tagged `gscraft_npc` and `gscraft_npc_<npc>` (a nitwit: no trades - the right-click is Phase
C's, the quest book). `camp_npcs` runs all six (a respawn of everything). The site loop runs a building's `held` list -
`camp_npc_marshall` on the gatehouse, Tony and Tune on the north complex, James on the crossing; Walker and Michael are
in the compound from the start (`camp_torches` at the deploy runs beside them: run `camp_npcs` once at the deploy too).

The spot: the lowest hard-surface column near the middle of the survivor's lock rectangle (skadowsky-camp §3) at floor
level, read from the world - a first cut for the visual pass to move, like the rectangles themselves.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from camp_ruins import Ground  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FN = ROOT / "build" / "datapacks" / "gscraft" / "data" / "gscraft" / "functions"

# npc -> (name, lock rectangle x0, z0, x1, z1 (skadowsky-camp §3), the floor level to prefer)
NPCS = {
    "walker": ("Walker the Foreman", (-975, -880, -940, -845), 64),      # the yard (the compound's hall side)
    "michael": ("Michael the Engineer", (-938, -900, -910, -870), 64),   # the brick block
    "marshall": ("Marshall", (-978, -955, -955, -940), 66),              # the gatehouse, the bridge's east end
    "tony": ("Tony the Medic", (-966, -1060, -930, -1020), 63),          # the clinic
    "tune": ("Tune the Technician", (-925, -1040, -905, -1020), 63),     # the radio shack
    "james": ("James the Scout", (-905, -978, -884, -964), 66),          # the signal box and the crossing's paving beside it (the box's columns are roof)
}
# hard ground a survivor stands on; not cobblestone (the torches' plinths)
HARD = {"stone", "andesite", "diorite", "granite", "gravel", "stone_bricks", "smooth_stone", "polished_andesite",
        "polished_diorite", "polished_granite", "bricks", "deepslate_tiles", "polished_deepslate", "cracked_stone_bricks",
        "stone_brick_slab", "smooth_stone_slab", "oak_planks", "spruce_planks", "dark_oak_planks", "concrete", "terracotta", "mud_bricks"}


def spot(g, rect, floor):
    """the column nearest the rectangle's middle whose top is hard ground within two of the floor level"""
    x0, z0, x1, z1 = rect
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    best = None
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            y, top = g.top(x, z)
            if y is None or abs(y - floor) > 2:
                continue
            name = (top or "").split(":")[-1]
            if not any(name == h or name.endswith("_" + h) for h in HARD):   # "_concrete", "_terracotta"; never "cobblestone" for "stone"
                continue
            d = (x - cx) ** 2 + (z - cz) ** 2
            if best is None or d < best[0]:
                best = (d, x, y + 1, z, name)
    return best


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    g = Ground(Path(argv[1]))
    FN.mkdir(parents=True, exist_ok=True)
    placed = {}
    for npc, (name, rect, floor) in NPCS.items():
        s = spot(g, rect, floor)
        if s is None:
            print(f"  {npc:9} no hard floor near {floor} in {rect}")
            continue
        _, x, y, z, ground = s
        nbt = ('{NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,'
               f'CustomName:\'{{"text":"{name}"}}\',Tags:["gscraft_npc","gscraft_npc_{npc}"],'
               'VillagerData:{profession:"minecraft:nitwit",level:1,type:"minecraft:plains"}}')
        lines = [f"kill @e[type=minecraft:villager,tag=gscraft_npc_{npc}]", f"summon minecraft:villager {x} {y} {z} {nbt}"]
        (FN / f"camp_npc_{npc}.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")
        placed[npc] = {"name": name, "x": x, "y": y, "z": z, "ground": ground}
        print(f"  {npc:9} ({x:5}, {y:3}, {z:5}) on {ground}")
    (FN / "camp_npcs.mcfunction").write_text("\n".join(f"function gscraft:camp_npc_{n}" for n in placed) + "\n", encoding="utf-8")
    (ROOT / "tools" / "camp_npcs.json").write_text(json.dumps(placed, indent=1), encoding="utf-8")
    print("wrote", len(placed), "survivor functions and camp_npcs")


if __name__ == "__main__":
    main(sys.argv)
