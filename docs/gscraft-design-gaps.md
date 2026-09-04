# GSCraft Wasteland — Design gap audit (2026-09-04)

Every design document read against every other: `gscraft-map-design.md` (design), `gscraft-quests.md`
(quests), `gscraft-crafting.md` (crafting), `gscraft-mod-capabilities.md` (modcaps),
`gscraft-structure-plan.md` (structure), `gscraft-woods-plan.md` (woods), `gscraft-onboarding.md`
(onboard), `gscraft-map-layout-v6.md` (layout), `gscraft-map-review-v6.md` (review),
`notes/gscraft-scale-and-travel.md` (scale), `HANDOFF.md`. Result: 53 contradictions, 24 dangling
references, 28 missing systems. Triage: **A** fixed in this pass (mechanical, one right answer);
**B** owner decision, with the default this document recommends; **C** belongs to a build phase and
now has one.

## A. Fixed in this pass (stale facts, one right answer)

| # | Gap | Fix applied |
|---|---|---|
| A1 | Novo stale at "1.5 km S / substation pad" in design, quests (W5 "South, a mile", "sends them south"), onboard | 1.06 km ENE on the spine everywhere; W5 retitled "East, a mile" |
| A2 | Financial Plaza stale at "2.5 km SE / hospital pad"; "sewers later under the hospital pad"; review Phase A item about the plaza's causeway; boat "the plaza before its road" | 2.1 km W, dry, one road; the stale lines corrected or struck |
| A3 | Radio tower stale at "2.1 km E", origin (2066, 64, −141), a district → tower road, "the radio mast not visible from home" | the camp NE corner, origin (107, 100, −101); tower road dropped; the mast is the first thing seen |
| A4 | Distances disagree by document: hub 6.0/6.2/6.18, settlement 3.6/3.7, plant 2.3/2.4, Bio Gen 3.9/4.0 | one set from the layout sheet (measured from the camp centre): Novo 1.06, residential 2.0, plant 2.3, FR-06 2.45, plaza 2.1, settlement 3.7, runway 3.9, Bio Gen 4.0, hub 6.2 *(2026-09-04: the layout sheet §3.1 now reads hempcrete 2.2, plant 2.4, residential 1.9, Bio Gen 3.9)* |
| A5 | Quest total 77 (design, HANDOFF) vs 105 (quests) vs 106 (crafting); Walker 22 vs 23 rows | 106 quests, Walker 23, everywhere *(121 after the C items, 2026-09-04)* |
| A6 | Small items "~30" and J11 "the thirty small items" vs 40 in the catalogue | 40 *(42 after the C items: gunpowder, emerald)* |
| A7 | Bio Gen footprint 64×256 vs two groups | two groups, 64×64 and 16×32 |
| A8 | Tune's shack x 60…75 vs moved to x 40…55 | 40…55 (design table) |
| A9 | Design §2.4 roads list (district → Novo, district → tower, Novo may move) vs the built roads | §2.4 points at layout §4: spine via Novo, camp → plaza, district → runway, district → settlement |
| A10 | scale §6/§8 still route to the substation and tower pads and keep a random attack cycle | marked superseded in scale (design §6 has no cycle; roads per layout §4) |
| A11 | Trip 7 "R6 marker and assault" — the plaza's marker is R5 | R5 |
| A12 | Cross-references: W8 gate lists M5 while M7 says it opens W8; W11 says "Marshall's X1 hand-in" (it is X2); J8 says "Walker W13 open" while W13 gates on W9/M11/J6 | W8 gate → W7, M7; W11 → X2; J8 → "Walker W13 already open; feeds Storage 4" |
| A13 | Onboard "four colours (dark / scouted / looted / held / defended)" lists five | five states, five colours |
| A14 | "No mod is added" vs EMI added | "no gameplay mod is added; EMI is a client recipe viewer" |
| A15 | Two Novo Expograds: the industrial zone and the hub; Marshall calls Novo "the refinery" (M4's word for the plant) | names fixed: **Novo** = the industrial zone (Act I strongpoint), **the hub** = the Novo Expograd city in the air ring; Marshall: "the industrial yard east along the road" |
| A16 | HANDOFF says "draft 5" and "77 quests" in its design list | draft 6, 106 *(121 after the C items)* |
| A17 | Woods "1.3 km north of Novo", "due north" | 1.6 km north-north-east of Novo's pad |
| A18 | Structure plan foot-range keeps "two bunkers, one fog house" vs table (houses foot = 0) | "two bunkers" |

## B. Owner decisions (each with the default this audit recommends)

**Decided 2026-09-04:** B1 = **after the introductions** (Marshall speaks and the tower chapter opens together;
stages stay part-gated). B30 = **a research-backed finale design, not the dragon by default** (`gscraft-finale.md`).
Every other row: **the default, applied** in the same commit as this note.

| # | Question | Where it shows | Recommended default |
|---|---|---|---|
| B1 | **Tower chapter gate**: after the five introductions (design), after R1 (onboard), or R2+R3+R4 + Workshop 2 + Water 2 + Storage 2 + car (quests) | design L13/176, onboard §2, quests L33-35 | the quests' gate (end of Act II); design and onboard adopt it. Marshall *speaks* after the introductions; the *tower chapter* opens at the gate |
| B2 | **NPC tier-2 gate**: strongpoint *held* (design) or *defended* (quests) | design §3.6 vs every *-B2 | defended (the quests) |
| B3 | **Level-3 "one hub component" rule** vs the actual level-3 rewards (W10 anchor cable, W13 avionics, W14 none, M12 membrane, D4 anchor cable) | design §5 vs quests | drop the blanket rule; state per function which component it takes (the quests already do) |
| B4 | **Component respawn**: every 2 in-game days / on defended / while held / Lootr refresh 5 days | design L232/367/385/397, quests, modcaps L83 | components respawn every 2 in-game days **while the site is held**; Lootr refresh 5 days is for ordinary loot only; write it once in design §6 |
| B5 | **Attack warning** = max(10 min, foot travel): travel to every built site is under 10 min, so the rule is always 10 | design L384 | a flat 10 minutes; drop the formula |
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
| B27 | **Team offline during a fortify clock or attack** | design §6 | clocks tick only while ≥ 2 team members are online; an attack that starts with < 2 online is postponed to the next login |
| B28 | **Restart mid-assault** | quests §9 | the contested slot and clocks persist; a wave in progress restarts at its start; the marker stands |
| B29 | **Lootr instancing vs hand-in counts and component containers** | design §6, HANDOFF | ordinary loot instanced; **component and dossier containers are shared** (one per site per cycle) |
| B30 | **Finale**: dragon in the overworld, HP/affixes, fail state, retry | design §7, X7-X8 | **Decided by `gscraft-finale.md` (2026-09-04):** the Sleeper, a named Warden scaled by `/attribute`, with four Apotheosis-boss Captains; fail = the marker falls or all dead, retry = X6b one in-game day later; Phase E decides numbers |
| B31 | **After the finale** | X9 | free play, board live; the Woods chain is season 1's (C11); season 2 = a second part list and a new region (a design later) |
| B32 | **Hunger / food** | D3 only | Farmer's Delight cooking at the camp kitchen (D3) plus canned goods in the loot tables; hunger left on |
| B33 | **Sleep / night** | nowhere | sleep percentage 100 (no skipping) - nights are the game |
| B34 | **PvP / friendly fire** | nowhere | pvp off; friendly fire off (sedparties) |
| B35 | **Lost vehicle** | crafting §2 | re-kit; the bay repairs a damaged vehicle for one steel frame (W-B2's "repair at the bay") |
| B36 | **Ammunition** | crafting §5.2 | ammo crafted at stations from casings + powder; powder = 1 gunpowder + 1 solvent (crafting §5.6), gunpowder from the stone complex and military chests; loot ammo scarce |
| B37 | **Stage sharing** (team vs player) | quests §9 | team for sites, functions, blueprints, car_built; player for first-time onboarding lines and revives_3 |
| B38 | **Held sites and claims; how a marker falls** | design §6 | the marker is a block; it falls when broken by the attack's last wave reaching it or by a player; no player claims at strongpoints |
| B39 | **World border warning** | nowhere | vanilla border damage off, warning distance 200 blocks |
| B40 | **2-of-5 players difficulty** | design L405 | wave size scales with players in the rectangle (as designed); clocks pause below 2 (B27) |

## C. Assigned to a phase (was "later" with no owner)

| # | Item | Phase |
|---|---|---|
| C1 | Motor-assembly, fuel-can, cargo-crate, boat/truck/aircraft cargo, claim-marker, vest/helmet, casings/powder recipes and their blueprint quests | C (crafting sheet v2) |
| C2 | Sequencing holes: welding torch needs a fuel can before the plant; hand drill needs an electric motor in Act I; fuel tank needs sealed tubing before M3 | C (crafting sheet v2 reorders or substitutes) |
| C3 | Stages missing from quests §9: aircraft prep, finale readiness, season, hangar unlocked, hub loot switch, first-time lines, `bp_*` | C (the stage list) |
| C4 | Farm 2 / Farm 3 quests | C |
| C5 | Camp functions `gscraft:camp_<npc>_<tier>`, `camp_npcs`, `board_<site>_<state>`, signs, banners, the rack; what blocks they are | B (camp.py) |
| C6 | Coordinates for glass tower, acacia hall, library, hempcrete compound, stone complex, residential block rectangle; copper tower / prismarine hall roles | B (layout sheet, from site_inventory) |
| C7 | Sites that drop nothing anyone needs (copper tower, prismarine hall, hempcrete compound, stone complex, mud village, the Woods) | C (loot tables by site) |
| C8 | Camp-ruins tables lack the introductions' wrench, water filter, broken radio, folder | C (loot tables) |
| C9 | Flashlight, notebook (Patchouli), runway lights | C / B |
| C10 | Undefined rewards: named tool, named backpack, "everlasting slot", "valuables' worth", FD kit | C |
| C11 | Woods quests (ids, acts, gates, rewards), Woods In Control rules, sixth-strongpoint decision | design draft 7 |
| C12 | Bunker side quests | design draft 7 |
| C13 | Vehicle-qualified location tasks ("by car", "by air") | D (KubeJS check on the player's vehicle) |
| C14 | Apotheosis affixes on elites without random bosses | D |
| C15 | IV craftingoverrides file, backpack upgrade gating, ParCool ziplines, Guard Villagers per tier, Recruits hiring, SW defence orders | C / D (modcaps §2 rows) |
| C16 | Marker anchor points per site; crater ramp car test; resurface pass; in-place pruning inside kept rects; Improved Mobs digging vs the lock; IV crash vs the fence | A (visual pass) |
| C17 | Hub component economy (phased array ×3, satellite receiver ×6, power filter ×4 at one or two per visit, 6 km by air) | D (respawn tuning) |
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
| C9 | camp spec §5 (runway lights, the Night-Vision flashlight, the notebook) |
| C10 | quests W14, J3, J9, J10, J11, D3; loot sheet §7 |
| C11 | quests §7.5 (nine quests; no sixth strongpoint; the Woods In Control rule) |
| C12 | quests §7.6 (U-D1…U-D3) |
| C13 | quests §9.1 |
| C14 | design §6.3 (elites by `spawn_boss`) |
| C15 | crafting §5.7, camp spec §4, mod capabilities §5c |
| C16 | **open** — needs the v7 world (Phase A visual pass, `gscraft-map-review-v6.md`) |
| C17 | design §4.4, loot sheet §6 |
| C18 | design §4.5; `build/phase05/config/playerrevive.json` (bleedTime 6000, maxDistance 6) |

Related: every design document above. The A fixes are applied in the same commit as this file; B is the
owner's list; C rows are copied into the phase they name in `HANDOFF.md`.
