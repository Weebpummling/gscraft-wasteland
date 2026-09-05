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

### 2.3 Connectors - all of them (`roads_v8_short.json` + `roads_v8_long.json`, routes `routes_v8_*.json`)

Owner: "Those aren't decisions?" - they are not; roads are the spine, every sector's gate is connected. Built in the
Skadowsky vocabulary (`roads.py build --style skadowsky`; farm tracks 5 wide, sector roads 9 wide): the 11 short ones
(hub S, Novo E, Bio Gen S, hempcrete E, library S, runway W, farmsteads 01/10/13/25/26) and the 16 long ones - hub N 598 m,
plaza N 629, Skadowsky E 1,214 (routed round the lake), Skadowsky W 865 (from the extended viaduct's west end, retargeted to
the network *west* of the river so it does not cross it again), mega-base S 1,040, industrial E 477 / N 769, farmsteads 04,
12, 16, 19, 20, 23, 24, 27, 29 at 630-1,700 m. 118 k road columns. The routes cross at most 8 m of water (a stream) and
avoid every building. The connectors of the removed sites (settlement, old07, old28) were dropped.

**Two viaducts** where the river cut the Pripyat roads (`tools/bridge.py` viaduct mode, `buildmap/plan_v8/viaducts_v8.json`):
the gravel highway (embankment y 76) gets a 341 m viaduct between its intact ends (x -1302 to -962, deck y 76, 7 wide) and the
cobble road a 233 m one (x -1293 to -1060, deck y 65, 9 wide): gray-concrete deck, andesite-wall kerbs, 3-wide concrete piers
every 10 blocks down to the bank or bed, nothing under the deck touched.

### 2.4 Finishing the edges (owner: "Go ahead and finish it up")

- **Stub connectors** (`tools/edgeroads.py`, `roads_v8_stubs.json`): every remaining road stub at a footprint edge (3-30
  wide) was matched to the network - the census roads plus the connectors already built. 27 gates already touch a road, 5 end
  at water (Skadowsky's quays on the river: a road ending at a quay is its designed end), the rest became connectors: one gate
  per 80 m of edge and at most three per sector, so a small build does not sprout a fan of tracks (a first run gave the
  library six; those were stripped again with `unroad.py`). 17 built, 9.7 k road columns.
- **Small water edges** (`edgewater.py --min-width 3`): nine ditches and canal mouths of 4-8 blocks at the industrial district
  and mega-base edges got rounded ends. One lesson: the audit listed a *cave pool* at y 8 under the library's west edge as a
  water feature and the first run carved a 26 k-column crater down to it; `regrade.py` (new) put the land back on the plan
  and edgewater now ignores water below y 40.
- **Elevated ends** (16 left): pipes and decks that stop at a footprint edge - broken infrastructure, wasteland-plausible, left.

### 2.5 Edge audit after the pass (`buildmap/plan_v8/edge_features_v8.json`)

126 features: 91 road (the sectors' own pavements and roads reaching their edges - all now within reach of a connector or
ending at a quay), 19 water (all under 8 wide, rounded or closed), 16 elevated (broken ends).

### 2.6 Staged

`scratch/worlds/v8-build` copied to `server/wasteland-v8` (region, entities, level.dat) for the local server; the hosted
server is untouched (HANDOFF §6).

### 2.7 Pass 5 - hard edges of the terrain (owner: "from an overall point of view, smooth out the hard edges on the map -
terrain related only, not buildings")

`tools/smoothcliffs.py` over the whole cell from the pass-4 height arrays: (1) every step of 3+ blocks between two open-land
columns (23,745 cliff columns - the west border rim's slope, the mega-base hull's edges, the hempcrete compound's terrain,
odd steps at the cell's north and south edges) gets the ground within 12 blocks replaced by a smoothed height field, so a
step becomes a slope; (2) every open-land column within 14 blocks of a lake or river and more than 1 block above its
surface (140,332 columns - the big lake's steep Pripyat banks above all) is graded to water + 1 with a sand/gravel beach on
the first two blocks. 198 k columns changed (mean 3.2 blocks), 2,848 chunks. Untouched: built columns, roads and 6 blocks
of shoulder, water, Skadowsky's own terrain. Render `v8_cell_pass5_inspect.png`; staged to `server/wasteland-v8`.
What remains as hard edges is not terrain: the paved edges of the city blocks (mega-base, plaza, Novo) and Skadowsky's
quays on the river.

## 3. Open

- Step 8 is done for this pass: every sector's gates are connected, the river is bridged, quays end at the water.
- Step 9+: the camp on the plateau, Lost Cities modules in the city zones, props; the runway.
- Sector list housekeeping: drop the six empty old sites and the settlement from `sectors_v8.json` when the plan is next
  regenerated (they are marked, not deleted, so the tools skip them).
