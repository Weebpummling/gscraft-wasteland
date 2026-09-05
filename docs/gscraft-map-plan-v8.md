# GSCraft Wasteland — map v8 plan (roads and terrain first)

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
| A  Camp plateau | the open land between the town's east edge and the lake, about x -2150..-1250, z -2700..-2000 | 84-90, a basin cut down to the lake level (63) at its centre for the crater lake and the Warium island; slopes 1:6 to the town side, a bluff to the lake | the camp overlooks both the town and the water; the only high ground in the middle of the map |
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
hills - the pack has a low rise of 70-77 inside the river bend - are kept and the relief adds to them. The camp plateau
zone comes out low (mean 72, top 88) because scattered sheds inside it pin their surroundings; the camp sector's own
grade shapes that ground when it is placed, so this is accepted. Woods 65-77 (mean 68), fields 61-74. Renders:
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

| Build | Group | Position (blocks) | Footprint | m to a road |
|---|---|---|---|---|
| Camp | camp | x -1792..-1409, z -2492..-2109 | 384 x 384 | - |
| Novo Expograd hub (desert city) | cyber | x -3376..-2545, z -624..15 | 832 x 640 | 40 |
| Novo Expograd Industrial Zone | cyber | x -2880..-2737, z -816..-657 | 144 x 160 | 86 |
| Financial Plaza + sewers | cyber | x -3456..-3297, z -800..-657 | 160 x 144 | 91 |
| Bio Gen offices | cyber | x -2512..-2449, z -704..-449 | 64 x 256 | 99 |
| Skadowsky sector | sector | x -1088..-625, z -1488..-737 | 464 x 752 | 89 |
| Mega-base | player | x 368..751, z -2128..-1601 | 384 x 528 | 40 |
| Industrial district | player | x 336..799, z -1376..-1105 | 464 x 272 | 86 |
| Hempcrete compound | player | x -3392..-3073, z -1344..-1025 | 320 x 320 | 68 |
| Library | player | x -2480..-2385, z -3808..-3713 | 96 x 96 | 96 |
| Runway (pad) | pad | x -2064..-1553, z -3792..-3601 | 512 x 192 | 58 |

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
  spawn is still the pack's (in the town), the camp sector itself is not built yet (its plateau and basin are).
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
- Next: re-stage to the server, render, the owner's fly-through, then step 7 (roads hooked to the builds' own stubs).

