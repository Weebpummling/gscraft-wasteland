# GSCraft Wasteland — the system as a whole, now with squads and armour

*Design pass, 2026-09-12. Owner's ask: "do a design pass on the system as a whole now that we have AI squads and
vehicles." Companion to `gscraft-start-compound-2026-09-12.md` (the start moves into the south compound). Design
only; nothing on either server has been touched.*

*What this reads against: the war mod design (2026-09-09), the enemy review the owner accepted whole (2026-09-10,
W1–W15, X1–X7), the armour design and its results (2026-09-11/12, §1–§17), the camp, objectives, quests, onboarding
and finale docs, and the mod as it stands in the repo (phases 2–23 green on the local server). Where a document and
the mod disagree, the mod is what exists and the document is what is stale; §4 lists those.*

---

## 0. Where the system stands

Two systems exist today and they have never met.

**The enemy layer is real.** One mod owns bodies, factions, ranks and kit, the director (zones, caps, garrisons,
sweeps), the fighters' AI (orders, hearing, suppression, cover, the Sergeant's call, the Marksman's reach, the
Shield), the sites (assault and defence waves by table, stages on the ladder), horrors by ground, drops, and since
this week armour: crewed Superb Warfare vehicles that patrol roads with infantry riding in the bay, fight from
limited cones with a target priority, hold fire for their own men, withdraw hurt, bail out disabled, burn and wreck
and drop loot; in patrols, in waves, and as named bosses. All of it runs locally, 23 test phases deep. On live, the
fighters and the director are up (2026-09-10 push); the armour is not.

**The player layer is a design.** The camp, the survivors and their chains, the stations and crafting, the site
ladder as the players see it (markers, the board, the clocks, the warnings), the tower, the finale — all designed to
the coordinate, and all still on paper: KubeJS/FTB Quests Phase C onward (HANDOFF §5). The one piece of it in the
world is the site ladder's stages, which the mod already reads and writes.

The pass therefore has one job: state how the two layers fit, so that when Phase C is built it is built against the
enemy system that exists rather than the one the 2026-09-04 documents assumed (In Control areas, Hordes waves,
Improved Mobs' distance curve, illager bodies — all retired).

## 1. The layers, and what each owns

| Layer | Owns | Lives in | State |
|---|---|---|---|
| **The world** | the v8 cell, roads as the spine, the three lands and the district; Skadowsky as the home sector | region files; `docs/gscraft-map-plan-v8.md` | deployed |
| **Zones** | where anything may be placed: 40 boxes with caps, pools, garrisons, horrors, patrol routes, armour rolls; exclusions for every player build and the camp | `gscraft_zones/map.json` (from `tools/war_zones.py`) | live |
| **The director** | the pass every 200 ticks per player: ambient placement to the cap inside 48 blocks, garrisons topped up, the sweep at 128, the ceilings (12 per player, 48 per server, a vehicle counts four), the phantom for tests | `world/Director.java`, `Loop.java` | live |
| **Factions** | who fights whom, and toward players (both armies hostile, Scavengers provoked, the Dead hostile to all) as data | `gscraft_factions/*.json` | live |
| **Ranks and kit** | weighted ranks per faction with role, armour, gun, magazines, grenades; uniform skins by faction; the crewman | `gscraft_ranks/*.json`, `tools/make_skins.py` | live (crewman local) |
| **Fighters** | the humanoid AI: gun goals for both gun mods, finite ammunition, hearing (64 blocks, 12 suppressed), suppression and pinning, cover and the slide, orders (hold, advance, goto, squad), the Sergeant's call, the Converted | `entity/*`, `combat/*` | live (the weapon-agnostic hooks pushed 2026-09-12) |
| **Squads** | a leader and members, formations, routes, patrols on the fronts; the escort of a vehicle | `entity/Squad.java`, `/gscraft squad` | live |
| **Armour** | crews in Superb Warfare hulls: drive, fight, retreat, riders, bail-out, wreck loot; patrols by zone roll, wave entries, bosses with stages; the damage lists and the flat TACZ hit; the explosive pass | `armour/*`, `tools/armour_override.py` | **local only** |
| **Sites** | per site: the box, the anchor, the faction, the approach, six assault waves and three defence waves, bosses; stages on the ladder | `gscraft_sites/*.json` (hospital, switchyard, turbine, intake, camp) | live (armour entries local) |
| **Horror** | one at a time, by ground and night, never in a wave | zone `horrors`, `Loop` | live |
| **Drops** | materials never products; per entity and per wreck | `gscraft_drops/*.json` | live (armour local) |
| **The camp and the survivors** | the compound, the six buildings taken by stage, the chains, stations, crafting, the board, the map wall | KubeJS/FTB Quests Phase C, `tools/camp.py` | **design** |
| **The tower and the finale** | five stages, the beacon, the countdown, five waves with Captains, the Sleeper, the fail rectangle at the mast | design; the mod's waves can carry it | **design** |

The seam between the two halves is **stages** (`Stages.add`, the `<site>_scouted/looted/held/defended` ladder,
`test_<boss>` on a boss's death). The mod already sets and reads them; FTB Quests reads the same store. Every rule
below that says "on stage X" is therefore buildable today on the enemy side.

## 2. The loop, seen from the compound

The loop the 2026-09-04 design wrote still holds, and the new layer serves it better than the old one could:

1. **Quiet work: the loot run.** Thin occupiers placed by zone cap, dressed by place; noise draws them — a shot
   is heard at 64 blocks by every fighter, 12 with a suppressor, and an idle ally joins the shooter's fight. A
   patrol on the road is a thing to wait out or avoid; a garrison in a building is a thing to plan for. Armour makes
   the run a different game on the fronts: a tank is heard before it is seen (engine noise at 96 blocks) and its
   crew's cone is narrow, so a run *behind* a patrol is possible and a run across its front is not. That is the
   design's reason for infantry riding with it.
2. **Loud work: the take.** The marker, five minutes, six waves at 45 seconds from the site's edges, the site's
   own faction, team-scaled — the mod's assault loop. The last wave of the plant's sites carries a Bradley
   (assault) and an M1A2 with a Bradley (defence); no rifle stops it, the mine, the RPG or the C4 does.
3. **The counterattack, at the gate.** When the fortify clock ends the waves come to the compound's gate, never
   to the site, from the pocket's approaches. This is where armour turns a fight into an event and where the walls
   earn their keep (start doc §6).
4. **The war around.** NATO and RUAF hold fronts and outposts across the river line from each other and fight
   where they meet; the Scavengers work the town and hold grudges; the Dead are everywhere the armies are not; the
   Machines wait at the plant. The player can watch it, wait it out or start it. Outposts changing hands (W3,
   phase 8) is the piece not built.

## 3. The threat ladder by act

What the enemy system should put in front of the players, act by act, with what the players have to answer it.
The land gates the acts (objectives §6); this table gates the *enemies* to the same land.

| Act | Ground | Infantry | Armour | What answers it |
|---|---|---|---|---|
| **I — the town you woke in** | the compound, the pocket, the sector north to the hospital | the Dead dense, Scavengers in the streets, the two Skadowsky posts (RUAF `sk_out_w`, NATO `sk_out_e`) as the first squads seen — three each, garrisoned, never patrolling into the pocket | **none inside the sector** (`no_armour` until `skadowsky_held`); heard on the far bank | the pistol, the first rifle, the walls, the gate; no anti-armour and none needed |
| **II — over the bridge, down the bank** | the fronts either side of the river, the Line to the farm, KROT, the east bank to the plant's outer works | patrols with a Sergeant on the fronts; outposts of four; hearing makes the first firefights | **APC patrols** (BMP-2 on the RUAF side, Bradley on NATO's) with four riders, on the roads; the first counterattack with armour is the Skadowsky defence, wave 3, one APC | the RPG (Superb Warfare's, blueprint from the Line's depot — two rounds kill an APC), TNT and mines, the 40 mm; the crewmen who bail are a fight in themselves |
| **III — the plant** | the switchyard, the turbine hall, the intake works | NATO organised: Marksmen and Gunners in the halls, Shields on the doors; the plant's ambient armour roll (0.04) | **tanks**: the T-90A at the plant gate as a named boss; M1A2 + Bradley in the last defence wave of each plant site; APC patrols on the bank road | the Javelin (two on a tank, one on an APC), C4 on a parked hull, the truck to carry it; the first gun on the mast field (G1–G4) as the long answer |
| **IV — the reactor, the far bank, the finale** | the confinement hall, the town, the bridge road west | the Captains' waves; the Machines | a boss tank in the finale's last wave with the Sentinel; the M1A2 the NATO column lost at the bridge as the far bank's boss | everything above; the gun's range card; the battery |

Rules the table implies, each one a line of data or a flag:

- **`no_armour` on a zone, lifted by stage.** The Skadowsky sector zone gets it until `skadowsky_held`; the
  compound's exclusion never rolls anything anyway.
- **The armour roll respects the ceiling of the act.** Chance 0.06 on fronts and outposts is right for Act II
  ground; the plant's 0.04 should carry tanks only after `switchyard_scouted` (the players have seen the plant),
  else APCs. A composition entry gains an optional `stage`.
- **Counterattack armour by stage.** The Skadowsky defence carries one APC in wave 3 only once `line_depot` (the
  RPG blueprint) is held — the players must have been handed the answer before the question. The plant sites' tank
  waves are already Act III.
- **Bosses are placed, not rolled.** The T-90 at the plant gate and the M1A2 at the bridge are `director wave`
  placements with a name and a stage, done by the site's scripts on `scouted`; they hold their ground and are the
  quest's marker on the map.
- **Scavengers never get armour.** A technical is a season-two thing with a hull the pack does not have.

## 4. Stale rulings and contradictions, settled

| Where | What it says | What stands |
|---|---|---|
| enemy review §5 | "NPC-driven vehicles: **no**; no vehicle in the pack has AI" | **superseded 2026-09-11** by the armour design: the crew gives the vehicle its AI. Everything else in that table stands. |
| entities-v8 §4 | placement keyed on In Control `areas.json` and spawner rules with `maxcount` | retired; the zone map is the table now. The rows' *content* (who is where) was carried into `map.json` and is right; the mechanism column is dead. |
| entities-v8 §5, enemies §4 | waves by Hordes' `/hordes spawnWave`, dressed by In Control `finalize` | retired (W14); the site files carry the tables and the director places them. |
| enemies §5, mod-capabilities | "difficulty is distance": Improved Mobs' two-step curve from the world spawn | Improved Mobs is gone (owner, 2026-09-10). Difficulty is **the land** (which faction holds the ground), **the rank table** (what the zone rolls) and **the ceiling**. The world spawn moving to the yard changes nothing here. |
| skadowsky-camp §3, §5; onboarding §2 | the team starts holding the pocket, five torches, spawn on the junction | superseded by the start doc: the compound, two torches, the yard. |
| map-design §6.2 | "every counterattack comes to the camp gate" | stands; the gate is the compound's gap, and the wave's target point is a datum in `camp.json`, not a perimeter. |
| skadowsky-camp §5 | `skadowsky_held` extends suppression to the sector | stands, and it is also the stage that lifts `no_armour`. |
| armour design §3 | "an APC's riders dismount and it covers them from twenty blocks back" | as built: the crew halts to fight and the riders come out beside the hull on the crew's target; the twenty-block cover is not built and is not missed. |
| armour design §2 | "the missile for another vehicle" | as built: the cannon always (the missile's magazine of one never reloads for a mob, 2026-09-12). |
| armour §12 (owner) | the contact line, module hits and the rest in chat | chat is off (`armour.chat 0`, owner 2026-09-12); the engine sound and the bar are the tells. |
| quests §7 / camp spec | Marshall's first ask is the parts rack | moved to the gap (start doc §5); the parts rack follows on `gatehouse_taken`. |

## 5. Rules to add to the enemy layer (the design asks of the next code session)

Each is small; none is a new system.

1. **Zone `no_armour` and a stage gate on it** (`"no_armour": "skadowsky_held"` — no armour rolls in the zone
   until the stage exists). One field, one check in the roll.
2. **Composition `stage`** on an armour entry, so tanks at the plant wait for `switchyard_scouted`.
3. **Wave `stage`** on a site's wave entry, so the Skadowsky defence's APC waits for `line_depot`.
4. **`camp.json` gate datum**: `"gate": [-948, -893]` as the counterattack's target, and the compound box as
   `square`. The approaches stay.
5. **Zone stage growth**: the `camp` exclusion as a list of boxes each with a stage (`compound` always; `square`
   on `square_taken`; the pocket on `clinic_taken`…), so the director's denial grows with the players' ground.
6. **Building takes as sites**: the five buildings of Act I are tiny site files (box, anchor, faction, one defence
   wave, no assault) so the ladder's mechanism does the work and the survivor's summon function runs on `held`.
7. **Bosses placed on `scouted`** by the site loop: a `boss` block in the site file (`vehicle`, `name`, `at`,
   `stage`) rather than a command.
8. **The crewman counts** as the faction's fighter for ceilings and sweeps (it does, being a soldier), and never
   rolls (weight 0 — done).

## 6. What the players are told, and how

The chat is off for armour and should stay off for everything the world can say by itself. The tells:

- **Sound.** The engine at 96 blocks, the shot at 64, the suppressor at 12. A tank is heard first — that is a rule
  of the design and the crew's cone is what makes it fair.
- **Sight.** Faction by uniform (the skins), rank by kit (the Gunner's belt, the Marksman's scope, the Shield),
  the vehicle by silhouette. A crewman in trousers and a pistol reads as a crewman.
- **The bar.** Only while a crew is engaged with you, only within earshot, letters for the modules. It drops when
  the crew bails; the burning hull says the rest.
- **The board and the book.** The player layer's job: the sector's state, the site's state, the clocks and the
  ten-minute warning. Radio 3's "attack's composition" should list armour when a wave carries it — that is the
  one place a tank is announced, and it is a reward for building the radio.

## 7. Budget

Measured, not assumed, on the local server: a vehicle is tracked at 512 chunks (view distance 10 is the cap, so
one is visible from 160 blocks); one counts four against the ceilings; a patrol of one APC and four riders is
five entities plus the crew. The server ceiling of 48 with a 12-per-player cap means at most three armour groups
alive across the map at once, which is the intended rarity. The convoy, if it comes, is another group. The
performance budget of the enemy review (§8) has not been re-measured with armour in play and should be, in person,
before the live push: two APC patrols and a firefight with six players is the case.

## 8. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| S1 | The start is the south compound; spawn (−956, 65, −876), radius 4 | **yes** (this pass) |
| S2 | Act I is the pocket taken building by building (five small sites) | **yes** — it is the ladder at building scale and needs no new mechanism |
| S3 | No armour inside the Skadowsky sector until `skadowsky_held` | **yes** |
| S4 | The first armour the players fight is one APC in the Skadowsky defence's wave 3, after the RPG blueprint | **yes** |
| S5 | Tanks at the plant only after `switchyard_scouted`; the T-90 boss at the gate placed on that stage | **yes** |
| S6 | Bosses: the T-90 at the plant gate, the M1A2 at the bridge (Act IV), a tank in the finale's last wave | **yes**; names to the quest doc |
| S7 | The convoy (a truck with an escort between two sites, loot in the truck) | **season two** — the road graph is a 17,000-node skeleton and the drive goal is not a pathfinder |
| S8 | Outposts changing hands (phase 8) | **after the live push** of the armour; a week of play first |
| S9 | Armour chat off for good, or a per-player toggle later | **off**; a toggle is a player-layer item |
| S10 | The live push of the armour: jar + pack (the crew and crewman ranks, the skins), the override datapack in the live world, the zones file, `tacz-common.toml`, `superbwarfare-server.toml` (the explosive pass) | **after** the owner's in-person pass on local with the compound start (S1–S3 first) |

## 9. Order of work

1. **The start** (data and datapack, small): the spawn at the deploy; `camp.json` gate; the compound and
   building boxes in `map.json` with stage growth; `no_armour`; the torch functions by stage. Phase 24 test: a
   fresh spawn lands in the yard, nothing rolls inside the compound, an armour roll refuses inside the sector
   until the stage, the counterattack's wave walks to the gap.
2. **The building takes** as site files, and the survivor summon functions (`camp.py`, Phase A/B of HANDOFF §5).
3. **The stage gates** on compositions and waves (§5.2–5.3) and the placed bosses (§5.7).
4. **The in-person pass** on local: a session from the yard through the square to the hospital with the armour
   on; the budget measured.
5. **Live**: S10.
6. **Phase C** (the player layer) built against this document.
