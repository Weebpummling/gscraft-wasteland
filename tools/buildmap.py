#!/usr/bin/env python3
"""
buildmap.py - turn region scans into a build inventory.

    python buildmap.py --live <live overworld region dir> --old <old overworld region dir> --out <dir>

For each world: classify chunks as "built", cluster adjacent built chunks into sites, and report each
site's block-coordinate bounding box, size, block entities, and the non-vanilla namespaces it depends on.
Then match old-world built chunks against the live world by content signature to find the transplant
offset that was used, and list any old-world sites that have no counterpart in the live world.

Writes <out>/buildmap.txt (human) and <out>/builds.json (for transplant.py).
"""

import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import scanregion as sr  # noqa: E402

# Namespaces whose placed blocks only ever come from worldgen in this pack, never from a player.
WORLDGEN_ONLY = {"spore", "irons_spellbooks", "horror_element_mod", "from_the_caves", "minetraps",
                 "modern_structures", "tf_dnv"}
# In this pack Lost Cities fills city ground with IE hempcrete; a chunk that is mostly hempcrete is terrain.
TERRAIN_FILL = {"immersiveengineering:hempcrete", "immersiveengineering:hempcrete_pillar"}


def chunk_rows(region_dir: Path):
    """Yield (cx, cz, placed:Counter, nbe:int, be_ids:Counter, ntypes:int) for every chunk."""
    for f in sorted(region_dir.glob("r.*.mca")):
        for chunk in sr.read_region(f):
            cx, cz = chunk.get("xPos"), chunk.get("zPos")
            if cx is None:
                continue
            placed, types = Counter(), set()
            for sec in chunk.get("sections", []):
                for name, n in sr.count_section(sec).items():
                    types.add(name)
                    ns = name.split(":", 1)[0]
                    if name in sr.NATURAL or ns in sr.GENERATED_NAMESPACES or sr.ORE_RE.search(name):
                        continue
                    if ns in WORLDGEN_ONLY or name in TERRAIN_FILL:
                        continue
                    placed[name] += n
            bes = chunk.get("block_entities", [])
            be_ids = Counter(b.get("id", "?") for b in bes)
            yield cx, cz, placed, len(bes), be_ids, len(types)


STRONG_BE = {"minecraft:beacon", "minecraft:command_block", "minecraft:chain_command_block",
             "minecraft:repeating_command_block", "minecraft:jukebox", "minecraft:enchanting_table",
             "minecraft:brewing_stand", "minecraft:beehive", "minecraft:chiseled_bookshelf"}


def strong_player_signal(placed: Counter, nbe: int, be_ids: Counter) -> bool:
    """Signals that Lost Cities / apocalypse-pack structures do not produce."""
    modded = sum(n for name, n in placed.items() if not name.startswith("minecraft:"))
    if modded >= 200:
        return True
    if any(be_ids.get(k, 0) for k in STRONG_BE):
        return True
    if be_ids.get("minecraft:dispenser", 0) >= 12 or be_ids.get("minecraft:hopper", 0) >= 12:
        return True
    return False


def is_built(placed: Counter, nbe: int, ntypes: int) -> bool:
    total = sum(placed.values())
    if total == 0 and nbe == 0:
        return False
    top = placed.most_common(1)[0][1] if placed else 0
    fill = top / total if total else 0
    # Real builds: several block entities, or a decent volume of varied placed blocks.
    if nbe >= 4:
        return True
    if total >= 250 and ntypes >= 35 and fill < 0.9:
        return True
    return False


def cluster(built: dict):
    """8-connected clustering of built chunk coords -> list of sets."""
    seen, out = set(), []
    for start in built:
        if start in seen:
            continue
        q, comp = deque([start]), set()
        seen.add(start)
        while q:
            cx, cz = q.popleft(); comp.add((cx, cz))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (cx + dx, cz + dz)
                    if n in built and n not in seen:
                        seen.add(n); q.append(n)
        out.append(comp)
    return out


def describe(world: str, built: dict):
    sites = []
    for comp in cluster(built):
        xs = [c[0] for c in comp]; zs = [c[1] for c in comp]
        placed, bes, deps = Counter(), Counter(), Counter()
        for c in comp:
            p, nbe, be_ids, _ = built[c]
            placed.update(p); bes.update(be_ids)
            for name, n in p.items():
                ns = name.split(":", 1)[0]
                if ns != "minecraft":
                    deps[ns] += n
        sites.append({
            "world": world, "chunks": len(comp),
            "chunk_min": [min(xs), min(zs)], "chunk_max": [max(xs), max(zs)],
            "block_min": [min(xs) * 16, min(zs) * 16], "block_max": [max(xs) * 16 + 15, max(zs) * 16 + 15],
            "placed": sum(placed.values()), "block_entities": sum(bes.values()),
            "top_blocks": placed.most_common(8), "top_block_entities": bes.most_common(6),
            "dependencies": deps.most_common(),
            "_chunks": sorted(comp),
        })
    # Generated structures recur with the same block-entity mix (chest + spawner + blast furnace,
    # sign + campfire + decorated pot...); a player build is one of a kind. Spawners are never
    # player-placed in survival.
    from collections import Counter as _C
    fp = _C()
    for s in sites:
        s["fingerprint"] = frozenset(k for k, _ in s["top_block_entities"][:3])
        fp[s["fingerprint"]] += 1
    for s in sites:
        s["repeats"] = fp[s["fingerprint"]] if s["fingerprint"] else 1
        spawners = dict(s["top_block_entities"]).get("minecraft:mob_spawner", 0)
        s["generated"] = (s["repeats"] >= 2 and s["block_entities"] > 0) or spawners >= 5
        s["fingerprint"] = sorted(s["fingerprint"])
    sites.sort(key=lambda s: (s["placed"] + 20 * s["block_entities"]), reverse=True)
    return sites


def signature(placed: Counter, nbe: int, ntypes: int):
    top = placed.most_common(3)
    return (sum(placed.values()), nbe, ntypes, tuple(k for k, _ in top))


def main(argv):
    args = dict(zip(argv[1::2], argv[2::2]))
    live_dir, old_dir, out = Path(args["--live"]), Path(args["--old"]), Path(args["--out"])
    out.mkdir(parents=True, exist_ok=True)

    worlds = {}
    for label, d in (("live", live_dir), ("old", old_dir)):
        built = {}
        total = 0
        for cx, cz, placed, nbe, be_ids, ntypes in chunk_rows(d):
            total += 1
            if is_built(placed, nbe, ntypes):
                built[(cx, cz)] = (placed, nbe, be_ids, ntypes)
        worlds[label] = built
        print(f"{label}: {total} chunks scanned, {len(built)} built")

    live, old = worlds["live"], worlds["old"]

    # Offset voting: for each old built chunk, find live chunks with the same signature.
    live_by_sig = defaultdict(list)
    for c, (p, nbe, _, nt) in live.items():
        live_by_sig[signature(p, nbe, nt)].append(c)
    votes = Counter()
    for c, (p, nbe, _, nt) in old.items():
        for lc in live_by_sig.get(signature(p, nbe, nt), []):
            votes[(lc[0] - c[0], lc[1] - c[1])] += 1
    best = votes.most_common(3)
    dx, dz = best[0][0] if best else (0, 0)

    matched = changed = 0
    missing = {}
    moved = []
    for c, v in old.items():
        target = (c[0] + dx, c[1] + dz)
        if target not in live:
            missing[c] = v
        elif signature(v[0], v[1], v[3]) == signature(live[target][0], live[target][1], live[target][3]):
            matched += 1; moved.append(c)
        else:
            changed += 1; moved.append(c)
    mx = [c[0] for c in moved]; mz = [c[1] for c in moved]
    moved_bbox = (min(mx), min(mz), max(mx), max(mz)) if moved else (0, 0, 0, 0)
    # Old chunks never transplanted AND outside the moved block AND with a strong player signal.
    strong_missing = {c: v for c, v in missing.items()
                      if not (moved_bbox[0] <= c[0] <= moved_bbox[2] and moved_bbox[1] <= c[1] <= moved_bbox[3])
                      and strong_player_signal(v[0], v[1], v[2])}

    lines = []
    lines.append(f"Transplant offset old->live by signature vote: {best} (chunks); using dx={dx}, dz={dz} = blocks ({dx*16}, {dz*16})")
    lines.append(f"old built chunks: {len(old)} -> identical in live at that offset: {matched}; present but edited since: {changed}; "
                 f"NO built chunk at the target position (never transplanted): {len(missing)}")
    lines.append(f"block already moved by the previous admin: old chunks x {moved_bbox[0]}..{moved_bbox[2]}, z {moved_bbox[1]}..{moved_bbox[3]} "
                 f"= old blocks ({moved_bbox[0]*16}..{moved_bbox[2]*16+15}, {moved_bbox[1]*16}..{moved_bbox[3]*16+15}); "
                 f"in live: chunks x {moved_bbox[0]+dx}..{moved_bbox[2]+dx}, z {moved_bbox[1]+dz}..{moved_bbox[3]+dz}")
    lines.append(f"never-transplanted old chunks OUTSIDE that block with a strong player signal: {len(strong_missing)}")
    lines.append("")

    result = {"offset_old_to_live_chunks": [dx, dz], "moved_bbox_old_chunks": list(moved_bbox), "sites": {}}
    for label, built in (("live", live), ("old-only", strong_missing)):
        sites = describe(label, built)
        result["sites"][label] = sites
        n_player = sum(1 for s in sites if not s.get("generated"))
        lines.append(f"=== {label.upper()} BUILD SITES ({len(sites)} clusters, {n_player} judged player-built) ===")
        shown = [s for s in sites if not s.get("generated")][:25] + [s for s in sites if s.get("generated")][:8]
        for i, s in enumerate(shown, 1):
            deps = ", ".join(f"{ns}:{n}" for ns, n in s["dependencies"][:8]) or "vanilla only"
            tops = ", ".join(f"{k.split(':',1)[-1]}x{v}" for k, v in s["top_blocks"][:6])
            tbes = ", ".join(f"{k.split(':',1)[-1]}x{v}" for k, v in s["top_block_entities"][:4])
            tag = f"  [GENERATED x{s['repeats']}]" if s.get("generated") else "  [PLAYER BUILD]"
            lines.append(f"{i:>2}. {s['chunks']:>3} chunks  blocks x {s['block_min'][0]}..{s['block_max'][0]}  z {s['block_min'][1]}..{s['block_max'][1]}"
                         f"   placed {s['placed']:>6}  BEs {s['block_entities']:>4}{tag}")
            lines.append(f"      deps: {deps}")
            lines.append(f"      blocks: {tops}")
            lines.append(f"      BEs: {tbes}")
        lines.append("")

    # Global dependency tally across live sites only (what the rebuild must satisfy).
    dep_total = Counter()
    for s in result["sites"]["live"]:
        if s.get("generated"):
            continue
        for ns, n in s["dependencies"]:
            dep_total[ns] += n
    n_gen = sum(1 for s in result["sites"]["live"] if s.get("generated"))
    lines.append(f"=== DEPENDENCIES OF LIVE PLAYER BUILD SITES (generated structures excluded: {n_gen}) ===")
    for ns, n in dep_total.most_common():
        lines.append(f"{n:>10}  {ns}")
    # And the specific block names per namespace, for a remap table.
    block_total = Counter()
    for s in result["sites"]["live"]:
        if s.get("generated"):
            continue
        for name, n in s["top_blocks"]:
            block_total[name] += n
    lines.append("")
    lines.append("=== NON-VANILLA BLOCKS IN LIVE SITES (top 60, from per-site top lists) ===")
    for name, n in block_total.most_common(60):
        if not name.startswith("minecraft:"):
            lines.append(f"{n:>10}  {name}")

    # Complete block lists for namespaces that are being cut: the remap table has to cover every one.
    CUT = {"create", "createdeco", "createbigcannons", "crusty_chunks", "survival_instinct", "movingelevators",
           "waterframes", "doggytalents", "waystones", "reddensstonelantern", "chisel", "antiblocksrechiseled",
           "factory_blocks"}
    per_ns = defaultdict(Counter)
    for label in ("live", "old-only"):
        for site in result["sites"][label]:
            if site.get("generated"):
                continue
            for c in site["_chunks"]:
                src = live if label == "live" else old
                for name, n in src[c][0].items():
                    ns = name.split(":", 1)[0]
                    if ns in CUT:
                        per_ns[ns][name] += n
    lines.append("")
    lines.append("=== EVERY BLOCK FROM A CUT OR BUILD-DEPENDENCY NAMESPACE IN PLAYER SITES (live + never-transplanted old) ===")
    remap_skeleton = {}
    for ns in sorted(per_ns, key=lambda k: -sum(per_ns[k].values())):
        lines.append(f"-- {ns}: {sum(per_ns[ns].values())} blocks, {len(per_ns[ns])} kinds")
        for name, n in per_ns[ns].most_common():
            lines.append(f"     {n:>8}  {name}")
            remap_skeleton[name] = None
    (out / "remap_skeleton.json").write_text(json.dumps(remap_skeleton, indent=1), encoding="utf-8")

    # Transplant plan. Live: one rectangle around the major player sites (the district), plus each
    # outlier site on its own. Old: each strong never-transplanted site, shifted by the known offset.
    plan = []
    major = [x for x in result["sites"]["live"] if not x.get("generated") and (x["placed"] >= 5000 or x["block_entities"] >= 100)]
    if major:
        xs = [x["chunk_min"][0] for x in major] + [x["chunk_max"][0] for x in major]
        zs = [x["chunk_min"][1] for x in major] + [x["chunk_max"][1] for x in major]
        # Drop far outliers from the district rectangle: anything more than 60 chunks from the median.
        import statistics as _st
        cxm, czm = _st.median(xs), _st.median(zs)
        core = [x for x in major if abs((x["chunk_min"][0] + x["chunk_max"][0]) / 2 - cxm) <= 60
                and abs((x["chunk_min"][1] + x["chunk_max"][1]) / 2 - czm) <= 60]
        xs = [x["chunk_min"][0] for x in core] + [x["chunk_max"][0] for x in core]
        zs = [x["chunk_min"][1] for x in core] + [x["chunk_max"][1] for x in core]
        district = [min(xs) - 1, min(zs) - 1, max(xs) + 1, max(zs) + 1]
        # The previous admin already moved one block of the old world into the live world; the
        # players regard everything inside it as theirs. Carry that whole block, plus anything major built outside it since.
        mb = [moved_bbox[0] + dx, moved_bbox[1] + dz, moved_bbox[2] + dx, moved_bbox[3] + dz]
        district = [min(district[0], mb[0]), min(district[1], mb[1]), max(district[2], mb[2]), max(district[3], mb[3])]
        core = [x for x in major if district[0] <= x["chunk_min"][0] and x["chunk_max"][0] <= district[2]
                and district[1] <= x["chunk_min"][1] and x["chunk_max"][1] <= district[3]]
        plan.append({"source": "live", "offset": [0, 0], "chunks": district, "what": f"player district ({len(core)} major sites)",
                     "chunk_count": (district[2] - district[0] + 1) * (district[3] - district[1] + 1)})
        for x in major:
            if x in core:
                continue
            plan.append({"source": "live", "offset": [0, 0],
                         "chunks": [x["chunk_min"][0] - 1, x["chunk_min"][1] - 1, x["chunk_max"][0] + 1, x["chunk_max"][1] + 1],
                         "what": "live outlier site", "chunk_count": x["chunks"], "placed": x["placed"], "block_entities": x["block_entities"]})
        lines.append("")
        lines.append(f"=== TRANSPLANT PLAN ===")
        lines.append(f"live district: chunks x {district[0]}..{district[2]}, z {district[1]}..{district[3]} = blocks "
                     f"({district[0]*16}..{district[2]*16+15}, {district[1]*16}..{district[3]*16+15}), {plan[0]['chunk_count']} chunks, {len(core)} major sites inside")
        for r in plan[1:]:
            lines.append(f"live outlier: chunks {r['chunks']}  placed {r.get('placed')}  BEs {r.get('block_entities')}")
    for site in result["sites"]["old-only"]:
        if dict(site["top_block_entities"]).get("minecraft:mob_spawner", 0) >= 5:
            continue  # only spawner-heavy clusters are excluded; adjacent halves of one build share a fingerprint
        plan.append({"source": "old", "offset": [dx, dz],
                     "chunks": [site["chunk_min"][0] - 1, site["chunk_min"][1] - 1, site["chunk_max"][0] + 1, site["chunk_max"][1] + 1],
                     "what": "old never-transplanted site", "chunk_count": site["chunks"], "placed": site["placed"], "block_entities": site["block_entities"]})
        lines.append(f"old site -> live at +({dx},{dz}): old chunks {plan[-1]['chunks']}  placed {site['placed']}  BEs {site['block_entities']}  "
                     f"top BEs {', '.join(k.split(':',1)[-1]+'x'+str(v) for k, v in site['top_block_entities'][:4])}")
    (out / "transplant_plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    for label in ("live", "old-only"):
        for site in result["sites"][label]:
            site.pop("_chunks", None)

    text = "\n".join(lines)
    print(text)
    (out / "buildmap.txt").write_text(text, encoding="utf-8")
    (out / "builds.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"\n-> {out / 'buildmap.txt'}\n-> {out / 'builds.json'}")


if __name__ == "__main__":
    main(sys.argv)
