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

### 2.8 Pass 6 - water fixes (owner: the land tongue on the lake with a bridge instead, the north-east stripes, the arm cut
off from the lake, the river mouth, the trees over the Skadowsky river, the leftover land in it)

- **Lake land tongue** (x -1030..-790, z -2350..-2060): a chunk-stepped flat at y 65 between the lake's two lobes, carrying
  six farm tracks. The tracks were stripped (`unroad.py`), the tongue went back to the relief plan and a 190-230-wide strait
  was carved through it (`river.py`, `rivers_strait_v8.json`), its remnants forming capes; the tracks now cross on a 308 m
  track viaduct (`viaduct_lake_v8.json`, deck y 65, piers every 10) and were re-routed to its ends (`roads_v8_lake.json`).
  Two detours on the way are recorded here because they cost time: a box-shaped fill and an "organic" refill both left
  straight shorelines; the strait as a river job with the lake protected was the answer.
- **North-east arm** (y 62): the chunk strip across its north shore and two 16-block square islands became water, the straight
  north shore was given a wavy edge (`shoreline.py wobble`, 20 blocks), and the broken connection to the lake's north tip
  became a 34-44-wide stream with five one-block rapids from the arm (62) down to the lake (57) (`rivers_arm_v8.json`).
- **River mouth at the lake**: the two beach tongues went (`lakefill.py`), the junction is open water.
- **Shorelines**: `shoreline.py naturalize` blurs the water mask (sigma 8-9) and re-thresholds it over the lake and the arm,
  so chunk staircases become curves (about 6 k shore columns each way); the Pripyat cooling-pond's stone embankments are
  builds and stay stepped.
- **Trees in the river**: the river tool had counted any column with a tree as *built* (leaves and logs are not in the
  terrain set) and skipped it, which is why a forest stood in the river through the wood south of Skadowsky and why the
  first canopy clean-up found little. `river.column_built` now treats trees as landscape; the Skadowsky river and the arm
  stream were re-carved (275 k channel columns) and the canopy over water cleared (`lakefill.py clear_over_water`).
- **Leftover land in the Skadowsky river**: inside the protected map terrain, natural columns in the channel up to 12 blocks
  above the water and without a stone/road top are carved (`cut_protected_natural`); quays, embankments and the town's
  own highway bridge stay. A first version of the rule (any natural column) took that bridge as leftover land and carved it;
  Skadowsky was re-integrated from the clean transplant and the bridge re-stamped. Bridges now write protect masks
  (`bridge_<name>_mask.npz`) that `smoothcliffs.py` and the river tools honour.
- Second round on the same points after the render: the strait's rounded ends had cut circular bays into the lobes'
  shallow margins (the shoreline blur had turned those margins to land first), so the strait was re-carved with its
  endpoints in open water; two straight leftover edges south-west of the strait were given wavy shores (`shoreline.py
  wobble`); the remaining stone rocks and islets in Skadowsky's river go unless within 4 blocks of a build (the map's quays)
  or 13+ above the water (the bridge deck); the square islands' shallow beds were deepened; the arm's rectangular notch got
  a wavy west edge and the rectangular pond by the arm-to-lake stream went back to land.
- Then `smoothcliffs.py` over the new shores and the whole cell again; render `v8_cell_pass6_inspect.png`; staged.

### 2.9 Hosted server (2026-09-05, owner: "upload the current map onto the server, and restart the server with enemies
turned off; gameplay is worked on locally, scripting on the server only when finalised")

`tools/deploy_v8.py` (upload-pack, upload-world, swap, status) drives `bisectpanel.py`. Uploaded: `/wasteland-v8` (level.dat,
region, entities, data without the local map items, serverconfig, the worldgen and lcfix datapacks - not the gameplay
datapack), `/mods_20260905` (the 2026-09-05 set, Superb Warfare 0.8.8), `/config_20260905`, `/defaultconfigs_20260905`,
`server.properties.v8` (peaceful, spawn-monsters=false, level-name wasteland-v8, survival). Swap: mods/config/defaultconfigs
folders renamed, `/kubejs` moved aside as `/kubejs_off_20260905` (no scripts), properties swapped, start. Forge on the host
stays 47.4.10 (every mod's range accepts it). Deployed 2026-09-05 16:04: `Done (2.2 s)`, "Preparing level wasteland-v8",
ModernFix 22 s load, the benign error set, no `[gscraft]` lines (scripts off), one expected warning "Missing data pack
file/gscraft" (the level.dat still lists the gameplay datapack that was deliberately not uploaded); mcping answers with
MOTD "GSCraft Wasteland - test build v8 (map review, enemies off)", 0/10. Old folders kept on the host as
`*_old_20260905`, `kubejs_off_20260905`, `server.properties.v7`. Left for a later pass: a right-angled small bay on the
strait's south-west shore (x -1050..-975, z -2130..-2050).

## 3. Open

- Step 8 is done for this pass: every sector's gates are connected, the river is bridged, quays end at the water.
- Step 9+: the camp on the plateau, Lost Cities modules in the city zones, props; the runway.
- Sector list housekeeping: drop the six empty old sites and the settlement from `sectors_v8.json` when the plan is next
  regenerated (they are marked, not deleted, so the tools skip them).
