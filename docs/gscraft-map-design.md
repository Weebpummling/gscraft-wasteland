# GSCraft Wasteland — Map and Systems Design

Draft 5, 2026-09-03. **This is the version the world build and the first tests are made from.**
One build, one border; everything with a plan behind it is in it; seasons stay a future idea.

**Decision log (owner):** draft 3 — strongpoints are player-built structures, radio tower custom;
medical at the residential block, Bio Gen a loot site; sewers are dungeons; water pad re-cut; air
ring expedition-only; tower second-closest; vehicle speeds as shipped; no custom mod. Draft 4 — item
catalogue, bulky rule, storage as a base function, the five tower recipes, crafting at the IE
workbench with blueprints: all accepted. Draft 5 — the contacts are **NPCs living in the starting
area, each with a building**: Walker the Foreman, Tony the Medic, Michael the Engineer, Tune the
Technician, James the Scout, and Marshall, who opens the tower questline once each of the five has had
their starting tasks done.

---

## 1. The game in one paragraph

Five players wake in a crater camp run by six survivors. Around them is a Lost Cities wasteland with a
custom-built district two kilometres east and five player-built strongpoints scattered between 1.5
and 2.5 km. Every ruin is full of small useful junk; the camp's NPCs teach the players to turn it into
parts at the workbench and to grow their own hideout. Taking a strongpoint starts a clock; holding it
means defending it when the camp's radio names it as the next target; each strongpoint yields one
complex component nothing can craft. Five of those, built into five complete parts, repair the radio
tower stage by stage until its beacon lights. That starts the countdown to the finale: waves on the
players' own base, the last one carrying the boss. Cars get the parts home; the plane reaches the one
site that holds the last component.

The loop, in order: **scavenge → craft → upgrade the hideout → take → hold → repair the tower →
defend the base**.

---

## 2. The map

> **Placement revision (v6, 2026-09-03):** the coordinates below are draft 5's first cut. The
> revised placements — the radio tower in the camp (north-east corner, locked), Novo on the spine
> 1.1 km east, the old substation pad restored, offsets and pad levels for every transplant — are
> in `gscraft-map-layout-v6.md`, which the world build uses. Where the two differ, the sheet wins.

### 2.1 Border and ranges

**10 km square, centred on (1900, 1250)**: x −3100 … 6900, z −3750 … 6250. About 390,000 chunks,
~2.4 h of Chunky, ~6 GB, pre-generated in full before the first test. Set once with
`/worldborder center 1900 1250` and `/worldborder set 10000`.

| Range | From the camp | Owned by | What lives there | Attackable? |
|---|---|---|---|---|
| **Foot** | 0 – 1.5 km | walking | the camp, glass tower, acacia hall, Novo on the old substation pad | strongpoints only |
| **Road** | 1.5 – 4 km | cars, boats | the district, the tower, Financial Plaza, the settlement, Bio Gen and the runway | strongpoints only |
| **Air** | 4.5 – 6.5 km | aircraft | the hub and generated cities kept as found; the only source of the rare loot-only parts | never |

### 2.2 The camp (starting area)

The 384×384 cleared area around the crater, x/z −176…207, with the Warium structure on its lake
island in the pit (plaza y 93, world spawn 19 94 26) and the rebuilt surface on the rim. The camp is
**neutral ground**: the NPC buildings are protected, spawns are suppressed inside the outline, and
the players' own hideout is wherever they claim. The recommended claim is the crater floor: a pit
with one ramp is the best wave-defence ground on the map, and it is where they woke up.

Six NPC buildings sit on the rim in a ring, 60–150 blocks from the crater centre, each with a yard.
Positions are first cut, to be adjusted on the visual pass against the rebuilt surface:

| NPC | Building | Footprint (blocks) | Where on the rim | What is in it |
|---|---|---|---|---|
| **Marshall** | the gatehouse | 24×16 | east gate, x 150…173 × z 0…15, where the spine leaves the camp | the map table, the tower parts rack (empty until parts arrive), the strongpoint board; players pass him on every trip east |
| **Walker the Foreman** | the yard | 40×32 | south-east, x 60…99 × z 80…111 | the Engineer's Workbench (the only one), garage bays, a vehicle lot, scrap piles |
| **Tony the Medic** | the clinic | 20×16 | north-west, x −100…−81 × z −100…−85 | beds, the med station, a PlayerRevive point |
| **Michael the Engineer** | the plant | 32×24 | south, x −40…−9 × z 100…123, at the crater edge above the lake | generator shed, water collector, tanks, the fuel pump |
| **Tune the Technician** | the radio shack | 16×16 with a 12-block mast | north-east high ground, x 60…75 × z −120…−105 | the small mast (a visible echo of the tower), the map board, the intel desk |
| **James the Scout** | the lookout | 8×8 tower, 20 tall | north-west corner, x −150…−143 × z −150…−143 | the expedition board, a view over the approach |

Each building is a structure template placed once at world build by a generator in the style of
`tools/tower.py` (a `camp.py`, to write), so the camp can be re-cut without hand building.

### 2.3 Strongpoints and sites

| # | Strongpoint (holdable) | Where | From the camp | Role | NPC |
|---|---|---|---|---|---|
| 1 | **Novo Expograd Industrial Zone** (transplant 144×160) | old substation pad 215…374 × 1415…1574 | 1.5 km S | Heavy industry | Walker |
| 2 | **Residential block** (district) | from 1328, 1376 | 1.9 km | Medical | Tony |
| 3 | **Industrial plant** (district 464×272) | 1904…2367 × 864…1135 | 2.4 km | Fuel and water | Michael |
| 4 | **FR-06 complex** (district 384×528) | 2192…2575 × 400…927 | 2.5 km E | Power and hangar | Michael |
| 5 | **Financial Plaza Quarantine** (transplant 160×144) | old hospital pad 675…866 × 2367…2558 | 2.5 km SE | Electronics | Tune |
| — | **Radio tower** (custom) | 2023…2150 × −184…−57 | 2.1 km E | Endgame | Marshall |

Loot sites, never attacked: **Bio Gen Offices** (64×256) beside the runway on the old airfield pad;
**the settlement** (272×288) on the water-treatment pad re-cut to 288×304; **the sewers** (96×96)
under Financial Plaza, later under the hospital pad and the plant; **the hub** (832×640) in the air
ring at about (6000, 1500), James's territory; the library, hempcrete compound, stone complex (a
spawner dungeon) and the small district builds. If a transplant fails its remap, the hempcrete
compound takes its role.

### 2.4 Roads and water

1. **Spine:** Marshall's gate → district west edge (900 m), on the old rail causeways where they help.
2. **Strongpoint roads:** district → Novo; district → the tower.
3. **Causeways** at every water crossing; if the one to Novo is longer than the pad is wide, Novo
   lands on dry ground instead.
4. Nothing beyond the road ring. The crater ramp must take a car; if it cannot, Walker's yard gets
   the garage and the crater stays foot-only.

### 2.5 Travel (vehicles at their shipped speeds)

| Distance | Walk | Sprint | Boat | Car street | Car rubble | Aircraft |
|---|---|---|---|---|---|---|
| 1 km | 3.9 | 3.0 | 2.1 | 0.8 | 2.1 | 0.3 |
| 2 km | 7.7 | 5.9 | 4.2 | 1.7 | 4.2 | 0.6 |
| 4 km | 15.4 | 11.9 | 8.3 | 3.3 | 8.3 | 1.2 |
| 6 km | 23.1 | 17.9 | 12.5 | 5.0 | 12.5 | 1.8 |

Minutes one way; a Minecraft day is 20 real minutes.

---

## 3. The NPCs

**Implementation.** Named villager entities with no AI, invulnerable, persistent and silent, placed by
a datapack function (`gscraft:camp_npcs`) so they can be respawned in one command. A KubeJS
entity-interact handler makes right-click open the quest book and print the NPC's line; each NPC's
chapter is tagged with their name. Villager skins give each a look (Tony a cleric, Walker a
toolsmith, Michael an armorer, Tune a librarian, James a fletcher, Marshall a nitwit in a helmet is
the joke, or a cartographer if not). The Recruits mod in the pack stays for hireable guards later;
it is not used for these six. No mod is added.

**Who unlocks what.** The full chains, 77 quests across the six chapters, scaled by act and distance, are in `gscraft-quests.md`; the trip table in §3.5 shows which of them one outing clears.

| NPC | Owns | Starting tasks (the introduction) | Unlocks when done | Their chain |
|---|---|---|---|---|
| Walker the Foreman | Workshop, Garage, Storage | bring 8 bolts, 8 nuts, a wrench | fastener-kit and steel-frame blueprints; the basic backpack | take and hold Novo; motor assembly; vehicles; the mast section kit |
| Tony the Medic | Medical | bring 4 bandages, 2 painkillers | med-kit blueprint | hold the residential block; revive a teammate; medical analyzer; finale readiness |
| Michael the Engineer | Generator, Water | bring 3 wire spools, a power cord, a water filter | wiring-harness and filter blueprints | hold the plant; coolant; hold FR-06; the cooling loop, then the generator kit |
| Tune the Technician | Radio / intel | bring a circuit board, 2 capacitors, a broken radio | circuit-assembly blueprint; the map | hold Financial Plaza; antenna elements; the transmitter, then the antenna array |
| James the Scout | expeditions | visit the glass tower, the acacia hall and the library | waypoints; the expedition board | the settlement by car; the hub by air; the phased array element |
| Marshall | the strongpoint loop and the tower | **none: he talks once all five introductions are done** | the tower chapter and the strongpoint board | take → hold → defend; five parts in order; the beacon; the finale |

---

## 3.5 Trips: what each area clears at once

The quest chapters are written against the same areas, so one outing closes quests for several
NPCs at once. Quest ids are from `gscraft-quests.md`. "Haul" is the number of slots the trip's
hand-ins need if everything is found, and bulky items take a hand or a vehicle seat each; neither is
a limit. A trip that does not fit is simply two trips: the sites stay where they are and a held
site's component containers respawn on the loop's cycle, so nothing is lost by coming back.

| Trip | Act | Area (from the camp) | Quests it serves | Haul (slots) | Bulky | Get there |
|---|---|---|---|---|---|---|
| 1 | I | the camp's own ruins (0–300 m) | W1, T1, M1, U1 hand-ins; D1 concrete later | 11 | — | foot |
| 2 | I | glass tower + acacia hall (1.3–1.55 km) | J1 locations; W3 metal scrap; M2 light bulb; T2 med items | 6 | — | foot |
| 3 | I | Novo (1.5 km S) | W5 reach and kill, R2 claim; hardware and spark plugs for W7; after the hold: W11 heavy anchor cable, W9 heavy diesel engine | 8 | 2 (after the hold) | foot; the bulky parts one per carrier, or the first car |
| 4 | II | the west edge: residential block, hempcrete compound, library, the tower ruin (1.9–2.5 km) | T3 blood bags, T4 kill, R3 claim; J2 locations; U3 hard drive, J3 folders; electrical items for U2 and U8; X1 briefing | 14 | — | foot, then the first car |
| 5 | II | the industrial plant (2.4 km) | M4 reach and kill, R4 claim; hoses, tubes and fins for M3 and M6; fuel cans for M7 and W8; after the hold: M6 industrial pump | 9 | 1 | car |
| 6 | III | FR-06 (2.5 km E), with the factory annex and hopper array on the way | M8 reach and kill, R5; electrical items; after the hold: M10 transformer core, M11 avionics module and reactor control module | 10 | 3 | car |
| 7 | III | Financial Plaza and the sewers under it (2.5 km SE) | U4 reach and kill, R5; U6 sewers and encrypted radio; electrical and valuables; after the hold: U7 military circuit board; D4 concrete | 12 | 1 | car |
| 8 | III | the far ring by road: stone complex, mud village, the settlement, Bio Gen, the runway (2.8–3.9 km) | J4 locations, J5 valuables, W12 pressure gauge, T7 surgical kit, J6 hard drive; W10 second anchor cable on the way back past Novo; M12 membrane at the plant | 9 | 3 | truck, or boat to the settlement |
| 9 | IV | the hub (6.2 km E) and the four generated cities | J7, J9 locations; J8 phased array element and satellite receiver; T9 and M13 military power filters | 6 | 4 | aircraft |
| 10 | II–IV | home: the gatehouse and the claim | X2–X6 hand-ins, T10 ready room, D1–D4, R6 | — | the five complete parts, one at a time | — |

What the table fixes is the pairing: which NPCs' quests point at the same place in the same act, so
the group decides together where to go next and everyone has a reason to be there. How many trips
it takes is the players' business.

---

## 4. Items, crafting and space

### 4.1 Three tiers, one rule

| Tier | How you get it | Stack |
|---|---|---|
| **Small items** (~30, §4.2) | loot only, everywhere, by building type | 4–8, tools and valuables 1 |
| **Intermediates** | crafted at Walker's Engineer's Workbench from blueprints the NPCs hand out per base-function level | 4 |
| **Complete parts** | intermediates **plus one loot-only component** | 1, bulky |
| **Loot-only components** | at the strongpoint that owns the role, or the hub; no recipe exists | 1, bulky |

**Nothing complete is ever loot; nothing complex is ever crafted.** Every complete part needs a
crafting chain and a trip.

### 4.2 Small items

| Category | Items | Drop mostly in | Stack |
|---|---|---|---|
| Hardware | bolts, nuts, screws, nails, metal scrap, duct tape, insulating tape | garages, workshops, factories, Novo, the plant | 8 |
| Electrical | wire spool, power cord, light bulb, capacitor, relay, circuit board, electric motor, car battery | offices, Financial Plaza, FR-06 decks, the library | 4 (motor, battery 1) |
| Mechanical | corrugated hose, silicone tube, radiator fin, pressure gauge, spark plug | the plant, garages, Novo, the sewers | 4 |
| Filters and chemicals | water filter, gas-mask filter, bleach, antifreeze, motor oil, solvent | stores, the plant, apartments, Bio Gen | 4 |
| Medical | bandage, painkillers, syringe, antiseptic, blood bag | apartments, the residential block, Bio Gen | 4 |
| Tools | wrench, pliers, screwdriver set, hand drill, welding torch | garages, Novo, FR-06 hangar | 1 |
| Valuables | broken radio, computer parts, hard drive, folder of documents | offices, Financial Plaza, the hub | 1 |

### 4.3 Intermediates (blueprints at the IE Engineer's Workbench, `gscraft` category)

| Intermediate | Recipe | Blueprint from |
|---|---|---|
| Fastener kit | 4 bolts + 4 nuts + 4 screws + 4 nails | Walker, Workshop 1 |
| Steel frame | 6 metal scrap + 1 fastener kit, welding torch held | Walker, Workshop 1 |
| Toolbox | wrench + pliers + screwdriver set + hand drill | Walker, Workshop 1 |
| Motor assembly | 1 electric motor + 1 spark plug + 1 wiring harness | Walker, Garage 1 |
| Wiring harness | 3 wire spool + 1 power cord + 1 duct tape | Michael, Generator 1 |
| Filter cartridge | 1 water filter + 1 corrugated hose + 1 bleach | Michael, Water 1 |
| Coolant | 2 antifreeze + 1 water bucket | Michael, Water 1 |
| Sealed tubing | 1 silicone tube + 2 insulating tape | Michael, Water 1 |
| Circuit assembly | 1 circuit board + 2 capacitor + 1 relay + 1 wire spool | Tune, Radio 1 |
| Antenna element | 2 metal scrap + 1 wire spool + 1 insulating tape | Tune, Radio 2 |
| Med kit | 2 bandage + 1 painkillers + 1 antiseptic + 1 syringe | Tony, Medical 1 |

### 4.4 Complete parts and loot-only components

| Stage | Complete part | Intermediates | Loot-only component | Found at | Needs |
|---|---|---|---|---|---|
| 1 | Mast section kit | 6 steel frame + 2 fastener kit | Heavy anchor cable | Novo | Workshop 2 |
| 2 | Cooling loop | 2 filter cartridge + 2 coolant + 2 sealed tubing | Industrial pump | the plant | Water 2 |
| 3 | Generator kit | 2 wiring harness + 1 motor assembly | Transformer core | FR-06 reactor plaza | Generator 2 |
| 4 | Transmitter | 2 circuit assembly + 1 wiring harness | Military circuit board | Financial Plaza | Radio 2 |
| 5 | Antenna array | 4 antenna element + 1 circuit assembly | Phased array element | the hub only | Radio 3 |

Other loot-only components, first cut: heavy diesel engine (Novo); purification membrane (the
plant); reactor control module, avionics module (FR-06); encrypted radio (Financial Plaza); medical
analyzer, surgical kit (residential block, Bio Gen); satellite receiver, military power filter (the
hub). They spawn in specific containers at their site, one or two per visit, and respawn on the
loop's cycle, so a held strongpoint keeps producing. Base upgrade kits have the same shape: a kit of
intermediates, from level 2 one component from the role's strongpoint, at level 3 one from the hub.

### 4.5 Space

36 slots and an offhand; a fighting kit takes 10–12; the rest is the loot budget, and a complete
part's shopping list is 6–10 different items, so the budget is spent on **variety**.

- Small items stack 4–8; intermediates 4; complete parts and components **stack 1 and are bulky**:
  no backpack, Slowness and no sprint while carried (KubeJS item + player tick; backpack exclusion
  through the backpack mod's config if it has one, else a KubeJS insert check).
- Death drops everything except the secure pack (keepInventory off; PlayerRevive makes it rare).
- **Storage is Walker's function**, on Sophisticated Backpacks in the Curios slot:

| Storage | Unlocks | Carried |
|---|---|---|
| 1 | basic backpack; the stash crates at the claim | +27 |
| 2 | iron backpack; stack upgrade ×2; a car with a cargo crate | +54, +27–54 in the car |
| 3 | gold backpack; **everlasting upgrade** (survives death: the secure container); truck cargo | +81, +108 in the truck |
| 4 | diamond backpack; aircraft cargo | +108 |

Bulky items ride in vehicle cargo or in hand. The garage is how tower parts get home.

---

## 5. The hideout

The players' claim (FTB Chunks, one team). Functions: Workshop, Garage, Storage (Walker);
Generator, Water (Michael); Medical (Tony); Radio / intel (Tune); Walls and defences, Farm and
kitchen (Marshall's chapter). Three levels each: level 1 from small items and intermediates, level 2
needs the role's strongpoint held and one of its components, level 3 needs one component from the
hub. Each level is a quest in the owning NPC's chapter; the reward flips a KubeJS stage that gates
recipes, hands out the next blueprint, and applies the effect (guard villagers, warning length,
vehicle recipes). Level 3 of every function requires holding ground, a plane and an expedition: the
whole map, used once.

---

## 6. The strongpoint loop and the timers

Marshall's chapter. Taking a strongpoint (clearing its garrison and placing the claim marker) sets
its held flag and starts the fortify clock. Each cycle the loop draws one held strongpoint, Marshall
and the radio name it, the warning runs, the attack comes. Lose it or die there and the flag clears
and the garrison respawns; win and it stays held and its components keep respawning. The tower's
five components come from five different held sites, so the loop is the tower's supply line.

| Timer | Value |
|---|---|
| Fortify clock after taking a strongpoint | 2 in-game days (40 min) |
| Attack warning | max(10 min, foot travel time camp → target); 12–15 min for the far ones |
| Attack cycle | every 5 in-game days |
| Hordes | folded into the loop, or left at 10 days as background |
| Finale countdown after the beacon lights | 3 in-game days (60 min) |

---

## 7. The radio tower

Six sparse structure templates in the datapack (`gscraft:tower_stage_0…5`, `tools/tower.py`, render
`docs/renders/radio_tower_stages.png`), origin (2066, 64, −141). Stage 0 is placed at world build;
each hand-in to Marshall runs the next stage's function.

| Stage | Hand in | Appears |
|---|---|---|
| 0 | — | ruined plinth, three leg stubs, wrecked hall, broken fence, rubble |
| 1 | Mast section kit | lattice mast to 64, braces, platforms, four guy anchors with chain wires |
| 2 | Cooling loop | two coolant tanks, pipe run, radiator bank |
| 3 | Generator kit | generator shed, relays up the mast, aviation lights and floodlights on |
| 4 | Transmitter | hall repaired and fitted out, dish on the roof |
| 5 | Antenna array | iron cap, spire, dipoles, and the **beacon** whose beam starts the countdown |

---

## 8. Tech stack (no custom mod)

KubeJS (items, blueprint recipes, stages, the loop, the bulky rule, NPC interaction), FTB Quests
(chapters, tasks, rewards), FTB Chunks and Teams (claim, per-team state), Immersive Engineering (the
workbench and blueprints), Sophisticated Backpacks and Curios (storage), In Control! and Hordes
(waves), Lootr (instanced loot), datapacks (loot tables, tower and camp templates, NPC summons). All
of it edits live on the server without a client reinstall.

---

## 9. Build order, and the tests it unblocks

Each phase ends in a test with a pass condition; nothing in a later phase starts until the earlier
test passes.

**Phase A — Visual pass on the v5 world (now).** Local server, `start-visual.bat`, five players or
one. Fly the camp rim and mark the six building sites on the rebuilt surface; drive out of the
crater; walk the spine line and note every water crossing; check each landing pad's fit; look at the
generated cities between the camp and the district. *Pass:* a marked-up list of terrain fixes and
final building positions.

**Phase B — World build v6 (offline, on the pristine set + v5 edits, then uploaded).**
1. Border set; water pad re-cut to 288×304; four pads' outlines left for the transplants to overwrite.
2. Roads and causeways from the Phase A list (`terrain.py`, `runpass.py`).
3. Camp buildings (`camp.py`, to write) and tower stage 0 placed; the NPC summon function.
4. Transplants as the remap allows, in this order: the settlement, Novo, Financial Plaza, Bio Gen,
   the sewers, the hub (`anvil112.py` writer, `remap112.json`, `transplant.py`).
5. Chunky the full box; pull the region set as the new pristine; regenerate the district map page.
*Pass:* boot with the benign-12 error set; every site reachable on foot or by road in a second
visual pass.

**Phase C — Systems v1.** KubeJS items (small, intermediate, complete, components; stack sizes;
bulky rule), IE blueprint recipes, datapack loot tables by building type and site, NPC interaction,
the five introduction chapters and Walker's storage levels. *Test 2, five players, foot range only:*
find items, craft at the workbench, reach Storage 1 and Workshop 1, and get Marshall to talk.

**Phase D — The loop and vehicles.** Held flags, fortify clock, warnings, attacks, garrison respawn,
component respawn; the garage tier and fuel chain. *Test 3:* take Novo, hold it through one attack,
bring a heavy anchor cable home in a car, build the mast section kit.

**Phase E — The tower, the air ring and the finale.** Stages 1–5 wired to Marshall's chapter; the
hub's rare loot; aircraft; the beacon countdown and the base waves. *Test 4:* the beacon lights and
the finale runs to the boss.

---

## 10. Open items (small)

- Exact rim positions of the six buildings: after Phase A.
- The full base-upgrade recipe sheet: written with Phase C, in the shape fixed in §4.4.
- Whether the crater ramp takes a car: Phase A; the fallback is written in §2.4.
- Recruits-mod guards as a Marshall "Walls and defences" level: later, not this build's first tests.

Related: `gscraft-quests.md` (every quest and task), `wasteland-server-blueprint.html` (the original design record),
`notes/gscraft-scale-and-travel.md`, `notes/gscraft-foreign-worlds.md`, `wasteland-district-map.html`,
`build/tower_parts.json`.
