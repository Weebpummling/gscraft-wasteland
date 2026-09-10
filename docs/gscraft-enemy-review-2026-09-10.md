# GSCraft Wasteland — Enemy design review under the mod (2026-09-10)

Every enemy document so far was written around four borrowed limits: bodies that could not show kit,
factions keyed to entity type, dressing keyed to type and place, and spawns with no memory. The GSCraft War
mod removes all four (`docs/gscraft-war-mod-design.md`; phase 1 confirmed in person 2026-09-09). This review
reads the whole enemy design again with those limits gone: what stays, what was only ever a workaround,
what the new freedom makes possible, what it costs, and which calls are the owner's.

Sources read in full: `gscraft-enemies.md` (draft 1), `gscraft-entities-v8.md`, `gscraft-enemy-design-2026-09-08.md`,
`notes/gscraft-entity-inventory.md`, `gscraft-equipment-inventory.md`, `gscraft-finale.md`,
`gscraft-design-review-2026-09-08.md` §3–§4f, map design §6, objectives v8 §1–§4, and the enemy passages of the
quests, onboarding, interface, capabilities, camp and Woods docs. Capability claims marked **(jar)** were read out of
the shipped jars for this review; **(test)** means not yet proven in game.

---

## 1. What the old limits forced, and what is left of them

| # | Limit | What it forced into the design | Under the mod |
|---|---|---|---|
| L1 | Illager renderers have no armour layer | every faction kit invisible; "legible at fifty metres" (enemies principle 3) carried by silhouette alone | **gone** — humanoid bodies render all armour, confirmed in person |
| L2 | Mob Factions assigns loyalty per entity type | NATO and RUAF shared four types and could never fight; the front was "expressed through placement" only | **gone** — loyalty is per entity; NATO and RUAF engaged in the local test |
| L3 | In Control dresses by type and place, first match | a Scavenger pillager standing in RUAF ground became a RUAF Grenadier; pools had to be pruned by area | **gone** — whoever spawns a soldier chooses its rank |
| L4 | No area-scoped counts; spawner rules cannot be geofenced | a tag gate, a KubeJS spawner with its own AABB ceiling, world-wide caps that emptied one side to fill the other | **gone** — the director counts per zone and remembers squads |
| L5 | Enemies barely use guns | Pillager's Gun's own five guns; TACZ only by tag; infinite ammunition set by a default (F4) | **gone** — soldiers fire issued TACZ guns through `IGunOperator`; magazine and reload are ours |
| L6 | No memory | a "garrison" was a spawn rule re-rolled forever; nothing could be *held* or *lost* by an enemy | **gone** — SavedData squads |
| L7 | `sizemultiply` is a logged no-op | the Matron (×1.5) and the Bloater (×1.4) could not be built as written | **gone** — a mod body sets its own dimensions and render scale |
| L8 | Mob Factions cannot see mod-by-mod nuance | the Machines, Recruits and the Knocker needed faction entries that were missing or wrong | **gone** — the mod injects target goals into any mob; vanilla `Mob.goalSelector` / `targetSelector` are `protected` **(jar)**, so it needs one access-transformer line |

What is **still** true, and shapes everything below:

- **Other mods' brains stay theirs.** Recruits, Guard Villagers, Pomkot's mechs, the three horror mods and Hordes
  infection run their own AI. The mod can steer who they target; it cannot rewrite how they fight.
- **Unloaded chunks do not simulate.** A war that happens where no player is must be bookkeeping, not entities.
- **There is no art pipeline.** Faction skins, voice lines and animated models are new work that nobody has
  done yet. Vanilla's nine default skins carry phase 1.
- **The server budget is real and unmeasured.** Every headless tick figure before 2026-09-09 was taken on a
  paused world (The Hordes' `pauseEventServer`). The only standing number is ~0.5 ms per placement.
- **Mob griefing is off by ruling** until the builders finish, so any enemy role built around doors and walls is
  inert for now.

## 2. What the enemies are for

Nothing in the loop changes; the review is about serving it better. The enemy layer has to deliver:

1. **Loot runs as quiet, careful work** — thin occupiers, noise that draws them (Zombie Awareness), suppressors
   worth their price.
2. **The take as a loud fight** — the five-minute assault, six 45-second waves from the site's edges.
3. **The counterattack at the gate** — three waves at the camp's entry points when the fortify clock ends; no site
   is ever lost to a wave (owner, 2026-09-04).
4. **A world that is occupied and at war** — the faction war the player can watch, wait out or start.
5. **Readable at fifty metres** — who is coming, from silhouette, kit and noise.
6. **Any team size** — ×0.4 solo to ×1.2 for six or more; clocks run with one player online.
7. **The economy's rules** — nothing an enemy carries ever drops; enemies drop materials, never products.
8. **Horror between fights** — one horror at a time, never in a wave.

## 3. Contradictions the new rulings opened, to settle before building

The owner's rulings of 2026-09-09 moved the factions. The older documents were never re-cut to match, and the
mod will build whatever they say, so these come first.

| # | Question | Older docs say | Ruled 2026-09-09 | Recommendation |
|---|---|---|---|---|
| X1 | Who holds the town? | the Dead's land (entities §4); a Scavenger squad at the palace of culture | RUAF's heartland; the Dead ambient everywhere | the town is **RUAF-held with the Dead underneath**; the palace of culture's squad becomes a RUAF post |
| X2 | Who holds the plant? | NATO inside, the Machines at the gates, all day (entities §4) | NATO's heartland | **NATO holds the plant**; the Machines shrink to Act IV's confinement hall (§4.7) |
| X3 | Are Scavengers enemies? | raiders who shoot on sight, KROT's garrison and counterattack, the dog-tag bounty, the Torch, the Chemist, the Wrecker | people; hostile to mobs; to players only if attacked | keep the ruling and give it teeth: a **standing** per team (§4.4). Every rank built on "they attack the camp" moves to a separate hostile band or is cut |
| X4 | KROT | Act II strongpoint, Scavenger garrison, Kessler's keeper chain | a player-built work in progress; nothing spawns there | KROT's **take is unspecified until the builders finish**; the director treats builds as exclusion zones with an explicit override for a site's assault |
| X5 | Who counterattacks from each strongpoint? | the site's faction plus the one it hates | not restated | hospital → **the Dead**; switchyard, turbine hall, intake works → **NATO** (the plant is theirs); KROT → pending X4 |
| X6 | What runs the waves? | Hordes `spawnWave` tables (made to work in phase 2) or the loop's summons | Hordes waves retired locally with the old stack | **the director** runs assaults, counterattacks and the finale; Hordes keeps infection only (B6 "event off for good" stands) |
| X7 | Kill quests that name vanilla mobs | D-O1 "kill 10 pillagers", L6 "kill 8 armed pillagers", R-W1 "kill 15", W-A5 "kill 15" | — | retarget to faction types. **No quest data exists yet** (0 chapters), so this is a doc edit, not a migration. D-O1 and L6 currently ask players to kill neutrals |

## 4. The factions, re-cut for the mod

### 4.1 NATO — the east: the plant, the east-bank spine, the rail-yard outpost

**Body** `gscraft:nato_soldier`. **Kit** stays as the owner saw it: PASGT, IOTV, kr06 trousers, M4A1.

| Rank | Kit change from today | What it does that an illager could not |
|---|---|---|
| Rifleman | — | the line: bursts, holds ground, reloads in cover |
| Sergeant (≈1 in 8) | fast helmet, kr06 vest | **leads a squad**: picks the squad's target, orders the fall-back when the squad is under half strength |
| Marksman | sniper21 helmet, a scoped TACZ rifle chosen in test | overwatch from height; long aim time, one heavy shot. Pillager's Gun's laser tell can be copied for fairness |
| Gunner | a TACZ machine gun chosen in test | suppression: fires at the player's **last known position** when sight is lost |
| Shield | IE steel chest and legs, `minecraft:shield` (the pack's only shield) | actually **raises the shield** while advancing; the rest of the squad walks behind him |
| Grenadier | as Rifleman | throws `superbwarfare` hand grenades or smoke **(jar: `HandGrenadeEntity`, `SmokeDecoyEntity`)** — only after a test proves `EXPLOSION_DESTROY = false` covers them **(test)** |

Doctrine: **fewer, better protected, patient.** NATO holds posts and waits for the player to come to them.

### 4.2 RUAF — the west: the town, the west-bank front, the bridgehead outpost

**Body** `gscraft:ruaf_soldier`. **Kit**: 6B47, 6B43, MSV trousers, AK-47. The same rank list as NATO keeps the
build cheap, but the two should not *play* the same, or the front is one army in two colours.

Doctrine: **more of them, louder, from the buildings.** RUAF garrison windows and stairwells in the town's blocks,
use suppressive fire freely, and push in larger squads. Gorka on RUAF recon in the Woods and fields gives the
west a second silhouette.

### 4.3 The front — faction war made real

What the placement-only ruling could not give, and the mod now can:

- **Contacts where the player is.** Squads from both banks meet at the crossings and the fronts
  (`front_wn/ws`, `front_en/es`, the bridge). The director stages a fight near a player crossing the river rather
  than simulating fights nobody sees.
- **Outposts that can change hands (W3).** SavedData records who holds each outpost. With no player near, a
  contested outpost resolves on paper from the two sides' strength, slowly. With a player near, the squads are real
  and the fight decides it. Heartlands (the town, the plant) never flip, and **player sites never flip** — the
  2026-09-04 ruling is untouched.
- **The Skadowsky introduction.** Both outposts face each other over the one bridge: the first time a player sees
  guns, it is two armies shooting at each other and at the Dead, not at the player.

### 4.4 The Scavengers — people, with a standing

**Body** `gscraft:scavenger`, and deliberately **not** a `Monster`. Superb Warfare's turrets target anything
implementing `Enemy` (enemy pass §2.4, bytecode-read), and Guard Villagers attack hostiles; a neutral body stays out
of both **(test)**. The existing looks all carry over: Scavenger, Digger, Scrapper, Raider, Captain. The **Gunman**
moves off `dragonrise_reforge:terrorist` onto this body (W8) — that entity has no lang entry, a fixed skin, and
hardcoded golden-apple drops that handed over an infection cure on 13 of 40 kills.

**Standing (W1).** One number per team, kept in SavedData:

| Standing | What Scavengers do | How you get there |
|---|---|---|
| Friendly | trade; a Captain shares a site dossier or a patrol route | trade, return a lost Scavenger, kill the Dead near their camp |
| Neutral | ignore you; fight the Dead | the start |
| Wary | warning shot, a chat line ("back off"), then leave | hit one; loot in their camp |
| Hostile | attack on sight, that band and its neighbours | kill Scavengers |

This turns two old designs from contradictions into choices. The **dog-tag bounty** (E2) becomes a real trade-off:
Marshall pays for tags, and every tag costs standing. The **raider** ranks the older docs wanted — the Torch, the
Chemist, the Wrecker, KROT's counterattack — belong to a separate **hostile band** that does not share the
Scavengers' standing, if the owner wants that band at all.

**Trading** is possible on a mod body: vanilla's merchant screen works for any entity that implements `Merchant`,
which is how the wandering trader does it. That is a Scavenger counter that restocks on its own, which villager
NPCs cannot do (entity inventory §3).

### 4.5 The Dead — ambient everywhere, dressed by place, with a history

**Bodies** stay vanilla — zombie, husk, zombie villager, drowned — because Hordes infection, Zombie Awareness, Guard
Villagers and the Magnum Torches all already know them. The director dresses them per zone with the kits already
chosen: Plant Worker, Containment Crew, The Infected, Yard Hand, Peacekeeper, The Drowned, Drowned Patrol.

What the mod adds:

| Addition | What it is | Cost |
|---|---|---|
| **The Converted (W7)** | a soldier killed by the Dead rises as a zombie **wearing his own kit** (vanilla zombies render armour). The war leaves visible residue: dead RUAF in the town, dead NATO at the plant | low — a death hook |
| **The Matron** | the hospital's elite at her designed size, on a `gscraft:` husk subclass | low |
| **The Bloater** | the designed ×1.4 body, slow and tough, Act III onward | low; its death effect is a test |
| **The Runner** | speed on a vanilla body; no new entity needed | trivial |
| **Hearing gunfire** | TACZ posts `GunFireEvent` and `GunShootEvent` **(jar)**; the director alerts the Dead in a radius the gun's own loudness sets, smaller with a suppressor | low–medium |

Special Dead that are mod subclasses must have their ids added to Hordes' `infection_entities.json` and Zombie
Awareness' `enhancedMobs`, or they fall out of those systems.

### 4.6 The Horrors — theirs, placed by us

Unchanged in kind. The director decides **where** each may appear: the fog man in the Woods at night (his
location trigger went with the retired KubeJS spawner and returns here), the Knocker at the hospital after dark,
the Eyes in dark places. The mods' own random timers stay off where they misbehave — the fog man's
`enable_spawning = false` stands, since his random trigger produced effects with no man and disconnected the owner.

### 4.7 The Machines — shrink to Act IV (W5)

The plant-gate war with NATO was a way to give two edges an owner. NATO now owns the plant outright, the hub is
deferred, and Pomkot's mechs are alpha and the only sci-fi note in a gun-and-zombie world. Keep **the Overseer**
(the confinement hall, Act IV) and **the Custodian** (J-H1) as set pieces; drop the ambient mechs. The mod gives them
"hostile to everything" through injected target goals rather than a Mob Factions entry.

### 4.8 The Camp — allies stay where they are

Recruits and Guard Villagers keep hiring, orders and site-guard duty; quests D2 and the site ladder depend on them.
They target NATO and RUAF (both `Monster`) and ignore Scavengers (not `Monster`) **(test)**. A camp militia on the
mod's own soldier body — visible kit, real TACZ guns — is possible later and is **not** recommended now.

## 5. Behaviour, ranked by value and cost

| Capability | What it gives the game | Cost | Call |
|---|---|---|---|
| Visible kit and rank | principle 3, finally | done | **done** |
| Per-entity faction war | the front, the Skadowsky introduction | done (basic) | **done**; relations to JSON next |
| Squads with a leader, formations, patrol routes | an army instead of a crowd; the front has shape | medium | **now** |
| Persistent garrisons that refill | an outpost feels held, and emptying one matters | medium | **now** |
| Hearing gunfire (TACZ events, suppressor-aware) | quiet runs vs loud takes, for every faction | low–medium | **now** |
| Finite ammunition and reload (F4) | fights have rhythm; a reloading enemy is a window | low | **now** |
| Shields that block | the Shield rank means something | low | **now** |
| The Converted | the war's history on the ground | low | **now** |
| Director-run waves | assault, counterattack and finale from one system, geofenced, team-scaled | medium | **now** |
| Scavenger standing and trading | a neutral faction with consequences | medium | **next** |
| Cover-seeking and suppression (accuracy falls under fire) | firefights that reward flanking | high | **next** |
| Grenades and smoke | squads can dislodge a camper | low–medium, needs the block-damage test | **next** |
| Surrender and capture → intel | a live alternative to the dossier; mercy as a choice | medium | **later** |
| Outposts changing hands offscreen | the war moves while you are away | medium | **later** |
| Custom faction skins | faces and patches instead of Steve in a helmet | art, not code | **later**; commission 6–10 |
| Voice callouts | "reloading", "grenade" | audio assets | **later**; chat subtitles (E1) now |
| NPC-driven vehicles | armour on the front | high; no vehicle in the pack has AI | **no** |
| Diplomacy with NATO or RUAF | a truce chapter | a season of design | **no** (E3, season two) |

## 6. Waves, re-expressed

The four roles stand — **Body, Breacher, Shooter, Anchor** — and the share table of enemies §4 stands. What changes
is who fills them:

| Role | The Dead (hospital) | NATO (the plant's three sites) |
|---|---|---|
| Body | Shamblers, Runners, the Converted | Riflemen |
| Breacher | Plant Workers and Yard Hands with tools | Grenadiers |
| Shooter | — (the hospital is meant to feel like drowning) | Marksmen, Gunners |
| Anchor | Bloaters, the Matron | Shields, the Sergeant |

**While mob griefing is off, the Breacher role breaks nothing.** Its share folds into Body and Anchor until the
builders finish and griefing returns (W13). Team scaling (×0.4–×1.2), the 45-second cadence and the counterattack
entry points 48 blocks outside the perimeter all carry over unchanged.

## 7. Drops and the economy

"Nothing an enemy carries ever drops" gains weight, because the kit is now visible and wanted — the infection
ladder already rates the military helmets and vests at 0.15 (E3). So:

- **Guns never drop.** Unchanged.
- **Armour at a low rate (F3)** is now the one open lever that turns a visible kit into a reason to fight. Recommend
  yes, per rank, per piece.
- **Loot sheet 2 needs re-cutting.** NATO's drops were IE revolver parts because NATO *was* IE's Commando; that body
  is gone. Military materials and **dog tags** (from NATO and RUAF, not Scavengers) replace them.
- **Corpse tables** become `gscraft:entities/<rank>` in the mod's own data, materials only.

## 8. Performance budget — to measure, not assume

On a **ticking** local server (the lesson of 2026-09-09), with spark:

1. AI cost per soldier — idle, patrolling, fighting.
2. TACZ bullet cost per burst.
3. A player bubble: hostiles within 64 blocks at the target density; squads materialise within about 128 blocks and
   fold back into SavedData beyond about 160.
4. Five players spread across both banks and a contact at the bridge: tick time, not guesses.

## 9. What retires, what stays

**Retires from the design:** the illager faction bodies; IE's Commando, Fusilier and Bulwark as NATO; Mob Factions
for any faction the mod owns; In Control dressing and density rules; the KubeJS area spawner and neutrality
script (already off locally); Hordes wave tables (already off locally); `dragonrise_reforge:terrorist`; Apotheosis
bosses for faction elites unless W9 says otherwise; the ambient mechs; the "NATO vs the Machines at the gates" set
piece.

**Stays:** the site ladder, timers, the counterattack at the gate and "no site is lost to a wave"; the four wave roles
and team scaling; Hordes infection; Zombie Awareness for the Dead; the horror mods; Recruits and Guard Villagers;
the finale's Sleeper (a Warden) — its four Captains become one elite per fighting faction on mod bodies; the equipment
roster from the registry; the infection ladder; the builds-are-no-spawn ruling; mob griefing off.

## 10. Decisions for the owner

**RULED 2026-09-10 (owner): every recommendation below is accepted, W1 to W15, and the recommendations of §3
(X1 to X7) with them.** Implementation starts locally at phase 2 of §11.
One call the review left open is taken as a default and recorded here: NATO, RUAF and the Scavengers are
**neutral to each other** (each retaliates when struck), so the Scavengers stay people between the armies
rather than targets for both. It is one line in the faction data.

| # | Decision | Recommendation |
|---|---|---|
| W1 | Scavenger **standing** per team: kill them and bands turn hostile; trade with them when friendly | **yes** |
| W2 | NATO and RUAF toward players in season one | **both hostile**; any truce is season two (E3) |
| W3 | Outposts on the front can change hands between NATO and RUAF over time | **yes, slowly** — never heartlands, never player sites |
| W4 | Counterattack faction per strongpoint: hospital the Dead; the plant's three NATO; KROT pending | **confirm** |
| W5 | The Machines only as the Overseer and the Custodian (Act IV); no ambient mechs | **yes** |
| W6 | The Matron and the Bloater as mod bodies at their designed size | **yes** |
| W7 | The Converted: soldiers killed by the Dead rise wearing their own kit | **yes** |
| W8 | Retire `dragonrise_reforge:terrorist`; the Gunman moves to the Scavenger body | **yes** |
| W9 | Faction elites (Sergeant Kell, the Broker, the Captains) native to the mod, or Apotheosis bosses | **native** — behaviour matters, and Apotheosis gear drops would need suppressing |
| W10 | NPC ammunition (F4) | **finite**: a few magazines each; when dry, fall back or close to melee |
| W11 | Grenadiers with Superb Warfare grenades | **yes, after** a test proves no block damage |
| W12 | An art budget for faction skins; voice later | **skins yes** (6–10); chat subtitles until voice |
| W13 | While mob griefing stays off, the Breacher share folds into Body and Anchor | **confirm** (follows the standing ruling) |
| W14 | Hordes: infection only, waves from the director | **yes** |
| W15 | A hostile raider band separate from the Scavengers, carrying the Torch, the Chemist and the Wrecker | **defer** until W1 has been played |

## 11. Build order

Updates the war-mod design's phases. Each passes locally, on a ticking server, before the next.

| Phase | Build | Passes when |
|---|---|---|
| 2 | Relations as JSON; the Scavenger body and its neutrality; injected goals so the Dead hunt soldiers; the Converted | a scripted three-way fight tallies right; a Scavenger ignores a player until struck |
| 3 | Ranks as data: Marksman, Gunner, Shield (blocking), Sergeant; finite ammunition; hearing gunfire | each rank's behaviour probe; the owner plays a firefight |
| 4 | The director: zones from `incontrol_areas.py`, exclusions (builds, camp, torches), ambient Dead dressed by place, persistent outpost garrisons, horror placement | probes plus the performance budget of §8 |
| 5 | Squads, patrol routes, contacts at the front | in person at the bridge |
| 6 | Director waves: the assault, the counterattack, the finale Captains | one site's full ladder in person |
| 7 | Standing and trading; grenades after the block test | in person |
| 8 | Outposts changing hands | a week of play |

**Phase 2 done locally, 2026-09-10** (`tools/war_phase2.py`, 8 of 8 on a ticking server): factions load from
`data/gscraft/gscraft_factions/*.json` and reload with `/reload`; the Dead hunt soldiers and Scavengers through an
injected target goal (access transformer on `Mob.goalSelector`/`targetSelector`); a Scavenger starts fights with the
Dead on its own and ignores the armies, which ignore it; the Converted rise wearing their kit. Two findings: Create's
cardboard sword deals no damage, so the Scrapper now carries Superb Warfare's knife; and a lone melee Scavenger loses
to two live zombies on Hard, which is left as balance for phase 3 to judge.

**Phase 3 done locally, 2026-09-10** (`tools/war_phase3.py` 8 of 8, `war_phase2.py` 8 of 8 as regression): ranks
are data in `data/gscraft/gscraft_ranks/<faction>.json` with a role each — Rifleman, Sergeant (calls his target to
idle allies within 20 blocks), Marksman (64-block reach, long aim, holds distance, backs away inside 16), Gunner
(long bursts, two seconds of fire on the last known position), Shield (raises a real shield while closing and
reloading). Guns from the 54 loaded TACZ guns: NATO `m4a1`/`mk14`/`m249`/`m9a4`, RUAF `ak47`/`sks_tactical`/`rpk`/`cz75`.
Ammunition is finite (W10): spare magazines per rank, then melee. Gunfire is heard: 64 blocks, 12 with a suppressor
(TACZ `GunProperties.SILENCE`); an enemy walks to the shot, an idle ally joins the shooter's fight. Measured: a
rifleman with no spare magazine closed to melee at 0.8 blocks; a Marksman held 30 blocks and took a target from 200 to
48; a RUAF soldier 50 blocks out walked from the shot's 50 to 18 blocks and killed the shooter. In person still: the
Shield's block, the Gunner's suppression, the Sergeant's call.

**Phase 4 done locally, 2026-09-10** (`tools/war_phase4.py` 13 of 13; phases 3 and 2 still 8 of 8 each): the director.
Zones are data (`data/gscraft/gscraft_zones/map.json`, 40 zones generated by `tools/war_zones.py` from the measured
boxes: 10 builds excluded, 6 garrisons, 3 horror grounds, then open ground). Every 200 ticks, per player, it places
one fighter or one of the Dead 20 to 44 blocks out when fewer than the zone's cap stand within 48 blocks; the zone is
read where the placement lands. The Dead are dressed by zone from `gscraft_ranks/dead.json` (The Infected at the
hospital, Plant Workers and Containment Crew at the reactor hall, Peacekeepers in the town); a zombie under open sky
by day is placed as a husk. Placement asks Forge's position check and the Magnum Torch handler directly (the torches
refuse on entity load, not through Forge's spawn events). Garrisons: persistent members bound to their post, topped up
10 minutes after the last refill. Horrors: the fog man in the Woods, the Knocker at the hospital, the Eyes in the
turbine hall, at night, one at a time. Measured: ~0.3 to 1.1 ms per placement; a live 26-strong fight in the town took
the overworld from 3.0 to 5.0 ms per tick, 0.08 ms each. Commands: `/gscraft zone|zones|director pass|horrors|stats|
pause|resume` and `/gscraft garrison <zone> fill|force`.

**Improved Mobs removed, 2026-09-10 (owner):** it served no purpose once the mod owned gear, targeting and placement,
and it was rolling gear onto the Dead after the director dressed them (lava buckets, ender pearls, flint and steel).
Difficulty by distance goes with it; if difficulty scaling returns, it is the director's, per zone. RUAF's Skadowsky
post moved into the town, to the brick block between the camp and the hospital (`sk_out_w`, centre -752, -1124).

**Areas, ground and kit, 2026-09-10** (`tools/war_phase4b.py` 12 of 12; phases 4, 3 and 2 still 13, 8 and 8 of each). Owner asks: each
area with its own creatures; how underground placement affects surface density; thinner in the open, denser indoors;
randomised Scavenger kit, limited variety for the armies.

- *Ground kinds* (`world/Env.java`), read from what is overhead: rock or earth, or a built ceiling with three or more
  blocks of rock or earth over it, is underground; other solid is indoor; nothing for 24 blocks is open. Open: cap
  ×0.75, placed 28–52 blocks out. Indoor and underground: cap ×1.5, placed 6–24 out. Placement stays on the player's
  kind of ground, caps count per kind, and indoors or underground a placement must have a walkable path to the player.
- *Area creatures*: Bloaters at the plant (5 in 60 placements), the Matron alone in the hospital lair (persistent, not
  doubled), Riders on the farm's fields at night, cave spiders with the Dead under the Woods (19 and 11 in 40), Runners
  among the town's Dead (speed 0.30 against 0.23). The `farm` zone had never matched: its box sits inside `woods`, which
  was listed first; the order is fixed.
- *What the first version did to density*, same reference points, 150 samples each. From a street it put 6–18 % of
  placements indoors or underground (town centre 18 of 131), and every one counted against the street's cap. From the
  plant yard, 21 % landed off the player's ground, 10 blocks up or down on average, 11 of 40 walkable. From inside a
  building it placed 79–98 % outdoors (RUAF post 116 of 129, Skadowsky house 111 of 113, town centre 106 of 134); from
  the hospital's ground floor, half went underground. From bunkers and the
  west-front dungeon it put the Dead 5.6–10.2 blocks above or below on average, 0–16 % visible, 1–8 of 25–40 walkable. The spawner
  blocks (167 in the playable area, half below y 40) spawn nothing under the hold, so the underground held only what the
  director placed, and that came mostly from players on the surface above it.
- *Layered*: 100 % on the player's ground everywhere. Underground: 75–100 % visible and every sampled placement walkable in
  the bunkers, the cellar and the dungeon. Indoors, walkability decides: the hospital gives 52 placements, 98 % visible; the RUAF post's
  brick block gives 1 and a Skadowsky house 3, because their rooms are shut off by doors the Dead cannot open. Before the
  walkable rule the post took 34, of which 33 could never reach the player and would have filled the cap. Ruled (owner): a small share may wait behind shut doors - one indoor or
  underground placement in five skips the walkable rule, held to a quarter of the cap (tag `gs_sealed`). Open ground
  sees less of it (town street 15 %, Skadowsky street 6 % visible) because placement is further out; they walk in.
- *Kit*: every rank slot is a weighted choice (`"none"` leaves it empty). Scavengers roll each slot: 20 different
  loadouts in 20. NATO and RUAF keep one uniform per rank and vary the weapon (NATO Riflemen: 12 in the same vest,
  M4A1 6 / HK416D 5 / M16A4 1). RUAF now draws on the CIBR pack already in the player pack (AK-105, AK-103, AK-24,
  AS Val, PKP, SVD), and the RUAF Sergeant wears the MSV vest instead of the KR06 vest NATO's Sergeant wears.
- *Commands*: `/gscraft env <x y z>`, `director passat|survey <x y z> …`, `director room <x z> <radius>`,
  `director horrors <x y z>`.

Related: `gscraft-war-mod-design.md` (the mod), `gscraft-enemies.md` and `gscraft-entities-v8.md` (superseded where
this review says so, once the owner rules), `gscraft-enemy-design-2026-09-08.md` (the capability record),
`gscraft-equipment-inventory.md` (the wardrobe), `gscraft-finale.md` (the Sleeper), map design §6 (the loop).
