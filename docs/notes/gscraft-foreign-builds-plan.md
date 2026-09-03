
# Implementing the foreign builds (plan, 2026-09-03)

Owner's call: the desert hub in `world/` IS the cyberpunk city; the three ships in the sky over it
are out. Everything else from the five 1.12.2 saves comes across. This is the plan for getting
them into the wasteland world, in the order the work has to happen.

## 1. What comes across, and what does not

Measured from `buildmap/foreign/rects.json` (the hub was profiled by height:
`incoming\census\hub_columns.json`). The city sits at y 7–103; the ships hang at y 104–255 and
nothing of the ground city rises above 103, so a **y-cut at 104** separates them cleanly.

| Build | Source save | Source blocks (x0 z0 x1 z1) | Y | Size | Placed | Role in the new world |
|---|---|---|---|---|---|---|
| **Novo Expograd — the city** (desert hub) | world | −1456 1536 −625 2175 | ≤103 | 832×640 | 1.07 M | The cyberpunk city. The main location cluster of the map. |
| — north compound | world | −816 1536 −689 1615 | ≤103 | 128×80 | 18 k | Part of the city rect; comes with it. |
| **Kinyu Hiroba (Financial Plaza)** | Financial Plaza Quarantine | −432 −1168 −273 −1025 | all | 160×144 | 236 k | City district: offices → electronics loot. |
| **Novo Expograd Industrial Zone** | Novo Expograd Industrial Zone | 624 144 767 303 | all | 144×160 | 34 k | City district: refinery → fuel chain loot. |
| **Novo Expograd Sewers** | SewerPVP | −944 −320 −849 −225 | all | 96×96 | 59 k | Under the city: the horror route in. |
| East compound | world | −432 1472 −161 1759 | all | 272×288 | 228 k | Suburb / outlying location. Nearly vanilla. |
| Bio Gen offices | Bio Gen Offices Restricted Areas | 464 −1200 527 −945 | all | 64×256 | 7 k | Small filler POI. Last, if at all. |

**Excluded:** the starship + hangar ship (x −1056..−737, z 1568..2079, y ≥104) and the battleship
(x −672..−641, z 1712..1967, y ≥104). Excluded by the y-cut inside those two boxes; anything in
those boxes below 104 (shadows, mooring towers) is kept and reviewed on the flight.

The names line up: three of the saves are districts of the same city (Novo Expograd Industrial
Zone, Novo Expograd Sewers, and the hub itself), and Kinyu Hiroba is its financial quarter. So
they are reassembled as **one metropolis**, not scattered POIs: the hub in the middle, the plaza
and the industrial zone as districts 100–200 m off its edges, the sewers under the hub, the east
compound as the suburb. Total footprint about 1.3 × 1.0 km.

## 2. Where it goes

Siting rules (from the map plan and the scale note): inside the 5 km box, at least 1 km from the
crater so the finale stays a different fight, at least 500 m from the nearest pad, on ground that
is dry or can be made dry with one `pad` pass, reachable by the road spine.

Two candidate zones, to be settled on the pre-generated render, not before:

- **North (preferred):** x 500…1900, z −1150…−150. About 1.2 km north-east of the crater, ends
  next to the radio tower pad (x 2023…2150, z −184…−57). The city and the endgame tower become one
  skyline, and the spine from the crater runs crater → city → tower → district.
- **West:** x −600…800, z 1500…2600. 1.6 km south-west of the crater, near the substation pad.
  Farther from the district; keeps the north empty for later seasons.

Both are outside the generated area today. **Pre-generation of the whole 5 km box is the first
step** of this plan, because the choice needs the terrain and the terrain does not exist yet.

## 3. The pipeline to build (tooling)

What exists: `anvil112.py` reads 1.12 saves and names blocks; `transplant.py` shifts, remaps and
writes 1.20.1 chunks and carries the entity/POI logic; `anvil.py` has the 1.20 section codec
(`encode`, `Chunk.set`); `fixspawners.py`, `terrain.py`, `strongpoints.py`, `topdown.py` do the
after-care. What is missing is the middle: turning a 1.12 volume into 1.20.1 chunks.

1. **`extract112.py` (new)** — `anvil112` → a build volume: for a rect and y range, per chunk,
   arrays of `(name, meta)` plus the tile entities, saved as `.npz` + JSON. Applies the y-cut and
   the exclusion boxes. Output is what every later step reads, so the 1.12 saves are opened once.
2. **Vanilla layer — let the game flatten it.** Copy the save, run the **vanilla 1.20.1 server**
   on it with `--forceUpgrade --eraseCache nogui`. Its DataFixer converts every vanilla
   `(id, meta)` to the exact 1.20.1 blockstate — stairs, doors, beds, banners, all of it — and
   drops modded ids to air. That gives a 1.20.1 world with holes where the modded blocks were.
   *(Needs `eula=true` in that folder; the same acceptance as the local test server.)* If the
   upgrade refuses a Forge 1.12 world, fallback is a hand table for the 430 vanilla `(name, meta)`
   pairs in the rects — rule-driven (wool/planks/glass/concrete colour metas, slab/stair bits),
   still finite.
3. **Modded layer — our table.** `remap112.json` (from `tools/remap112_todo.json`, 471 names,
   61 cover 95%) maps each modded `(name, meta)` to a 1.20.1 blockstate. Policy per family in §4.
   **Unmapped → `minecraft:light_gray_concrete`**, never air, so a hole in the table is visible
   on the render and in the flight.
4. **`merge112.py` (new)** — reads the upgraded vanilla chunks and the extracted volume, and for
   every position that was modded in 1.12 writes the table's block (with `anvil.py`'s `Chunk.set`),
   drops modded tile entities, keeps vanilla ones. Result: a 1.20.1 region set of the build, at
   its source coordinates, with the ships absent.
5. **`transplant.py` / `runplan.py`** — move the build to its destination with the existing
   shift/remap/orphan-drop path, exactly as the player district was moved. The plan file gains
   one rectangle per build with its offset.
6. **After-care, in the existing order:** `fixspawners.py` (1.12 spawners carry entity ids that
   the DFU renames; anything not in the pack → zombie), `terrain.py pad` under each build's
   footprint at its source ground level (the hub's ground is y 56–72, the wasteland's is 90–140:
   the builds go on cut pads, not on fill), `ramp` at every edge, roads to the spine.
7. **Verify:** `anvil112.py topdown` of the source rect vs `topdown.py` of the destination rect,
   overlaid; then the mob-free flight on the local server with the checklist from the blueprint.

Every step reads files and writes files; nothing is done inside a running game except the
vanilla upgrade in step 2 and the pre-generation.

## 4. Remap policy (the decisions, one line per family)

| Family (count in rects) | To | Note |
|---|---|---|
| `chisel:antiblock` (130 k) | white / light-gray concrete by meta (colour) | Antiblock is a full-bright colour block; Simply Light fills the glow role. |
| `chisel:factory*`, `technical*`, `laboratory`, `blocksteel`, `futura` (~110 k) | Chipped / Factory Blocks equivalents (both in the pack), else gray concrete | Chipped 3.x ships the same families under new names; map by look. |
| `chisel:basalt1`, `concrete_lightgray1`, `glass*`, `ironpane` | vanilla basalt, light gray concrete, glass, iron bars | |
| `immersiveengineering:stone_decoration` (~95 k, meta = concrete/leaded/hempcrete/tile…) | IE 1.20 blocks of the same name | IE is in the pack; only the names changed. |
| `immersiveengineering:sheetmetal*`, `metal_decoration*`, `treated_wood*`, `wooden_decoration` | IE 1.20 equivalents | Same. |
| `furenikusroads:generic_blocks` [3] and `road_block_*` (~104 k) | black concrete (road), gray concrete slab (kerb), yellow/white concrete for markings by meta | Roads are what make the vehicles work; keep them flat and dark. |
| `hbm:deco_steel`, `steel_wall`, `steel_scaffold`, `steel_grate`, `railing_*` | IE sheetmetal / scaffolding, iron bars, chains | |
| `hbm:deco_pipe_*` (rusted, framed, quad…) | IE pipes where a pipe exists, else copper / oxidised copper by "rusted" | |
| `hbm:machine_tower_large/small`, refinery and vault dummies, `tileentity_dummy` | the shell only: gray concrete for tower blocks, air for dummies | HBM multiblocks cannot exist; keep the silhouette. |
| `hbm:brick_concrete*`, `brick_light`, `reinforced_*` | gray / light gray concrete, stone bricks | |
| `simplylight:*` (25 k) | sea lantern / glowstone / end rod for edge lights | Keeps the neon. |
| `torchmaster:invisible_light`, `srparasites:infestremain`, `cfm:*`, `mw:*`, `weather2:*` | air | Invisible, gore, furniture with no equivalent, guns. |
| `twilightforest:*` planks/logs (631) | dark oak | |
| `immersivepetroleum:stone_decoration` | IE concrete | |

Anything not in this table is decided when it shows up light gray on the render.

## 5. Order of work

0. **Pre-generate the 5 km box locally** so a site can be chosen (Chunky is in the pack; a
   `localpregen.py` drives the local server console: `chunky world wasteland`, `chunky corners
   -600 -1250 4400 3750`, `chunky start`, wait for "Task finished", `stop`). Then render it and
   pick the zone in §2. *Needs `eula=true` in `server\`.*
1. Write `extract112.py`; extract the seven volumes; render each from the volume to prove the
   extraction and the y-cut (the ships must be gone from the hub render).
2. Run the vanilla upgrade on a copy of `world/` and of the three district saves; confirm it
   completes and that a known modded position reads as air. *Needs `eula=true` in each copy.*
3. Fill `remap112.json` from the worklist, family by family, per §4. Review the light-gray count
   on the first merged render; fix the table until the count is what we accept.
4. Write `merge112.py`; merge the plaza first (smallest with the most modded content, 83%), render,
   review; then the sewers, the industrial zone, then the city.
5. Add the seven rectangles to the transplant plan with their offsets into the chosen zone;
   `runplan.py --dry-run`, then write; `fixspawners.py wasteland`.
6. Terrain: pads and ramps under the seven footprints from the pristine v2 set + the new pregen;
   the road spine crater → city → radio tower.
7. Render diff, then the flight. Findings into the district map page (`makemap.py` gets the new
   sites).

Steps 1, 3 and 4 are the real work; the rest is the existing pipeline.

**Status 2026-09-03 (map work parked while the design session finishes the map):** steps 1-4 are
built and proven, map-independent, on the local machine:
- `extract112.py` - volumes for all six rects (`incoming/volumes/*.npz`); the hub's y-cut removes the ships.
- `upgrade112.py` - the vanilla 1.20.1 server `--forceUpgrade` on a copy of each save. Works on the
  Forge 1.12 saves as-is (plaza: 2,382 chunks in 7 s; `world`: 12,742 chunks in about 90 s). Vanilla
  blocks flatten exactly (`concrete[0]` becomes `white_concrete`, DataVersion 3465); modded ids become air.
- `makeremap112.py` writes `remap112.json` - 1,258 (name, meta) pairs resolved, none unmapped; every
  target validated against the vanilla block report and the pack's IE / Factory Blocks / Chipped
  blockstates (`scratch/reports/`).
- `merge112.py` - writes the modded layer back; drops non-vanilla block entities.
- `verify112.py` - block-by-block proof (`--rect` also checks the cut zone is air): plaza, sewers,
  Bio Gen, east compound CLEAN; industrial zone 10 gravel and the hub 13 vines lost to the upgrade
  server's few ticks of physics (negligible). Hub: 41.3 M positions, 3.74 M modded written, ships
  gone (2,493 ship block entities dropped with them). `merge112.py --rect` applies the y-cut to the
  upgraded chunks too, because the ships were vanilla blocks the upgrade kept.
Merged 1.20.1 region sets sit in `scratch/upgrade/<build>/world/region` at source coordinates,
ready for `transplant.py` once a destination exists. Nothing has touched the wasteland world. Nothing in this plan is
done on the hosted server; it all lands on the local `wasteland` world and is uploaded as a
region set when it has passed the flight.

Related: [[gscraft-foreign-worlds]] (census, worklist), [[gscraft-player-builds]] (the 1.20 transplant
path), [[gscraft-scale-and-travel]] (box, roads), the blueprint page (map plans).
