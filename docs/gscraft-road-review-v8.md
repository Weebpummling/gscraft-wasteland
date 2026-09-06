# GSCraft v8 - road network review and proposal (2026-09-06)

Owner: "do a comprehensive review of the road network, and propose how to improve it". Nothing in the world was changed
by this review; the tools that produced every number are in `tools/roadreview/`, the renders in
`G:/GSCraft/incoming/census/v8_roadnet.png` (coloured by network component) and `v8_road_proposal.png` (breaks marked).

Measured on the deployed world `G:/GSCraft/server/wasteland-v8` and the pass-6 height/surface arrays
(`v8_cell_pass6_inspect.npz`), cell x -3900..1200, z -3900..700.

## 1. What is on the ground

| | |
|---|---|
| Road inherited from the source maps (Pripyat grid, eastern industrial city, the radial highways) | 1.26 M surface columns |
| Connectors, viaducts and bridges laid for v8 | 45 roads, 16.4 km, 91 k columns |
| Distinct network components of 3,000 columns or more | 21 |
| Largest component | 933 k columns, 69% of the road surface |

The 45 standing connectors are `routes_v8_short` (11) + `routes_v8_long` (16, less the six stripped by `unroad.py` in
`fix_water.sh`) + `routes_v8_stubs` (17) + `routes_v8_lake` (7). `routes_v8.json` was the first connectors.py run and was
superseded by short+long; it is not in the world.

## 2. Findings

### 2.1 The network is severed at 19 points, and most of the cuts are metres wide

A minimum spanning tree over the 21 components says **792 m of road would make the whole cell one network**: four links
of 73-177 m, nine patches of 20-44 m, six hairline breaks under 20 m. The breaks were verified block by block in the
world, not just in the raster.

The worst consequence is the **east-west trunk at z = -205**, the only continuous road between the western half of the
map (Pripyat, desert city, hempcrete, library, runway, spawn) and the eastern half (Skadowsky, mega-base, industrial
district). It is paved at y 65 on both sides of each cut and interrupted by plain grass at:

- x -1858..-1844 (15 m), between the desert-city network and the middle segment;
- x -1408..-1394 (15 m), between the middle segment and the river viaduct's approach.

With those two patches plus the 177 m link at the desert city's north-east corner, (-2484,-444) to (-2592,-584), the two
halves of the map become one network. Today a road-only route from Skadowsky reaches no other named destination.

The four links that need real road:

| length | from | to | what it joins |
|---|---|---|---|
| 177 m | (-2484, -444) | (-2592, -584) | desert city / Bio Gen to the Pripyat network |
| 112 m | (-1144, -2568) | (-1256, -2564) | the lake's west shore track to the camp side |
| 88 m | (-564, -2332) | (-564, -2420) | farmstead 20's track to farmstead 16's |
| 73 m | (-1372, -2856) | (-1360, -2928) | the north-west lake shore to the runway approach |

### 2.2 Later terrain passes wiped 4% of the roads that were laid

Walking every connector's centre line in the world, 85 of 2,052 samples are no longer a road surface. The damage is
concentrated where a road meets water, which is where `smoothcliffs.py` shore grading and the strait and river carving
ran after `roads.py build`:

| connector | length | worst continuous break |
|---|---|---|
| skad_E | 1,224 m | 104 m at the town end |
| skad_W | 872 m | 56 m at the south end, then water |
| lake_bridge_S | 432 m | 56 m, starts in water |
| old29_S, old27_W, old23_W, old16_S, old12_S, hub_N | 408-1,704 m | 32 m each |
| plaza_N, old24_S, old20_W | 216-832 m | 24 m each |

`smoothcliffs.py` protects road columns and six blocks of shoulder, but it reads them from the surface-name array, so a
road already buried, or a deck of a material outside its keyword list, is unprotected; `river.py` and `shoreline.py`
have no road mask at all.

### 2.3 Half of the new road is duplicated corridor

988 of 2,052 centre-line samples run within 48 m of another connector: **48% of the 16.4 km**. The cause is
`connectors.py` and `edgeroads.py`, which route each gate independently to the nearest point of the network and never
look at each other.

- **North-east farm belt.** Six tracks (old12, old16, old20, old23, old24, old27) run 4,128 m, each its own way to the
  same lake bridge. A single spine touching every farm and the bridge once is 1,884 m: **2,244 m, 54%, is duplication.**
- **Eastern trio.** mega_S, indu_N, indu_E and old29_S total 4,016 m and all converge on the same node near (564,-644).
  indu_N is 100% within 48 m of another connector, mega_S is 86%, old04_S and old16_S are 100%.

### 2.4 The long connectors are ruler lines

Three connectors over 400 m bend less than 4% of their chord: old23_W (1,088 m, 2.3%), old20_W (832 m, 3.5%),
plaza_E (568 m, 2.2%). old29_S runs 1,704 m at a detour ratio of 1.02. The router's cost is
`1 + 40*water + 80*built + 3*|slope|`, so on the flat plains east of the lake nothing competes with the straight line and
the result reads as drawn with a ruler, exactly the complaint made about the transplant edges.

### 2.5 There is no hierarchy and no redundancy

Every road is either 9 wide ("skadowsky") or 5 wide ("track"), chosen by the sector's group, not by the road's job. A
1,704 m cross-country link and a 48 m farm driveway are built identically. The 45 connectors form a tree: there is no
alternative route anywhere, so any one of the breaks in 2.1 isolates a region.

### 2.6 Smaller items

- **Six connectors do not meet pavement at one or both ends** (`tools/roadreview/gates.py`): indu_E's inner end at
  (803,-1116) has no road within 60 m, skad_W's south end at (-1235,-207) likewise, skad_E has 3 m and 23 m of grass,
  indu_N 3 m, lake_bridge_S 1 m, old04_S 1 m.
- **Gradients are fine.** Only skad_W has more than one step over 3 blocks per 8 m (three, worst 8); indu_N, indu_E and
  lake_bridge_S have one each. All are bridge ramps.
- **The camp has no connector** (`connectors.py` skips id `camp`), but the Pripyat network already touches its footprint,
  so it is reachable; it just has no designed approach.
- **World spawn (-2555,-2539) is 13 m from a road** on the main western network. Skadowsky's centre is 97 m from one and
  the mega-base's is 196 m.

## 3. Proposal

In the order I would do it: value per block of work, cheapest first.

### Step 1 - close the 19 breaks (792 m)

A new `tools/roadpatch.py` taking the link list in `tools/roadreview/mstlinks.json`: for each pair of end points, lay the
carriageway of the road it is repairing, matching the material mix and width found at both ends rather than imposing the
skadowsky vocabulary, then regrade the two shoulders. The six hairline breaks and nine patches are a straight stamp; the
four real links get a routed path. This alone turns 21 networks into one and makes every destination reachable by road.

### Step 2 - protect roads from the terrain tools

Give `river.py`, `shoreline.py`, `lakefill.py` and `smoothcliffs.py` a shared road mask, written by `roads.py build` the
way `bridge.py` already writes `bridge_<name>_mask.npz`. Then re-lay the 12 damaged connector sections from 2.2. Without
this any future terrain pass re-opens the same breaks.

### Step 3 - replace the spokes with spines

Two rewrites, both removing more road than they add:

- **North-east farm belt**: strip the six tracks (`unroad.py`), lay the 1,884 m spine old12-old27-old20-old23 and
  old12-old16-old24-bridge, and give each farm a driveway of 20-60 m. Net -2.2 km.
- **Eastern trio**: one trunk from the industrial district north to the mega-base with old29 hung off it, instead of four
  independent runs to (564,-644).

This wants a change in `connectors.py`: plan all gates together, and let a new connector target an existing *planned*
connector, not only the census network. That is the root cause of 2.3 and it will keep producing fans otherwise.

### Step 4 - hierarchy and shape

- Three classes instead of two: **trunk** 9 wide with kerbs for the routes between named places, **road** 7 wide for
  sector approaches, **track** 5 wide gravel for farms. Set the class from the road's length and what it joins, not from
  the owner's group.
- Add a meander term to the router: a small lateral noise plus a preference for following the 2-block contour, so a
  1 km link on flat ground wanders 30-60 m rather than running dead straight. The same value-noise function the river
  and shoreline tools use is already there.
- Flare the junctions. Every connector currently butts into the network at a single column. A 12-block taper with the
  kerb carried round would make them read as junctions.

### Step 5 - one loop

With step 1 done the map is a tree hanging off the z = -205 trunk. A second east-west crossing in the north, from the
camp across the lake's west shore to the farm belt, would give the cell a ring and remove the single point of failure.
This is the only step that needs new bridge work, so it is last.

## 4. Numbers to check the work against

| | now | after steps 1-3 |
|---|---|---|
| network components >= 3,000 columns | 21 | 1 |
| connector length | 16.4 km | about 14 km |
| duplicated corridor (within 48 m of another connector) | 48% | under 20% |
| connector centre line no longer a road surface | 4.1% | 0% |
| destinations with a road-only route to Skadowsky | 0 of 15 | 15 of 15 |


---

# Part two - the work (2026-09-06)

Owner: "just go ahead and finish the rest", meaning steps 1 to 5 of section 3. Built in
`G:/GSCraft/scratch/worlds/v8-build`. New and changed tools: `worldborder.py`, `roadpatch.py`, `roadrelay.py`,
`roadmask.py`, and `roads.py`, `river.py`, `shoreline.py`, `lakefill.py`, `smoothcliffs.py`.

## 0. The world border (found on the way, not in the review)

Owner: "there is a forcefield near -3100, 583, and along the y axis". It is not a block wall: `level.dat` still carried
the Pripyat map's world border, centre (1900.5, 1250.5) size 10000, whose west edge is x -3099.5 and whose north edge is
z -3749.5. The Financial Plaza and farmsteads 14 and 26 were wholly outside it, and the desert-city hub, the hempcrete
compound, the library, the runway and farmstead 19 were cut by it.

`tools/worldborder.py` sets it to centre (-1350.5, -1600.5) size 5200: x -3950.5 .. 1249.5, z -4200.5 .. 999.5. That
contains the cell (x -3900..1200, z -3900..700) with a 50-block margin, and no build is outside it. The old level.dat is
kept as `level.dat.border.bak`.

## 1. The 19 breaks (`tools/roadpatch.py`, `buildmap/plan_v8/road_links_v8.json`)

Each link is snapped to the nearest real road column at both ends; the carriageway mix comes from the full blocks found
within 24 blocks of those ends (kerbs, slabs, stairs and the wasteland's terracotta are excluded from the mix but a
kerb count decides whether the patch gets andesite-wall kerbs), and the width is measured across the road, capped at 11
so a measurement across a plaza cannot widen a patch. A gap up to 80 m whose straight line is dry is stamped; anything
longer, or anything whose straight line crosses water, is routed instead so no patch becomes a causeway.

19 patches, 9,806 columns, 168 chunks. The two that matter most are the 15 m and 25 m grass cuts in the east-west trunk
at z -204, rebuilt in the trunk's own cobble / stone / mossy-cobble / light-grey-concrete mix.

## 2. Road masks and the re-lay (`tools/roadmask.py`, `tools/roadrelay.py`)

`roads.py build` now writes `road_<name>_mask.npz` for every road, the way `bridge.py` writes bridge masks;
`roadmask.py --from-routes` back-filled the 45 roads built before that. `river.py`, `shoreline.py`, `lakefill.py` and
`smoothcliffs.py` all take `--protect-roads [dilate]` and skip masked columns. In `river.py` the guard yields to a
`cut_roads` job, which is the one case where a road is meant to be cut (a bridge site).

`roadrelay.py` then walked every standing route, found the spans whose surface is no longer a road, split each span at
the water, and re-laid the dry parts in the material of the road surviving on either side. 25 spans, 11,426 columns.
Two spans were left alone because water runs beside them: the last 12 m of the Skadowsky west connector at the road
viaduct's abutment and 22 m of the lake bridge's north approach. Those are banks, not breaks.

## 3. Spines instead of spokes

- **North-east farm belt.** The six tracks were stripped (`unroad.py`; note that after the first one the rest returned
  almost nothing, which is the 100% duplication measured in part one). One track now runs from the lake viaduct's south
  end through all six farm gates: viaduct - old24 - old16 - old12 - old27 - old20 - old23, 1,600 m routed with meander
  on, 9,088 columns. It replaces 4,128 m.
- **Eastern trunk.** mega_S, indu_N, indu_E and old29_S were stripped (4,016 m) and replaced by one 9-wide trunk from
  (724,-648) north through the industrial district's east gate, the mega-base's east gate and farmstead 29, 1,728 m,
  17,052 columns.

Net: 8,144 m of spoke removed, 3,328 m of spine laid.

## 4. Classes, meander and junctions (`tools/roads.py`)

- Three classes: `trunk` (9 wide, stone/andesite/gravel, andesite-wall kerbs; `skadowsky` is kept as its old name),
  `road` (7 wide, andesite/gravel/cobble, cobble kerbs) and `track` (5 wide, gravel and coarse dirt). A route may carry
  its own `style`, which beats `--style`.
- `--meander A` adds a smooth value-noise field of amplitude A to the cell cost. At 0.4 it is far below the water (40)
  and building (80) costs, so it never re-routes a road, only bends it. The farm belt's legs now bend 9 to 37% of their
  chord where the old tracks bent 2 to 3%.
- Every route's carriageway opens by 4 blocks over the last 14 blocks at each end, so a connector meets the network as
  a flared junction instead of butting into it at one column.

## 5. The ring

The map was a tree hanging off the z -204 trunk. The eastern channel between farmstead 23 and farmstead 29 is at its
narrowest at z -2450: 17 m of water at y 57 with both banks at y 65. A 48 m track viaduct crosses it
(`viaduct_ring_v8.json`, deck y 65, piers every 10) and two track halves join it to the farm belt's east end and to
farmstead 29 on the east trunk (`roads_v8_ring.json`, 320 m and 248 m). The cell now has a loop: west network - lake
bridge - farm belt - ring - east trunk - z -204 trunk - west network.


## 6. Result, measured on `v8_cell_pass8_inspect.npz`

| | before | after |
|---|---|---|
| road components of 3,000 columns or more | 21 | **1** |
| builds on the network (34 of them) | not measurable, the network was in pieces | **34 of 34** |
| connector length | 16,416 m (45 roads) | 12,168 m (39 roads) |
| duplicated corridor (within 48 m of another connector) | 48% | **30%** |
| connector centre line no longer a road surface | 4.1% | **1.1%** |
| builds outside the world border | 3 wholly, 5 partly | **none** |

The 1.1% that is still not a road surface is where a route ends at a bank or a bridge abutment, which is where a road
should end.

## 7. Maps

`docs/maps/` carries the current set, all rendered from the pass-8 arrays:

- `gscraft-wasteland-v8.png` (2550 x 2300, 2 blocks per pixel) and `-small.png`: the labelled world map, from
  `tools/worldmap.py`. Surface colouring, hillshade, coordinate grid, the road network, and every named place.
- `gscraft-roads-v8-before.png`: the network before the work, every break marked.
- `gscraft-roads-v8-after.png`: the network after it, with the patches, the two spines and the ring picked out.

Re-render after any map change with:

    python tools/render_inspect.py <world> v8_cell_passN -3900 -3900 1200 700 1
    python tools/worldmap.py G:/GSCraft/incoming/census/v8_cell_passN_inspect.npz docs/maps/gscraft-wasteland-v8.png --scale 2

## 8. Deployed

`scratch/worlds/v8-build` staged to `server/wasteland-v8` (30 region files and level.dat), then uploaded to the hosted
server with the server stopped, and started again: "Preparing level wasteland-v8", Done in 1.6 s, the known benign error
set (pointblank loot tables, the chipped recipe, In Control's spawn.json keywords), `worldborder get` reports 5200
blocks, and the ping answers with 0/10 players on the enemies-off MOTD.

---

# Part three - the underground and the 1.12 re-skin (2026-09-06)

Owner: "none of the underground sections of any of the map builds and player builds from previous maps had their
underground section copied over, check to see if we can move it over still", then "what mod packs can we add to save the
desert city blocks so it resembles the 1.12 version", then "go ahead and do both".

## 1. What had gone, and what had not

`transplant.py` copies whole chunks, so nothing was clipped on the way in. `integrate.py` is what removed it: it rebuilt
every column it did not classify as build, top to bottom, and only the Financial Plaza carried `keep_underground=True`.
Measured against the clean transplants, built blocks more than four below each column's own surface:

| | before | after |
|---|---|---|
| Financial Plaza and its sewers | 99.0% | 99.7% |
| Skadowsky | 93.8% | 99.6% |
| mega-base | 93.2% | 99.5% |
| industrial district | 89.3% | 99.0% |
| desert-city hub | 77.2% | 98.4% |
| hempcrete compound | 34.2% | 99.4% |
| the farmsteads | 2% to 99% | 88% to 100% |
| **all sectors** | **88.5%** | **98.7%** |

The sewers were never lost. The hempcrete compound was the worst case of the large builds and had lost about 87,000
blocks of its facility.

## 2. The restore (`tools/underground.py`)

`scratch/worlds/fresh_sectors` still holds the clean transplants at their final coordinates, so the plaza's own rule was
applied retroactively: below the shallower of the two ground levels minus six, the source column comes back. Block
entities below the cut come with it, so a restored chest is still a chest with its contents. Water carved after the
transplant and a road's embankment push the cut further down instead of skipping the column, which is why the remaining
1.3% is exactly where it should be. 53.6 M blocks restored across 31 sectors, 35 region files.

## 3. The 1.12 re-skin (`tools/reskin112.py`)

Of the 665,417 modded blocks in the desert city, only 18,244 (2.7%) fell through to the grey concrete placeholder. The
rest were mapped, but to flat vanilla lookalikes because the upgrade predated a 1.20.1 Chisel in the pack: every Chisel
factory panel became one `factory_blocks:factory`, every Fureniku road block became black concrete, every antiblock
became vanilla concrete.

All six original 1.12.2 saves are still in `incoming/Maps` at DataVersion 1343, so no re-transplant was needed. For each
position the tool reads the original 1.12 block, works out what the old table made of it, and replaces it only where the
destination still holds exactly that. Anything integrate, the roads or the rivers changed is left alone.

Targets are the mods already installed, so nothing was added to the pack: Chisel 2.0.0 (which names blocks
`<pattern>/<base>`, giving `chisel:road/black_concrete`, `chisel:plates/iron_block`, `chisel:vents/iron_block` and so
on), Antiblocks Rechiseled for the nine flat "bright" colours, and Immersive Engineering. All 43 target blocks were
verified present in the installed jars before anything was written.

| site | blocks re-skinned |
|---|---|
| desert-city hub | 132,719 |
| Financial Plaza | 130,127 |
| sewers | 12,841 |
| Bio Gen and Novo | ~700 |

Two mods have no 1.20.1 answer and their blocks were re-pointed rather than left flat: **Fureniku's Roads** (103,001
blocks in the city, the mod has no 1.20.1 build) now uses Chisel's `road` pattern, and **HBM's Nuclear Tech** (54,306
blocks, 1.12 only, no port) uses Chisel's iron plating and vents. Simply Light (25,089) and Scape and Run: Parasites
(14,330) are CurseForge-only and were left on their vanilla stand-ins; adding them is still open if the look matters.
