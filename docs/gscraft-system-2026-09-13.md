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
| R16 | The station was to be spiked in KubeJS first (R3, S4) | **the mod, directly** (owner, 2026-09-13): `gscraft.war.station` - block, block entity, menu, screen; orders in `gscraft_recipes/recipes.json` (the card is the order; `#tags` allowed; the class sets the time: quick 20 s, intermediate 2:00, equipment 5:00, trip 20:00; `station.speed` for the yard's tiers); tools wear one point per order (64 uses); `/gscraft station` for the console. The card's tooltip lists its needs. `card_sandbags` deleted (R15). |
| R17 | No bandage recipe anywhere, though the timer table lists bandages as quick | **2 cloth → 1 bandage**, quick, no card; the hospital table still drops them |
| R19 | The first-join kit was Custom Starting Gear's (onboarding §8); the mod already runs the first join | **the mod gives the kit** (`first_join.kit` in survivors.json: the station, a loaded glock with one spare magazine of its own ammo, the flashlight and a battery, a bandage); Custom Starting Gear stays in the pack unconfigured; the notebook (Patchouli, onboarding §6) is not in the slice |
| R20 | How a right-click reaches a chapter | the mod cancels the villager's interaction and runs `/ftbquests open_book #<chapter>` as the player: a chapter carries the tag of its survivor's id (`tools/chapters.py` writes the six with stable ids), so no hex id is ever copied into code; the hello line plays once per player (`seen_<id>`, a per-player tag + advancement) |
| R21 | Only Tune's first line and Walker's sign were written | the mod's lang file carries **placeholder lines** in each voice (`gscraft.say.<npc>.<key>`: Tune's three join lines and the map line, six hellos, Walker's station line, Michael's lights, Marshall's first speech) for **the owner's line pass**; the shape is fixed (interface §3.4), the words are not. The vanilla join message is not yet replaced (open) |
| R22 | The gap and the takes had no chapter: their askers arrive with them (Marshall with the gatehouse, Tony and Tune with the clinic, James with the crossing) and Marshall does not speak before the introductions | **a seventh chapter, "The pocket"**, visible from the start, holds R0 and the five takes in Walker's voice; each survivor's chapter is hidden behind a **meet quest** (an advancement task on the per-player `seen_<id>`, which the right-click sets), so a chapter appears when its survivor has been spoken to; Marshall's chapter holds R1 alone, hidden until the five introductions |
| R23 | The takes' hand-ins were never itemised | a take is **reach the building (its site box) + bar its doors**: 1 fastener kit + 8 metal scrap (the mast 2 + 16); the square asks for 8 scrap from its streets and pays `square_taken` + `skadowsky_scouted` (R11); the mast follows the other three and pays `mast_taken` + `skadowsky_held`; the gap asks for 8 sandbags (R15) and pays `compound_closed` |
| R24 | Three quests needed something the slice has not built | W2 pays a **basic backpack item** (Storage 1 is a stage; the backpack order is Phase C's); J1's second location is **the mast's field** until the railway station is measured; the function levels `workshop_1 storage_1 medical_1 generator_1 water_1 radio_1` are stages in the registry, set by the second quests, read by nothing yet |
| R25 | The assault had no way to be lost (the loop held every site after five minutes) and no marker | **the marker item** (`gscraft:claim_marker`, used on the ground inside a strongpoint) runs the claim: refused in Marshall's words before `looted` or while another site is contested (the marker stays in the hand); accepted, it is consumed and a white banner stands at the anchor's surface. **At the end the banner must stand and a player must be inside the box**, else the assault is lost: the site stays looted, the banner is gone, the marker is re-crafted (crafting §5.6), Marshall says so. The console's `site <id> set held` claims without a marker and keeps the old rule (the tests' path). The banner stays as the site's flag after a hold |
| R26 | The board's wall was never chosen; the spec says 13 × 4 | `tools/board.py` **finds the wall**: the longest solid run inside the hall at y 65-68 with open floor in front - the north wall, origin (-952, 65, -857), 13 along x facing south: six 2-wide columns of concrete three high (unknown black, scouted yellow, looted orange, held light blue, defended lime, lost red), the contested lamp at the east end, a wall sign per column in front. 45 functions (`board_<site>_<state>`, `board_lamp_on/off`, `board_place`); the loop calls them on every state change; `gscraft_board/board.json` gives the mod the geometry for the look-at readout (`THE HOSPITAL — held — clock 39:54 — garrison 6/6`). Radio 2's clock sign and Radio 3's composition sign are not in the slice |
| R27 | The first minute explained nothing (owner, 2026-09-13: "there doesn't seem to be a very good explanation at log in, and the lines don't make sense") | **the polish pass on the first hour.** The title card carries *Skadowsky* under WASTELAND; five seconds later the book opens by itself on a new first chapter, **The compound**, whose one page says where you are, who is in the hall and the block, that a right-click on a survivor opens their chapter, and that the station in your pack goes down inside the wire. Tune's three lines are rewritten to the compound start (the yard, the hall, the block; right-click Walker and Michael; the station; Marshall's corner) and every hello names what the survivor wants. Looking at a survivor within six blocks reads `WALKER THE FOREMAN — right-click to talk` on the action bar; a sign stands beside each (name, place, want, right-click). W1 and W2 say how a card works; the gap says the sandbag recipe; the pocket chapter appears with the first hand-in instead of showing a locked quest. The station's empty readout says where the card goes and the station item has a tooltip. The lines are still the owner's to voice (R21); their facts are now true |
| R28 | The director placed the Dead in plain sight 36 blocks from a player, and the compound filled with them (owner, 2026-09-13) | the compound's box was already excluded; what filled it was placements at its wall walking in through the open corner after the **villagers** (zombies hunt villagers). Three rules: **nothing is placed where a player within `director.hidden_from` (64) can see it** (a clip from the eyes to the stand, every try); **an excluded zone may carry a margin** (map.json `margin`; the compound 32) inside which nothing ambient is placed either, so a player in the yard gets no placements at all and one on the square gets them only north of the margin; **a survivor is never a target** (`LivingChangeTargetEvent` cancelled for `gscraft_npc`). Indoors and underground the ring starts at 10 and 8 instead of 6. The counterattacks still march on the gate: that is the fight the compound is for |
| R29 | Vehicles only knew the road mod's blocks; Skadowsky's streets are vanilla stone work, so nothing patrolled there (owner, 2026-09-13) | **roads by data**: `gscraft_armour/roads.json` - the road mod's surfaces by name anywhere, and per zone a list of plain blocks that count as road inside its box. The `skad` entry lists the streets' stone, andesite, diorite, gravel, slabs, stone bricks and grey concrete **for now**; the road network pass replaces it. Plazas of the same stone count too until then |
| R30 | A holding vehicle never withdrew: the withdrawal was decided only inside the fight goal with a target engaged, and the bail's coin toss (at the disabled share, 60 %) came before the withdrawal's third | **a hit withdraws**: on a health drop the crew withdraws from whoever hit it (else from the nearest player, else straight back) when the hull is under the disabled share or the turret is out, engine permitting; **the bail waits for the retreat to end** (a crew that can drive drives); with the threat ahead the hull **backs straight out** instead of turning in place; **never off a drop or into water** (the ground three and six blocks along the way is probed; the other way if that is safe, else the hull stays). The engaged withdrawal uses the same share, so a hull at 60 % leaves the fight rather than sitting to 33 %. `armour.retreat_share` and `armour.disabled_share` remain the settings |
| R31 | The player's health and armour bars showed inside a hull (owner, 2026-09-13) | **hidden in a vehicle**: the vanilla health and armour overlays and the mod's wounds figure are not drawn while the player rides anything that is not a living mount (`client/VehicleHud`); the hull's state is the vehicle's |
| R32 | Fire missions (owner, 2026-09-13): a mortar strike item, an artillery upgrade, an air strike, a cooldown, the players told | **three strike grenades**, designed in `docs/gscraft-strikes-2026-09-13.md` and built: thrown, they land as coloured smoke and make the call; the mortar's spotting round at 15 s then six rounds, the guns' at 20 s then eight heavy rounds wide, the Cobra (DragonRise's AH-1F, flown as a prop) at 20 s with eight rockets converging on the smoke and five seconds of guns, breaking off if hit, unloaded 300 blocks past. Rounds are Superb Warfare's own shells and rockets spawned in flight (reflection). A cooldown per grenade (the tube 3:00, the guns 5:00, the Cobra 8:00), not one for all; the Cobra's power is held so its rotor turns and its engine sounds, at 55 up; Marshall and Tune speak. Earned in Marshall's chapter: **The tube** (the mortar's parts + 2 steel frames → `mortar_built`, the yard's mortar, the shell card) then three repeatable hand-ins (6 shells / 4 heavy shells on `gun_fired` / 4 rockets on `radio_2`). The registry gains `mortar_built`, `gun_fired`, `radio_2`. The mod has its own creative tab |
| R33 | Crews had trouble acquiring: the detection cone sat on the hull's heading and only opened all round when hit, with no idea where from (owner, 2026-09-13) | **the visual scan**: with nothing engaged the driver crew sweeps the turret slowly across ±70° of the hull's heading (a full sweep in 12 s, 1.5°/tick; `armour.scan_*`) and the 120° cone rides on the turret; **a hit turns the sweep onto the hitter's bearing** (the mod's last attacker) for the alert's length, a narrow ±25° search with a wider cone and acquisition twice as fast; a hit from nothing known still opens the cone all round. The gunner's cone stays on the hull. The survivors: every attack refused at the source (R31's cousin: a creative thrower's rounds bypassed Invulnerable) |
| R34 | The server hung in the autosave (2026-09-13): a survivor summoned with an empty offer list generates trades on the save, and a cartographer's map trade locates a structure on the server thread | every survivor carries **one disabled placeholder trade** (`tools/camp.py`); the right-click never opens the trade screen anyway. A profession with a map trade is safe only with that placeholder |
| R35 | The bail-out was a coin toss at a health share (owner, 2026-09-13: make it stress, a series of hits) | **stress**: every hit adds a point plus the share of the hull it took times four; it decays half a point a second once three seconds have passed without a hit; at five the crew bails at once (the turret out still bails it). Four hits in ten seconds bail a crew; one big one does not. `armour.stress_*`; `armour.bail_chance` is gone. **The Cobra is crewed** (the camp faction, never withdraws or bails, the run picks its weapon): the mod's own rotor, sound, aiming and rounds; a dummy at the smoke as the aim point |
| R36 | Blocks never broke: Superb Warfare's blasts off, mob griefing off (owner, 2026-09-13: on, for wooden blocks only, for vehicles and artillery rounds, not bullets) | **wooden only**: the mod's blasts break blocks again (`explosion_destroy`), and `world/BlastRule.java` strips every non-wooden block from any blast's list (vanilla TNT excepted), so a shell wrecks a shed, a fence or a plank floor and leaves stone, brick and earth; vehicles crush blocks in the mod's soft-collision tag, which the armour datapack replaces with our `gscraft:wooden` tag (normal, hard, beastly off); bullets break nothing (`allow_projectile_destroy_glass` off). `tools/armour_override.py` writes the flags (into the world's `serverconfig/superbwarfare-server.toml`, the Forge SERVER config the mod reads, and the old `config/` copy) and the tag; on a running server `/sbw config explosionDestroy true`, `/sbw config collisionDestroy soft`, `/sbw config projectileDestroyBlocks false` set and save the same; `tools/war_phase41.py`. The tag is the vanilla wooden tags plus the wooden utility blocks; the pack's modded wood (Refurbished Furniture, Doomsday Decoration) is not in it yet |
| R37 | The start compound was the south yard and hall (start-compound §2) | **the walled compound** (owner, 2026-09-17): x −900…−720, z −920…−835 - the big hall, the yard west of it, the north gate where the road enters; spawn (−829, 71, −893); every survivor starts inside; the board free-standing in the yard; start-compound doc §6 has the anatomy and the layout |
| R38 | The journal was a set of survivor chapters with an invisible meet quest each; nothing named the key; rewards waited for a click; the notebook was a plan (owner, 2026-09-17: not intuitive) | **the hub and the notebook**: the compound chapter opens on Wake up and six visible Meet quests that say where each survivor stands; item rewards land on completion; Tune's third line names J and the notebook; the survivor's notebook (Patchouli, eight short pages, in the mod jar) comes with the kit |
| R39 | Nothing on screen said what to do next; the rules had no place to be named | **the pin and the field notes** (2026-09-18): the mod pins the first three startable quests per player through FTB Quests' API (reflection; only its own pins; `gs_nopins` opts out), so the overlay is the to-do list; the `notes` chapter writes itself on five first-time events via per-player `note_<key>` stages, each entry hidden until earned |
| R40 | The strongpoint board: six two-wide concrete columns, a lamp and signs, on the hall's wall and then free-standing in the yard (build 8) | **removed** (owner, 2026-09-18: "too much space for too little information... we'll need a different way to display this"): the blocks cleared by `board_remove`, no `board.json`, so every board call in the mod no-ops as it was written to; the information survives as `/gscraft board`'s one line per strongpoint. The replacement display is undesigned |
| R41 | Nothing checked that what the quests and the station ask for can be had (owner, 2026-09-18: work on the items and drop tables) | **`tools/itemflow.py`** audits sources against asks from the loaded data, with a per-player scarcity estimate. Fixed from it: the powder card with The tube, cloth for the claim marker's uncraftable banner, the clinic's barrels bound to the hospital table. **Bodies and wrecks drop `gscraft:metal_scrap`** where their notes always said scrap (it was an iron nugget nothing consumed): the economy's first renewable input. Fasteners (9.4 expected per player against 44 needed) are the owner's call - HANDOFF has the numbers |
| R42 | Fasteners came from six chests and nothing else; a welding torch was a 40% find and each mortar part 64%; the mortar stood before it was built | **three rules** (owner, 2026-09-19: fix it): bulk materials are renewable (scavengers drop bolts, nuts, nails, screws); the start area covers the first hour (bolts and nuts in the workshop table, 4-6 rolls); a thing needed ONCE has a pool of its own (one of the tube's three parts or a welding torch in every workshop chest, half the garage's) - 97.5% each. **The mortar is The tube's reward only**: tagged, cleared by the quest reset, never a deploy step |
| R43 | A strongpoint climbed its ladder by operator command only, so the claim marker was refused to every player (slice review, finding 1) | **play moves a strongpoint** (`SitePlay`): five seconds of players on foot inside the box scouts it (creative and spectator do not count); six different Lootr containers opened inside it loots it (a search on unknown ground scouts it first). Dials `site.scout_seconds`, `site.loot_goal`. Strongpoints only (a site with no alias); the building takes stay with their quests. Marshall's chapter carries the hospital: Eyes on it, What they left, Plant it |
| R44 | The claim marker cost forty minutes of station time and a lost assault destroyed it (finding 6) | the marker's order is class `equipment` (five minutes); a lost assault **drops the marker where it stood** |
| R45 | Nothing could be eaten (finding 3); closing the gate did nothing (finding 8) | `canned_goods` is food (6, 0.6) - items.json takes `"food": [nutrition, saturation]`; R0's reward runs `gate_close`, the quest reset `gate_open` |
| R46 | No container between the compound and the hospital, none in it (finding 5) | `chests.py` covers the hospital's box and the road north in two halves. **The map's own barrels are furniture**: one is bound only if a hand can reach it and it holds nothing (two hold a written book and are left alone). A placed chest wants a laid floor, two of air, a laid roof within ten, and street level or above - never a cellar. Only the shortfall of a budget is placed; a container's own table is the record's truth |
| R47 | Every build had a green phase and the slice could not be finished | **phase 44 plays the chain and may not use `site set` or `stage add`**: only what stands in for feet and hands. Any new rung of the slice is added to it |
| R48 | The kit's TACZ Glock could not be reloaded: the world drops Superb Warfare's ammunition (finding 2) | **the player's guns are Superb Warfare's** (owner, 2026-09-19). Kit: `superbwarfare:glock_17` with `{GunData:{Ammo:17}}` and 34 `superbwarfare:handgun_ammo` (one round an item; a player pockets rounds with a right-click and reloads from the pocket - the notebook's page The pistol says so). Rounds in the apartment and office tables (weight 8, 4-10). The factions keep their TACZ guns: bodies never drop one |
| R49 | A death disarmed a player for good (finding 4) | **re-issue, not keepInventory** (owner, 2026-09-19): a kit entry marked `"respawn": true` is given again at respawn unless the player carries that item. The pistol, loaded, and the notebook; never rounds, the station or the rest |
| R50 | Nothing in the slice improved a player's weapons or armour at any step (finding 7) | **one step up before each fight**: R0 (the gate, before the junction) gives `superbwarfare:marlin` and 32 rifle rounds; the junction gives `superbwarfare:ru_chest_6b43` and two `armor_plate`. Plates already worked: `Damage` keeps chest points under SW's `ArmorPlate` key, so SW's plate item refills a worn vest (to 30 on a military vest: level 2 x 15). A helmet cannot be refilled |
| R51 | A fighter fired on sight (eye to eye) at the chest: lowered behind a rise it shot the rise | **the muzzle line**: before a round, the line from the eye to the aim point less `Cover.DROP` (0.25) must be clear; else the head if that is; else stand, drop the cover, and no new crouch for `LOW_BLOCKED_TICKS`. `Cover.find` wants a lean clear to the chest as well as the eyes |
| R52 | The counterattack marched to the south compound's corner | `camp.json` `gate` is (-833, -906), just inside the walled compound's north gate. **A barred gate (R0) means a wave cannot walk in**: it must be beaten at the wall. Whether that is wanted is the owner's call after a session |
| R18 | Two orders can both match what is loaded (a bandage's 2 cloth inside sandbags' 2 cloth + 4 sand) | **the order that consumes the most starts**; among a card's orders likewise (the torch over the wrench when the tube is loaded). The player controls it by loading what the card lists. The hand tools are the equipment class (5:00), as the timer table says. |
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
| 4 | **Act I loot**: five `building/*` tables; chests bound by `LootTable` NBT in the compound and the square; the dead `ruins/*` deleted | a fresh player covers W1/T1/M1/U1's lists inside 20 minutes; Lootr instancing holds  **Built 2026-09-13** (phase 31; 41 Lootr chests placed and bound by `tools/chests.py` - the buildings held eight; the 20-minute walk is the in-game check). |
| 5 | **The station** in the mod (R16; the spike skipped on the owner's instruction), the eleven cards' orders and five quick recipes as one data file, `bp_*` per card | card and parts in, the kit out at 2:00 with the countdown; a second player's items refused  **Built 2026-09-13** (phase 32, 7/7: the countdown from 2:00, the kit at 121 s and the block lit until taken, the tool and the count named, cloth and sandbags with no card in 22 s, the stranger's refusal, ten `bp_*`; the screen, the chime and the lit texture are the in-game check). |
| 6 | **The survivors as the book**: right-click → that chapter; the six summons re-issued with a profession; `gscraft:say` and the lang file; the first-join script (title, Tune's three lines, the kit) | right-click on Walker opens his chapter; a new player hears Tune inside a minute  **Built 2026-09-13** (phase 33, 7/7; in the mod - `gscraft.war.survivor` - with `gscraft_survivors/survivors.json`, six chapter files by `tools/chapters.py`, the kit from the mod (R19), `/ftbquests open_book #<chapter>` (R20), the lines as placeholders for the owner's pass (R21); the book opening and the first join are the in-game check: WarTest, `/gscraft join @s`). |
| 7 | **The first twelve quests + the five takes**: W1–3, T1–2, M1–2, U1–2, J1, R0 (the gap → `compound_closed`), R1; hand-ins for `square_taken`, `gatehouse_taken`, `clinic_taken`, `crossing_taken` | the chain plays from the yard to Marshall's first line; each take lights its torch and seats its survivor  **Built 2026-09-13** (phase 34, 7/7; `tools/chapters.py` writes seven chapters and 22 quests - the twelve, the five takes and the mast, five hidden "meet" quests - as FTB Quests files, installed locally; FTB Quests logs them loaded; rulings R22-R24; the played chain is the in-game check: WarTest, `/gscraft reset all`). |
| 8 | **The hospital as the first strongpoint** as it already is, plus the claim marker item and the board on the hall's wall (six columns, three functions per column for the states the slice reaches) | the marker starts the assault; the board turns; the counterattack comes to the gate; the loss and the hold both read on the wall  **Built 2026-09-13** (phase 35, 6/6; the marker item and `/gscraft site <id> marker`, the marker's outcome rule R25, the board by `tools/board.py` on the hall's north wall at (-952, 65, -857) facing south with all six states per column R26, the look-at readout; the right-click, the lines and the counterattack at the gate in play are the in-game check). |
| 9 | **The session**: the owner and four players, an hour from the yard; spark's tick report with the hospital's counterattack and one APC patrol on the front | the numbers in HANDOFF and the answer to the gate question |

After the slice: the live push of everything at once (the jar, the datapack, the pack with the scripts and quests, the
spawn commands), then Act II from the same document.

## 8. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| S1 | Cut the building takes down to a stage + functions (§6) | **yes** - it is a deletion, it removes the drift, the data stays |
| S2 | The vertical slice as the next deliverable, the enemy layer frozen until it plays | **yes** |
| S3 | R1–R10 as ruled above | **yes**, unless one is wrong |
| S4 | The station: spike in KubeJS first, the mod as the fallback | **yes**; the spike is one session. *Revised 2026-09-13: the owner chose the mod directly (R16); no spike.* |
| S5 | The live push withdrawn until the slice plays | **yes** - live keeps today's armour build; steps 1–3 wait with the slice |
