# GSCraft Wasteland — Quests and Tasks

Draft 3, 2026-09-04 (draft 2 on 2026-09-03). Companion to `gscraft-map-design.md` (draft 6). Every quest here is buildable
in FTB Quests with the pack as it is; task types used are item hand-in, location, kill, stage flag
(set by KubeJS), advancement and checkmark; rewards are blueprints, KubeJS stages, items and
commands.

## 1. How the quests push outward

The map has four areas at increasing distance, and every chapter is written so that the **next
blueprint needs an item that only drops in the next area out**. Players are never told to go
further; they run out of things to find where they are.

| Act | Area | From the camp | What is there | How you get there | Sessions (est.) |
|---|---|---|---|---|---|
| **I — The doorstep** | the home bank, on foot | 0 – 1.5 km | camp ruins, the settlement (0.6 km SE), the runway (1.4 km N), the farmsteads around the camp, **Skadowsky — the residential block** (1.4 km SE, down the Line) | on foot | 1–2 |
| **II — The town and the district** | the home bank, by car | 1.5 – 3.3 km by road | the town's ruins (1–2.5 km W), the library (1.7), the hempcrete compound (2.0), the radio tower compound (in the camp), **Novo** (2.0 km SW) and **Financial Plaza** (2.4 km SW) in the cyberpunk district; **the Woods** (2.9 km NNE, sixteen quests across the chapters from J-W1, seven of them Teddy's) | on foot, then the first car | 3–5 |
| **III — The far bank** | the river line and beyond, truck and boat | 3.7 – 4.2 km by road, 2.2 km by boat | **FR-06** (the mega-base, 2.2 km E) and **the industrial plant** (the waterworks sector, 2.4 km ESE), reached by road over the viaduct past Skadowsky — the lake is the boat's shortcut; the sewers under the plaza | car, truck, boat | 6–9 |
| **IV — The two far edges** | the district's heart and the plant complex; aircraft | 3.1 km and 3.5–4.3 km | the hub (2.4 km SW, walled into the district, the Custodian), the pack's power-plant complex (2.9–4.3 km) | truck, aircraft over the lake | 10–12 |

Rules that hold across every chapter:

- **Introductions first.** Each NPC's first quest asks for common items from the camp's own ruins.
  Marshall does not speak until all five introductions are done.
- **One strongpoint per act boundary (v8 distances, owner default E1).** Skadowsky — the residential block — closes
  Act I; Novo and Financial Plaza are Act II; FR-06 and the plant are Act III; the hub is Act IV. The tower's parts come from Novo, the plant, FR-06, the plaza and the hub; the block feeds the clinic.
- **Every strongpoint is three quests in three chapters before it is held** (design §6.1): James's
  scout quest (reach it, bring back its dossier), the owning NPC's loot quest (hand-ins that drop
  only there, two or three trips), then Marshall's take (place the marker, win the 5-minute
  assault). The marker is refused until the first two are done. The owning NPC's hold quest
  completes when the site's counterattack is beaten at the base, which always comes at the end of the fortify clock.
- **The tower chapter opens with Marshall** (owner, 2026-09-04). When the five introductions are done Marshall speaks,
  the strongpoint board lights and the tower chapter appears in the book at the same moment; X1 is the briefing.
  The stages themselves stay gated by their parts, so the chapter is visible early and completed late. (Superseded
  text follows for the record.) Draft 2 gated it on **significant progress**:
  three strongpoints held (Novo, the block, the plant), Workshop 2, **Water 2**, Storage 2, and a
  car built. That is the end of Act II at the earliest. (Draft 1 said Generator 2, which is M9's
  reward for holding FR-06 in Act III and would have kept the chapter shut a whole act longer than
  the stage labels claim.) Stages 1–2 are Act II parts, 3–4 are Act III, 5 is Act IV, so the tower
  is repaired across the second half of the game, not at its end.
- **Every attack is a quest, and every attack comes to the base** (owner, 2026-09-04). A taken site is held by a
  friendly **site guard** the take unlocks (design §6.1); when its fortify clock runs out the site's counterattack marches on the camp
  gate, and beating it there is the owning NPC's hold quest. It is deterministic, it is fought at home, and it is the
  only attack that site will ever bring.
- **Every NPC's building climbs three tiers** (design §3.6): three `*-B` quests per chapter, each
  hand-in rebuilds their site on the same footprint and re-summons them in it. Tier 1 after the
  introduction, tier 2 after their strongpoint's counterattack has been beaten at the base (one more of its
  component), tier 3 with a hub item (the gatehouse: the plant complex's reactor control module).
- **Attacks only where the players are fighting.** A site is contested from its marker to the end
  of its counterattack at the base, and that is the only attack running; there is no random cycle, defended
  sites are safe for good, and only one site can be contested at a time. Holding all five is
  therefore the natural end of Marshall's loop (R6), not a standing burden.
- **Every kind of placed structure has a quest, and every quest lives in its NPC's chapter.** The Woods (a loot-and-quest
  region, not a sixth strongpoint: its bandit outpost is a one-off clear, R-W1) and the kept generated
  structures — the bunkers, the road-range capital, the pillager outpost, a boss tower, the nearest ancient city, a fog
  house — are quests inside the six chapters, gated like everything else; the Woods opens with James's J-W1. The kept structures of a
  kind beyond the quested ones (nine more bunkers, five capitals, five outposts, ten boss towers, three ancient cities, the
  monuments, pyramids, igloos, trail ruins, strongholds and the mansion) are expedition finds with their loot tables and no quest. The
  district's small sites (copper tower, prismarine hall, stone complex) have theirs in Tune's, Michael's and Walker's
  chapters. The Woods' In Control rule is design §6.3.
- **A quest may ask for an item only if an earlier quest has handed out its blueprint, or it is a
  loot-only component.** The capability audit that enforces this is `gscraft-crafting.md` §1; it
  closed the boat, the hand tools, firearms, armour and the marker, and broke the W13 ↔ J7 loop.
- **Hand-ins of loot-only components need no "found in raid" tag**: they have no recipe, so the item
  is the proof of the trip.

Quest counts: Walker 27 (6 armoury, 1 boat, 2 military blueprints incl. the mech, 1 Woods), Tony 14 (1 Woods), Michael 18 (1 Woods, 1 district site), Tune 19 (1 Woods, 3 bunkers, 2 sites), James 25 (5 scout, 3 Woods, 2 expedition finds, the Custodian),
Marshall 34 (loop 6, walls 3, farm 3, tower 10, gatehouse 3, Woods 2, the road outpost 1, The Line 6), Teddy 7 (explosives, §7A). One hundred and forty-four quests in the seven chapters, plus the Create chapter's ten (The Gun, §7.6), eighteen site-chain quests (§7B) and Teddy's H8 (crafting §5.8): 173; eighteen
of them the `*-B` building tiers. Which of them one outing clears is the trip table in
`gscraft-map-design.md` §3.5; how many outings it takes is up to the players.

---

## 2. Walker the Foreman — Workshop, Garage, Storage

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| W1 | Nuts and bolts | I | camp ruins | hand in 8 bolts, 8 nuts | — | a wrench; fastener-kit and hand-tool blueprints; your personal work station is bound (crafting §4) |
| W2 | A place for everything | I | camp | craft and hand in 2 fastener kits | W1 | **Storage 1**: basic backpack recipe, stash crates at the claim |
| W3 | Frame of mind | I | camp, glass tower | hand in 12 metal scrap; show a welding torch | W2 | steel-frame blueprint, **Workshop 1** (IE machine recipes) |
| W4 | The toolbox | I | camp | show a toolbox (crafted) | W3 | Workshop 1 effects; 16 iron ingots |
| W5 | Two miles west | II | **Novo**, 2.0 km SW in the cyberpunk district (v8) | hand in 6 spark plugs, 12 metal scrap, 4 motor oil — Novo's drops | W4, J-S1 | stage `novo_looted`; Marshall R2 opens |
| W6 | Hold the yard | I→II | the camp gate | stage `novo_held`; stage `novo_defended` (Novo's counterattack beaten at the camp gate, at the end of its fortify clock) | W5, Marshall R2 | **Workshop 2** (motor-assembly and mast-section-kit blueprints); **Storage 2**: iron backpack, stack upgrade ×2, magnet upgrade |
| W7 | Wheels | I–II | camp, the Line's depot | hand in 1 motor assembly, 4 steel frames, 1 car battery | L4 (the depot hands out the motor-assembly blueprint and its chest holds an electric motor), T5, M3 | **Garage 1**: quad and runabout recipes, wheel, fuel-tank, empty-fuel-can and cargo-crate blueprints; a full tank and 2 fuel cans; stage `car_built` when one is crafted |
| W8 | Fuel run | II | camp | hand in 2 fuel cans | W7, M7 | fuel-can refill recipe (at Michael's plant pump, M-B2; Walker's drum rack stores them) |
| W9 | Heavy metal | III | Novo | hand in 1 heavy diesel engine, 2 motor assemblies | W8, M-B2, `novo_held` | **Garage 2**: van and truck recipes |
| W10 | The big pack | III | Novo | hand in a second heavy anchor cable (Novo respawns them while held), 2 fastener kits | W9 | **Storage 3**: gold backpack, **everlasting upgrade** (the secure pack), feeding and pickup upgrades, truck cargo |
| W11 | Mast section kit | II–III | camp | show 1 mast section kit (6 steel frames + 2 fastener kits + heavy anchor cable) | W6, `novo_held` | the kit is Marshall's X2 hand-in |
| W12 | Boats | III | the settlement | reach the settlement by water (location); hand in 1 pressure gauge | W8, J4, W-V1 | boat cargo recipe |
| W13 | Hangar rights | III→IV | FR-06, the runway | hand in 1 avionics module, 2 circuit assemblies | W9, M11, J6 | **Garage 3**: light-aircraft recipe; **Storage 4** opens on J8 (diamond backpack needs the satellite receiver), tank and void upgrades, aircraft cargo |
| W14 | Foreman's pride | IV | everywhere | hand in one of every hardware and tool item (12 items) | W13 | Workshop 3; **the Foreman's Wrench** (an unbreakable, named wrench that fills a station's tool slot without wear) |
| W-A1 | Sidearm | I | camp | hand in 6 metal scrap, 4 screws, 1 fastener kit, 4 planks | W1 | gun-frame, barrel and trigger-group blueprints; pistol, pump-shotgun and their ammunition blueprints; the salvage rule (crafting §5.2) |
| W-A2 | Plates | I–II | camp | hand in 8 metal scrap, 2 duct tape | W3 | plate blueprint; scrap vest and helmet blueprints; rifle ammunition |
| W-A3 | Long guns | II | camp | hand in 2 gun frames, 1 steel frame | W-A1, `novo_defended` | assault-rifle and SMG blueprints; iron sights, extended magazine |
| W-A4 | Precision | III | camp, Financial Plaza | hand in 1 circuit assembly, 1 military circuit board | W-A3, W9 | sniper and machine-gun blueprints; optics, suppressor (explosives are Teddy's, §7A) |
| W-M1 | Motor pool | III | camp, FR-06, Financial Plaza | hand in 1 military circuit board, 4 plates, 1 heavy diesel engine; stages `fr06_defended` and `financial_defended` | W-A2, W-A4, D4, R5 | **Humvee RWS blueprint** (crafting §2.1; the SW assembling table at yard tier 2 builds it from the kit) |
| W-V1 | Something that floats | II | camp, the lake | hand in 12 planks, 1 fastener kit | W7 | boat blueprint; boat cargo opens with W12 |
| W-B1 | The yard, roofed | I | camp | hand in 8 metal scrap, 4 fastener kits, 16 planks | W2 | **yard tier 1**: roofed workshop, one bay, the lot fenced |
| W-B2 | Second bay | II–III | camp, Novo | hand in 4 steel frames, 32 concrete, 1 heavy diesel engine (Novo respawns them while held) | W-B1, `novo_defended` | **yard tier 2**: two bays, gantry crane, fuel rack, lights; vehicle repair at the bay |
| W-M2 | The pilot | IV | camp, the hub | hand in 8 steel frames, 1 large battery pack, 1 reactor control module (the Custodian's wreck is the story) | J-H1, W-B3 | the **PMV01B Core Stone**: the team's one mech (right-click summons it, left-click with the Stone heals it — the mod's rules); no second one exists |
| W-B3 | The shed | IV | camp, the hub | hand in 8 steel frames, 64 concrete, 1 satellite receiver | W-B2, J7, M13 | **yard tier 3**: steel shed, vehicle lift, floodlit lot, truck and aircraft bays; light-helicopter blueprint; **UH-60 Black Hawk blueprint** (crafting §2.1) |
| W-A5 | The dump | III | the stone complex (2.9 km, the spawner dungeon) | reach it (location); kill 15 there; hand in 16 gunpowder | W-A3, J4 | 2 salvage rifles; the powder order yields ×8 instead of ×4 |
| W-A6 | The tower on the hill | III | the town's tallest apartment block, 1.2 km W (design §2.7) | kill its boss (an Apotheosis boss; kill task, stage `boss_tower_1`) | W-A3, J2 | 1 Apotheosis gem, 2 salvage weapons — the Salvaging Table's first customer |
| W-W1 | Timber | II–III | the sawmill | hand in 64 planks, 1 **saw blade** (drops only at the sawmill) | W7, J-W1 | lumber orders (1 log → 8 planks, Quick) and the **timber barricade** for Walls 1 (6 planks + 1 fastener kit) |

---

## 3. Tony the Medic — Medical

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| T1 | Field dressing | I | camp ruins | hand in 4 bandages, 2 painkillers | — | med-kit blueprint; the clinic cures infection from now on |
| T2 | Stock the clinic | I | camp | craft and hand in 2 med kits | T1 | **Medical 1**: the clinic revive point — a downed player inside the camp outline is revived by the script after 10 s (PlayerRevive's range is one global value, 6 m; design §4.5); 4 med kits back |
| T3 | Neighbours | I | **Skadowsky — the residential block**, 1.4 km down the Line | hand in 3 blood bags, 4 syringes, 2 antiseptic — the block's drops | T2, J-S2 | stage `residential_looted`; Marshall R3 opens |
| T4 | Take the block | I | Skadowsky | stage `residential_held` (Marshall's assault won) | T3, Marshall R2 | 8 bandages, 4 antiseptic |
| T5 | Hold the block | I–II | the camp gate | stage `residential_defended` (the block's counterattack, at the base) | T4 | **Medical 2**: reduced death penalty; the med kit cures infection in the field |
| T6 | Analyzer | II | Skadowsky | hand in 1 medical analyzer | T5 | Medical 2 effects; 4 blood bags |
| T7 | Bio Gen | II | **Bio Gen**, 1.9 km SW in the cyberpunk district | reach Bio Gen (location); hand in 1 surgical kit | T6, J-S1 | surgical-kit use: full revive |
| T8 | Triage | III | anywhere | stage `revives_3` (three teammate revives, counted by KubeJS) | T5 | 8 med kits |
| T9 | Full power | IV | the hub | hand in 1 military power filter | T7, J7 | **Medical 3** |
| T10 | Ready room | IV | the base | hand in 10 med kits, 4 blood bags at the claim | T9 | finale readiness flag; Marshall X6 opens |
| T-B1 | Four walls | I | camp | hand in 16 planks, 8 bandages, 2 med kits | T2 | **clinic tier 1**: walls, four beds, the med station |
| T-B2 | Surgery | II–III | camp, residential block | hand in 32 concrete, 1 wiring harness, 1 medical analyzer (the block respawns them while held) | T-B1, `residential_defended` | **clinic tier 2**: surgery room, its own generator, the lit cross; faster revive at the clinic |
| T-B3 | The ward | IV | camp, the hub | hand in 64 concrete, 4 med kits, 1 military power filter | T-B2, T9 | **clinic tier 3**: two storeys, ward, quarantine tent, helipad; full revive at the clinic |
| T-W1 | Foraging | II–III | the hunters' hide, the forest | hand in 8 sweet berries, 4 brown mushrooms, 2 rabbit hide | T2, J-W1 | **poultice** recipe (2 sweet berries + 1 bandage → heals 2 hearts, clears poison; Quick); T7's surgical kit may also come from the wreck's medkit |

---

## 4. Michael the Engineer — Generator, Water

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| M1 | Sparks | I | camp ruins | hand in 3 wire spools, 1 power cord, 1 water filter | — | wiring-harness and filter-cartridge blueprints |
| M2 | Lights on | I | camp | hand in 2 wiring harnesses, 1 light bulb | M1 | **Generator 1**: lighting recipes, IE power |
| M3 | Clean water | I | camp, the lake | hand in 2 filter cartridges | M2 | **Water 1**: coolant and sealed-tubing blueprints |
| M4 | The refinery | III | **the industrial plant**, 2.4 km ESE across the lake | hand in 4 corrugated hoses, 4 radiator fins, 2 fuel cans — the plant's drops | M3, J-S3 | stage `plant_looted`; Marshall R4 opens |
| M5 | Hold the plant | III | the camp gate | stage `plant_held`; stage `plant_defended` (the plant's counterattack, at the base) | M4, Marshall R5 | **Water 2**: biodiesel chain, fuel cans |
| M6 | Pump it | III | the industrial plant | hand in 1 industrial pump | M5 | cooling-loop blueprint |
| M7 | Fuel for the road | II | camp | hand in 4 fuel cans | M5 | Walker W8 opens; 2 fuel cans back |
| M8 | The reactor plaza | III | **FR-06**, 2.5 km E | hand in 2 relays, 2 electric motors, 1 car battery — FR-06's drops | M6, W7, J-S4 | stage `fr06_looted`; Marshall R5 opens |
| M9 | Hold FR-06 | III | the camp gate | stage `fr06_held`; stage `fr06_defended` (FR-06's counterattack, at the base) | M8, Marshall R5 | **Generator 2**; transformer cores start spawning |
| M10 | Core | III | FR-06 | hand in 1 transformer core | M9 | generator-kit blueprint |
| M11 | The hangar | III→IV | FR-06 hangar, the plant complex | hand in 1 avionics module (FR-06); hand in 1 reactor control module (the plant complex's control room — the first far-edge trip, by truck through the west gate) | M10 | hangar unlocked; Walker W13 opens |
| M12 | Purification | III | industrial plant | hand in 1 purification membrane | M6 | **Water 3** |
| M13 | Full grid | IV | the hub | hand in 1 military power filter, 2 wiring harnesses | M11, J7 | **Generator 3** |
| M-B1 | Under a roof | I | camp | hand in 8 metal scrap, 2 wiring harnesses, 1 filter cartridge | M2 | **plant tier 1**: generator shed, water collector |
| M-B2 | Tank farm | II–III | camp, industrial plant | hand in 4 steel frames, 32 concrete, 4 sealed tubing, 1 purification membrane (the plant respawns them while held) | M-B1, `plant_defended` | **plant tier 2**: tanks, pump house, pipe run to the lake, the fuel pump, **the charging station**; fuel cans refill at the pump; battery-pack blueprints (crafting §5.4) |
| M-B3 | The grid | IV | camp, FR-06, the hub | hand in 8 steel frames, 1 transformer core, 1 military power filter | M-B2, M13 | **plant tier 3**: wind mast, transformer yard, biodiesel column; the camp lit and powered |
| M-P1 | The wet hall | II | the prismarine hall (2.2 km) | reach it (location); hand in 4 water filters, 2 antifreeze — the hall's drops | M3, J2 | 2 coolant; Tune's first line about the sculk on its floor (finale §3) |
| M-W1 | The cabin's generator | III | the ranger cabin | hand in 1 **portable generator** (found only in the cabin) | M5, J-W1 | the ranger's still: 1 motor oil + 1 empty fuel can → 1 fuel can at the plant's pump (M-B2) |

---

## 5. Tune the Technician — Radio and intel

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| U1 | Static | I | camp ruins | hand in 1 circuit board, 2 capacitors, 1 broken radio | — | circuit-assembly blueprint |
| U2 | The map | I | camp | hand in 2 circuit assemblies | U1 | **Radio 1**: shared waypoints, the warning system |
| U3 | Listening post | II | the tower compound (in the camp), the library | reach both (location); hand in 1 hard drive | U2, J2 | the strongpoint board shows garrison strength |
| U4 | The plaza | III | **Financial Plaza**, 2.1 km W | hand in 2 circuit boards, 2 computer parts, 1 hard drive — the plaza's drops | U3, W7, J-S5 | stage `financial_looted`; Marshall R5 opens |
| U5 | Hold the plaza | III | the camp gate | stage `financial_held`; stage `financial_defended` (the plaza's counterattack, at the base) | U4, Marshall R5 | **Radio 2**: the contested site's whole countdown on the board; antenna-element blueprint |
| U6 | Under the plaza | III | the sewers | reach the sewers (location); kill 20 there; hand in 1 encrypted radio | U5 | the board shows which entry point the next counterattack uses (east road or north rim) |
| U7 | Military board | III | Financial Plaza | hand in 1 military circuit board | U5 | transmitter blueprint |
| U8 | Antennas | III | camp | craft and show 4 antenna elements | U5 | 4 antenna elements back |
| U9 | Array | IV | the hub | hand in 1 phased array element | U8, J8 | antenna-array blueprint; **Radio 3** |
| U10 | Technician's ear | IV | everywhere | hand in one of every electrical item (8) | U9 | Radio 3 effects: the coming attack's composition on the board from the moment the marker is placed |
| U-B1 | Mast up | I | camp | hand in 6 metal scrap, 2 wire spools, 1 circuit assembly | U2 | **shack tier 1**: mast to 24 with a dish, the map wall extended |
| U-B2 | Antenna field | III | camp, Financial Plaza | hand in 4 steel frames, 4 antenna elements, 1 encrypted radio (the plaza respawns them while held) | U-B1, `financial_defended` | **shack tier 2**: antenna field, intel desk (the board's countdown readout is Radio 2's, U5) |
| U-B3 | Uplink | IV | camp, the hub | hand in 8 antenna elements, 2 circuit assemblies, 1 satellite receiver | U-B2, U9 | **shack tier 3**: mast to 40 with an aviation light, second dish, roof receiver (the board's readouts come from Radio 2 and 3) |
| U-C1 | Copper | II | the copper tower (2.2 km) | reach it (location); hand in 4 relays, 4 wire spools — the tower's drops | U2, J2 | 2 circuit assemblies; the notebook marks the tower as the electrical run |
| U-A1 | Dead quiet | III | the sculk cellar under the town's palace of culture, 1.1 km W (design §2.7) | reach it (location); hand in 1 echo shard from its chests | U5, W-A3 | 1 encrypted radio; stage `ancient_city_1`; Tune: "Whatever is down there is listening." |
| U-W1 | Quiet ground | III | the ranger cabin's high ground | hand in 1 antenna element at the cabin's relay mast (location + hand-in) | U5, J-W1 | the relay: the board shows the Woods sites and the outpost's garrison (`woods_relay`); 2 antenna elements back |
| U-D1 | Go down | I–II | the bunker under the farmstead at (−1712, −1744), 0.6 km | reach it (location); hand in 1 hard drive from it | U2 | stage `bunker_1`; 2 circuit assemblies; the notebook's "Getting hurt" page notes the dark |
| U-D2 | Deeper | III | the road-range bunkers under the farmsteads at (−2432, −1168), (−528, −2640), (432, −2448) | reach all three (location); hand in 1 encrypted radio | U-D1, W7 | 1 military circuit board |
| U-D3 | The archive | IV | the plant complex's bunker beyond the river, 3.5 km E | reach it by air (`bunker_east_by_air`); hand in 2 hard drives | U-D2, J7 | 1 satellite receiver (a second source: one fewer hub item to find, design §4.4) |

---

## 6. James the Scout — expeditions

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| J1 | Get your bearings | I | glass tower, acacia hall | reach both (location) | — | waypoints; a compass and a map |
| J-S1 | Scout: Novo | II | Novo, 2.0 km SW | reach Novo (location); hand in the **Novo dossier** (the gatehouse office, chest at (−2844, −754)) | J1 | stage `novo_scouted`; the board shows Novo's garrison and its component container; Walker W5 opens |
| J2 | The west edge | II | residential block, hempcrete compound, library | reach all three (location) | J1 | waypoints; the expedition board |
| J-S2 | Scout: the block | I | Skadowsky, 1.4 km SE down the Line | hand in the **block dossier** (the caretaker's flat in Skadowsky's hospital, placed with the sector's dressing) | J2 | stage `residential_scouted`; Tony T3 opens |
| J-S3 | Scout: the plant | III | the industrial plant, across the lake | reach the plant (location); hand in the **plant dossier** (the control room, chest at (558, −1277)) | J2 | stage `plant_scouted`; Michael M4 opens |
| J-S4 | Scout: FR-06 | III | FR-06 | reach the reactor plaza (location); hand in the **FR-06 dossier** (the hangar office, chest at (601, −1690)) | J-S3, W7 | stage `fr06_scouted`; Michael M8 opens |
| J-S5 | Scout: the plaza | II | Financial Plaza | reach the plaza (location); hand in the **plaza dossier** (the vault anteroom, chest at (−3345, −677)) | J-S3, W7 | stage `financial_scouted`; Tune U4 opens (J-S5 gates on J-S1, not J-S3, in v8) |
| J3 | Paper trail | II | offices, the library | hand in 2 folders of documents | J2 | a **valuables bag** (opens to 8 random valuables — loot sheet §7) |
| J4 | The far ring | II–III | the bus depot, the four farmsteads south of the Woods, the settlement, Bio Gen (design §2.7) | reach all four (location); the far two by car | J3, W7 | waypoints; Tony T7 and Walker W12 open |
| J5 | Settle in | III | the settlement | hand in 3 valuables found there | J4, W-V1, M-B2 | speedboat blueprint |
| J6 | Runway | III | the runway | stand on the runway (location); hand in 1 hard drive | J4 | aircraft prep flag |
| J7 | The hub | IV | **the hub**, 6.2 km | reach the hub by air (location) | J6, W13 | the hub's loot tables switch on |
| J8 | Bring it back | IV | the hub | hand in 1 phased array element, 1 satellite receiver | J7, J-H1 | Tune U9 opens; Storage 4 (W13's diamond pack) unlocks |
| J9 | Every capital | IV | the whole box | reach the town's four quarters (location; design §2.7) | J7 | a **components crate**: choose any 4 of heavy diesel engine, purification membrane, encrypted radio, medical analyzer (held-site components, never a hub item; loot sheet §7) |
| J10 | Cartographer | IV | everywhere | reach every named site on the map (location, 20) | J9 | **the Cartographer's Pack**: a diamond backpack fitted with magnet, everlasting and stack ×3 (the pack's cap), named |
| J-H1 | The custodian | IV | the hub's core (the Pantsir plaza) | kill **the Custodian** (a Pomkot's Mechs PMB01 the loop script spawns when a player first enters the core; kill task, stage `custodian_dead`; its terrain destruction is denied by `gscraft_mech_griefing.js`) | J7 | the hub's core opens: the phased-array container arms (J8 can be done); 8 emeralds |
| J11 | Every ruin | IV | everywhere | hand in one of each of the forty-two small items | J10 | the Collector analogue: an **inception upgrade** and a second everlasting upgrade — a nested pack that also survives death |
| J-B1 | A flag on it | I | camp | hand in 16 planks, 4 fastener kits, 1 folder of documents | J1, W1 | **lookout tier 1**: platform, ladder, a flag |
| J-B2 | The spotlight | III | camp, the far ring | hand in 4 steel frames, 2 light bulbs, 1 car battery, 3 valuables from the settlement | J-B1, J4 | **lookout tier 2**: 30 tall, a night spotlight (waypoint sharing is Radio 1's); zipline rope and hook orders (crafting §5.7) |
| J-B3 | The cabin | IV | camp, the hub | hand in 8 steel frames, 16 glass, 1 satellite receiver | J-B2, J7 | **lookout tier 3**: 40 tall, glass cabin, telescope, waypoint beacon; every named site marked |
| J-C1 | The capital | III | the town centre, 1.2 km W | reach it by car (`capital_1`, §9.1); hand in 2 folders of documents found there | J4 | 6 emeralds; the capital marked on the board; J9's four air-ring capitals come later |
| J-C2 | The house in the fog | II–III | the fog house at the Woods farmstead (−2192, −32), 2.2 km — or either of the Woods' two | reach one (location); the book only says "go at night" | J2 | a Field note; 4 emeralds |
| J-W1 | Into the trees | II–III | the sawmill (south edge), the ranger cabin (high ground) | reach both (location) | J2, W7 | waypoints; the notebook's Woods line; stage `woods_scouted` |
| J-W2 | Two doors down | III | the two Woods bunkers | reach both (location); hand in 1 hard drive from them | J-W1 | stage `woods_bunkers`; 2 circuit assemblies |
| J-W3 | The wreck | III | the downed aircraft | reach it (location); hand in the **flight recorder** (a valuables item found only there) | J-W1 | 1 avionics module (the second source; W13 and the Black Hawk want them) |

---

## 7. Marshall — the loop, the defences, the tower

**Gate to speak:** W1, T1, M1, U1, J1 all done.

### 7.1 The strongpoint loop

Each take is the same shape: the marker is placed at the site's anchor point, the assault runs
for 5 minutes, the marker must survive and a player must be inside the rectangle at the end
(design §6.1). The marker is refused until the site is scouted and looted, and while another site
is still contested — one fight at a time, in this order.

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| R1 | Muster | I | camp | checkmark; read the strongpoint board | the five introductions | the board and the map wall revealed, the camp's outline lit (B9); the claim-marker blueprint (trip-length order; re-crafted after a failed assault) |
| R2 | The block | I | Skadowsky — the residential block | place the marker; win the assault (stage `residential_held`) | R1, `residential_looted`, L6 | the block's site guard and its keeper (Vera) appear; the fortify clock starts; Tony T4 opens; the first counterattack is the lightest (enemies §5's Matron leads it) |
| R3 | Novo | II | Novo | place the marker; win the assault (stage `novo_held`) | R2, `residential_defended`, `novo_looted` | Novo's site guard and Kessler appear; Walker W6 opens |
| R4 | The plaza | II | Financial Plaza | place the marker; win the assault (stage `financial_held`) | R3, `financial_looted` | Ilya appears; Tune U5 opens |
| R5 | The waterworks | III | the waterworks, over the viaduct | place the marker; win the assault (stage `plant_held`) | R4, `novo_defended`, `truck_built`, `plant_looted` | Oksana appears; Michael M5 opens |
| R5b | The far shore | III | FR-06, across the lake | place the marker; win the assault (stage `fr06_held`) | R5, `boat_built`, `fr06_looted` | Rook appears; Michael M9 opens; the boat has done its job |
| R6 | Every site | III | all five | all five held and defended at once (stage `all_held`) | R5 | component respawn rate doubled |

### 7.2 Walls, defences, farm, the field

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| D1 | Walls | I | the claim | hand in 32 concrete, 2 fastener kits | R1 | **Walls 1**: sandbag, barbed-wire and claymore orders (crafting §5.7); the timber barricade after W-W1; +2 soldiers at every site guard |
| D2 | Guards | II | the claim | stage `novo_defended` and `residential_defended` | D1, M-B2 | **Walls 2**: the Recruit's Table at the gatehouse — hire recruits, shieldmen and bowmen with emeralds and food; guard villagers at every NPC building tier 2; drone orders and Create Big Cannons' drop mortar (crafting §5.7 — Superb Warfare's mortar is gone; the Create chapter's gun is the artillery proper); +2 soldiers at every site guard |
| D3 | Farm and kitchen | II | the claim, the hempcrete compound (seeds, bowls; the mud village later) | hand in 16 seeds, 8 bowls, 1 med kit | D1 | **Farmer's Delight kit** (stove, cooking pot, skillet, cutting board, knife; 8 each of rice, tomato seeds, onions, cabbage seeds); **Farm 1**: the kitchen's meals feed the team |
| D4 | Bunker | III | the claim | hand in 64 concrete, 4 steel frames, 1 heavy anchor cable | D2, W9, M9 | **Walls 3**: blast doors, radar, C4 and jump-pad orders (crafting §5.7; the laser tower is replaced by the autocannon nests of G8); armoured-car recipe; +2 soldiers at every site guard |
| D5 | Greenhouse | III | the claim, the plant | hand in 16 cabbages, 16 onions, 8 cooked meals (Farmer's Delight), 1 industrial pump (irrigation; the plant respawns them while held) | D3, `plant_defended` | **Farm 2**: greenhouse and irrigation; crops inside the claim grow at double rate (KubeJS random-tick boost) |
| D6 | Rations | III–IV | the claim, the plant | hand in 32 cooked meals, 1 purification membrane (the plant respawns them while held) | D5, `plant_defended` | **Farm 3**: hydroponics; the **ration pack** recipe (4 meals → 1 pack, Saturation, stacks 16) — the hub run's food |
| D-O1 | The outpost by the road | II | the outpost at the farmstead (−2720, −1072), 1.7 km SW | kill 10 pillagers there (kill task, stage `road_outpost_cleared`) | D1, W-A1 | 90 rifle rounds; the outpost stays quiet (the script stops its pillagers respawning) |
| R-W1 | The outpost | III | the bandit outpost | clear it: kill 15 there (kill task, stage `woods_outpost_cleared`); no marker, no contested slot, no site guard, no counterattack — it is not a strongpoint | R4, J-W1 | the outpost's cache (2 salvage rifles, 90 rounds, 4 emeralds); bandits stop spawning in the Woods; **Teddy the Hermit** appears in the outpost's tower (§7A) |
| R-W2 | What the trees heard | IV | the Woods bunkers' lower levels | kill 30 below y 40 in the two bunkers; hand in 1 encrypted radio found there | J-W2, U6 | 1 military circuit board; the Woods page of the notebook completes |

### 7.3 The tower

**Gate:** the five introductions (R1). X1 opens with Marshall; the stages stay part-gated (owner, 2026-09-04).

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| X1 | The tower | I | the tower compound in the camp | walk to the tower (location); checkmark after Marshall's briefing | the five introductions (with R1) | the tower chapter's stage list; the parts rack's five hooks are named |
| X2 | Mast section kit | II | camp, Novo | hand in 1 mast section kit | X1, W11 | **stage 1** placed; the mast stands |
| X3 | Cooling loop | III | camp, the plant | hand in 1 cooling loop | X2, M6 | **stage 2** placed |
| X4 | Generator kit | III | camp, FR-06 | hand in 1 generator kit | X3, M10 | **stage 3** placed; the lights come on |
| X5 | Transmitter | III | camp, Financial Plaza | hand in 1 transmitter | X4, U7 | **stage 4** placed; the dish |
| X6 | Antenna array | IV | camp, the hub | hand in 1 antenna array | X5, U9, T10, M13 | **stage 5** placed; the beacon lights; the countdown starts; **M3A3 Bradley blueprint** - the finale's armoured vehicle is built during the countdown, not handed over (crafting §2.1) |
| X7 | Hold the line | IV | the base | survive waves 1–4 (stages `wave_1`…`wave_4`) | X6 | between waves: 8 med kits, ammunition |
| X8 | The Sleeper | IV | the base | kill the Sleeper (a named Warden, tag `gscraft_boss`; `gscraft-finale.md`) | X7 | the game's ending; the season flag; the finale chest at the plinth |
| X6b | Relight | IV | camp | repeatable, no hand-in; visible after `finale_failed`, one in-game day later | X6 | restarts the 60-minute countdown; Radio 3 shows the same composition |
| X9 | Afterwards | IV | camp | checkmark | X8 | free play; the board stays live |

### 7.4 The gatehouse

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| R-B1 | A gate | I–II | camp | hand in 32 concrete, 4 steel frames, 2 fastener kits | R2 | **gatehouse tier 1**: the gate, wall stubs (the parts rack stands from tier 0) |
| R-B2 | Watchtowers | II–III | camp, Novo | hand in 64 concrete, 8 steel frames, 1 heavy anchor cable | R-B1, R3, R4 | **gatehouse tier 2**: walled gate, two watchtowers, barricades; guard villagers at the gate |
| R-B3 | Blast doors | IV | camp, the plant complex | hand in 128 concrete, 8 steel frames, 1 reactor control module (the plant complex) | R-B2, X4 | **gatehouse tier 3**: blast doors, floodlights, the board as a lit wall map; the finale's first wave breaks on the gate |

## 7A. Teddy the Hermit — explosives (the Woods outpost)

Teddy is the seventh survivor and the only one outside the camp (owner, 2026-09-04). He appears at the
Woods' bandit outpost (the farmstead at (−2176, −576)) the moment R-W1 clears it — `gscraft:npc_teddy` summons him in the
outpost's tower — and his chapter is the game's only source of **explosive weapons and their ammunition**:
grenades, the M79 and its 40 mm rounds, the RPG-7 and its rockets, all Superb Warfare items, all crafted at
the stations from his blueprints and sold at his counter (vendors doc §3). Nothing explosive is craftable
or sold anywhere else; Marshall's Walls orders stay Marshall's; C4 and mortar shells get
cheaper once Teddy's last blueprint is in.

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| H1 | The hermit | III | the Woods outpost | hand in 8 gunpowder, 4 canned goods | R-W1 | **hand grenade** blueprint (crafting §5.8); Teddy's counter opens at LL1 |
| H2 | Smoke | III | the outpost | hand in 4 antifreeze, 8 cloth | H1 | **smoke grenade** blueprint |
| H3 | Old ordnance | III | the outpost, the stone complex | hand in 12 powder, 4 steel frames, 1 salvage rifle | H1, W-A5 | **RGO grenade** blueprint; the counter's hand-grenade cap rises from 2 to 4 a day |
| H4 | The tube | III–IV | the outpost | hand in 4 plates, 1 circuit assembly, 20 powder | H3, W-A2 | **M79 grenade launcher** and **40 mm grenade** blueprints; counter LL2 (40 mm rounds) |
| H5 | Backblast | IV | the outpost, Financial Plaza | hand in 1 military circuit board, 2 steel frames, 30 powder | H4, W-A4 | **RPG-7** and **standard rocket** blueprints; counter LL3 (rockets) |
| H6 | Thermobaric | IV | the outpost, FR-06 | hand in 1 transformer core, 40 powder | H5 | **TBG rocket** blueprint |
| H7 | The cache | IV | the outpost, the hub | hand in 1 hard drive, 50 powder | H6, J7 | **high-energy explosives** blueprint — Marshall's C4 order takes 1 of them instead of 4 powder, and the HE shell order (G7) 1 instead of 2 powder for a double yield (crafting §5.8) |

Teddy's counter has no building tiers: its loyalty levels are H1, H4 and H5. He buys gunpowder and
powder (vendors doc §4).

---


### 7.5 The Line

Marshall's chapter carries the corridor's spine; each stop's own quest sits with its NPC (the L-ids
below are the stops; the NPC's task is in the row). The stops are walked in order because each
building's chest holds the next stop's marker. The corridor is design §2.6: the old power line from
the camp's south edge to the residential block's west gate.

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| L1 | The farmstead | I–II | The Line | reach the farmstead (location); hand in 8 wheat and 4 wild herbs to Tony | J1 | Tony: herb blueprints early; Marshall: D3 opens with the seeds |
| L2 | The pump house | II | The Line | reach it (location); fill 2 filter cartridges at its pump, hand them to Michael | L1, M2 | Michael: **Water 1** if not already held |
| L3 | Substation A | II | The Line | reach it (location); hand in 2 wiring harnesses and 1 relay to Michael | L2 | Michael: the harness kit; the line's power comes on to Substation A (floodlight) |
| L4 | The depot | II | The Line | reach it (location); hand in 12 metal scrap and 2 fuel cans to Walker | L3 | Walker: truck-cab blueprint; the **motor-assembly blueprint** (the first car before the district walk, review fix 5) |
| L5 | Substation B | II | The Line | reach it (location); place a relay mast on its yard | L4, U3 | Tune: the board shows the block's garrison; power reaches Substation B |
| L6 | The switching station | II | The Line | clear the checkpoint (kill 8 armed pillagers there); hand in 1 circuit assembly to Marshall | L5, `residential_looted` | the switching hall lights; **R3 opens** — the block's take is walked in from here |

### 7.6 The Gun (the Create chapter, `gscraft-create-and-artillery.md` §4)

In Marshall's chapter. The first gun is built in the camp — cast in Walker's yard, bored on its hand-cranked frame,
mounted in the gun pit — and fired before a single site is held; the sites scale it up. Nothing about operating it is
ours: laid by rotation, fired by redstone, read on goggles or the pit's display board (interface doc §4.8).

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| G1 | Sand and iron | II | camp — Walker's yard | hand in 16 casting sand, 8 cast-iron ingots (Novo's loot), 4 logs | W-B2, `novo_looted` | the cannon cast and the moulds; the yard's basins pour cast iron |
| G2 | The first pour | II | camp — the yard | pour a cast: one unbored barrel and a cannon end | G1 | stage `gun_cast`; the cast pit's hoist |
| G3 | The bore | II | camp — the yard | bore two barrels and a chamber on the hand-cranked frame (four minutes each) | G2 | stage `gun_bored` |
| G4 | Mount and charge | II–III | camp — the gun pit | the cannon mount, hand crank, yaw controller, loader, lever; 8 powder charges, 4 solid shot; **fire it** (CBC's advancement) | G3, Walls 1 | the first gun; stage `gun_fired` |
| G5 | The gunner's manual | III | Skadowsky | hand in the manual (Vera, S-residential-1) and 2 spyglasses | S-residential-1, G4 | the range card (a Patchouli book per gun), the pit board, the map wall's rings; stage `gun_range` |
| G6 | Steel | III | FR-06 T2 | 24 steel ingots poured at Novo's foundry, the cannon builder at FR-06 | S-fr06-2, S-novo-2, G5, `fr06_defended` | the long gun, the quick-firing breech; `gun_steel` |
| G7 | Shells | III–IV | the plaza T2 | 4 HE, 2 AP, 2 shrapnel; impact and proximity fuzes | S-financial-2, G6 | shells and fuzes as station orders; the smoke shell; `gun_shells` |
| G8 | The battery | IV | FR-06 T3, the gatehouse T3 | a bronze autocannon with handles on each watchtower; an ammo container of AP | S-fr06-3, R-B3 | Walls 3's nests (they replace the laser tower); `gun_battery` |
| G9 | The carriage | IV | Walker T3 | the cannon carriage and a second gun; tow it with the truck | G6, W-B3 | a mobile gun; `gun_carriage` |
| G10 | Nethersteel | IV | the tower | nethersteel (steel + nether material, superheated): the thick chamber | tower stage 4 | the finale's shot — the answer to the fifth wave's vehicle; no gate on the finale; `gun_nethersteel` |

### 7B. The site chains (the Create chapter §3)

Each held strongpoint's keeper gives three quests, `S-<site>-1…3` (site ∈ residential, novo, financial, fr06, plant),
climbing the site through Repair, Works and Fortify; each hand-in places `gscraft:site_<site>_<tier>` over the site's
core building. Hand-ins follow the camp tiers' rule (design §3.6): tier 1 camp junk and first intermediates, tier 2
bulk material plus one more of the site's own component, tier 3 one hub item. Fifteen quests plus Skadowsky's rail
yard (S-residential-3 places the depot; the train is James's J-T1…3, three more) = 18. The keepers and their works:
Vera (Skadowsky: the hospital, a second revive point by the script; the rail yard at tier 3), Kessler (Novo: the
foundry), Ilya (the plaza: the fuze lab), Rook (FR-06: the steel works), Oksana (the plant: the power house and the
boring mill). Full rows in the Create chapter §3.

## 8. How the acts feel in play

**Act I (sessions 1–2).** Five introductions in the camp's own ruins; the personal station, the first
backpack, lights. James sends them to the settlement and the runway to learn the ground. The town's east blocks are the first ruins, 200 m from the gate (O2). Then the Line: down the pylons
south-east to Skadowsky, the one strongpoint in walking range — its dossier, two or three loot runs for Tony, the
switching station, then Marshall's marker and the assault. Skadowsky is held by its site guard and Vera, its fortify
clock runs, and its counterattack — the lightest in the game — arrives at the camp gate on schedule. The depot on the
Line hands out the motor-assembly blueprint, so the first car is built before anyone walks two kilometres.

**Act II (sessions 3–5).** The town and the cyberpunk district by car: Novo and the plaza are scouted, looted, taken
and held; Bio Gen and the library are looted; the first gun is cast, bored and fired in the camp (G1–G4). The tower
chapter, open since the introductions, gets its first parts; stage 1 goes up. Three sites are held.

**Act III (sessions 6–9).** The far bank. The truck first: over the viaduct and up the east bank to the waterworks
(the industrial district beside the pack's plant complex) — its take needs a bulky item carried, which is what the
truck is for. Then the boat: straight across the lake to FR-06 on the east shore, 2.2 km of water against 4.2 km of
road, the boat's one real job. The rail yard on the lake's north-east shore and James's train (J-T1–3) tie the far bank
together. The secure pack arrives. Stages 2–4 go up: the tower has power and a dish; the gun gets steel, shells and the range
card. Five sites in the pool means five counterattacks fought and won at the gate, one at a time, and the map is theirs.

**Act IV (sessions 10–12).** The two far edges, opposite corners of the map: the hub inside the district (the
Custodian, the phased array element and the satellite receivers) and the plant complex (the reactor control module in
the control room, the switchyard, U-D3's bunker), by truck through the plant's west gate or by air over the lake from
the runway. The antenna array goes up, the beacon lights. Tony's ready room, Marshall's walls and the battery decide the finale; the waves come to the base; the
Sleeper (`gscraft-finale.md`).

---

## 9. What FTB Quests needs from KubeJS

Stages, all **team** stages (FTB Teams) unless marked *player*, set by the loop script or a quest
reward and read by stage tasks (C3, 2026-09-04):

| Group | Stages |
|---|---|
| Site ladder | `<site>_scouted`, `<site>_looted`, `<site>_held`, `<site>_defended`, `<site>_lost` (the counterattack at the base was lost; the site stays held and the wave returns after the next clock) for `novo`, `residential` (the Skadowsky sector in v8), `plant`, `fr06`, `financial`; `all_held` |
| The Woods and the kept structures | `woods_scouted`, `woods_bunkers`, `woods_outpost_cleared`, `woods_relay`, `bunker_1`, `road_outpost_cleared`, `boss_tower_1`, `ancient_city_1`, `capital_1` |
| Vehicles | `car_built`, `boat_built`, `truck_built`, `aircraft_built`; the vehicle-qualified location flags `settlement_by_car`, `biogen_by_car`, `settlement_by_boat`, `hub_by_air`, `bunker_east_by_air`, `capital_1` (§9.1) |
| Function levels | `workshop_1…3`, `garage_1…3`, `storage_1…4`, `medical_1…3`, `generator_1…3`, `water_1…3`, `radio_1…3`, `walls_1…3`, `farm_1…3` |
| Building tiers | `camp_<npc>_<tier>` for the six NPCs, tiers 1–3 |
| The tower and the finale | `marshall_speaks` (the five introductions), `tower_1…5`, `beacon_lit`, `finale_ready` (T10), `wave_1…5`, `finale_won`, `finale_failed`, `season_1_done` |
| Gates and switches | `hangar_unlocked` (M11), `aircraft_prep` (J6), `hub_loot_on` (J7), `custodian_dead` (J-H1), `teddy_present` (R-W1), `revives_3` (*player*) |
| Blueprints | `bp_<recipe>`, one per recipe in the crafting sheet (the recipe file is the list); the card item is the player's copy, the stage is the team's record (crafting §4) |
| The Gun and the site chains | `gun_cast`, `gun_bored`, `gun_fired`, `gun_range`, `gun_steel`, `gun_shells`, `gun_battery`, `gun_carriage`, `gun_nethersteel`; `site_<site>_1…3` for the five sites; `train_1…3` (J-T) |
| First-time lines (*player*, onboarding §8) | `seen_station`, `seen_bulky`, `seen_infection`, `seen_warning`, `seen_board`, `seen_down` |

Items the script owns: the five dossiers and the claim
marker. The loop script keeps, per site, the fortify deadline, the counterattack flag (cleared on `_lost` so it re-runs), the site guard's target size and owner, and the
component-container state and the single `contested` slot; all clocks count online ticks only. Rewards run commands:
`kubejs stage add`, `function gscraft:tower_stage_N`, `function gscraft:camp_<npc>_<tier>` (the
building tiers, which also re-summon the NPC), a team stage `bp_<recipe>` for blueprints (the book says "blueprint", the mechanism is the stage - crafting §4; the old text: an IE blueprint item
with the `gscraft` category NBT). Location tasks use the site rectangles from the district map;
the six NPC building rectangles are locked by the tower-lock script (a list of rectangles, quest
functions exempt), so a `*-B` reward is the only thing that ever changes them; dossier chests are placed by `gscraft:dossiers` and filled by `dossiers_fill` (parked in `build/phase_c/` until the dossier items exist) at the coordinates in `tools/dossiers.json`; the kill tasks are the sewers (U6), the stone complex (W-A5), the boss tower (W-A6), the road outpost (D-O1), the Woods outpost (R-W1), the Woods bunkers (R-W2), the Custodian (J-H1) and the Sleeper (X8); every other clearing is the assault event, whose
waves use the garrison mob types In Control! spawns at each site.

### 9.1 Vehicle-qualified location tasks (C13)

"By car", "by boat" and "by air" are not FTB Quests task types. The loop script checks, once a second for every online
player, `player.vehicle`: an Immersive Vehicles entity (`mts:*`) or a Superb Warfare vehicle counts as *car* (boat and
aircraft ids are two short lists from crafting §2), and when a player in a qualifying vehicle is inside the target
rectangle the script sets the flag stage (`settlement_by_car`, `biogen_by_car`, `settlement_by_boat`, `hub_by_air`,
`bunker_east_by_air`, `capital_1`). The quest's task is then a stage task, and the book's text says "by car". A player who walks
there has the location for free but not the flag.
