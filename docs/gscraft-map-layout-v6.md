# GSCraft Wasteland — Map Layout v6 (placement sheet)

2026-09-03. The coordinates behind `gscraft-map-design.md` §2, revised against everything now
decided: the design (draft 5), the quests, the scale note, the tower generator, and the six
foreign builds as converted. Two owner rulings drive this revision: **the radio tower stands in the
camp**, and **no site is bound to the old pads** — every building is placed where it belongs.

Every rectangle here is chunk-aligned, because the transplant tool moves whole chunks. Vertical
offsets are whole sections (16 blocks), and each pad is cut to *source ground + 16·k* (measure the
source ground from the terrain, never from the spawn point: two of the saves are superflats with the
ground at y 54 and y 230) so the build
lands on its pad without a block-level re-slice. "Terrain: pending" means the ring there is not
generated yet; the 10 km pre-generation is running on the local server and those sites get their
final pad level (and a dry/wet check) from its render.

## 1. What changed and why

| Item | Draft 5 | v6 | Why |
|---|---|---|---|
| Radio tower | own pad 2.1 km E | **in the camp**, north-east corner | owner ruling. The beacon lights over home; the finale's countdown and its waves are one place. The camp's NE corner is its flattest 128×128 (y ≈ 99, spread 36 blocks), between Tune's shack and Marshall's gate, so the players pass the tower on every trip east. |
| Novo Expograd Industrial Zone | old substation pad 1.5 km S | **1.1 km ENE, on the spine**, north of the district's west end | the first strongpoint should sit on the road everyone uses, so held ground is a forward base and not a detour; Act I already goes east (acacia hall, glass tower). Still foot range. |
| Financial Plaza + sewers | old hospital pad 2.5 km SE | **2.1 km WEST of the camp, on dry land** | the review found the lake site an island with 440 m of water on its road; the owner ruled dry land. The west window (x −1984…−1777, z 832…1023) is the flattest, driest, unbuilt ground at road range, and it puts a strongpoint on the far side of the camp from the district, so attacks come from more than one direction. The old hospital pad is restored to lake. |
| The settlement (east compound) | water pad re-cut, 3.6 km E | **same place, on merit** | the wet seed is a feature here: a lakeside town reachable by boat as well as by road (trip 8). Re-cut 288×304, raised to y 80. |
| Bio Gen offices | beside the runway | **same**, pad's west end, two groups | a loot site the runway trip passes; the runway keeps 420 m. |
| The hub (Novo Expograd city) | air ring ≈ (6000, 1500) | **same direction, 6.0 km E** | the accepted decision: the air ring is expedition-only and the hub is its prize. East keeps it on the axis camp → district → runway, a 2.4 km flight from the runway. |
| Old substation pad | Novo | **restored to terrain** | freed; a bare levelled square in the ring would read as a site. One pass from the pristine set. |
| District → tower road | needed | **dropped** | the tower is home. Replaced by district → Financial Plaza. |

## 2. The camp (0 – 0.2 km), x/z −176…207

As draft 5 §2.2, with the tower added and one building moved.

| Element | Blocks (x0 z0 x1 z1) | Level | Note |
|---|---|---|---|
| **Radio tower compound** | 64 −144 191 −17 (chunks 4..11 × −9..−2) | pad y 99 | `tools/tower.py` retargeted: PAD, GROUND_Y 99, origin (107, 100, −101); templates rebuilt. Stage 0 placed at world build. |
| Tune's radio shack | 40 −120 55 −105 | rim | moved 20 m west, at the compound's west gate; its own small mast stays as the practice echo. |
| Marshall's gatehouse | 150 0 173 15 | rim | unchanged; the compound's south wall is 17 m north of it. |
| Walker, Tony, Michael, James | as draft 5 | small pads | each NPC site gets a pad at its own median ground (`tools/pads_camp.json`: Walker 94, Michael 108 as a terrace over the crater lake, Marshall 111, Tony 84, Tune 85, James 88) with ramps, crater and tower protected; `camp.py` places the buildings on them. |
| Crater, spawn, camp outline | −16…47 / 19 94 26 / −176…207 | — | unchanged. |

The spine leaves at Marshall's gate (173, 8) and runs east.

### 2.1 The tower lock (owner ruling)

The compound is sealed: the only thing that changes a block inside x 64…191, z −144…−17 is a quest
reward running a stage function. Three layers, none of which the stage functions touch (they are
server-run `/place template`):

1. **KubeJS, two files** — `build/kubejs/server_scripts/gscraft_tower_lock.js`: player break, place
   and right-click cancelled inside the rect (ops in creative bypass, so the world build can be
   hand-edited). `build/kubejs/startup_scripts/gscraft_tower_lock_native.js` (Forge events, which
   KubeJS 2001 exposes to startup scripts only): explosions lose every affected block in the rect;
   mob griefing denied for any entity standing inside (zombie doors, creepers, endermen, and
   Improved Mobs digging where it asks the gamerule); fluids cannot flow in; pistons within 13
   blocks of the edge do nothing; non-player placements (falling blocks, vehicles, dispensers)
   cancelled. Both load clean on the local server (boot check 2026-09-03).
2. **FTB Chunks** — `protect_unknown_explosions: true` in the world config. This build of FTB
   Chunks (2001.3.8) has no server-owned claims, so the compound is not claimed; the script is the
   protection. Nothing stops players claiming those chunks for themselves, and that is fine: the
   script does not care who owns them.
3. **Our own tools** — the rect joins the crater as a protected rectangle in the terrain passes
   (`runpass.py` / `terrain.py`), so no pad, ramp or smooth pass ever writes into it, and the
   Chunky pre-generation cannot touch it because the camp is already generated.

The templates contain nothing flammable (iron, chain, glass, sea lantern, stone slabs, gravel,
cobblestone, lightning rod, beacon), so fire is not a path in. Two things to prove on the local
server in Phase C: that Improved Mobs' digging respects the mob-griefing event, and that an
Immersive Vehicles crash into the fence breaks nothing.

## 3. Strongpoints and sites — the placement table

Distances are from the camp centre (16, 16), straight line. Ranges are draft 5's: foot ≤ 1.5 km,
road 1.5–4 km, air 4.5–6.5 km.

| Site | Kind | Destination blocks (x0 z0 x1 z1) | Size | From camp | Source (rect in `buildmap/foreign/rects.json`) | dy | Pad level | Terrain |
|---|---|---|---|---|---|---|---|---|
| **Novo Expograd Industrial Zone** | strongpoint 1 (industry, Walker) | 992 96 1135 255 (chunks 62..70 × 6..15) | 144×160 | 1.06 km ENE | `novo_industrial` −432→… source x 624..767, z 144..303 | −160 (superflat ground 230 → 70) | new pad, y 70; pregen terrain median 71, 10% water in the margin | generated |
| **Residential block** | strongpoint 2 (medical, Tony) | district, from 1328, 1376 | — | 1.9 km | in place | — | — | built |
| **Industrial plant** | strongpoint 3 (fuel/water, Michael) | 1904 864 2367 1135 | 464×272 | 2.3 km | in place | — | — | built |
| **FR-06 complex** | strongpoint 4 (power/hangar, Michael) | 2192 400 2575 927 | 384×528 | 2.45 km E | in place | — | — | built |
| **Financial Plaza** | strongpoint 5 (electronics, Tune) | −1952 848 −1793 991 (chunks −122..−113 × 53..61) | 160×144 | 2.1 km W | `financial_plaza` | +16 (superflat ground 54 → 70) | new pad 176×160 at y 70 on dry, flat, unbuilt ground west of the camp (owner: dry land; the lake site is restored) | generated |
| **The sewers** | dungeon, under the plaza | −1920 880 −1825 975 (chunks −120..−115 × 55..60) | 96×96 | under Financial Plaza | `sewers` | −16 (y −16…50, below the pad) | none; section-stacked into the plaza's chunks below y 48 | v5 pad |
| **The settlement** | loot site, road + boat | 3520 640 3791 927 (chunks 220..236 × 40..57) | 272×288 | 3.7 km E | `world_east_site` | +16 (ground 62–70 → 78–86) | water pad re-cut 288×304 at y 80 (from 72) | v5 pad, water around |
| **Runway** | air (Michael's airfield tier) | 3040 2519 3470 2710 | 430×192 | 3.9 km SE | strongpoint pad, east 430 m | — | airfield pad re-cut to y 67 (from 64) | v5 pad |
| **Bio Gen offices, south group** | loot site | 2976 2528 3039 2591 (chunks 186..189 × 158..161) | 64×64 | 4.0 km SE | `biogen_strip` chunks 29..32 × −63..−60 | +64 (ground 3 → 67) | airfield pad west end, y 67 | v5 pad |
| **Bio Gen offices, north group** | loot site | 2976 2608 2991 2639 (chunk 186 × 163..164) | 16×32 | 4.0 km SE | `biogen_strip` chunk 30 × −75..−74 | +64 | same | v5 pad |
| **The hub — Novo Expograd** | air-ring prize, never attacked | 5600 1184 6431 1823 (chunks 350..401 × 74..113) | 832×640 | 6.0 km E | `world_hub` (y ≤ 103, ships cut) | +16 (edge ground ≈66 → 82) | new pad, y 82; pregen terrain median 71, p90 89, 12% water | generated |
| Radio tower | endgame | camp, §2 | 128×128 | 0.1 km | `tools/tower.py` | — | y 99 | v5 |
| **The Woods** (planned) | wilderness zone, quest focus | 400 −3500 2400 −1500 | 2000×2000 | 2.9 km NNE | regenerated under the `woods` LC profile (no city); 5 sparse structures; `docs/gscraft-woods-plan.md` | — | none | generated |
| Old substation pad | — | 215 1415 374 1574 | 160×160 | 1.5 km S | pristine chunks copied back | — | restored | v5 |

The library, hempcrete compound, stone complex, mud village, acacia hall, glass tower and the small
district builds stay where they are (draft 5 §2.3). The generated Lost Cities towns stay as found.

## 4. Roads and water

1. **Spine:** gate (173, 8) → Novo's west gate (≈ 992, 176) → the district's north-west corner
   (896, 384). About 1.0 km; the old rail causeways west of the district are used where they lie
   on the line.
2. **West road, camp → Financial Plaza:** from the camp's west edge (−176, 40) to the plaza's east
   gate (−1780, 924). About 1.8 km, routed around water and buildings by `tools/roads.py`.
3. **District → runway:** from the mud village (2368, 1552) south-east to the pad (3040, 2600).
   0.9 km. The settlement is reached by road along the district's east side and by boat.
4. **District → settlement:** from the district's east edge (3103, 783) to the settlement's west gate
   (3512, 783). 0.4 km, plus the boat.
5. Roads are routed (`roads.py route`: least-cost path on 8-block cells, water ×40, buildings ×80,
   slope) and built (`roads.py build`: 7 wide, black concrete with gray kerbs and a dashed centre line,
   terracotta fill, causeways where water is unavoidable, shoulders ramped 8 blocks out). Routes live
   in `buildmap/routes_v6.json`; the review checks water and steps along them.
6. Inside the camp: the crater ramp must take a car (Phase A); the fallback is draft 5 §2.4.

## 5. Build mechanics this layout needs

- **Vertical shift** in `transplant.py` — DONE: `dy` in whole sections per plan rectangle (section Y
  relabelled, block entities, ticks and entities moved, heightmaps and light dropped, out-of-world
  sections dropped, everything under the build's lowest solid section filled with stone/deepslate
  so there is no void under a raised build). Proven on the plaza at +64: bedrock at 64, stone to 0,
  deepslate below.
- **Section-stack write** in `runplan.py` — DONE: a rectangle with `"sections_below_y": 48` merges
  only its sections (and block entities) below that height into the chunks already at the
  destination. Proven: the sewers at −16 under the plaza at +64 share one chunk column, the sewer
  ceiling at 47, the plaza's bedrock at 64.
- **Plan file** `buildmap/transplant_plan_v6.json` — the seven rectangles of §6 with `source_dir`
  pointing at the merged worlds; `runplan.py --dry-run` is clean (2,467 chunks, every block
  resolves in the pack).
- **Pads** re-cut with `strongpoints.py` / `terrain.py pad` at the levels above, the pristine
  set as the base, then `ramp` at every edge; the runway pad stays one plane.
- **Sources** are the merged 1.20.1 worlds in `scratch/upgrade/<build>/world/region` (verified
  clean); `runplan.py` takes them as extra source worlds, one rectangle each, offsets from this
  sheet.
- **Order** (draft 5 §9 Phase B): border; pads; roads; camp buildings + tower stage 0; transplants
  in the order settlement, Novo, Financial Plaza, Bio Gen, sewers, hub; Chunky; pull the new
  pristine; regenerate the district map page.
- **Runners:** `tools/buildv6.py` does the offline part on a copy of the pre-generated world (copy,
  restore the substation pad, pads from `tools/pads_v6.json`, transplants from the plan, ramps, gaps
  report); `tools/localconsole.py` boots the local server for the in-game part (tower stage 0,
  world spawn, boot check); `tools/localpregen.py` drove the 10 km Chunky run with the border set.
  Roads wait for the Phase A list; the camp buildings for `camp.py`.

## 6. Offsets, for the plan file

| Rect | Source chunks (x0 z0 x1 z1) | Destination chunks | Offset (dx, dz) chunks | dy |
|---|---|---|---|---|
| novo_industrial | 39 9 47 18 | 62 6 70 15 | (+23, −3) | −160 |
| financial_plaza | −27 −73 −18 −65 | 43 148 52 156 | (+70, +221) | +16 |
| sewers | −59 −20 −54 −15 | −120 55 −115 60 | (−61, +75) | −16 |
| world_east_site | −27 92 −11 109 | 220 40 236 57 | (+247, −52) | +16 |
| biogen south | 29 −63 32 −60 | 186 158 189 161 | (+157, +221) | +64 |
| biogen north | 30 −75 30 −74 | 186 163 186 164 | (+156, +238) | +64 |
| world_hub | −91 96 −40 135 | 350 74 401 113 | (+441, −22) | +16 |

Related: `gscraft-map-design.md` (the design), `notes/gscraft-foreign-builds-plan.md` (the
conversion pipeline; its §2 siting is superseded by this sheet), `notes/gscraft-scale-and-travel.md`,
`tools/strongpoints.json`, `build/tower_parts.json`.
