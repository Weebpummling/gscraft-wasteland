# GSCraft Wasteland — map v8 plan (roads and terrain first)

> **Realigned 2026-09-07 — the camp.** Sections 2, 3, 4, 5 and 9 were corrected in place to the camp's site in
> Skadowsky, east of the south-west bridge. See `docs/gscraft-skadowsky-camp.md`.


Owner's order of work (2026-09-04), after v7's flight: the map is redesigned from the ground up, denser and smaller
(a 4 km square), with the road network and the terrain as its spine. Nothing is generated until each step is signed off.

1. **Road network** — planned, or copied from a real place (this document, section 1).
2. **Terrain heights** — the relief the map is going for, decided before anything is built (section 2).
3. Roads + terrain = the spine. **Finalised before sectors are placed.** The roads follow the Skadowsky vocabulary
   (stone / andesite / gravel carriageway with andesite walls, gravel service tracks, grey-concrete viaducts on pylons).
4. **Sector placement** for a balanced map (camp, Skadowsky sector, the preserved player builds, Novo, plaza + sewers,
   settlement, Bio Gen, hub, runway, the 29 old sites, the Woods).
5. Sectors placed, then adjusted and cleaned up until they look right.
6. Roads connected to each sector's own road stubs (gates found by scanning each build's edges, not box midpoints).
7. Lost Cities buildings placed as modules inside the city zones.
8. Props and random dressing fill the rest.

Tools: the plan is authored as data (this document + `buildmap/plan_v8/`), the terrain is built by WorldPainter's
scripting host from a heightmap and masks generated from the plan, builds transplant with the existing pipeline, roads
are graded into the terrain and surfaced to match what they connect. The interactive planner page (`tools/planner/`)
is retired: the artifact viewer would not let the owner move or draw reliably, and boxes joined by lines are not a
realistic network anyway.

## 1. Road network candidates (real places, OpenStreetMap, 4 km x 4 km, north up)

Rendered in `scratch/osm/candidates.png` (1 px = 4 blocks); raw data `scratch/osm/<name>.json` (roads, rail, water,
land use, buildings). All three fit the 4 km border; the roads, rail and water copy across at 1 m = 1 block.

| Candidate | What the network gives | Terrain (real) | Fit |
|---|---|---|---|
| **Pripyat** (51.405 N 30.055 E) | one main road across the cell, the town's avenues and blocks in the centre, a rail line along the south with a station, the plant road east, a lake and river arm north, forest around | flat, 105-120 m | **recommended**: an abandoned town as the city zone is exactly the Lost Cities role; sparse network outside it leaves room for the sectors and the Woods; the rail gives the Skadowsky sector its line |
| Tosno outskirts (59.545 N 30.880 E) | the M10 highway and the Moscow-Petersburg rail as a diagonal corridor, a secondary road grid, the Tosna river meandering with several bridges, industry NW, dense dacha grid E | flat, 30-40 m | richest network; the dacha grid must be thinned to its main streets or the whole cell reads as town |
| Skadovsk (46.125 N 32.905 E) | a rectangular port-town grid, two radial roads, rail into the port, coast to the south | flat steppe, 5-10 m | the sector's namesake; the flattest and least varied; a coast is a border, not a playground |

Recommendation: Pripyat's network as the skeleton, with Tosno's highway-and-rail corridor idea borrowed if a stronger
east-west spine is wanted. Decision: owner.

### 1b. Ready-made Pripyat worlds (owner-supplied, 2026-09-04)

Two downloaded packs in `G:/GSCraft/incoming/pripyat/` replace the OpenStreetMap tracing: the roads, rail, river,
lake, town and plant already exist as blocks. Census by `tools/census_world.py` + `tools/crop_render.py`, renders in
`incoming/census/`.

| Pack | Version | What it holds | Ground | Fit |
|---|---|---|---|---|
| **Pripyat After the Accident (Outdated Project)** | 1.16.5 (DataVersion 2586), Bukkit world, vanilla blocks only (498 ids) | the whole exclusion zone: Pripyat town (1.85 x 2.25 km grid of 9-storey blocks, avenues, the diagonal main road), the ChNPP complex (reactor block, turbine hall, cooling towers, switchyard), the cooling pond and river, the rail yard, roads between, forest and fields; built extent about 3.7 x 4.4 km | flat, natural ground y 65, buildings to 89 (town) / 113 (plant) | **the basis**: roads, rail, water, land use and two whole sectors in one piece; upgrade path = vanilla `--forceUpgrade` (`upgrade112.py`, running into `scratch/upgrade/pripyat_after`) |
| **ПРИПЯТЬ** | 1.21.8 (DataVersion 4440), vanilla, 31 block ids newer than 1.20.1 (tuff and copper variants, short grass) | the town centre only, 1.0 x 1.5 km: stadium, central square, culture palace, hotel, shops, a few blocks, dense forest around | superflat floor at y -61 with the town at y -5..48 | **the detail donor** for the town centre: overlays the same area of the older world once aligned; needs `tools/remap121.json` (drafted) and a 1.20.1 rewrite (my anvil tools) |

Decision to take: the older world as the spine (its roads and rail are the network; the town and the plant are two of
the sectors; the lake and river are the water), trimmed to the border; our sectors (camp, Skadowsky, the player builds,
Novo, plaza, settlement, hub, runway, the Woods) placed on the open land along its roads; the 1.21 centre swapped in
where it is better. Attribution: both packs' authors to be credited in the docs and release notes (owner to supply the
sources).

## 2. Terrain heights (over the Pripyat footprint; draft for decision, render `incoming/census/height_plan_step2.png`)

The source ground is y 65 everywhere (superflat), water at 62. Everything built keeps its level: the town, the plant,
every road and rail line, the lake and river banks. Relief is authored only on open land, graded so no road climbs
steeper than 1:8 and the town and plant edges never see a wall.

| Zone | Where (blocks) | Heights | Purpose |
|---|---|---|---|
| A  The east plateau | the open land between the town's east edge and the lake, about x -2150..-1250, z -2700..-2000 | 84-90, a basin cut down to the lake level (63) at its centre; slopes 1:6 to the town side, a bluff to the lake | the only high ground in the middle of the map. It was built and it still stands as terrain, but nothing was ever built on it: there is no crater lake and no Warium island, and the camp is in Skadowsky (section 9) |
| B  West ridge | the western strip x -4000..-3450, from z -2600 south to the border | 95-105, a continuous wall with two saddles at 88 where roads cross | the map's western edge reads as a wall, not a fence |
| C  The Woods | the forest and fields south of the town, x -3400..-1600, z -1400..100 | 66-74 rolling, dense trees, a stream at 63 running north to the river | the wilderness zone of the design |
| D  Rolling fields | the open land east of the town and around the lake's south shore, and the strip north of the town (D2) | 65-72, folds of 2-4 blocks over 100 m | ground for the placed sectors (Skadowsky, Novo, plaza, settlement, runway) |
| Fixed | town (x -3700..-1850, z -3700..-1450), plant (x -1100..1120, z -350..1870), the rail yard and every road | 65 | as built |
| Water | lake, river, channels | 62, banks 65 | as built; the Woods stream added |

**Border: A chosen (owner, 2026-09-04).** The options were:
- **A: 5.1 x 4.6 km, everything in place** - x -3900..1200, z -3900..700. Town, lake, river, plant and rail yard exactly
  where the pack has them. Longest trip (town centre to plant) 4.3 km.
- **B: 4.2 x 4.2 km, plant moved** - x -3900..300, z -3900..300, the plant complex transplanted 900 blocks north-west
  onto the lake's south shore (its rail and road links rebuilt in step 8). Longest trip 3.2 km. Denser, closer to the
  4 km the owner asked for; costs the pack's true geography between lake and plant.

Ungenerated holes inside either border (black in the render) are filled by the terrain build.

## 3. The spine: roads and terrain (draft, 2026-09-04)

Inputs: the upgraded world `scratch/upgrade/pripyat_after/world` (1.20.1; the cell's 14,877 ungenerated chunks filled
flat at y 65 by `tools/flatfill.py`), the per-block surface class raster (`tools/classraster.py`: ground, road, rail,
water, building, tree, bare) and `tools/heightplan.py`, which authors the relief from the section-2 zones.

Results (seed 7): 18.3 % of the cell's columns are fixed (roads, rail, water, buildings, with a 24-block apron); 8.6 M
columns move, 53 M blocks of fill and 8.9 M of cut, almost all of it the west ridge (mean 94.6, top 103). Existing
hills - the pack has a low rise of 70-77 inside the river bend - are kept and the relief adds to them. The east plateau
zone (A) comes out low (mean 72, top 88) because scattered sheds inside it pin their surroundings; no camp sector is
placed there to grade that ground, so the relief stands as it was built, and stands empty (section 9).
Woods 65-77 (mean 68), fields 61-74. Renders:
`incoming/census/heightplan/height_preview.png`, statistics in `height_stats.txt`.

Road network (`tools/roadnet.py`): 158 km of road centre line extracted from the blocks - the town's grid and ring road,
the main road south-east to the plant, the diagonal to the south-west, the plant's internal roads, the field tracks; 834
dead ends, of which the ones at the border are the map's exits and the rest are stubs sectors can hook onto. The skeleton
is noisy inside paved courtyards (16 k "junctions"); it is pruned before it is used for gates. The rail embankment
reads as bare ground (coarse dirt) rather than rails and is traced separately. Render: `incoming/census/roadnet/roadnet.png`.

Next: apply the heightmap to the world (column raise/cut with the grade tool's column writer; ground cover and trees
follow with WorldPainter), then a fly-through render; then step 4, sector placement on the rolling fields.

## 4. Sector placement - art pass (owner rules, 2026-09-04; `tools/place_sectors.py`, `buildmap/plan_v8/sectors_v8.json`)

Owner's rules for this pass: it is an art pass, not a gameplay pass (areas for play are defined later); the four
Novo Expograd builds form ONE cyberpunk district; the Woods is a named area on the forest that already exists (no
relief, no regeneration); the player builds are not kept together as a district but set individually into the landscape;
every build is integrated with the existing terrain (set at ground level, edges blended, roads and trees around it kept,
no pads). Placement is by visual fit: free ground (no water or rail under it, at most a few sheds or field tracks that the
transplant replaces), 12-90 m from an existing road and never on one, flat, 16 blocks clear of anything built, 48 of
other placed builds. The cyberpunk district stands against the west ridge at the end of the south-west road; Skadowsky
in the centre fields north of the rail embankment; the mega-base on the lake's east shore; the industrial district
beside the plant; the hempcrete compound under the ridge south-west of the town; the library and the runway north of
the town by the lake; the 29 old sites scatter as farmsteads 40 m off roads, 150 m apart, the Woods included. Render:
`incoming/census/sectors/sectors_v8.png`.

**2026-09-06, east district.** The hub was expanded to the whole western half of the 1.12 city (x -3568..-2385,
z -1008..700), and that expansion overwrote the plots the Financial Plaza, Novo Industrial and Bio Gen stood on, because
the hub's own source map holds open desert at those three spots. The three builds have been transplanted again from
their original 1.12 saves and set down as an east district, 32 blocks off the city's east edge, on flat ground at y 65:
the plaza and its sewers at the north end, the industrial zone in the middle, the Bio Gen offices at the south. Plan:
`buildmap/plan_v8/transplant_plan_v8_district.json`. Three streets tie the district into the network
(`buildmap/plan_v8/roads_v8_district.json`): a through avenue from the desert city across the district to the
north-south trunk, a spine along the builds' east flank, and a mid-district link east to the trunk.

| Build | Group | Position (blocks) | Footprint | m to a road |
|---|---|---|---|---|
| Camp | camp | x -978..-770, z -1060..-845 | 209 x 216 | - |
| Novo Expograd hub (desert city) | cyber | x -3568..-2385, z -1008..700 | 1184 x 1709 | 40 |
| Financial Plaza + sewers | cyber | x -2352..-2193, z -1008..-865 | 160 x 144 | 72 |
| Novo Expograd Industrial Zone | cyber | x -2352..-2209, z -832..-673 | 144 x 160 | 82 |
| Bio Gen offices | cyber | x -2352..-2289, z -640..-529 | 64 x 112 | 160 |
| Skadowsky sector | sector | x -1088..-625, z -1488..-737 | 464 x 752 | 89 |
| Mega-base | player | x 368..751, z -2128..-1601 | 384 x 528 | 40 |
| Industrial district | player | x 336..799, z -1376..-1105 | 464 x 272 | 86 |
| Hempcrete compound | player | x -3392..-3073, z -1344..-1025 | 320 x 320 | 68 |
| Library | player | x -2480..-2385, z -3808..-3713 | 96 x 96 | 96 |
| Runway (pad) | pad | x -2064..-1553, z -3792..-3601 | 512 x 192 | 58 |

**2026-09-07, the camp row.** The camp moved off the east plateau into Skadowsky - the pocket east of the south-west
bridge - and the row above is that rectangle, matching `buildmap/plan_v8/sectors_v8.json`. It sits inside the Skadowsky
sector's own rectangle on purpose: the camp is part of the town.
The old plateau rectangle x -1792..-1409, z -2492..-2109 is dead and nothing was ever built on it.
Section 9 and `docs/gscraft-skadowsky-camp.md` carry the camp itself.

**2026-09-07, deferred builds.** These builds are placed and stay placed, but no quest points at any of them; they are
deferred to a later quest line, which can pick them up as they stand: the Novo Expograd Industrial Zone, the Financial
Plaza and its sewers, the Bio Gen offices, the Novo Expograd hub (the desert city), the mega-base (FR-06), the
industrial district ("the waterworks"), the library and the runway pad. Questing routes only to the Pripyat base map,
the Skadowsky sector and the hempcrete compound.

Farmstead centres: (-2192,224), (-1472,-256), (-2176,-576), (-2192,-32), (-1712,-1744), (-2720,-1072), (-2112,-896), (-1696,-272), (-1568,-1472), (432,-2448), (-2432,-1168), (-304,-2848), (128,-2368), (-1312,-864), (-1920,-272), (-2080,576), (-3792,-2848), (-1344,-3152), (-528,-2640), (672,-2320), (-208,-2432), (-2320,512), (144,-3456), (-1200,-3792), (-3760,-3712), (-720,-2400), (-2208,-304), (-3008,416), (-2416,240).

Named areas: town x -3750..-1800 z -3750..-1400; plant x -1150..1200 z -400..700; the Woods x -2450..-1600 z -1350..100.

## 5. Build log (v8, 2026-09-05)

- World: `scratch/worlds/v8-build` = the upgraded Pripyat world, 14,877 holes filled flat (`flatfill.py`).
- Relief: `applyheight.py` shifted 4,828,237 columns in 36,969 chunks (138 s) to the authored heights; roads, rail,
  water and buildings untouched; trees and cover moved with their ground (ground-under-canopy raster).
- Transplants: `runplan.py` with `buildmap/plan_v8/transplant_plan_v8.json` - 40 entries, 5,678 chunks, block-exact
  vertical shifts (section shift + residual column shift), every block resolving in the pack (Custom NPCs waypoint
  markers -> air). The hub, Novo, plaza + sewers, Bio Gen, Skadowsky (+35), settlement, mega-base, industrial district,
  hempcrete compound, library and 29 farmsteads are in.
- Edge grading: `grade_v8.py` blends the land around every build into y 65 over 48 blocks. First run used the wasteland
  terracotta fill (brown rings in `incoming/census/v8_cell_topdown.png`); re-run with dirt/grass and a repaint of the rings.
- Server: `server/wasteland-v8` booted clean on the local server 2026-09-05 00:27 (visual profile) for the owner's fly-through;
  spawn was still the pack's (in the town) at that boot. (2026-09-07: the world spawn is the paved junction at
  (-940, -979), ground y 65, in Skadowsky. The east plateau and its basin were built and are still there as terrain,
  but nothing was ever built on them and the camp is not there - section 9.)
- Step 6 started (owner: the sectors themselves may change to unify with the terrain): `settle.py` keeps every structure
  inside a footprint and re-grounds the open columns - imported desert sand, superflat plates and hillsides become the local
  dirt/grass at a height that meets the neighbouring foundations and the outside level, so footprint edges disappear.
  Skadowsky (its own landscape) and the camp are excluded.
  Two traps met and fixed on the way: (1) the first settle classifier counted sandstone, stone and terracotta as ground and
  flattened buildings made of them (the hub kept 10 k of 54 k structure columns) - now only soil is ground, hard blocks are
  structure or pavement, and the wasteland terracotta counts as soil only for the builds lifted from the live world; the
  footprints were restored by re-running the transplants. (2) Chunks upgraded from 1.12 by the vanilla server keep the
  status `minecraft:spawn` / `minecraft:empty`; the terrain tools skipped them (plaza and settlement "had nothing built")
  and the game would treat them as unfinished - `runplan.py` now writes every transplanted chunk as `minecraft:full`.
- Settle results (2026-09-05 01:30): hub 53,913 structure columns kept / 452,720 open re-grounded (its desert floor is now
  the local grass), mega-base 133,680 / 69,072, industrial district 63,986 / 47,282, settlement 14,777 / 52,982, hempcrete
  11,567 / 90,827, Novo 16,688 / 239, plaza 5,221 / 479, library 2,319 / 6,897, 29 farmsteads. Re-staged to
  `server/wasteland-v8` and booted 01:39 for the owner's fly-through.
- Owner's notes after the first fly-through (2026-09-05) and what was done: (1) "pave the ground" of the hub - its desert
  floor restored (hub re-transplanted) and the settle run with sand counted as pavement, so the platform, streets and
  sand floor stay and only true soil becomes grass; (2) Skadowsky's edges blended - `settle.py --edge-only`: the outer
  40 blocks of its footprint meet the outside level, the interior untouched; (3) water where it should not be - the settle
  pass now removes imported ponds standing on open columns (trees kept); (4) "connect the river to Skadowsky's river" -
  `tools/river.py` carves a 22-wide channel from the sector's river mouth (-1011, -1356) north-east to the lake at
  (-713, -1726), bed 3 under the water, banks 1:3 (`buildmap/plan_v8/rivers_v8.json`); the sector's south outlet at
  (-1045, -745) is left as a stream end for now.
- Pass 3 (2026-09-05, after the owner's second look: "the water and river system looks unnatural, grass chunks, weird
  patches", "the desert city looks like a cut and paste job - the city is what I want preserved, the surrounding terrain can
  be discarded"):
  - `tools/integrate.py` (new): a sector footprint is rebuilt column by column from a *fresh* transplant
    (`buildmap/plan_v8/transplant_plan_v8_fresh.json` -> `scratch/worlds/fresh_sectors`) and the spine world with the relief
    applied. Only the build's own columns are kept (hub: man-made blocks in the top 9, specks under 60 columns dropped,
    courtyards closed r 10, apron 3, the source map's east border fence dropped, every kept component lifted so its floor
    meets the land, dy -11..+5; Skadowsky: the map's own terrain above y 40 in components of 2000+ columns plus the
    man-made columns standing on it - the y 38 plate the map was built on and the template displays parked on it go).
    Everything else inside the footprint and every open column in a 48-block margin becomes the local landscape again; a
    band (32/40 blocks) bends the land to the build's floor with low-frequency noise; other sectors' footprints and any
    man-made column in the margin are never touched. Hub: 43 k columns kept of 532 k; Skadowsky: 226 k kept of 349 k
    (the sector had been sitting on its 27-block-deep plate, which is what the 40-block edge terraces were blending to).
  - `tools/river.py` rewritten: meandering centre line (18/220 + 7/90 sine offsets, ends pinned), width 16-26, water
    stepping 53 -> 57 in four 1-block rapids from the Skadowsky river (its surface is y 53 at the map edge) up to the lake,
    smoothstep banks 1:2.5-1:4.5 varying per side, sand/gravel beach, noise, the natural land taken from the relief plan
    (so the first carve's flat 65 corridor went back to the 69-70 relief), the old straight channel's corridor restored,
    the lake and the kept Skadowsky columns protected, the channel allowed to cut its mouth through the map's rim
    (`mouth_t`). Shore jobs grade the Skadowsky river's west bank outside the footprint (the map ends in a straight cliff
    there) down to the water over 36 blocks. `buildmap/plan_v8/rivers_v8.json`.
  - `tools/anvil.py`: `Chunk.set` now creates a missing/empty section on demand. Before this every World-based tool
    silently lost blocks placed into an empty 16-block section (a bank filled to y 66 through an empty section 4 ended as
    dirt at y 63) - the source of several "dirt patches" in pass 2.
  - Renders: `incoming/census/v8_cell_pass3_inspect.png` (full cell, hillshaded), `v8_pass3_hub.png`,
    `v8_pass3_skadowsky_river.png`, and the per-sector `integrate_<id>_preview.png` / `_mask.npz` (the kept mask, used by
    river.py as its protect layer).
  - Not done yet with the same tool: the mega-base, industrial district and settlement footprints still carry their own
    imported ground slabs (visible as squares in the full render); `integrate.py` takes a new SECTORS entry per sector.
- Pass 3b (2026-09-05, owner: "that section of the river makes no sense, and a bridge on Skadowsky also doesn't; transplants
  have blending issues exactly at their edges"). Diagnosis: the source map's west water is the town's big river cut at the
  map boundary; keeping the cut left a rectangle of water with a straight edge, a stream leaving its corner and the highway
  viaduct ending at the map edge. Ground blending is solved by the integrate pass; what remains at every footprint edge is
  *linear features* running off the source map, which need a continuation in their own vocabulary or a designed end.
  - The river is now the region's main river (`rivers_v8.json`, one job): it drains the lake (y 57, four 1-block rapids in
    the first 200 m), runs 84-110 wide along Skadowsky's west side (the map's straight-cut water is its east half, the
    kept columns untouched), then south out of the cell at z 700 (owner: "out of the cell"). Roads on the line are cut
    (`cut_roads`: the gravel highway embankment at z -520 and the road at z -205 - bridge sites for step 8). The 22-wide
    channel and the shore strips are gone. 227 k channel + 271 k bank columns.
  - `tools/bridge.py` (new): stamps the viaduct's own cross-section (two decks, earth median, lamp posts, taken at
    x -1030) from the map edge across the river to the new west bank, with the median as piers every 12 blocks and open
    water between, then 60 columns onto the bank as the highway at grade; ends at x -1234 (`bridge_v8.json`, stub in
    `bridge_v8.json.stubs.json` for step 8). A routed 9-wide connector was tried first and removed (`tools/unroad.py`):
    its target was a 42-pixel farm track and the router's 32-block cells gave a dogleg.
  - `tools/statusfix.py` (new): 7,263 chunks of the cell still carried the 1.12 upgrade's `spawn`/`carvers` status; every
    World-based tool skipped them (the river had gaps south of z 300, the relief pass had skipped them too - checked: the
    open land there was already at plan height). All chunks are `full` now.
  - `tools/edgeaudit.py` (new): every footprint edge scanned for water, elevated (deck) and road/rail features running
    off the source map -> `buildmap/plan_v8/edge_features_v8.json`: 158 features (85 road, 47 water, 26 elevated). The
    water ones are the industrial district's north edge (its own canal system cut at the edge), the hempcrete compound's
    west edge, the mega-base's west edge, the settlement's east edge; the elevated ones are pipes/decks at the mega-base,
    industrial district and settlement edges. Each is a step-7/8 item: continue it or end it.
  - `tools/connectors.py`: connector targets are now the road network proper (components of 3000+ pixels); the earlier
    plan sent both Skadowsky gates and several farmsteads to a 42-pixel track. `roads_v8.json` regenerated (16 connectors;
    the far farmsteads now show 1-1.8 km tracks - a design decision for step 8, not built).
  - Renders: `incoming/census/wide_river_inspect.png` (the whole course), `bridge_area_inspect.png`.
- Pass 4 (2026-09-05, owner: "do a complete review of the issues, then start applying the fixes"): every sector onto the
  landscape with `integrate.py` (manmade+lift / hull / plate / remove modes per group), the settlement removed on the
  owner's call, six empty old sites dropped, canal mouths rounded (`edgewater.py`), the 11 connectors under 300 m built in
  the Skadowsky style. Full review and results: `docs/gscraft-map-review-v8-pass4.md`. Render `v8_cell_pass4_inspect.png`.
- Pass 4b/4c: all 27 sector connectors, 17 stub connectors, two river viaducts, water edge ends; staged to `server/wasteland-v8`.
- Pass 5: `smoothcliffs.py` - cell-wide cliff (3+ steps) and shore smoothing of the open land, terrain only.
- Next: the owner's look (WorldPainter or the local server); then step 9+ (camp, Lost Cities modules, props).

## 7-8. Road hooks (prepared 2026-09-05, not built)

`tools/stubs.py` scans each footprint's outer 3-block ring for road materials that lead inward (a plate edge or a wall
base fails the test) and records the builds' own stubs (`buildmap/plan_v8/stubs_v8.json`: the hub 5, Skadowsky 4, the
settlement 4, the industrial district 3, Bio Gen 3, the hempcrete compound 5 tracks, the library 2 slab paths; the plate-
edged 1.12 builds and the runway have none). `tools/connectors.py` turns the stubs (or a fallback gate on the edge facing
the nearest road) into connector roads to the nearest point of the existing network, at most two per build, none when the
network is already within 40 m; `roads.py route` routed them on the built terrain: 13 connectors, 3.4 km
(`roads_v8.json`, `routes_v8.json`, render `incoming/census/connectors_v8.png`). They are built with
`roads.py build --style skadowsky` (stone / andesite / gravel carriageway, andesite-wall kerbs, dirt fill, 9 wide) or
`--style track` (gravel and coarse dirt, 5 wide) once the owner is happy with the sectors (step 6).

## 9. The camp - design (started 2026-09-05, owner: design first, build later)

**Realigned 2026-09-07.** The camp is in Skadowsky, not on the plateau. What follows replaces the plateau spec that
stood in this section (its eight rectangles, the tower pad, the Warium spawn structure and the crater lake); the
authority document is `docs/gscraft-skadowsky-camp.md`. The east plateau of section 2 and its basin were built and are
still in the world as terrain, but nothing was ever built on them, there is no crater and no crater lake there, and
they are not the camp. The plateau sketch `incoming/census/camp_v8_sketch.png` and `buildmap/plan_v8/camp_v8.json`
hold that dead spec's coordinates and go with it; `tools/camp_torches.py`, `tower.py`, `theline.py` and
`pads_camp.json` are keyed to the plateau too, and `camp_ruins.py` is retired outright (below). None of them has ever
been run against the world, so re-keying them is a text change and not a rebuild.

**Where.** The pocket east of Skadowsky's south-west bridge. The camp box is x -978..-770, z -1060..-845 (209 x 216),
which takes in the pocket, the mast and the mast's field and crosses the rail embankment, whose level crossing becomes
the east gate. It sits inside the Skadowsky sector's rectangle on purpose: the camp is part of the town, and clearing
the town is Act I. The west gate is the south-west bridge, x -1104..-981, deck z -957..-936, deck level y 89,
stone-brick masonry with iron railings and truss sides reaching y 94; water sits at y 53, so the deck stands 36 blocks
above it, and it is the only crossing on Skadowsky's west side.

**The centre.** No crater lake and no Warium spawn structure. The world spawn is the paved junction at (-940, -979),
ground y 65 - stone, andesite and gravel, already hard surface, and facing the bridge.

**The buildings already exist**, so this is not a sector to generate onto empty ground the way the plateau spec assumed.
Inside the perimeter:

| Feature | Position (blocks) | Footprint | Ground y | Note |
|---|---|---|---|---|
| north complex | x -966..-898, z -1090..-1000 | 69 x 91 | 63 | stone and iron railings; holds 24 beds already (48 bed blocks at x -956..-933, z -1033..-1006, y 63-71) |
| paved junction | x -962..-918, z -996..-962 | 45 x 35 | 65 | stone, andesite and gravel; the world spawn |
| south complex | x -978..-922, z -900..-822 | 57 x 79 | [needs measurement] | two buildings, not one hall: a brick block 15 x 39 at x -938..-924, z -869..-831, roof y 85, and a deepslate-trimmed structure west of it at x -971..-937, z -893..-822 whose polished deepslate sits on the upper floors, y 74-84 |

**The ring** (the design's table 3.6 adapted to the standing buildings; first cut, for the visual pass to adjust,
exactly as the plateau table was):

| Building | Position (blocks) | Footprint | Note |
|---|---|---|---|
| marshall | x -978..-955, z -955..-940 | 24 x 16 | gatehouse at the bridge's east end; every trip west crosses him |
| tony | x -966..-930, z -1060..-1020 | 37 x 41 | clinic in the north complex, where the 24 beds already are |
| tune | x -925..-905, z -1040..-1020 | 21 x 21 | radio shack at the north complex's east end, nearest the mast and in sight of it |
| walker | x -975..-940, z -880..-845 | 36 x 36 | the yard in the south complex's deepslate-trimmed structure, walled with standing floors |
| michael | x -938..-910, z -900..-870 | 29 x 31 | the plant on the south complex's east side, beside the yard and off the square |
| james | x -905..-897, z -975..-967 | 9 x 9 | lookout in the rail embankment's signal box; it already overlooks both approaches |
| gun_pit | x -846..-835, z -1000..-989 | 12 x 12 | the mast field's west edge, firing east over open grass |
| tower_compound | x -840..-770, z -1040..-960 | 71 x 81 | the mast's field; the finale's fail rectangle and the sculk ring |

**The tower is the sector's own mast**, at (-808, -1008), standing on a building whose roof is y 104. It is dead: no
power, no feed, no array, and its lattice is cut where it was salvaged. Its column, read from the world: yellow
concrete y 104-120, cobblestone wall 121-124, spruce fence 125-131, iron bars 132-136, an end rod at 137. There is no
tower pad to build. `tools/tower.py` moves its origin to the mast's foot and stage 1 becomes "repair the cut lattice
section so the mast can be climbed" rather than erecting a mast to 64 - same Mast section kit, same quest X2, same
gate; stages 2 to 5 (cooling, generator, transmitter, array) are unchanged in count, gating and reward. The aircraft is
rotary and lifts from the mast's field inside the perimeter, so no airfield is needed: the runway pad and
`runway_lights` are retired, and the runway itself is deferred to a later quest line.

**Suppression.** Five Magnum Torches cover the pocket at 64-block radius. They do not cover the sector, which is
deliberate: extending suppression to the whole sector is the reward for `skadowsky_held`.

**Vocabulary.** Tier-0 palettes from `gscraft-camp-spec.md` section 6 (wreck segments, oak planks, cobblestone, tarps,
sandbags and barbed wire, torches and campfires, barrels), aged with Immersive Weathering variants; the camp reads as a
survivor camp squatting in a Soviet town it has not cleared yet, not as a base - the concrete panels, stone brick and
Doomsday Decoration props of Skadowsky around it are the reference. The west gate road is the bridge itself; the east
gate is the rail embankment's level crossing.

**Still to decide before building:** nothing about the site. What is left is the visual pass - the ring rectangles
above walked and adjusted against the buildings that are already standing - and then `camp.py` for whatever those
buildings do not already provide. `camp_ruins.py` and its 24 wrecks are retired: Skadowsky is a 464 x 752 town with a
hospital, a station and a level crossing, so Act I has plenty to loot without inventing wrecks.

