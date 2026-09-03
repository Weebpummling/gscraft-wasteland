# GSCraft Wasteland — Quests and Tasks

Draft 1, 2026-09-03. Companion to `gscraft-map-design.md` (draft 5). Every quest here is buildable
in FTB Quests with the pack as it is; task types used are item hand-in, location, kill, stage flag
(set by KubeJS), advancement and checkmark; rewards are blueprints, KubeJS stages, items and
commands.

## 1. How the quests push outward

The map has four areas at increasing distance, and every chapter is written so that the **next
blueprint needs an item that only drops in the next area out**. Players are never told to go
further; they run out of things to find where they are.

| Act | Area | From the camp | What is there | How you get there | Sessions (est.) |
|---|---|---|---|---|---|
| **I — The Camp** | foot range | 0 – 1.5 km | camp ruins, glass tower (1.3 km), acacia hall (1.55 km), the generated ruins around the camp, **Novo** (1.5 km S) | on foot | 1–2 |
| **II — The West Edge** | near district | 1.5 – 2.5 km | residential block (1.9), copper tower, prismarine hall, hempcrete compound (2.2), the tower ruin (2.1), **industrial plant** (2.4), library (2.5), **FR-06** (2.5) | on foot, then the first car | 3–5 |
| **III — The Far Ring** | far road range | 2.5 – 4 km | **Financial Plaza** (2.5 SE) and the sewers under it, stone complex (2.9), mud village (2.8), the settlement (3.6 E), Bio Gen and the runway (3.9 SE) | car, truck, boat | 6–9 |
| **IV — The Sky** | air ring | 4.5 – 6.5 km | the hub (6.2 km E), the generated cities kept as found | aircraft | 10–12 |

Rules that hold across every chapter:

- **Introductions first.** Each NPC's first quest asks for common items from the camp's own ruins.
  Marshall does not speak until all five introductions are done.
- **One strongpoint per act boundary.** Novo closes Act I; the residential block and the plant are
  Act II; FR-06 and Financial Plaza are Act III; the hub is Act IV. The tower needs one component from
  each.
- **The tower unlocks late.** Marshall opens the tower chapter only after **significant progress**:
  three strongpoints held (Novo, the block, the plant), Workshop 2, Generator 2, Storage 2, and a
  car built. That is the end of Act II at the earliest. Stages 1–2 are Act II parts, 3–4 are Act III,
  5 is Act IV, so the tower is repaired across the second half of the game, not at its end.
- **Every attack is a quest.** Holding a site through its first attack is a task in the owning NPC's
  chapter, so the loop and the book agree.
- **Hand-ins of loot-only components need no "found in raid" tag**: they have no recipe, so the item
  is the proof of the trip.

Quest counts: Walker 14, Tony 10, Michael 13, Tune 10, James 11, Marshall 19 (loop 6, defences 4,
tower 9). Seventy-seven quests. Which of them one outing clears is the trip table in
`gscraft-map-design.md` §3.5; how many outings it takes is up to the players.

---

## 2. Walker the Foreman — Workshop, Garage, Storage

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| W1 | Nuts and bolts | I | camp ruins | hand in 8 bolts, 8 nuts, 1 wrench | — | fastener-kit blueprint; the workbench is yours |
| W2 | A place for everything | I | camp | craft and hand in 2 fastener kits | W1 | **Storage 1**: basic backpack recipe, stash crates at the claim |
| W3 | Frame of mind | I | camp, glass tower | hand in 12 metal scrap; show a welding torch | W2 | steel-frame blueprint, **Workshop 1** (IE machine recipes) |
| W4 | The toolbox | I | camp | show a toolbox (crafted) | W3 | Workshop 1 effects; 16 iron ingots |
| W5 | South, a mile | I | **Novo**, 1.5 km S | reach Novo (location); kill 12 of its garrison | W4, J1 | Novo appears on the strongpoint board |
| W6 | Hold the yard | I→II | Novo | stage `novo_held`; stage `novo_defended` (survive the first attack) | W5, Marshall R2 | **Workshop 2**; **Storage 2**: iron backpack, stack upgrade ×2 |
| W7 | Wheels | II | camp, Novo | hand in 1 motor assembly, 4 steel frames, 1 car battery | W6, M2 | **Garage 1**: first car recipe, cargo crate; stage `car_built` when one is crafted |
| W8 | Fuel run | II | camp | hand in 2 fuel cans | W7, M5 | fuel recipes at the garage pump |
| W9 | Heavy metal | III | Novo | hand in 1 heavy diesel engine, 2 motor assemblies | W8, `novo_held` | **Garage 2**: truck recipe |
| W10 | The big pack | III | Novo | hand in a second heavy anchor cable (Novo respawns them while held), 2 fastener kits | W9 | **Storage 3**: gold backpack, **everlasting upgrade** (the secure pack), truck cargo |
| W11 | Mast section kit | II–III | camp | show 1 mast section kit (6 steel frames + 2 fastener kits + heavy anchor cable) | W6, `novo_held` | the kit is Marshall's X1 hand-in |
| W12 | Boats | III | the settlement | reach the settlement by water (location); hand in 1 pressure gauge | W8, J4 | boat cargo recipe |
| W13 | Hangar rights | IV | FR-06, the hub | hand in 1 avionics module, 1 satellite receiver | W9, M11, J7 | **Garage 3**: aircraft recipe; **Storage 4**: diamond backpack, aircraft cargo |
| W14 | Foreman's pride | IV | everywhere | hand in one of every hardware and tool item (12 items) | W13 | Workshop 3; a named tool |

---

## 3. Tony the Medic — Medical

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| T1 | Field dressing | I | camp ruins | hand in 4 bandages, 2 painkillers | — | med-kit blueprint |
| T2 | Stock the clinic | I | camp | craft and hand in 2 med kits | T1 | **Medical 1**: revive range up; 4 med kits back |
| T3 | Neighbours | II | **residential block**, 1.9 km | reach the block (location); find 3 blood bags there | T2, J2 | the block on the strongpoint board |
| T4 | Take the block | II | residential block | kill 12 of its garrison; stage `residential_held` | T3, Marshall R3 | 8 bandages, 4 antiseptic |
| T5 | Hold the block | II | residential block | stage `residential_defended` | T4 | **Medical 2**: reduced death penalty |
| T6 | Analyzer | II–III | residential block | hand in 1 medical analyzer | T5 | Medical 2 effects; blood-bag recipe |
| T7 | Bio Gen | III | **Bio Gen**, 3.9 km | reach Bio Gen (location); hand in 1 surgical kit | T6, J4 | surgical-kit use: full revive |
| T8 | Triage | III | anywhere | stage `revives_3` (three teammate revives, counted by KubeJS) | T5 | 8 med kits |
| T9 | Full power | IV | the hub | hand in 1 military power filter | T7, J7 | **Medical 3** |
| T10 | Ready room | IV | the base | hand in 10 med kits, 4 blood bags at the claim | T9 | finale readiness flag; Marshall X6 opens |

---

## 4. Michael the Engineer — Generator, Water

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| M1 | Sparks | I | camp ruins | hand in 3 wire spools, 1 power cord, 1 water filter | — | wiring-harness and filter-cartridge blueprints |
| M2 | Lights on | I | camp | hand in 2 wiring harnesses, 1 light bulb | M1 | **Generator 1**: lighting recipes, IE power |
| M3 | Clean water | I | camp, the lake | hand in 2 filter cartridges | M2 | **Water 1**: coolant and sealed-tubing blueprints |
| M4 | The refinery | II | **industrial plant**, 2.4 km | reach the plant (location); kill 12 of its garrison | M3, J2 | the plant on the board |
| M5 | Hold the plant | II | industrial plant | stage `plant_held`; stage `plant_defended` | M4, Marshall R4 | **Water 2**: biodiesel chain, fuel cans |
| M6 | Pump it | II | industrial plant | hand in 1 industrial pump | M5 | cooling-loop blueprint |
| M7 | Fuel for the road | II | camp | hand in 4 fuel cans | M5 | Walker W8 opens; 2 fuel cans back |
| M8 | The reactor plaza | III | **FR-06**, 2.5 km E | reach the plaza (location); kill 16 of its garrison | M6, W7 | FR-06 on the board |
| M9 | Hold FR-06 | III | FR-06 | stage `fr06_held`; stage `fr06_defended` | M8, Marshall R5 | **Generator 2**; transformer cores start spawning |
| M10 | Core | III | FR-06 | hand in 1 transformer core | M9 | generator-kit blueprint |
| M11 | The hangar | III→IV | FR-06 hangar | hand in 1 avionics module; hand in 1 reactor control module | M10 | hangar unlocked; Walker W13 opens |
| M12 | Purification | III | industrial plant | hand in 1 purification membrane | M6 | **Water 3** |
| M13 | Full grid | IV | the hub | hand in 1 military power filter, 2 wiring harnesses | M11, J7 | **Generator 3** |

---

## 5. Tune the Technician — Radio and intel

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| U1 | Static | I | camp ruins | hand in 1 circuit board, 2 capacitors, 1 broken radio | — | circuit-assembly blueprint |
| U2 | The map | I | camp | hand in 2 circuit assemblies | U1 | **Radio 1**: shared waypoints, the warning system |
| U3 | Listening post | II | the tower ruin (2.1 km), the library | reach both (location); hand in 1 hard drive | U2, J2 | the strongpoint board shows garrison strength |
| U4 | The plaza | III | **Financial Plaza**, 2.5 km SE | reach the plaza (location); kill 16 of its garrison | U3, W7 | Financial Plaza on the board |
| U5 | Hold the plaza | III | Financial Plaza | stage `financial_held`; stage `financial_defended` | U4, Marshall R6 | **Radio 2**: longer warnings; antenna-element blueprint |
| U6 | Under the plaza | III | the sewers | reach the sewers (location); kill 20 there; hand in 1 encrypted radio | U5 | the target is named a full cycle early |
| U7 | Military board | III | Financial Plaza | hand in 1 military circuit board | U5 | transmitter blueprint |
| U8 | Antennas | III | camp | craft and show 4 antenna elements | U5 | 4 antenna elements back |
| U9 | Array | IV | the hub | hand in 1 phased array element | U8, J8 | antenna-array blueprint; **Radio 3** |
| U10 | Technician's ear | IV | everywhere | hand in one of every electrical item (8) | U9 | Radio 3 effects: the board shows the next target's timer |

---

## 6. James the Scout — expeditions

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| J1 | Get your bearings | I | glass tower, acacia hall | reach both (location) | — | waypoints; a compass and a map |
| J2 | The west edge | II | residential block, hempcrete compound, library | reach all three (location) | J1 | waypoints; the expedition board |
| J3 | Paper trail | II | offices, the library | hand in 2 folders of documents | J2 | 8 valuables' worth of loot |
| J4 | The far ring | III | stone complex, mud village, the settlement, Bio Gen | reach all four (location); the settlement and Bio Gen by car | J3, W7 | waypoints; Tony T7 and Walker W12 open |
| J5 | Settle in | III | the settlement | hand in 3 valuables found there | J4 | a boat |
| J6 | Runway | III | the runway | stand on the runway (location); hand in 1 hard drive | J4 | aircraft prep flag |
| J7 | The hub | IV | **the hub**, 6.2 km | reach the hub by air (location) | J6, W13 | the hub's loot tables switch on |
| J8 | Bring it back | IV | the hub | hand in 1 phased array element, 1 satellite receiver | J7 | Tune U9 and Walker W13 open |
| J9 | Every city | IV | the air ring | reach the four generated cities (location) | J7 | 4 rare components' worth of loot |
| J10 | Cartographer | IV | everywhere | reach every named site on the map (location, 20) | J9 | a named backpack |
| J11 | Every ruin | IV | everywhere | hand in one of each of the thirty small items | J10 | the Collector analogue: an extra everlasting slot |

---

## 7. Marshall — the loop, the defences, the tower

**Gate to speak:** W1, T1, M1, U1, J1 all done.

### 7.1 The strongpoint loop

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| R1 | Muster | I | camp | checkmark; read the strongpoint board | the five introductions | the board; the claim marker item |
| R2 | Novo | I | Novo | place the claim marker at Novo (stage `novo_held`) | R1, W5 | fortify clock starts; Walker W6 opens |
| R3 | The block | II | residential block | stage `residential_held` | R2, T3 | Tony T4 opens |
| R4 | The plant | II | industrial plant | stage `plant_held` | R2, M4 | Michael M5 opens |
| R5 | The plaza and the reactor | III | FR-06, Financial Plaza | stage `fr06_held` and `financial_held` | R3, R4, `car_built` | Michael M9, Tune U5 open |
| R6 | Every site | III | all five | all five held at once (stage `all_held`) | R5 | component respawn rate doubled |

### 7.2 Walls, defences, farm

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| D1 | Walls | I | the claim | hand in 32 concrete, 2 fastener kits | R1 | **Walls 1**: barricade and razor-wire recipes |
| D2 | Guards | II | the claim | stage `novo_defended` and `residential_defended` | D1 | **Walls 2**: guard villagers (Recruits later) |
| D3 | Farm and kitchen | II | the claim | hand in 16 seeds, 8 bowls, 1 med kit | D1 | Farmer's Delight kit; **Farm 1** |
| D4 | Bunker | III | the claim | hand in 64 concrete, 4 steel frames, 1 heavy anchor cable | D2, W9 | **Walls 3**: blast doors, turret-style defences |

### 7.3 The tower

**Gate ("significant progress"):** R2, R3, R4 done; Workshop 2, Generator 2, Storage 2; stage
`car_built`. Then X1 opens.

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| X1 | The tower | II | the tower ruin | reach the tower (location); checkmark after Marshall's briefing | the gate above | the tower chapter; the parts rack at the gatehouse |
| X2 | Mast section kit | II | camp, Novo | hand in 1 mast section kit | X1, W11 | **stage 1** placed; the mast stands |
| X3 | Cooling loop | II | camp, the plant | hand in 1 cooling loop | X2, M6 | **stage 2** placed |
| X4 | Generator kit | III | camp, FR-06 | hand in 1 generator kit | X3, M10 | **stage 3** placed; the lights come on |
| X5 | Transmitter | III | camp, Financial Plaza | hand in 1 transmitter | X4, U7 | **stage 4** placed; the dish |
| X6 | Antenna array | IV | camp, the hub | hand in 1 antenna array | X5, U9, T10 | **stage 5** placed; the beacon lights; the countdown starts |
| X7 | Hold the line | IV | the base | survive waves 1–4 (stages `wave_1`…`wave_4`) | X6 | between waves: 8 med kits, ammunition |
| X8 | The boss | IV | the base | kill the boss (kill task) | X7 | the game's ending; the season flag for the future |
| X9 | Afterwards | IV | camp | checkmark | X8 | free play; the board stays live |

---

## 8. How the acts feel in play

**Act I (sessions 1–2).** Five introductions in the camp's own ruins; the workbench, the first
backpack, lights. James sends them to the glass tower and the acacia hall to learn the ground. Walker
sends them south to Novo, the one strongpoint in walking range; Marshall speaks; Novo is taken and
held through its first attack. Storage 2 and Workshop 2 arrive. Nothing here needs a vehicle.

**Act II (sessions 3–5).** The residential block and the plant are taken and held; the first car is
built from Novo's parts and the plant's fuel. The tower ruin is found and Marshall opens the chapter;
stages 1 and 2 go up. The district's west edge is looted for electrical items. The players are now
2.5 km out on foot or wheels, and the loop is running with three sites in the pool.

**Act III (sessions 6–9).** FR-06 and Financial Plaza need the car to reach and hold; the truck
appears; the secure pack arrives. Stages 3 and 4 go up: the tower has power and a dish. The far
ring (settlement, Bio Gen, the sewers) supplies the third-level components. Five sites in the pool
means an attack somewhere every cycle, and the warning timer is now the players' calendar.

**Act IV (sessions 10–12).** The hangar, the runway, the plane. The hub is reached, the phased array
element comes home in the plane's cargo, the antenna array goes up, the beacon lights. Tony's ready
room and Marshall's walls decide the finale; the waves come to the base; the boss.

---

## 9. What FTB Quests needs from KubeJS

Stages set by the loop script and read by stage tasks: `novo_held`, `novo_defended`,
`residential_held`, `residential_defended`, `plant_held`, `plant_defended`, `fr06_held`,
`fr06_defended`, `financial_held`, `financial_defended`, `all_held`, `car_built`, `revives_3`,
`wave_1`…`wave_4`, and the function levels (`workshop_1`…`radio_3`). Rewards run commands:
`kubejs stage add`, `function gscraft:tower_stage_N`, `give` for blueprints (an IE blueprint item
with the `gscraft` category NBT). Location tasks use the site rectangles from the district map;
kill tasks use the garrison mob types In Control! spawns at each site.
