"""Extract a build volume from a Forge 1.12.2 save: named blocks per chunk section, with a y-cut and
exclusion boxes applied, plus the tile entities. One open of the save per rect; everything after
(rendering, merging into the upgraded 1.20.1 chunks) reads the volume.

usage: extract112.py <rects.json> <rect name> <out dir>
       extract112.py --render <out dir>/<rect>.npz <out.png> [--scale N]

rects.json is buildmap/foreign/rects.json: each rect has "save" (folder under the saves root),
"blocks" [x0 z0 x1 z1], optional "y_max", optional "exclude_sky" [{blocks, y_min}]. The saves root
is the parent of rects.json's "saves_root" key, else G:\\GSCraft\\incoming\\Maps.

Volume file <rect>.npz:
  names      object array   registry names, index = numeric id
  keys       int32 [n,3]    (cx, cz, section y) per stored section
  ids        uint16 [n,4096] numeric block ids per section, YZX order (index = y*256 + z*16 + x)
  meta       uint8  [n,4096]
  modded     bool   [n,4096] True where the block is non-vanilla, non-air (the merge overlay mask)
  tiles.json (next to it): [{"cx","cz","x","y","z","id", ...nbt as json...}] for kept positions
"""
import sys, json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from anvil112 import read_level, registry, iter_chunks, sections, decode_section, AIR_ID

DEFAULT_ROOT = Path(r"G:\GSCraft\incoming\Maps")


def jsonable(v):
    """typed NBT (tag, value) -> plain json."""
    t, val = v
    if t == 10: return {k: jsonable(x) for k, x in val.items()}
    if t == 9: return [jsonable((val[0], x)) for x in val[1]]
    if t == 7: return list(val)
    return val


def extract(rects_path: Path, name: str, out_dir: Path):
    rects = json.load(open(rects_path))
    r = rects[name]
    root = Path(rects.get("saves_root", DEFAULT_ROOT))
    save = root / r["save"]
    x0, z0, x1, z1 = r["blocks"]
    cx0, cz0, cx1, cz1 = x0 >> 4, z0 >> 4, x1 >> 4, z1 >> 4
    y_max = r.get("y_max", 255)
    excl = [(e["blocks"], e.get("y_min", 0)) for e in r.get("exclude_sky", [])]
    reg = registry(read_level(save))
    names = np.array([reg.get(i, f"unknown:id{i}") for i in range(4096)], dtype=object)
    vanilla = np.array([n.startswith("minecraft:") for n in names], dtype=bool)
    keys, ids_l, meta_l, mod_l, tiles = [], [], [], [], []
    nchunks = cut = 0
    for cx, cz, level in iter_chunks(save):
        if not (cx0 <= cx <= cx1 and cz0 <= cz <= cz1):
            continue
        nchunks += 1
        bx, bz = cx * 16, cz * 16
        for sec in sections(level):
            y = sec["Y"][1]
            if y * 16 > y_max:
                continue
            ids, meta = decode_section(sec)
            ids = ids.copy(); meta = meta.copy()
            # y-cut inside the section
            yy = (np.arange(4096) >> 8) + y * 16
            kill = yy > y_max
            # exclusion boxes (world coords)
            xx = (np.arange(4096) & 15) + bx
            zz = ((np.arange(4096) >> 4) & 15) + bz
            for (ex0, ez0, ex1, ez1), ymin in excl:
                kill |= (xx >= ex0) & (xx <= ex1) & (zz >= ez0) & (zz <= ez1) & (yy >= ymin)
            if kill.any():
                cut += int((ids[kill] != AIR_ID).sum())
                ids[kill] = AIR_ID; meta[kill] = 0
            if not (ids != AIR_ID).any():
                continue
            keys.append((cx, cz, y)); ids_l.append(ids); meta_l.append(meta)
            mod_l.append((ids != AIR_ID) & ~vanilla[ids])
        for te in level.get("TileEntities", (0, (0, [])))[1][1]:
            tx, ty, tz = te["x"][1], te["y"][1], te["z"][1]
            if ty > y_max: continue
            if any(ex0 <= tx <= ex1 and ez0 <= tz <= ez1 and ty >= ymin for (ex0, ez0, ex1, ez1), ymin in excl): continue
            d = {k: jsonable(v) for k, v in te.items()}
            d.update({"cx": cx, "cz": cz})
            tiles.append(d)
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_dir / f"{name}.npz", names=names, keys=np.array(keys, dtype=np.int32),
                        ids=np.array(ids_l, dtype=np.uint16), meta=np.array(meta_l, dtype=np.uint8),
                        modded=np.array(mod_l, dtype=bool))
    json.dump(tiles, open(out_dir / f"{name}.tiles.json", "w"))
    total = int(sum((s != AIR_ID).sum() for s in ids_l)); modded = int(sum(m.sum() for m in mod_l))
    print(f"{name}: {nchunks} chunks, {len(keys)} sections, {total:,} blocks kept ({modded:,} modded), "
          f"{cut:,} blocks cut by y/exclusions, {len(tiles)} tile entities -> {out_dir / (name + '.npz')}")


def render(npz: Path, out: str, scale: int = 1):
    from topdown import colour_of as _c
    from anvil112 import colour_name
    from PIL import Image
    v = np.load(npz, allow_pickle=True)
    names = v["names"]; keys = v["keys"]; ids = v["ids"]
    cache = {}
    def col(i):
        c = cache.get(i)
        if c is None: c = cache[i] = _c(colour_name(names[i]))
        return c
    per_chunk = {}
    for (cx, cz, y), sec in zip(keys.tolist(), ids):
        per_chunk.setdefault((cx, cz), []).append((y, sec.reshape(16, 16, 16)))
    tiles = {}
    for k, secs in per_chunk.items():
        secs.sort(key=lambda t: -t[0])
        img = np.zeros((16, 16, 3), dtype=np.uint8); done = np.zeros((16, 16), dtype=bool)
        for y, arr in secs:
            solid = arr != AIR_ID
            top = np.where(solid.any(axis=0), 15 - np.argmax(solid[::-1], axis=0), -1)
            for z in range(16):
                for x in range(16):
                    if done[z, x] or top[z, x] < 0: continue
                    img[z, x] = col(int(arr[top[z, x], z, x])); done[z, x] = True
        tiles[k] = img
    xs = [k[0] for k in tiles]; zs = [k[1] for k in tiles]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    W, H = (x1 - x0 + 1) * 16, (z1 - z0 + 1) * 16
    img = np.full((H, W, 3), 236, dtype=np.uint8)
    for (cx, cz), t in tiles.items():
        img[(cz - z0) * 16:(cz - z0 + 1) * 16, (cx - x0) * 16:(cx - x0 + 1) * 16] = t
    if scale > 1:
        img = img[:H // scale * scale, :W // scale * scale].reshape(H // scale, scale, W // scale, scale, 3).mean(axis=(1, 3)).astype(np.uint8)
    Image.fromarray(img).save(out)
    print(f"{out}: chunks x {x0}..{x1} z {z0}..{z1}, {img.shape[1]}x{img.shape[0]}")


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 4 and a[1] == "--render":
        render(Path(a[2]), a[3], int(a[a.index("--scale") + 1]) if "--scale" in a else 1)
    elif len(a) == 4:
        extract(Path(a[1]), a[2], Path(a[3]))
    else:
        sys.exit(__doc__)
