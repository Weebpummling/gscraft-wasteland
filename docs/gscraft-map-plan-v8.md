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

## 2. Terrain heights (to decide next)

Proposal to react to: sea level 63 as the river and lake level; the general ground 70-80 (rolling, 2-4 block folds
over 100 m, so a road never needs a cutting deeper than 3); a plateau of 84-90 north of the river where the camp sits
(the camp basin is cut 6 into it, the crater lake at 63); a low ridge of 95-105 along the west edge as a wall; nothing
above 110 inside the border; the Woods on ground 72-82 with dense trees and a stream. The real terrain of all three
candidates is flat, so the relief is authored, not copied.
