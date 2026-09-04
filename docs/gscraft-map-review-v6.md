# Map review — wasteland v6 (2026-09-03)

The built v6 world (`server\wasteland-v6` on the working machine, master copy
`scratch\worlds\wasteland-v6`), audited by `tools/reviewv6.py`: every one of the 421,201 chunks parsed,
every block name checked against the pack, every planned site, pad, road line and design distance
measured. Numbers below are from the final run (`incoming\renders\v6\review2.json`); the renders it
reads against are in `incoming\renders\v6\` and `docs/renders/`.

## 1. Verdicts

| Check | Result | What it means |
|---|---|---|
| chunks | FAIL by the strict rule, pre-existing | all 441 region files and 421,201 chunks parse; DataVersion 3465 everywhere; 23 sections with Y outside −4..19 exist in the pre-generated world (Lost Cities), none in any rectangle we wrote |
| palette | PASS | every block name in the world resolves in the pack; no 1.12-era names survived the conversion |
| entities | FAIL by the strict rule, pre-existing | 539 `DUMMY` block entities in the pre-generated world (Forge's placeholder for a block-entity type it could not load); none in our rectangles; harmless log noise on load |
| sites | PASS | all seven rectangles present and complete; the two ship boxes above the cut are empty |
| pads | WARN | five pads 99.7 % level across their apron; the hub's apron 89 % (its ramps start inside the measured ring); outlines complete on all six |
| tower | PASS | pad flat at 99; stage 0 (concrete, steel, fence, scaffolding) present; nothing else built |
| camp | WARN | crater untouched vs the pre-gen copy; all six NPC pads level (height spread 0–1); the only built columns on a site are the spine passing through Marshall's gate |
| water | PASS | the plaza now has 5–7 % water in its margin; all four built roads have no water on their line |
| distances | WARN (accepted) | industrial plant and FR-06 are 418 m apart (see §2.4); plaza 2.09 km W, Novo 1.06 km, hub 6.18 km |
| border | PASS | 10,000 blocks centred 1900, 1250; spawn 19 94 26 |

## 2. Issues raised for the owner, and the decisions taken (2026-09-03)

### 2.1 Water — the seed is wetter than the design assumed
25 % of the 10 km box is water (measured on the overview render), plus 2 % ice and 4 % snow.

| Where | Measured | Consequence |
|---|---|---|
| Financial Plaza | 35–43 % water in a 48-block ring around the pad | it is an island. Reachable by boat now; the road needs a causeway |
| district → plaza road line | 440 m of water in 6 crossings | the longest causeway on the map, or a different line (round the lake's north shore) |
| district → runway road line | 236 m of water in 6 crossings | causeways |
| spine camp → Novo → district | 56 m of water in 6 crossings | small bridges; fine |
| settlement, hub, Novo, tower, airfield | 4–7 % water around | fine |

**Decision: dry land.** The plaza and its sewers moved to the driest, flattest, unbuilt window at road
range: x −1952…−1793, z 848…991, 2.1 km WEST of the camp (a ring search over 45,000 chunks of the
pre-generated terrain, scored on water, buildings, height spread and water along the road line). The
old hospital pad is restored to lake from the pristine set. Roads are now routed by `tools/roads.py`
(least-cost path on 8-block cells, water ×40, buildings ×80, slope) and built 7 wide with causeways
only where unavoidable. As built and re-measured along each centre line: spine 1,405 m, no water, road
surface on 96 % of the line (longest break 4 m); west road 2,189 m, no water, 95 % (14 m); runway road
1,392 m, no water, 81 % (32 m) where it threads generated blocks; settlement road 513 m, no water, 89 %
(8 m). The breaks are Lost Cities buildings and streets the line runs into: the road stops at the wall
and resumes past it, which the generated city's own streets carry.

### 2.2 Cities — the wasteland is one-fifth city with highways everywhere
Sampling every 25th chunk: about 20 % of land chunks carry a Lost Cities fingerprint (street blocks,
spawners, sandbags), and the overview render shows LC's highway grid across the whole landmass. So
the "empty first kilometre" concern is gone — there is a generated city inside the Novo pad's margin
and around the settlement, the hub and the plaza — and vehicles already have roads between cities.
**Decision: keep the cities; make the roads connect.** The four roads above are routed around the
generated blocks and join the LC highways where they meet them; the review measures water and steps
along each built road.

### 2.3 Pads cut through generated buildings
Every pad that landed in a city (Novo, settlement, hub, plaza margins) flattened the LC buildings
inside it and left their neighbours cut at the pad edge; the ramp pass skips built columns by design,
so those façades stay as cut walls. **Fixed:** `buildv6.py` now clears generated buildings in a
24-block ring outside every site pad (`terrain.py pad --clear-only` with the pad protected) before the
ramps run.

### 2.4 Two strongpoints under 500 m apart
Industrial plant and FR-06 are 418 m apart, both in place in the district. The 500 m rule was written
for attacks spilling over; these two were built as one complex. **Decision: accepted.**

### 2.5 Camp rim sites
Walker's yard (x 60…99, z 80…111) spans 22 blocks of height and Michael's plant (x −40…−9, z 100…123)
28. **Fixed:** every NPC site now has its own small pad at the median of its own ground with ramps
(`tools/pads_camp.json`: Walker 94, Michael 108 as a terrace over the crater lake, Marshall 111,
Tony 84, Tune 85, James 88), crater and tower protected. The alternative considered was letting
`camp.py` give each building a foundation skirt down to the ground instead of a pad; the pads win
because the yards and vehicle lots around the buildings need flat ground too, and they are small
(the largest 48×40).

### 2.6 Frozen projectiles (player request)
Rockets and shells freeze at the edge of the simulated area and then "follow" the player: the server
only ticks entities within the simulation distance (6 chunks = 96 m in the shipped properties), and a
projectile past that ring sits in a chunk that is still rendered but not ticked. Neither Superb Warfare
nor TaCZ has a lifetime or range option. **Fixed two ways:** `build/kubejs/server_scripts/gscraft_projectiles.js`
retires any gun-mod projectile that is 40 blocks inside the simulation edge from every player or older
than 30 s (mines, charges, vehicles and drones untouched), and the simulation distance is raised to 10
(server.properties, and Dynamic View's ceiling from 6 to 10) so entities tick as far as they render.
Immersive Vehicles already chunk-loads vehicles on roads (`chunkloadVehicles: true`).

## 3. Build findings (fixed, or cosmetic)

| Finding | State |
|---|---|
| Hub edges were cliffs (393 of 1,168 edge columns off by 3+ blocks) | fixed: the `smooth` pass is now part of `buildv6.py`; hub rect re-checked in the final run |
| Novo and Financial Plaza landed 160 and 50 blocks above their pads (superflat sources with ground at y 230 / y 54) | fixed: dy −160 and +16, pads at 70; verified column by column |
| Superflat ground shows as a square inside three sites: stone at Novo, grass at Bio Gen, sandstone under the plaza | cosmetic; a resurface pass (replace the natural top layer of unbuilt columns inside the rect with the pad fill) would hide it |
| Ships over the hub | gone; verified empty above the cut |
| 5,7xx chunks without light / heightmaps | expected: every edited chunk; the game recomputes on first load |
| Lootr: 1.12 chests came across as plain chests with their surviving vanilla items | expected; the design's typed loot arrives by datapack anyway |
| Voice chat tried to bind the Bisect IP locally | server-ip is empty in the local property profiles; the hosted profile keeps the IP |
| `superbwarfare` is the second-largest block namespace in the world (6.1 M palette entries) | the Lost Cities apocalypse pack builds with its sandbags and barricades; nothing to do |
| Lost Cities 7.5.3 logs `Error generating chunk ...: "state" is null` (ChunkDriver.correct) for about 7 % of generated chunks, in the v6 pre-generation and again in the v7 test generation | pre-existing: a building part in the apocalypse pack resolves to a block the pack does not have, so that part of the building is skipped; the chunk still generates. Worth finding the missing block before v7 (the LC asset palettes in the profile), cosmetic otherwise |

## 4. What Phase A (the visual pass) should look at, in order
1. The camp rim: the six NPC sites, the tower compound and its gate side, the crater ramp with a car.
2. The spine line and its six small crossings; where the LC city north of the district meets Novo's pad.
3. Financial Plaza from the lake: is an island plaza the right feel, and where would the causeway land.
4. The settlement's lakeside, the runway's flatness end to end, Bio Gen's green square.
5. The hub by air: its edges after the smooth pass, the cut LC buildings around it, the lake that
   crossed its site (now under the pad).
6. Any place the generated highways run into a pad.

Related: `gscraft-map-layout-v6.md` (placements), `gscraft-map-design.md` (the design),
`notes/gscraft-foreign-builds-plan.md` (the conversion), `tools/reviewv6.py`.
