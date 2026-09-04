# GSCraft Wasteland — What the pack can do that the design does not use yet

Draft 1, 2026-09-03. Every gameplay mod in the pinned set (95 jars, 78 with gameplay content) was
opened and read for blocks, items, entities, structures and recipe types. The design (draft 6),
quests (draft 2) and crafting (draft 1) use about a third of what is there. This is the rest,
ordered by how much it would add for how little it costs, with a recommendation on each.

## 1. Use now — cheap, and they close design holes

| Mod | Capability | Used today | Proposal |
|---|---|---|---|
| **Doomsday Decoration** (1,143 blocks) | wrecked cars and vans by colour and segment, sandbags, fridges, tape recorders, shopping trolleys, street furniture — the whole apocalypse prop set, names in Chinese | not at all | replace the sheet-metal car and bus in `camp_ruins.py` with the mod's wreck segments, and use its sandbags for the checkpoints and the camp tiers. The camp and the NPC buildings should be built from this set; it is exactly the vocabulary the design describes in words |
| **Magnum Torch** (3 blocks) | suppresses hostile spawns in a large radius around a placed torch | not at all (the camp's neutral ground is "a KubeJS rule") | the camp's suppression becomes a physical thing: one torch per NPC building at tier 1, the crater's at Marshall's gate. Players see why the camp is safe, and a torch can be a tier reward |
| **Recruits** (10 entities, 6 tables) | hireable soldiers with ranks — recruit, shieldman, bowman, crossbowman, horseman, nomad, scout, captain, commander — plus **claim and siege** mechanics | parked for a later "Walls" level | this is the garrison the design keeps writing by hand. Marshall's D2 "guards" become Recruits hired at the gatehouse; a held site's defence can station them; the mod's own siege logic is a ready-made attack event to compare against the loop script |
| **Guard Villagers** | armed villager guards that patrol and fight | D2 reward, unimplemented | the NPCs' own protection at tiers 2–3 (a guard at each building) so the six survivors read as a community, not six statues |
| **Zombie Awareness** | mobs hear gunfire and smell blood; noise draws hordes | config carried, not designed with | make it a stated rule: every shot at a site pulls its ambient garrison in. That is why the loot trips are quiet work and the take is loud, and why a suppressor (W-A4) is worth crafting |
| **Mob Factions** | any mobs can be set as factions that fight each other | config carried (mech references stripped) | bandits vs zombies at every site: the ambient garrison fights itself, so a patient team can watch a site thin out before going in. One config file |
| **The Hordes — infection** | zombie hits infect; infection kills unless cured | not designed with | the medical function's reason to exist: Tony's tier 1 cures infection at the clinic, the med kit blueprint at Medical 2 cures in the field. Ties the residential block (blood bags) to the mechanic |
| **Lukis Grand Capitals** (269 structure files) + **Hostile Villages** | replaces vanilla villages, outposts, mansions with large versions; villages spawn hostile | generated in the 10 km box already; never used | the generated capitals are ready-made bandit settlements. James's J9 "every city" should point at them; the loot-site list gains them for free |
| **Underground Bunkers** (50 templates, SCP-themed) | randomly generated bunkers under the world | generated already; never used | dungeons that are not the sewers: mark the ones inside the box on the map page and give U-chapter side quests a reason to go down (a hard drive in a bunker) |

## 2. Use in the systems build — they replace something the design invents

| Mod | Capability | Proposal |
|---|---|---|
| **Superb Warfare — defences** | Laser Defense Tower, Waveforce tower, H/PJ-11 CIWS, Claymore, C4, Mortar, Drone, Sandbag, Barbed Wire, Jump Pad, FuMO25 Fire Control Radar, Aircraft Catapult, Vehicle Deployer | Marshall's Walls 1–3 are these, not "turret-style defences" in the abstract: Walls 1 sandbags + barbed wire + claymores; Walls 2 the mortar and drones; Walls 3 the laser tower and the radar. Each is a station order (crafting §5.7); only the Walls 3 pieces take a strongpoint component |
| **Apotheosis** | boss affixes, the **Boss Spawner** block, Salvaging Table, Reforging / Augmenting tables, gems | the elite in each garrison table and the finale's four Captains (`gscraft-finale.md`) get their affixes here — boss definitions are JSON under `data/<ns>/bosses/`, summoned with `/apoth spawn_boss <id> <rarity>`; the elites are `gscraft:elite_<site>` boss definitions summoned by the loop with `/apoth spawn_boss` (B20: the script spawns the waves, Apotheosis the elite — the command is what the Boss Spawner block calls, so no block is placed); Salvaging is what "salvage" in the crafting doc should literally be — the Salvaging Table in Walker's yard turns loot gear into parts |
| **Immersive Engineering — machines** | crusher, arc furnace, excavator, diesel generator, fluid pipes, wiring, the workbench | Michael's Generator and Water functions are IE's diesel generator and pump; the biodiesel chain (Water 2) is IE's fermenter + refinery; the plant's tier-2 tank farm is real IE tanks. The design says "IE power" — this says which machines |
| **Sophisticated Backpacks — upgrades** | magnet, feeding, everlasting, stack, void, tank upgrades, backpack-in-backpack | Storage 1–4 list the packs but not the upgrades; magnet at Storage 2, feeding at Storage 3 alongside everlasting. Each is a station recipe |
| **ParCool** | zipline hooks and rope, vaulting, wall-runs | ziplines from James's lookout tier 3 and the radio tower platforms; the camp's lookout becomes a fast exit over the rim |
| **Farmer's Delight** | stove, cooking pot, skillet, crops, cabinets | Marshall's D3 "Farm and kitchen" as written; add hunger as the reason the camp needs it — Hordes and long trips make food a real cost |
| **Refurbished Furniture** | 448 blocks of interiors — tables, chairs, kitchens, computers, mailboxes, a **Workbench** | the NPC building interiors at every tier; **its Workbench must be removed** under the station-only rule |
| **sedparties** | party system with xp sharing and 24 configurable elements | the five players are one party from first join; xp sharing keeps everyone at the same Apotheosis level after a split trip |
| **Ping Wheel** | in-world markers for the team | no design needed; mention it in the install guide so the players use it for dossier rooms and marker anchors |

## 3. Already in and quietly load-bearing — say so in the design

| Mod | Why it matters |
|---|---|
| **Custom Starting Gear** | hands the personal station and the starting sidearm to every new player — the first-join moment |
| **PlayerRevive** | revives are Tony's whole chapter (T8 counts three) |
| **Lootr** | per-player loot in every container; its refresh interval is the reason a site can be looted on three trips |
| **In Control!** | the ambient garrison rules of §6.3 |
| **Improved Mobs** | garrisons harden with distance from spawn — the difficulty curve across the three ranges comes for free |
| **Let Me Despawn, Get It Together Drops, chunksending, ModernFix, Canary, FerriteCore** | keep five players and 100 mods playable on 8 GB |
| **FTB Chunks + Teams** | the claim, the team, the shared stage state |
| **Xaero** | the only map; every "reach the site" task assumes waypoints |

## 4. Kept, with a job (owner, 2026-09-03: nothing is cut)

| Mod | Use |
|---|---|
| **vvp, MCSP** (81 military vehicles) | a **military tier** above the civilian garage, crafting §2.1: the MCSP Humvee RWS as Walker's W-M1 blueprint (2026-09-04 addendum), beside Marshall's LAV-150, the vvp UH-60 Black Hawk as the Act IV heavy helicopter (six seats, cargo — the hub run for the whole team), and one armoured vehicle (M3A3 Bradley) as the beacon's reward for the base defence. The rest become **static wrecks at the strongpoints**: dead vehicles (no battery, no fuel) parked as scenery that hold the component containers — FR-06's plaza gets a BMPT and two Strykers, the plant a Typhoon-K convoy, the runway an abandoned Mi-24 — placed at world build by the site dressing pass, immobile until the players learn to build their own |
| **Immersive Weathering** | its **aging** is the camp's tier readout: tier-0 buildings are placed pre-aged (mossy, cracked, rusted), each rebuild is placed clean and left to weather again; its **tallow** (rendered from animal fat) is the camp's candle and torch recipe before Michael's power arrives; frost and icicles are the winter dressing of the north ring; leaf decay keeps the roads clear |
| **AI Improvements, spark, BHStats, WorldEdit** | server tooling, stays; WorldEdit is how an op fixes the visual-pass findings in place (and the reason Phase A needs an op online) |
| **TaCZ fire control extension** | the aim assist is the difference between five players who hit and five who miss at range; kept on, tuned in Phase C with the guns |

## 5. Done on 2026-09-03 (the cheap rows)

- Doomsday Decoration: the eight ruin pieces rebuilt from its wrecks, sandbags, drums, wire and cones
  (`camp_ruins.py` v2; `camp_ruins_clear` removes the v1 blocks first).
- Magnum Torch: ten diamond torches placed by `gscraft:camp_torches`; the camp's suppression is physical.
- Recruits and Guard Villagers: written into D2 and the NPC tiers.
- Zombie Awareness and Mob Factions: stated as rules in design §6.3; the carried configs already do it.
- Hordes: `infectPlayers = true`; Tony's tiers cure it.
- Bandits mod: `enableMod = false` — its random raids contradict the contested-site rule; the jar stays
  for its loot and gear. Neither it nor Pillagers Gun adds an entity: bandits are armed pillagers.
- Lukis Grand Capitals, Hostile Villages, Underground Bunkers: every generated structure in the 10 km
  box counted and positioned in `tools/structures_v6.json` (see the design's loot-site list).

## 5b. Done on 2026-09-04

- **Station-only rule, the recipe half:** `build/kubejs/server_scripts/gscraft_recipes.js` removes every bench recipe (the
  vanilla crafting table, IE's crafting table and Engineer's Workbench, the Refurbished Furniture workbench, Superb
  Warfare's assembling and reforging tables, all eleven Immersive Vehicles benches and the fuel pump), the Superb Warfare
  defence items (Walls 1-3 station orders later), every vvp / MCSP vehicle assembling recipe and the twenty-one Superb Warfare
  vehicles outside the roster, plus TaCZ's gun smith table, Apotheosis' five tables and every Sophisticated Backpacks
  recipe (packs and upgrades are Storage 1-4 orders). The inert crafting table (block interaction) and the station block are Phase C.
- **Improved Mobs by distance:** `Difficulty type = DISTANCESPAWN`, difficulty 0 inside 1.5 km of the camp, 3 from 1.5 km,
  6 from 2.5 km, 10 from 4 km, 15 in the air ring - the three ranges of the design, measured from the world spawn. It was
  GLOBAL (time-based) before, so the "hardens with distance" line in §3 was not true until now.
- **sedparties:** `useFTBTeams = true` - the party is the FTB team; xp share was already on.
- **Lootr:** `refresh_modids = ["gscraft"]`, `refresh_value = 120000` (5 in-game days): the site chests and the hub's component containers that carry `gscraft:` tables refresh on that rhythm — a held site's component containers use the loop's 2-day timer instead (design §6.2); Lost Cities chests stay one-shot per player.
- **Apotheosis:** `Boss Spawn Cooldown` set to its maximum, which stops the mod's random surface bosses; elites come only
  from the loop's `spawn_boss` calls (§2, design §6.3).
- **Install guide:** EMI and Ping Wheel keys added for the players.
- **Military vehicles:** blueprint-gated quest rewards (crafting §2.1) - the strip above removes their default recipes.

Still words, not files: the IV crafting overrides for the civilian roster (the jar's `JSONConfigCraftingOverrides` has
`overrides -> packID -> itemName -> {commonMaterialLists, extraMaterialLists, repairMaterialLists, returnedMaterialLists}` and
a `dumpCraftingConfig` flag, but the dedicated server has never written the file in our runs and `mtsconfig.json` carries no
such key - the file name and trigger are to be found with the game in Phase C), Recruits at the gatehouse, Guard
Villagers per tier, the elite boss definitions, the Salvaging Table in the yard, Sophisticated Backpacks
upgrade gating, ParCool ziplines, Farmer's Delight hunger - all Phase C/D script and template work; the design half of
each is now written (§5c).

## 5c. Done on 2026-09-04 (the gap audit's phase items, design side)

- **Vendors** on vanilla merchant offers (no trade mod, KubeJS has no villager-trade events): `gscraft-vendors.md`.
- **Flashlight / NVG / thermal** audit: nothing for players in the pack; vvp has vehicle NVG/thermal keybinds; a mod is
  recommended for the flashlight (`notes/gscraft-flashlight-and-nvg.md`).

- **Superb Warfare defences** as Walls 1–3 station orders with verified ids (`gscraft-crafting.md` §5.7).
- **Sophisticated Backpacks upgrades** gated per Storage level, ids listed (crafting §5.7); the inception upgrade is J11's reward only.
- **ParCool ziplines**: rope and iron hooks as J-B2 orders; hooks placed by the lookout tier 3 and tower functions (crafting §5.7, camp spec §1).
- **Guard Villagers per tier and Recruits hiring**: counts, tags, the emerald currency (`gscraft-camp-spec.md` §4).
- **Apotheosis elites**: `gscraft:elite_<site>` boss definitions, summoned by command (design §6.3); the finale's Captains the same way (`gscraft-finale.md`).
- **Farmer's Delight**: Farm 1–3 quests (D3, D5, D6), the ration pack (quests §7.2).
- **Hordes infection and PlayerRevive numbers** (design §4.5; `build/phase05/config/playerrevive.json`).
- **Immersive Vehicles override**: still the Phase C in-game find; the fallback is written (crafting §5.7).

## 6. What this changes in the documents

Nothing in draft 6 is contradicted. The six rows of §1 are additions to Phase C and D that use
what is already installed, and the four Superb Warfare / Apotheosis / IE / Backpacks rows of §2 give
names to things the design left as words. The one hard rule that follows: **the Refurbished
Furniture Workbench and every other bench outside Walker's yard are removed from crafting**, or
the station-only rule leaks.

Sources: the pinned mod jars (`build/manifest.json`), read for lang files, `mods.toml`
descriptions, structure folders and recipe types on 2026-09-03.
