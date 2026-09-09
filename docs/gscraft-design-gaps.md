# GSCraft Wasteland — Design gap audit (2026-09-04)

Every design document read against every other: `gscraft-map-design.md` (design), `gscraft-quests.md`
(quests), `gscraft-crafting.md` (crafting), `gscraft-mod-capabilities.md` (modcaps),
`gscraft-structure-plan.md` (structure), `gscraft-woods-plan.md` (woods), `gscraft-onboarding.md`
(onboard), `gscraft-map-layout-v6.md` (layout), `gscraft-map-review-v6.md` (review),
`notes/gscraft-scale-and-travel.md` (scale), `HANDOFF.md`. Result: 53 contradictions, 24 dangling
references, 28 missing systems. Triage: **A** fixed in this pass (mechanical, one right answer);
**B** owner decision, with the default this document recommends; **C** belongs to a build phase and
now has one.

**Standing note, 2026-09-07 — read this before any row below.** The camp is **in Skadowsky**, the pocket east of the
south-west bridge, at x −978…−770 × z −1060…−845, with the world spawn at the paved junction (−940, −979), ground y 65.
It is not on a plateau; both plateau camp rectangles are dead and nothing was ever built on either (H7). Every distance
in this ledger that was measured from the plateau camp centre is dead with it, and the tower is Skadowsky's own mast at
(−808, −1008), not a build. Quests and gameplay route **only** to the Pripyat base map, the Skadowsky sector and the
KROT; eight places named throughout the rows below are **deferred to a later quest line** and no quest
may point at any of them — the Novo Expograd Industrial Zone, the Financial Plaza and the sewers, the Bio Gen offices,
the desert city hub, the mega-base / FR-06, the industrial district ("the waterworks"), the library and the runway.
Where a row names one of them, the row is deferred with it rather than deleted, so the later quest line can pick it up.
The settlement is gone from the map. Authority: `docs/gscraft-skadowsky-camp.md`.

## A. Fixed in this pass (stale facts, one right answer)

| # | Gap | Fix applied |
|---|---|---|
| A1 | Novo stale at "1.5 km S / substation pad" in design, quests (W5 "South, a mile", "sends them south"), onboard | 1.06 km ENE on the spine everywhere; W5 retitled "East, a mile" *(2026-09-07: dead. The distance was measured from the plateau camp centre, and the Novo Expograd Industrial Zone is now deferred to a later quest line — no quest points at it, so W5 and the design's Novo lines are deferred with it and are not re-measured from the Skadowsky camp)* |
| A2 | Financial Plaza stale at "2.5 km SE / hospital pad"; "sewers later under the hospital pad"; review Phase A item about the plaza's causeway; boat "the plaza before its road" | 2.1 km W, dry, one road; the stale lines corrected or struck *(2026-09-07: dead for the same reason as A1 — measured from the plateau camp centre, and the Financial Plaza and its sewers are deferred to a later quest line. Not re-measured from the Skadowsky camp)* |
| A3 | Radio tower stale at "2.1 km E", origin (2066, 64, −141), a district → tower road, "the radio mast not visible from home" | the camp NE corner, origin (107, 100, −101); tower road dropped; the mast is the first thing seen *(2026-09-07: superseded. There is no tower to build and no tower pad. The tower is Skadowsky's own mast at (−808, −1008), standing on a building whose roof is y 104, inside the camp perimeter — so "the mast is the first thing seen" holds, and there is no tower road to drop)* |
| A4 | Distances disagree by document: hub 6.0/6.2/6.18, settlement 3.6/3.7, plant 2.3/2.4, Bio Gen 3.9/4.0 | one set from the layout sheet (measured from the camp centre): Novo 1.06, residential 2.0, plant 2.3, FR-06 2.45, plaza 2.1, settlement 3.7, runway 3.9, Bio Gen 4.0, hub 6.2 *(2026-09-04: the layout sheet §3.1 now reads hempcrete 2.0, plant 2.4, residential 1.9, Bio Gen 3.9)* *(2026-09-07: the whole set is dead — every figure in it was measured from the plateau camp centre. Measured from the camp square (−940, −979): the hospital 0.34, the plant switchyard 1.09, the collective farm 1.17, the confinement hall 1.53, the town's east avenue 1.52, the plant turbine hall 2.06, the plant intake works 2.16, KROT 2.30, the town centre 2.46, the runway 2.85, the library 3.16. Within the plant: switchyard → turbine hall 1.31, turbine hall → intake works 0.66, switchyard → intake works 1.71. Novo, the plaza, Bio Gen, FR-06, the hub, the runway and the library are deferred to a later quest line; the settlement is gone)* |
| A5 | Quest total 77 (design, HANDOFF) vs 105 (quests) vs 106 (crafting); Walker 22 vs 23 rows | 106 quests, Walker 23, everywhere *(138 after the C items, the placed-structure quests, Teddy's chapter and the mech quests — 2026-09-04)* |
| A6 | Small items "~30" and J11 "the thirty small items" vs 40 in the catalogue | 40 *(42 after the C items: gunpowder, emerald)* |
| A7 | Bio Gen footprint 64×256 vs two groups | two groups, 64×64 and 16×32 |
| A8 | Tune's shack x 60…75 vs moved to x 40…55 | 40…55 (design table) |
| A9 | Design §2.4 roads list (district → Novo, district → tower, Novo may move) vs the built roads | §2.4 points at layout §4: spine via Novo, camp → plaza, district → runway, district → settlement *(2026-09-07: dead. Every road in that list either serves a site deferred to a later quest line — Novo, the plaza, the runway — or the settlement, which is gone. The camp's own two roads are the south-west bridge, x −1104…−981, deck z −957…−936 at y 89, as the west gate, and the rail embankment's level crossing as the east gate; the rest of the v8 road list `[needs measurement]`)* |
| A10 | scale §6/§8 still route to the substation and tower pads and keep a random attack cycle | marked superseded in scale (design §6 has no cycle; roads per layout §4) |
| A11 | Trip 7 "R6 marker and assault" — the plaza's marker is R5 | R5 |
| A12 | Cross-references: W8 gate lists M5 while M7 says it opens W8; W11 says "Marshall's X1 hand-in" (it is X2); J8 says "Walker W13 open" while W13 gates on W9/M11/J6 | W8 gate → W7, M7; W11 → X2; J8 → "Walker W13 already open; feeds Storage 4" |
| A13 | Onboard "four colours (dark / scouted / looted / held / defended)" lists five | five states, five colours *(six after C5: `lost` = red)* |
| A14 | "No mod is added" vs EMI added | "no gameplay mod is added; EMI is a client recipe viewer" |
| A15 | Two Novo Expograds: the industrial zone and the hub; Marshall calls Novo "the refinery" (M4's word for the plant) | names fixed: **Novo** = the industrial zone, **the hub** = the Novo Expograd city (the desert city) *(2026-09-07: the two names still separate the two places, but neither is in play — the industrial zone and the hub are both deferred to a later quest line. Novo is not the Act I strongpoint: Act I is clearing Skadowsky, which pays out perimeter and has no keeper, and Walker's heavy-industry strongpoint is KROT. Marshall's "the industrial yard east along the road" is deferred with the zone)* |
| A16 | HANDOFF says "draft 5" and "77 quests" in its design list | draft 6, 106 *(138 after the C items, the placed-structure quests, Teddy's chapter and the mech quests)* |
| A17 | Woods "1.3 km north of Novo", "due north" | 1.6 km north-north-east of Novo's pad |
| A18 | Structure plan foot-range keeps "two bunkers, one fog house" vs table (houses foot = 0) | "two bunkers" |

## B. Owner decisions (each with the default this audit recommends)

**Decided 2026-09-04:** B1 = **after the introductions** (Marshall speaks and the tower chapter opens together;
stages stay part-gated). B30 = **a research-backed finale design, not the dragon by default** (`gscraft-finale.md`).
Every other row: **the default, applied** in the same commit as this note.

| # | Question | Where it shows | Recommended default |
|---|---|---|---|
| B1 | **Tower chapter gate**: after the five introductions (design), after R1 (onboard), or R2+R3+R4 + Workshop 2 + Water 2 + Storage 2 + car (quests) | design L13/176, onboard §2, quests L33-35 | **decided 2026-09-04: after the five introductions** (design §3.6, quests §7.3, onboard §4.4) — this row's earlier recommendation is superseded |
| B2 | **NPC tier-2 gate**: strongpoint *held* (design) or *defended* (quests) | design §3.6 vs every *-B2 | defended (the quests) |
| B3 | **Level-3 "one hub component" rule** vs the actual level-3 rewards (W10 anchor cable, W13 avionics, W14 none, M12 membrane, D4 anchor cable) | design §5 vs quests | drop the blanket rule; state per function which component it takes (the quests already do) |
| B4 | **Component respawn**: every 2 in-game days / on defended / while held / Lootr refresh 5 days | design L232/367/385/397, quests, modcaps L83 | components respawn every 2 in-game days **while the site is held**; Lootr refresh 5 days is for ordinary loot only; write it once in design §6 |
| B5 | **Attack warning** = max(10 min, foot travel): travel to every built site is under 10 min, so the rule is always 10 | design L384 | a flat 10 minutes; drop the formula *(2026-09-04: the counterattack is at the base, so the 10 minutes cover the drive home — every built site is under 4 km)* |
| B6 | **Hordes event**: "as the pack ships it" (design) vs disabled (HANDOFF) | design L391 | disabled for good; the loop is the only calendar |
| B7 | **Recruits**: "later / not these six" vs written into D2; the table at gatehouse tier 1 vs Walls 2 | design L164/202/522, quests D2 | Recruits hired from D2 (Walls 2) at the gatehouse; the tier-1 table is Marshall's map only |
| B8 | **Parts rack**: rewarded twice (R-B1 and X1) and shown at minute 2 | quests, onboard | the rack exists from tier 0 (empty hooks are the point); R-B1 and X1 lose the reward line |
| B9 | **Camp lights / map wall / infection cure**: given at the introductions (onboard, design §3) or at Michael tier 3 / U2 / U-B1 / T2 (quests) | onboard §2, quests | the introductions light the camp *outline* and reveal the map wall (cheap, visible rewards); tiers add more. Infection cure at T1's clinic from the start (else Act I infection has no cure) |
| B10 | **Blueprint sources** disagree between design §4.3 and the quests for the fastener kit, filter cartridge, circuit assembly, med kit, steel frame | design §4.3 | the quests win; regenerate §4.3's "blueprint from" column from the quest tables |
| B11 | **Blueprints**: team stages `bp_<recipe>` (crafting) or IE blueprint items (quests §9) | crafting §4, quests §9 | team stages; the quest reward line reads "blueprint" but the mechanism is the stage |
| B12 | **Engineer's Workbench** "the only one" vs its recipe removed and stations only | design, crafting §4 | stations only; the design's workbench lines become "Walker's benches" |
| B13 | **Order times**: fastener kit 60 s with a wrench (onboard) vs intermediates 2 min, no tool (crafting) | onboard §2, crafting §3 | the crafting sheet's class times; onboard's first order is 2 min, no tool; the tool slot is introduced by W3 (steel frame, torch) |
| B14 | **Tower parts** 30 min vs "a trip-length order" 20 min | crafting L144/L174 | 20 min (trip-length) |
| B15 | **Military packs** "stripped" (crafting §2) vs kept (§2.1); "eight vehicles" vs eleven | crafting | eleven; §2's strip paragraph excludes the three |
| B16 | **Humvee RWS owner**: Marshall's Walls-3 vehicle (modcaps) vs Walker's W-M1 (crafting) | modcaps L53 | Walker (W-M1), as the 2026-09-04 addendum says |
| B17 | **Fuel**: SW vehicles "electric, no fuel" vs fuel tanks in their recipes; three different pumps (garage, plant, drum rack); IV fuel pump recipe removed | crafting §2/§5.5, quests W8/M-B2, design | SW vehicles: batteries only, fuel tanks out of their recipes; IV vehicles fuel at **Michael's plant pump (tier 2)**; Walker's rack stores cans; W8 wording follows |
| B18 | **Storage 2** "a car with a cargo crate" vs W6's iron backpack | design §4.5 | crate is W7's; §4.5 row corrected |
| B19 | **Salvage**: a "damaged weapon" item vs the Apotheosis Salvaging Table | crafting §5.2, modcaps | the Salvaging Table in Walker's yard (tier 2) is the salvage mechanic; the damaged-weapon item is its input |
| B20 | **Assault waves**: the loop script's edge spawns vs the Apotheosis Boss Spawner | design §6, modcaps | the script spawns waves; the elite is an Apotheosis boss summoned by the loop's `spawn_boss` command, no block placed (C14) |
| B21 | **Elites**: named mobs / kept boss towers / garrison tables | design, structure, modcaps | garrison tables name them; the kept towers are loot sites, not the elite source |
| B22 | **Heavy diesel engine**: Novo's vs "in the Woods sawmill" | woods §4 | Novo keeps it; the sawmill's own drop is the saw blade (W-W1) — no second engine |
| B23 | **W1 asks for a wrench** before any tool exists | quests W1, crafting L26 | W1 asks for bolts and nuts only; the wrench is W1's reward |
| B24 | **W5 asks for motor oil "Novo's drops"** but oil drops elsewhere | quests W5, design §4.2 | add motor oil to Novo's site table |
| B25 | **Death**: respawn point, what drops, bleed-out time, revive range numbers | nowhere | respawn at the camp (world spawn); everything drops except the secure pack (Storage 3); PlayerRevive bleed-out 5 min; revive range 6 m, one global value — the tiers act through the script (C18) |
| B26 | **Late joiner / 6th player** | nowhere | stages are **team** stages (FTB Teams); a joiner gets the team's stages, the starting kit and the introductions as a tour |
| B27 | **Team offline during a fortify clock or attack** | design §6 | clocks tick while ≥ 1 team member is online *(owner 2026-09-04: no team-size assumption; was ≥ 2)* |
| B28 | **Restart mid-assault** | quests §9 | the contested slot and clocks persist; a wave in progress restarts at its start; the marker stands |
| B29 | **Lootr instancing vs hand-in counts and component containers** | design §6, HANDOFF | ordinary loot instanced; **component and dossier containers are shared** (one per site per cycle) |
| B30 | **Finale**: dragon in the overworld, HP/affixes, fail state, retry | design §7, X7-X8 | **Decided by `gscraft-finale.md` (2026-09-04):** the Sleeper, a named Warden scaled by `/attribute`, with four Apotheosis-boss Captains; fail = the tower compound overrun or all dead, retry = X6b one in-game day later; Phase E decides numbers |
| B31 | **After the finale** | X9 | free play, board live; the Woods chain is season 1's (C11); season 2 = a second part list and a new region (a design later) |
| B32 | **Hunger / food** | D3 only | Farmer's Delight cooking at the camp kitchen (D3) plus canned goods in the loot tables; hunger left on |
| B33 | **Sleep / night** | nowhere | sleep percentage 100 (no skipping) - nights are the game |
| B34 | **PvP / friendly fire** | nowhere | pvp off; friendly fire off (sedparties) |
| B35 | **Lost vehicle** | crafting §2 | re-kit; the bay repairs a damaged vehicle for one steel frame (W-B2's "repair at the bay") |
| B36 | **Ammunition** | crafting §5.2 | ammo crafted at stations from casings + powder; powder = 1 gunpowder + 1 solvent (crafting §5.6), gunpowder from the town's military chests and the plant complex's four storage halls at (-888, 167), (-743, 167), (-890, 54) and (-775, 54) *(2026-09-07, F11: the stone complex is gone from the v8 map)*; loot ammo scarce |
| B37 | **Stage sharing** (team vs player) | quests §9 | team for sites, functions, blueprints, car_built; player for first-time onboarding lines and revives_3 |
| B38 | **Held sites and claims; how a marker falls** | design §6 | the marker is a block; during the 5-minute assault the waves can destroy it (fail); once `held` only a player can break it (owner 2026-09-04: sites are held by a site guard and every counterattack comes to the base); no player claims at strongpoints |
| B39 | **World border warning** | nowhere | vanilla border damage off, warning distance 200 blocks |
| B40 | **2-of-5 players difficulty** | design L405 | wave size scales ×0.4 solo … ×1.2 for six+ — by players in the site rectangle for the assault, by players online for the counterattack and the finale; clocks run for any team size (B27) |

## C. Assigned to a phase (was "later" with no owner)

| # | Item | Phase |
|---|---|---|
| C1 | Motor-assembly, fuel-can, cargo-crate, boat/truck/aircraft cargo, claim-marker, vest/helmet, casings/powder recipes and their blueprint quests | C (crafting sheet v2) |
| C2 | Sequencing holes: welding torch needs a fuel can before the plant; hand drill needs an electric motor in Act I; fuel tank needs sealed tubing before M3 | C (crafting sheet v2 reorders or substitutes) |
| C3 | Stages missing from quests §9: aircraft prep, finale readiness, season, hangar unlocked, hub loot switch, first-time lines, `bp_*` | C (the stage list) |
| C4 | Farm 2 / Farm 3 quests | C |
| C5 | Camp functions `gscraft:camp_<npc>_<tier>`, `camp_npcs`, `board_<site>_<state>`, signs, banners, the rack; what blocks they are | C (camp.py, after the visual pass) |
| C6 | Coordinates for glass tower, acacia hall, library, KROT, stone complex, residential block rectangle; copper tower / prismarine hall roles *(2026-09-07: the library is deferred to a later quest line, the stone complex is gone from the v8 map, KROT is x −3392…−3073 × z −1344…−1025, and the "residential block" is the Skadowsky hospital at x −865…−698 × z −1312…−1242, roof y 115, ground y 64)* | B (layout sheet, from site_inventory) |
| C7 | Sites that drop nothing anyone needs (copper tower, prismarine hall, KROT, stone complex, mud village, the Woods) *(2026-09-07: the stone complex is gone from the v8 map)* | C (loot tables by site) |
| C8 | Camp-ruins tables lack the introductions' wrench, water filter, broken radio, folder | C (loot tables) |
| C9 | Flashlight, notebook (Patchouli), runway lights *(2026-09-07: `runway_lights` and the runway pad are retired with `camp_ruins` — the aircraft is rotary and lifts from the mast's field inside the camp perimeter, so no airfield is needed, and the runway is deferred to a later quest line. The flashlight and the notebook stand)* | C / B |
| C10 | Undefined rewards: named tool, named backpack, "everlasting slot", "valuables' worth", FD kit | C |
| C11 | Woods quests (ids, acts, gates, rewards), Woods In Control rules, sixth-strongpoint decision | design draft 7 |
| C12 | Bunker side quests | design draft 7 |
| C13 | Vehicle-qualified location tasks ("by car", "by air") | D (KubeJS check on the player's vehicle) |
| C14 | Apotheosis affixes on elites without random bosses | D |
| C15 | IV craftingoverrides file, backpack upgrade gating, ParCool ziplines, Guard Villagers per tier, Recruits hiring, SW defence orders | C / D (modcaps §2 rows) |
| C16 | Marker anchor points per site (the site guard spawns there too); the crater ramp car test *(2026-09-07: dropped — the camp is in Skadowsky and there is no crater and no ramp; the camp's two approaches are the bridge deck and the level crossing)*; resurface pass; in-place pruning inside kept rects; Improved Mobs digging vs the lock; IV crash vs the fence | A (visual pass) |
| C17 | Hub component economy (phased array ×3, satellite receiver ×6, power filter ×4 at one or two per visit, 6 km by air) *(2026-09-07: the desert city hub is deferred to a later quest line, so its component economy is deferred with it)* | D (respawn tuning) |
| C18 | Infection-to-death timer; revive numbers | D |

### C status (2026-09-04)

| # | Done where |
|---|---|
| C1 | crafting §5.6 (fuel can, cargo crate and the three cargo variants, claim marker, casings, powder, ammunition) with their blueprint quests |
| C2 | crafting §5.3/§5.6: torch and hand drill from camp junk; W7 gated on M3 |
| C3 | quests §9 stage table |
| C4 | quests D5 Greenhouse, D6 Rations |
| C5 | `gscraft-camp-spec.md` §1–§3, §6 |
| C6 | layout sheet §3.1 (library identification to confirm on the visual pass) |
| C7 | `gscraft-loot-tables.md` §5 |
| C8 | `gscraft-loot-tables.md` §2 |
| C9 | camp spec §5 (runway lights, the Night-Vision flashlight, the notebook) *(2026-09-07: the runway lights are retired with the runway; the flashlight and the notebook stand)* |
| C10 | quests W14, J3, J9, J10, J11, D3; loot sheet §7 |
| C11 | the sixteen Woods quests (nine plus Teddy's seven), folded into the NPC chapters (quests §2–§7A; no sixth strongpoint; the Woods In Control rule in design §6.3) |
| C12 | Tune's chapter (U-D1…U-D3) |
| C13 | quests §9.1 |
| C14 | design §6.3 (elites by `spawn_boss`) |
| C15 | crafting §5.7, camp spec §4, mod capabilities §5c |
| C16 | **open** — needs the v7 world (Phase A visual pass, `gscraft-map-review-v6.md`) *(2026-09-07: the crater ramp car test is dropped from the row; the remainder is the map and dressing session, F9)* |
| C17 | design §4.4, loot sheet §6 |
| C18 | design §4.5; `build/phase05/config/playerrevive.json` (bleedTime 6000, maxDistance 6) |

## D. Enemy design (2026-09-04, `gscraft-enemies.md`)

The gap the owner named: the garrison tables gave counts, not identities. Draft 1 of the enemies sheet
closes D1–D6 and opens E1–E5 (its §9) as owner questions.

| # | Gap | Closed by |
|---|---|---|
| D1 | Who the enemies are: no factions, no identity, no reason they fight | enemies §1 (five factions), §2 (the faction war) |
| D2 | No equipment design — mob gear was Improved Mobs' random roll | enemies §0.1, §3 (ranks and per-act equipment through In Control!'s rule fields) |
| D3 | No wave composition: "zombies 12" said nothing about what the wave *does* | enemies §4 (four roles, share per wave, what answers each) |
| D4 | Elites named in C14 but never defined | enemies §5 (six definitions with base, rarity, gear and affix flavour) |
| D5 | Mobs dropped nothing designed; the ammunition floor depended on containers | enemies §6 (mob drop tables; sheet 2 of the loot doc) |
| D6 | **Four wrong config defaults**, found reading the jars: mobs steal from containers (`StealGoal` verified), mobs can pick up and use dropped mod weapons, Pillagers Gun's bazooka can blow up the camp gate, and the ten `recruits:` ids are in no Mob Factions faction (hired soldiers are invisible to hostiles) | enemies §8 rows 1, 2, 4, 5 — **apply before the next player test** |

Related: every design document above. The A fixes are applied in the same commit as this file; B is the
owner's list; C rows are copied into the phase they name in `HANDOFF.md`.

## E. The v8 rebase and the fork integration (2026-09-05)

A full read of the sixteen design documents found the design still on the v6/v7 geography while the world is v8, the
Create chapter still a fork, and the interface doc's decisions in no parent. All three were folded in on 2026-09-05
(design §2.1–2.7, §3.6, §6.1, §8; quests §1, §7.2, §7.6, §7B, §9; crafting §2.1, §4, §5.7–5.8; vendors §3–4, §8; camp
spec §1, §5; onboarding §2, §6; the woods plan, modpack review, finale, loot, mod capabilities). The rebase forced
decisions; each below was taken with the default shown and is the owner's to overturn. **Caveat (owner, 2026-09-05):
the v8 layout is mostly decided but its clean-up pass is still running in another session; every coordinate and
distance used here (E1, E3, E5, E6, E10, E17 and design §2) is provisional until the v8 plan's §4 is marked final.**

| # | Decision | Default taken | Why |
|---|---|---|---|
| E1 | Acts by v8 distance | **Superseded 2026-09-07.** Skadowsky is not what Act I closes with, it is where the camp is: Act I is the pocket, then north to the hospital (0.34 km), on foot inside the sector. Act II runs west over the bridge to the collective farm and the town and south down the east bank to the plant's outer works (gate: the first vehicle, and the car stays in Act II). Act III is the plant complex proper — switchyard, turbine hall, intake works (the truck, the marsh channels). Act IV is the confinement hall and the bridge west to KROT (air, or the bridge road). Novo, the plaza, FR-06 and the hub are deferred to a later quest line and no act points at them | the acts gate on land, not on distance rings; Skadowsky is the home sector rather than an objective, and it is cleared by player action |
| E2 | The residential block | **Superseded 2026-09-07.** Skadowsky is the home sector and holds the camp, so it is not the residential block and not a strongpoint. Tony's medical strongpoint, keeper Vera, is **the Skadowsky hospital**, x −865…−698 × z −1312…−1242, roof y 115, ground y 64, 0.34 km due north of the camp square; it holds 372 of the sector's 425 white stained glass blocks and 935 of its 1,785 bone blocks. The `residential_*` stage names are renamed `hospital_*` | the camp is inside the sector, so the sector cannot also be a distant objective; the rename stops the sector and the strongpoint sharing a name |
| E3 | The hub without an air ring | the hub is 2.4 km SW inside the cyberpunk district, reached by truck or by air over the lake; Act IV is "the far edge", the plant complex is the far band *(2026-09-07: the desert city hub is deferred to a later quest line and no quest points at it. Act IV is the confinement hall and the bridge west to KROT)* | the v8 cell is 5.1 × 4.6 km; nothing is 4.5 km away |
| E4 | Quests that named generated structures | re-targeted to placed templates at farmsteads and to the town's landmarks (design §2.7) | v8 has no generated structures inside the cell |
| E5 | Teddy's outpost | the Woods farmstead at (−2176, −576) | inside the v8 Woods, 1.8 km from the camp |
| E6 | The Line | **Superseded 2026-09-07.** The Line runs **west over the bridge to the collective farm** at (−2112, −896), 1.17 km. The six stops and quests L1–L6 keep their owners and their shapes; only the direction reverses. L6's switching station becomes the farm's own substation at the west end, and clearing it opens the farm, not "the block". The corridor stays deliberately empty between stops | the old route, plateau → Skadowsky, is dead at both ends: the camp is in Skadowsky and the old destination, the settlement, is gone. The pylons now lead away from home, which is the right shape for Act II |
| E7 | Danylo | dropped; Vera keeps the medical strongpoint *(2026-09-07: the Skadowsky hospital, not the sector — the sector holds the camp)*; the rail yard is her tier 3 | one keeper per site |
| E8 | Quest count | **172** = 144 + The Gun 10 + the site chains 18 (15 + the train's 3, J-T1…3); the 18 Counter pages are not counted | four different totals stood in four docs |
| E9 | Walls 2 and 3 | no mortar, no laser tower: Superb Warfare's artillery stays stripped, the Create chapter's gun and G8's autocannon nests are the artillery | the fork's ruling, applied to crafting §5.7, quests §7.2, vendors §3–4 |
| E10 | The gun pit | 12×12 at **x −846…−835 × z −1000…−989**, the mast field's west edge, firing east over open grass; locked, tier 0 visible from minute 2 *(2026-09-07: the plateau rectangle x −1340…−1329 × z −2290…−2279 beside the gatehouse is dead)* | onboarding §1: show the object before the system |
| E11 | Walker's tier 2 | gains the basin, blaze burner, Create saw, cast pit and hand-cranked boring frame; tier 3's crane is a rope-pulley contraption | G1–G3 happen in the camp |
| E12 | The train | James's J-T1…3 after `hospital_defended` and S-hospital-3 *(2026-09-07: `residential_*` is renamed `hospital_*`)*; a hauler on a schedule, **no tickets, no fast travel** | design §2.5 prices the game in travel minutes |
| E13 | Site-guard growth | doubles once on `defended`; a keeper's tier 2 adds two Recruits | two triggers stood |
| E14 | A second revive point | the script's camp-revive rule applied to the hospital rectangle (PlayerRevive has one global distance) | design §4.5 |
| E15 | The station model | **the blueprint is a card** in the station's card slot; `bp_<recipe>` stays as the team's record and the vendors' gate; lost cards re-issued for 4 emeralds | interface §4.3 vs crafting §4 |
| E16 | Infection cure at a site | free at Vera's, as at Tony's | vendors §3 |
| E17 | The world spawn | **Superseded 2026-09-07.** The paved junction in the camp, **(−940, −979)**, ground y 65 — already stone, andesite and gravel, already hard surface, and facing the bridge. There is no Warium plaza structure and no Warium spawn structure. Improved Mobs' distance rings measure from it | enemies §7, mod caps §5b |
| E18 | The notebook | seven pages (Driving appears with Garage 1) | interface §3.9 |

**Closed 2026-09-07: the y of the spawn and the tower origin.** Neither waits on the camp core being levelled, because
nothing is levelled: the world spawn is the existing paved junction at (−940, −979), ground y 65, and the tower is
Skadowsky's own mast at (−808, −1008), standing on a building whose roof is y 104 — column yellow concrete y 104–120,
cobblestone wall 121–124, spruce fence 125–131, iron bars 132–136, end rod at 137.

Still open after this pass (Phase C finds): the six Line stops' coordinates (now west of the bridge, on the run to the
collective farm); the town landmarks named in design §2.7 (the dressing pass assigns real
buildings from the measured candidates); the S-chain hand-in rows per site (the Create chapter §3 has the tiers, not the item lists); the keeper
counters' JSON; the Create/CBC section of `gscraft_recipes.js`; design §7.1's dragon paragraph (finale §6 calls it
history; left in place).

## F. The design review on the final sectors and the mod audit (2026-09-05)

`gscraft-design-review-v8.md` (the loop holds on the final rectangles; the paperwork did not) and
`gscraft-mod-utilization-2026-09-05.md` (45 mods rated: none 3, low 9, medium 19, full 14; fifteen capability
mismatches) were applied the same day. What changed and what stays open:

| # | Item | State |
|---|---|---|
| F1 | E1 applied to the quest rows: R2 = Skadowsky after L6, R3 = Novo, R4 = the plaza, R5 = FR-06 + the plant; T3–T7, J-S2/3/5, M4–M6, X3, W7 relabelled; §8 rewritten; onboarding's session 2 | **superseded 2026-09-07** — E1 changed under it. R2 cannot be a strongpoint take after L6: Skadowsky is the home sector and the camp, so R2 is clearing it on the site ladder (`skadowsky_scouted` → `skadowsky_looted` → `skadowsky_held` → `skadowsky_defended`, paying out perimeter rather than a keeper), and it does not sit behind the Line, which now runs west to the collective farm. R3 (Novo), R4 (the plaza) and R5 (FR-06) name sites deferred to a later quest line and are deferred with them; the takes that remain are the hospital, the switchyard, the turbine hall, the intake works and KROT. T3–T7, J-S2/3/5, M4–M6, X3, W7, §8 and onboarding's session 2 need relabelling again against that |
| F2 | The first car before the district walk: L4 (the depot) hands out the motor-assembly blueprint; W7 gates on L4 + T5 + M3 | done (loot §2: an electric motor in the depot's chest — **map/dressing session**) |
| F3 | No crater: design §2.2/§6.1, onboarding §2, create §2, camp spec §1, finale §3 reworded *(2026-09-07: still no crater — the camp is in Skadowsky, which never had one, and there is no crater lake and no crater ramp. The plaza rectangle x −1522…−1459 × z −2262…−2199 is dead: the base's last line is the camp perimeter x −978…−770 × z −1060…−845, and the finale's fail rectangle and sculk ring are the mast's field, x −840…−770 × z −1040…−960)* | done |
| F4 | Blueprint cards per player + a 4-emerald copy (E15 revised) | done |
| F5 | Vendors restock every three in-game days; four hub runs (eighteen hub items) *(2026-09-07: the hub is deferred to a later quest line, so the four hub runs and the eighteen hub items are deferred with it; the restock rule stands)* | done |
| F6 | Difficulty by take order, not distance rings; the Skadowsky counterattack the lightest (the Matron) | done (enemies §1.5, quests R2); design §6.3's tables re-ranked in Phase D |
| F7 | Interface: `held` is the title's moment (no line); the 10-minute warning is one rung per player; the beacon title has no line; the clock readout waits for Radio 2; FTB Quests toasts off; the marker's anchor is a banner post; the component container's lid shows its refresh | done |
| F8 | Mod ids (re-pointed 2026-09-06 when MCSP and vvp were dropped): `fcp:hmmwv_armored_m2` / `dragonrise_reforge:m3a3`; `fcp:mi17` for the runway wreck; CBC moulds `small_cast_mould` / `cannon_end_cast_mould`, four fuzes and no fuze head, autocannon handles are a breech state; Sophisticated Backpacks slot caps (iron 2, gold 3, diamond 5, stack ×3); no flamethrower in Pillagers Gun; onions, not onion seeds; Chipped's benches to strip | done |
| F9 | **Build task, not a design gap (2026-09-07).** Map and dressing session (handed over in HANDOFF): walk and adjust the camp ring inside the camp rectangle **x −978…−770 × z −1060…−845** in Skadowsky, against the buildings that are already standing there — the first-cut NPC rectangles are in `gscraft-skadowsky-camp.md` §3 and map plan §9, and the old job "re-cut the camp ring inside the §4 rectangle (Marshall, James, Walker, the gun pit are east of x −1409)" is dead with the plateau, see H7; the world spawn needs no y and no platform, it is the existing paved junction at (−940, −979), ground y 65; the Line's six stops west of the bridge on the run to the collective farm, and the east-bank road in step 8 (N4); the town's landmarks for §2.7 (N5 defaults, now measured: the palace of culture, the broad civic block at (−2650, −2889), 131 × 114 in grey concrete; the tallest block — any of the 4,044 columns standing at y 118 or above, the town has no single tallest building and does not need one; the central square, the park with the radiating avenues at (−2380, −2975); the four microdistricts at (−2088, −1967), (−1937, −2184), (−2337, −1791) and (−2350, −2289); the stadium at (−2395, −3482); the pool, the hotel, the bus depot and the four farmsteads south of the Woods `[needs measurement]`); the road signs at the junctions (v6 text). **One thing to reconcile on the walk:** the camp perimeter as measured does not contain the tony, walker and michael first-cut rectangles, which run to z −1060, z −845 and z −870, and `tools/checkdocs.py` carries a different perimeter and fails on this one — settle which of the two is right on the ground `[needs measurement]` | build |
| F10 | **Build task, not a design gap (2026-09-07).** Phase C config wins from the audit: `mtsconfig.json` `generateOverrideConfigs: true`; `/hordes SpawnHordeWave` as the wave engine; In Control `areas.json` per site and `effects.json` (the sewers' Darkness); FTB Quests' Stage Barrier (hangar door, tower gate), Quest Chest (the rack) and Item Filters for the "any of" hand-ins; Antiblocks for the lit board, the Doomsday safe for the dossiers; Apotheosis' and IV's first-join books off (the kit is five slots); Recruits patrols off; Hostile Villages `vanillaVillageChance` 0; enemies §8's config rows 1–5 | build |
| F11 | Gunpowder's v8 source (the stone complex is gone): the IE steel route for G6 named in crafting | **decided 2026-09-07**: the town's military chests and the plant complex's four storage halls at (-888, 167), (-743, 167), (-890, 54), (-775, 54) - `gscraft-skadowsky-camp.md` §11.5 |
| F12 | The "plant sector" is "the waterworks" in speech (N7) | done in design §2.3; other docs as they are touched |

## G. Objectives on the v8 map (2026-09-05, `gscraft-objectives-v8.md`)

| # | Decision | State |
|---|---|---|
| G1 | Acts by land: the doorstep / the town and the district / the far bank / the two far edges (O1) | applied: quests §1, §8; design §2.3 |
| G2 | The town's east blocks are Act I's first ruins (O2) | applied: onboarding §2, loot §5 |
| G3 | The reactor control module comes from the plant complex's control room, not FR-06 (O3, owner) | applied: design §3.6, §4.4; quests M11, R-B3; loot §4, §6; crafting §2 |
| G4 | The waterworks (O4) | applied: design §2.3 |
| G5 | Act III: the waterworks by truck first (R5), FR-06 by boat second (R5b) (O5, O8) | applied: quests §7.1 — **superseded 2026-09-07**: both the industrial district ("the waterworks") and the mega-base / FR-06 are deferred to a later quest line, so R5 and R5b are deferred with them. Act III is the plant complex proper: the switchyard, the turbine hall and the intake works, reached by truck through the marsh channels |
| G6 | The farm role: **the collective farm** — the pack's fields south of the town with the farmstead at (−2112, −896) as its yard; the world scan (`farmscan`, 452 farm chunks, all composters in the town's blocks, one carrot plot inside the mega-base) found no farmland, so the fields are planted by the dressing pass (O6, owner) | applied: design §2.7, loot §5; **map session:** plant the fields |
| G7 | The rail yard as a named loot site and the train's north terminus (O7) | applied: objectives §3; quests J-T (to write with the S-chains) |
| G8 | Difficulty by land through In Control areas (O9) | applied: enemies §7 |
| G9 | The crossings list (O10) | handed over: HANDOFF |

## H. The 2026-09-06 gap sweep, and what closed it

A read of the docs against the installed jars found six things the design named but no document wrote, and two
contradictions. All eight are closed the same day; the mod side found nothing missing (every jar the design calls for
is installed, and the only mods still queued are the designer tools of `notes/gscraft-designer-tools.md`, owner's pick).

| # | Gap | Closed by |
|---|---|---|
| H1 | The fifteen keeper quests existed as a summary paragraph only | quests §7B: all fifteen written with tasks, gates and rewards; the Create chapter §3 points at them |
| H2 | The train (J-T1–3) was named in four docs and written in none | quests §6: J-T1 the line, J-T2 the locomotive, J-T3 the schedule; stages `train_1…3` |
| H3 | Teddy's H8 had a recipe and a vendor input but no quest | quests §7A: H8 "The better powder", counter LL4 |
| H4 | The eighteen counter pages were specified but unwritten | quests §7C: `C-<npc>-1…3`, completed by trading once, not counted in the 173 |
| H5 | Nothing said what a keeper's counter does when a site falls back to *looted* | design §6.1 and vendors §3: the keeper stays, the tiers and completed quests hold, the counter closes until the re-take |
| H6 | The boat was built in Act II for an errand the rebase deleted | quests: J5 (Act II, the settlement's slipway) hands out the **boat**; W-V1 (Act III) becomes the **speedboat**; W12 crosses the lake to FR-06 (`fr06_by_boat`); crafting §2 follows *(2026-09-07: the settlement is gone and FR-06 is deferred to a later quest line, so J5's slipway needs a new home and W12 is deferred with FR-06; the boat and speedboat themselves stand)* |
| H7 | The map plan carries two camp rectangles and three buildings plus the gun pit fall outside one of them | **Closed 2026-09-07: neither rectangle is live, so there is nothing to choose between.** Design §2.2's box (x −1690…−1290 × z −2480…−2080, centre (−1490, −2280)) and plan §4's row (x −1792…−1409 × z −2492…−2109) are both plateau rectangles, both dead, and nothing was ever built on either. **The camp is in Skadowsky at x −978…−770 × z −1040…−900**, the pocket east of the south-west bridge, with the mast and its field inside it; `buildmap/plan_v8/sectors_v8.json`, map plan §4's camp row and map plan §9 all now carry that rectangle. What is left is a text edit, not a decision: `gscraft-map-design.md` §2.2 still asserts the plateau box and has to be corrected to the Skadowsky rectangle. F9's "re-cut the ring inside the §4 rectangle" job died with the same question |
| H8 | The Militia held "the hub's approaches" in the enemies doc and the far bank in the entities doc | enemies §1 and §3.3: the far bank and the plant complex's gates; the hub is the Machines' *(2026-09-07: the hub is deferred to a later quest line, so the Machines' holding is deferred with it; the Militia's far bank and plant-complex gates stand)* |

Counts after the sweep: **173** = 148 in the seven chapters (144 + H8 + the three rail quests) + 10 The Gun + 15 keeper
quests; the 18 counter pages are not counted. Hub items spent: 18 (3 phased array, 9 satellite receivers, 6 power
filters), four hub runs, unchanged.

Still open and unchanged by this sweep: the seven entity decisions (`gscraft-entities-v8.md` §9), the four enemy
questions (enemies §9), the designer-tool tiers, and §F9–F10 (the map-session handoffs and the Phase C config wins).
*(2026-09-07: gunpowder's v8 source is closed — F11, the town's military chests and the plant complex's four storage
halls. H7 is closed too: both plateau camp rectangles are dead and the camp is in Skadowsky.)*
