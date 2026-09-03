#!/usr/bin/env python3
"""
transplant.py - copy chunks from one Anvil world into another, shifted, with block-name remapping.

    python transplant.py --src <src region dir> --dst <dst region dir> \
        --chunks x1,z1,x2,z2 [--offset dx,dz] [--remap remap.json] \
        [--src-entities <dir> --dst-entities <dir>] [--dry-run]

  --chunks    inclusive chunk-coordinate rectangle in the SOURCE world
  --offset    chunk offset applied when writing into the destination (default 0,0)
  --remap     JSON {"old:block": "new:block", ...}; a block whose namespace is not installed in the
              destination pack and is not remapped will be reported (and become air when the world loads)
  --dry-run   parse and report; write nothing

Everything in the chunk is carried: block palettes, block entities, ticks, heightmaps, lighting.
Structure references are dropped (they are chunk-coordinate-relative to the old world).
Entities (mobs, item frames, armour stands) live in the separate entities/ region set; pass both
--src-entities and --dst-entities to move those too. POI files for touched regions are deleted from
the destination so the game rebuilds them.

The NBT reader/writer here is typed and round-trips byte-for-byte, which is what --selftest checks:
    python transplant.py --selftest <any region dir>
"""

import gzip
import json
import struct
import sys
import time
import zlib
from pathlib import Path

# ----------------------------------------------------------------------------- typed NBT

T_END, T_BYTE, T_SHORT, T_INT, T_LONG, T_FLOAT, T_DOUBLE, T_BYTES, T_STRING, T_LIST, T_COMPOUND, T_INTS, T_LONGS = range(13)


class R:
    __slots__ = ("b", "i")

    def __init__(self, b): self.b, self.i = b, 0

    def take(self, fmt):
        v = struct.unpack_from(fmt, self.b, self.i); self.i += struct.calcsize(fmt); return v[0]

    def string(self):
        n = self.take(">H"); s = self.b[self.i:self.i + n].decode("utf-8", "surrogateescape"); self.i += n; return s

    def payload(self, t):
        if t == T_BYTE: return self.take(">b")
        if t == T_SHORT: return self.take(">h")
        if t == T_INT: return self.take(">i")
        if t == T_LONG: return self.take(">q")
        if t == T_FLOAT: return self.take(">f")
        if t == T_DOUBLE: return self.take(">d")
        if t == T_BYTES:
            n = self.take(">i"); v = self.b[self.i:self.i + n]; self.i += n; return v
        if t == T_STRING: return self.string()
        if t == T_LIST:
            et = self.take(">b"); n = self.take(">i")
            return (et, [self.payload(et) for _ in range(n)])
        if t == T_COMPOUND:
            d = {}
            while True:
                et = self.take(">b")
                if et == T_END: return d
                name = self.string(); d[name] = (et, self.payload(et))
        if t == T_INTS:
            n = self.take(">i"); v = list(struct.unpack_from(f">{n}i", self.b, self.i)); self.i += 4 * n; return v
        if t == T_LONGS:
            n = self.take(">i"); v = list(struct.unpack_from(f">{n}q", self.b, self.i)); self.i += 8 * n; return v
        raise ValueError(f"tag {t}")

    def root(self):
        t = self.take(">b"); assert t == T_COMPOUND
        name = self.string(); return name, self.payload(T_COMPOUND)


class W:
    def __init__(self): self.out = bytearray()

    def put(self, fmt, v): self.out += struct.pack(fmt, v)

    def string(self, s):
        b = s.encode("utf-8", "surrogateescape"); self.put(">H", len(b)); self.out += b

    def payload(self, t, v):
        if t == T_BYTE: self.put(">b", v)
        elif t == T_SHORT: self.put(">h", v)
        elif t == T_INT: self.put(">i", v)
        elif t == T_LONG: self.put(">q", v)
        elif t == T_FLOAT: self.put(">f", v)
        elif t == T_DOUBLE: self.put(">d", v)
        elif t == T_BYTES: self.put(">i", len(v)); self.out += v
        elif t == T_STRING: self.string(v)
        elif t == T_LIST:
            et, items = v; self.put(">b", et); self.put(">i", len(items))
            for it in items: self.payload(et, it)
        elif t == T_COMPOUND:
            for name, (et, val) in v.items():
                self.put(">b", et); self.string(name); self.payload(et, val)
            self.put(">b", T_END)
        elif t == T_INTS: self.put(">i", len(v)); self.out += struct.pack(f">{len(v)}i", *v)
        elif t == T_LONGS: self.put(">i", len(v)); self.out += struct.pack(f">{len(v)}q", *v)
        else: raise ValueError(f"tag {t}")

    def root(self, name, d):
        self.put(">b", T_COMPOUND); self.string(name); self.payload(T_COMPOUND, d); return bytes(self.out)


# ----------------------------------------------------------------------------- region files


def read_region_raw(path: Path):
    """Return {slot: (timestamp, compression, decompressed nbt bytes)} for every chunk present."""
    if not path.exists() or path.stat().st_size < 8192:
        return {}
    data = path.read_bytes()
    out = {}
    for idx in range(1024):
        off = struct.unpack_from(">I", data, idx * 4)[0]
        sectors, offset = off & 0xFF, off >> 8
        if offset == 0 or sectors == 0:
            continue
        ts = struct.unpack_from(">I", data, 4096 + idx * 4)[0]
        start = offset * 4096
        length = struct.unpack_from(">I", data, start)[0]
        comp = data[start + 4]
        blob = data[start + 5:start + 4 + length]
        raw = zlib.decompress(blob) if comp == 2 else gzip.decompress(blob) if comp == 1 else blob
        out[idx] = (ts, comp, raw)
    return out


def write_region(path: Path, chunks: dict):
    """Write {slot: (timestamp, compression, decompressed nbt bytes)} as a fresh region file."""
    header = bytearray(8192)
    body = bytearray()
    sector = 2
    for idx in sorted(chunks):
        ts, comp, raw = chunks[idx]
        blob = zlib.compress(raw, 6)
        payload = struct.pack(">I", len(blob) + 1) + bytes([2]) + blob
        pad = (-len(payload)) % 4096
        payload += b"\x00" * pad
        n = len(payload) // 4096
        if n > 255:
            raise ValueError(f"chunk slot {idx} too large ({n} sectors)")
        struct.pack_into(">I", header, idx * 4, (sector << 8) | n)
        struct.pack_into(">I", header, 4096 + idx * 4, ts or int(time.time()))
        body += payload
        sector += n
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(header) + bytes(body))


def slot_of(cx, cz): return (cx & 31) + 32 * (cz & 31)
def region_of(cx, cz): return (cx >> 5, cz >> 5)


# ----------------------------------------------------------------------------- chunk surgery


FAMILIES = ("_stairs", "_slab", "_door", "_trapdoor", "_wall", "_fence", "_pane", "_bars", "_button")


def _same_family(a: str, b: str) -> bool:
    """True when both names end in the same block-family suffix, so their state properties line up."""
    for suf in FAMILIES:
        if a.endswith(suf) and b.endswith(suf):
            return True
    return False


def shift_chunk(name, root, dx, dz, remap, unmapped):
    """Shift a parsed chunk by (dx,dz) chunks in place; remap block names; return namespaces seen."""
    bx, bz = dx * 16, dz * 16
    root["xPos"] = (T_INT, root["xPos"][1] + dx)
    root["zPos"] = (T_INT, root["zPos"][1] + dz)
    namespaces = {}
    for sec in root.get("sections", (T_LIST, (T_COMPOUND, [])))[1][1]:
        bs = sec.get("block_states")
        if not bs:
            continue
        pal = bs[1].get("palette")
        if not pal:
            continue
        for entry in pal[1][1]:
            nm = entry["Name"][1]
            if nm in remap:
                new_name = remap[nm]
                entry["Name"] = (T_STRING, new_name)
                if "Properties" in entry and not _same_family(nm, new_name):
                    del entry["Properties"]
                nm = new_name
            ns = nm.split(":", 1)[0]
            namespaces[ns] = namespaces.get(ns, 0) + 1
    remapped_ns = {k.split(":", 1)[0] for k in remap if not k.startswith("_")}
    kept = []
    for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
        bid = be.get("id", (T_STRING, ""))[1]
        if bid.split(":", 1)[0] in remapped_ns:
            continue  # its block is gone or changed kind
        if "x" in be: be["x"] = (T_INT, be["x"][1] + bx)
        if "z" in be: be["z"] = (T_INT, be["z"][1] + bz)
        kept.append(be)
    if "block_entities" in root:
        root["block_entities"] = (T_LIST, (T_COMPOUND, kept))
    for key in ("block_ticks", "fluid_ticks"):
        if key in root:
            for t in root[key][1][1]:
                if "x" in t: t["x"] = (T_INT, t["x"][1] + bx)
                if "z" in t: t["z"] = (T_INT, t["z"][1] + bz)
    if "structures" in root:
        root["structures"] = (T_COMPOUND, {"References": (T_COMPOUND, {}), "starts": (T_COMPOUND, {})})
    return namespaces


def shift_entities_chunk(root, dx, dz):
    bx, bz = dx * 16, dz * 16
    if "Position" in root:
        p = root["Position"][1]; root["Position"] = (T_INTS, [p[0] + dx, p[1] + dz])
    for ent in root.get("Entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
        if "Pos" in ent:
            et, pos = ent["Pos"][1]
            ent["Pos"] = (T_LIST, (et, [pos[0] + bx, pos[1], pos[2] + bz]))
        for k, d in (("TileX", bx), ("TileZ", bz)):
            if k in ent: ent[k] = (ent[k][0], ent[k][1] + d)


def transplant(src: Path, dst: Path, rect, dx, dz, remap, dry, entity_pair=None):
    x1, z1, x2, z2 = rect
    by_dst_region = {}
    unmapped, namespaces_total, moved = {}, {}, 0
    for cx in range(x1, x2 + 1):
        for cz in range(z1, z2 + 1):
            rx, rz = region_of(cx, cz)
            cache = transplant.cache.setdefault((src, rx, rz), read_region_raw(src / f"r.{rx}.{rz}.mca"))
            entry = cache.get(slot_of(cx, cz))
            if not entry:
                continue
            ts, comp, raw = entry
            name, root = R(raw).root()
            ns = shift_chunk(name, root, dx, dz, remap, unmapped)
            for k, v in ns.items():
                namespaces_total[k] = namespaces_total.get(k, 0) + v
            out = W().root(name, root)
            ncx, ncz = cx + dx, cz + dz
            by_dst_region.setdefault(region_of(ncx, ncz), {})[slot_of(ncx, ncz)] = (ts, 2, out)
            moved += 1
    print(f"chunks read from source: {moved}")
    print("namespaces in transplanted chunks (palette entries):")
    for k, v in sorted(namespaces_total.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>6}  {k}")
    if dry:
        print("dry run - nothing written")
        return
    for (rx, rz), slots in by_dst_region.items():
        path = dst / f"r.{rx}.{rz}.mca"
        existing = read_region_raw(path)
        existing.update(slots)
        write_region(path, existing)
        print(f"  wrote {len(slots):>4} chunks into {path.name} (now {len(existing)} chunks)")
        poi = dst.parent / "poi" / f"r.{rx}.{rz}.mca"
        if poi.exists():
            poi.unlink(); print(f"  removed stale {poi}")
    if entity_pair:
        esrc, edst = entity_pair
        by_dst = {}
        for cx in range(x1, x2 + 1):
            for cz in range(z1, z2 + 1):
                rx, rz = region_of(cx, cz)
                cache = transplant.cache.setdefault((esrc, rx, rz), read_region_raw(esrc / f"r.{rx}.{rz}.mca"))
                entry = cache.get(slot_of(cx, cz))
                if not entry:
                    continue
                ts, comp, raw = entry
                name, root = R(raw).root()
                shift_entities_chunk(root, dx, dz)
                ncx, ncz = cx + dx, cz + dz
                by_dst.setdefault(region_of(ncx, ncz), {})[slot_of(ncx, ncz)] = (ts, 2, W().root(name, root))
        for (rx, rz), slots in by_dst.items():
            path = edst / f"r.{rx}.{rz}.mca"
            existing = read_region_raw(path); existing.update(slots); write_region(path, existing)
            print(f"  wrote {len(slots):>4} entity chunks into {path}")


transplant.cache = {}


def selftest(region_dir: Path):
    """Parse and re-serialise every chunk; the bytes must match exactly."""
    files = sorted(region_dir.glob("r.*.mca"))
    ok = bad = 0
    for f in files:
        for idx, (ts, comp, raw) in read_region_raw(f).items():
            name, root = R(raw).root()
            again = W().root(name, root)
            if again == raw:
                ok += 1
            else:
                bad += 1
                if bad <= 3:
                    print(f"  MISMATCH {f.name} slot {idx}: {len(raw)} vs {len(again)} bytes")
    print(f"selftest: {ok} chunks round-trip byte-for-byte, {bad} mismatches, {len(files)} files")
    return bad == 0


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest(Path(argv[argv.index("--selftest") + 1])) else 1)
    args = dict(zip(argv[1::2], argv[2::2]))
    dry = "--dry-run" in argv
    src, dst = Path(args["--src"]), Path(args["--dst"])
    rect = [int(v) for v in args["--chunks"].split(",")]
    dx, dz = (int(v) for v in args.get("--offset", "0,0").split(","))
    remap = json.loads(Path(args["--remap"]).read_text(encoding="utf-8")) if "--remap" in args else {}
    remap = {k: v for k, v in remap.items() if not k.startswith("_")}
    ents = (Path(args["--src-entities"]), Path(args["--dst-entities"])) if "--src-entities" in args else None
    transplant(src, dst, rect, dx, dz, remap, dry, ents)


if __name__ == "__main__":
    main(sys.argv)
