"""Apply an authored heightmap to an existing 1.20.1 world by shifting whole columns (ground, plants, trees, snow move
together; the gap is filled from below, cuts remove subsoil), so the landscape keeps its cover instead of being
re-surfaced. Fixed columns (roads, rail, water, buildings) are never touched.

usage: applyheight.py <world dir> <census dir> <heightplan dir> [--regions rx0 rz0 rx1 rz1] [--dry-run]
  census dir:     classes.npy (0 ground 1 road 2 rail 3 water 4 building 5 tree 6 bare 7 missing), ground_y.npy
  heightplan dir: height.npy (target ground height per block)
Cell origin x -3900 z -3900 (5101 x 4601 blocks). Sections are decoded and re-encoded with numpy; heightmaps and light
are dropped so the game recomputes them on first load.
"""
import sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW

X0, Z0 = -3900, -3900
T_BYTE, T_INT, T_LONG, T_STRING, T_LIST, T_COMPOUND, T_LONG_ARRAY = 1, 3, 4, 8, 9, 10, 12
AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def unpack(data, n_pal):
    """block_states data longs -> 4096 palette indices (numpy)."""
    bits = max(4, (n_pal - 1).bit_length()); per = 64 // bits
    longs = np.array(data, dtype=np.int64).astype(np.uint64)
    k = np.arange(per, dtype=np.uint64) * np.uint64(bits)
    idx = ((longs[:, None] >> k[None, :]) & np.uint64((1 << bits) - 1)).reshape(-1)[:4096]
    return idx.astype(np.int32)


def pack(idx, n_pal):
    bits = max(4, (n_pal - 1).bit_length()); per = 64 // bits
    n_longs = -(-4096 // per)
    padded = np.zeros(n_longs * per, dtype=np.uint64); padded[:4096] = idx.astype(np.uint64)
    k = np.arange(per, dtype=np.uint64) * np.uint64(bits)
    longs = (padded.reshape(n_longs, per) << k[None, :]).sum(axis=1, dtype=np.uint64)
    return longs.astype(np.int64).tolist()


def key_of(entry):
    props = entry.get("Properties", (0, {}))[1]
    return (entry["Name"][1], tuple(sorted((k, v[1]) for k, v in props.items())))


def decode_chunk(root):
    """-> (ids[384,16,16] int32 with -1 for missing sections, palette list of NBT compounds, section template)."""
    secs = root["sections"][1][1]
    pal, index = [], {}
    ids = np.full((384, 16, 16), -1, np.int32)
    tmpl = {}
    for s in secs:
        y = s["Y"][1]
        if y < -4 or y > 19: continue
        tmpl[y] = s
        bs = s.get("block_states")
        if not bs: continue
        p = bs[1]["palette"][1][1]
        local = []
        for e in p:
            k = key_of(e)
            if k not in index: index[k] = len(pal); pal.append(e)
            local.append(index[k])
        local = np.array(local, np.int32)
        data = bs[1].get("data")
        sec_idx = unpack(data[1], len(p)) if data else np.zeros(4096, np.int32)
        ids[(y + 4) * 16:(y + 5) * 16] = local[sec_idx].reshape(16, 16, 16)   # [y][z][x]
    return ids, pal, tmpl


def encode_chunk(root, ids, pal, tmpl):
    out = []
    air_id = next((i for i, e in enumerate(pal) if e["Name"][1] == "minecraft:air"), None)
    for y in range(-4, 20):
        block = ids[(y + 4) * 16:(y + 5) * 16]
        s = dict(tmpl.get(y, {"Y": (T_BYTE, y), "biomes": (T_COMPOUND, {"palette": (T_LIST, (T_STRING, ["minecraft:plains"]))})}))
        s["Y"] = (T_BYTE, y)
        if (block < 0).all():
            s.pop("block_states", None); out.append(s); continue
        flat = block.reshape(-1).copy()
        if (flat < 0).any():
            if air_id is None: pal.append({"Name": (T_STRING, "minecraft:air")}); air_id = len(pal) - 1
            flat[flat < 0] = air_id
        used, inv = np.unique(flat, return_inverse=True)
        sec_pal = [pal[i] for i in used]
        bs = {"palette": (T_LIST, (T_COMPOUND, sec_pal))}
        if len(sec_pal) > 1: bs["data"] = (T_LONG_ARRAY, pack(inv.astype(np.int32), len(sec_pal)))
        s["block_states"] = (T_COMPOUND, bs); s.pop("BlockLight", None); s.pop("SkyLight", None)
        out.append(s)
    root["sections"] = (T_LIST, (T_COMPOUND, out))
    root.pop("Heightmaps", None); root["isLightOn"] = (T_BYTE, 0)


def main(a):
    if len(a) < 4: sys.exit(__doc__)
    world, cdir, hdir = Path(a[1]), Path(a[2]), Path(a[3]); dry = "--dry-run" in a
    cls = np.load(cdir / "classes.npy"); gnd = np.load(cdir / "ground_y.npy").astype(np.int32); tgt = np.load(hdir / "height.npy").astype(np.int32)
    H, W = cls.shape
    delta = tgt - gnd; delta[np.isin(cls, (1, 2, 3, 4, 7))] = 0
    if "--regions" in a:
        i = a.index("--regions"); rx0, rz0, rx1, rz1 = map(int, a[i + 1:i + 5])
    else:
        rx0, rz0, rx1, rz1 = X0 >> 9, Z0 >> 9, (X0 + W - 1) >> 9, (Z0 + H - 1) >> 9
    t0 = time.time(); cols = chunks = files = 0
    for rx in range(rx0, rx1 + 1):
        for rz in range(rz0, rz1 + 1):
            f = world / "region" / f"r.{rx}.{rz}.mca"
            if not f.exists(): continue
            reg = read_region_raw(f); changed = False
            for slot, entry in list(reg.items()):
                cx, cz = rx * 32 + (slot & 31), rz * 32 + (slot >> 5)
                bx, bz = cx * 16 - X0, cz * 16 - Z0
                if bx < 0 or bz < 0 or bx + 16 > W or bz + 16 > H: continue
                d = delta[bz:bz + 16, bx:bx + 16]
                if not d.any(): continue
                name, root = R(entry[2]).root()
                if root.get("Status", (0, ""))[1] not in ("minecraft:full", "full"): continue
                ids, pal, tmpl = decode_chunk(root)
                g = gnd[bz:bz + 16, bx:bx + 16]
                for lz in range(16):
                    for lx in range(16):
                        dy = int(d[lz, lx])
                        if dy == 0: continue
                        col = ids[:, lz, lx]; gi = int(g[lz, lx]) + 64   # index of the ground block
                        base = max(gi - 3, 1)
                        if dy > 0:
                            top = 384 - dy
                            col[base + dy:384] = col[base:top].copy()
                            col[base:base + dy] = col[base] if col[base] >= 0 else col[gi]
                        else:
                            k = -dy
                            src_lo = base                      # remove k blocks below the stack: new[y] = old[y + k] for y >= base - k
                            col[base - k:384 - k] = col[base:384].copy()
                            col[384 - k:384] = -1
                        cols += 1
                encode_chunk(root, ids, pal, tmpl)
                if not dry: reg[slot] = (entry[0], entry[1], NbtW().root(name, root))
                chunks += 1; changed = True
            if changed and not dry: write_region(f, reg); files += 1
            print(f"  r.{rx}.{rz}: {chunks} chunks, {cols:,} columns so far, {int(time.time() - t0)} s", flush=True)
    print(f"{'DRY RUN ' if dry else ''}done: {chunks} chunks, {cols:,} columns shifted, {files} region files, {int(time.time() - t0)} s")


if __name__ == "__main__":
    main(sys.argv)
