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

**Border options** (owner decision):
- **A: 5.1 x 4.6 km, everything in place** - x -3900..1200, z -3900..700. Town, lake, river, plant and rail yard exactly
  where the pack has them. Longest trip (town centre to plant) 4.3 km.
- **B: 4.2 x 4.2 km, plant moved** - x -3900..300, z -3900..300, the plant complex transplanted 900 blocks north-west
  onto the lake's south shore (its rail and road links rebuilt in step 8). Longest trip 3.2 km. Denser, closer to the
  4 km the owner asked for; costs the pack's true geography between lake and plant.

Ungenerated holes inside either border (black in the render) are filled by the terrain build.

