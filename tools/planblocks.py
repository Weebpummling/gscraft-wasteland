#!/usr/bin/env python3
"""
planblocks.py - list every block inside the transplant rectangles whose mod will not exist in the
rebuilt pack, so remap.json can be completed before the transplant runs.

    python planblocks.py --plan transplant_plan.json --live <live region dir> --old <old region dir> \
        --remap remap.json --out remap_todo.json
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import scanregion as sr  # noqa: E402

# Namespaces present in the rebuilt pack (blocks from these need no remap).
KEEP = {
    "minecraft", "immersiveengineering", "superbwarfare", "mcsp", "vvp", "tacz", "chaoszpack",
    "keerdm_zombie_essentials", "lostcities", "underground_bunkers", "factory_blocks", "chisel",
    "antiblocksrechiseled", "refurbished_furniture", "farmersdelight", "doomsday_decoration",
    "immersive_weathering", "hordes", "magnumtorch", "sophisticatedbackpacks", "sophisticatedcore",
    "playerrevive", "customstartinggear", "guardvillagers", "hostilevillages", "recruits",
    "zombieawareness", "incontrol", "mob_factions", "chaoszprojectbandits", "eyesinthedarkness",
    "the_knocker", "parcool", "bettercombat", "sedparties", "pillagers_gun", "lootr", "improvedmobs",
    "ftbchunks", "ftbquests", "xaerominimap", "xaeroworldmap", "immersiveaircraft", "mts", "kubejs",
    "voicechat", "apotheosis", "chipped", "worldedit", "lc2h",
}


def rects_for(plan, source):
    return [r["chunks"] for r in plan if r["source"] == source]


def scan(region_dir: Path, rects, per_ns: dict):
    inside = lambda cx, cz: any(r[0] <= cx <= r[2] and r[1] <= cz <= r[3] for r in rects)
    files = sorted(region_dir.glob("r.*.mca"))
    seen = 0
    for f in files:
        # Skip region files that cannot intersect any rectangle.
        rx, rz = (int(v) for v in f.name[2:-4].split("."))
        if not any(r[0] <= rx * 32 + 31 and r[2] >= rx * 32 and r[1] <= rz * 32 + 31 and r[3] >= rz * 32 for r in rects):
            continue
        for chunk in sr.read_region(f):
            cx, cz = chunk.get("xPos"), chunk.get("zPos")
            if cx is None or not inside(cx, cz):
                continue
            seen += 1
            for sec in chunk.get("sections", []):
                for name, n in sr.count_section(sec).items():
                    ns = name.split(":", 1)[0]
                    if ns not in KEEP:
                        per_ns[ns][name] += n
    return seen


def main(argv):
    a = dict(zip(argv[1::2], argv[2::2]))
    plan = json.loads(Path(a["--plan"]).read_text(encoding="utf-8"))
    remap = {k: v for k, v in json.loads(Path(a["--remap"]).read_text(encoding="utf-8")).items() if not k.startswith("_")}
    per_ns = defaultdict(Counter)
    n_live = scan(Path(a["--live"]), rects_for(plan, "live"), per_ns)
    n_old = scan(Path(a["--old"]), rects_for(plan, "old"), per_ns)
    print(f"chunks inspected: live {n_live}, old {n_old}")
    todo = {}
    print("\n=== BLOCKS FROM MODS NOT IN THE NEW PACK, INSIDE THE PLAN RECTANGLES ===")
    for ns in sorted(per_ns, key=lambda k: -sum(per_ns[k].values())):
        total = sum(per_ns[ns].values())
        mapped = sum(n for name, n in per_ns[ns].items() if name in remap)
        print(f"-- {ns}: {total} blocks, {len(per_ns[ns])} kinds, {mapped} already covered by remap.json")
        for name, n in per_ns[ns].most_common():
            flag = "   " if name in remap else "TODO"
            print(f"   {flag} {n:>9}  {name}")
            if name not in remap:
                todo[name] = n
    Path(a["--out"]).write_text(json.dumps(todo, indent=1), encoding="utf-8")
    print(f"\n{len(todo)} blocks still need a mapping -> {a['--out']}")


if __name__ == "__main__":
    main(sys.argv)
