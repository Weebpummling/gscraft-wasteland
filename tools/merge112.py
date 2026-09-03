"""Merge the modded layer of a 1.12.2 build volume into its vanilla-upgraded 1.20.1 world.

usage: merge112.py <volume.npz> <upgraded world dir> [--remap remap112.json] [--reports <dir>]

The upgraded world (from upgrade112.py) has every vanilla block flattened exactly and every modded
block as air. For every position the volume marks as modded, this writes the block the remap
table gives (properties allowed: "minecraft:oak_slab[type=top]"); "air" leaves air. Block entities
whose type is not a vanilla block-entity type are dropped (the DFU keeps them as junk NBT).
Every target is validated against the vanilla block report and the pack's mod blockstates
(reports dir: generated/reports/blocks.json + mod_blocks.json); a target that does not exist
becomes the placeholder and is listed, so the table can be fixed.

Region files are rewritten in place inside the upgraded world. Run once per volume.
"""
import sys, json, collections
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from transplant import R, W, read_region_raw, write_region, region_of, slot_of, T_BYTE, T_LIST, T_COMPOUND, T_STRING, T_INT
from anvil import Chunk, decode, encode
from makeremap112 import resolve

DEFAULT_REPORTS = Path(r"G:/GSCraft/scratch/reports")


def parse_target(t: str):
    if t == "air": return "minecraft:air", {}
    if "[" in t:
        name, rest = t[:-1].split("[", 1)
        props = dict(kv.split("=", 1) for kv in rest.split(",") if kv)
        return name, props
    return t, {}


def load_valid(reports: Path):
    valid = set(json.load(open(reports / "generated/reports/blocks.json")).keys())
    mods = json.load(open(reports / "mod_blocks.json"))
    for ns, names in mods.items():
        valid |= {f"{ns}:{n}" for n in names}
    reg = json.load(open(reports / "generated/reports/registries.json"))
    bes = set(reg["minecraft:block_entity_type"]["entries"].keys())
    return valid, bes


def ensure_section(root, y, template):
    """Add an all-air section Y=y to the chunk root, copying biomes from a template section."""
    secs = root["sections"][1][1]
    sec = {"Y": (T_BYTE, y),
           "block_states": (T_COMPOUND, {"palette": (T_LIST, (T_COMPOUND, [{"Name": (T_STRING, "minecraft:air")}]))})}
    if template is not None and "biomes" in template:
        sec["biomes"] = template["biomes"]
    else:
        sec["biomes"] = (T_COMPOUND, {"palette": (T_LIST, (T_STRING, ["minecraft:plains"]))})
    secs.append(sec)
    secs.sort(key=lambda s: s["Y"][1])
    return sec


def main(argv):
    if len(argv) < 3: sys.exit(__doc__)
    vol = Path(argv[1]); world = Path(argv[2])
    remap = Path(argv[argv.index("--remap") + 1]) if "--remap" in argv else Path(__file__).parent / "remap112.json"
    reports = Path(argv[argv.index("--reports") + 1]) if "--reports" in argv else DEFAULT_REPORTS
    valid, be_types = load_valid(reports)
    table = json.load(open(remap)); resolved = table["resolved"]; placeholder = table["placeholder"]
    # --rect rects.json <name>: apply the rect's y_max / exclude_sky to the UPGRADED chunks too, so
    # vanilla blocks the y-cut removed from the volume (the ships) are cleared here as well
    y_max, excl = 255, []
    if "--rect" in argv:
        rects = json.load(open(argv[argv.index("--rect") + 1])); rr = rects[argv[argv.index("--rect") + 2]]
        y_max = rr.get("y_max", 255); excl = [(e["blocks"], e.get("y_min", 0)) for e in rr.get("exclude_sky", [])]
    def cut_mask(cx, cz, y):
        """bool[4096] of positions in section (cx,cz,y) that the rect cuts."""
        yy = (np.arange(4096) >> 8) + y * 16; xx = (np.arange(4096) & 15) + cx * 16; zz = ((np.arange(4096) >> 4) & 15) + cz * 16
        m = yy > y_max
        for (ex0, ez0, ex1, ez1), ymin in excl:
            m |= (xx >= ex0) & (xx <= ex1) & (zz >= ez0) & (zz <= ez1) & (yy >= ymin)
        return m
    cleared = 0
    v = np.load(vol, allow_pickle=True)
    names = v["names"]; keys = v["keys"]; ids = v["ids"]; meta = v["meta"]; mod = v["modded"]
    region_dir = world / "region"
    # group volume sections by chunk
    per_chunk = collections.defaultdict(list)
    for n, (cx, cz, y) in enumerate(keys.tolist()):
        per_chunk[(cx, cz)].append(n)
    # group chunks by region
    per_region = collections.defaultdict(list)
    for (cx, cz) in per_chunk:
        per_region[region_of(cx, cz)].append((cx, cz))
    written = collections.Counter(); missing = collections.Counter(); dropped_be = collections.Counter(); kept_be = 0
    no_chunk = 0; created = 0; tgt_cache = {}
    for (rx, rz), chunks_here in sorted(per_region.items()):
        path = region_dir / f"r.{rx}.{rz}.mca"
        raw = read_region_raw(path)
        changed = False
        for (cx, cz) in chunks_here:
            slot = slot_of(cx, cz)
            if slot not in raw:
                no_chunk += 1; continue
            ts, comp, blob = raw[slot]
            name, root = R(blob).root()
            ch = Chunk(root)
            template = next(iter(root["sections"][1][1]), None)
            for n in per_chunk[(cx, cz)]:
                y = int(keys[n][2]); mm = mod[n]
                if not mm.any(): continue
                if y not in ch.secs:
                    sec = ensure_section(root, y, template); ch.secs[y] = [sec, ["minecraft:air"], sec["block_states"][1]["palette"][1][1], [0] * 4096, False]; created += 1
                sec_ids = ids[n]; sec_meta = meta[n]
                for i in np.nonzero(mm)[0].tolist():
                    key = f"{names[sec_ids[i]]}[{int(sec_meta[i])}]"
                    tgt = resolved.get(key)
                    if tgt is None:
                        # not in the worklist (terrain families) -> the table's own rules
                        tgt, why = resolve(names[sec_ids[i]], int(sec_meta[i]))
                        resolved[key] = tgt
                        if why == "unmapped": missing[key] += 1
                    t = tgt_cache.get(tgt)
                    if t is None:
                        bn, props = parse_target(tgt)
                        if bn not in valid:
                            missing[f"TARGET {tgt}"] += 1; bn, props = placeholder, {}
                        t = tgt_cache[tgt] = (bn, props)
                    bn, props = t
                    if bn == "minecraft:air": continue
                    x, z = i & 15, (i >> 4) & 15
                    ch.set(x, y * 16 + (i >> 8), z, bn, props or None)
                    written[bn] += 1
            # the y-cut / exclusion boxes, applied to every section of the chunk (ships were vanilla blocks)
            if y_max < 255 or excl:
                for sy, s in list(ch.secs.items()):
                    m = cut_mask(cx, cz, sy)
                    if not m.any(): continue
                    sec, snames, pal, idx, _ = s
                    air_i = next((i for i, p in enumerate(pal) if p["Name"][1] == "minecraft:air"), None)
                    if air_i is None:
                        pal.append({"Name": (T_STRING, "minecraft:air")}); snames.append("minecraft:air"); air_i = len(pal) - 1
                    for i in np.nonzero(m)[0].tolist():
                        if idx[i] != air_i and snames[idx[i]] != "minecraft:air":
                            idx[i] = air_i; cleared += 1
                    s[4] = True
            # block entities: keep vanilla types only, and none in the cut
            bes = root.get("block_entities")
            if bes:
                keep = []
                for be in bes[1][1]:
                    bid = be.get("id", (0, "?"))[1]
                    bx, by, bz = be.get("x", (0, 0))[1], be.get("y", (0, 0))[1], be.get("z", (0, 0))[1]
                    in_cut = by > y_max or any(ex0 <= bx <= ex1 and ez0 <= bz <= ez1 and by >= ymin for (ex0, ez0, ex1, ez1), ymin in excl)
                    if bid in be_types and not in_cut: keep.append(be); kept_be += 1
                    else: dropped_be[bid if bid not in be_types else "cut"] += 1
                root["block_entities"] = (T_LIST, (T_COMPOUND, keep))
            ch.commit()
            w = W(); w.root(name, root)
            raw[slot] = (ts, 2, bytes(w.out))
            changed = True
        if changed:
            write_region(path, raw)
    tot = sum(written.values())
    print(f"{vol.name}: wrote {tot:,} modded blocks into {world}; sections created {created}; chunks absent {no_chunk}")
    print("  top targets:", ", ".join(f"{k.split(':')[-1]}={v:,}" for k, v in written.most_common(12)))
    print(f"  block entities kept {kept_be}, dropped {sum(dropped_be.values())} ({', '.join(f'{k}={v}' for k, v in dropped_be.most_common(6))})")
    if missing:
        print(f"  MISSING ({sum(missing.values()):,} blocks -> placeholder):")
        for k, c in missing.most_common(20): print(f"    {c:>8,}  {k}")


if __name__ == "__main__":
    main(sys.argv)
