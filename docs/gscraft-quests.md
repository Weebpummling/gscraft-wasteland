# GSCraft Wasteland — Quests and Tasks

> **Realigned 2026-09-07** against `docs/gscraft-skadowsky-camp.md`. Questing routes only to the Pripyat
> base map, the Skadowsky sector and the hempcrete compound. The camp is in Skadowsky, in the pocket east
> of the south-west bridge; Skadowsky is the home sector, and the medical strongpoint is the **Skadowsky
> hospital**, which is a different place 0.34 km north of the square. Quests that point at Novo Industrial,
> the Financial Plaza and its sewers, Bio Gen, the desert city hub, the mega-base FR-06, the waterworks,
> the library or the runway are marked **deferred**: they keep their design for a later quest line and are
> not live act targets.


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
| **I — The town you woke in** | the pocket, then north through Skadowsky | 0 – 0.4 km | Skadowsky's own ruins, its station and its level crossing, **the Skadowsky hospital** (0.34 km N) | on foot, inside the sector | 1–2 |
| **II — West over the bridge, and south down the bank** | the home (east) bank by car, and the far bank over the bridge | 1.2 – 2.5 km by road | the collective farm (1.17 km W, the Line's far end), the town's ruins (its east avenue 1.52 km W, the central square 2.46 km W), **the hempcrete compound** (2.30 km W, Walker's strongpoint), the mast's field (in the camp); **the Woods** (sixteen quests across the chapters from J-W1, seven of them Teddy's) [needs measurement] | on foot, then the first car | 3–5 |
| **III — The plant complex** | south down the east bank, no river crossing | 1.1 – 2.2 km by road | **the switchyard and admin block** (1.09 km, Tune's), **the turbine hall** (2.06 km, Michael's), **the cooling intake works** (2.16 km, Michael's), the plant's four storage halls | the truck, the marsh channels | 6–9 |
| **IV — The reactor** | the confinement hall, and the bridge road west | 1.53 km | **the confinement hall** (1.53 km, roof y 198) — Act IV's prize and not a strongpoint: the reactor control module for the gatehouse tier 3 and the antenna array for tower stage 5 | air from the mast field, or the bridge road | 10–12 |

Rules that hold across every chapter:

- **Introductions first.** Each NPC's first quest asks for common items from Skadowsky's own ruins —
  the sector is a 464 × 752 town and needs no wrecks invented for it (`camp_ruins` is retired).
  Marshall does not speak until all five introductions are done.
- **One strongpoint per act boundary (v8 distances, owner default E1).** The Skadowsky hospital closes
  Act I; the hempcrete compound is Act II; the plant's switchyard, turbine hall and intake works are Act III; the confinement hall — Act IV's prize, not a strongpoint — closes the game. The tower's parts follow the strongpoint order: the mast repair from Skadowsky, the transmitter from the switchyard, the generator from the turbine hall, the cooling loop from the intake works, the array from the confinement hall; the hospital feeds the clinic.
- **Every strongpoint is three quests in three chapters before it is held** (design §6.1): James's
  scout quest (reach it, bring back its dossier), the owning NPC's loot quest (hand-ins that drop
  only there, two or three trips), then Marshall's take (place the marker, win the 5-minute
  assault). The marker is refused until the first two are done. The owning NPC's hold quest
  completes when the site's counterattack is beaten at the base, which always comes at the end of the fortify clock.
- **The tower chapter opens with Marshall** (owner, 2026-09-04). When the five introductions are done Marshall speaks,
  the strongpoint board lights and the tower chapter appears in the book at the same moment; X1 is the briefing.
  The stages themselves stay gated by their parts, so the chapter is visible early and completed late. (Superseded
  text follows for the record.) Draft 2 gated it on **significant progress**:
  three strongpoints held (the compound, the hospital, the intake works), Workshop 2, **Water 2**, Storage 2, and a
  car built. That is the end of Act II at the earliest. (Draft 1 said Generator 2, which is M9's
  reward for holding the turbine hall in Act III and would have kept the chapter shut a whole act longer than
  the stage labels claim.) Stages 1–2 are Act II parts, 3–4 are Act III, 5 is Act IV, so the tower
  is repaired across the second half of the game, not at its end.
- **Every attack is a quest, and every attack comes to the base** (owner, 2026-09-04). A taken site is held by a
  friendly **site guard** the take unlocks (design §6.1); when its fortify clock runs out the site's counterattack marches on the camp
  gate, and beating it there is the owning NPC's hold quest. The approaches are the bridge from the west, the main road
  east, and the rail corridor north and south; the bridge is a single 8-block deck and is where Act I's counterattack is
  fought. It is deterministic, it is fought at home, and it is the
  only attack that site will ever bring.
- **Every NPC's building climbs three tiers** (design §3.6): three `*-B` quests per chapter, each
  hand-in rebuilds their site on the same footprint and re-summons them in it. Tier 1 after the
  introduction, tier 2 after their strongpoint's counterattack has been beaten at the base (one more of its
  component), tier 3 with an Act IV item from the confinement hall (the gatehouse: its reactor control module).
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
  small sites (copper tower, prismarine hall) have theirs in Tune's and Michael's chapters; the stone complex is gone
  from the v8 map and Walker's W-A5 moved to the plant complex's four storage halls. The Woods' In Control rule is design §6.3.
- **A quest may ask for an item only if an earlier quest has handed out its blueprint, or it is a
  loot-only component.** The capability audit that enforces this is `gscraft-crafting.md` §1; it
  closed the boat, the hand tools, firearms, armour and the marker, and broke the W13 ↔ J7 loop.
- **Hand-ins of loot-only components need no "found in raid" tag**: they have no recipe, so the item
  is the proof of the trip.

Quest counts: Walker 27 (6 armoury, 1 boat, 2 military blueprints incl. the mech, 1 Woods), Tony 14 (1 Woods), Michael 18 (1 Woods, 1 small site), Tune 19 (1 Woods, 3 bunkers, 2 sites), James 28 (5 scout, 3 Woods, 3 rail, 2 expedition finds, the Custodian),
Marshall 34 (loop 6, walls 3, farm 3, tower 10, gatehouse 3, Woods 2, the road outpost 1, The Line 6), Teddy 8 (explosives, §7A). One hundred and forty-eight quests in the seven chapters (the three rail quests and Teddy's H8 included), plus the Create chapter's ten (The Gun, §7.6) and the fifteen keeper quests (§7B): 173; the eighteen counter pages (§7C) are not counted; eighteen
of them the `*-B` building tiers. Which of them one outing clears is the trip table in
`gscraft-map-design.md` §3.5; how many outings it takes is up to the players.

---

## 2. Walker the Foreman — Workshop, Garage, Storage

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| W1 | Nuts and bolts | I | Skadowsky's ruins | hand in 8 bolts, 8 nuts | — | a wrench; fastener-kit and hand-tool blueprints; your personal work station is bound (crafting §4) |
| W2 | A place for everything | I | camp | craft and hand in 2 fastener kits | W1 | **Storage 1**: basic backpack recipe, stash crates at the claim |
| W3 | Frame of mind | I | camp, glass tower | hand in 12 metal scrap; show a welding torch | W2 | steel-frame blueprint, **Workshop 1** (IE machine recipes) |
| W4 | The toolbox | I | camp | show a toolbox (crafted) | W3 | Workshop 1 effects; 16 iron ingots |
| W5 | Two miles west | II | **the hempcrete compound**, 2.30 km W over the bridge | hand in 6 spark plugs, 12 metal scrap, 4 motor oil — the compound's drops | W4, J-S1 | stage `novo_looted` (the compound's rung, §9); Marshall R3 opens |
| W6 | Hold the yard | II | the camp gate | stage `novo_held`; stage `novo_defended` (the compound's counterattack beaten at the camp gate, at the end of its fortify clock) | W5, Marshall R3 | **Workshop 2** (motor-assembly and mast-section-kit blueprints); **Storage 2**: iron backpack, stack upgrade ×2, magnet upgrade |
| W7 | Wheels | I–II | camp, the Line's depot | hand in 1 motor assembly, 4 steel frames, 1 car battery | L4 (the depot hands out the motor-assembly blueprint and its chest holds an electric motor), T5, M3 | **Garage 1**: quad and runabout recipes, wheel, fuel-tank, empty-fuel-can and cargo-crate blueprints; a full tank and 2 fuel cans; stage `car_built` when one is crafted |
| W8 | Fuel run | II | camp | hand in 2 fuel cans | W7, M7 | fuel-can refill recipe (at Michael's plant pump, M-B2; Walker's drum rack stores them) |
| W9 | Heavy metal | II–III | the hempcrete compound | hand in 1 heavy diesel engine, 2 motor assemblies | W8, M-B2, `novo_held` | **Garage 2**: van and truck recipes |
| W10 | The big pack | III | the hempcrete compound | hand in a second heavy anchor cable (the compound respawns them while held), 2 fastener kits | W9 | **Storage 3**: gold backpack, **everlasting upgrade** (the secure pack), feeding and pickup upgrades, truck cargo |
| W11 | Mast section kit | II | camp | show 1 mast section kit (6 steel frames + 2 fastener kits + heavy anchor cable) | W6, `skadowsky_held` | the kit is Marshall's X2 hand-in — it patches the mast's cut lattice section so the mast can be climbed |
| W12 | Boats | III | **deferred** — the lake, FR-06 | cross the lake to FR-06 by water (`fr06_by_boat`, §9.1); hand in 1 pressure gauge | W-V1, J-S4 | boat-cargo recipe. FR-06 is deferred, and the plant complex is on Skadowsky's own bank, so the crossing this quest exists for has no live route; kept for the later quest line |
| W13 | Hangar rights | III→IV | camp, the turbine hall — **the runway is retired**: the aircraft is rotary and lifts from the mast field inside the perimeter | hand in 1 avionics module, 2 circuit assemblies | W9, M11 | **Garage 3**: light-helicopter recipe; **Storage 4** opens on J8 (diamond backpack needs the satellite receiver), tank and void upgrades, aircraft cargo |
| W14 | Foreman's pride | IV | everywhere | hand in one of every hardware and tool item (12 items) | W13 | Workshop 3; **the Foreman's Wrench** (an unbreakable, named wrench that fills a station's tool slot without wear) |
| W-A1 | Sidearm | I | camp | hand in 6 metal scrap, 4 screws, 1 fastener kit, 4 planks | W1 | gun-frame, barrel and trigger-group blueprints; pistol, pump-shotgun and their ammunition blueprints; the salvage rule (crafting §5.2) |
| W-A2 | Plates | I–II | camp | hand in 8 metal scrap, 2 duct tape | W3 | plate blueprint; scrap vest and helmet blueprints; rifle ammunition |
| W-A3 | Long guns | II | camp | hand in 2 gun frames, 1 steel frame | W-A1, `novo_defended` | assault-rifle and SMG blueprints; iron sights, extended magazine |
| W-A4 | Precision | III | camp, the plant's switchyard | hand in 1 circuit assembly, 1 military circuit board | W-A3, W9 | sniper and machine-gun blueprints; optics, suppressor (explosives are Teddy's, §7A) |
| W-M1 | Motor pool | III | camp, the turbine hall, the switchyard | hand in 1 military circuit board, 4 plates, 1 heavy diesel engine; stages `fr06_defended` and `financial_defended` | W-A2, W-A4, D4, R5 | **Humvee RWS blueprint** (crafting §2.1; the SW assembling table at yard tier 2 builds it from the kit) |
| W-V1 | Put a motor on it | III | camp, the lake | hand in 1 motor assembly, 1 small battery pack, 2 steel frames | J5, W9, M-B2 | **speedboat** blueprint; boat cargo opens with W12, which is deferred with FR-06 |
| W-B1 | The yard, roofed | I | camp | hand in 8 metal scrap, 4 fastener kits, 16 planks | W2 | **yard tier 1**: roofed workshop, one bay, the lot fenced |
| W-B2 | Second bay | II–III | camp, the hempcrete compound | hand in 4 steel frames, 32 concrete, 1 heavy diesel engine (the compound respawns them while held) | W-B1, `novo_defended` | **yard tier 2**: two bays, gantry crane, fuel rack, lights; vehicle repair at the bay |
| W-M2 | The pilot | IV | camp, the confinement hall | hand in 8 steel frames, 1 large battery pack, 1 reactor control module (the Custodian's wreck is the story) | J-H1, W-B3 | the **PMV01B Core Stone**: the team's one mech (right-click summons it, left-click with the Stone heals it — the mod's rules); no second one exists |
| W-B3 | The shed | IV | camp, the confinement hall | hand in 8 steel frames, 64 concrete, 1 satellite receiver | W-B2, J7, M13 | **yard tier 3**: steel shed, vehicle lift, floodlit lot, truck and helicopter bays (the helicopter lifts from the mast field); light-helicopter blueprint; **UH-60 Black Hawk blueprint** (crafting §2.1) |
| W-A5 | The dump | III | the plant complex's four storage halls, (−888, 167), (−743, 167), (−890, 54), (−775, 54) — the stone complex is gone from the v8 map | reach them (location); kill 15 there; hand in 16 gunpowder | W-A3, J4 | 2 salvage rifles; the powder order yields ×8 instead of ×4 |
| W-A6 | The tower on the hill | III | one of the town's blocks standing at y 118 or above — the town has 4,044 such columns and no single tallest building [needs measurement] | kill its boss (an Apotheosis boss; kill task, stage `boss_tower_1`) | W-A3, J2 | 1 Apotheosis gem, 2 salvage weapons — the Salvaging Table's first customer |
| W-W1 | Timber | II–III | the sawmill | hand in 64 planks, 1 **saw blade** (drops only at the sawmill) | W7, J-W1 | lumber orders (1 log → 8 planks, Quick) and the **timber barricade** for Walls 1 (6 planks + 1 fastener kit) |

---

## 3. Tony the Medic — Medical

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| T1 | Field dressing | I | Skadowsky's ruins | hand in 4 bandages, 2 painkillers | — | med-kit blueprint; the clinic cures infection from now on |
| T2 | Stock the clinic | I | camp | craft and hand in 2 med kits | T1 | **Medical 1**: the clinic revive point — a downed player inside the camp outline is revived by the script after 10 s (PlayerRevive's range is one global value, 6 m; design §4.5); 4 med kits back |
| T3 | Neighbours | I | **the Skadowsky hospital**, 0.34 km due N of the square | hand in 3 blood bags, 4 syringes, 2 antiseptic — the hospital's drops | T2, J-S2 | stage `hospital_looted`; Marshall R2 opens |
| T4 | Take the hospital | I | the Skadowsky hospital | stage `hospital_held` (Marshall's assault won) | T3, Marshall R2 | 8 bandages, 4 antiseptic |
| T5 | Hold the hospital | I–II | the camp gate | stage `hospital_defended` (the hospital's counterattack, fought at the bridge) | T4 | **Medical 2**: reduced death penalty; the med kit cures infection in the field |
| T6 | Analyzer | II | the Skadowsky hospital | hand in 1 medical analyzer | T5 | Medical 2 effects; 4 blood bags |
| T7 | Bio Gen | II | **deferred** — Bio Gen, in the transplanted district | reach Bio Gen (location); hand in 1 surgical kit | T6, J-S1 | surgical-kit use: full revive. Bio Gen is deferred to a later quest line; kept as written |
| T8 | Triage | III | anywhere | stage `revives_3` (three teammate revives, counted by KubeJS) | T5 | 8 med kits |
| T9 | Full power | IV | the confinement hall | hand in 1 military power filter | T6, J7 (T7 is deferred) | **Medical 3** |
| T10 | Ready room | IV | the base | hand in 10 med kits, 4 blood bags at the claim | T9 | finale readiness flag; Marshall X6 opens |
| T-B1 | Four walls | I | camp | hand in 16 planks, 8 bandages, 2 med kits | T2 | **clinic tier 1**: walls, four beds, the med station |
| T-B2 | Surgery | II–III | camp, the Skadowsky hospital | hand in 32 concrete, 1 wiring harness, 1 medical analyzer (the hospital respawns them while held) | T-B1, `hospital_defended` | **clinic tier 2**: surgery room, its own generator, the lit cross; faster revive at the clinic |
| T-B3 | The ward | IV | camp, the confinement hall | hand in 64 concrete, 4 med kits, 1 military power filter | T-B2, T9 | **clinic tier 3**: two storeys, ward, quarantine tent, helipad; full revive at the clinic |
| T-W1 | Foraging | II–III | the hunters' hide, the forest | hand in 8 sweet berries, 4 brown mushrooms, 2 rabbit hide | T2, J-W1 | **poultice** recipe (2 sweet berries + 1 bandage → heals 2 hearts, clears poison; Quick); T7's surgical kit may also come from the wreck's medkit |

---

## 4. Michael the Engineer — Generator, Water

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| M1 | Sparks | I | Skadowsky's ruins | hand in 3 wire spools, 1 power cord, 1 water filter | — | wiring-harness and filter-cartridge blueprints |
| M2 | Lights on | I | camp | hand in 2 wiring harnesses, 1 light bulb | M1 | **Generator 1**: lighting recipes, IE power |
| M3 | Clean water | I | camp, the river | hand in 2 filter cartridges | M2 | **Water 1**: coolant and sealed-tubing blueprints |
| M4 | The refinery | III | **the plant's cooling intake works**, 2.16 km S down the east bank | hand in 4 corrugated hoses, 4 radiator fins, 2 fuel cans — the intake works' drops | M3, J-S3 | stage `plant_looted` (the intake works' rung, §9); Marshall R5 opens |
| M5 | Hold the intake works | III | the camp gate | stage `plant_held`; stage `plant_defended` (the intake works' counterattack, at the base) | M4, Marshall R5 | **Water 2**: biodiesel chain, fuel cans |
| M6 | Pump it | III | the intake works | hand in 1 industrial pump | M5 | cooling-loop blueprint |
| M7 | Fuel for the road | II | camp | hand in 4 fuel cans | M5 | Walker W8 opens; 2 fuel cans back |
| M8 | The turbine hall | III | **the plant's turbine hall**, 2.06 km S down the east bank | hand in 2 relays, 2 electric motors, 1 car battery — the turbine hall's drops | M6, W7, J-S4 | stage `fr06_looted` (the turbine hall's rung, §9); Marshall R5b opens |
| M9 | Hold the turbine hall | III | the camp gate | stage `fr06_held`; stage `fr06_defended` (the turbine hall's counterattack, at the base) | M8, Marshall R5b | **Generator 2**; transformer cores start spawning |
| M10 | Core | III | the turbine hall | hand in 1 transformer core | M9 | generator-kit blueprint |
| M11 | The hangar | III→IV | the turbine hall, the confinement hall | hand in 1 avionics module (the turbine hall); hand in 1 reactor control module (the confinement hall, 1.53 km — the first Act IV trip, by truck down the east bank, crossing no water) | M10 | hangar unlocked; Walker W13 opens |
| M12 | Purification | III | the intake works | hand in 1 purification membrane | M6 | **Water 3** |
| M13 | Full grid | IV | the confinement hall | hand in 1 military power filter, 2 wiring harnesses | M11, J7 | **Generator 3** |
| M-B1 | Under a roof | I | camp | hand in 8 metal scrap, 2 wiring harnesses, 1 filter cartridge | M2 | **plant tier 1**: generator shed, water collector |
| M-B2 | Tank farm | II–III | camp, the intake works | hand in 4 steel frames, 32 concrete, 4 sealed tubing, 1 purification membrane (the intake works respawns them while held) | M-B1, `plant_defended` | **plant tier 2**: tanks, pump house, pipe run to the river, the fuel pump, **the charging station**; fuel cans refill at the pump; battery-pack blueprints (crafting §5.4) |
| M-B3 | The grid | IV | camp, the turbine hall, the confinement hall | hand in 8 steel frames, 1 transformer core, 1 military power filter | M-B2, M13 | **plant tier 3**: wind mast, transformer yard, biodiesel column; the camp lit and powered |
| M-P1 | The wet hall | II | the prismarine hall [needs measurement] | reach it (location); hand in 4 water filters, 2 antifreeze — the hall's drops | M3, J2 | 2 coolant; Tune's first line about the sculk on its floor (finale §3) |
| M-W1 | The cabin's generator | III | the ranger cabin | hand in 1 **portable generator** (found only in the cabin) | M5, J-W1 | the ranger's still: 1 motor oil + 1 empty fuel can → 1 fuel can at the plant's pump (M-B2) |

---

## 5. Tune the Technician — Radio and intel

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| U1 | Static | I | Skadowsky's ruins | hand in 1 circuit board, 2 capacitors, 1 broken radio | — | circuit-assembly blueprint |
| U2 | The map | I | camp | hand in 2 circuit assemblies | U1 | **Radio 1**: shared waypoints, the warning system |
| U3 | Listening post | II | the tower compound — the mast's field, inside the perimeter (the library is **deferred**) | reach it (location); hand in 1 hard drive | U2, J2 | the strongpoint board shows garrison strength |
| U4 | The switchyard | III | **the plant's switchyard and admin block**, 1.09 km S | hand in 2 circuit boards, 2 computer parts, 1 hard drive — the switchyard's drops | U3, W7, J-S5 | stage `financial_looted` (the switchyard's rung, §9); Marshall R4 opens |
| U5 | Hold the switchyard | III | the camp gate | stage `financial_held`; stage `financial_defended` (the switchyard's counterattack, at the base) | U4, Marshall R4 | **Radio 2**: the contested site's whole countdown on the board; antenna-element blueprint |
| U6 | Under the plaza | III | **deferred** — the sewers under Financial Plaza | reach the sewers (location); kill 20 there; hand in 1 encrypted radio | U5 | the board shows which approach the next counterattack uses (the bridge, the east road, or the rail corridor north or south). The plaza and its sewers are deferred to a later quest line; kept as written |
| U7 | Military board | III | the switchyard | hand in 1 military circuit board | U5 | transmitter blueprint |
| U8 | Antennas | III | camp | craft and show 4 antenna elements | U5 | 4 antenna elements back |
| U9 | Array | IV | the confinement hall | hand in 1 phased array element | U8, J8 | antenna-array blueprint; **Radio 3** |
| U10 | Technician's ear | IV | everywhere | hand in one of every electrical item (8) | U9 | Radio 3 effects: the coming attack's composition on the board from the moment the marker is placed |
| U-B1 | Mast up | I | camp | hand in 6 metal scrap, 2 wire spools, 1 circuit assembly | U2 | **shack tier 1**: mast to 24 with a dish, the map wall extended |
| U-B2 | Antenna field | III | camp, the switchyard | hand in 4 steel frames, 4 antenna elements, 1 encrypted radio (the switchyard respawns them while held) | U-B1, `financial_defended` | **shack tier 2**: antenna field, intel desk (the board's countdown readout is Radio 2's, U5) |
| U-B3 | Uplink | IV | camp, the confinement hall | hand in 8 antenna elements, 2 circuit assemblies, 1 satellite receiver | U-B2, U9 | **shack tier 3**: the shack's own mast to 40 with an aviation light, second dish, roof receiver (the sector's mast is Marshall's, §7.3; the board's readouts come from Radio 2 and 3) |
| U-C1 | Copper | II | the copper tower [needs measurement] | reach it (location); hand in 4 relays, 4 wire spools — the tower's drops | U2, J2 | 2 circuit assemblies; the notebook marks the tower as the electrical run |
| U-A1 | Dead quiet | III | the sculk cellar under the town's palace of culture, the broad civic block at (−2650, −2889) [needs measurement] | reach it (location); hand in 1 echo shard from its chests | U5, W-A3 | 1 encrypted radio; stage `ancient_city_1`; Tune: "Whatever is down there is listening." |
| U-W1 | Quiet ground | III | the ranger cabin's high ground | hand in 1 antenna element at the cabin's relay mast (location + hand-in) | U5, J-W1 | the relay: the board shows the Woods sites and the outpost's garrison (`woods_relay`); 2 antenna elements back |
| U-D1 | Go down | I–II | the bunker under the farmstead at (−1712, −1744) [needs measurement] | reach it (location); hand in 1 hard drive from it | U2 | stage `bunker_1`; 2 circuit assemblies; the notebook's "Getting hurt" page notes the dark |
| U-D2 | Deeper | III | the road-range bunkers under the farmsteads at (−2432, −1168), (−528, −2640), (432, −2448) | reach all three (location); hand in 1 encrypted radio | U-D1, W7 | 1 military circuit board |
| U-D3 | The archive | IV | the plant complex's bunker, south down the home (east) bank — no river to cross [needs measurement] | reach it by air (`bunker_east_by_air`); hand in 2 hard drives | U-D2, J7 | 1 satellite receiver (a second source: one fewer hub item to find, design §4.4) |

---

## 6. James the Scout — expeditions

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| J1 | Get your bearings | I | Skadowsky's station and its level crossing | reach both (location) | — | waypoints; a compass and a map |
| J-S1 | Scout: the compound | II | the hempcrete compound, 2.30 km W over the bridge | reach the compound (location); hand in the **compound dossier** (its gatehouse office [needs measurement]) | J1 | stage `novo_scouted`; the board shows the compound's garrison and its component container; Walker W5 opens |
| J2 | The town | II | the town's central square (−2380, −2975), 2.46 km W, and the hempcrete compound (the library is **deferred**) | reach both (location) | J1 | waypoints; the expedition board |
| J-S2 | Scout: the hospital | I | the Skadowsky hospital, 0.34 km due N of the square | hand in the **hospital dossier** (the caretaker's flat in the hospital, placed with the sector's dressing) | J1 | stage `hospital_scouted`; Tony T3 opens |
| J-S3 | Scout: the intake works | III | the plant's cooling intake works, 2.16 km S down the east bank | reach it (location); hand in the **intake-works dossier** (its control room [needs measurement]) | J2 | stage `plant_scouted`; Michael M4 opens |
| J-S4 | Scout: the turbine hall | III | the plant's turbine hall, 2.06 km S | reach the turbine hall (location); hand in the **turbine-hall dossier** (its hall office [needs measurement]) | J-S3, W7 | stage `fr06_scouted`; Michael M8 opens |
| J-S5 | Scout: the switchyard | II | the plant's switchyard and admin block, 1.09 km S | reach it (location); hand in the **switchyard dossier** (the admin block [needs measurement]) | J-S3, W7 | stage `financial_scouted`; Tune U4 opens (J-S5 gates on J-S1, not J-S3, in v8) |
| J3 | Paper trail | II | the town's offices (the library is **deferred**) | hand in 2 folders of documents | J2 | a **valuables bag** (opens to 8 random valuables — loot sheet §7) |
| J4 | The far ring | II–III | the bus depot, the four farmsteads south of the Woods (the settlement is gone from the v8 map — its sector is group `removed` — and Bio Gen is **deferred**) [needs measurement] | reach them (location); the far ones by car | J3, W7 | waypoints; Tony T7 and Walker W12 open — both deferred |
| J5 | Settle in | II | **the settlement is gone from the v8 map**; this quest needs a replacement site inside the routing rule [needs measurement] | hand in 3 valuables found there | J4 | the **boat** blueprint — a hull on the town's slipway; stage `boat_built` when one is built |
| J6 | Runway | III | **deferred and retired** — the runway was never built, and the aircraft is rotary: a helicopter lifts from the mast field inside the perimeter, so Act IV needs no airfield | stand on the runway (location); hand in 1 hard drive | J4 | aircraft prep flag; kept for the later quest line |
| J7 | The reactor | IV | **the confinement hall**, 1.53 km S (roof y 198) | reach the confinement hall (location) — by air from the mast field, or by the east-bank road; no water to cross | W13 | the confinement hall's loot tables switch on |
| J8 | Bring it back | IV | the confinement hall | hand in 1 phased array element, 1 satellite receiver | J7, J-H1 | Tune U9 opens; Storage 4 (W13's diamond pack) unlocks |
| J9 | Every capital | IV | the whole box | reach the town's four microdistricts, (−2088, −1967), (−1937, −2184), (−2337, −1791) and (−2350, −2289) (location) | J7 | a **components crate**: choose any 4 of heavy diesel engine, purification membrane, encrypted radio, medical analyzer (held-site components, never an Act IV item; loot sheet §7) |
| J10 | Cartographer | IV | everywhere | reach every named site on the map (location, 20) | J9 | **the Cartographer's Pack**: a diamond backpack fitted with magnet, everlasting and stack ×3 (the pack's cap), named |
| J-H1 | The custodian | IV | the confinement hall's core | kill **the Custodian** (a Pomkot's Mechs PMB01 the loop script spawns when a player first enters the core; kill task, stage `custodian_dead`; its terrain destruction is denied by `gscraft_mech_griefing.js`) | J7 | the core opens: the phased-array container arms (J8 can be done); 8 emeralds |
| J11 | Every ruin | IV | everywhere | hand in one of each of the forty-two small items | J10 | the Collector analogue: an **inception upgrade** and a second everlasting upgrade — a nested pack that also survives death |
| J-B1 | A flag on it | I | camp | hand in 16 planks, 4 fastener kits, 1 folder of documents | J1, W1 | **lookout tier 1**: platform, ladder, a flag |
| J-B2 | The spotlight | III | camp, the far ring | hand in 4 steel frames, 2 light bulbs, 1 car battery, 3 valuables from the far ring (the settlement is gone) | J-B1, J4 | **lookout tier 2**: 30 tall, a night spotlight (waypoint sharing is Radio 1's); zipline rope and hook orders (crafting §5.7) |
| J-B3 | The cabin | IV | camp, the confinement hall | hand in 8 steel frames, 16 glass, 1 satellite receiver | J-B2, J7 | **lookout tier 3**: 40 tall, glass cabin, telescope, waypoint beacon; every named site marked |
| J-C1 | The capital | III | the town centre (the central square, −2380, −2975), 2.46 km W | reach it by car (`capital_1`, §9.1); hand in 2 folders of documents found there | J4 | 6 emeralds; the capital marked on the board; J9's four microdistricts come later |
| J-C2 | The house in the fog | II–III | the fog house at the Woods farmstead (−2192, −32) [needs measurement] — or either of the Woods' two | reach one (location); the book only says "go at night" | J2 | a Field note; 4 emeralds |
| J-W1 | Into the trees | II–III | the sawmill (south edge), the ranger cabin (high ground) | reach both (location) | J2, W7 | waypoints; the notebook's Woods line; stage `woods_scouted` |
| J-W2 | Two doors down | III | the two Woods bunkers | reach both (location); hand in 1 hard drive from them | J-W1 | stage `woods_bunkers`; 2 circuit assemblies |
| J-T1 | The line | III | the camp's level crossing, the sector's rail yard | walk the rail between the two yards (location, both ends); hand in 16 metal scrap, 4 steel frames — the sleepers and the missing track | S-residential-3, `plant_defended` | stage `train_1`; the level crossing and the yard's points work; the rail yard's loot table switches on (loot §5) |
| J-T2 | Steam up | III–IV | the rail yard, the intake works | hand in 1 boiler (Oksana's, S-plant-2 — pending §7B's re-cut), 8 steel frames, 1 heavy diesel engine | J-T1, S-plant-2 | stage `train_2`; the **locomotive**: Create's steam train, built at the depot; it drives by hand between the two yards |
| J-T3 | The schedule | IV | the rail yard | hand in 2 circuit assemblies, 1 military circuit board; set a schedule between the two stations | J-T2 | stage `train_3`; the schedule block runs the train unattended — the east bank's hauler: a cargo car carries bulky items and components home while the team walks |
| J-W3 | The wreck | III | the downed aircraft | reach it (location); hand in the **flight recorder** (a valuables item found only there) | J-W1 | 1 avionics module (the second source; W13 and the Black Hawk want them) |

---

## 7. Marshall — the loop, the defences, the tower

**Gate to speak:** W1, T1, M1, U1, J1 all done.

### 7.1 The strongpoint loop

Each take is the same shape: the marker is placed at the site's anchor point, the assault runs
for 5 minutes, the marker must survive and a player must be inside the rectangle at the end
(design §6.1). The marker is refused until the site is scouted and looted, and while another site
is still contested — one fight at a time, in this order.

The five sites are the settled ones (`gscraft-skadowsky-camp.md` §11.4): the Skadowsky hospital (Vera),
the hempcrete compound (Kessler), the plant's switchyard (Ilya), its cooling intake works (Oksana) and its
turbine hall (Rook). The ladder stage ids are unchanged — `novo_*` is the compound's rung, `financial_*` the
switchyard's, `plant_*` the intake works', `fr06_*` the turbine hall's — and `residential_*` is renamed
`hospital_*` so the sector and the strongpoint do not share a name (§9).

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| R1 | Muster | I | camp | checkmark; read the strongpoint board | the five introductions | the board and the map wall revealed, the camp's outline lit (B9); the claim-marker blueprint (trip-length order; re-crafted after a failed assault) |
| R2 | The hospital | I | the Skadowsky hospital, 0.34 km due N of the square | place the marker; win the assault (stage `hospital_held`) | R1, `hospital_looted` | the hospital's site guard and its keeper (Vera) appear; the fortify clock starts; Tony T4 opens; the first counterattack is the lightest and is fought at the bridge (enemies §5's Matron leads it) |
| R3 | The compound | II | the hempcrete compound, 2.30 km W over the bridge | place the marker; win the assault (stage `novo_held`) | R2, `hospital_defended`, `novo_looted` | the compound's site guard and Kessler appear; Walker W6 opens |
| R4 | The switchyard | III | the plant's switchyard and admin block, 1.09 km S | place the marker; win the assault (stage `financial_held`) | R3, `financial_looted` | Ilya appears; Tune U5 opens |
| R5 | The intake works | III | the plant's cooling intake works, 2.16 km S | place the marker; win the assault (stage `plant_held`) | R4, `novo_defended`, `truck_built`, `plant_looted` | Oksana appears; Michael M5 opens |
| R5b | The turbine hall | III | the plant's turbine hall, 2.06 km S | place the marker; win the assault (stage `fr06_held`) | R5, `fr06_looted` | Rook appears; Michael M9 opens |
| R6 | Every site | III | all five | all five held and defended at once (stage `all_held`) | R5 | component respawn rate doubled |

### 7.2 Walls, defences, farm, the field

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| D1 | Walls | I | the claim | hand in 32 concrete, 2 fastener kits | R1 | **Walls 1**: sandbag, barbed-wire and claymore orders (crafting §5.7); the timber barricade after W-W1; +2 soldiers at every site guard |
| D2 | Guards | II | the claim | stage `novo_defended` and `hospital_defended` | D1, M-B2 | **Walls 2**: the Recruit's Table at the gatehouse — hire recruits, shieldmen and bowmen with emeralds and food; guard villagers at every NPC building tier 2; drone orders and Create Big Cannons' drop mortar (crafting §5.7 — Superb Warfare's mortar is gone; the Create chapter's gun is the artillery proper); +2 soldiers at every site guard |
| D3 | Farm and kitchen | II | the claim, the collective farm (seeds, bowls; the mud village later) | hand in 16 seeds, 8 bowls, 1 med kit | D1 | **Farmer's Delight kit** (stove, cooking pot, skillet, cutting board, knife; 8 each of rice, tomato seeds, onions, cabbage seeds); **Farm 1**: the kitchen's meals feed the team |
| D4 | Bunker | III | the claim | hand in 64 concrete, 4 steel frames, 1 heavy anchor cable | D2, W9, M9 | **Walls 3**: blast doors, radar, C4 and jump-pad orders (crafting §5.7; the laser tower is replaced by the autocannon nests of G8); armoured-car recipe; +2 soldiers at every site guard |
| D5 | Greenhouse | III | the claim, the intake works | hand in 16 cabbages, 16 onions, 8 cooked meals (Farmer's Delight), 1 industrial pump (irrigation; the intake works respawns them while held) | D3, `plant_defended` | **Farm 2**: greenhouse and irrigation; crops inside the claim grow at double rate (KubeJS random-tick boost) |
| D6 | Rations | III–IV | the claim, the intake works | hand in 32 cooked meals, 1 purification membrane (the intake works respawns them while held) | D5, `plant_defended` | **Farm 3**: hydroponics; the **ration pack** recipe (4 meals → 1 pack, Saturation, stacks 16) — the Act IV run's food |
| D-O1 | The outpost by the road | II | the outpost at the farmstead (−2720, −1072) [needs measurement] | kill 10 pillagers there (kill task, stage `road_outpost_cleared`) | D1, W-A1 | 90 rifle rounds; the outpost stays quiet (the script stops its pillagers respawning) |
| R-W1 | The outpost | III | the bandit outpost | clear it: kill 15 there (kill task, stage `woods_outpost_cleared`); no marker, no contested slot, no site guard, no counterattack — it is not a strongpoint | R4, J-W1 | the outpost's cache (2 salvage rifles, 90 rounds, 4 emeralds); bandits stop spawning in the Woods; **Teddy the Hermit** appears in the outpost's tower (§7A) |
| R-W2 | What the trees heard | IV | the Woods bunkers' lower levels | kill 30 below y 40 in the two bunkers; hand in 1 encrypted radio found there | J-W2, U6 | 1 military circuit board; the Woods page of the notebook completes |

### 7.3 The tower

> **Realigned 2026-09-07** against `docs/gscraft-skadowsky-camp.md`. The camp is in Skadowsky, east of the
> south-west bridge, and the sector's own mast at (−808, −1008) replaced the built radio tower: X1 walks to
> the mast, X2 repairs its cut lattice section. Stages 2–5 are unchanged in count, gating and reward.

**Gate:** the five introductions (R1). X1 opens with Marshall; the stages stay part-gated (owner, 2026-09-04).

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| X1 | The tower | I | the tower compound — the mast's field, x −840…−770 × z −1040…−960, inside the perimeter | walk to the mast at (−808, −1008) (location); checkmark after Marshall's briefing | the five introductions (with R1) | the tower chapter's stage list; the parts rack's five hooks are named |
| X2 | Mast section kit | II | camp | hand in 1 mast section kit | X1, W11 | **stage 1** placed: the cut lattice section is repaired and the mast can be climbed (it already stands, dead, to y 137) |
| X3 | Cooling loop | III | camp, the intake works | hand in 1 cooling loop | X2, M6 | **stage 2** placed |
| X4 | Generator kit | III | camp, the turbine hall | hand in 1 generator kit | X3, M10 | **stage 3** placed; the lights come on |
| X5 | Transmitter | III | camp, the switchyard | hand in 1 transmitter | X4, U7 | **stage 4** placed; the dish |
| X6 | Antenna array | IV | camp, the confinement hall | hand in 1 antenna array | X5, U9, T10, M13 | **stage 5** placed; the beacon lights; the countdown starts; **M3A3 Bradley blueprint** - the finale's armoured vehicle is built during the countdown, not handed over (crafting §2.1) |
| X7 | Hold the line | IV | the base | survive waves 1–4 (stages `wave_1`…`wave_4`) | X6 | between waves: 8 med kits, ammunition |
| X8 | The Sleeper | IV | the base | kill the Sleeper (a named Warden, tag `gscraft_boss`; `gscraft-finale.md`) | X7 | the game's ending; the season flag; the finale chest at the plinth |
| X6b | Relight | IV | camp | repeatable, no hand-in; visible after `finale_failed`, one in-game day later | X6 | restarts the 60-minute countdown; Radio 3 shows the same composition |
| X9 | Afterwards | IV | camp | checkmark | X8 | free play; the board stays live |

### 7.4 The gatehouse

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| R-B1 | A gate | I–II | camp | hand in 32 concrete, 4 steel frames, 2 fastener kits | R2 | **gatehouse tier 1**: the gate at the bridge's east end (x −978…−955 × z −955…−940), wall stubs (the parts rack stands from tier 0) |
| R-B2 | Watchtowers | II–III | camp, the hempcrete compound | hand in 64 concrete, 8 steel frames, 1 heavy anchor cable | R-B1, R3, R4 | **gatehouse tier 2**: walled gate, two watchtowers, barricades; guard villagers at the gate |
| R-B3 | Blast doors | IV | camp, the confinement hall | hand in 128 concrete, 8 steel frames, 1 reactor control module (the confinement hall) | R-B2, X4 | **gatehouse tier 3**: blast doors, floodlights, the board as a lit wall map; the finale's first wave breaks on the gate |

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
| H3 | Old ordnance | III | the outpost, the plant complex's storage halls | hand in 12 powder, 4 steel frames, 1 salvage rifle | H1, W-A5 | **RGO grenade** blueprint; the counter's hand-grenade cap rises from 2 to 4 a day |
| H4 | The tube | III–IV | the outpost | hand in 4 plates, 1 circuit assembly, 20 powder | H3, W-A2 | **M79 grenade launcher** and **40 mm grenade** blueprints; counter LL2 (40 mm rounds) |
| H5 | Backblast | IV | the outpost, the switchyard | hand in 1 military circuit board, 2 steel frames, 30 powder | H4, W-A4 | **RPG-7** and **standard rocket** blueprints; counter LL3 (rockets) |
| H6 | Thermobaric | IV | the outpost, the turbine hall | hand in 1 transformer core, 40 powder | H5 | **TBG rocket** blueprint |
| H8 | The better powder | IV | the outpost, the intake works | hand in 16 nitrate (Oksana's counter, S-plant-2 — pending §7B's re-cut), 8 cotton, 20 powder | H7, S-plant-2 | **nitropowder** and **guncotton** blueprints (crafting §5.8) — the long gun's charges; counter LL4 |
| H7 | The cache | IV | the outpost, the confinement hall | hand in 1 hard drive, 50 powder | H6, J7 | **high-energy explosives** blueprint — Marshall's C4 order takes 1 of them instead of 4 powder, and the HE shell order (G7) 1 instead of 2 powder for a double yield (crafting §5.8) |

Teddy's counter has no building tiers: its loyalty levels are H1, H4, H5 and H8. He buys gunpowder and
powder (vendors doc §4).

---


### 7.5 The Line

> **Realigned 2026-09-07** against `docs/gscraft-skadowsky-camp.md`. The Line reverses: it now runs **west
> over the bridge to the collective farm** at (−2112, −896), 1.17 km. L1 to L6 keep their owners and their
> shapes; only the direction changed.

Marshall's chapter carries the corridor's spine; each stop's own quest sits with its NPC (the L-ids
below are the stops; the NPC's task is in the row). The stops are walked in order because each
building's chest holds the next stop's marker. The corridor is design §2.6: the old power line running
west from the bridge to the collective farm's own substation at the far end. It stays deliberately empty
between stops, and the pylons now lead away from home rather than toward it — the right shape for Act II.

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| L1 | The farmstead | I–II | The Line | reach the farmstead (location); hand in 8 wheat and 4 wild herbs to Tony | J1 | Tony: herb blueprints early; Marshall: D3 opens with the seeds |
| L2 | The pump house | II | The Line | reach it (location); fill 2 filter cartridges at its pump, hand them to Michael | L1, M2 | Michael: **Water 1** if not already held |
| L3 | Substation A | II | The Line | reach it (location); hand in 2 wiring harnesses and 1 relay to Michael | L2 | Michael: the harness kit; the line's power comes on to Substation A (floodlight) |
| L4 | The depot | II | The Line | reach it (location); hand in 12 metal scrap and 2 fuel cans to Walker | L3 | Walker: truck-cab blueprint; the **motor-assembly blueprint** (the first car before the walk west, review fix 5) |
| L5 | Substation B | II | The Line | reach it (location); place a relay mast on its yard | L4, U3 | Tune: the board shows the farm's garrison; power reaches Substation B |
| L6 | The switching station | II | The Line, the farm's west end | clear the checkpoint (kill 8 armed pillagers there); hand in 1 circuit assembly to Marshall | L5 | the farm's own substation lights; **the collective farm opens** at (−2112, −896), 1.17 km |

### 7.6 The Gun (the Create chapter, `gscraft-create-and-artillery.md` §4)

In Marshall's chapter. The first gun is built in the camp — cast in Walker's yard, bored on its hand-cranked frame,
mounted in the gun pit — and fired before a single site is held; the sites scale it up. Nothing about operating it is
ours: laid by rotation, fired by redstone, read on goggles or the pit's display board (interface doc §4.8).

| # | Quest | Act | Area | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| G1 | Sand and iron | II | camp — Walker's yard | hand in 16 casting sand, 8 cast-iron ingots (the hempcrete compound's loot), 4 logs | W-B2, `novo_looted` | the cannon cast and the moulds; the yard's basins pour cast iron |
| G2 | The first pour | II | camp — the yard | pour a cast: one unbored barrel and a cannon end | G1 | stage `gun_cast`; the cast pit's hoist |
| G3 | The bore | II | camp — the yard | bore two barrels and a chamber on the hand-cranked frame (four minutes each) | G2 | stage `gun_bored` |
| G4 | Mount and charge | II–III | camp — the gun pit, the mast field's west edge (x −846…−835 × z −1000…−989) | the cannon mount, hand crank, yaw controller, loader, lever; 8 powder charges, 4 solid shot; **fire it** (CBC's advancement) | G3, Walls 1 | the first gun; stage `gun_fired`; it fires east over 70 blocks of open grass |
| G5 | The gunner's manual | III | the Skadowsky hospital | hand in the manual (Vera, S-residential-1) and 2 spyglasses | S-residential-1, G4 | the range card (a Patchouli book per gun), the pit board, the map wall's rings; stage `gun_range` |
| G6 | Steel | III | Rook's site T2 | 24 steel ingots poured at Kessler's foundry, the cannon builder at Rook's works (both §7B, pending its re-cut) | S-fr06-2, S-novo-2, G5, `fr06_defended` | the long gun, the quick-firing breech; `gun_steel` |
| G7 | Shells | III–IV | Ilya's site T2 | 4 HE, 2 AP, 2 shrapnel; impact and proximity fuzes | S-financial-2, G6 | shells and fuzes as station orders; the smoke shell; `gun_shells` |
| G8 | The battery | IV | Rook's site T3, the gatehouse T3 | a bronze autocannon with handles on each watchtower; an ammo container of AP | S-fr06-3, R-B3 | Walls 3's nests (they replace the laser tower); `gun_battery` |
| G9 | The carriage | IV | Walker T3 | the cannon carriage and a second gun; tow it with the truck | G6, W-B3 | a mobile gun; `gun_carriage` |
| G10 | Nethersteel | IV | the tower | nethersteel (steel + nether material, superheated): the thick chamber | tower stage 4 | the finale's shot — the answer to the fifth wave's vehicle; no gate on the finale; `gun_nethersteel` |

### 7B. The site chains (the Create chapter §3)

Each held strongpoint's keeper gives three quests — Repair, Works, Fortify — and each hand-in places
`gscraft:site_<site>_<tier>` over the site's core building and sets `site_<site>_<n>`. The chain opens when the keeper
appears (`held`) and does not close if the site is later lost (§7.1). Hand-ins follow the camp tiers' rule (design
§3.6): tier 1 camp junk and first intermediates, tier 2 bulk material plus **one more** of the site's own loot-only
component, tier 3 **one Act IV item from the confinement hall**. The keeper's counter opens at tier 1 and grows
with the tier (vendors §3).

> **Deferred, 2026-09-07.** Four of the five chains below were written for sites that are now deferred:
> **S-novo-1…3** (Novo Expograd Industrial Zone), **S-financial-1…3** (Financial Plaza and its sewers),
> **S-plant-1…3** (the industrial district, "the waterworks") and **S-fr06-1…3** (the mega-base FR-06). They
> are kept whole for the later quest line and are **not live act targets**. Their keepers have been re-homed
> inside the routing rule — Kessler to the hempcrete compound, Ilya to the plant's switchyard, Oksana to its
> cooling intake works, Rook to its turbine hall (`gscraft-skadowsky-camp.md` §11.4) — so each chain has still
> to be re-cut against its keeper's new site, and everything that gates on one of them (G6, G7, G8, H8, J-T2)
> is pending that re-cut. **S-residential-1…3 is the one live chain**: it is the Skadowsky hospital's, Vera's,
> and it is corrected below. Its quest ids are unchanged; its ladder stages are `hospital_*`.

| # | Quest | Act | Keeper | Tasks | Gate | Reward |
|---|---|---|---|---|---|---|
| S-residential-1 | Beds again | I–II | Vera, the Skadowsky hospital | hand in 16 planks, 8 cloth, 4 bandages | `hospital_held` | **hospital tier 1**: the ground floor cleared as the field hospital; Vera's counter (LL1); the **gunner's manual** (G5's input) |
| S-residential-2 | The ward | II | Vera | hand in 32 concrete, 4 steel frames, 1 medical analyzer | S-residential-1, T6 | **tier 2**: the upper wards — a second revive point (the camp-revive rule applied to its rectangle, x −865…−698 × z −1312…−1242) and the free infection cure; the stables (horseman and nomad hiring, entities §1.3); LL2 |
| S-residential-3 | The level crossing | III | Vera | hand in 64 concrete, 8 steel frames, 1 satellite receiver | S-residential-2, J7 | **tier 3**: the sector's rail yard depot, the schedule block and the fuel bunker — James's J-T1 opens; the level crossing, the camp's east gate, works; LL3 |
| S-novo-1 | Roof first | II | Kessler, Novo (deferred) | hand in 12 planks, 4 fastener kits, 8 metal scrap | `novo_held` | **Novo tier 1**: the main hall cleared, the yard lit; Kessler's counter (LL1: casting sand, cast-iron nuggets) |
| S-novo-2 | The pour | II | Kessler | hand in 32 concrete, 4 steel frames, 1 heavy anchor cable | S-novo-1, W9 | **tier 2**: the foundry — three basins, the mould bench, four barrels a pour (G6's cast iron); the site guard gains two Recruits; LL2 |
| S-novo-3 | The crane | III | Kessler | hand in 64 concrete, 8 steel frames, 1 military power filter | S-novo-2, J7 | **tier 3**: walled yard, two guard posts, the rope-pulley crane over the cast pit; LL3 |
| S-financial-1 | The lifts | II | Ilya, the plaza (deferred) | hand in 12 planks, 4 fastener kits, 2 circuit assemblies | `financial_held` | **plaza tier 1**: the ground floor cleared, the lifts running; Ilya's counter (LL1: redstone, quartz) |
| S-financial-2 | The fuze lab | II–III | Ilya | hand in 32 concrete, 4 steel frames, 1 military circuit board | S-financial-1, U5 | **tier 2**: mechanical crafters and the fuze bench — G7's shells and fuzes; LL2 |
| S-financial-3 | Shutters | IV | Ilya | hand in 64 concrete, 8 steel frames, 1 satellite receiver | S-financial-2, J7 | **tier 3**: shutters, a lobby guard post, the sewers barred; LL3 |
| S-plant-1 | Relight one | III | Oksana, the waterworks (deferred) | hand in 16 planks, 8 metal scrap, 2 filter cartridges | `plant_held` | **waterworks tier 1**: the pump house cleared, one boiler relit; Oksana's counter (LL1: boiler water, packed gunpowder) |
| S-plant-2 | The power house | III | Oksana | hand in 32 concrete, 4 steel frames, 1 industrial pump | S-plant-1, M6 | **tier 2**: the steam engine on the rebuilt boilers and the shaft run to the **boring mill** — G6's steel barrels bore here in one minute instead of four; the nitrate line (H8's input); LL2 |
| S-plant-3 | The intake | IV | Oksana | hand in 64 concrete, 8 steel frames, 1 military power filter | S-plant-2, J7 | **tier 3**: fence, a guard tower, the water intake fortified; LL3 |
| S-fr06-1 | Clear the hall | III | Rook, FR-06 (deferred) | hand in 16 planks, 8 metal scrap, 4 relays | `fr06_held` | **FR-06 tier 1**: the reactor hall floor cleared, the hangar door freed (a Create sliding door); Rook's counter (LL1: steel plates) |
| S-fr06-2 | The steel works | III | Rook | hand in 32 concrete, 4 steel frames, 1 transformer core | S-fr06-1, M8 | **tier 2**: the cannon builder and the press line for big cartridges — G6's long gun; LL2 |
| S-fr06-3 | The blast wall | IV | Rook | hand in 64 concrete, 8 steel frames, 1 satellite receiver | S-fr06-2, J7 | **tier 3**: blast wall, the roof nest — G8's autocannons; LL3 |

Fifteen quests. The three that follow the rail (James's **J-T1–3**, §6) make the eighteen the count names. Five
items from the confinement hall are spent here: three satellite receivers and two military power filters (loot §6).

### 7C. The counters (the vendor pages)

Eighteen checkmark quests, three per camp NPC (`C-<npc>-1…3`, npc ∈ walker, tony, michael, tune, james, marshall),
one per loyalty level, each unlocked by that NPC's building tier and each **completed by the act of trading once at
that counter**. The body is that level's stock list with its prices — the recipe viewer cannot show villager trades
(vendors §7), so the book is where a player reads what a counter sells before walking to it. They carry no reward
beyond the page itself and are **not counted in the 173**. The five keepers' counters are pages of their own site
chain's quests (§7B) rather than separate quests; Teddy's four levels are H1, H4, H5 and H8 (§7A).

## 8. How the acts feel in play

**Act I (sessions 1–2).** The team wakes squatting in the pocket east of the south-west bridge, holding five Magnum
Torches' worth of quiet ground and nothing else. Five introductions in Skadowsky's own ruins; the personal station,
the first backpack, lights. James sends them to the station and the level crossing to learn the ground. Then north,
on foot, through their own town: the Skadowsky hospital 0.34 km up the road is the one strongpoint in walking range —
its dossier from the caretaker's flat, two or three loot runs for Tony, then Marshall's marker and the assault. The
hospital is held by its site guard and Vera, its fortify clock runs, and its counterattack — the lightest in the game
— arrives at the bridge on schedule. Clearing the sector itself runs alongside on the site ladder
(`skadowsky_scouted` → `looted` → `held` → `defended`): holding it extends spawn suppression to the whole sector and
makes the mast's field camp ground.

**Act II (sessions 3–5).** West over the bridge and south down the bank. The Line is walked out along the pylons to
the collective farm at (−2112, −896), 1.17 km, and its depot hands out the motor-assembly blueprint, so the first car
is built early. Then the hempcrete compound, 2.30 km west — Walker's strongpoint, scouted, looted, taken and held —
and the town's ruins, its east avenue at 1.52 km and its central square at 2.46 km. The first gun is cast, bored and
fired in the pit at the mast field's west edge (G1–G4). The tower chapter, open since the introductions, gets its
first part: W11's mast section kit patches the cut lattice and the mast can be climbed.

**Act III (sessions 6–9).** The plant complex, straight down the home bank with no river to cross — the truck and the
marsh channels are the gate, not a boat. The switchyard and admin block at 1.09 km is Tune's; the turbine hall at
2.06 km and the cooling intake works at 2.16 km are Michael's. They are 1.31, 0.66 and 1.71 km apart, so three
strongpoints in one complex is still three journeys. The sector's rail yard and James's train (J-T1–3) tie the bank
together. The secure pack arrives. Stages 2–4 go up: the tower has power and a dish; the gun gets steel, shells and
the range card. Five sites in the pool means five counterattacks fought and won at the gate, one at a time, and the
map is theirs.

**Act IV (sessions 10–12).** The confinement hall at 1.53 km, roof y 198, the largest ruin on the map: the Custodian,
the phased array element, the satellite receivers and the reactor control module all come out of it, and U-D3's
bunker sits on the same bank. It is reached by the east-bank road, or by helicopter lifting from the mast field
inside the perimeter — there is no airfield and none is needed. The bridge road west to the hempcrete compound is the
other half of the act. The antenna array goes up, the beacon lights. Tony's ready room, Marshall's walls and the
battery decide the finale; the waves come to the base, at the bridge, the east road and the rail corridor; the
Sleeper (`gscraft-finale.md`).

---

## 9. What FTB Quests needs from KubeJS

Stages, all **team** stages (FTB Teams) unless marked *player*, set by the loop script or a quest
reward and read by stage tasks (C3, 2026-09-04):

| Group | Stages |
|---|---|
| Site ladder | `<site>_scouted`, `<site>_looted`, `<site>_held`, `<site>_defended`, `<site>_lost` (the counterattack at the base was lost; the site stays held and the wave returns after the next clock) for `hospital` (the Skadowsky hospital — renamed from `residential_*`, 2026-09-07, so the sector and the strongpoint do not share a name), `novo` (the hempcrete compound), `financial` (the plant's switchyard), `plant` (its cooling intake works), `fr06` (its turbine hall); `all_held`. The home sector runs the same ladder on its own axis — `skadowsky_scouted`, `skadowsky_looted`, `skadowsky_held`, `skadowsky_defended` — and pays out perimeter rather than a keeper: `skadowsky_held` extends spawn suppression from the pocket to the whole sector, makes the mast's field camp ground and unlocks NPC building tier 2; `skadowsky_defended` is the first counterattack, fought at the bridge |
| The Woods and the kept structures | `woods_scouted`, `woods_bunkers`, `woods_outpost_cleared`, `woods_relay`, `bunker_1`, `road_outpost_cleared`, `boss_tower_1`, `ancient_city_1`, `capital_1` |
| Vehicles | `car_built`, `boat_built`, `truck_built`, `aircraft_built` (the aircraft is rotary); the vehicle-qualified location flags `hub_by_air` (the confinement hall), `bunker_east_by_air`, `capital_1` (§9.1). `settlement_by_car` and `settlement_by_boat` are dead with the settlement, and `fr06_by_boat` and `biogen_by_car` are deferred with FR-06 and Bio Gen |
| Function levels | `workshop_1…3`, `garage_1…3`, `storage_1…4`, `medical_1…3`, `generator_1…3`, `water_1…3`, `radio_1…3`, `walls_1…3`, `farm_1…3` |
| Building tiers | `camp_<npc>_<tier>` for the six NPCs, tiers 1–3 |
| The tower and the finale | `marshall_speaks` (the five introductions), `tower_1…5`, `beacon_lit`, `finale_ready` (T10), `wave_1…5`, `finale_won`, `finale_failed`, `season_1_done` |
| Gates and switches | `hangar_unlocked` (M11), `aircraft_prep` (J6, deferred with the runway), `hub_loot_on` (J7, now the confinement hall), `custodian_dead` (J-H1), `teddy_present` (R-W1), `revives_3` (*player*) |
| Blueprints | `bp_<recipe>`, one per recipe in the crafting sheet (the recipe file is the list); the card item is the player's copy, the stage is the team's record (crafting §4) |
| The Gun and the site chains | `gun_cast`, `gun_bored`, `gun_fired`, `gun_range`, `gun_steel`, `gun_shells`, `gun_battery`, `gun_carriage`, `gun_nethersteel`; `site_<site>_1…3` for the five sites; `train_1…3` (J-T) |
| First-time lines (*player*, onboarding §8) | `seen_station`, `seen_bulky`, `seen_infection`, `seen_warning`, `seen_board`, `seen_down` |

Items the script owns: the five dossiers and the claim
marker. The loop script keeps, per site, the fortify deadline, the counterattack flag (cleared on `_lost` so it re-runs), the site guard's target size and owner, and the
component-container state and the single `contested` slot; all clocks count online ticks only. Rewards run commands:
`kubejs stage add`, `function gscraft:tower_stage_N`, `function gscraft:camp_<npc>_<tier>` (the
building tiers, which also re-summon the NPC), a team stage `bp_<recipe>` for blueprints (the book says "blueprint", the mechanism is the stage - crafting §4; the old text: an IE blueprint item
with the `gscraft` category NBT). Location tasks use the site rectangles from the sector and plant-complex maps;
the six NPC building rectangles are locked by the tower-lock script (a list of rectangles, quest
functions exempt), so a `*-B` reward is the only thing that ever changes them; dossier chests are placed by `gscraft:dossiers` and filled by `dossiers_fill` (parked in `build/phase_c/` until the dossier items exist) at the coordinates in `tools/dossiers.json`; the kill tasks are the sewers (U6, deferred), the plant's storage halls (W-A5), the boss tower (W-A6), the road outpost (D-O1), the Woods outpost (R-W1), the Woods bunkers (R-W2), the Custodian (J-H1) and the Sleeper (X8); every other clearing is the assault event, whose
waves use the garrison mob types In Control! spawns at each site.

### 9.1 Vehicle-qualified location tasks (C13)

"By car", "by boat" and "by air" are not FTB Quests task types. The loop script checks, once a second for every online
player, `player.vehicle`: an Immersive Vehicles entity (`mts:*`) or a Superb Warfare vehicle counts as *car* (boat and
aircraft ids are two short lists from crafting §2), and when a player in a qualifying vehicle is inside the target
rectangle the script sets the flag stage (`hub_by_air` — the confinement hall, flown from the mast field —
`bunker_east_by_air`, `capital_1`; `settlement_by_car` and `settlement_by_boat` are dead with the settlement, and
`biogen_by_car` and `fr06_by_boat` are deferred). The quest's task is then a stage task, and the book's text says "by car". A player who walks
there has the location for free but not the flag.
