# GSCraft v8 - complete issue review and pass 4 (2026-09-05)

Owner: "Do a complete review of the issues, then start applying the fixes." Review of the whole cell after pass 3b
(`incoming/census/v8_cell_pass3_inspect.png`, the per-sector renders, the edge audit, the height probes), then the fixes
in the order they were applied. Result render: `incoming/census/v8_cell_pass4_inspect.png` (`_small.png` at 1/3).

## 1. Where the map stood

Working: the relief (open land at the plan height everywhere but 180 k columns of 16 M, all river corridors or the cell's
west margin), the hub and Skadowsky on the landscape after pass 3, the region's river and the highway bridge after pass 3b,
every chunk `full`.

| # | Issue | Where | Cause | Fix |
|---|---|---|---|---|
| 1 | **Imported ground slabs** - a footprint still shows as a square: the source map's own terrain (hills, geodes, a lake, a lawn) ends in a straight line at the footprint edge; the settle pass had only flattened the open columns to y 65 | mega-base, industrial district, settlement, hempcrete compound, library, Novo, plaza, Bio Gen, 29 farmsteads | the transplant copies the whole rectangle | `integrate.py` on every sector (§2.1) |
| 2 | **Linear features running off a footprint edge** - roads, canals, pipes, decks that continue on the source map and stop dead at our edge | 158 features before this pass: 85 road, 47 water, 26 elevated | the source map is bigger than the footprint | roads: step 8 connectors, the short ones built (§2.3); water: closed by the landscape restore or given a rounded end (§2.2); elevated: broken ends, wasteland-plausible, left |
| 3 | **Skadowsky's off-map river and bridge** | west side | the map's main river cut at the boundary | pass 3b |
| 4 | **Terraced contour rings and radial facets** on graded slopes | around every graded build | 1-block contours on gentle slopes; the band's edge height taken from the *nearest* build column gave Voronoi facets (radial ridges, first pass-4 run) | noise on every band; the edge height is now a smooth field of the build's edge heights that is exact at the edge and smooth further out |
| 5 | **Unfinished chunks** - 7,263 chunks at the 1.12 upgrade's `spawn`/`carvers` status, skipped by every tool | 5 % of the cell | the vanilla upgrader | `statusfix.py` (pass 3b) |
| 6 | **Connector plan aimed at fragments** - Skadowsky's gates and several farmsteads routed to a 42-pixel track | plan only | any road pixel counted as the network | targets are 3000+-pixel components (pass 3b) |
| 7 | **Silent block loss above empty sections** | every tool before pass 3 | `Chunk.set` did not create sections | fixed in `anvil.py` (pass 3) |
| 8 | **Empty "farmsteads"** - six of the 29 old sites hold nothing man-made (0-8 columns) | old03, old07, old17, old18, old21, old28 | the live-world census marked terrain scars as sites | footprints restored to landscape; keep them off the sector list |
| 9 | **The settlement** - two rows of identical modules on a slab | x -1280..-1009, z -2016..-1729 | owner: "this sector can be removed, its a pointless area" | removed: group `removed`, footprint + margin restored, its connectors dropped |
| 10 | Bed seam under the widened river at x -1088 (map bed y 48 vs ours y 49) | Skadowsky west water | two beds | under 5 blocks of water; left |
| 11 | Straight pavement edges of the city blocks (mega-base's Lost Cities ground, the plaza, Novo) on grass | cyber district, mega-base south edge | a paved city block cut by the footprint | left: a paved block ending on grass reads as a kerb; step 8 roads meet them |
| 12 | Camp not built, runway pad a placeholder, Lost Cities modules and props not placed | plateau, runway, city zones | design steps 9+ | not this pass |

## 2. Pass 4 - what was applied

### 2.1 Every sector onto the landscape (`tools/integrate.py`, `tools/integrate_all.sh`)

Clean transplants of all 41 plan entries into `scratch/worlds/fresh_sectors` (`runplan.py`, `transplant_plan_v8_fresh.json`),
then one integrate run per sector. Three modes, chosen per sector group (`sector_config`):

- **manmade + lift** (hub, Novo, plaza, Bio Gen, library, the farmsteads): only the build's man-made columns stay (specks
  dropped, courtyards closed, apron 3), each kept component is shifted vertically so its floor meets the land, the rest is
  landscape. The plaza keeps the source's blocks 6+ under the surface (`keep_underground`) so the sewers survive under open
  ground.
- **hull** (mega-base, industrial district, hempcrete compound): player bases built into real terrain - hills, a lake,
  tunnels. The build *and the ground inside its hull* (closing r 24, holes filled, apron 4) stay as one landform, blended to
  the landscape over 80 blocks; a lake at the hull edge meets the land at its surface. Only the imported terrain outside the
  hull goes (the mega-base's geode hills, the lawn squares).
- **plate** (Skadowsky) and **remove** (the settlement) as before / as decided.

Counts: hub 43 k of 532 k columns kept; Skadowsky 226 k of 349 k; mega-base 129 k of 203 k; industrial district, hempcrete,
library, Novo, plaza, Bio Gen and 23 farmsteads kept their builds; 6 farmsteads and the settlement became landscape. 39
sectors, 12 k chunks rewritten; Skadowsky's margin restore erases the river's west half, so the river and the bridge are
re-laid after it in the batch. Hempcrete counts as a build material everywhere (Lost Cities city ground and the compound's
walls are kept as pavement/walls), Immersive Weathering soils as ground.

### 2.2 Water at the edges (`tools/edgewater.py`)

After the restore the water features fell from 47 to 21, 17 of them under 8 blocks wide (ditches, closed by the band). The
four canal mouths at the industrial district's north edge (8-15 wide, y 57) got rounded ends outside the footprint: short
river.py jobs of the canal's width running 9-12 blocks out, banks graded, the district's columns protected
(`buildmap/plan_v8/rivers_edges_v8.json`).

### 2.3 Connectors under 300 m (`roads_v8_short.json`, `routes_v8_short.json`)

Built in the Skadowsky vocabulary (`roads.py build --style skadowsky`): hub S (105 m), Novo E (100), Bio Gen S (96),
hempcrete E (117, track), library S (44, track), runway W (153, track), farmsteads 01 N, 10 N, 13 E, 25 W, 26 S (tracks);
8,449 road columns. Not built - owner decisions for step 8 (`roads_v8.json`, 29 entries): the long ones - Skadowsky's
highway west of the new bridge (736 m to the network), Skadowsky E (732), hub N (602), plaza N (610), mega-base S (952),
industrial N/E (771/474), farmsteads 04, 07, 12, 16, 19, 20, 23, 24, 27, 28, 29 at 570-1,770 m. A farmstead 1.5 km from
any road is a design question (a track that long, or no road), not a build step.

### 2.4 Edge audit after the pass (`buildmap/plan_v8/edge_features_v8.json`)

124 features: 80 road (step 8 material - every sector's own road/pavement reaching its edge), 21 water (all under 8 wide
now), 23 elevated (pipes and decks at the mega-base, industrial district, Novo, plaza, hub, some farmsteads - broken ends,
left as wasteland).

## 3. Open

- Step 8: the long connectors (owner decisions above), bridges at the two cut roads on the river (z -520 gravel highway,
  z -205 road), the 80 road stubs.
- Step 9+: the camp on the plateau, Lost Cities modules in the city zones, props; the runway.
- Sector list housekeeping: drop the six empty old sites and the settlement from `sectors_v8.json` when the plan is next
  regenerated (they are marked, not deleted, so the tools skip them).
