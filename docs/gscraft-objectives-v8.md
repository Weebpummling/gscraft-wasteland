# GSCraft Wasteland — Where things live on the v8 map

Draft 2, 2026-09-05 (draft 1 the same day; owner: O3 confirmed, O6 = the collective farm, the rest confirmed; applied to the parents). A reassessment from the map itself (the current `scratch/worlds/v8-build`, sectors final, edges
still being cleaned in the other session): where the strongpoints and every other objective should live, given a map
that is nothing like the one the design was written on. Render: `docs/renders/v8_geography.png` (roads cream, water
blue, built magenta, sectors yellow, farmsteads orange, the camp red with 1 / 2 / 3 km rings). Distances "by road" were
measured on the road network as it stands today (`incoming/census/v8_routes.json`): the pack's roads plus the
transplants' own, **without** the thirteen step-8 connectors or the camp's gate road, so they are the ceiling, not the
floor. This is a proposal; §7 lists what it changes and what the owner decides.

## 0. The map in three lands

The v8 cell is 5.1 × 4.6 km with the Pripyat pack as its spine, and it reads as three lands divided by water:

| Land | What is there | How it is reached |
|---|---|---|
| **The home bank** (west of the river, north of the plant highway) | the camp on the plateau between the town's east edge and the lake; the **town** (1.85 × 2.25 km of nine-storey blocks, avenues, the stadium, the palace of culture) whose east avenue is 200 m from the camp; the **settlement** 0.5 km south; the **runway** and **library** north along the lake's west shore; the **Woods** (fields and forest with the farmsteads) south of the town | on foot from minute one |
| **The river line** (north to south, from the lake's outlet to the plant complex) | **Skadowsky** on the east bank right across the river from the settlement; the plant highway's **viaduct** over the river south of Skadowsky; the marsh and the second viaduct further south | one ford (the Line's) and the viaducts |
| **The far bank** (east of the river and the lake) | the **rail yard** on the lake's north-east shore; the **mega-base** (FR-06) on the lake's east shore; the **industrial district** south of it beside the pack's **plant complex** (the reactor block, turbine hall, cooling towers, switchyard, cooling pond) at the cell's south-east; the rail line running down the east bank from the yard past the district into the plant | by road round the lake's north (4.2 km to the mega-base) or over the viaduct and up the east bank; by boat straight across the lake (2.2 km to the mega-base); by air |
| **The district** (a fourth pocket, south-west under the ridge) | the cyberpunk district: **Novo**, **Financial Plaza**, **Bio Gen**, the **hub** city walled inside it; the **hempcrete compound** on its north edge | the town's south road, 3 km by road, 2 km straight |

The camp itself: the town on its doorstep to the west (the first ruins are the town's east blocks, not scattered
wrecks), the lake to the north and east (the tower pad on its shore), open plateau to the south and the Line's fields
beyond. Every counterattack therefore comes from the south-east fields, the town's edge or the lake road — never the
north, which is water.

### Distances from the camp gate

| Objective | Straight | By road today | Walk / car (design §2.5) | Note |
|---|---|---|---|---|
| the settlement | 0.62 km | 0.5 km | 2 min / — | the first walk |
| the town's east avenue | 0.2 km | 0.2 km | 1 min | the first ruins |
| Skadowsky | 1.40 km | 1.1 km | 4.5 min / 1 min | across the river: the Line's ford |
| the runway | 1.41 km | 2.2 km | 9 min / 2 min | north along the lake shore |
| the library | 1.68 km | 4.1 km (a loop) | — / 3 min | needs its connector to be near |
| the hempcrete compound | 1.98 km | 2.9 km | 11 min / 2.5 min | the district's north edge |
| Novo | 1.98 km | 3.1 km | 12 min / 2.5 min | the district |
| Financial Plaza | 2.37 km | (no road yet) ≈ 3.3 km | — / 3 min | the district's west end |
| Bio Gen | 1.94 km | 3.3 km | — / 3 min | the district's east strip |
| the hub | 2.42 km | 3.1 km | — / 2.5 min | walled inside the district |
| the industrial district (the waterworks) | 2.41 km | 3.7 km | — / 3 min | over the viaduct, up the east bank |
| the mega-base (FR-06) | 2.20 km | 4.2 km | — / 3.5 min by road, **2.2 km by boat** | round the lake, or across it |
| the plant complex (nearest gate) | 2.9 km | 2.3 km to its west gate, 3.5–4.3 km inside | — / 2–3.5 min | the map's largest ruin |
| the Woods (nearest point) | 0.9 km | 2.1 km by road, 0.9 km on foot | 4 min | due south |

## 1. Objectives by act

| Act | Land | Objectives | Strongpoint taken | What the act is about |
|---|---|---|---|---|
| **I — The doorstep** | the home bank, foot | the camp's ruins and the town's east blocks (introductions), the settlement (J1's first walk, W3's scrap), **the Line** south past the settlement to the river, **Skadowsky** (scout, loot, take, hold) | **Skadowsky** | learning the loop within a five-minute walk; the first counterattack, the lightest |
| **II — The town and the district** | the home bank, car | the town's landmarks (the re-targeted structure quests: the palace of culture, the tallest block, the central square, the stadium), the runway and the library (north), the hempcrete compound, then the district: **Novo** and **Financial Plaza** with Bio Gen between them, the hub seen through its wall (the Custodian) | **Novo**, then **the plaza** | the first car; two takes in one district; the first gun (G1–G4) cast, bored and fired in the camp |
| **III — The far bank** | the river line and beyond, truck and boat | the viaduct; **the waterworks** (the industrial district) and **FR-06** (the mega-base); the rail yard and the train (James's J-T1–3: the east-bank spine from the yard past the district into the plant); the lake crossing by boat | **the waterworks**, then **FR-06** | the truck and the boat both earn their keep: the boat is the short way to FR-06, the truck is the only way to the waterworks with a bulky item |
| **IV — The two far edges** | the district's heart and the plant complex; aircraft | **the hub** (the walled city: the phased array element, the satellite receiver, the Custodian) and **the plant complex** (the reactor block: the reactor control module, the switchyard's transformer core; U-D3's bunker; the cooling towers as the landmark), reached by truck through the plant's west gate or by air over the lake from the runway | — | the tower's last parts; the beacon; the finale at the camp |

The order inside the acts follows the roads: Act II's first stop is the runway (the north road, 2.2 km) or the town
(on foot), its far stop the plaza; Act III's first take is the waterworks (the viaduct road), its second FR-06 (the
boat); Act IV's two edges are opposite corners of the map, which is the point.

## 2. The five strongpoints

| Role (design §2.3) | Camp NPC | Sector | Keeper | Why this sector |
|---|---|---|---|---|
| Medical — the residential block | Tony | **Skadowsky** (464 × 752, a town with a hospital, a station and a level crossing) | Vera | the only strongpoint in walking range; a town across a river is the right first fight; its hospital is the second revive point; its station and the river make it the Line's end and the train's south terminus later |
| Heavy industry | Walker | **Novo Expograd Industrial Zone** (144 × 160) | Kessler | the foundry; small, so its assault is fast; the district's east gate |
| Electronics | Tune | **Financial Plaza + the sewers** (160 × 144) | Ilya | the fuze lab; the district's west end, so the two district takes bracket the hub |
| Fuel and water | Michael | **The industrial district — "the waterworks"** (464 × 272), beside the plant complex | Oksana | the power house and boring mill next to the real power plant; the first far-bank take, on the viaduct road; the train's yard is a road away |
| Power and hangar | Michael | **The mega-base — FR-06** (384 × 528), the lake's east shore | Rook | the steel works; reached by boat across the lake or by the rail-yard road; its hangar faces the runway across the water, which is why the aircraft's first flight is the lake |

Rejected alternatives, for the record: the hub as a strongpoint (too large to hold, and it is the Act IV prize);
the settlement as the first strongpoint (0.5 km is a loot walk, not a take); the mega-base as the fuel-and-water site
(it is on the wrong side of the lake from the waterworks' road, and its hangar is what the runway needs).

## 3. The loot sites and the ruin field

| Site | Act | Role (loot doc §5) | Where it sits |
|---|---|---|---|
| the settlement | I | the first walk's hardware, W3's scrap, J1's location | 0.5 km south, on the Line |
| **the town** | I–II | the ruin field: every "generated structure" quest re-targeted here (design §2.7); the palace of culture (U-A1's cellar), the tallest block (W-A6's roof boss), the central square (J-C1), the four microdistricts (J9), the swimming pool (the prismarine hall's role), the hotel (the glass tower's), the bus depot (the stone complex's: W-A5, H3, gunpowder) | west, from the camp's doorstep to 2.5 km |
| the runway, the library | II | the aircraft's home; the library's folders (J5) | north along the lake shore |
| the hempcrete compound | II | a walled survivor holdout: medical, hardware, the first seeds (loot §5) | the district's north edge |
| **the collective farm** | I–II | the pack's fields south of the town (x −2700…−1900, z −1350…−700) with the farmstead at (−2112, −896) as its yard: the farm role (D3's seeds and bowls, D5's crops) — the world scan found no farmland in the pack, only the town's composters, so the fields are the farm and the dressing pass plants them | between the town and the Woods, 1.5 km |
| Bio Gen | II | T7's surgical kit, medical analyzers | the district's east strip |
| the sewers | III | U6's kill task, the encrypted radio | under the plaza |
| the rail yard | III | the train (Create track, the depot, the schedule block); a loot stop on the north road | the lake's north-east shore |
| the Woods and the 29 farmsteads | I–IV | Teddy, the bunkers, the fog house, the outpost (design §2.7); a farmstead every 150 m on every road | south of the town, and everywhere |
| **the hub** | IV | the hub items (phased array element, satellite receiver), the Custodian, the mechs | walled in the district |
| **the plant complex** | IV | the reactor control module (moved here from FR-06 — §7), the transformer core's second source, U-D3's bunker, the power filters (loot §6), the switchyard, the cooling pond | the south-east corner, the map's largest ruin |

## 4. The tower's parts, by site

| Stage | Part | Component | From |
|---|---|---|---|
| 1 | Mast | heavy diesel engine | Novo |
| 2 | Cooling | purification membrane | the waterworks |
| 3 | Generator | (FR-06's) | FR-06 |
| 4 | Transmitter | military circuit board | Financial Plaza |
| 5 | Array | phased array element, satellite receiver | the hub |
| the gatehouse tier 3 | reactor control module | **the plant complex's control room** (was FR-06) |

One change: the reactor control module comes from the reactor building of the real plant, not from a base on the lake.
It gives Act IV a second edge and the plant complex a reason to exist beyond a bunker.

## 5. The crossings and roads the objectives need (for the map session)

| # | What | Where | Serves |
|---|---|---|---|
| C1 | **The Line's ford** — the carved river's rapids are the natural place | between the settlement and Skadowsky's north-west corner, on the channel from the lake's outlet | Act I |
| C2 | the camp's gate road to the lake-shore road (step 8) | Marshall's gate, east | everything |
| C3 | the Skadowsky connectors (`skad_W`, `skad_E` in the step-8 list) and the viaduct road | the plant highway | Acts I and III |
| C4 | the north road: camp → lake's west shore → the runway and the library (their connectors, `lib`'s loop is 4.1 km today) | north | Act II |
| C5 | the district road: the town's south road → the hempcrete compound → Novo → Bio Gen → the plaza (`plaza_E`, `biogen_S`, `hemp_E`, `hub_N/S`); the plaza has **no road at all** today | south-west | Acts II and IV |
| C6 | the east-bank road: the viaduct → the waterworks → FR-06 → the rail yard (`indu_N/E`, `mega_N`), and the rail-yard road round the lake's north-east | east | Act III |
| C7 | a boat landing on each side of the lake (the camp's shore, FR-06's shore) | the lake | Act III |
| C8 | the plant complex's west gate road from the highway | south-east | Act IV |

## 6. What this does to the systems

- **Difficulty by land, not by ring.** Every site but Skadowsky is 2.0–2.4 km straight from the camp, so Improved
  Mobs' distance rings cannot separate the acts. Difficulty follows the land: home bank light, the district and the
  north medium, the far bank hard, the two edges hardest — In Control `areas.json` per land (mod audit win 3), with
  Improved Mobs' distance curve flattened to two steps (inside 1.5 km, beyond).
- **The counterattacks' entry points** are the south-east fields (from Skadowsky and the waterworks), the town's
  east avenue (from the district) and the lake road (from FR-06 and the plant); the wave's origin tells the players
  which site is attacking before the board does.
- **Vehicles earn their place:** the car for the district (Act II), the truck for the viaduct and the waterworks
  (Act III, a bulky item), the boat for FR-06 across the lake (Act III), the aircraft for the plant complex over the
  lake and for the hub's roof (Act IV). Design §2.5's travel table stands; the routes above are what it prices.
- **The train** is the far bank's spine, not fast travel: the rail yard to the waterworks to the plant complex, hauling
  the far bank's bulk (steel, boiler parts, the reactor module) to the boat landing.

## 7. What changes in the documents, and the owner's decisions

Applied 2026-09-05 (owner's rulings: O3 and O6 as marked, the rest confirmed):

| # | Change | Docs | Decision |
|---|---|---|---|
| O1 | Act structure as §1 (the doorstep / the town and the district / the far bank / the two far edges) | quests §1, §8; design §2.1, §3.5; onboarding §2 | confirm |
| O2 | Act I's first ruins are the town's east blocks, not only the camp's 24 wrecks: the introductions' hand-ins list the avenue's chests | onboarding §2, loot §5 | confirm |
| O3 | the reactor control module from the plant complex; FR-06 keeps the generator | design §2.3, §4.4, §7; quests M11, R-B3, W-M2; loot §4, §6 | **decided** |
| O4 | the industrial district is "the waterworks" in every doc | all | confirm (N7) |
| O5 | Act III's order: the waterworks first (the viaduct road), FR-06 second (the boat); R5 becomes two quests again | quests §7.1 | confirm |
| O6 | the farm role goes to **the collective farm**: the pack's fields south of the town with the farmstead at (−2112, −896) as its yard (owner, 2026-09-05: something pre-existing; the scan found no farmland, so the fields are it) | loot §5, design §2.7 | **decided** |
| O7 | the rail yard is a named loot site and the train's north terminus | loot §5, create §2, quests J-T | confirm |
| O8 | boat landings on both shores; the boat quest (W-B?) moves to the start of Act III | quests §2, camp spec | confirm |
| O9 | difficulty by land (In Control areas) instead of distance rings | enemies §7, design §6.3 | confirm |
| O10 | the crossings list §5 handed to the map session | HANDOFF | confirm |
