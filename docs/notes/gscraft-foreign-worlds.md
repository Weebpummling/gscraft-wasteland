
**Foreign worlds (received 2026-09-03 via the owner's Google Drive folder, builder atreyu137):**
two full saves and three world zips, all from ONE Forge **1.12.2** pack (DataVersion 1343):

| Item | What it is | Size |
|---|---|---|
| `world/` | Full save, level name `world`, generator `lostcities_bop`, spawn −790 151 1675, last played 2022-04-23. 27 overworld region files (~150 MB) plus DIM-1, DIM1, DIM7 (Twilight Forest). | ~150 MB overworld |
| `Bio Gen Offices Restricted Areas/` | Full save, same pack, last played 2022-12-18. Region files not yet listed. | unknown |
| `Financial Plaza Quarantine - Copy-20230610-220632.zip` | World zip, 2023-06-11 | 2.7 MB |
| `SewerPVP-20230220-161204.zip` | World zip, 2023-02-21 | 30.8 MB |
| `Novo Expograd Industrial Zone-20230212-005027.zip` | World zip, 2023-02-12 | 11.3 MB |

The `GSCraft-Client.zip` in the same folder is the staged player pack and is ignored.

**The pack behind them** (from `world/level.dat` → `FML/ModList`, 103 mods): Lost Cities 2.0.22 +
Biomes O' Plenty, HBM's Nuclear Tech (`hbm`, 763 blocks), Fureniku's Roads (417), Chisel (249),
Pam's HarvestCraft (223), MrCrayfish Furniture `cfm` (216), Twilight Forest (171), Modern Warfare
`mw` (108), Future MC (68), Macaw's Bridges (47), Immersive Engineering 0.12 (44), Dynamic Trees,
Random Portals, SR Parasites, Vehicle, CustomNPCs, Open Modular Turrets, Simply Light, Weather2,
Torchmaster. **2,910 registered blocks; 254 are vanilla.** The registry (numeric id → name) is in
`FML/Registries/minecraft:blocks/ids` of each save's level.dat — that table is what makes the
transplant possible.

**Why nothing existing works:**
- 1.12 chunks store blocks as numeric id + 4-bit metadata (`Blocks`/`Add`/`Data` arrays per
  section), not a palette of names. The 1.20.1 tools in this repo (`anvil.py`, `scanregion.py`,
  `transplant.py`) read palettes and cannot open them.
- Vanilla's upgrader (`--forceUpgrade` on a 1.20.1 server) flattens only the 254 vanilla ids;
  every modded id becomes air. Forge never supported carrying 1.12 modded chunks forward.
- Amulet can read 1.12 Forge saves and name modded blocks from the registry, but its cross-version
  export passes unknown blocks through unchanged (`hbm:xyz` with 1.12 metadata), which 1.20.1
  loads as air, and it is a GUI tool with its own numpy pin — not for the firm Python.

**The safe path — extend our own pipeline, keep every decision in a table:**
1. **Reader** (`tools/anvil112.py`, to write): parse the 1.12 region format (section
   `Blocks` + `Add` + `Data` nibbles, `TileEntities`, `Entities`), name every block through the
   save's own `FML/Registries/minecraft:blocks` table, and emit the same per-chunk material
   layers `worldscan.py` produces today, so `topdown.py` renders the old worlds and
   `buildmap.py` finds the builds in them unchanged.
2. **Census** before any remap: every `(name, meta)` pair with counts, per world, into
   `buildmap/foreign/<world>_blocks.json`. This is the list to decide against, and it is the
   only honest measure of what will be lost.
3. **Remap table** `tools/remap112.json`, two layers: (a) the vanilla flattening table
   (1.12 id+meta → 1.13 blockstate name; import the published table from the `minecraft-data`
   repo as a data file, no library install); (b) the modded layer in the same style as
   `remap.json`: `hbm:concrete_*` → concrete colours, `furenikusroads:*` → the road blocks
   already in the pack (black/gray concrete, asphalt-like slabs), `chisel:*` → the Chipped
   equivalents, `cfm:*` furniture → air or the nearest vanilla, `mw:*` → air, `twilightforest:*`
   planks → vanilla woods. **Unmapped names default to a visible placeholder (light gray
   concrete), never to air**, so a hole in the table shows up on the render instead of as a
   missing wall.
4. **Writer**: convert the selected rectangles into 1.20.1 palette chunks and hand them to
   `transplant.py` with the existing shift/remap/orphan-drop logic. Block entities from cut
   mods are dropped; chests keep vanilla items only (1.12 item ids do not survive either).
5. **Verification**: render before (1.12 reader) and after (1.20.1 reader) with `topdown.py`
   and diff the two images; then the in-game flight.

**Order of work:** census first (steps 1–2) on `world/` — it shows how much of a build is
`hbm`/`furenikusroads` and whether the remap is worth it per site — then the table, then the
writer. Do not start the writer before the census exists.

**Census DONE (2026-09-03, `tools/anvil112.py census|topdown`, outputs in `buildmap/foreign/`,
renders `docs/renders/foreign_*.png`).** All five saves read cleanly; the reader names every block
through each save's own registry. Headline: 95% of the 30.5 M modded blocks are worldgen strata
(Chisel marble2/limestone2/basalt2 [15], HBM and Modern Warfare ores, Dynamic Trees leaves, BOP
dirt) — terrain, not builds. The builds themselves are small and tractable:

| Rect (`buildmap/foreign/rects.json`) | Save | Blocks (x0 z0 x1 z1) | Size | Placed | Modded | What it is |
|---|---|---|---|---|---|---|
| `world_hub` | world | −1456 1536 −639 2175 | 832×640 | 1.50 M | 25% | The desert hub: a ~140×140 dark platform with a rail spine, a pink/orange starship (~60×220), a pale hangar-ship (~80×150), a brown battleship (~30×180), red-sandstone plazas, roads. 7.4 k IE slabs, 2.4 k HBM multiblock dummies, 1.3 k signs, 628 beds. **This is the custom cityscape.** |
| `world_east_site` | world | −432 1472 −161 1759 | 272×288 | 228 k | 5% | Red-sandstone compound with roads; nearly vanilla. |
| `financial_plaza` | Kinyu Hiroba Quarantine Zone | −432 −1168 −273 −1025 | 160×144 | 236 k | 83% | Office/plaza block: 123 k `chisel:antiblock`, concrete, IE stone decoration, Simply Light. |
| `novo_industrial` | Novo Expograd Industrial Zone | 624 144 767 303 | 144×160 | 34 k | 96% | Refinery yard: HBM cooling towers (`machine_tower_large/small`), refinery dummies, IE stone decoration, roads. |
| `sewers` | Novo Expograd Sewers | −944 −320 −849 −225 | 96×96 | 59 k | 99% | Sewer complex: 37 k IE stone decoration, Chisel factory/technical, HBM rusted pipes and grates. |
| `biogen_strip` | Bio Gen Offices Restricted Areas | 464 −1200 527 −945 | 64×256 | 7 k | 34% | Three small HBM-brick offices. Marginal. |

Everything else the cluster pass found is generated: Lost Cities 2.0 city blocks (`stonebrick` +
`double_stone_slab` + 40–150 spawners per cluster) and HBM's own worldgen (2-chunk bunkers with
`reinforced_sand`, launch pads, satellite poles, and the 1-chunk `stonebrick` loot hut with 4
spawners + 8 chests that recurs in every save — the same fingerprint rule as the 1.20 pack).
The 400×400 white square in the Sewers render is snow cover, not a build.

**Remap worklist:** `tools/remap112_todo.json` — every modded name inside the six rectangles with
counts, metas and which rects use it; fill `to` with a 1.20.1 block or `air`. The table is
dominated by a few families: Chisel (`antiblock`, `factory*`, `technical*`, `basalt1`,
`concrete_lightgray1`, `laboratory`, `glass*`) → Chipped/vanilla concrete/glass; Fureniku's Roads
(`generic_blocks`, `road_block_*`) → black/gray concrete and slabs; IE `stone_decoration` (meta =
concrete/hempcrete/leaded/etc.) → the IE 1.20 equivalents, which are IN the pack; HBM
`deco_steel`/`steel_*`/`deco_pipe_*`/`machine_tower_*` → IE sheetmetal, scaffolding and vanilla
iron/chains; Simply Light → sea lantern / glowstone; `srparasites:infestremain` → air.
The vanilla side needs the 1.12→1.13 flattening table for the (name, meta) pairs present
(red_sandstone, concrete [colour meta], wool, planks, stained glass, stonebrick variants…).

**Next:** fill the table (own the decisions, one line per family), then the writer.

**Getting the files here:** the Drive connector returns file bodies base64-inline and is only
usable for small files (the two `level.dat`s were fetched that way into
`G:\GSCraft\incoming\drive-world\`). The region folders and zips come down through the browser
(Drive's folder download zips them) into `G:\GSCraft\incoming\`.

Related: [[gscraft-player-builds]] (the 1.20.1 transplant pipeline), [[gscraft-phase-log]].
