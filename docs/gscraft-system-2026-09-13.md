# GSCraft Wasteland — the game as one system (2026-09-13)

*The integration document. Owner, 2026-09-13: "reassess the plan and close out design contradictions and better
integration of all the mechanics we've developed … I just don't feel like it's the right direction and I consider the
project losing focus." This document is the answer: every mechanic built to date placed in one loop, the contradictions
closed with rulings (marked so they can be overturned), and a candid reassessment of the last three steps and of the
direction. It supersedes the "next steps A–E" of `gscraft-design-review-2026-09-13.md` §2 and the order of
`gscraft-next-steps-plan-2026-09-12.md` §8. Nothing on either server was touched; the plan's live push is withdrawn.*

---

## 1. The game in one paragraph, as designed and as it stands

Five players wake in the walled yard of a dead town, scavenge the streets for parts, hand them to six survivors who
teach them stations and blueprints, take the town back a building at a time, then claim and hold the five
strongpoints along the river and the plant against counterattacks, each held site paying a part of the mast that
ends the game. That is `gscraft-map-design.md` §1 with the compound start of 2026-09-12. **As it stands, only the
enemy's half of every sentence exists.** The players wake in the yard; the streets, the fronts, the strongpoints and
the counterattacks are all real, tested and live; but there is no part to pick up, no survivor who speaks, no station,
no blueprint, no quest, no reason to take a building and nothing that happens when one is taken except a torch. A
new player today spawns, hears an engine, and has nothing to do. That is the whole of the focus problem, and it is
not a fault in any single decision - it is the order the work was done in.

## 2. The loop, and which half of each rung is built

| Rung of the loop | The enemy's half (mod, live) | The player's half (KubeJS / FTB Quests / data) | State |
|---|---|---|---|
| Wake in the compound | the compound denied to spawns; waves march on its gate; two torches | the starting kit, the title card, Tune's first lines, the notebook | enemy half built |
| Scavenge the streets | the Dead and scavengers by zone, garrisons at the two posts, the front's patrols beyond | loot tables by building type, the `gscraft:` items, the bulky rule | nothing player-side |
| Hand in to a survivor | the six survivors summoned as no-AI villagers | right-click opens their chapter; 173 quests; stages as rewards | nothing player-side |
| Craft at a station | - | the station block, ~85 blueprint cards, the timers, the readout | nothing |
| Take a building (Act I) | five building sites: scouted on entry, `cleared` by a clear, `taken` by a stage, torch + survivor on held, lost by five attackers in the compound | the quest that asks for it and sets `<id>_taken`; the gap as a station order | enemy half built (local) |
| Claim a strongpoint | the ladder, six assault waves, the site guard, the fortify clock, three counterattack waves to the gate, the loss check, `defended` | the claim marker, the board, the clock sign, the warning line, the keeper's chain | enemy half built |
| Meet armour | patrols with riders on the fronts, cones and priority, bail-outs, wrecks with loot; waves and bosses by stage; no tanks near Skadowsky | the RPG blueprint (`line_depot`) that gates the first APC; the Javelin later | enemy half built |
| Build the mast | the tower lock | the tower chapter, the parts, `tower_stage_1..5` | functions only |
| The finale | the site-wave mechanism, the boss block | the beacon, the countdown, the Sleeper, the Captains | mechanism only |

Read down the right-hand column: **the player's half is empty from the second rung to the last.** Read down the
left: the enemy's half is not just built, it is refined - twenty-seven test phases, damage lists per vehicle, a
bail-out coin toss. The refinement was good work and it is not wasted, but it was done against a game nobody can play.

## 3. The mechanics developed, integrated: what each is for, what it reads, what it writes

The one bus between the layers is the **stage set**: a set of strings in the world's record (`SiteData`), written by
the mod (`Stages.add`) and by operators or quests (`/gscraft stage add`), read by the mod (zones, compositions, wave
entries, bosses, takes) and - once ruling R2 is built - by FTB Quests through an advancement per stage. Everything
below either writes a stage or reads one; that is what makes it one system rather than a pile.

| Mechanic | Reads | Writes / shows the player | Where it lives |
|---|---|---|---|
| **Zones by ground and stage** (`gscraft_zones/map.json`, 45) | the player's position, the stage set | who spawns where; the compound denied; a taken box thins to the Dead | `Zones`, `Director` |
| **The director** (caps, ceilings, garrisons, sweeps, horrors, the phantom) | zones, players' presence | the ambient population; nothing is told | `Director` |
| **Fighters** (ranks, kit, skins, hearing, suppression, cover, grenades, callouts, squads, patrols) | factions, ranks data | sight and sound only, by design (§6 of the system pass) | `entity/*` |
| **Factions** (`gscraft_factions`) | - | who fights whom; scavengers provoked, the rest hostile to players | `Factions` |
| **Sites, the ladder** (`gscraft_sites`, 9 + camp) | the claim (a command today), the stage set, presence | `<id>_scouted/looted/held/defended/lost`; titles (hold, held, fell, coming); the boss bar; Tune's warning line | `Loop`, `Sites` |
| **Building takes** (5) | `<id>_taken` (the quest's stage) | held / lost with it; the `held`/`lost` functions (torch, survivor); the zone flips; titles (taken, fell) | `Loop.building` |
| **The counterattack** | the camp's approaches and gate, the online clock | waves marching to the gate; the loss check in the compound; "THE GATE" bar | `Loop.counter/march` |
| **Armour** (patrols, riders, cones, priority, bail, wrecks, waves, bosses) | zones' compositions and their stages, wave entries and their stages, a site's boss block | engine sound at 96, the bar while engaged, the crewman on the ground, the wreck's loot; chat off | `armour/*` |
| **Damage** (the body model, the vehicles' lists, the flat TACZ explosives) | the world datapack `gscraft_armour`, settings | wounds and bleeding on players; modules on vehicles | `combat/*`, `ArmourDamage` |
| **Drops** (`gscraft_drops`: NATO, RUAF, scavengers, the Dead, the Bloater and Rider, wrecks) | the entity type | what a body leaves: materials and dog tags, never a gun; armour at `drops.armour_chance` | `Drops` |
| **The tower lock** (`gscraft_locks/camp.json`) | the tower rectangle | blocks the mast's ground until the chapter opens it | `Locks` |
| **Stages** | - | player tags and, since build 1, an advancement per stage (`gscraft:stage/<name>`, the registry in `tools/stages.py`) | `Stages` |
| **Functions** (torches ×6, survivors ×6, tower stages ×6, dossiers) | run by the loop's `held`/`lost` lists or by hand | the world changes: a torch, a survivor, a tower stage | `build/datapacks/gscraft` |
| **Settings** (`gscraft_settings`, ~130 keys) | a datapack overlay per server | every tunable above | `Settings` |
| **Commands** (`/gscraft director|site|stage|vehicle|squad|fighter|monitor|settings`) | - | the operator's and the tests' hands | `*Commands` |

**What is missing for these to be one system**, in the order it matters:

1. **A reader of stages on the quest side** (R2). Until it exists no quest can react to a take, a hold, a boss's
   death or a rung; the mod is talking to nobody.
2. **A writer of stages on the quest side** other than an operator: the quest reward that runs `/gscraft stage add`.
   The take mechanism waits on this by design (the owner's ruling).
3. **Something to hand in**: the items. Every hand-in, every loot table, every station order is an item id that does
   not exist.
4. **Something that speaks**: the survivors as the book (right-click → chapter), `gscraft:say` for Tune's lines.
5. **The board**: the one place a player reads the ladder's state; today the state is in a command.

## 4. The contradictions, closed

Rulings are mine, applied to the documents on 2026-09-13 by dated in-place notes; the owner overturns any by saying so.

| # | Contradiction | Ruling |
|---|---|---|
| R1 | Two stage vocabularies (`novo/financial/plant/fr06` in quests §9; `hempcrete/…` elsewhere; the mod's ids) | **the mod's ids**: `hospital`, `switchyard`, `intake`, `turbine`, `krot`; rungs `_scouted/_looted/_held/_defended/_lost`; takes `_cleared`/`_taken`; bosses `<site>_<boss>`; recipes `bp_<recipe>`. The registry is §5 below. |
| R2 | How a quest reads a mod stage (no tag task in FTB Quests) | **an advancement per stage** granted by the mod with the tag; read by FTB Quests' native task; per player by nature; no compat mod, no script |
| R3 | The station (KubeJS `BlockEntityBuilder`, unproven) | **a spike before the commitment**; failing that, the station is a block entity in the mod, which already owns entities, data and commands |
| R4 | The board and the map wall: gatehouse (camp spec) vs the hall (quests R1); six vs seven columns | **the hall's ground floor in Act I**, six columns; the gatehouse gets the board when taken; Skadowsky's state is its torches |
| R5 | KROT's take and counterattack faction (X4/X5 open) | a strongpoint **held by assault**, RUAF-occupied, counterattack from the west approach; box re-measured first |
| R6 | Three descriptions of the enemy layer (In Control era, the enemies doc, the data) | **the data is the truth** (`gscraft_sites`, `gscraft_zones`, `gscraft_ranks`, `gscraft_factions`, `gscraft_settings`); the documents describe intent and are corrected to it; balance is tuned in data, never in a document alone |
| R7 | The camp's rectangles: four sources, a failing checker | **the live data is the registry**: `gscraft_sites/camp.json` (the compound, the gate, the approaches), `gscraft_zones/map.json` (the six camp boxes), `gscraft_locks/camp.json` (the tower), `tools/camp_torches.json` and `tools/camp_npcs.json` (the spots); `tools/pads_camp.json` retired; `tools/checkdocs.py` to be re-pointed at these or dropped |
| R8 | The finale's fail rectangle vs the compound as "fall-back" | the fail is the mast's field falling; the compound is where the survivors regroup and the retry begins - one fail line, not two |
| R9 | The create/artillery doc never rehomed (Novo, FR-06, the plaza) | rehomed to the keeper table (Kessler KROT, Ilya switchyard, Rook turbine, Oksana intake, Vera hospital); G6–G8 rehomed and marked for the owner |
| R12 | Where the items live (the plan said KubeJS startup scripts) | **the mod**: one JSON line per item, registered at start; models, placeholder textures and names generated by a tool; no script, no sync of scripts between server and client |
| R13 | U1's broken radio had no Act I source (the library is deferred) | it joins `building/office` |
| R14 | Powder's solvent had no source in the slice | it joins `building/garage` |
| R15 | R0's "W-kit" is undefined; its sandbags' recipe unlocked two quests later | R0 asks for **sandbags only**, a quick recipe (2 cloth + 4 sand, no blueprint); the gate item comes with the steel frame; R0 gates on W1 |
| R11 | The sector ladder `skadowsky_*` beside the building takes (quests §9, objectives §1) | **derived, not claimed**: `skadowsky_scouted` = `square_taken`; `skadowsky_held` = the pocket's other three takes held (the last take's hand-in sets it); `skadowsky_defended` = `hospital_defended`; no marker on the sector itself |
| R10 | Building takes described nowhere in the ladder docs | a building take is **a rung shape of its own**: no assault, cleared by a clear, taken by a quest, lost by the compound's loss check, retaken by the clear; written into map-design §6.1 by note |

## 5. The stage registry (the one vocabulary)

| Group | Stages | Written by | Read by |
|---|---|---|---|
| Strongpoints ×5 | `hospital_*`, `switchyard_*`, `intake_*`, `turbine_*`, `krot_*` with `_scouted`, `_looted`, `_held`, `_defended`, `_lost` | the loop (the claim, the assault, the clock, the loss) | zones, quests, functions, wave entries |
| Building takes ×5 | `square`, `gatehouse`, `north`, `crossing`, `mast` with `_held`; aliases `square_taken`, `gatehouse_taken`, `clinic_taken`, `crossing_taken`, `mast_taken` | **the quest** (`_taken`); the loop (`_held` with it) | zones (the boxes by stage), the loop (the take), quests |
| The sector | `compound_closed`; `skadowsky_scouted` / `_held` / `_defended` derived from the takes and the hospital (R11) | the quest (the takes' hand-ins) | zones (the pocket on `skadowsky_held`), torches, quests |
| Bosses | `switchyard_gatekeeper`; later the bridge's M1A2, the finale's | the boss's death | quests |
| Gates on enemies | `line_depot` (the first APC), `switchyard_scouted` (every tank) | quests; the loop | wave entries, compositions |
| Recipes | `bp_<recipe>` (~85) | the quest (the card's hand-in) | the station, the vendors' copy offer |
| Building tiers | `camp_<npc>_<tier>`, `storage_<n>` | the quest | vendors' loyalty, the tier functions |
| Per player | `joined`, `seen_*`, `revives_3`, `marshall_speaks` | the first-join script, the quests | chapter visibility, first-time lines |

## 6. The reassessment: steps 1–3, and the direction

**Step 1, the compound start** (spawn, the gate datum, zones by stage, torches by stage). *Right, and small.* A
defensible start with one open corner is the first real thing the game asks the players to do, the counterattack
needs a place to go, and the zone growth is the cheapest way to make the ground the players hold feel held. Keep
all of it. The only cost was a day.

**Step 2, the building takes as five sites.** *Right idea, over-built.* The idea - Act I is the pocket taken a
building at a time - is the compound doc's and it is good. The build made each building a site with its own defence
wave, counterattack, loss check, guard slot, held/lost hooks and a two-step cleared/taken ladder, so five buildings
carry the same machinery as a strongpoint. That is a strongpoint ladder at building scale, built before there is a
single quest to ask for a building or an item to hand in for it. It is the clearest case of the enemy layer being
refined past what the player layer can use, and it is what made the last two days feel like drift. **Keep the data,
cut the machinery**: a building take should be a stage the quest sets (`<id>_taken`) that runs its functions (the
torch, the survivor) and flips its zone - and nothing more. No per-building counterattack, no loss check, no guard,
no `_cleared` timer. The sector's own counterattacks (the hospital's, later KROT's) are what attack the gate; that is
enough pressure for Act I and it is already built. This is a deletion, not a build: `Loop.building/take` shrink to
"alias set → held → functions", the five files lose `defence` and `approach`, phase 26 shrinks to match.

**Step 3, the stage gates and bosses.** *Right, and cheap.* It is pure data on mechanisms that existed, it is the only
place the armour layer and the ladder touch, and it fixed a real bug (no wave vehicle had ever placed). Keep.

**The direction.** The plan of 2026-09-12 was in the right order on paper and wrong in practice: it put the player
layer sixth, after four more enemy-layer steps, in a project whose enemy layer was already the most finished thing in
it. Every session since the armour went live has added texture to the enemy (blast radii, a bail chance, riders hidden
in the bay) while the player still has nothing to hold. The owner's feeling is correct. **The correction is a
vertical slice, and a freeze.**

- **The vertical slice**: one hour of play from the yard, end to end, using only what exists plus the smallest
  possible player layer - the first twelve quests, the six survivors as the book, ~25 items, five loot tables bound
  in the compound and the square, one station with six cards, the gap as the first quest, the square as the first
  take, the hospital's counterattack as the first fight at the gate. Playable by the owner and four others, measured
  as a session. Its gate is a question, not a phase count: *did five people have an hour?*
- **The freeze**: no new enemy-layer feature until the slice plays. Bugs and the drop tables only (the drops are the
  loot economy under the slice, so they are part of it). Outposts changing hands, standing and trading, the
  Machines, the finale's cast, the convoy, the underground network stay parked where the review left them.
- **The documents**: this file is the living description of the system and is kept current with every build; the
  design set of 2026-09-04/07 is the record of intent, corrected by dated notes (done today) and otherwise frozen;
  `gscraft-design-review-v8.md` is archived. New design goes into this file or a dated note, not a new document.

## 7. The vertical slice, as a build list

Order, inputs, and what "done" means. Each is a session or less. No step depends on a live push; the slice is played
on the local server and WarTest first.

| # | Build | Done when |
|---|---|---|
| 0 | **Cut the takes down** (§6 step 2): the alias stage takes a building, runs its functions, flips its zone; no per-building counterattack, loss, guard or clear timer; phase 26 rewritten | `/gscraft stage add square_taken` lights the torch and flips the zone; nothing else moves; phase 25/26/6 green  **Built 2026-09-13.** |
| 1 | **R2: an advancement per stage** in the mod, generated from the registry (§5) plus any `bp_*` the recipes list; `/gscraft stage add` grants it | an FTB Quests advancement task on `gscraft:stage/square_taken` completes when the stage is set; survives a relogin  **Built 2026-09-13** (`tools/stages.py`, 50 advancements, `/gscraft stage check`); the FTB Quests task is the in-game check. |
| 2 | **Drop tables** per faction with dog tags and low-rate armour; `dead.json` re-cut from In Control's file | a killed rifleman leaves materials and a tag, never a gun; a wreck's table unchanged  **Built 2026-09-13** (phase 29; the kill is the in-game check). |
| 3 | **Items** (60 for the slice) with stack sizes, the bulky rule, one tooltip each - **in the mod** (R12: `gscraft_items/items.json` + `tools/items.py`), not KubeJS | every id gives; a bulky item slows and cannot sprint. **Built 2026-09-13** (phase 30; the screen is the in-game check). |
| 4 | **Act I loot**: five `building/*` tables; chests bound by `LootTable` NBT in the compound and the square; the dead `ruins/*` deleted | a fresh player covers W1/T1/M1/U1's lists inside 20 minutes; Lootr instancing holds |
| 5 | **The station spike** (R3), then the station and six cards, four quick recipes, `bp_*` via the stage | card and parts in, the kit out at 2:00 with the countdown; a second player's items refused |
| 6 | **The survivors as the book**: right-click → that chapter; the six summons re-issued with a profession; `gscraft:say` and the lang file; the first-join script (title, Tune's three lines, the kit) | right-click on Walker opens his chapter; a new player hears Tune inside a minute |
| 7 | **The first twelve quests + the five takes**: W1–3, T1–2, M1–2, U1–2, J1, R0 (the gap → `compound_closed`), R1; hand-ins for `square_taken`, `gatehouse_taken`, `clinic_taken`, `crossing_taken` | the chain plays from the yard to Marshall's first line; each take lights its torch and seats its survivor |
| 8 | **The hospital as the first strongpoint** as it already is, plus the claim marker item and the board on the hall's wall (six columns, three functions per column for the states the slice reaches) | the marker starts the assault; the board turns; the counterattack comes to the gate; the loss and the hold both read on the wall |
| 9 | **The session**: the owner and four players, an hour from the yard; spark's tick report with the hospital's counterattack and one APC patrol on the front | the numbers in HANDOFF and the answer to the gate question |

After the slice: the live push of everything at once (the jar, the datapack, the pack with the scripts and quests, the
spawn commands), then Act II from the same document.

## 8. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| S1 | Cut the building takes down to a stage + functions (§6) | **yes** - it is a deletion, it removes the drift, the data stays |
| S2 | The vertical slice as the next deliverable, the enemy layer frozen until it plays | **yes** |
| S3 | R1–R10 as ruled above | **yes**, unless one is wrong |
| S4 | The station: spike in KubeJS first, the mod as the fallback | **yes**; the spike is one session |
| S5 | The live push withdrawn until the slice plays | **yes** - live keeps today's armour build; steps 1–3 wait with the slice |
