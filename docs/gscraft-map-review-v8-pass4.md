# GSCraft v8 - complete issue review and pass 4 (2026-09-05)

Owner: "Do a complete review of the issues, then start applying the fixes." Review of the whole cell after pass 3b
(`incoming/census/v8_cell_pass3_inspect.png`, the per-sector renders, the edge audit `buildmap/plan_v8/edge_features_v8.json`,
the height probes), then the fixes in the order they were applied.

## 1. Where the map stood

Working: the relief (open land is at the plan height everywhere but 180 k columns of 16 M, all of them river corridors or
the cell's west margin), the hub and Skadowsky sitting on the landscape after pass 3, the region's river and the highway
bridge after pass 3b, all chunks `full` after the status fix.

Issue classes found, in order of visual weight:

| # | Issue | Where | Cause | Fix |
|---|---|---|---|---|
| 1 | **Imported ground slabs** - a sector footprint still shows as a square: its own terrain (hills, geodes, a lake, a lawn) ends in a straight line at the footprint edge, the settle pass only flattened the open columns to y 65 | mega-base, industrial district, settlement, hempcrete compound, library, Novo, plaza, Bio Gen, the 29 farmsteads | the transplant copies the whole rectangle; settle.py kept its ground | `integrate.py` on every sector (this pass) - keep only the build's own columns, restore the landscape, band + lift |
| 2 | **Linear features running off a footprint edge** - roads, canals, pipes and decks that continue on the source map and stop dead at our edge | 158 features: 85 road, 47 water, 26 elevated; the largest water ones are the industrial district's canals (its N edge, up to 64 wide), the hempcrete compound's ponds (W/N), the mega-base's west lake, the settlement's east ditches | the source map is bigger than the footprint | roads: step 8 connectors (plan regenerated to target the real network); water: closed by the landscape restore (a pond cut at the edge becomes a pond inside the build's mask or disappears), the survivors re-audited below; elevated: cut back or left as broken ends (wasteland) |
| 3 | **Skadowsky's off-map river and bridge** | west side | the map's main river was cut at the boundary | done in pass 3b (main river to the lake and out of the cell, viaduct carried across) |
| 4 | **Terraced contour rings** on gentle slopes | around every graded build, the camp plateau, the relief's own slopes | 1-block contour steps on gentle slopes read as rings in a hillshade; unavoidable in Minecraft terrain, made regular by machine-smooth profiles | noise on every band and bank (pass 3); the camp plateau's rings are the designed zone A and go with the camp build |
| 5 | **Unfinished chunks** - 7,263 chunks still at the 1.12 upgrade's `spawn`/`carvers` status; every tool skipped them | scattered through the cell (5 %) | the vanilla upgrader leaves them | `statusfix.py` (pass 3b) |
| 6 | **Connector plan aimed at fragments** - both Skadowsky gates and several farmsteads were routed to a 42-pixel farm track | plan only, nothing built | `connectors.py` took any road pixel as the network | targets are components of 3000+ pixels now; 16 connectors, several farmsteads at 1-1.8 km (owner decision at step 8) |
| 7 | **Silent block loss above empty sections** - fills crossing into an empty 16-block section ended as dirt at y 63 | every World-based tool before pass 3 | `Chunk.set` did not create sections | fixed in `anvil.py` (pass 3) |
| 8 | **Bed seam** under the widened river at x -1088: the map's bed (y 48) meets our bed (y 49) along the old footprint line | Skadowsky west water | two beds | under 5 blocks of water, invisible in play; left |
| 9 | Camp not built, runway pad a placeholder, Lost Cities modules and props not placed | plateau, runway, city zones | design steps 9+ | not part of this pass |

## 2. Pass 4 - what was applied

Filled in below as the run completes.
