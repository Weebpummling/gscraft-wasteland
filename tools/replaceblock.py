"""Replace every occurrence of one block with another, across a rectangle, straight in the region files.

Written to undo a re-skin choice that deadlocks the server. `industrialdeco:metal_fence_block` computes its shape by
asking the level for its neighbours' block states. The sky-light engine calls getShape while it is lighting a chunk;
if a neighbour is in a chunk that is not loaded yet, the light worker blocks on that chunk while the main thread is
already blocked waiting for the chunk being lit. Nothing else runs and the watchdog eventually kills the tick. A
thread dump of the local server caught it exactly:

    LightEngine.getOpacity -> BlockStateBase.getShape
      -> industrialdeco MetalFenceBlock.getShape (line 108)
        -> Level.getBlockState -> ServerChunkCache.getChunkOffThread -> CompletableFuture.join   [parked]

Vanilla `minecraft:iron_bars` takes its shape from its own blockstate properties and never touches the level, so it
is a safe stand-in and looks close enough.

usage: replaceblock.py <world dir> <from> <to> <x0> <z0> <x1> <z1> [--prefix] [--dry-run]
       replaceblock.py G:/GSCraft/server/wasteland-v8 industrialdeco: minecraft:iron_bars -3616 -1056 -2337 748 --prefix

With --prefix, <from> matches any block whose name starts with it, which is how a whole mod's blocks are swept out.
Block entities at replaced positions are dropped, since the new block has none.
"""
import sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, T_STRING, T_LIST, T_COMPOUND


def main(a):
    if len(a) < 8: sys.exit(__doc__)
    world = Path(a[1]); src, dst = a[2], a[3]
    x0, z0, x1, z1 = (int(v) for v in a[4:8])
    pref = "--prefix" in a; dry = "--dry-run" in a
    cx0, cz0, cx1, cz1 = x0 >> 4, z0 >> 4, x1 >> 4, z1 >> 4
    regions = {}
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            regions.setdefault(region_of(cx, cz), []).append((cx, cz))
    t0 = time.time(); blocks = 0; chunks = 0; names_hit = {}
    for rk, cs in sorted(regions.items()):
        p = world / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        if not p.exists(): continue
        reg = read_region_raw(p); out = {}
        for cx, cz in cs:
            e = reg.get(slot_of(cx, cz))
            if not e: continue
            name, root = R(e[2]).root()
            try: ids, pal, tmpl = decode_chunk(root)
            except Exception: continue
            names = [x["Name"][1] for x in pal]
            hit = [i for i, n in enumerate(names) if (n.startswith(src) if pref else n == src)]
            if not hit: continue
            for i in hit: names_hit[names[i]] = names_hit.get(names[i], 0) + int((ids == i).sum())
            # one palette entry for the replacement, no properties
            tgt = next((i for i, n in enumerate(names) if n == dst and not pal[i].get("Properties")), None)
            if tgt is None:
                tgt = len(pal); pal.append({"Name": (T_STRING, dst)}); names.append(dst)
            n = 0
            for i in hit:
                m = ids == i
                n += int(m.sum()); ids[m] = tgt
            if n == 0: continue
            keep = [be for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]
                    if not (cx * 16 <= be["x"][1] < cx * 16 + 16 and cz * 16 <= be["z"][1] < cz * 16 + 16
                            and ids[be["y"][1] + 64, be["z"][1] & 15, be["x"][1] & 15] == tgt)]
            root["block_entities"] = (T_LIST, (T_COMPOUND, keep))
            encode_chunk(root, ids, pal, tmpl)
            out[slot_of(cx, cz)] = (e[0], 2, NbtW().root(name, root))
            blocks += n; chunks += 1
        if out and not dry:
            reg.update(out); write_region(p, reg)
        if out: print(f"  r.{rk[0]}.{rk[1]}: {len(out)} chunks", flush=True)
    print(f"{blocks:,} blocks in {chunks} chunks -> {dst}; {time.time()-t0:.0f}s{' (dry run)' if dry else ''}")
    for n, c in sorted(names_hit.items(), key=lambda t: -t[1]): print(f"   {c:8,d}  {n}")


if __name__ == "__main__":
    main(sys.argv)
