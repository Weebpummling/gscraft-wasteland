# GSCraft Wasteland — mod utilization plan

Draft 1, 2026-09-05. The audit's idle content (`gscraft-mod-utilization-2026-09-05.md`) placed inside the design: the lands and acts of `gscraft-objectives-v8.md` (the newest ruling), design §3–§6, the quests, crafting §5.7, the vendors, Create, interface, camp, enemies and loot docs. Every none / low mod and every medium mod with named idle content has a row. No new mod content: every id was read from the jar's `en_us.json` (Immersive Vehicles: the pack's `jsondefs/`); audit corrections are marked *(corr.)*.

Columns: mod · idle content · hook (act · site · carrier) · player · channel (interface §3) · cost · phase (design §9: B world, C systems, D loop, E finale). "Order line" = a crafting §5.7 row; "furnish entry" = `tools/furnish.json`.

## 1. The camp itself (and the server-wide lines)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| C1 | Superb Warfare, TaCZ | `superbwarfare:target` + `target_deployer`; `tacz:target`, `tacz:statue` | Act I · Walker's yard tier 1 (camp spec §6) · a W-A1 task (quests §2): kill 10 targets on the yard's range; the TaCZ blocks dress it | the first pistol is proven on the range before anyone walks out | block; book task (§4.1) | 3 lines in `camp.py` walker_1; one task | C |
| C2 | Superb Warfare | `medical_kit` (item + deployable entity) | Act II–III · T-B2 (quests §3) · Tony's "field station" card | a heal point set down behind the gate | tooltip | one order line | C |
| C3 | Superb Warfare | `dragon_teeth` | Act III · Walls 3, D4 (quests §7.2) · Marshall's order | concrete teeth on the gate road the Breachers must climb | tooltip; block | one order line | C |
| C4 | TaCZ | `ammo_box` iron / gold / diamond | Act I–IV · Storage 2 / 3 / 4 (W6, W10, W13) · Walker's cards | a box of magazines that rides in the pack | tooltip | three order lines | C |
| C5 | Immersive Engineering | `turret_gun` | Act II · Walls 2, D2, beside the drones · Marshall's order, fed from the plant's tier-2 line (M-B2) | a turret on the wall that takes what the drones miss | tooltip; the turret's own | two order lines (turret, cartridges) | C |
| C6 | Immersive Engineering | `gunpart_barrel` + `gunpart_drum` + `gunpart_hammer` → `revolver` | Act III · W-A4 (quests §2), not the audit's W-A2: the parts drop only from the Militia at FR-06 (enemies §6) · Walker's card: 3 parts + 1 gun frame | the Militia's own sidearm, taken from them | tooltip | one order line | C |
| C7 | IE, Farmer's Delight, Magnum Torch | `cloche`; `rich_soil`; `emerald_magnum_torch` | Act III · Farm 2, D5 (quests §7.2) · a new template `gscraft:camp/farm_2` by the kitchen, function `gscraft:farm_2` | a glass house of cloches on rich soil whose animals are placed, never spawned; the cloche is the "double growth" | block | one template + one function in `camp.py` | C |
| C8 | Refurbished Furniture | `light_electricity_generator`, `light_lightswitch`, `light_ceiling_light` (+ `dark_`) | Act I · Generator 1, M2 "lighting recipes" (quests §4) · Michael's "lighting kit" card | a generator in the shed, a switch by the door, no wiring | tooltip; block | three order lines; electricity on in `refurbished_furniture.server.toml` | C |
| C9 | Doomsday Decoration | `weapon_rack`, `weaponbox`, `ammunitionbox`; `trailergenerator`; `ambulance_1`, `medical_bed`, `stretcher`; `vendingmachine` | Act I · the tier templates (camp spec §6): Walker's tier-1 armoury, Michael's and Tony's tier 0, every counter (vendors §7) | each survivor's place looks like what it is | block | palette lines in `camp.py` (the † ids pinned) | C |
| C10 | Immersive Weathering | `soot`, `charred_log`, `charred_planks` | Act I · the ruin pieces' burnt entries (`camp_ruins.py`; loot §2) | burnt-out wrecks are black, not just called burnt | block | one palette line. `steel_wool` stays in the jar: a 43rd small item breaks J11 | B |
| C11 | Antiblocks | `bright_<colour>` | Act IV · the gatehouse tier-3 lit wall map, R-B3 (design §3.6; camp spec §2) · a tier-3 palette for the 32 `board_*` functions | the board glows in its six colours at night, no power | block | palette swap in `camp.py` (win 5) | C |
| C12 | Chipped (Chisel, Factory Blocks) | seven `data/chipped/recipes/benches/*.json` | the station-only rule (crafting §4) | nothing — the benches never existed | — | seven `event.remove` in `gscraft_recipes.js` | C |
| C13 | Apotheosis | `apotheosis:salvaging` recipes; Village / Garden / Spawner modules; first-join book | Act II · the Salvaging Table, W-B2 (crafting §5.1) · the salvage rule as recipes: damaged gun → gun frame + barrel | a damaged rifle on Walker's table comes apart into the parts the card needs | tooltip; the table's screen | three JSONs in `data/gscraft/recipes/salvaging/`; four lines in `apotheosis/*.cfg` | C |
| C14 | Sophisticated Backpacks | `refill_upgrade`; `deposit_upgrade`, `restock_upgrade` | Act III · W-A4's reward (refill); Storage 3, W10 orders (deposit / restock for the stash crates; gold has three slots, audit §4: choices beside everlasting) | a magazine stack that refills itself; a pack that empties into the crates | tooltip | one reward line; two order lines | C |
| C15 | ParCool | `limitation_imposed`, `permit_*` | Act I · interface §2's cuts made the server's | the dodge and the flip never happen | — | five lines in `parcool-server.toml` | C |
| C16 | FTB Quests | `ftbquests:chest`; `stage_barrier`; Item Filters | Act I–IV · the parts rack (camp spec §2): X2–X6's kits go into the chest; a barrier on the tower compound's gate keyed `tower_1`; filters for the six "any of" hand-ins (D5, D6, J5, W14, U10, J11) | the kit goes in the box at the rack and the mast rises | block | two template blocks; six filters (win 4) | C |
| C17 | Custom Starting Gear | `/csg` (the `brandon3055/CSG` folder is empty) | Act I minute 0 · the kit (onboarding §8; camp spec §7) | five slots on first join | — | one command once the items exist | C |
| C18 | sedparties | `partySize`, `useVanillaTeams` | interface §4.7 | six or more play as one party | — | two lines in `sedparties-common.toml` | C |
| C19 | The Hordes | `/hordes SpawnHordeWave`; the five wave tables | Act I–IV · every counterattack at the gate and every assault (design §6.2–6.3; enemies §4) · the loop script's wave call | the waves walk in from the entry points on their own paths | boss bar (§3.6, unchanged) | six site tables; the call in the loop script (win 2) | D |
| C20 | Improved Mobs | `Stealer / Equipment / Weapon / Enchanting Chance`, `Item Blacklist` | Act I · enemies §8 rows 1–3 | a chest still holds what it rolled; no zombie in netherite | — | five lines in `improvedmobs/common.toml`, before the next test | C |
| C21 | Pillagers Gun | `Bazooka Chance`; the dead flamethrower key | Act I · enemies §8 row 4 | no explosion at the gate | — | one line; strike enemies §3.2's flamethrower sentence | C |
| C22 | Recruits | `ShouldRecruitPatrolsSpawn`; `horseman`, `nomad` | Act IV · patrols off (design §6.2); two horsemen at the lookout from J-B3, summoned by `camp_james_3` | riders at the lookout | entity | one config line; two summon lines | C |
| C23 | Immersive Vehicles | `giveManualsOnJoin`; `generateOverrideConfigs` | Act I · the kit; the vehicle kits (crafting §5.7) | a five-slot kit; a vehicle kit builds the vehicle | — | two lines in `server/config/mtsconfig.json` (win 1) | C |
| C24 | Hostile Villages | `vanillaVillageChance`, `allowVanillaVillagerSpawn` | vendors §2 | no villager but the survivors ever trades | — | two lines in `hostilevillages.json` | C |
| C25 | In Control | `areas.json`, `phases.json` (both `[]`) | Act I–IV · one rectangle per site, per land band and the camp outline (objectives §6; design §6.3); the `contested` phase | difficulty by land, not by ring | — | one file each (win 3) | D |
| C26 | Better Combat | no player melee weapon | Act I · W-A1 · Walker's machete card (iron sword: 3 metal scrap + 1 planks) | a blade for the quiet work | tooltip | one order line | C |
| C27 | Create Big Cannons | `bag_of_grapeshot` | Act II–III · G4 (quests §7.6) · the pit's second shot | the gun's canister round against the Body waves | the mod's own | G4's task gains 2; one order line | D |

## 2. The home bank (the town, the settlement, the runway, the library, the Woods)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| H1 | Immersive Vehicles (MTS Official Pack `jsondefs/`, *corr.*: no lang keys) | 30 poles (`pole_streetlight`, `pole_trafficsignal`, `sign_stop`, `sign_route`…), 16 decors (`crashbarrier`, `trafficcone`, `telephonebooth`, `fuelpump`) | Act I–II · the connectors C2, C4, C5 and the town's avenues (objectives §5) · the road-furniture pass | a dead traffic light on the avenue, a barrier on the lake road | block (§3.2 road signs) | a list in `furnish.json` after `connectors.py` | B |
| H2 | vvp | `mi_8_amtsh` (the design's "Mi-24", audit §4) | Act II · the runway apron (objectives §3; design §2.3) | a dead helicopter the first flight taxis past | entity | one furnish entry | C |
| H3 | vvp | `toyota` | Act III · the Woods outpost, R-W1 (quests §7.2) · the Scavengers' wreck | a truck with a gun on it that will never move | entity | one furnish entry | C |
| H4 | The Man From The Fog | `cassette_recorder_block`, `cassette_1safetyinstructions` | Act II–III · J-C2 (quests §6) · a hand-in task | a recorder on the table; the cassette is what James wanted | tooltip ("Cassette — James wants to hear it"); the book | one task; the recorder is the fog house's own block | C |
| H5 | Underground Bunkers | `underground_bunker_normal / supply / treasure` | Act I–IV · the 14 kept bunkers (loot §5): U-D1, U-D2, J-W2, R-W2, U-D3 | the bunkers' chests roll the military table with the mod's own on top | Lootr glow | one loot row: the three tables alias `building/military` (loot §3) | C |
| H6 | In Control | `areas.json` | Act II–IV · the Woods rule (design §6.3) as one `area` | fewer, quieter dead under the trees | — | one area entry | D |

## 3. The river line (the Line, Skadowsky, the viaduct)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| R1 | Doomsday Decoration | `safe` | Act I · the five dossier containers (`tools/dossiers.json`), first Skadowsky's caretaker's flat, J-S2 (quests §6) | the dossier is in a safe, and a safe reads as the thing worth taking | block | palette swap in `dossiers.py` (win 5); if the safe has no inventory the chest sits in its alcove | C |
| R2 | Mob Factions | `piglin` → `militia`; the ten `recruits:` ids in `civilian` | Act I · Skadowsky watched from the Line's ford, C1 (objectives §5; enemies §2) | the block fights itself before the team goes in; hired soldiers draw fire | — | `MobFactions.toml` (enemies §8 row 5) | C |
| R3 | The Man From The Fog | `break_blocks = true` | Act I on · he stalks the block from the take (design §6.3) against §6.2's "nothing random ever targets a site" | he cannot dig into Vera's hospital | — | one line in `man_config.toml` (ruling: the locks cover the rectangles only) | C |

## 4. The far bank (the rail yard, FR-06, the waterworks)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| F1 | Create | `packager`, `package`, `package_frogport`, the postboxes | Act III–IV · the train J-T1–3 (Create chapter §2; objectives §6): a packager at the rail-yard depot (S-residential-3), a frogport at Skadowsky's station; the keepers' steel and boiler parts ride as packages, bulky components stay in hand (design §4.5) | the train pulls in and a package drops out of the frogport | block; the mod's own | two blocks in `site.py`; J-T2's task | E |
| F2 | MCSP | `ural_green` | Act III · the waterworks, Oksana's site (objectives §2) · `components/plant` in the lorry's bed | the site's parts are in the back of a dead Ural | block (the lid state, interface §5) | one furnish entry, the container block at bed height | C |
| F3 | FTB Quests | `stage_barrier` | Act III→IV · FR-06's hangar door on `hangar_unlocked`, M11 (quests §4) | the hangar is shut until Michael has the module | block | one block in `furnish_fr06.mcfunction` | C |

## 5. The district (Novo, the plaza and the sewers, Bio Gen)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| D1 | vvp | `toyota` | Act II · Novo's yard (enemies §1: the Scavengers') | the same wreck as the outpost: the faction's mark | entity | one furnish entry | C |
| D2 | The Knocker | `knocker_disc` | Act III · `components/sewers` (loot §5) | the one thing down there that is not a part; plays on a jukebox | tooltip | one loot row | C |
| D3 | In Control | `effects.json` (`[]`) | Act III · `minecraft:darkness` inside the sewers' area (design §6.3 "the dark"; U6) | the basement goes black past the first turn | the effect itself | one rule (win 3) | D |
| D4 | Farmer's Delight | `rope`, `safety_net` | Act II–III · the sewers' descent and the plaza's lift shafts before S-financial-1's pulleys (Create chapter §3) | a rope down the shaft, a net at the bottom | block | lines in `furnish_financial.mcfunction` | C |
| D5 | Doomsday Decoration | `shutter_1…5`; `constanttemperatureincubator` | Act II · Bio Gen's lab, T7 (quests §3); the plaza's tier-3 "shutters", S-financial-3 (Create chapter §3) | shutters come down when Ilya fortifies the plaza | block | palette lines in `site.py` financial_3; one furnish entry | C |
| D6 | Create Big Cannons | `wrought_iron_drop_mortar_end`, `drop_mortar_shell` | Act III · Walls 2's mortar returns as Create's: the end poured at Novo's foundry (S-novo-2), the shells at Ilya's lab (G7); D2's card on `gun_cast` | a mortar in the pit for the fields the big gun cannot see | the mod's own | an order line each at Kessler and Ilya; a D2 reward line | E |
| D7 | Create Big Cannons | `timed_fuze` (Ilya sells it, vendors §3; nothing asks for it) | Act III–IV · G7 (quests §7.6) · airburst over the south-east fields, the counterattacks' entry (objectives §6) | a shell bursts over the wave before it reaches the wire | the mod's own | G7's task gains 2 | E |

*(corr.)* 5.11.4 has a `very_small_cast_mould`; the Create chapter's "very small cannon mould" needs only the id.

## 6. The two edges (the hub, the plant complex)

| # | Mod | Idle content | Hook | Player meets | Channel | Cost | Ph |
|---|---|---|---|---|---|---|---|
| E1 | FTB Quests | `stage_barrier` | Act IV · the hub's core gate on `custodian_dead`, J-H1 (quests §6) | the Custodian's yard is walled until it is dead | block | one block in `furnish_hub.mcfunction` | E |
| E2 | Superb Warfare | `dragon_teeth` | Act IV · the plant complex's west gate road, C8 (objectives §5) · dressing | the plant's gate was a checkpoint once | block | a few blocks in one furnish entry | C |
| E3 | Pomkot's Mechs | 200 parts, blueprints, the trader | hub-only by owner ruling (audit §1); no hook; the config and `gscraft_mech_griefing.js` both stay as locks | — | — | — | — |

## 7. The five wins as Phase C tasks

1. **The IV override file.** `G:\GSCraft\server\config\mtsconfig.json`: `generateOverrideConfigs: true`, `giveManualsOnJoin: false`; boot once; copy the dumped `craftingoverrides.json` into `build/phase05/config/`; fill `overrides → pack → vehicle → commonMaterialLists` for crafting §2's roster; set the flag back. The §5.7 fallback is struck.
2. **The wave engine.** Six tables `server/config/hordes/data/hordes/horde_data/tables/gscraft_<site>.json` in `mixed_mobs.json`'s shape, filled from enemies §3–4 and design §6.3 (the waterworks from `drowned`, Novo and the plaza from `illagers`); the loop script (`build/kubejs/server_scripts/gscraft_loop.js`, Phase D's file) issues one `hordes SpawnHordeWave` per wave, with the mod's own arguments, at design §6.3's entry points (finale §2's "backup" becomes the plan).
3. **In Control by area.** `server/config/incontrol/areas.json`: one entry per rectangle from `tools/strongpoints.json` and `tools/pads_camp.json` (sites, sewers, Woods, hub, plant complex, camp outline) and one per land band (objectives §6); `spawn.json` rules reference `area` instead of the rejected `minx/maxx`; `effects.json` the sewers' Darkness; `phases.json` `contested`; Improved Mobs' steps flatten to two.
4. **FTB Quests' own blocks.** `tools/camp.py`: `ftbquests:chest` at the parts rack (marshall_0); `tower_stage_0.mcfunction`: a `stage_barrier` on the compound's gate (`tower_1`); `furnish_fr06.mcfunction`: the hangar door (`hangar_unlocked`); `furnish_hub.mcfunction`: the core gate (`custodian_dead`); six Item Filters in the chapter files.
5. **The lit board and the safe.** `tools/camp.py`: a tier-3 palette (`antiblocksrechiseled:bright_<colour>` per camp spec §2's six states) for the 32 `board_*` functions, selected by `camp_marshall_3`; `tools/dossiers.py`: `doomsday_decoration:safe` at the five `dossiers.json` coordinates (R1's inventory check first).

## 8. Bandits, Lukis Grand Capitals, Waterframes

- **Bandits** — a background jar. Five classes and a `PillagerRaidManager`: no assets, no lang, no loot. `enableMod = false` stays (its raids break design §6.2). "Kept for its loot and gear" (capabilities §5) keeps nothing; removing it is the owner's call (nothing is cut).
- **Lukis Grand Capitals** — *(corr.)* not "none": there is no `mr_lukis_grandcapitals` namespace; the jar replaces `minecraft:village_*`, `mansion` and `pillager_outpost` with its own jigsaws (`revampedvillages`, 444 nbt), which `place_kept.py` places, so the kept outposts and mansion (quests §1) are already its builds. One row: its loot tables (`revampedvillages:pillager_treasure`, `mansion_treasure`, `*_common`) alias `building/military` and `building/office` like H5. J9 stays on the town's quarters (design §2.7).
- **Waterframes** — a background jar: `block.waterframes.big_tv` exists but WaterMedia is not on the clients (audit §0). When it ships, one line in `camp.py` tune_3 puts the `big_tv` on static (Phase E).

## 9. Everything the plan adds

| Kind | What | Goes into |
|---|---|---|
| Quest tasks | W-A1: kill 10 `superbwarfare:target` (C1); J-C2: hand in `man:cassette_1safetyinstructions` (H4); G4: + 2 `bag_of_grapeshot`, G7: + 2 `timed_fuze` (C27, D7); J-T2: collect a package at Skadowsky (F1) | quests §2, §6, §7.6, §7B; Create chapter §2, §4 |
| Quest reward | W-A4: `refill_upgrade`, the revolver card (C14, C6); D2: the drop-mortar card (D6); D5: farm_2 (C7); M2: the lighting kit (C8); T-B2: the field station (C2) | quests §2, §7.2, §4, §3 |
| Item filters | D5, D6, J5, W14, U10, J11 (C16) | the chapter files; quests §9 |
| Order lines | field station; dragon teeth; three ammo boxes; gun turret + cartridges; revolver; lighting kit ×3; deposit, restock; machete; grapeshot; drop-mortar end (Kessler), shell (Ilya) | crafting §5.7 |
| Salvaging recipes | damaged pistol / shotgun / rifle → gun frame + barrel (C13) | crafting §5.1; `data/gscraft/recipes/salvaging/` |
| Loot rows | bunker tables → `building/military` (H5); Lukis tables → `military` / `office` (§8); `knocker_disc` in `components/sewers` (D2) | loot §3, §5 |
| Templates / functions | `camp/farm_2` + `gscraft:farm_2`; the yard range; the board's tier-3 palette; horsemen at `camp_james_3`; the Quest Chest and three Stage Barriers; `site.py`: depot packager, station frogport, plaza shutters | camp spec §1, §6; Create chapter §3 |
| Furnish entries | Mi-8, two Toyotas, the Ural container, Bio Gen's incubator, the plant's dragon teeth, the sewers' rope and net, the road furniture | `tools/furnish.json`; design §2.7 |
| Rules | In Control `areas.json` (sites, lands, camp), `effects.json` sewers Darkness, `phases.json` contested (C25, D3, H6); six Hordes site tables and the loop's `SpawnHordeWave` call (C19) | enemies §4, §8; design §6.3; finale §2 |
| Config lines | ParCool, Improved Mobs, Pillagers Gun, Mob Factions, Recruits, mtsconfig, Hostile Villages, Apotheosis, sedparties, the fog man, Refurbished electricity — 25 lines | enemies §8; audit §2 |
| Rulings asked | the fog man (R3); the revolver at W-A4 (C6); the drop mortar as Create's (D6); the Lukis loot row (§8) | owner |

Hooks by land: the camp 27, the home bank 6, the river line 3, the far bank 3, the district 7, the two edges 3 — 49, plus the three §8 verdicts.

## 10. Rulings (2026-09-05, from decisions already taken the same day)

| Asked | Ruling | Where it lands |
|---|---|---|
| R3 the fog man's `break_blocks` | **false** — `gscraft-entities-v8.md` §8 C8 (the farmsteads are not locked) | `config/man_config.toml` |
| C6 the revolver card at W-A4 | **yes** (the parts only drop from the Militia on the far bank, Act III) | crafting §5.2, quests W-A4 |
| D6 the drop mortar as Create's | **yes, as a Walls 2 order** — it is Create Big Cannons' own piece, loaded by hand and fired by redstone, so it keeps the "no direct control" rule (create chapter §4); the line "no mortar" in crafting §5.7 and quests D2 now reads "no Superb Warfare mortar" | crafting §5.7, quests §7.2 |
| the Lukis loot row | **void** — v8 has no generated structures inside the cell (design §2.3), so no kept outpost or mansion exists to carry its tables; Lukis stays a background jar | — |
| C19 the wave command | the literal is `/hordes spawnWave <n>` (`SpawnHordeWave` is the class); it is **test T1** of the entities doc before the loop relies on it | `gscraft_loop.js` |
| C22 the lookout's riders | placed scouts at James's tier 3 as written; **hiring** horsemen and nomads happens at Skadowsky's stables (entities §1.3) | camp spec §1, quests J-B3, S-residential-2 |
| E3 the mechs | superseded: the Machines are a faction on the two edges (`gscraft-entities-v8.md` §2–§3); the hub-only rule stands for the ambient, the plant complex gets its turrets and the Overseer | entities §4 |
