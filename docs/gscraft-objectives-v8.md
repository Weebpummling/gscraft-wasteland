# GSCraft Wasteland — Where things live on the v8 map

> **Realigned 2026-09-07 — §0 to §6 were rewritten onto the Skadowsky camp.** Authority: `docs/gscraft-skadowsky-camp.md`.


Draft 2, 2026-09-05 (draft 1 the same day; owner: O3 confirmed, O6 = the collective farm, the rest confirmed; applied to the parents). A reassessment from the map itself (the current `scratch/worlds/v8-build`, sectors final, edges
still being cleaned in the other session): where the strongpoints and every other objective should live, given a map
that is nothing like the one the design was written on. Render: `docs/renders/v8_geography.png` (roads cream, water
blue, built magenta, sectors yellow, farmsteads orange, the camp red with 1 / 2 / 3 km rings). Distances "by road" were
measured on the road network as it stands today (`incoming/census/v8_routes.json`): the pack's roads plus the
transplants' own, **without** the thirteen step-8 connectors or the camp's gate road, so they are the ceiling, not the
floor. This was a proposal; §7's decisions were all taken, and the camp move of 2026-09-07 replaced its geography
wholesale, so §0 to §6 were realigned onto the Skadowsky camp on that date - see the banner above. The render itself
still draws the plateau camp and its rings and has not been redrawn.

## 0. The map in three lands

The v8 cell is 5.1 × 4.6 km with the Pripyat pack as its spine, and it reads as three lands divided by water:

| Land | What is there | How it is reached |
|---|---|---|
| **The home bank** (east of the river: the Skadowsky sector, and the bank running south from it) | **Skadowsky** itself — the camp in the pocket east of the south-west bridge, the **hospital** 0.34 km due north, the station, the rail yard and the level crossing; then south down the bank the rail line and road to the pack's **plant complex** (the switchyard and admin block, the turbine hall, the cooling intake works, the confinement hall) | on foot from minute one; the plant's outer works by the road and rail south, its inner works across the marsh channels |
| **The river line** (the home bank's west edge) | the **south-west bridge**, x −1104…−981, deck z −957…−936 at y 89 over water at y 53 — the camp's west gate and the only crossing on Skadowsky's west side | the bridge, and nothing else on this side |
| **The far bank** (west of the river) | the **town** (1.85 × 2.25 km of nine-storey blocks, avenues, the stadium, the palace of culture); the **collective farm** at (−2112, −896) and the **Woods** (fields and forest with the farmsteads) south of the town; the **KROT** further west | over the bridge, with a vehicle: the farm 1.17 km, the town's east avenue 1.52 km, the compound 2.30 km |
| **The district** (a fourth pocket, south-west under the ridge) | the cyberpunk district: **Novo**, **Financial Plaza**, **Bio Gen**, the **hub** city walled inside it; the **KROT** on its north edge | **deferred to a later quest line** — no quest points into the district; KROT on its north edge is the one piece still in scope |

The camp itself: the river and its single bridge to the west, the rail embankment and its level crossing to the east,
the mast and its field inside the perimeter, and the rest of Skadowsky — the town the players are squatting in — north.
The first ruins are the sector's own buildings, not scattered wrecks. Every counterattack therefore comes over the
bridge from the west, up the main road east, or along the rail corridor north and south.

### Distances from the camp square (−940, −979)

Straight-line figures are measured from the world spawn at the paved junction. The road network was never re-measured
from this camp — every "by road" and travel-time figure in draft 2 was taken from the dead plateau, so they are open.

| Objective | Straight | By road today | Walk / car (design §2.5) | Note |
|---|---|---|---|---|
| the hospital | 0.34 km | [needs measurement] | [needs measurement] | the first walk, due north inside the sector |
| the plant switchyard | 1.09 km | [needs measurement] | [needs measurement] | same bank, no water crossed |
| the collective farm | 1.17 km | [needs measurement] | [needs measurement] | the Line's west end, over the bridge |
| the town's east avenue | 1.52 km | [needs measurement] | [needs measurement] | over the bridge |
| the confinement hall | 1.53 km | [needs measurement] | [needs measurement] | Act IV's prize; same bank |
| the plant turbine hall | 2.06 km | [needs measurement] | [needs measurement] | inside the plant complex |
| the plant intake works | 2.16 km | [needs measurement] | [needs measurement] | inside the plant complex |
| KROT | 2.30 km | [needs measurement] | [needs measurement] | over the bridge, the district's north edge |
| the town centre (the central square, −2380, −2975) | 2.46 km | [needs measurement] | [needs measurement] | over the bridge |
| the runway | 2.85 km | [needs measurement] | [needs measurement] | deferred to a later quest line |
| the library | 3.16 km | [needs measurement] | [needs measurement] | deferred to a later quest line |
| Novo | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| Financial Plaza | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| Bio Gen | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| the hub | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| the industrial district (the waterworks) | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| the mega-base (FR-06) | [needs measurement] | [needs measurement] | [needs measurement] | deferred to a later quest line |
| the plant complex (nearest gate) | [needs measurement] | [needs measurement] | [needs measurement] | its three sites are listed above; the map's largest ruin |
| the Woods (nearest point) | [needs measurement] | [needs measurement] | [needs measurement] | over the bridge, south of the town |
| Skadowsky | — | — | — | home: the camp is inside it |
| the settlement | — | — | — | gone: its sector is group `removed` and the ground there is 91 % grass |

Within the plant complex: switchyard → turbine hall 1.31 km, turbine hall → intake works 0.66 km, switchyard → intake
works 1.71 km.

## 1. Objectives by act

| Act | Land | Objectives | Strongpoint taken | What the act is about |
|---|---|---|---|---|
| **I — The town you woke in** | the pocket, then the sector; foot | the buildings around the camp square (the introductions), **Skadowsky** itself scouted, looted, held and defended — the rungs pay perimeter, not a keeper — and north 0.34 km to the **hospital** (J1's first walk, W3's scrap) | **the Skadowsky hospital** | learning the loop inside your own town; the first counterattack, the lightest, fought at the bridge |
| **II — Over the bridge, and down the bank** | west over the bridge; the east bank south; car | **the Line** west over the bridge to the collective farm (1.17 km), the town's landmarks (the re-targeted structure quests: the palace of culture, the tallest block, the central square, the stadium), the **KROT**; south down the east bank, the rail line and road to the plant's outer works. The runway and the library, which draft 2 put here, are deferred to a later quest line | **KROT** | the first car (the town at 1.52–2.46 km is a car's range, not a walk); the first gun (G1–G4) cast, bored and fired in the camp |
| **III — The plant complex** | the home bank south, truck and the marsh channels | the plant proper: the **switchyard and admin block** (1.09 km), the **turbine hall** (2.06 km), the **cooling intake works** (2.16 km); the plant's four storage halls at (−888, 167), (−743, 167), (−890, 54) and (−775, 54); the rail line as the bank's spine (James's J-T1–3). The waterworks and FR-06, which draft 2 put here, are deferred to a later quest line | **the switchyard**, then **the turbine hall**, then **the intake works** | one industrial landscape, its three sites 0.66 to 1.71 km apart from each other; the truck and the marsh channels are the gate |
| **IV — The reactor, and the far bank** | the confinement hall; the bridge west; air | **the confinement hall** (−642, 518, roof y 198): the reactor control module for the gatehouse tier 3 and the antenna array for tower stage 5, 1.53 km away on the camp's own bank, reached by road or by helicopter from the mast field inside the perimeter; then the bridge road west. The hub, with the rest of the district, is deferred to a later quest line | — | the tower's last parts; the beacon; the finale on the mast's field |

The order inside the acts follows the land: Act I is a walk north inside the sector; Act II crosses the one bridge west
and runs south down the east bank; Act III works the plant complex outward from the switchyard; Act IV's prize sits on
the home bank, so the bridge road serves it and the helicopter is a shortcut rather than the only way in.

## 2. The five strongpoints

| Role (design §2.3) | Camp NPC | Site | Keeper | Centre | From camp | Act | Why this site |
|---|---|---|---|---|---|---|---|
| Medical — the hospital | Tony | **the Skadowsky hospital** (x −865…−698 × z −1312…−1242, roof y 115, ground y 64) | Vera | −782, −1277 | 0.34 km | I | inside the home sector but not the camp: it holds 372 of the sector's 425 white stained glass blocks and 935 of its 1,785 bone blocks — the morgue and the mass grave of a quarantine that failed. Act I is a walk north through your own town to the building at the end of it; it is the second revive point |
| Electronics | Tune | **the plant's switchyard and admin block** | Ilya | −815, 105 | 1.09 km | III | relays and transformers, so the transmitter comes off the site that is thematically exact; the nearest of the three plant sites |
| Power | Michael | **the plant's turbine hall** | Rook | 400, 590 | 2.06 km | III | the generators themselves; 1.31 km deeper into the plant than the switchyard |
| Fuel and water | Michael | **the plant's cooling intake works** | Oksana | 895, 155 | 2.16 km | III | cooling water; the marsh channels are its gate, and the truck is the only way in with a bulky item |
| Heavy industry | Walker | **KROT** (x −3392…−3073 × z −1344…−1025) | Kessler | −3233, −1185 | 2.30 km | II | the one walled holdout across the river; the far end of Act II's drive west, and the only strongpoint that crosses the bridge |

**Skadowsky is the home sector, not a strongpoint.** It is the starting zone and becomes the camp by being cleared, so
it is never "the residential block", never a distant objective across a river; the `residential_*` stages are renamed
`hospital_*` to stop the sector and the strongpoint sharing a name. The **confinement hall** (−642, 518, roof y 198) is
not a strongpoint either: it is Act IV's prize, the reactor control module and the antenna array, which keeps the map's
largest ruin as the finale's source rather than one more take.

Draft 2's other four sites are deferred, not rejected: **Novo Expograd Industrial Zone** (heavy industry), **Financial
Plaza and the sewers** (electronics), **the industrial district, "the waterworks"** (fuel and water) and **the mega-base,
FR-06** (power) all sit outside the routing rule and wait with the rest of the district for a later quest line, along
with the hub, the runway and the library. The settlement, once floated as a first strongpoint, is gone from the map.

## 3. The loot sites and the ruin field

| Site | Act | Role (loot doc §5) | Where it sits |
|---|---|---|---|
| **the Skadowsky sector** | I | the first loot field: the buildings around the camp square, the streets north, the station, the rail yard and the level crossing. The introductions' hand-ins come out of them — `camp_ruins.py`, its 24 wrecks and the four `ruins/*` tables are retired, because a 464 × 752 town with a hospital, a station and a level crossing has plenty to loot without inventing wrecks | around the camp, from the square outward |
| the hospital | I | the medical strongpoint's own loot: the morgue and the mass grave (372 white stained glass blocks, 935 bone blocks) | 0.34 km due north of the camp square |
| the settlement | — | W3's scrap and J1's first walk move to the sector and the hospital | **gone**: its sector is group `removed` and the ground there is 91 % grass |
| **the town** | II | the ruin field: every "generated structure" quest re-targeted here (design §2.7); the palace of culture (U-A1's cellar, the broad civic block at (−2650, −2889)), the tallest block (W-A6's roof boss — any of the 4,044 columns at y 118 or above), the central square (J-C1, the park with the radiating avenues at (−2380, −2975)), the four microdistricts (J9) at (−2088, −1967), (−1937, −2184), (−2337, −1791) and (−2350, −2289), the stadium (−2395, −3482), the swimming pool (the prismarine hall's role), the hotel (the glass tower's), the bus depot (the stone complex's: W-A5, H3). The stone complex that held the gunpowder is gone from the v8 map: gunpowder now comes from the town's military chests and the plant complex's four storage halls | west over the bridge, 1.52 km to the east avenue, 2.46 km to the centre |
| the runway, the library | — | the library's folders (J5) wait with it. The aircraft no longer needs the runway: it is rotary and lifts from the mast field inside the camp perimeter, and `runway_lights` and the pad are retired with `camp_ruins` | **deferred to a later quest line**; 2.85 km and 3.16 km from the camp square |
| KROT | II | a walled survivor holdout: medical, hardware, the first seeds (loot §5); Walker's heavy-industry strongpoint | west over the bridge, 2.30 km, the district's north edge |
| **the collective farm** | II | the pack's fields south of the town (x −2700…−1900, z −1350…−700) with the farmstead at (−2112, −896) as its yard: the farm role (D3's seeds and bowls, D5's crops) — the world scan found no farmland in the pack, only the town's composters, so the fields are the farm and the dressing pass plants them. It is now the Line's destination, L6's switching station becoming its own substation | west over the bridge, 1.17 km: the Line's west end |
| Bio Gen | — | T7's surgical kit and the medical analyzers wait with it | **deferred to a later quest line**, the district's east strip |
| the sewers | — | U6's kill task and the encrypted radio wait with Financial Plaza | **deferred to a later quest line**, under the plaza |
| the rail yard | I–II | the train (Create track, the depot, the schedule block); a loot stop inside the home sector, and the head of the east-bank spine south | in the Skadowsky sector, on the rail corridor east of the camp; the level crossing is the camp's east gate |
| the Woods and the 29 farmsteads | II–IV | Teddy, the bunkers, the fog house, the outpost (design §2.7); a farmstead every 150 m on every road | west over the bridge, south of the town, and everywhere |
| **the hub** | — | the hub items (phased array element, satellite receiver), the Custodian and the mechs wait with it; tower stage 5's array now comes from the confinement hall | **deferred to a later quest line**, walled in the district |
| **the plant complex** | III–IV | the switchyard, the turbine hall, the intake works, the four storage halls at (−888, 167), (−743, 167), (−890, 54) and (−775, 54) (gunpowder), the transformer core's second source, U-D3's bunker, the power filters (loot §6), the cooling pond; and the confinement hall, Act IV's prize: the reactor control module and the antenna array | the south-east, on Skadowsky's own bank — no water crossed: the switchyard 1.09 km, the confinement hall 1.53 km, the turbine hall 2.06 km, the intake works 2.16 km |

## 4. The tower's parts, by site

| Stage | Part | Component | From |
|---|---|---|---|
| 1 | Mast | the Mast section kit (quest X2 unchanged) | **Skadowsky** — the mast at (−808, −1008) already stands; stage 1 repairs the cut lattice section so it can be climbed, rather than erecting a mast to 64 |
| 2 | Cooling | purification membrane | the plant's cooling intake works |
| 3 | Generator | the generator kit | the plant's turbine hall |
| 4 | Transmitter | military circuit board | the plant's switchyard and admin block |
| 5 | Array | phased array element, satellite receiver | the confinement hall |
| — | the gatehouse tier 3 (not a tower stage) | reactor control module | **the confinement hall** (−642, 518, roof y 198) |

The parts follow the strongpoint order: the mast repair from Skadowsky, the transmitter from the switchyard, the
generator from the turbine hall, the cooling loop from the intake works, the array from the confinement hall. Stages 2
to 5 are unchanged in count, gating and reward — only stage 1's fiction changes, because a dead mast still needs
everything the other four stages add. The stage numbers and that site order do not run in step, which costs nothing:
the three plant sites are all Act III and can be taken in any order.

Both of Act IV's inputs, the array and the reactor control module, come out of the confinement hall rather than a base
on the lake. That keeps the map's largest ruin as the finale's source and gives the plant complex a reason to exist
beyond a bunker.

## 5. The crossings and roads the objectives need (for the map session)

| # | What | Where | Serves |
|---|---|---|---|
| C1 | **The Line's crossing is the south-west bridge.** The Line runs west over it to the collective farm at (−2112, −896), 1.17 km; its old ford between the settlement and Skadowsky is dead at both ends and its old destination is gone | the bridge: x −1104…−981, deck z −957…−936 at y 89, water at y 53 | Act II |
| C2 | the camp's gates: the bridge is the west gate, with Marshall's gatehouse at its east end (x −978…−955 × z −955…−940); the rail embankment's level crossing is the east gate; the paved junction at (−940, −979) is the road they meet on | the pocket | everything |
| C3 | the road and rail south down the east bank to the plant's outer works | the home bank, south | Acts II and III |
| C4 | the north road: the camp square → the hospital, 0.34 km, the first walk out and entirely inside the sector. (This was the road to the runway and the library; both are deferred to a later quest line and their connectors wait with them) | north, inside Skadowsky | Act I |
| C5 | the district road: the bridge → the town's south road → KROT. Novo, Bio Gen, the plaza and the hub are deferred to a later quest line, so only the compound's leg is needed now; the plaza still has **no road at all** | west over the bridge, then south-west | Act II |
| C6 | the east-bank spine: the sector's rail yard south down the bank into the plant complex. The viaduct road to the waterworks, FR-06 and the lake road are deferred with the district | the home bank, south | Acts II and III |
| C7 | boat landings wait with FR-06 in the deferred quest line. Nothing on the critical path needs a boat: a straight line from the camp to the confinement hall crosses no water, and Act III's water is the plant's marsh channels | the plant's marsh | Act III |
| C8 | the plant complex's west gate road from the highway | south-east | Acts III and IV |

## 6. What this does to the systems

- **Difficulty by land, not by ring.** The sites now run from 0.34 km (the hospital) to 2.30 km (the hempcrete
  compound), but that spread still cannot carry four acts: three of the five strongpoints sit inside the plant complex
  between 1.09 and 2.16 km, and Act IV's confinement hall at 1.53 km is nearer than two Act III sites. So Improved
  Mobs' distance rings cannot separate the acts. Difficulty follows the land: the home sector light, the east bank
  south and the far bank over the bridge medium, the plant complex hard, the confinement hall hardest — In Control
  `areas.json` per land (mod audit win 3), with Improved Mobs' distance curve flattened to two steps (inside 1.5 km,
  beyond).
- **The counterattacks' entry points** are the bridge from the west, the main road east, and the rail corridor north
  and south; the wave's origin tells the players which approach is live before the board does. All three are inside
  the camp perimeter's own ground, so the fight is at the gate rather than out in the fields.
- **Vehicles earn their place:** the car for Act II (the bridge, the farm at 1.17 km, the town at 1.52–2.46 km — a
  car's range, not a walk), the truck for Act III (the plant's outer works and the marsh channels, and the only way
  home with a bulky item), the helicopter for Act IV. The aircraft is rotary and lifts from the mast field inside the
  camp perimeter, so no airfield is needed and `runway_lights` and the runway pad are retired; the boat waits with
  FR-06 in the deferred quest line. Design §2.5's travel table stands; the routes above are what it prices.
- **The train** is the home bank's spine, not fast travel: the sector's rail yard south down the east bank into the
  plant complex, hauling the bulk (steel, boiler parts, the reactor module) back to the camp.

## 7. What changes in the documents, and the owner's decisions

Applied 2026-09-05 (owner's rulings: O3 and O6 as marked, the rest confirmed). This table is the record of what was
decided that day and is left as it was written; where a row disagrees with §0 to §6 above, the realigned section is the
live text. O1's act names, O2's camp wrecks, O3's FR-06 generator, O5's Act III order and O8's boat landings were all
overtaken by the camp move of 2026-09-07.

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
