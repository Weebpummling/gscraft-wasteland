"""Re-skin a 1.12.2 transplant in place, from the original save, onto the decoration mods the pack actually ships.

The 1.12 sources (the desert city, the Financial Plaza, the sewers, Novo, Bio Gen) were upgraded with `remap112.json`
before there was a 1.20.1 Chisel in the pack, so 665 k modded blocks were mapped to plain vanilla lookalikes: every
Chisel factory panel became one flat `factory_blocks:factory`, every Fureniku road block became black concrete, every
antiblock became vanilla concrete. Only 2.7 % actually fell through to the grey placeholder; the rest are there but
featureless.

This does not re-transplant. For every position it reads the ORIGINAL 1.12 block, works out what the old table turned
it into, and replaces it only if the destination still holds exactly that block. Anything integrate, the roads, the
rivers or a player changed is left alone, so the terrain blending and everything built since are safe.

usage: reskin112.py <1.12 save> <dest world> <plan.json> <source name> [--dry-run] [--limit N]
       reskin112.py "G:/GSCraft/incoming/Maps/world" G:/GSCraft/scratch/worlds/v8-build \
                    ../buildmap/plan_v8/transplant_plan_v8_fresh.json hub

The plan entry supplies the source chunk rectangle, the chunk offset and the y shift, so the lookup is exact.
"""
import sys, json, time, collections
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from anvil112 import read_level, registry, decode_section
from transplant import read_region_raw, write_region, R, W as NbtW, slot_of, region_of
from applyheight import decode_chunk, encode_chunk, T_STRING
from makeremap112 import resolve as old_resolve

COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
           "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
# Antiblocks Rechiseled ships nine flat "bright" colours; the rest keep vanilla concrete, which is the closer match
BRIGHT = {"white", "orange", "magenta", "yellow", "cyan", "blue", "green", "red", "black"}
# Chisel 1.20.1 names blocks <pattern>/<base block>; these are the industrial patterns the 1.12 city used
FACTORY = ["chisel:plates/iron_block", "chisel:rivets/iron_block", "chisel:vents/iron_block", "chisel:gears/iron_block",
           "chisel:dent/light_gray_concrete", "chisel:tiles_small/light_gray_concrete", "chisel:cut/gray_concrete",
           "chisel:array/gray_concrete", "chisel:panel/light_gray_concrete", "chisel:crate_dark/iron_block",
           "chisel:plates/gold_block", "chisel:rivets/gold_block", "chisel:dent/gray_concrete",
           "chisel:tiles_medium/light_gray_concrete", "chisel:panel/gray_concrete", "chisel:array/light_gray_concrete"]
TECHNICAL = ["chisel:panel/light_gray_concrete", "chisel:rivets/iron_block", "chisel:plates/iron_block",
             "chisel:vents/iron_block", "chisel:dent/light_gray_concrete", "chisel:cut/light_gray_concrete"]
ROADS = {0: "chisel:road/black_concrete", 1: "chisel:road/gray_concrete", 2: "chisel:road/light_gray_concrete",
         3: "chisel:road/black_concrete"}

IMPROVED = {}
IMPROVED.update({f"chisel:antiblock[{i}]": (f"antiblocksrechiseled:bright_{c}" if c in BRIGHT else f"minecraft:{c}_concrete")
                 for i, c in enumerate(COLOURS)})
IMPROVED.update({f"chisel:factory[{i}]": FACTORY[i] for i in range(16)})
IMPROVED.update({f"chisel:factory1[{i}]": FACTORY[(i + 8) % 16] for i in range(16)})
IMPROVED.update({f"chisel:technical[{i}]": TECHNICAL[i % len(TECHNICAL)] for i in range(16)})
IMPROVED.update({f"chisel:technical1[{i}]": TECHNICAL[(i + 2) % len(TECHNICAL)] for i in range(16)})
IMPROVED.update({f"chisel:technicalnew[{i}]": TECHNICAL[(i + 4) % len(TECHNICAL)] for i in range(16)})
# 2026-09-08: Fureniku's Roads is back. The city's streets were laid with it in 1.12, and the author's
# ground-up 1.20.1 rewrite (0.1.0, alpha) carries the same surface textures under the same names, so
# these stop being an approximation and become the originals. `_16` is the full cube; the 4/8/12 heights
# are slabs we do not want here. The rewrite has no markings, kerbs, bollards or drain covers yet, so
# the ~2,100 blocks of road paint and furniture keep their old mapping below.
FR = "furenikusroads:"
# Matched on texture brightness against the vanilla concrete the old table used: road_block_dark
# averages rgb 34 against black concrete's 10, standard 64 against gray's 57, light 116 against light
# gray's 122. Metas 0 and 3 were both black concrete in ROADS, so both stay one surface.
ROADS_120 = {0: FR + "road_block_dark_16",
             1: FR + "road_block_standard_16",
             2: FR + "road_block_light_16",
             3: FR + "road_block_dark_16"}
IMPROVED.update({f"furenikusroads:generic_blocks[{m}]": t for m, t in ROADS_120.items()})
IMPROVED.update({f"furenikusroads:road_block_standard[{m}]": FR + "road_block_standard_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:road_block_concrete_2[{m}]": FR + "road_block_concrete_2_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:road_block_yellow[{m}]": FR + "road_block_pale_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:road_block_gravel[{m}]": FR + "stone_road_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:road_block_muddy[{m}]": FR + "stone_road_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:street_block_b[{m}]": FR + "sidewalk_16" for m in range(16)})
IMPROVED.update({f"furenikusroads:street_block_a[{m}]": FR + "sidewalk_clean_16" for m in range(16)})
IMPROVED.update({
    "chisel:laboratory": "chisel:tiles_small/white_concrete",
    "chisel:concrete_lightgray1": "chisel:array/light_gray_concrete",
    "chisel:concrete_gray1": "chisel:array/gray_concrete",
    "chisel:concrete_white1": "chisel:array/white_concrete",
    "chisel:concrete_black1": "chisel:array/black_concrete",
    "chisel:glass": "chisel:screen/glass",
    "chisel:glass1": "chisel:steelframe/glass",
    "chisel:hexplating": "chisel:plates/iron_block",
    "chisel:futura": "chisel:array/light_blue_concrete",
    "hbm:deco_steel": "chisel:rivets/iron_block",
    "hbm:brick_concrete": "chisel:cut/gray_concrete",
    "hbm:machine_tower_small": "chisel:vents/iron_block",
    "srparasites:infestremain": "minecraft:sculk",
})

# ---- 2026-09-06: the mods added for the desert city (owner: Simply Light yes, TorchMaster yes, an HBM
# cosmetic substitute, MrCrayfish mapped 1:1; Scape and Run: Parasites declined)
SIMPLY = ["illuminant_block_on", "illuminant_block", "illuminant_panel", "illuminant_slab",
          "edge_light", "edge_light_top", "wall_lamp", "rodlamp", "lightbulb"]
IMPROVED.update({f"simplylight:{b}": f"simplylight:{b}" for b in SIMPLY})   # 1.20.1 keeps the 1.12 names
IMPROVED.update({
    "torchmaster:mega_torch": "torchmaster:megatorch",
    "torchmaster:dread_lamp": "torchmaster:dreadlamp",
    "torchmaster:feral_flare_lantern": "torchmaster:feral_flare_lantern",
    "torchmaster:invisible_light": "torchmaster:invisible_light",
    "torchmaster:terrain_lighter": "torchmaster:invisible_light",
})
# HBM has no 1.20.1 port; Industrial Decorations and IndustrialDeco carry the cosmetic side
HBM = {
    "deco_steel": "industrial_deco:industrial_steel",
    "concrete_smooth": "minecraft:smooth_stone",
    "brick_concrete": "industrial_deco:lab_wall",
    "brick_concrete_cracked": "minecraft:cracked_stone_bricks",
    "brick_concrete_mossy": "minecraft:mossy_stone_bricks",
    "brick_concrete_broken": "minecraft:cracked_stone_bricks",
    "brick_light": "chisel:array/white_concrete",
    "machine_tower_small": "industrial_deco:industrial_pipe",
    "steel_grate": "immersiveengineering:alu_scaffolding_grate_top",
    "fence_metal": "minecraft:iron_bars",
    "railing_normal": "minecraft:iron_bars",
    "reinforced_glass": "industrial_deco:reinforced_glass",
    "blast_door": "industrial_deco:blast_door",
}
IMPROVED.update({f"hbm:{k}": v for k, v in HBM.items()})
# NEVER map to industrialdeco:metal_fence_block. Its getShape asks the level for its neighbours, which the
# sky-light engine calls while lighting a chunk; if a neighbour is in an unloaded chunk the light worker
# blocks on it while the main thread waits for the chunk being lit, and the server deadlocks until the
# watchdog kills the tick. 838 of them in the expanded desert city cost a whole evening (2026-09-06).
# Vanilla iron_bars takes its shape from its own blockstate and never touches the level.
HBM_PREFIX = [("deco_pipe", "industrial_deco:industrial_pipe"), ("hazard", "industrial_deco:hazard_lab_wall"),
              ("deco_", "industrial_deco:industrial_steel"), ("brick_", "industrial_deco:lab_wall"),
              ("concrete", "minecraft:smooth_stone"), ("steel_", "industrial_deco:industrial_steel"),
              ("fence", "minecraft:iron_bars"), ("railing", "minecraft:iron_bars")]
# MrCrayfish's Furniture -> Refurbished Furniture, matched on the object rather than the wood or colour
CFM = {
    "electric_fence": "minecraft:iron_bars", "bar_stool": "refurbished_furniture:light_gray_stool",
    "inflatable_castle": "refurbished_furniture:light_gray_trampoline", "cabinet_kitchen": "refurbished_furniture:oak_kitchen_cabinetry",
    "counter_sink": "refurbished_furniture:oak_kitchen_sink", "tv": "refurbished_furniture:television",
}
CFM_PREFIX = [("desk", "refurbished_furniture:oak_desk"), ("table", "refurbished_furniture:oak_table"),
              ("chair", "refurbished_furniture:oak_chair"), ("sofa", "refurbished_furniture:light_gray_sofa"),
              ("stool", "refurbished_furniture:light_gray_stool"), ("bedside_cabinet", "refurbished_furniture:oak_drawer"),
              ("cabinet", "refurbished_furniture:oak_storage_cabinet"), ("crate", "refurbished_furniture:oak_crate"),
              ("hedge", "refurbished_furniture:oak_hedge"), ("toilet", "refurbished_furniture:oak_toilet"),
              ("bath", "refurbished_furniture:oak_bath"), ("basin", "refurbished_furniture:oak_basin"),
              ("fridge", "refurbished_furniture:dark_fridge"), ("freezer", "refurbished_furniture:dark_freezer"),
              ("microwave", "refurbished_furniture:dark_microwave"), ("toaster", "refurbished_furniture:dark_toaster"),
              ("stove", "refurbished_furniture:dark_stove"), ("oven", "refurbished_furniture:dark_stove"),
              ("cooler", "refurbished_furniture:light_gray_cooler"), ("grill", "refurbished_furniture:light_gray_grill"),
              ("mail_box", "refurbished_furniture:oak_mail_box"), ("post_box", "refurbished_furniture:oak_mail_box"),
              ("lamp", "refurbished_furniture:light_gray_lamp"), ("ceiling_fan", "refurbished_furniture:oak_light_ceiling_fan"),
              ("bin", "refurbished_furniture:recycle_bin"), ("computer", "refurbished_furniture:computer"),
              ("printer", "refurbished_furniture:computer"), ("plate", "refurbished_furniture:plate"),
              ("cutting_board", "refurbished_furniture:oak_cutting_board"), ("workbench", "refurbished_furniture:workbench"),
              ("storage_jar", "refurbished_furniture:oak_storage_jar"), ("mirror", "refurbished_furniture:oak_basin"),
              ("door_bell", "refurbished_furniture:doorbell"), ("light_switch", "refurbished_furniture:dark_lightswitch"),
              ("trampoline", "refurbished_furniture:light_gray_trampoline"), ("stepping_stone", "refurbished_furniture:andesite_stepping_stones")]
IMPROVED.update({f"cfm:{k}": v for k, v in CFM.items()})
# Refurbished Furniture names every piece with its material, so each object above resolves to a concrete block


def prefix_target(name):
    """Family rules for the mods with hundreds of 1.12 variants (HBM decoration, MrCrayfish furniture)."""
    ns, _, base = name.partition(":")
    table = HBM_PREFIX if ns == "hbm" else (CFM_PREFIX if ns == "cfm" else None)
    if table is None: return None
    for key, tgt in table:
        if key in base: return tgt
    return None


# ---- 2026-09-08: the last of the vanilla stand-ins, onto mods the pack already ships.
# An audit against the 1.12 save found 4,437 blocks still standing in the city as plain vanilla
# lookalikes. Three families account for 3,962 of them, and every target below is already in the pack,
# so this costs no new mod, no memory and no registry risk.
#
# NEVER map anything to industrialdeco:metal_fence_block. Its getShape asks the level for its
# neighbours' states, the sky-light engine calls it mid-lighting, and the server deadlocks. That block
# cost six crashes on 2026-09-06 and 838 of them were swept out with replaceblock.py.
DECOR = {
    # ruined concrete brickwork: three damage states that all collapsed onto two vanilla blocks
    "hbm:brick_concrete": "chipped:massive_stone_bricks",
    "hbm:brick_concrete_cracked": "chipped:cracked_disordered_stone_bricks",
    "hbm:brick_concrete_broken": "chipped:vertical_disordered_stone_bricks",
    "hbm:brick_concrete_mossy": "chipped:eroded_mossy_stone_bricks",
    # railings and fences: iron bars is the right shape, but a dead city's steel is not shiny, and the
    # three kinds should not read as one. Immersive Weathering's bars carry their own rust.
    "hbm:railing_normal": "immersive_weathering:rusted_iron_bars",
    "hbm:railing_bend": "immersive_weathering:rusted_iron_bars",
    "hbm:railing_end_self": "immersive_weathering:rusted_iron_bars",
    "hbm:railing_end_flipped_self": "immersive_weathering:rusted_iron_bars",
    "hbm:railing_end_floor": "immersive_weathering:rusted_iron_bars",
    "hbm:railing_end_flipped_floor": "immersive_weathering:rusted_iron_bars",
    "hbm:fence_metal": "immersiveengineering:steel_fence",
    "cfm:electric_fence": "immersiveengineering:alu_fence",   # a wire fence, not a window grille
    # the three concretes that all became smooth stone
    "hbm:concrete_smooth": "chipped:smooth_light_gray_concrete",
    "hbm:concrete_pillar": "chipped:stacked_light_gray_concrete",
    "hbm:concrete_asbestos": "chipped:sanded_smooth_stone",
}
# The 475 antiblock positions that fall to vanilla purple and light grey concrete are left alone on
# purpose: an antiblock IS a flat single-colour block, and vanilla concrete is exactly that. Antiblocks
# Rechiseled only ships nine "bright" colours and these two are not among them.

DECOR_PREV = {}
for _k, _v in DECOR.items():
    _prev = IMPROVED.get(_k) or prefix_target(_k)
    if _prev and _prev != _v:
        DECOR_PREV[_k] = _prev          # what the last pass wrote, so this pass can recognise it
    IMPROVED[_k] = _v


def new_resolve(name, meta):
    return IMPROVED.get(f"{name}[{meta}]") or IMPROVED.get(name) or prefix_target(name)


def plain(n):
    return n.split("[")[0]


def props_of(n):
    if "[" not in n: return {}
    return dict(kv.split("=") for kv in n[n.index("[") + 1:-1].split(","))


# What an earlier re-skin already wrote. A destination holding one of these has still not been touched
# by anything else, so it is safe to improve again. Add to this whenever a mapping is superseded.
SUPERSEDED = {}
SUPERSEDED.update({f"furenikusroads:generic_blocks[{m}]": t for m, t in ROADS.items()})
SUPERSEDED.update({f"furenikusroads:road_block_standard[{m}]": "chisel:road/black_concrete" for m in range(16)})
SUPERSEDED.update({f"furenikusroads:street_block_b[{m}]": "chisel:road/gray_concrete" for m in range(16)})
SUPERSEDED.update({f"furenikusroads:street_block_a[{m}]": "chisel:road/light_gray_concrete" for m in range(16)})
# Every block the decoration pass re-targets: DECOR_PREV holds what the pass before it wrote, which is
# what is standing in the world now.
SUPERSEDED.update(DECOR_PREV)


def main(a):
    if len(a) < 5: sys.exit(__doc__)
    save, dest, planp, want = Path(a[1]), Path(a[2]), a[3], a[4]
    dry = "--dry-run" in a
    entry = next(e for e in json.load(open(planp)) if e["source"] == want)
    cx0, cz0, cx1, cz1 = entry["chunks"]; ox, oz = entry["offset"]; dy = entry.get("dy", 0)
    print(f"{want}: source chunks x {cx0}..{cx1} z {cz0}..{cz1}, offset {ox},{oz}, dy {dy}")
    reg = registry(read_level(save))
    names = {i: n for i, n in reg.items()}
    # per (id, meta) target tables
    lut_old = {}; lut_new = {}
    for i, n in names.items():
        if n.startswith("minecraft:"): continue
        for m in range(16):
            o = old_resolve(n, m); o = o[0] if isinstance(o, tuple) else o
            nw = new_resolve(n, m)
            accept = set()
            if o:
                accept.add(plain(o))
            sup = SUPERSEDED.get(f"{n}[{m}]") or SUPERSEDED.get(n)
            if sup:
                accept.add(plain(sup))
            accept.discard(plain(nw) if nw else None)
            if nw and accept:
                lut_old[(i, m)] = accept; lut_new[(i, m)] = nw
    print(f"{len(lut_new)} (block, meta) pairs have a better target; "
          f"{len({v for v in lut_new.values()})} distinct 1.20 blocks")
    src_regions = {}
    def src_chunk(cx, cz):
        rk = (cx >> 5, cz >> 5)
        if rk not in src_regions:
            p = save / "region" / f"r.{rk[0]}.{rk[1]}.mca"
            src_regions[rk] = read_region_raw(p) if p.exists() else {}
        ent = src_regions[rk].get(slot_of(cx, cz))
        if not ent: return None
        try: _, root = R(ent[2]).root()
        except Exception: return None
        return root.get("Level", (0, None))[1]

    dst_regions = {}
    def dst_region(cx, cz):
        rk = region_of(cx, cz)
        if rk not in dst_regions:
            p = dest / "region" / f"r.{rk[0]}.{rk[1]}.mca"
            dst_regions[rk] = read_region_raw(p) if p.exists() else {}
        return dst_regions[rk], rk

    t0 = time.time(); by_region = {}; changed_total = 0; hits = collections.Counter(); done = 0
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            level = src_chunk(cx, cz)
            if not level: continue
            dcx, dcz = cx + ox, cz + oz
            dreg, rk = dst_region(dcx, dcz); dent = dreg.get(slot_of(dcx, dcz))
            if not dent: continue
            try:
                dname, droot = R(dent[2]).root(); dids, dpal, dtmpl = decode_chunk(droot)
            except Exception:
                continue
            dnames = [e["Name"][1] for e in dpal]
            want_old = {}; want_new = {}
            for sec in level.get("Sections", (0, (0, [])))[1][1]:
                sy = sec["Y"][1]
                if "Blocks" not in sec: continue
                ids, meta = decode_section(sec)
                key = ids.astype(np.int32) * 16 + meta
                uniq = np.unique(key)
                for k in uniq:
                    bid, m = int(k) // 16, int(k) % 16
                    if (bid, m) not in lut_new: continue
                    pos = np.nonzero(key == k)[0]
                    ys = sy * 16 + pos // 256 + dy + 64
                    zs = (pos // 16) % 16; xs = pos % 16
                    good = (ys >= 0) & (ys < 384)
                    want_old.setdefault(k, []).append((ys[good], zs[good], xs[good]))
            if not want_old: continue
            pindex = {n: i for i, n in enumerate(dnames)}
            def pid(n):
                if n not in pindex:
                    pindex[n] = len(dpal)
                    e = {"Name": (T_STRING, plain(n))}
                    p = props_of(n)
                    if p: e["Properties"] = (10, {k: (T_STRING, v) for k, v in p.items()})
                    dpal.append(e); dnames.append(plain(n))
                return pindex[n]
            nchanged = 0
            for k, groups in want_old.items():
                bid, m = int(k) // 16, int(k) % 16
                old_set, new_n = lut_old[(bid, m)], lut_new[(bid, m)]
                tgt = pid(new_n)
                for ys, zs, xs in groups:
                    cur = dids[ys, zs, xs]
                    if cur.size == 0: continue
                    ok = (cur >= 0) & np.array([dnames[c] in old_set if c >= 0 else False for c in cur], dtype=bool)
                    if not ok.any(): continue
                    dids[ys[ok], zs[ok], xs[ok]] = tgt
                    n = int(ok.sum()); nchanged += n; hits[new_n] += n
            if nchanged == 0: continue
            encode_chunk(droot, dids, dpal, dtmpl)
            by_region.setdefault(rk, {})[slot_of(dcx, dcz)] = (dent[0], 2, NbtW().root(dname, droot))
            changed_total += nchanged; done += 1
            if limit and done >= limit: break
        if limit and done >= limit: break
    print(f"\n{changed_total:,} blocks re-skinned in {done} chunks, {len(by_region)} region files; {time.time()-t0:.0f}s")
    for n, c in hits.most_common(14): print(f"   {c:9,d}  {n}")
    if dry: print("DRY RUN, nothing written"); return
    for rk, slots in by_region.items():
        p = dest / "region" / f"r.{rk[0]}.{rk[1]}.mca"
        reg2 = dst_regions[rk]; reg2.update(slots); write_region(p, reg2)
        poi = dest / "poi" / f"r.{rk[0]}.{rk[1]}.mca"
        if poi.exists(): poi.unlink()
    print(f"{len(by_region)} region files written")


if __name__ == "__main__":
    main(sys.argv)
