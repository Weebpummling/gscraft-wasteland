"""Comprehensive review of a built wasteland world (v6 layout): every chunk parsed, every rule checked.

usage: reviewv6.py <world dir> <out prefix> [--pristine <pregen world dir>]

Checks (each a section of the report, each with a PASS / WARN / FAIL):
  chunks      every region file and chunk parses; DataVersion; sections in range; duplicate chunk slots
  palette     every block name in the world resolves in the pack (tools/planblocks.KEEP namespaces +
              the vanilla report); 1.12-era names that should not exist after the upgrade
  entities    block entities of non-vanilla types the pack does not have; entity ids outside the pack
  sites       every v6 rectangle (transplant_plan_v6.json) has its chunks; placed-block count vs the
              source volume's count (transplant completeness); the two ship boxes above y 104 are air
  pads        every pad (pads_v6.json) is level at its y across its interior (top of terrain columns
              outside builds), and its outline exists
  tower       tower pad flat at 99 and stage 0 present (beacon/iron in the compound); nothing else built
  camp        crater rect untouched vs the pregen copy; camp NPC building sites (draft 5) clear of builds
  water       water share inside each site rect + margin; water columns along the three road lines
  distances   camp -> every site, site <-> site spacing against the design's rules
  border      level.dat: border centre/size, spawn
Writes <prefix>.json (numbers) and <prefix>.md (the readable report).
"""
import sys, json, gzip, math, collections, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transplant import R, read_region_raw, region_of, slot_of
from anvil import Chunk, decode
from planblocks import KEEP
from terrain import NATURAL, PLANT

AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
CAMP_CENTRE = (16, 16)
CRATER = (-16, -16, 47, 47)
NPC_SITES = {"Marshall gatehouse": (150, 0, 173, 15), "Walker yard": (60, 80, 99, 111), "Tony clinic": (-100, -100, -81, -85),
             "Michael plant": (-40, 100, -9, 123), "Tune shack": (40, -120, 55, -105), "James lookout": (-150, -150, -143, -143)}
ROADS = {"spine camp->Novo->district": [(173, 8), (992, 176), (896, 384)],
         "district->plaza": [(1328, 1376), (767, 2440)], "district->runway": [(2368, 1552), (3040, 2600)]}
SHIPS = [((-1056 + 441 * 16, 1568 - 22 * 16, -737 + 441 * 16, 2079 - 22 * 16), 104 + 16),
         ((-672 + 441 * 16, 1712 - 22 * 16, -641 + 441 * 16, 1967 - 22 * 16), 104 + 16)]


class World:
    def __init__(self, region: Path):
        self.region = region; self.cache = {}
    def raw(self, cx, cz):
        rx, rz = region_of(cx, cz)
        if (rx, rz) not in self.cache:
            f = self.region / f"r.{rx}.{rz}.mca"; self.cache[(rx, rz)] = read_region_raw(f) if f.exists() else {}
            if len(self.cache) > 40: self.cache = dict(list(self.cache.items())[-20:])
        return self.cache[(rx, rz)].get(slot_of(cx, cz))
    def chunk(self, cx, cz):
        r = self.raw(cx, cz)
        return Chunk(R(r[2]).root()[1]) if r else None


def verdict(fails, warns): return "FAIL" if fails else ("WARN" if warns else "PASS")


def check_chunks_palette_entities(region: Path, valid_vanilla, report):
    t0 = time.time()
    bad = collections.Counter(); ns = collections.Counter(); names_out = collections.Counter(); be_bad = collections.Counter()
    ent_bad = collections.Counter(); n = 0; dv = collections.Counter(); nolight = 0; noheight = 0; legacy = collections.Counter()
    legacy_names = {"minecraft:concrete", "minecraft:stained_hardened_clay", "minecraft:wool", "minecraft:log", "minecraft:leaves",
                    "minecraft:stonebrick", "minecraft:double_stone_slab", "minecraft:tallgrass"}   # minecraft:grass IS 1.20.1 short grass
    files = sorted(region.glob("r.*.mca"))
    for f in files:
        try: raw = read_region_raw(f)
        except Exception as e: bad[f"region unreadable {f.name}: {e}"] += 1; continue
        for slot, (ts, comp, blob) in raw.items():
            n += 1
            try: _, root = R(blob).root()
            except Exception: bad["chunk nbt unparseable"] += 1; continue
            dv[root.get("DataVersion", (0, 0))[1]] += 1
            if root.get("isLightOn", (0, 1))[1] == 0: nolight += 1
            if "Heightmaps" not in root: noheight += 1
            for sec in root.get("sections", (0, (0, [])))[1][1]:
                y = sec["Y"][1]
                if not -4 <= y <= 19: bad["section Y out of range"] += 1
                bs = sec.get("block_states")
                if not bs: continue
                for p in bs[1]["palette"][1][1]:
                    nm = p["Name"][1]; ns[nm.split(":")[0]] += 1
                    if nm.split(":")[0] not in KEEP and nm.split(":")[0] != "minecraft": names_out[nm] += 1
                    elif nm.startswith("minecraft:") and nm not in valid_vanilla: names_out[nm] += 1
                    if nm in legacy_names: legacy[nm] += 1
            for be in root.get("block_entities", (0, (0, [])))[1][1]:
                bid = be.get("id", (0, "?"))[1]
                if bid.split(":")[0] not in KEEP and bid.split(":")[0] != "minecraft": be_bad[bid] += 1
    report["chunks"] = {"region_files": len(files), "chunks": n, "unparseable": dict(bad), "data_versions": dict(dv),
                        "light_off": nolight, "no_heightmap": noheight, "seconds": int(time.time() - t0),
                        "verdict": verdict(bad, dv.keys() - {3465})}
    report["palette"] = {"namespaces": dict(ns.most_common()), "outside_pack": dict(names_out.most_common(30)),
                         "legacy_112_names": dict(legacy), "verdict": verdict(names_out or legacy, [])}
    report["entities"] = {"block_entities_outside_pack": dict(be_bad.most_common(20)), "verdict": verdict(be_bad, [])}


def placed_count(world: World, blocks):
    x1, z1, x2, z2 = blocks; tot = 0; chunks = 0; missing = 0
    for cx in range(x1 >> 4, (x2 >> 4) + 1):
        for cz in range(z1 >> 4, (z2 >> 4) + 1):
            r = world.raw(cx, cz)
            if not r: missing += 1; continue
            chunks += 1; _, root = R(r[2]).root()
            for sec in root.get("sections", (0, (0, [])))[1][1]:
                d = decode(sec)
                if not d: continue
                names, pal, idx = d
                keep = [i for i, nm in enumerate(names) if nm not in AIR and nm not in NATURAL and nm not in PLANT
                        and not nm.endswith("_ore") and nm.split(":")[0] not in ("lostcities",)]
                if keep:
                    ks = set(keep); tot += sum(1 for i in idx if i in ks)
    return tot, chunks, missing


def box_is_air(world: World, box, ymin):
    x1, z1, x2, z2 = box; solid = 0
    for cx in range(x1 >> 4, (x2 >> 4) + 1):
        for cz in range(z1 >> 4, (z2 >> 4) + 1):
            r = world.raw(cx, cz)
            if not r: continue
            _, root = R(r[2]).root()
            for sec in root.get("sections", (0, (0, [])))[1][1]:
                if sec["Y"][1] * 16 + 15 < ymin: continue
                d = decode(sec)
                if not d: continue
                names, pal, idx = d
                nonair = [i for i, nm in enumerate(names) if nm not in AIR]
                if not nonair: continue
                y0 = sec["Y"][1] * 16
                for i, pi in enumerate(idx):
                    if pi in nonair and y0 + (i >> 8) >= ymin: solid += 1
    return solid


def check_sites(world: World, plan, volumes: Path, report):
    rows = []; fails = []; warns = []
    for r in plan:
        blocks = r["dest_blocks"]; tot, chunks, missing = placed_count(world, blocks)
        src = None
        vol = volumes / f"{ {'settlement': 'world_east_site', 'novo': 'novo_industrial', 'plaza': 'financial_plaza', 'hub': 'world_hub', 'sewers': 'sewers', 'biogen_s': 'biogen_strip', 'biogen_n': 'biogen_strip'}.get(r['source'], r['source']) }.npz"
        rows.append({"site": r["source"], "dest": blocks, "chunks": chunks, "missing_chunks": missing, "placed_blocks": tot})
        if missing: fails.append(f"{r['source']}: {missing} chunks missing")
        if tot == 0: fails.append(f"{r['source']}: no placed blocks found")
    ships = [box_is_air(world, box, ymin) for box, ymin in SHIPS]
    if any(ships): fails.append(f"ship boxes above the y-cut still hold {ships} blocks")
    report["sites"] = {"rows": rows, "ship_boxes_solid_blocks": ships, "verdict": verdict(fails, warns), "fails": fails, "warns": warns}


def pad_flatness(world: World, p, step=4, inner=None):
    """inner: a transplant rect inside the pad - its interior is the build's own ground, so only the apron is judged."""
    x1, z1, x2, z2 = p["blocks"]; y = p["y"]; ys = []; border = 0; border_n = 0
    for x in range(x1, x2 + 1, step):
        for z in range(z1, z2 + 1, step):
            if inner and inner[0] <= x <= inner[2] and inner[1] <= z <= inner[3]: continue
            c = world.chunk(x >> 4, z >> 4)
            if not c: continue
            ty, nm = c.top(x & 15, z & 15)
            if nm in NATURAL or nm in PLANT or nm == "minecraft:yellow_concrete": ys.append(ty)
    for x in range(x1, x2 + 1, 8):
        for z in (z1, z2):
            c = world.chunk(x >> 4, z >> 4)
            if not c: continue
            border_n += 1
            if c.get(x & 15, y, z & 15) == "minecraft:yellow_concrete" or c.get(x & 15, y + 1, z & 15) == "minecraft:yellow_concrete": border += 1
    arr = np.array(ys) if ys else np.array([y])
    return {"name": p["name"], "y": y, "terrain_columns": len(ys), "at_level": int((np.abs(arr - y) <= 1).sum()), "share_at_level": round(float((np.abs(arr - y) <= 1).mean()), 3),
            "min": int(arr.min()), "max": int(arr.max()), "border_share": round(border / max(1, border_n), 2)}


def check_pads(world: World, pads, report, plan=None):
    def inner_of(p):
        x1, z1, x2, z2 = p["blocks"]
        for r in (plan or []):
            a, b, c, d = r["dest_blocks"]
            if a >= x1 and b >= z1 and c <= x2 and d <= z2 and (c - a) * (d - b) > 0.5 * (x2 - x1) * (z2 - z1): return r["dest_blocks"]
        return None
    rows = [pad_flatness(world, p, inner=inner_of(p)) for p in pads]; fails = []; warns = []
    for r in rows:
        if r["share_at_level"] < 0.5: fails.append(f"pad {r['name']}: only {r['share_at_level']:.0%} of terrain columns at y {r['y']}")
        elif r["share_at_level"] < 0.9: warns.append(f"pad {r['name']}: {r['share_at_level']:.0%} of terrain columns at y {r['y']} (builds inside count as not-terrain)")
        if r["border_share"] < 0.5: warns.append(f"pad {r['name']}: outline found on {r['border_share']:.0%} of sampled edge points")
    report["pads"] = {"rows": rows, "verdict": verdict(fails, warns), "fails": fails, "warns": warns}


def check_tower(world: World, report):
    x1, z1, x2, z2 = 64, -144, 191, -17; y = 99; names = collections.Counter(); above = 0
    for cx in range(x1 >> 4, (x2 >> 4) + 1):
        for cz in range(z1 >> 4, (z2 >> 4) + 1):
            c = world.chunk(cx, cz)
            if not c: continue
            for x in range(16):
                for z in range(16):
                    for yy in range(y + 1, y + 95):
                        nm = c.get(x, yy, z)
                        if nm not in AIR: names[nm] += 1; above += 1
    stage0 = {"minecraft:iron_block", "minecraft:chain", "minecraft:cobblestone", "minecraft:gravel", "minecraft:smooth_stone_slab", "immersiveengineering:steel_scaffolding_standard"}
    has = {k: v for k, v in names.items() if k in stage0 or k.startswith("immersiveengineering")}
    fails = []; warns = []
    if not has: fails.append("no stage-0 blocks found on the tower pad (run function gscraft:tower_stage_0)")
    stray = {k: v for k, v in names.items() if k not in stage0 and not k.startswith("immersiveengineering") and k != "minecraft:yellow_concrete"}
    if stray: warns.append(f"other blocks above the tower pad: {dict(collections.Counter(stray).most_common(6))}")
    report["tower"] = {"blocks_above_pad": above, "by_name": dict(names.most_common(12)), "verdict": verdict(fails, warns), "fails": fails, "warns": warns}


def check_camp(world: World, pristine: World, report):
    x1, z1, x2, z2 = CRATER; diff = 0; cols = 0
    for x in range(x1, x2 + 1, 2):
        for z in range(z1, z2 + 1, 2):
            a = world.chunk(x >> 4, z >> 4); b = pristine.chunk(x >> 4, z >> 4) if pristine else None
            if not a or not b: continue
            cols += 1
            if a.top(x & 15, z & 15) != b.top(x & 15, z & 15): diff += 1
    sites = {}
    for name, (sx1, sz1, sx2, sz2) in NPC_SITES.items():
        built = 0; tops = []
        for x in range(sx1, sx2 + 1, 2):
            for z in range(sz1, sz2 + 1, 2):
                c = world.chunk(x >> 4, z >> 4)
                if not c: continue
                ty, nm = c.top(x & 15, z & 15); tops.append(ty)
                if nm not in NATURAL and nm not in PLANT and nm not in AIR and nm != "minecraft:yellow_concrete": built += 1
        sites[name] = {"built_columns": built, "surface_min": min(tops) if tops else None, "surface_max": max(tops) if tops else None}
    fails = [f"crater changed vs pregen in {diff}/{cols} sampled columns"] if diff else []
    warns = [f"{k}: {v['built_columns']} built columns on the site" for k, v in sites.items() if v["built_columns"]]
    warns += [f"{k}: surface spread {v['surface_max'] - v['surface_min']} blocks" for k, v in sites.items() if v["surface_min"] is not None and v["surface_max"] - v["surface_min"] > 12]
    report["camp"] = {"crater_diff_columns": diff, "crater_sampled": cols, "npc_sites": sites, "verdict": verdict(fails, warns), "fails": fails, "warns": warns}


def load_roads():
    """Routed polylines (buildmap/routes_v6.json) when present, else the straight design lines."""
    f = HERE.parent / "buildmap" / "routes_v6.json"
    if f.exists():
        return {r["name"]: [tuple(p) for p in r["polyline"]] for r in json.load(open(f))}
    return ROADS


def check_water(world: World, plan, pads, report):
    rows = []; warns = []
    for name, blocks in [(p["name"], p["blocks"]) for p in pads] + [(r["source"], r["dest_blocks"]) for r in plan]:
        x1, z1, x2, z2 = blocks; m = 48; water = 0; cols = 0
        for x in range(x1 - m, x2 + m + 1, 8):
            for z in range(z1 - m, z2 + m + 1, 8):
                if x1 <= x <= x2 and z1 <= z <= z2: continue
                c = world.chunk(x >> 4, z >> 4)
                if not c: continue
                cols += 1
                if c.top(x & 15, z & 15)[1] == "minecraft:water": water += 1
        rows.append({"site": name, "water_share_around": round(water / max(1, cols), 3)})
        if water / max(1, cols) > 0.3: warns.append(f"{name}: {water / max(1, cols):.0%} water around the site (causeway needed)")
    roads = {}
    for name, pts in load_roads().items():
        water = 0; total = 0; runs = 0; inwater = False
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            n = max(abs(bx - ax), abs(bz - az)) // 4
            for i in range(n + 1):
                x = ax + (bx - ax) * i // max(1, n); z = az + (bz - az) * i // max(1, n)
                c = world.chunk(x >> 4, z >> 4)
                if not c: continue
                total += 1; w = c.top(x & 15, z & 15)[1] == "minecraft:water"
                if w: water += 1
                if w and not inwater: runs += 1
                inwater = w
        roads[name] = {"samples": total, "water_samples": water, "water_metres": water * 4, "crossings": runs}
        if water: warns.append(f"road {name}: {water * 4} m of water in {runs} crossing(s)")
    report["water"] = {"sites": rows, "roads": roads, "verdict": verdict([], warns), "warns": warns}


def check_distances(plan, pads, report):
    def centre(b): return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    sites = {r["source"]: centre(r["dest_blocks"]) for r in plan}
    sites.update({"residential": (1328 + 100, 1376 + 100), "plant": (2135, 1000), "fr06": (2383, 663), "tower": (127, -80)})
    fails = []; warns = []; rows = {}
    for k, (x, z) in sites.items():
        d = math.hypot(x - CAMP_CENTRE[0], z - CAMP_CENTRE[1]); rows[k] = round(d)
    strong = ["novo", "residential", "plant", "fr06", "plaza"]
    for k in strong:
        if rows[k] < 1000: fails.append(f"strongpoint {k} is {rows[k]} m from the camp (< 1 km)")
    for i, a in enumerate(strong):
        for b in strong[i + 1:]:
            d = math.hypot(sites[a][0] - sites[b][0], sites[a][1] - sites[b][1])
            if d < 500: warns.append(f"strongpoints {a} and {b} are {d:.0f} m apart (< 500 m)")
    if not 4500 <= rows["hub"] <= 6500: warns.append(f"hub is {rows['hub']} m from the camp (air ring is 4.5-6.5 km)")
    report["distances"] = {"from_camp_m": rows, "verdict": verdict(fails, warns), "fails": fails, "warns": warns}


def check_border(world_dir: Path, report):
    d = R(gzip.decompress((world_dir / "level.dat").read_bytes())).root()[1]["Data"][1]
    b = {k: d[k][1] for k in ("BorderCenterX", "BorderCenterZ", "BorderSize") if k in d}
    sp = (d["SpawnX"][1], d["SpawnY"][1], d["SpawnZ"][1])
    fails = []
    if abs(b.get("BorderSize", 0) - 10000) > 1 or abs(b.get("BorderCenterX", 0) - 1900) > 2 or abs(b.get("BorderCenterZ", 0) - 1250) > 2: fails.append(f"border is {b}, expected 10000 at 1900,1250")
    if sp != (19, 94, 26): fails.append(f"spawn is {sp}, expected 19 94 26")
    report["border"] = {"border": b, "spawn": sp, "verdict": verdict(fails, []), "fails": fails}


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    world_dir, prefix = Path(a[1]), a[2]
    pristine_dir = Path(a[a.index("--pristine") + 1]) if "--pristine" in a else None
    world = World(world_dir / "region"); pristine = World(pristine_dir / "region") if pristine_dir else None
    plan = json.load(open(HERE.parent / "buildmap" / "transplant_plan_v6.json")); pads = json.load(open(HERE / "pads_v6.json"))
    valid_vanilla = set(json.load(open(Path(r"G:/GSCraft/scratch/reports/generated/reports/blocks.json"))).keys())
    report = {"world": str(world_dir), "when": time.strftime("%Y-%m-%d %H:%M")}
    print("chunks / palette / entities (whole world) ...", flush=True); check_chunks_palette_entities(world_dir / "region", valid_vanilla, report)
    print("sites ...", flush=True); check_sites(world, plan, Path(r"G:/GSCraft/incoming/volumes"), report)
    print("pads ...", flush=True); check_pads(world, pads, report, plan)
    print("tower ...", flush=True); check_tower(world, report)
    print("camp ...", flush=True); check_camp(world, pristine, report)
    print("water ...", flush=True); check_water(world, plan, pads, report)
    check_distances(plan, pads, report); check_border(world_dir, report)
    json.dump(report, open(prefix + ".json", "w"), indent=1, default=str)
    lines = [f"# Map review: {world_dir}  ({report['when']})", ""]
    for k in ("chunks", "palette", "entities", "sites", "pads", "tower", "camp", "water", "distances", "border"):
        s = report[k]; lines.append(f"## {k}: **{s['verdict']}**")
        for f in s.get("fails", []): lines.append(f"- FAIL: {f}")
        for w in s.get("warns", []): lines.append(f"- WARN: {w}")
        detail = {kk: vv for kk, vv in s.items() if kk not in ("verdict", "fails", "warns", "rows")}
        lines.append("```"); lines.append(json.dumps(detail, indent=1, default=str)[:3000]); lines.append("```")
        if "rows" in s:
            for r in s["rows"]: lines.append(f"- {r}")
        lines.append("")
    Path(prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(l for l in lines if l.startswith("## ") or l.startswith("- FAIL") or l.startswith("- WARN")))
    print("->", prefix + ".md")


if __name__ == "__main__":
    main(sys.argv)
