"""Mark every generated chunk of a world as finished (Status minecraft:full). Chunks upgraded from 1.12 keep 'spawn' /
'empty' statuses; the terrain tools skip them (World.chunk) and the game treats them as unfinished.
usage: statusfix.py <world dir> [--dry-run]"""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import read_region_raw, write_region, R, W as NbtW

def main(a):
    world = Path(a[1]); dry = "--dry-run" in a; st = collections.Counter(); fixed = files = 0
    for f in sorted((world / "region").glob("r.*.mca")):
        reg = read_region_raw(f); changed = False
        for slot, (ts, comp, raw) in list(reg.items()):
            name, root = R(raw).root(); s = root.get("Status", (0, "?"))[1]; st[s] += 1
            if s in ("minecraft:full", "full"): continue
            secs = root.get("sections")
            if not secs or not any("block_states" in x for x in secs[1][1]): continue
            root["Status"] = (8, "minecraft:full"); reg[slot] = (ts, 2, NbtW().root(name, root)); fixed += 1; changed = True
        if changed and not dry: write_region(f, reg); files += 1
    print(f"statuses before: {dict(st)}; {fixed} chunks set to full in {files} files{' (dry)' if dry else ''}")

if __name__ == "__main__":
    main(sys.argv)
