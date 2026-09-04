# GSCraft wasteland — the camp's functions, blocks and readouts

*Spec 1, 2026-09-04, for `tools/camp.py` (Phase C, after the visual pass; the runway lights are Phase B). Closes gap audit C5 (function names and what
blocks they are), C9 (flashlight, notebook, runway lights) and the guard/recruit rows of C15.
Rectangles are `tools/pads_camp.json`; the NPC table is design §2.2 and the tiers design §3.6; what
the players are told is `gscraft-onboarding.md`.*

## 1. Functions

All under `build/datapacks/gscraft/data/gscraft/functions/`. Functions take no arguments in 1.20.1,
so every variant is its own file; the loop script (KubeJS) calls them with `server.runCommandSilent`.

| Function | Count | What it does |
|---|---|---|
| `camp_<npc>_<tier>` (npc ∈ walker, tony, michael, tune, james, marshall; tier 0–3) | 24 | inside the NPC's lock rectangle: `fill … air` above the pad from y+1 to y+48, `place template gscraft:camp/<npc>_<tier>` at the rectangle's origin, then `camp_npc_<npc>`, the Magnum Torch at its fixed spot, the building's sign, and from tier 2 the guards (§4). Tier 0 is run when `camp.py` lands (Phase C, after the visual pass). |
| `camp_npc_<npc>` | 6 | `kill @e[type=villager,tag=gscraft_npc_<npc>]`, then `summon minecraft:villager <x> <y> <z> {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomName:'…',CustomNameVisible:1b,Tags:["gscraft_npc","gscraft_npc_<npc>"],VillagerData:{profession:"…",type:"plains",level:2},Offers:{Recipes:[]}}` at the tier's spot (a per-tier coordinate table in `camp.py`) |
| `camp_npcs` | 1 | the six `camp_npc_*` in one call (respawn everything) |
| `board_<site>_<state>` (site ∈ novo, residential, plant, fr06, financial, woods_outpost; state ∈ unknown, scouted, looted, held, defended, lost) | 36 | `fill` that site's 2×3 column on the gatehouse board wall with the state's block (§2); `held` also summons the site's banner on the watchtower (gatehouse tier 2+), `lost` and `defended` swap it |
| `rack_<n>` (n = 1–5) | 5 | summons the fixed item frame on the parts rack holding the complete part of stage n (`summon item_frame … {Facing:…,Fixed:1b,Invulnerable:1b,Item:{id:"gscraft:<part>",Count:1b}}`); `rack_clear` removes all five |
| `camp_signs` | 1 | the six building signs and the three junction road signs (§3); re-run after any tier change |
| `camp_torches`, `camp_ruins`, `camp_ruins_clear`, `dossiers` | exist | unchanged |
| `runway_lights` | 1 | the runway's edge lights (§5) |
| `tower_stage_0…5`, `tower_beacon_dark` | exist / 1 | the tower; the fail-state beacon swap (finale §4) |

`camp_james_3` and `tower_stage_1` also place `parcool:iron_zipline_hook`s (crafting §5.7): the lookout's to the gate,
the tower's 64-metre platform to the crater rim.

The board's clock and the attack composition are **text on signs**, written by the loop script
directly (`data merge block <x> <y> <z> {front_text:{messages:['…']}}`) — no function, since the
text changes every minute.

## 2. The strongpoint board (Marshall's gatehouse)

A wall map 13 wide × 4 high on the gatehouse's inside wall (from tier 0 — R1 reads it before any gatehouse tier; tier 3 lights it), facing the
door. Six columns, one per site in loop order (Novo, block, plant, FR-06, plaza, the Woods' outpost),
each a 2×3 patch of concrete under a hanging sign with the site's name:

| State | Block | Meaning the notebook gives it |
|---|---|---|
| unknown | `minecraft:black_concrete` | "dark — nobody's been" |
| scouted | `minecraft:yellow_concrete` | "James has its dossier" |
| looted | `minecraft:orange_concrete` | "the marker can go down" |
| held | `minecraft:light_blue_concrete` | "ours — the clock is running" |
| defended | `minecraft:lime_concrete` | "ours for good" |
| lost | `minecraft:red_concrete` | "take it back from the marker" |

Above the columns: the **clock sign** (the contested site's countdown, Radio 2), the **composition
sign** (Radio 3), the **contested** lamp (`minecraft:redstone_lamp`, lit while a site is contested —
the script sets `lit=true`). The strength readout (U3's reward) is a row of `minecraft:item_frame`s
holding 1–5 `gscraft:rifle_ammo` under each column, re-summoned by the script.

**Banners:** one `minecraft:white_banner` per held site on the gatehouse watchtowers (tier 2+), the
site's name as `CustomName`; `board_<site>_defended` swaps it for a `lime_banner`, `_lost` removes it.
Team banners are not used (one team).

**The parts rack:** a `immersiveengineering:steel_scaffolding_standard` frame 6 wide against the
gatehouse's outer wall from tier 0, five `minecraft:oak_wall_sign`s naming the hooks (X1's reward
writes them: "MAST", "COOLING", "GENERATOR", "TRANSMITTER", "ARRAY"), and the five fixed item frames
of `rack_<n>`. Empty hooks show the sign only.

## 3. Signs

- **Building signs** (`camp_signs`): an `minecraft:oak_sign` at each door, three lines: the name,
  the role, the one-liner from the onboarding table (e.g. "WALKER / the yard / Bring me anything
  with a thread on it.").
- **Road signs** at the three junctions (Doomsday Decoration's street-sign blocks, ids pinned at
  camp.py time; fallback `minecraft:oak_sign` on a `minecraft:iron_bars` post): "NOVO 1 km →",
  "← PLAZA 2 km", "WOODS ↑ 1.6 km" at the Novo north gate, with a `doomsday_decoration:streetlamp_1`
  at each.

## 4. Guards and recruits (C15)

| Tier | Guard Villagers (`guardvillagers:guard`, iron sword or crossbow, `PersistenceRequired`, patrol point = the building) | Recruits (`recruits:*`) |
|---|---|---|
| gatehouse 1 (R-B1) | — | three unhired at the gate: `recruits:recruit`, `recruits:bowman`, `recruits:shieldman`; the mod's currency set to `minecraft:emerald` in `serverconfig/recruits-server.toml` (emeralds are valuables in the loot tables) |
| every building at tier 2 | 1 per building; 2 at the gate (design §3.6) | D2's Walls 2 lets the team hire; hired recruits follow or hold the gate (the mod's own orders) |
| every building at tier 3 | 2 per building, 4 at the gate — 14 in all | — |

Guards are summoned by the tier function with `Tags:["gscraft_guard_<npc>"]` and killed by the
next tier's function before re-summoning, so counts never drift. Their inventories are not lootable
(Guard Villagers' reputation gate, `guardvillagers-common.toml` default 15).

## 5. Runway lights, flashlight, notebook (C9)

- **Runway lights** (`runway_lights`, Phase B): `doomsday_decoration:floodlight` every 16 blocks
  along both long edges of the runway rectangle (3040…3470 × 2519…2710, layout §3) on 2-block
  `immersiveengineering:steel_scaffolding_standard` posts, plus two at each threshold. They are
  unpowered light blocks, so they are lit from the first night and visible from the settlement road
  (onboarding "Flying"). IE's powered `immersiveengineering:floodlight` is the gatehouse tier 3's
  and Walker's yard tier 3's light, wired to Michael's power.
- **Flashlight**: the pack has no dynamic-light mod and no flashlight item (checked: the jars offer only
  lanterns and IE's flare cartridge). **Dynamic Flashlight 2.1.0** (mod id `flashlight`; Forge 1.20.1, no dependencies; beam visible to other
  players, optional server-side light blocks) was added on 2026-09-04 — research in `notes/gscraft-flashlight-and-nvg.md`.
  The KubeJS Night-Vision item is no longer needed; the battery is the flashlight battery of crafting §5.6, recharged at Michael's charging
  station (M-B2) or with 1 car battery at any station. Night-vision goggles and thermal: `gscraft-vendors.md` §6.
- **Notebook** (`gscraft:survivors_notebook`, Patchouli): `build/patchouli_books/survivors_notebook/`,
  the six pages of onboarding §6; the "Where things are" page's entries are advancement-gated, and
  the loop script grants the advancement when the matching stage is set, so the page grows as sites
  are scouted. Given by Custom Starting Gear; `/give` re-issues it.

## 6. Blocks per tier (families, for camp.py's palettes)

Ids marked † are to be pinned from the jar when the template is written; the rest are verified.

| Family | Tier 0 (aged) | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|
| Structure | `doomsday_decoration` wreck segments†, `minecraft:oak_planks`, `minecraft:cobblestone`, tarps as `minecraft:white_wool` | `immersiveengineering:sheetmetal`†, `minecraft:stripped_oak_log`, `minecraft:oak_planks` | `immersiveengineering:steel_scaffolding_standard`, concrete (`minecraft:gray_concrete`, `light_gray_concrete`) | `immersiveengineering:steel_block`†, `minecraft:iron_bars`, `minecraft:glass`, `minecraft:polished_andesite` |
| Fence / wire | `doomsday_decoration` sandbags†, `superbwarfare:barbed_wire` | `minecraft:oak_fence`, `superbwarfare:sandbag` | `immersiveengineering:steel_fence`†, `superbwarfare:barbed_wire` | `immersiveengineering:razor_wire`† (the inventory's `razorwire`), `superbwarfare:sandbag` |
| Light | `minecraft:torch`, campfire | `minecraft:lantern`, `immersiveengineering:lantern`† | `doomsday_decoration:streetlamp_1`, `doomsday_decoration:floodlight` | `immersiveengineering:floodlight` (powered), `minecraft:redstone_lamp` |
| Storage / props | `minecraft:barrel`, `minecraft:chest`, oil drums† | `immersiveengineering:wooden_barrel`†, `immersiveengineering:crate`† | `refurbished_furniture` tables, chairs, cabinets† | `refurbished_furniture` computers, kitchens† |
| Aging | Immersive Weathering's mossy/cracked/rusted variants placed directly at tier 0 | clean | clean | clean |

Each NPC's specifics (the yard's benches, the clinic's beds and med station, the plant's IE
generator, pump, tanks and charging station, the shack's mast and dish, the lookout's ladder and
spotlight, the gatehouse's doors and board) follow design §3.6 row by row; the Refurbished Furniture
Workbench is never placed (station-only rule). Each tier-1 template carries a **counter** beside the NPC's spot
(Doomsday Decoration vending-machine or shop-counter prop†) — the vendors' visible desk (`gscraft-vendors.md` §7).

## 7. What this asks of the build

- `tools/camp.py`: the 24 templates from these palettes on the `pads_camp.json` rectangles; the
  per-tier NPC spots; the functions of §1 written out (the 36 board functions are a loop in the
  generator).
- `tools/runway_lights.py` → `runway_lights.mcfunction`.
- Custom Starting Gear kit: station, pistol + one magazine, flashlight + one battery, bandage, notebook (onboarding §8).
- `serverconfig/recruits-server.toml` currency; Guard Villagers left at defaults.
