# GSCraft Wasteland — the design set reviewed, and the logical next steps (2026-09-13)

*Review, 2026-09-13 (owner: "review the design documents and let's figure out the logical next steps"). Every design
document was read whole against the mod, the data folders, the datapack functions and the HANDOFF entries of
2026-09-12. Three findings frame everything below: the enemy layer is built and live and its documents are one to
three revisions behind it; the player layer has nothing built - no KubeJS startup script, no `gscraft:` item, no
quest file; and the plan's step 4 (the owner's in-person pass with the armour budget) was passed over when the
armour went live early, while steps 1-3 (the compound start, the building takes, the stage gates) sit on local only.*

---

## 0. Where the project stands

| Layer | Designed | Built | Live |
|---|---|---|---|
| Enemies: fighters, ranks, kit, factions, hearing, suppression, cover, squads, garrisons, horrors | yes | yes (27 phases green) | yes |
| Director: zones by ground and stage, ceilings, sweeps, the phantom | yes | yes | zones by stage local only |
| Sites: the ladder, assaults, counterattacks marching to the gate, building takes, bosses placed | yes | yes | building takes, gate, bosses local only |
| Armour: patrols, riders, bail-out, waves, blast pass, no tanks near Skadowsky | yes | yes | yes (tank gate local only) |
| The start in the compound: spawn, torches, survivors summoned | yes | yes | no |
| Items, blueprint cards, the station, recipes | yes (crafting) | **no** | no |
| Loot tables by building and site | yes (loot) | 3 of ~40, under old site ids | no |
| Quests: 173 pages, ~120 stages | yes (quests) | **no** | no |
| Survivors as the book, `gscraft:say`, titles, the board, the readout | yes (interface, onboarding) | the key map and HUD only | HUD yes |
| Vendors | yes | no | no |
| Camp building tiers (24 templates), site tiers (15) | yes (camp spec) | no; `camp.py` writes only the six summons | no |
| The tower, the finale | yes | `tower_stage_0..5` cut at the plateau origin | no |

## 1. What the review found

### 1.1 The documents lag the build - three descriptions of the enemy layer

`gscraft-map-design.md` §6.1/§6.3, `gscraft-design-gaps.md` D6/F10 and `gscraft-entities-v8.md` §0/§4/§8 still
describe In Control, Improved Mobs, Mob Factions, Recruits and Guard Villagers as the enemy layer, and map-design's
§8 heading still says "no custom mod". What runs is `Director`, `Zones`, `Sites`, `Loop`, the mod's own fighters and
factions, and the data in `gscraft_sites/*.json` - which has already gained content no document carries (the
hospital's BMP-2 on `line_depot`, every tank on `switchyard_scouted`, the building takes with no assault). The
finale's "stack the defence tables x1.5" reads from whichever description a session opens. Stale "cannot" claims
that a builder would trust: "no vehicle in the pack has AI", "there is no art pipeline for skins", "vendors on
vanilla offers because KubeJS has no trade events", "Improved Mobs gives the difficulty curve for free".

### 1.2 The player-layer documents contradict each other on the things a build keys on

- **Two stage vocabularies.** `gscraft-quests.md` §7.1 says the ladder ids are unchanged (`novo_*`, `financial_*`,
  `plant_*`, `fr06_*`); loot, crafting, vendors and the camp spec use the renamed set (`hospital`, `hempcrete`,
  `switchyard`, `intake`, `turbine`); the mod's files are `hospital`, `switchyard`, `intake`, `turbine` and no
  `hempcrete`. About forty quests gate on the wrong names today.
- **The camp's rectangles have four sources and no owner**: map-design §2.2, skadowsky-camp §3, `tools/pads_camp.json`
  (the plateau), and the live `gscraft_locks` + `gscraft_zones`; `tools/checkdocs.py` carries a fifth perimeter and
  fails against the document it enforces (gaps F9). Skadowsky-camp §8 and §11.4 give two distance sets for the same
  five sites; §10 says "nothing below has been applied" when half is.
- **`gscraft-create-and-artillery.md` was never rehomed** on 2026-09-07: its keeper table names Novo, FR-06 and the
  Financial Plaza (all deferred), its tier-3 rule is the dropped hub rule, and G1, G5-G8 gate on stages no site sets.
  Anyone building the gun chain from it builds for the wrong map.
- **The board has six columns in the camp spec and seven in onboarding; the map wall is on the gatehouse's wall in
  the spec and on the hall's ground floor in quests R1**; the gatehouse is unheld ground until Act I's step 3.
- **The five Act I takes have no quests**: `gatehouse_taken`, `clinic_taken`, `crossing_taken` appear in no quest
  row, though the mod carries the sites. J5's settlement is gone from the map and was the boat blueprint's source.
  The hub's two yields (nine satellite receivers, three phased array elements) have no source since the hub was
  deferred; three settlement items likewise.
- The finale's fail rectangle is the mast's field and the compound is "the fall-back when the field falls" - a fail
  with a fall-back is not reconciled.

### 1.3 The player layer rests on four unproven hooks

1. **How FTB Quests reads the mod's stages.** The mod writes a stage as a player tag; FTB Quests 2001.4.22 has no
   tag task. Options: FTB XMod Compat's stage task (another mod), a KubeJS custom task (script risk), or the mod
   granting an **advancement per stage** (`gscraft:stage/<name>`, data only) which FTB Quests reads natively. This
   gates roughly forty quests and every take.
2. **The station block**: crafting §4 rests on KubeJS 2001.6.5's `BlockEntityBuilder` with an inventory attachment
   and a server ticker, "verified in the jar" but never run. The whole crafting, card, vendor-copy and reward model
   hangs on it.
3. **Right-click on a survivor opens that survivor's chapter** (`/ftbquests open_book`), with sneak-click as the
   vendor's passthrough. Not written. The six built summons make nitwits with no offers, so vendors need a
   profession fix first.
4. **Per-player stages** (`seen_*`, `revives_3`, the first-time lines): `Stages.add` tags every online player; there
   is no per-player store. The advancement path above gives one for free.

### 1.4 What is missing on the enemy side that Act I and II quests will point at

Corpse and drop tables per rank (`gscraft_drops/dead.json` is still In Control's 2026-09-10 file; NATO, RUAF and
scavenger drops and dog tags do not exist - the loot economy under every quest); KROT as a site file (its take and
counterattack faction are still open, X4/X5, and its box is known stale); the town's, district's and Woods' placed
garrisons (the palace post, the bus depot, the outpost captain, the roof boss); the Grenadier rank; the fog man on the
east-bank road. Everything else unbuilt is Act III-IV or ruled to wait: outposts changing hands (S8, after a week of
play), scavenger standing and the raider band (W1/W15), the Machines, the Sleeper and the Captains, the convoy
(season two), the underground network, surrender.

### 1.5 Unfinished from the plan itself

Step 4 (the owner walks the compound start on local; the tick budget with two APC patrols and a firefight) has no
HANDOFF entry and is overdue. Step 5 (the data push of steps 1-3) waits on it. Live today: the pack spawn 2.5 km
from the compound, no zone stages, no building takes, no gate, tanks ungated.

## 2. The logical next steps, in order

> **Superseded the same day** by `gscraft-system-2026-09-13.md` §6–§7: the owner withdrew the live push and asked for the reassessment first; the order below (A–E) is replaced by the vertical slice, with the building takes cut down and the enemy layer frozen. §1's findings and §3's rulings stand and were applied to the documents on 2026-09-13.

### A. Close the plan: step 4, then step 5 (the owner; one empty window)

The in-person pass from the yard through the square to the hospital with the armour on, and spark's tick report
with two APC patrols in a firefight. Then the live push of the jar and the datapack functions, and the two console
commands for the spawn. Nothing in the player layer should be built against a live world that still starts 2.5 km
away.

### B. Rule five things (one sitting, a memo; §3)

The stage vocabulary, the stage-to-quest hook, the station spike's go/no-go, the board's home in hour one, and
KROT's take. Each is a decision, not work, and each blocks a chunk below.

### C. Bring the documents to the build (one session, mine)

The stale facts of §1.1-§1.2 corrected in place with dated notes, as the compound doc's §8 was: map-design §2.2/§6/§8,
the gaps ledger's standing note and D6/F10, create-and-artillery rehomed, skadowsky-camp §10 marked row by row and
one distance set kept, quests re-keyed to the mod's ids with rows for the five takes and J5's replacement, the camp
spec's torches and board, onboarding §8, the finale's fail/fall-back, `gscraft-design-review-v8.md` retired to an
archive banner with its economy findings moved to the gaps ledger, the equipment inventory's crew row. Cheap, and
it stops the next session building from the wrong page.

### D. The enemy-side data Phase C will point at (half a session)

Drop tables per faction with dog tags and low-rate armour; KROT's site file once B rules its take; the four placed
garrisons; the Grenadier rank; the east-bank fog man. All data against mechanisms that exist; tests by the existing
phases plus one new one for the drops.

### E. Phase C, Act I first, in five chunks with test gates

| Chunk | Build | Gate |
|---|---|---|
| 1. Items and tooltips | `build/kubejs/startup_scripts/` (new): ~45 small items, ~20 intermediates, the dossiers, the claim marker, stack sizes, the bulky tag, one tooltip line each | every id gives; EMI lists each with its tooltip; a bulky item slows, blocks sprint, refuses the pack |
| 2. Act I loot | five `building/*` tables (apartment, garage, workshop, office, hospital); chests bound by `LootTable` NBT at world build across the compound and the square; the four dead `ruins/*` deleted | a fresh player looting the compound and the square covers W1, T1, M1, U1 inside 20 minutes; Lootr instancing intact |
| 3. The station and six cards | the `BlockEntityBuilder` spike first, as a throwaway; then the station, the six introduction cards, four quick recipes, `bp_*` via the mod's stages, the look-at readout | card and parts in, fastener kit out at 2:00 with the countdown and the chime; a missing tool named; a second player's items refused |
| 4. Six survivors, the book, the first quests | the chapter set; W1-3, T1-2, M1-2, U1-2, J1, R0, R1 plus the five take quests; right-click opens the survivor's chapter; stage tasks by the hook B chose; first-join script; `gscraft:say` and the lang file | right-click on Walker opens his chapter; a hand-in yields the wrench, the cards and its stage; the stage survives a relogin; the fifth introduction unlocks Marshall |
| 5. The compound takes and the board | the gap as a station order (sandbags, a gate) setting `compound_closed`; `camp_walker_0/1`, `camp_michael_0/1` templates; the map wall in the hall; a board cut to Act I's columns; `camp_signs` | closing the gap lights the gap torch and arms the counterattack; clearing the square and handing in takes it, lights its torch, reveals the wall; the clinic and the signal box summon their survivors; one counterattack fought in the gap |

Then Act II: KROT, the Line re-placed west of the bridge, the gun chain rehomed (G1-G5), vendors at the two start
survivors, the building tiers, the town's garrisons.

## 3. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| R1 | The stage vocabulary | **the mod's ids** - `hospital`, `switchyard`, `intake`, `turbine`, and `krot` for the fifth (no `hempcrete`); re-key `gscraft-quests.md` and the create doc; every other doc already agrees |
| R2 | How a quest reads a stage | **an advancement per stage**, granted by the mod alongside the tag (`gscraft:stage/<name>`, generated data, per player by nature); FTB Quests' own advancement task reads it, no compat mod, no script |
| R3 | The station | **spike before commitment**: a throwaway `BlockEntityBuilder` block with an inventory and a ticker, one session; if it fails, the fallback is a vanilla block entity in the mod (the mod already carries entities and commands) |
| R4 | The board and the map wall in hour one | **the hall's ground floor**, both (quests R1); the gatehouse gets the strongpoint board when taken; six columns (the camp spec's), Skadowsky's state shown by the takes' torches instead |
| R5 | KROT's take | a **held-by-assault strongpoint** like the hospital, RUAF-occupied (it is the western side), counterattack from the west approach; its box re-measured before the file is written |

## 4. What this review does not change

The system pass's rulings (S1-S10) and the compound start stand. The plan's steps 1-3 are done; the order of the
rest is the same, with the document pass (C) and the enemy data (D) slotted before Phase C because both are cheap
and both would otherwise be redone once quests reference them.
