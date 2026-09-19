# GSCraft Wasteland — the loot design

*2026-09-19. Owner: "make a complete loot design now ... verify that the entire loot system functions". This supersedes
`gscraft-loot-tables.md` (sheet 1, 2026-09-04), whose rules it keeps and whose deferred parts it names as deferred. It is
written from the data the game loads, by a script, after `tools/war_phase46.py` passed 13 of 13 on the local server: every
table and every number below is what the server rolled, not what was intended. Local only; nothing here is on live.*

## 1. What the loot system is

Five things, and one rule that ties them: **nothing comes out of the world that nothing uses, and nothing is asked for
that the world does not give.** `tools/itemflow.py --gate` fails if either half breaks; it is check 1 of phase 46.

| Part | Where it lives | Count |
|---|---|---|
| Building tables - what a room of a kind holds | `tools/loot.py` -> `loot_tables/building/*.json` | 9 |
| Site tables - a strongpoint's own, a building table first and the site's signature second | `tools/loot.py` -> `loot_tables/sites/*.json` | 5 |
| The remap - every OTHER mod's chest table becomes one of ours as it loads | `gscraft_loot/remap.json`, `world/LootRemap.java` | 19 rules |
| Bodies and wrecks | `gscraft_drops/*.json` | 78 rules |
| The uses: station orders and quest hand-ins | `gscraft_recipes/recipes.json`, `tools/chapters.py` | 24 orders, 43 quests |

## 2. Rules

1. **Small items are loot; products are not.** No table gives a working gun, armour or an intermediate. A gun comes as
   salvage (`damaged_pistol`, four scrap under a screwdriver); armour is worn by bodies (5% a piece) or a quest's reward.
   The player's guns are Superb Warfare's and only two exist in the slice: the kit's Glock, R0's Marlin.
2. **A building type first, a site second.** A site table rolls one of its base building tables whole, then its signature pool.
3. **One loot system.** No other mod hands out loot: foreign chest tables are replaced (§5) and the global loot modifiers
   that add to chests are switched off (§6).
4. **Everything has a use.** A table entry, a drop or a reward that nothing consumes, wears, fires, eats or places fails the gate.
5. **Bulk is renewable, singles are certain.** What quests consume in bulk also drops from bodies; what a quest needs exactly
   once has a pool of its own (every workshop chest gives one of the mortar's three parts or a welding torch).
6. **Rounds are made, not only found.** Scrap makes casings, gunpowder and solvent make powder, and the two make rounds
   (Marshall's Brass). Soldiers give rounds, gunpowder and tags; five tags buy sixteen rifle rounds, as often as wanted.
7. **Tools are work.** Each of the five hand tools is some order's tool and loses a use an order: the wrench for fastener kits, pliers for
   harnesses, the screwdriver set for circuit assemblies and for stripping pistols and computers, the welding torch for frames, the
   hand drill for the claim marker. All five are orders of the hand-tools card (W1) and rare finds.
8. **Refresh.** Lootr rolls per player; tables under `gscraft:` refresh every five in-game days (`refresh_modids`). A remapped
   foreign table keeps its foreign id, so it is one-shot per player: the map's dungeons and bunkers are found once.

## 3. Building tables

Weights; `(xA-B)` is the stack. Rolls are per chest, per player.

| Table | Rolls | Pool |
|---|---|---|
| `building/apartment` | 2-4 | bandage 15 (x1-2), painkillers 8, canned_goods 20 (x1-3), bleach 6, water_filter 5, cloth 8 (x1-2), light_bulb 6, duct_tape 5, gas_mask_filter 3, handgun_ammo 8 (x4-10) |
| `building/office` | 2-4 | wire_spool 12 (x1-2), power_cord 10, capacitor 12 (x1-2), circuit_board 10, relay 8, computer_parts 5, hard_drive 6, folder_of_documents 8, broken_radio 4, handgun_ammo 8 (x4-10) |
| `building/garage` | 3-5 | bolt 15 (x2-4), nut 15 (x2-4), screw 10 (x2-4), metal_scrap 20 (x2-4), duct_tape 8, silicone_tube 10, spark_plug 8, motor_oil 10, car_battery 6, wrench 2, hand_drill 1, damaged_pistol 2, handgun_ammo 6 (x4-10), solvent 6, mortar_shell 4 (x1-2); **one of** mortar_barrel, mortar_bipod, mortar_base_plate, welding_torch (or nothing, 4 in 8) |
| `building/workshop` | 4-6 | metal_scrap 20 (x2-4), nail 15 (x2-4), screw 15 (x2-4), insulating_tape 8, pliers 3, screwdriver_set 3, pressure_gauge 6, corrugated_hose 8, bolt 12 (x2-4), nut 12 (x2-4), solvent 4, silicone_tube 5, spark_plug 5, motor_oil 5, car_battery 4; **one of** mortar_barrel, mortar_bipod, mortar_base_plate, welding_torch |
| `building/hospital` | 2-4 | bandage 20 (x1-3), painkillers 15, syringe 12, antiseptic 12, blood_bag 4, gas_mask_filter 4, damaged_pistol 1 |
| `building/store` | 3-5 | canned_goods 25 (x1-3), bleach 8, solvent 8, water_filter 8, bandage 8 (x1-2), duct_tape 8, cloth 6 (x1-2), light_bulb 5, handgun_ammo 6 (x4-10) |
| `building/factory` | 3-5 | metal_scrap 25 (x2-5), corrugated_hose 8, pressure_gauge 6, silicone_tube 6, gunpowder 6 (x1-3), solvent 6, motor_oil 5, relay 4, rifle_ammo 5 (x4-10), welding_torch 1 |
| `building/military` | 2-4 | rifle_ammo 12 (x6-14), handgun_ammo 8 (x6-12), gunpowder 8 (x1-3), damaged_pistol 4, gas_mask_filter 6, hard_drive 3, armor_plate 4, mortar_shell 4 (x1-2), medium_rocket_he 3 (x1-2), large_shell_he 2 (x1-2), metal_scrap 10 (x2-4) |
| `building/library` | 2-3 | folder_of_documents 15, hard_drive 4, broken_radio 6, capacitor 8 (x1-2), computer_parts 4, canned_goods 4 |

## 4. Site tables (the five strongpoints, ruling R1)

| Table | Base (rolled whole) | Signature pool |
|---|---|---|
| `sites/hospital` | one of hospital (2), apartment (1), whole | + 1-2 of: blood_bag 12, syringe 12, antiseptic 10, painkillers 8 |
| `sites/krot` | one of garage (1), factory (1), whole | + 1-2 of: spark_plug 15, motor_oil 12, bolt 10 (x2-4), nut 10 (x2-4), car_battery 4 |
| `sites/switchyard` | one of office (1), military (1), whole | + 1-2 of: circuit_board 15, computer_parts 12, hard_drive 8, relay 8 |
| `sites/turbine` | one of military (1), office (1), whole | + 1-2 of: relay 12, car_battery 6, circuit_board 8, capacitor 8 (x1-2) |
| `sites/intake` | one of factory (1), workshop (1), whole | + 1-2 of: corrugated_hose 15, pressure_gauge 10, water_filter 8, solvent 6 |

Four strongpoints stand in the world and each holds containers of its own table: the hospital 20, the switchyard
12, the intake works 12, the turbine hall 12 - at least twice `site.loot_goal`, or the site could never be looted and
claimed (the three plant sites held none until the completeness audit; `tools/war_phase47.py` climbs each by play). `sites/krot`
is written, loads and rolls, and waits for KROT to be a site.

## 5. The remap: every other mod's chest table

A scan of the local world's sixty largest region files counted what the map's containers carry: 255 `simple_dungeon`, 113
Underground Bunkers, 91 Keerdm gun and ammo chests, 29 Lost Cities, 23 `ancient_city`, villages, mineshafts, Apotheosis.
They gave diamonds, enchanted gear and working TACZ guns. Now any table whose path begins `chests/` and is not ours is
replaced as it loads (`LootTableLoadEvent`, at LOWEST priority so nothing another mod adds in the same event survives) by a
reference to the design table of the first rule that matches. Block, entity and gameplay tables are never touched.

| Rule (whole id, first match wins) | Becomes |
|---|---|
| `keerdm_zombie_essentials:chests/abandoned_car_emergency.*` | `building/hospital` |
| `keerdm_zombie_essentials:chests/abandoned_car.*` | `building/garage` |
| `keerdm_zombie_essentials:chests/apartment_bathroom.*` | `building/hospital` |
| `underground_bunkers:chests/underground_bunker/underground_bunker_supply` | `building/store` |
| `lostcities:chests/raildungeonchest` | `building/workshop` |
| `keerdm_zombie_essentials:chests/.*` | `building/military` |
| `underground_bunkers:chests/.*` | `building/military` |
| `apotheosis:chests/chest_valuable` | `building/office` |
| `apotheosis:chests/.*` | `building/military` |
| `lostcities:chests/.*` | `building/apartment` |
| `minecraft:chests/(simple_dungeon|ancient_city.*|nether_bridge|bastion.*|pillager_outpost|woodland_mansion|end_city_treasure|stronghold_corridor|stronghold_crossing)` | `building/military` |
| `minecraft:chests/(stronghold_library|village/village_cartographer)` | `building/library` |
| `minecraft:chests/(abandoned_mineshaft|village/village_(weaponsmith|armorer|toolsmith|mason|fletcher))` | `building/workshop` |
| `minecraft:chests/village/village_(butcher|fisher|shepherd|tannery)` | `building/store` |
| `minecraft:chests/village/village_temple` | `building/hospital` |
| `minecraft:chests/village/.*` | `building/apartment` |
| `minecraft:chests/(shipwreck.*|underwater_ruin.*|buried_treasure|igloo_chest|spawn_bonus_chest|desert_pyramid|jungle_temple|ruined_portal)` | `building/store` |
| `minecraft:chests/jungle_temple_dispenser` | `chests/jungle_temple_dispenser` |
| `[a-z0-9_.-]+:chests/.*` | `building/store` |

**A table defined in a WORLD datapack never reaches that event** (Forge skips it), so the six Keerdm `_vics` overrides in
`build/datapacks/gscraft` point at the design's tables themselves. `/gscraft loot remap <id>` answers where an id goes.

## 6. The global loot modifiers

Forge lets a mod add to any table as it is rolled. Thirty did, into chests: Farmer's Delight (its own `fd_*` tables), Sophisticated
Backpacks (backpacks), Superb Warfare (guns and blueprints), TACZ's injector (guns and ammunition), Apotheosis (affixed gear, gems).
`tools/glm.py <server dir>` writes the datapack's `data/forge/loot_modifiers/global_loot_modifiers.json` with `"replace": true` and
every installed modifier EXCEPT those; the twenty-eight that do not touch chests (straw from grass, hemp, ham from a pig) stay as
their mods wrote them. **Run it again whenever a mod is added or updated**, and deploy the datapack with the jar.

## 7. Bodies and wrecks

`chance (xmin-max)` per kill. A fighter's worn armour also drops at `drops.armour_chance` (0.05 a piece); a gun never.

| File | Body | Rules |
|---|---|---|
| armour | `t_90a` | large_shell_he 0.8 (x2-6), rifle_ammo 0.7 (x20-60), heavy_ammo 0.4 (x10-30), metal_scrap 1 (x6-12) |
| armour | `m_1a_2` | large_shell_he 0.8 (x2-6), rifle_ammo 0.7 (x20-60), heavy_ammo 0.4 (x10-30), metal_scrap 1 (x6-12) |
| armour | `bmp_2` | small_shell_he 0.8 (x2-6), rifle_ammo 0.7 (x20-60), heavy_ammo 0.4 (x10-30), metal_scrap 1 (x6-12), medium_anti_ground_missile 0.3 (x1-2) |
| armour | `bradley` | small_shell_he 0.8 (x2-6), rifle_ammo 0.7 (x20-60), heavy_ammo 0.4 (x10-30), metal_scrap 1 (x6-12), medium_anti_ground_missile 0.3 (x1-2) |
| armour | `ah1f` | medium_rocket_he 0.8 (x2-4), metal_scrap 1 (x4-8) |
| dead | `zombie` | rotten_flesh 0.6 (x1-2), string 0.3 (x1-1), cloth 0.2 (x1-1), gunpowder 0.1 (x1-1), metal_scrap 0.1 (x1-2) |
| dead | `zombie_villager` | rotten_flesh 0.6 (x1-2), string 0.3 (x1-1), cloth 0.2 (x1-1), gunpowder 0.1 (x1-1), metal_scrap 0.1 (x1-2) |
| dead | `husk` | rotten_flesh 0.6 (x1-2), string 0.3 (x1-1), cloth 0.2 (x1-1), gunpowder 0.08 (x1-1), metal_scrap 0.1 (x1-2) |
| dead | `drowned` | rotten_flesh 0.5 (x1-2), string 0.3 (x1-1), cloth 0.2 (x1-1), gunpowder 0.05 (x1-1), metal_scrap 0.1 (x1-2), dried_kelp 0.2 (x1-2) |
| dead | `zombified_piglin` | rotten_flesh 0.6 (x1-2), string 0.3 (x1-1), cloth 0.2 (x1-1), gunpowder 0.1 (x1-1), metal_scrap 0.1 (x1-2) |
| horrors | `bloater` | rotten_flesh 0.8 (x2-4), gunpowder 0.6 (x2-5), solvent 0.3 (x1-2) |
| horrors | `rider` | cloth 0.4 (x1-2), metal_scrap 0.4 (x2-5), handgun_ammo 0.2 (x2-6) |
| nato | `nato_soldier` | dog_tag 0.6 (x1-1), rifle_ammo 0.5 (x4-12), handgun_ammo 0.2 (x3-8), armor_plate 0.15 (x1-1), metal_scrap 0.4 (x2-5), string 0.3 (x1-2), cloth 0.15 (x1-1), gunpowder 0.2 (x1-3) |
| ruaf | `ruaf_soldier` | dog_tag 0.6 (x1-1), rifle_ammo 0.5 (x4-12), handgun_ammo 0.2 (x3-8), armor_plate 0.15 (x1-1), metal_scrap 0.4 (x2-5), string 0.3 (x1-2), cloth 0.15 (x1-1), gunpowder 0.2 (x1-3) |
| scavengers | `scavenger` | metal_scrap 0.5 (x1-4), string 0.4 (x1-3), cloth 0.2 (x1-1), canned_goods 0.2 (x1-1), handgun_ammo 0.15 (x2-6), bread 0.1 (x1-1), bolt 0.25 (x1-2), nut 0.25 (x1-2), nail 0.25 (x1-3), screw 0.25 (x1-3) |

## 8. Station orders

| Order | Card | Tool | In | Out | Class |
|---|---|---|---|---|---|
| `fastener_kit` | card_fastener_kit | wrench | 4 bolt, 4 nut, 4 screw, 4 nail | 1 fastener_kit | intermediate (120 s) |
| `steel_frame` | card_steel_frame | welding_torch | 6 metal_scrap, 1 fastener_kit | 1 steel_frame | intermediate (120 s) |
| `wiring_harness` | card_wiring_harness | pliers | 3 wire_spool, 1 power_cord, 1 duct_tape | 1 wiring_harness | intermediate (120 s) |
| `filter_cartridge` | card_filter_cartridge | - | 1 water_filter, 1 corrugated_hose, 1 bleach | 1 filter_cartridge | intermediate (120 s) |
| `circuit_assembly` | card_circuit_assembly | screwdriver_set | 1 circuit_board, 2 capacitor, 1 relay, 1 wire_spool | 1 circuit_assembly | intermediate (120 s) |
| `med_kit` | card_med_kit | - | 2 bandage, 1 painkillers, 1 antiseptic, 1 syringe | 1 med_kit | intermediate (120 s) |
| `wrench` | card_hand_tools | - | 3 metal_scrap | 1 wrench | equipment (300 s) |
| `pliers` | card_hand_tools | - | 2 metal_scrap | 1 pliers | equipment (300 s) |
| `screwdriver_set` | card_hand_tools | - | 2 metal_scrap, 1 planks | 1 screwdriver_set | equipment (300 s) |
| `hand_drill` | card_hand_tools | - | 4 metal_scrap, 1 wire_spool, 1 duct_tape | 1 hand_drill | equipment (300 s) |
| `welding_torch` | card_hand_tools | - | 4 metal_scrap, 2 silicone_tube | 1 welding_torch | equipment (300 s) |
| `casings` | card_rounds | - | 2 metal_scrap | 16 casings | quick (20 s) |
| `powder` | card_powder | - | 1 gunpowder, 1 solvent | 4 powder | quick (20 s) |
| `claim_marker` | card_claim_marker | hand_drill | 4 steel_frame, 1 circuit_assembly, 1 wiring_harness, 2 cloth | 1 claim_marker | equipment (300 s) |
| `cloth_wool` | - | - | 2 wool | 1 cloth | quick (20 s) |
| `cloth_string` | - | - | 4 string | 1 cloth | quick (20 s) |
| `bandage` | - | - | 2 cloth | 1 bandage | quick (20 s) |
| `sandbags` | - | - | 2 cloth, 4 sand | 4 sandbag | quick (20 s) |
| `mortar_shell` | card_mortar_shell | - | 3 metal_scrap, 2 powder | 2 mortar_shell | intermediate (120 s) |
| `relay` | - | - | 1 wire_spool, 1 insulating_tape, 1 metal_scrap | 1 relay | quick (20 s) |
| `strip_pistol` | - | screwdriver_set | 1 damaged_pistol | 4 metal_scrap | quick (20 s) |
| `salvage_computer` | - | screwdriver_set | 1 computer_parts | 1 circuit_board | quick (20 s) |
| `handgun_rounds` | card_rounds | - | 8 casings, 1 powder | 8 handgun_ammo | quick (20 s) |
| `rifle_rounds` | card_rounds | - | 8 casings, 2 powder | 8 rifle_ammo | quick (20 s) |

## 9. Every item: where it comes from and what uses it

62 registered items. Generated from the data; a `-` in the last column would fail the gate.

| Item | Role | From | Used by |
|---|---|---|---|
| `bolt` | small | garage, workshop, sites/krot, bodies: scavengers | order fastener_kit, W1 |
| `nut` | small | garage, workshop, sites/krot, bodies: scavengers | order fastener_kit, W1 |
| `screw` | small | garage, workshop, bodies: scavengers | order fastener_kit |
| `nail` | small | workshop, bodies: scavengers | order fastener_kit |
| `metal_scrap` | small | factory, garage, military, workshop, bodies: armour, bodies: dead, bodies: horrors, bodies: nato, bodies: ruaf, bodies: scavengers, order strip_pistol | order steel_frame, order wrench, order pliers, order screwdriver_set, order hand_drill, order welding_torch, order casings, order mortar_shell, order relay, W3, brass, square, gatehouse, clinic, crossing, mast |
| `duct_tape` | small | apartment, garage, store | order wiring_harness, order hand_drill |
| `insulating_tape` | small | workshop | order relay |
| `silicone_tube` | small | factory, garage, workshop | order welding_torch |
| `corrugated_hose` | small | factory, workshop, sites/intake | order filter_cartridge |
| `spark_plug` | small | garage, workshop, sites/krot | W4 |
| `motor_oil` | small | factory, garage, workshop, sites/krot | W4 |
| `car_battery` | small | garage, workshop, sites/krot, sites/turbine | W4 |
| `wire_spool` | small | office | order wiring_harness, order circuit_assembly, order hand_drill, order relay, M1 |
| `power_cord` | small | office | order wiring_harness, M1 |
| `capacitor` | small | library, office, sites/turbine | order circuit_assembly, U1 |
| `circuit_board` | small | office, sites/switchyard, sites/turbine, order salvage_computer | order circuit_assembly, U1 |
| `relay` | small | factory, office, sites/switchyard, sites/turbine, order relay | order circuit_assembly |
| `light_bulb` | small | apartment, store | M2 |
| `computer_parts` | small | library, office, sites/switchyard | order salvage_computer |
| `hard_drive` | small | library, military, office, sites/switchyard | U3 |
| `broken_radio` | small | library, office | U1 |
| `folder_of_documents` | small | library, office | J2 |
| `water_filter` | small | apartment, store, sites/intake | order filter_cartridge, M1 |
| `bleach` | small | apartment, store | order filter_cartridge |
| `solvent` | small | factory, garage, store, workshop, sites/intake, bodies: horrors | order powder |
| `gas_mask_filter` | small | apartment, hospital, military | T3 |
| `painkillers` | small | apartment, hospital, sites/hospital | order med_kit, T1 |
| `antiseptic` | small | hospital, sites/hospital | order med_kit |
| `syringe` | small | hospital, sites/hospital | order med_kit |
| `blood_bag` | small | hospital, sites/hospital | T3 |
| `canned_goods` | small | apartment, library, store, bodies: scavengers, reward of M3, reward of J2 | eaten |
| `cloth` | small | apartment, store, bodies: dead, bodies: horrors, bodies: nato, bodies: ruaf, bodies: scavengers, order cloth_wool, order cloth_string | order claim_marker, order bandage, order sandbags |
| `pressure_gauge` | small | factory, workshop, sites/intake | M3 |
| `damaged_pistol` | small | garage, hospital, military | order strip_pistol |
| `wrench` | tool | garage, order wrench (card), reward of W1 | order fastener_kit (tool) |
| `welding_torch` | tool | factory, garage, workshop, order welding_torch (card) | order steel_frame (tool), W3 (show) |
| `pliers` | tool | workshop, order pliers (card) | order wiring_harness (tool) |
| `screwdriver_set` | tool | workshop, order screwdriver_set (card) | order circuit_assembly (tool), order strip_pistol (tool), order salvage_computer (tool) |
| `hand_drill` | tool | garage, order hand_drill (card) | order claim_marker (tool) |
| `fastener_kit` | intermediate | order fastener_kit (card), reward of W4 | order steel_frame, W2, gatehouse, clinic, crossing, mast |
| `steel_frame` | intermediate | order steel_frame (card), reward of W4 | order claim_marker, tube |
| `wiring_harness` | intermediate | order wiring_harness (card) | order claim_marker, M2 |
| `filter_cartridge` | intermediate | order filter_cartridge (card) | M3 |
| `circuit_assembly` | intermediate | order circuit_assembly (card), reward of U3 | order claim_marker, U2 |
| `med_kit` | intermediate | order med_kit (card), reward of T2, reward of T3, reward of H2 | T2 |
| `casings` | intermediate | order casings (card) | order handgun_rounds, order rifle_rounds |
| `powder` | intermediate | order powder (card) | order mortar_shell, order handgun_rounds, order rifle_rounds |
| `card_fastener_kit` | card | reward of W1 | order fastener_kit needs it |
| `card_steel_frame` | card | reward of W3 | order steel_frame needs it |
| `card_wiring_harness` | card | reward of M1 | order wiring_harness needs it |
| `card_filter_cartridge` | card | reward of M1 | order filter_cartridge needs it |
| `card_circuit_assembly` | card | reward of U1 | order circuit_assembly needs it |
| `card_med_kit` | card | reward of T1 | order med_kit needs it |
| `card_hand_tools` | card | reward of W1 | order wrench needs it, order pliers needs it, order screwdriver_set needs it, order hand_drill needs it, order welding_torch needs it |
| `card_powder` | card | reward of tube, reward of brass | order powder needs it |
| `card_rounds` | card | reward of brass | order casings needs it, order handgun_rounds needs it, order rifle_rounds needs it |
| `card_claim_marker` | card | reward of R1 | order claim_marker needs it |
| `claim_marker` | part | order claim_marker (card) | planted at a strongpoint |
| `strike_mortar` | strike | reward of fire_mission | fired |
| `strike_artillery` | strike | reward of fire_for_effect | fired |
| `strike_air` | strike | reward of air_support | fired |
| `card_mortar_shell` | card | reward of tube | order mortar_shell needs it |

## 10. The start area, for one player

180 bound containers (50 apartment, 6 garage, 31 hospital, 27 office, 20 sites/hospital, 12 sites/intake, 12 sites/switchyard, 12 sites/turbine, 10 workshop). The gate holds the design to this:
every non-repeatable quest's needs added up are covered by what one player expects from those containers (or drop from
bodies), and every thing needed once is a nine-in-ten find or better, or the station makes it, or a quest gives it.
`python tools/itemflow.py` prints the table; the tightest rows today:

```
      gscraft:pliers                     the tool of order wiring_harness              85.4%  risky
      gscraft:screwdriver_set            the tool of order salvage_computer            85.4%  risky
```

## 11. Proof: `tools/war_phase46.py` (13 checks, no player)

The gate; the server has exactly the fourteen tables; each building table rolled 4000 times gives every entry, nothing
else, and totals within a third of the weights; each site table gives its signature and its bases and nothing else;
twenty-two foreign tables become design tables and roll nothing but the design; blocks, entities, the jungle dispenser
and our own tables are left alone; every body and wreck rule drops; the server knows all 92 item ids the system names; the
station loaded every order and every card is a quest's to give; a site table fills a real chest; every recorded
container stands as a Lootr container bound to its table; Lootr refreshes
`gscraft`; the quest book reloads clean; no errors. `/gscraft loot roll <table> <n>` is the instrument.

What writing the test found, that reading the data never would have: three dead site tables still in the world's datapack;
the loot modifiers; Immersive Weathering adding a pool in the same load event after ours; Forge not passing datapack
tables to that event; a Lootr container that answers "Modified" to a data merge and keeps its old table; and my own
`chests.py` placing 42 chests twice because it counted standing containers by the text of their command.

## 12. Out of the system, and named as such

- **Component containers** (`gscraft:components/<site>`: the medical analyzer, the diesel engine, the encrypted radio ...). The
  components are not items yet and the refill loop is not written. Sheet 1 §4 and §6 stand as the plan.
- **The deferred sites** of sheet 1 §5-§6 (the hotel, the exchange, the pool, the farm, the Woods, the hub, Bio Gen, the
  sewers): no table of their own. Their containers roll whatever building table the remap or `chests.py` gives them.
- **Reward containers** (the valuables bag, the components crate): with the quests that gave them, which are not in the slice.
- **Emeralds**: no recruit takes them yet, so no table gives them.
- **Shotgun and sniper rounds**: no player gun fires them, so nothing gives them.

## 13. To deploy (not done; live needs the owner's word)

The jar (tables, remap, orders, items, drops, stage advancements); the quest book; **the world datapack**
(`global_loot_modifiers.json`, the six Keerdm overrides, the three dead `sites/*` tables REMOVED from the world's copy); the
client pack (new items' models and names). Then the hospital's containers rebound on live with `chests.py` from live's world.
