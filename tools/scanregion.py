#!/usr/bin/env python3
"""
scanregion.py - find player builds in Minecraft Anvil region files and list the mods they depend on.

    python scanregion.py <dir-with-.mca-files> [more dirs...] [--out report.txt]

Reads every r.X.Z.mca (1.18+ chunk format), decodes each section's block palette, and reports:
  * every non-vanilla block namespace with a block count (the mod dependencies of what is built)
  * the top chunks by "built" signal - many distinct block types, modded blocks, block entities -
    with block coordinates, so builds can be located and copied.

No third-party NBT library: the parser below is the whole of what is needed for this job.
Uses numpy for unpacking block-state bit arrays when it is available; falls back to a slower path.
"""

import gzip
import struct
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

# Blocks that occur naturally and say nothing about building. Anything else that is non-vanilla,
# or vanilla but clearly placed (stairs, slabs, glass, concrete, wool, doors...), counts as "built".
NATURAL = {
    "minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:stone", "minecraft:dirt",
    "minecraft:grass_block", "minecraft:water", "minecraft:lava", "minecraft:bedrock", "minecraft:gravel",
    "minecraft:sand", "minecraft:sandstone", "minecraft:deepslate", "minecraft:tuff", "minecraft:andesite",
    "minecraft:diorite", "minecraft:granite", "minecraft:coal_ore", "minecraft:iron_ore", "minecraft:copper_ore",
    "minecraft:gold_ore", "minecraft:redstone_ore", "minecraft:lapis_ore", "minecraft:diamond_ore",
    "minecraft:emerald_ore", "minecraft:deepslate_coal_ore", "minecraft:deepslate_iron_ore",
    "minecraft:deepslate_copper_ore", "minecraft:deepslate_gold_ore", "minecraft:deepslate_redstone_ore",
    "minecraft:deepslate_lapis_ore", "minecraft:deepslate_diamond_ore", "minecraft:deepslate_emerald_ore",
    "minecraft:snow", "minecraft:snow_block", "minecraft:ice", "minecraft:packed_ice", "minecraft:clay",
    "minecraft:oak_log", "minecraft:oak_leaves", "minecraft:birch_log", "minecraft:birch_leaves",
    "minecraft:spruce_log", "minecraft:spruce_leaves", "minecraft:jungle_log", "minecraft:jungle_leaves",
    "minecraft:acacia_log", "minecraft:acacia_leaves", "minecraft:dark_oak_log", "minecraft:dark_oak_leaves",
    "minecraft:short_grass", "minecraft:grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern",
    "minecraft:seagrass", "minecraft:tall_seagrass", "minecraft:kelp", "minecraft:kelp_plant", "minecraft:vine",
    "minecraft:dead_bush", "minecraft:cactus", "minecraft:sugar_cane", "minecraft:pumpkin", "minecraft:melon",
    "minecraft:podzol", "minecraft:coarse_dirt", "minecraft:rooted_dirt", "minecraft:mud", "minecraft:moss_block",
    "minecraft:calcite", "minecraft:dripstone_block", "minecraft:pointed_dripstone", "minecraft:amethyst_block",
    "minecraft:budding_amethyst", "minecraft:obsidian", "minecraft:magma_block", "minecraft:netherrack",
    "minecraft:soul_sand", "minecraft:soul_soil", "minecraft:basalt", "minecraft:blackstone", "minecraft:end_stone",
    "minecraft:mossy_cobblestone", "minecraft:cobblestone", "minecraft:infested_stone", "minecraft:glow_lichen",
    "minecraft:red_sand", "minecraft:red_sandstone", "minecraft:terracotta", "minecraft:mycelium",
    "minecraft:brown_mushroom", "minecraft:red_mushroom", "minecraft:lily_pad", "minecraft:bamboo",
    "minecraft:sweet_berry_bush", "minecraft:spore_blossom", "minecraft:azalea", "minecraft:flowering_azalea",
    "minecraft:hanging_roots", "minecraft:cave_vines", "minecraft:cave_vines_plant", "minecraft:sculk",
    "minecraft:sculk_vein", "minecraft:mangrove_log", "minecraft:mangrove_leaves", "minecraft:mangrove_roots",
    "minecraft:cherry_log", "minecraft:cherry_leaves", "minecraft:dandelion", "minecraft:poppy",
    "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:azure_bluet", "minecraft:blue_orchid",
    "minecraft:allium", "minecraft:lilac", "minecraft:rose_bush", "minecraft:peony", "minecraft:sunflower",
}
# Lost Cities and worldgen mods generate with modded blocks too; their namespaces are generation, not building.
import re
# Ores and worldgen stones from mods: present everywhere underground, irrelevant to what was built.
ORE_RE = re.compile(r"(_ore$|_ore_|:ore_|:raw_|:(limestone|ochrum|asurine|scoria|crimsite|veridium|silt"
                    r"|bauxite|tar|deadrock|cracked_deadrock|steellium_ore)$)")
GENERATED_NAMESPACES = {"lostcities", "alexscaves", "twilightforest", "immersive_weathering", "underground_bunkers",
                        "fromthecaves", "backrooms", "keerdm_zombie_essentials", "chaoszpack", "chaoszpack_structures"}


# ----------------------------------------------------------------------------- minimal NBT


class NBTReader:
    __slots__ = ("b", "i")

    def __init__(self, data: bytes):
        self.b, self.i = data, 0

    def u8(self):
        v = self.b[self.i]; self.i += 1; return v

    def i16(self):
        v = struct.unpack_from(">h", self.b, self.i)[0]; self.i += 2; return v

    def i32(self):
        v = struct.unpack_from(">i", self.b, self.i)[0]; self.i += 4; return v

    def i64(self):
        v = struct.unpack_from(">q", self.b, self.i)[0]; self.i += 8; return v

    def string(self):
        n = struct.unpack_from(">H", self.b, self.i)[0]; self.i += 2
        s = self.b[self.i:self.i + n].decode("utf-8", "replace"); self.i += n; return s

    def payload(self, t):
        if t == 1: return self.u8() if self.b[self.i] < 128 else self.u8() - 256
        if t == 2: return self.i16()
        if t == 3: return self.i32()
        if t == 4: return self.i64()
        if t == 5: v = struct.unpack_from(">f", self.b, self.i)[0]; self.i += 4; return v
        if t == 6: v = struct.unpack_from(">d", self.b, self.i)[0]; self.i += 8; return v
        if t == 7:
            n = self.i32(); v = self.b[self.i:self.i + n]; self.i += n; return v
        if t == 8: return self.string()
        if t == 9:
            et = self.u8(); n = self.i32()
            return [self.payload(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                et = self.u8()
                if et == 0: return d
                name = self.string(); d[name] = self.payload(et)
        if t == 11:
            n = self.i32(); v = struct.unpack_from(f">{n}i", self.b, self.i); self.i += 4 * n; return list(v)
        if t == 12:
            n = self.i32()
            raw = self.b[self.i:self.i + 8 * n]; self.i += 8 * n
            return raw  # keep packed; decoded lazily with numpy
        raise ValueError(f"bad tag {t}")

    def root(self):
        t = self.u8(); assert t == 10, "root is not a compound"
        self.string(); return self.payload(10)


def read_region(path: Path):
    data = path.read_bytes()
    if len(data) < 8192:
        return
    for idx in range(1024):
        off = struct.unpack_from(">I", data, idx * 4)[0]
        sectors, offset = off & 0xFF, off >> 8
        if offset == 0 or sectors == 0:
            continue
        start = offset * 4096
        length = struct.unpack_from(">I", data, start)[0]
        comp = data[start + 4]
        blob = data[start + 5:start + 4 + length]
        try:
            raw = zlib.decompress(blob) if comp == 2 else gzip.decompress(blob) if comp == 1 else blob
            yield NBTReader(raw).root()
        except Exception as exc:  # corrupt chunk: report, keep going
            print(f"  ! {path.name} slot {idx}: {exc}", file=sys.stderr)


# ----------------------------------------------------------------------------- block counting


def count_section(sec):
    """Return Counter{block name: count} for one 16x16x16 section."""
    bs = sec.get("block_states")
    if not bs:
        return Counter()
    palette = [p.get("Name", "?") for p in bs.get("palette", [])]
    if len(palette) == 1:
        return Counter({palette[0]: 4096})
    packed = bs.get("data")
    if packed is None:
        return Counter({palette[0]: 4096})
    bits = max(4, (len(palette) - 1).bit_length())
    per_long = 64 // bits
    if np is not None:
        longs = np.frombuffer(packed, dtype=">u8")
        shifts = np.arange(per_long, dtype=np.uint64) * np.uint64(bits)
        idx = ((longs[:, None] >> shifts[None, :]) & np.uint64((1 << bits) - 1)).ravel()[:4096]
        counts = np.bincount(idx.astype(np.int64), minlength=len(palette))
        return Counter({palette[i]: int(c) for i, c in enumerate(counts) if c and i < len(palette)})
    out = Counter()
    mask = (1 << bits) - 1
    n = 0
    for k in range(0, len(packed), 8):
        v = int.from_bytes(packed[k:k + 8], "big")
        for _ in range(per_long):
            if n >= 4096:
                break
            i = v & mask
            if i < len(palette):
                out[palette[i]] += 1
            v >>= bits; n += 1
    return out


def scan_dir(d: Path, ns_counts: Counter, block_counts: Counter, chunks: list, placed_ns: Counter, placed_blocks: Counter):
    files = sorted(d.glob("r.*.mca"))
    print(f"{d}: {len(files)} region files")
    for f in files:
        for chunk in read_region(f):
            cx, cz = chunk.get("xPos"), chunk.get("zPos")
            if cx is None:
                continue
            built = Counter()
            total_types = set()
            for sec in chunk.get("sections", []):
                c = count_section(sec)
                for name, n in c.items():
                    total_types.add(name)
                    ns = name.split(":", 1)[0]
                    if ns != "minecraft":
                        ns_counts[ns] += n
                        block_counts[name] += n
                    if name not in NATURAL and ns not in GENERATED_NAMESPACES and not ORE_RE.search(name):
                        built[name] += n
                        if ns != "minecraft":
                            placed_ns[ns] += n
                            placed_blocks[name] += n
            bes = chunk.get("block_entities", [])
            placed = sum(built.values())
            fill = (built.most_common(1)[0][1] / placed) if placed else 0.0
            score = min(placed, 3000) + 20 * len(bes) + 15 * len(total_types)
            if fill > 0.85 and placed > 2000:
                score //= 10  # mostly one block: worldgen or a mass fill, not a build
            if built or bes:
                label = "/".join(d.parts[-3:-1])
                chunks.append((score, label, f.name, cx, cz, placed, len(bes), len(total_types), round(fill, 2),
                               built.most_common(6), Counter(b.get("id", "?") for b in bes).most_common(4)))


def main(argv):
    out = None
    dirs = []
    i = 1
    while i < len(argv):
        if argv[i] == "--out":
            out = Path(argv[i + 1]); i += 2; continue
        dirs.append(Path(argv[i])); i += 1
    if not dirs:
        sys.exit(__doc__)
    ns_counts, block_counts, chunks = Counter(), Counter(), []
    placed_ns, placed_blocks = Counter(), Counter()
    for d in dirs:
        scan_dir(d, ns_counts, block_counts, chunks, placed_ns, placed_blocks)
    chunks.sort(reverse=True)
    lines = []
    lines.append("=== PLACED-BLOCK DEPENDENCIES (non-vanilla blocks that are not ores, stones or worldgen) ===")
    for ns, n in placed_ns.most_common():
        lines.append(f"{n:>10}  {ns}")
    lines.append("")
    lines.append("=== TOP 50 PLACED NON-VANILLA BLOCKS ===")
    for name, n in placed_blocks.most_common(50):
        lines.append(f"{n:>10}  {name}")
    lines.append("")
    lines.append("=== NON-VANILLA BLOCK NAMESPACES (dependencies of everything in these regions) ===")
    for ns, n in ns_counts.most_common():
        tag = "  [worldgen]" if ns in GENERATED_NAMESPACES else ""
        lines.append(f"{n:>10}  {ns}{tag}")
    lines.append("")
    lines.append("=== TOP 40 NON-VANILLA BLOCKS ===")
    for name, n in block_counts.most_common(40):
        lines.append(f"{n:>10}  {name}")
    lines.append("")
    lines.append("=== TOP 60 BUILT CHUNKS (score = min(placed,3000) + 20/block-entity + 15/block-type; mass fills demoted) ===")
    lines.append("score  world                              file        chunk        block x,z       placed  BEs types fill  top placed blocks | top block entities")
    for score, dname, fname, cx, cz, placed, nbe, ntypes, fill, top, tbe in chunks[:60]:
        tops = ", ".join(f"{k.split(':',1)[-1]}x{v}" for k, v in top)
        tbes = ", ".join(f"{k.split(':',1)[-1]}x{v}" for k, v in tbe)
        lines.append(f"{score:>5}  {dname[:34]:<34} {fname:<11} ({cx:>4},{cz:>4})  ({cx*16:>6},{cz*16:>6})  {placed:>6}  {nbe:>3} {ntypes:>5} {fill:>4}  {tops} | {tbes}")
    lines.append("")
    lines.append(f"chunks with any built signal: {len(chunks)}")
    text = "\n".join(lines)
    print(text)
    if out:
        out.write_text(text, encoding="utf-8")
        print(f"\nreport -> {out}")


if __name__ == "__main__":
    main(sys.argv)
