# GSCraft Wasteland — Generated structures: what stays, what goes, and how

Draft 1, 2026-09-03. The census of the built v6 world (`tools/structures_v6.json`, every structure
start in the 10 km box) found 3,292 structures: 964 that are sites in their own right — bunkers, boss
towers, villages, outposts, ancient cities, mansions, the Man-From-The-Fog houses — and 2,328
background ones (mineshafts, shipwrecks, ocean ruins, ruined portals, buried treasure). The owner's
verdict: **far too dense**. A bunker every 200 m and a boss tower every 150 m turns the wasteland
into a theme park and drowns the six built sites the whole design is about. This document is the
placement: the rules, the kept list, and the way to make the world match.

## 1. Rules

1. **Nothing generated within 350 m of a designed site** — the six strongpoints and loot sites, the
   district, the hub, the runway, the camp outline. The built sites are the story; the generated ones
   are the texture between them.
2. **Kept sites stand apart**: bunkers 600 m from each other, boss towers 900 m, capitals 1.2 km,
   outposts 1 km, ancient cities 1.5 km.
3. **Caps per range ring**, so density follows the acts: foot range (0–1.5 km) almost empty — two
   bunkers, one Man-From-The-Fog house — road range (1.5–4 km) carries the middle game, the air ring
   (4.5–6.5 km) the expedition finds; nothing beyond 6.5 km is kept.
4. **Near a road wins**: among candidates that pass the rules, the ones nearest a built road are
   chosen first, because those are the ones players will actually reach.
5. **Background structures are left alone**: mineshafts, shipwrecks, ocean ruins, portals and buried
   treasure are underground or underwater, cost nothing, and give the wet seed its texture.

`tools/structure_plan.py` applies the rules to the census and writes `buildmap/structure_plan_v7.json`
(keep and prune lists with coordinates and the reason for every prune) and the map
`docs/renders/structures_v6.png` (kept sites bold, pruned faint, the six sites boxed, the roads drawn).

## 2. The result

| Type | In the box | Kept | foot / road / air | Role |
|---|---|---|---|---|
| Apotheosis boss towers | 439 | **11** | 0 / 5 / 6 | one elite per act range; the garrison tables' named elites can be these |
| Underground Bunkers | 284 | **14** | 2 / 6 / 6 | the U-chapter's side dungeons; the two in foot range are Act I's first "go down" |
| Villages (Lukis capitals, hostile) | 45 | **10** | 0 / 4 / 6 | bandit settlements; J9 visits four of the air-ring ones |
| Man-From-The-Fog houses | 35 | 6 | 0 / 3 / 3 | horror set pieces |
| Pillager outposts | 21 | 6 | 0 / 3 / 3 | armed-pillager garrisons on the roads |
| Ancient cities | 23 | 4 | 0 / 1 / 3 | Warden ground; the fallback boss lives here |
| Trail ruins, igloos, pyramids, monuments, strongholds, mansion | 117 | 16 | — | expedition-tier finds |
| **Total sites** | **964** | **67** | 2 / 26 / 39 | |
| Background (mineshafts, wrecks, ruins, portals, treasure) | 2,328 | all | — | left alone |

Sixty-seven sites across 78 km² is one every 1.2 km — a find per trip, not a find per minute — and
the foot range around the camp is nearly empty, which is what Act I needs: the players learn the
camp's own ruins, the glass tower, the acacia hall and Novo before the map opens up.

## 3. How to make the world match

Two routes. Both are scripted; the difference is where the work runs and what it costs.

**A. Regenerate — world build v7 (recommended).** A datapack override sets every structure set of
the pruned types to a spacing no chunk can satisfy (or removes the set), the 10 km box is
pre-generated again from the same seed, and the 67 kept sites are placed back at their census
coordinates with `/place structure` from the plan file. Then the whole v6 pipeline re-runs unchanged
— pads, transplants, roads, camp ruins, torches, dossiers, furnishing — because every one of those is
a script reading a JSON. Cost: about 2 h 15 of Chunky on the build machine (20 GB heap; this
workstation cannot), 11 min `buildv6.py`, 20 min roads, 35 min review, an hour of uploads. Result: a
clean world whose only structures are the chosen ones, terrain identical everywhere else.
*Caveat:* a re-placed structure is a fresh instance of the same template family, not the exact
building that stood there; only the position is preserved, which is what the plan needs.

**B. Prune in place.** For each of the 897 pruned starts, clear the blocks inside the start's
bounding box above the surface, patch the surface with the surrounding terrain, drop the start and
its references from the chunk NBT, and for bunkers fill the underground volume. Runs on this
workstation against the local region set, then uploads only the touched region files. Cost: a day of
tool-writing (`terrain.py` has the fill and smooth primitives; the bounding boxes are in the census
starts) and craters where 439 towers stood. Result: the same world minus the structures, with scars.

**A' - Regenerate around what we built (the route the tools implement).** A fresh world from the seed would
lose the v5 chunks - the transplanted player district, the 29 old-world sites and the camp - so the build
machine does this instead: `tools/carve_regen.py` copies the pre-generated world and drops every chunk
outside the v5 rectangles and the camp (15,502 chunks kept, 405,699 dropped); `tools/structure_override.py`
writes the datapack `build/datapacks/gscraft_worldgen` (16 structure sets at placement frequency 0: the four
Apotheosis towers, the Man house, the bunkers, and the vanilla villages, outposts, ancient cities, trail ruins,
igloos, pyramids, jungle temples, monuments, mansions, strongholds) which goes into the carved world's
`datapacks/` before the first boot; `tools/localpregen.py` then regenerates the dropped chunks - same seed, same
terrain, same Lost Cities, no pruned structures - in the same 2 h 15 min; `tools/place_kept.py` puts the 67 kept sites back at their census coordinates in batches (force-load the 3x3
chunks around each, wait, `place structure`, release - the command refuses unloaded chunks, and a single
function that force-loads everything stalls the server; the generated functions `gscraft:forceload_kept_structures`
/ `place_kept_structures` / `unforceload_kept_structures` remain for hand use in small groups); then `buildv6.py`, roads, the camp functions (ruins, torches, dossiers, furnishing),
review, release, deploy. A structure whose start chunk is inside a kept rectangle survives the carve; those
are inside the 350 m buffers and are the only in-place pruning still owed.

Route A is the right one: the world is already reproducible from scripts, that is the whole point of
the pipeline, and the scars of route B would need a smoothing pass anyway. The v7 build goes on the
Phase B list; **until it lands, mob spawning stays off** (HANDOFF), which also keeps the 439 boss
spawners quiet.

## 4. What Phase A should still look at

The visual pass is the check on this plan: fly four of the kept boss towers and four bunkers
(nearest the camp first — positions in the plan file) and say whether the templates read as
wasteland or as fantasy. If the Apotheosis towers look wrong for the setting, the cap goes to zero
and the elites come from In Control! alone; nothing else changes.

Related: `gscraft-map-design.md` §2.3 (the loot-site list), `gscraft-mod-capabilities.md` §1,
`tools/structure_plan.py`, `buildmap/structure_plan_v7.json`, `docs/renders/structures_v6.png`.
