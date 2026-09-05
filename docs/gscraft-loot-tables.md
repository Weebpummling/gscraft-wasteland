# GSCraft wasteland — loot tables by building and by site

*Sheet 1, 2026-09-04. Closes gap audit C7 (sites that dropped nothing anyone needs), C8 (the camp
ruins lacked the introductions' items), the loot half of C10 (the valuables bag, the components
crate) and C17 (the hub's economy). Companion to design §4 (the item ladder), quests draft 3 and
crafting draft 1. Every table here is a datapack file under `build/datapacks/gscraft/data/gscraft/loot_tables/`;
the ids below are the file paths. Item ids are the KubeJS items of Phase C (`gscraft:<name>`) unless
they are vanilla.*

## 1. Rules

1. **Small items are loot; products are not.** No table drops a working gun, armour, a vehicle, a
   complete part or an intermediate; Create's metals (zinc and copper ingots, brass sheets — the Create chapter §1) are small items and drop like hardware. Guns drop as **salvage** (`gscraft:damaged_pistol` …), armour
   not at all (crafting §5.5).
2. **Every table is a building type first and a site second.** A chest in a Lost Cities office rolls
   the office table wherever it stands; a chest inside a strongpoint's rectangle rolls the site's
   own table, which is the building table plus that site's signature items.
3. **Loot-only components never sit in ordinary chests.** They spawn in named component containers
   (`gscraft:components/<site>`) that the loop arms on `held` and refills on the component timer
   (design §6.2). At the never-held sites — the hub (§6), Bio Gen, the sewers, the Woods and the bunkers (§5) — the component containers are **shared, not Lootr-instanced** (B29), and the loop script refills them every 5 in-game days, the same rhythm as Lootr's ordinary refresh.
4. **Refresh:** Lootr `refresh_modids = ["gscraft"]`, `refresh_value = 120000` (5 in-game days), so
   every `gscraft:` table refreshes per player on that rhythm; Lost Cities' own tables stay one-shot
   per player. Component containers are never Lootr containers: the loop script refills them (2 in-game days while a site is held, 5 at the never-held sites — rule 3, design §6.2).
5. Two vanilla items join the small-item list (design §4.2): **gunpowder** (Filters and chemicals;
   the stone complex is where it is plentiful) and **emerald** (Valuables; the Recruits' hire currency).

## 2. The camp's ruins (Act I) — `gscraft:ruins/*`

The 24 ruin pieces' chests (`tools/camp_ruins.json`) carry these four tables. Every introduction's
hand-in list is covered here on purpose, at odds that make Trip 1 about 20 minutes for a team of five (fewer players, fewer chests opened per minute, the same 20 minutes each).

| Table | Rolls | Pool (weight) | Covers |
|---|---|---|---|
| `ruins/hardware` (wrecks, the shed) | 3–5 | bolt 20, nut 20, screw 15, nail 15, metal scrap 20, duct tape 8, silicone tube 6, **wrench 2**, pliers 2, screwdriver set 2 | W1 (8 bolts, 8 nuts; the wrench is W1's reward and a rare find here), W-A1's screws, the hand-tool ingredients (crafting §5.3, C2 fix) |
| `ruins/electrical` (the shed, the checkpoints) | 2–4 | wire spool 20, power cord 10, light bulb 10, capacitor 15, circuit board 8, **broken radio 4**, relay 4 | M1 (3 wire spools, a power cord), U1 (a circuit board, 2 capacitors, a broken radio), M2's light bulb |
| `ruins/medical` (the tents) | 2–3 | bandage 25, painkillers 12, antiseptic 8, syringe 6, **water filter 6**, canned goods 10 | T1 (4 bandages, 2 painkillers), M1's water filter, T2's med kits |
| `ruins/mixed` (buses, containers) | 2–4 | any hardware 30, any electrical 20, canned goods 15, **folder of documents 5**, motor oil 5, gunpowder 3, emerald 2 | J-B1's folder, W5's motor oil head start, D1's early junk |

## 3. Building-type tables — `gscraft:building/*`

These override the Lost Cities chest categories and the Keerdm `_tacz` / `_vics` tables (ids pinned
from the jars at Phase C; the `_vics` override already exists in the datapack).

| Table | Rolls | Pool (weight) |
|---|---|---|
| `building/garage` | 3–5 | bolt 15, nut 15, screw 10, metal scrap 20, duct tape 8, silicone tube 10, spark plug 6, motor oil 8, car battery 2, wrench 2, hand drill 1, salvage pistol 2, pistol ammo 6 |
| `building/workshop` | 3–5 | metal scrap 20, nail 15, screw 15, insulating tape 8, pliers 3, screwdriver set 3, welding torch 1, pressure gauge 4, corrugated hose 4 |
| `building/factory` | 3–5 | metal scrap 25, radiator fin 8, corrugated hose 8, pressure gauge 6, electric motor 3, gunpowder 4, salvage rifle 1, rifle ammo 5 |
| `building/office` | 2–4 | wire spool 12, power cord 10, capacitor 12, circuit board 10, relay 8, computer parts 5, hard drive 3, folder of documents 8, emerald 3 |
| `building/apartment` | 2–4 | bandage 15, painkillers 8, canned goods 20, bleach 6, water filter 5, cloth 8 (wool), light bulb 6, duct tape 5, gas-mask filter 3 |
| `building/store` | 3–5 | canned goods 25, bleach 8, antifreeze 6, solvent 6, water filter 8, bandage 8, duct tape 8, pistol ammo 6, shotgun ammo 4 |
| `building/hospital` | 2–4 | bandage 20, painkillers 15, syringe 12, antiseptic 12, blood bag 4, gas-mask filter 4, salvage pistol 1 |
| `building/military` (outposts, checkpoints, bunkers) | 2–4 | rifle ammo 12, shotgun ammo 8, gunpowder 8, salvage rifle 4, salvage shotgun 3, plate-worthy metal scrap 10, gas-mask filter 6, emerald 4, hard drive 3 |
| `building/library` | 2–3 | folder of documents 15, hard drive 4, broken radio 6, capacitor 8, computer parts 4 |

## 4. Site tables — the five strongpoints, `gscraft:sites/<site>`

Each is the matching building table **plus** the site's signature items (the owning NPC's loot quest
asks for exactly these, design §6.1). Rolls 3–5.

| Site | Base table | Signature items added (weight) | Component container `gscraft:components/<site>` |
|---|---|---|---|
| `novo` | garage + factory | spark plug 15, motor oil 12, bolt/nut 10 each, car battery 4 | heavy anchor cable 1, heavy diesel engine 1 (one each per refresh) |
| `residential` | apartment + hospital | blood bag 12, syringe 12, antiseptic 10 | medical analyzer 1 |
| `plant` | factory + workshop | corrugated hose 15, radiator fin 15, fuel can 8, antifreeze 6 | industrial pump 1, purification membrane 1 |
| `fr06` | military + office | relay 12, electric motor 8, car battery 6, circuit board 8 | transformer core 1, reactor control module 1, avionics module 1 |
| `financial` | office + military | circuit board 15, computer parts 12, hard drive 8, emerald 6 | military circuit board 1, encrypted radio 1 |

Dossier chests (`gscraft:dossier/<site>`) hold exactly the dossier item and nothing else, at the
coordinates in `tools/dossiers.json`.

## 5. The small sites that had no job (C7) — `gscraft:small/<site>`

Positions are `gscraft-map-layout-v6.md` §3.1. Rolls 2–4 unless noted.

| Site | Kind | Role now | Table (building base + additions) |
|---|---|---|---|
| **Glass tower** (1.3 km) | office tower | Act I's electrical run: U2's circuit assemblies, M2's bulb | office + light bulb 12, wire spool 12, computer parts 4 |
| **Acacia hall** (1.55 km) | hall with IE wiring | Act I's hardware and the first mechanical items | workshop + spark plug 6, silicone tube 8 |
| **Copper tower** (2.2 km) | the wired tower | **electrical**: Act II's wire and relays for the harnesses; Tune's U-C1 | office + wire spool 20, relay 12, capacitor 10, electric motor 3 |
| **Prismarine hall** (2.2 km) | the wet hall; sculk on its floor | **filters and chemicals** (Michael's M-P1); and the story's first sign of the Sleeper (finale §3) | store + water filter 12, bleach 10, antifreeze 8, solvent 8, computer parts 4 |
| **Hempcrete compound** (2.0 km) | a walled survivor holdout | **medical, hardware and the first seeds** (D3); the fallback transplant site | apartment + hospital, canned goods 15, duct tape 10, Farmer's Delight seeds 6 each, bowl 6, rare tools (wrench, pliers 2 each) |
| **Library** (2.5 km) | the reading room | **valuables**: J3's folders, U3's hard drive | library table as is |
| **Stone complex** (2.9 km) | the spawner dungeon | **the ammunition dump**: gunpowder and salvage (Walker's W-A5) | military + gunpowder 15, rifle ammo 12, salvage rifle 4, salvage shotgun 3, welding torch 1; rolls 3–5 |
| **Mud village** (2.8 km) | farm hamlet | **food and the farm**: D3's seeds and bowls, D5's crops; emeralds | canned goods 20, Farmer's Delight seeds (rice, tomato, onion, cabbage) 10 each, bowl 10, bandage 8, emerald 5 |
| **Bio Gen offices** (3.9 km SE, two groups) | the laboratory | T7's surgical kit; medical analyzers (design §4.4) | hospital + office; component container `components/biogen`: surgical kit 1, medical analyzer 1 per refresh |
| **The settlement** (3.7 km E) | lakeside town | W12's pressure gauge, J5's valuables, J-B2's valuables | apartment + store + garage, pressure gauge 12, valuables (broken radio, computer parts, folder) 6 each, emerald 6 |
| **The sewers** (under the plaza) | dungeon | U6's encrypted radio, dark work | military + cave-spider drops; component container `components/sewers`: encrypted radio 1 per refresh; rolls 2–3 |
| **The Woods** (2.9 km NNE, `gscraft-woods-plan.md`) | wilderness | sixteen quests across the chapters (J-W1 opens it; Teddy's seven at the cleared outpost) | sawmill: planks 20, **saw blade** 1 (only here), motor oil 6; ranger cabin: **portable generator** 1 (only here), canned goods 12, map 4; hunters' hide: rabbit hide 10, sweet berries 15, arrows→ 6 pistol ammo, salvage shotgun 2; downed aircraft: **flight recorder** 1 (only here); component container `components/wreck`: avionics module 1, surgical kit 1 (its medkit); the outpost's cache (R-W1 reward, not a chest): 2 salvage rifles, 90 rounds, 4 emeralds; Teddy's early hand-ins are gunpowder, powder and canned goods (H1–H3); the later ones are parts (quests §7A) |
| **Kept bunkers** (14, structure plan) | dungeons | five in Tune's side chain (U-D1…U-D3), the rest expedition finds | military + hard drive 8; below y 40 a component container `components/bunker` per bunker: encrypted radio 1 per refresh |
| **Lukis capitals, outposts, boss towers, ancient cities, fog houses** | the kept generated structures | J-C1, J9, D-O1, W-A6, U-A1, J-C2 | military + office; emerald 8 |

## 6. The hub — `gscraft:hub/*` (C17)

The hub is never held, so its component containers are shared and refilled by the loop script every 5 in-game days (rule 3), not on the held-site timer.

| Container table | Count in the hub | Yield per refresh | Needed by the game |
|---|---|---|---|
| `hub/phased_array` | 1 | 1 phased array element | 3 (X6 antenna array, U9, J8) |
| `hub/satellite_receiver` | 2 | 1 each | 6 (J8, W-B3, U-B3, J-B3, Storage 4, the Black Hawk) |
| `hub/power_filter` | 2 | 1 each | 4 (T9, M13, T-B3, M-B3) |
| `hub/rare` (ordinary chests) | many | office + military, computer parts 12, hard drive 8, emerald 8 | J9's four capitals share it |

Five components a visit, thirteen needed: **three hub runs** across Act IV's three sessions, one a
session, each about a 20-minute round trip by air with looting (crafting §3). U-D3's satellite receiver (the bunker
chain) saves one of the six. Nothing else in the game asks for a hub item.

## 7. Reward containers (C10)

| Item | Given by | Opens to |
|---|---|---|
| `gscraft:valuables_bag` | J3 | 8 rolls of the Valuables row: broken radio 5, computer parts 5, hard drive 3, folder of documents 5, emerald 6 |
| `gscraft:components_crate` | J9 | a **choice** (FTB Quests choice reward, not a roll) of any 4 of heavy diesel engine, purification membrane, encrypted radio, medical analyzer — held-site components only, never a hub item |
| the outpost's cache | R-W1 | 2 salvage rifles, 90 rifle rounds, 4 emeralds |
| the finale chest | X8 (finale doc §4) | the season flag, the Warium decoration set |

## 8. What this asks of Phase C

- The `gscraft:` items above exist (design §4.2 plus saw blade, portable generator, flight recorder,
  salvage weapons, the poultice, the ration pack, canned goods as a food item, the two containers).
- The Lost Cities and Keerdm table ids to override, read from the jars, listed in `build/datapacks/gscraft/README`.
- `tools/camp_ruins.json` chests bound to §2; the site rectangles to §4 by a KubeJS `LootEvents`
  hook (chest inside rect → site table) or by placing the chests' `LootTable` NBT at world build.
- Lootr config as in mod-capabilities §5b (already set).
