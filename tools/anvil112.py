"""Reader for Forge 1.12.2 saves (pre-flattening: numeric block id + 4-bit metadata per block).

Names every block through the save's own registry (level.dat -> FML/Registries/minecraft:blocks),
so modded blocks keep their names instead of becoming "unknown id 2731".

usage:
  anvil112.py census  <save dir> <out prefix>      every (name, meta) with counts + per-chunk summary
  anvil112.py topdown <save dir> <out.png> [--scale N]   colour render of the top block, like topdown.py
  anvil112.py info    <save dir>                    version, mods, registry size

<save dir> is the world folder holding level.dat and region/. Overworld only.
Output of census:
  <prefix>_blocks.json   [{"name","meta","count"}] sorted by count, plus namespace totals
  <prefix>_chunks.json   {"cx,cz": {"nonair","vanilla","modded","tiles":{id:n},"top_ns":[...]}}
  <prefix>_blocks.txt    the same census as a readable table (namespace, then name, then meta)
"""
import sys, json, gzip, collections
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from transplant import R, read_region_raw          # NBT reader + region file reader (format unchanged since 1.2)

T_LIST, T_COMPOUND = 9, 10
AIR_ID = 0
# 1.12 vanilla blocks that are terrain, for the "built" count (by name, no namespace)
NATURAL112 = {"stone", "grass", "dirt", "sand", "gravel", "water", "flowing_water", "lava", "flowing_lava",
              "bedrock", "sandstone", "clay", "snow_layer", "snow", "ice", "packed_ice", "leaves", "leaves2",
              "log", "log2", "tallgrass", "double_plant", "red_flower", "yellow_flower", "brown_mushroom",
              "red_mushroom", "cactus", "reeds", "vine", "waterlily", "deadbush", "web", "mycelium",
              "netherrack", "soul_sand", "end_stone", "obsidian", "coal_ore", "iron_ore", "gold_ore",
              "diamond_ore", "redstone_ore", "lapis_ore", "emerald_ore", "quartz_ore", "glowstone",
              "hardened_clay", "stained_hardened_clay", "monster_egg", "magma", "sapling", "cocoa", "pumpkin",
              "melon_block", "grass_path", "farmland", "cobblestone", "mossy_cobblestone", "air"}


# worldgen strata / plants from the mods in this pack: terrain, never "placed"
TERRAIN_MOD_PREFIX = ("hbm:ore_", "hbm:cluster_", "hbm:gas_", "hbm:stone_depth", "hbm:stone_gneiss", "hbm:block_meteor",
                      "hbm:meteor_", "hbm:ore_depth", "hbm:sellafield", "hbm:waste_", "hbm:grass_dead", "hbm:mycelium",
                      "mw:", "immersiveengineering:ore", "dynamictrees", "biomesoplenty:", "sereneseasons:",
                      "chisel:marble2", "chisel:limestone2", "chisel:basalt2", "harvestcraft:", "randomportals:",
                      "twilightforest:twilight_leaves", "twilightforest:twilight_log", "twilightforest:magic_",
                      "futuremc:")
TERRAIN_MOD_EXACT = {"immersiveengineering:ore"}


def is_terrain(name: str) -> bool:
    ns, _, path = name.partition(":")
    if ns == "minecraft":
        return path in NATURAL112
    if ns == "unknown":
        return False
    return name in TERRAIN_MOD_EXACT or name.startswith(TERRAIN_MOD_PREFIX)


def read_level(save: Path):
    raw = gzip.decompress((save / "level.dat").read_bytes())
    _, root = R(raw).root()
    return root


def registry(root) -> dict:
    """{numeric id: 'namespace:name'} from the FML block registry in level.dat."""
    fml = root.get("FML", (0, {}))[1]
    regs = fml.get("Registries", (0, {}))[1]
    blocks = regs.get("minecraft:blocks", (0, {}))[1]
    ids = blocks.get("ids", (0, (0, [])))[1][1]
    out = {}
    for e in ids:
        out[e["V"][1]] = e["K"][1]
    return out


def info(save: Path):
    root = read_level(save)
    d = root["Data"][1]
    ver = d.get("Version", (0, {}))[1]
    mods = root.get("FML", (0, {}))[1].get("ModList", (0, (0, [])))[1][1]
    reg = registry(root)
    ns = collections.Counter(n.split(":")[0] for n in reg.values())
    print(f"{save.name}: {d['LevelName'][1]!r} DataVersion {d.get('DataVersion', (0, '?'))[1]} "
          f"({ver.get('Name', (0, '?'))[1]}), generator {d.get('generatorName', (0, '?'))[1]}, "
          f"spawn {d['SpawnX'][1]} {d['SpawnY'][1]} {d['SpawnZ'][1]}")
    print(f"  mods {len(mods)}, registered blocks {len(reg)}; namespaces: {dict(ns.most_common(12))}")
    return root


def nibbles(b: bytes) -> np.ndarray:
    """2048 packed nibbles -> 4096 uint8 values, low nibble first."""
    a = np.frombuffer(b, dtype=np.uint8)
    out = np.empty(a.size * 2, dtype=np.uint8)
    out[0::2] = a & 0x0F
    out[1::2] = a >> 4
    return out


def decode_section(sec: dict):
    """-> (ids uint16[4096], meta uint8[4096]) in YZX order (index = y*256 + z*16 + x)."""
    blocks = np.frombuffer(sec["Blocks"][1], dtype=np.uint8).astype(np.uint16)
    if "Add" in sec:
        blocks = blocks | (nibbles(sec["Add"][1]).astype(np.uint16) << 8)
    meta = nibbles(sec["Data"][1]) if "Data" in sec else np.zeros(4096, dtype=np.uint8)
    return blocks, meta


def iter_chunks(save: Path):
    """Yield (cx, cz, level_compound) for every chunk in <save>/region."""
    for f in sorted((save / "region").glob("r.*.mca")):
        for slot, (ts, comp, raw) in read_region_raw(f).items():
            try:
                _, root = R(raw).root()
            except Exception:
                continue
            level = root.get("Level", (0, None))[1]
            if not level:
                continue
            yield level["xPos"][1], level["zPos"][1], level


def sections(level):
    return [s for s in level.get("Sections", (0, (0, [])))[1][1]]


# ------------------------------------------------------------------------------------------ census

def census(save: Path, prefix: str):
    root = info(save)
    reg = registry(root)
    names = np.array([reg.get(i, f"unknown:id{i}") for i in range(4096)], dtype=object)
    counts = collections.Counter()      # (id, meta) -> n
    terrain = np.array([is_terrain(n) for n in names], dtype=bool)
    chunks = {}
    nchunks = 0
    for cx, cz, level in iter_chunks(save):
        nchunks += 1
        tot = van = mod = placed = 0
        nsc = collections.Counter(); pl = collections.Counter()
        for sec in sections(level):
            ids, meta = decode_section(sec)
            keep = ids != AIR_ID
            if not keep.any():
                continue
            key = (ids[keep].astype(np.uint32) << 4) | meta[keep]
            u, c = np.unique(key, return_counts=True)
            for k, n in zip(u.tolist(), c.tolist()):
                counts[(k >> 4, k & 15)] += n
                nm = names[k >> 4]
                ns = nm.split(":")[0]
                nsc[ns] += n
                tot += n
                if ns == "minecraft":
                    van += n
                else:
                    mod += n
                if not terrain[k >> 4]:
                    placed += n; pl[nm] += n
        tiles = collections.Counter(te.get("id", (0, "?"))[1] for te in level.get("TileEntities", (0, (0, [])))[1][1])
        chunks[f"{cx},{cz}"] = {"nonair": tot, "vanilla": van, "modded": mod, "placed": placed,
                                "tiles": dict(tiles), "top_ns": [n for n, _ in nsc.most_common(4)],
                                "top_placed": [n for n, _ in pl.most_common(4)]}
    rows = [{"name": names[i], "meta": m, "count": n} for (i, m), n in counts.most_common()]
    by_ns = collections.Counter()
    for r in rows:
        by_ns[r["name"].split(":")[0]] += r["count"]
    json.dump({"save": save.name, "chunks": nchunks, "distinct": len(rows),
               "namespaces": dict(by_ns.most_common()), "blocks": rows},
              open(prefix + "_blocks.json", "w"), indent=1)
    json.dump(chunks, open(prefix + "_chunks.json", "w"))
    with open(prefix + "_blocks.txt", "w", encoding="utf-8") as fh:
        fh.write(f"{save.name}: {nchunks} chunks, {sum(by_ns.values()):,} non-air blocks, {len(rows)} distinct (name, meta)\n\n")
        fh.write("namespace totals\n")
        for ns, n in by_ns.most_common():
            fh.write(f"  {n:>12,}  {ns}\n")
        fh.write("\nblocks (count, name, meta)\n")
        for r in sorted(rows, key=lambda r: (r["name"].split(":")[0] != "minecraft", -r["count"])):
            fh.write(f"  {r['count']:>12,}  {r['name']}  [{r['meta']}]\n")
    modded = sum(n for ns, n in by_ns.items() if ns != "minecraft")
    print(f"  {nchunks} chunks, {sum(by_ns.values()):,} non-air blocks, {len(rows)} distinct; "
          f"modded {modded:,} ({100 * modded / max(1, sum(by_ns.values())):.1f}%)")
    print(f"  top namespaces: {dict(by_ns.most_common(8))}")
    print(f"  -> {prefix}_blocks.json / _chunks.json / _blocks.txt")


# ----------------------------------------------------------------------------------------- topdown

# 1.12 names -> a 1.20-style name the topdown.py colour table understands (render only, not a remap)
COLOUR_ALIAS = {
    "minecraft:grass": "minecraft:grass_block", "minecraft:tallgrass": "minecraft:grass",
    "minecraft:double_plant": "minecraft:grass", "minecraft:stained_hardened_clay": "minecraft:terracotta",
    "minecraft:hardened_clay": "minecraft:terracotta", "minecraft:log": "minecraft:oak_log",
    "minecraft:log2": "minecraft:oak_log", "minecraft:leaves": "minecraft:oak_leaves",
    "minecraft:leaves2": "minecraft:oak_leaves", "minecraft:flowing_water": "minecraft:water",
    "minecraft:flowing_lava": "minecraft:lava", "minecraft:snow_layer": "minecraft:snow",
    "minecraft:stonebrick": "minecraft:stone_bricks", "minecraft:brick_block": "minecraft:bricks",
    "minecraft:quartz_block": "minecraft:quartz", "minecraft:concrete": "minecraft:gray_concrete",
    "minecraft:concrete_powder": "minecraft:gray_concrete", "minecraft:iron_block": "minecraft:iron_block",
    "minecraft:stained_glass": "minecraft:glass", "minecraft:glass_pane": "minecraft:glass",
    "minecraft:stone_slab": "minecraft:stone", "minecraft:double_stone_slab": "minecraft:stone",
    "minecraft:stone_stairs": "minecraft:cobblestone", "minecraft:mycelium": "minecraft:moss",
    "minecraft:grass_path": "minecraft:dirt", "minecraft:farmland": "minecraft:dirt",
    "biomesoplenty:grass": "minecraft:grass_block", "biomesoplenty:dirt": "minecraft:dirt",
    "biomesoplenty:dried_sand": "minecraft:sand", "biomesoplenty:plant_0": "minecraft:grass",
    "biomesoplenty:leaves_0": "minecraft:oak_leaves", "biomesoplenty:leaves_1": "minecraft:oak_leaves",
    "biomesoplenty:leaves_2": "minecraft:oak_leaves", "biomesoplenty:leaves_3": "minecraft:oak_leaves",
    "biomesoplenty:leaves_4": "minecraft:oak_leaves", "biomesoplenty:leaves_5": "minecraft:oak_leaves",
    "biomesoplenty:leaves_6": "minecraft:oak_leaves", "biomesoplenty:log_0": "minecraft:oak_log",
    "biomesoplenty:log_1": "minecraft:oak_log", "biomesoplenty:log_2": "minecraft:oak_log",
    "biomesoplenty:log_3": "minecraft:oak_log", "biomesoplenty:log_4": "minecraft:oak_log",
    "biomesoplenty:mud": "minecraft:mud", "biomesoplenty:white_sand": "minecraft:sand",
    "chisel:marble2": "minecraft:stone", "chisel:limestone2": "minecraft:stone", "chisel:basalt2": "minecraft:basalt",
    "chisel:antiblock": "minecraft:white_concrete", "chisel:factory": "minecraft:factory",
    "chisel:factory1": "minecraft:factory", "furenikusroads:generic_blocks": "minecraft:black_concrete",
    "hbm:stone_depth": "minecraft:deepslate", "hbm:brick_concrete": "minecraft:gray_concrete",
    "hbm:brick_concrete_mossy": "minecraft:gray_concrete", "hbm:brick_concrete_cracked": "minecraft:gray_concrete",
    "hbm:brick_concrete_broken": "minecraft:gray_concrete", "hbm:deco_steel": "minecraft:sheetmetal",
    "hbm:steel_wall": "minecraft:sheetmetal", "hbm:brick_light": "minecraft:light_gray_concrete",
    "hbm:reinforced_light": "minecraft:light_gray_concrete", "hbm:concrete": "minecraft:gray_concrete",
    "hbm:concrete_smooth": "minecraft:light_gray_concrete", "hbm:asphalt": "minecraft:black_concrete",
    "immersiveengineering:stone_decoration": "minecraft:gray_concrete", "immersiveengineering:sheetmetal": "minecraft:sheetmetal",
    "immersiveengineering:ore": "minecraft:stone", "dynamictrees:leaves0": "minecraft:oak_leaves",
    "dynamictrees:leaves1": "minecraft:oak_leaves", "dynamictrees:oakbranch": "minecraft:oak_log",
    "dynamictrees:sprucebranch": "minecraft:oak_log", "dynamictrees:birchbranch": "minecraft:oak_log",
}
_ORE_NS = ("hbm:ore_", "hbm:cluster_", "hbm:gas_", "mw:", "immersiveengineering:ore")


def colour_name(name: str) -> str:
    a = COLOUR_ALIAS.get(name)
    if a: return a
    if name.startswith(_ORE_NS) and name.endswith("ore") or name.startswith(("hbm:ore_", "hbm:cluster_", "hbm:gas_")):
        return "minecraft:stone"
    if name.startswith("furenikusroads:"): return "minecraft:black_concrete"
    if name.startswith("chisel:"): return "minecraft:light_gray_concrete"
    if name.startswith("hbm:"): return "minecraft:gray_concrete"
    if name.startswith("dynamictrees"): return "minecraft:oak_leaves"
    if name.startswith("biomesoplenty:") and ("leaves" in name or "plant" in name or "flower" in name): return "minecraft:oak_leaves"
    return name


def topdown(save: Path, out: str, scale: int = 1):
    from topdown import colour_of as _colour_of
    from PIL import Image
    def colour_of(name, cache={}):
        c = cache.get(name)
        if c is None:
            c = cache[name] = _colour_of(colour_name(name))
        return c
    root = read_level(save)
    reg = registry(root)
    names = [reg.get(i, f"unknown:id{i}") for i in range(4096)]
    tiles = {}
    for cx, cz, level in iter_chunks(save):
        secs = []
        for sec in sections(level):
            ids, _ = decode_section(sec)
            if (ids != AIR_ID).any():
                secs.append((sec["Y"][1], ids.reshape(16, 16, 16)))    # [y][z][x]
        if not secs:
            continue
        secs.sort(key=lambda t: -t[0])
        img = np.zeros((16, 16, 3), dtype=np.uint8); done = np.zeros((16, 16), dtype=bool)
        for y, arr in secs:
            if done.all():
                break
            solid = arr != AIR_ID
            top = np.where(solid.any(axis=0), 15 - np.argmax(solid[::-1], axis=0), -1)
            for z in range(16):
                for x in range(16):
                    if done[z, x] or top[z, x] < 0:
                        continue
                    img[z, x] = colour_of(names[arr[top[z, x], z, x]]); done[z, x] = True
        tiles[(cx, cz)] = img
    if not tiles:
        print("no chunks"); return
    xs = [k[0] for k in tiles]; zs = [k[1] for k in tiles]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    W, H = (x1 - x0 + 1) * 16, (z1 - z0 + 1) * 16
    img = np.full((H, W, 3), 236, dtype=np.uint8)
    for (cx, cz), t in tiles.items():
        img[(cz - z0) * 16:(cz - z0 + 1) * 16, (cx - x0) * 16:(cx - x0 + 1) * 16] = t
    for gx in range((x0 // 32) * 32, x1 + 1, 32):
        if x0 <= gx <= x1: img[:, (gx - x0) * 16] = (255, 255, 0)
    for gz in range((z0 // 32) * 32, z1 + 1, 32):
        if z0 <= gz <= z1: img[(gz - z0) * 16, :] = (255, 255, 0)
    if scale > 1:
        img = img[:H // scale * scale, :W // scale * scale].reshape(H // scale, scale, W // scale, scale, 3).mean(axis=(1, 3)).astype(np.uint8)
    Image.fromarray(img).save(out)
    json.dump({"chunk_origin": [x0, z0], "chunk_max": [x1, z1], "scale": scale}, open(out + ".json", "w"))
    print(f"{out}: chunks x {x0}..{x1} z {z0}..{z1}, image {img.shape[1]}x{img.shape[0]} at 1px per {scale} blocks")


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    verb, save = argv[1], Path(argv[2])
    if verb == "info":
        info(save)
    elif verb == "census":
        census(save, argv[3])
    elif verb == "topdown":
        scale = int(argv[argv.index("--scale") + 1]) if "--scale" in argv else 1
        topdown(save, argv[3], scale)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
