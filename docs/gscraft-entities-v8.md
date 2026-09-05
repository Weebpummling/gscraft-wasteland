# GSCraft Wasteland — Everyone and everything that moves (v8)

Draft 1, 2026-09-05. The full roster of NPCs, allies, animals, factions, enemies, elites and bosses for the v8 map,
built from what the pack can actually field (`docs/notes/gscraft-entity-inventory.md`, read from the jars the same
day) and placed on the three lands of `gscraft-objectives-v8.md`. It extends `gscraft-enemies.md` (draft 1: the five
factions, ranks, waves, elites, drops), which stays the reference for the numbers it already gives; where the two
differ, this document wins. Nothing here needs a mod the pack does not carry.

## 0. Rules

1. **Nothing spawns by accident.** `doMobSpawning` stays off. Every living thing is placed by a template or a
   function, ruled by In Control per area, or summoned by the loop. The wasteland is authored, like the map.
2. **Every faction owns a land.** The Dead own the home bank and the river line; the Scavengers the district and the
   roads; the Militia the far bank; the Machines the two edges; the Horrors own the dark between fights and no ground.
3. **A site's occupiers are its faction; a site's counterattack is its faction plus the one it hates.** The faction
   war (Mob Factions) is real: an unclaimed site thins itself, and a held site's ambient stops.
4. **People are villagers with a name; soldiers are Recruits; guards are Guard Villagers.** No mod gives a talking
   NPC, so the survivors and keepers speak through the radio lines and the book (interface doc §3), face their door,
   and sit on a chair so nothing pushes them.
5. **One horror per land at a time, never in a wave.** The horror mods keep their own timers; In Control decides
   where each is allowed.
6. **Names are earned.** A named enemy is an Apotheosis boss definition or an In Control `customname`, summoned by
   the loop at a designed moment; ordinary mobs are anonymous.

## 1. The people (allies and neutrals)

### 1.1 The survivors and the keepers

All are `minecraft:villager` with `NoAI, Invulnerable, PersistenceRequired, Silent`, a `CustomName`, a profession skin,
a `Rotation` toward their door, seated on a `create:seat` or a Refurbished Furniture chair (a seated villager cannot be
shoved off its pad — inventory §3), summoned by their tier function (camp spec §1). Zombies still crowd an invulnerable
villager, which is why every NPC building has a guard from tier 2 and a Magnum Torch from tier 1.

| NPC | Where | Profession skin | Role in play | Counter |
|---|---|---|---|---|
| **Marshall** | the gatehouse | `armorer` | the loop, the walls, the tower, the gun | defences, recruits |
| **Walker** | the yard | IE `machinist` | stations, vehicles, the first gun | guns, ammunition, tools, armour |
| **Tony** | the clinic | `cleric` | revive, infection, the field | medical |
| **Michael** | the plant | IE `engineer` | power, water, the hangar | fuel, power, water |
| **Tune** | the radio shack | IE `electrician` | the board, the map, intel, the pit board | electronics, optics |
| **James** | the lookout | `cartographer` | expeditions, the train, waypoints | maps, kit |
| **Teddy** | the Woods outpost (the farmstead at (−2176, −576)) | Man's `cultist` — the only survivor who looks like the Woods | explosives, propellants (H1–H8) | explosives |
| **Vera** | Skadowsky's hospital | `cleric` | the residential chain, the range card, the second clinic | medical |
| **Kessler** | Novo's foundry | IE `machinist` | the foundry, cast iron | casting sand, cast iron, bronze |
| **Ilya** | the plaza's fuze lab | `librarian` | fuzes, shells | redstone, quartz, fuzes |
| **Rook** | FR-06's steel works | IE `machinist` | steel, the cannon builder, big cartridges | steel plates, cartridges |
| **Oksana** | the waterworks' power house | IE `engineer` | boilers, the boring mill | boiler water, nitrate, drill bits |

Two mod NPCs join them: Pomkot's **Wondering Mech Trader** (`pomkotsmechs:mech_trader`, his own trades) stands in the
hub's mech bay from J-H1 as the only source of mech parts for the team's PMV01B (W-M2) — he trades on his own, no
script; and Recruits' **noble** (`recruits:villager_noble`) is not used (no villages).

### 1.2 The guards

`guardvillagers:guard`, `PersistenceRequired`, patrol point at their building, armed by Pillagers Gun (`Villager
Spawn With Gun = true`: a pistol or a shotgun) or the mod's own iron sword and crossbow; counts per tier as camp spec
§4 (one per building at tier 2, two at tier 3, two and four at the gate). At a held site: two at the anchor. They are
the camp's *shape* — a place with guards at doors reads as held.

### 1.3 The soldiers (Recruits)

Ranks are separate entity types, hired with emeralds at a place that makes sense for each, `OwnerUUID` the hirer,
`FollowState` hold at a post or follow. They ride anything on the `MountWhitelist` — horses, mules, **boats** — so a
squad can be rowed across the lake.

| Rank | Hired at | From | Job |
|---|---|---|---|
| `recruit` (4 em), `recruit_shieldman` (10), `bowman` (6), `crossbowman` (8) | the gatehouse, D2 (Walls 2) | Act II | the gate line; walk one to a held site and order it to hold |
| `horseman` (20), `nomad` (19) | Skadowsky's stables, S-residential-2 | Act III | the far bank's roads; a mounted escort for the truck |
| `scout` | James's lookout, J-B2 | Act II | scouts an area and reports by compass — the in-fiction source of the board's garrison count (U3) |
| `messenger` | Tune's shack, U-B2 | Act II | carries a written note to a player anywhere on the map: the team's runner when voice is not enough |
| `captain`, `commander` | the gatehouse, D4 (Walls 3) | Act III–IV | a squad leader that holds a formation at the gate during the counterattacks |
| `patrol_leader` | never hired — the loop's | — | the site guard's leader (§1.4); the mod's own random patrols are **off** |
| `siege_engineer` | — | — | no siege blocks in the pack; unused |

### 1.4 The site guard

On `held`, `gscraft:siteguard_<site>` summons at the anchor: a `patrol_leader` and four followers (two `recruit`, a
`bowman`, a `recruit_shieldman`), `OwnerUUID` the marker's placer, `FollowState` hold, `AggroState` aggressive, plus
two Guard Villagers; +2 recruits per Walls level, doubled once on `defended`, the keeper's tier 2 adds two more
(design §6.1). Their tag `gscraft_siteguard_<site>` is how the loop counts and replaces them.

### 1.5 Animals

Placed, never spawned (rule 1); Improved Mobs excludes them all; Recruits and villagers eat nothing (`RecruitsStarving`
off).

| Where | What | Why |
|---|---|---|
| the collective farm | cows, sheep, chickens, a pen of pigs, two horses in the barn | D3's kit, Tony's tallow (Immersive Weathering), the horsemen's mounts |
| Skadowsky's stables (S-residential-2) | four horses, two mules | the far bank's escorts; the mule as the pack animal for a bulky item on the Line |
| the Woods | wolves (neutral, Improved Mobs' 5 % aggro), foxes, rabbits | the wilderness bites back a little |
| the lake, the river, the cooling pond | cod, salmon; frogs in the marsh; **drowned** below (§2) | food; the drowned are the lake's Dead |
| the town | cats on the balconies, bats in the cellars | texture; nothing else lives there |
| the far bank | zombie horses (§2.1 the Rider) | the Dead's cavalry, Hordes' `aggressiveZombieHorses` |

## 2. The factions

Six factions on the v8 map — the five of `gscraft-enemies.md` §1 and one new one, **the Machines**, because the pack
carries thirty-seven mech entities and two edges that need an owner.

| Faction | Who | Ids | Land | Signature |
|---|---|---|---|---|
| **The Dead** | the infected town | `zombie`, `zombie_villager`, `husk`, `drowned`, `zombie_horse`, Hordes' converted forms (a zombie villager re-skinned as a dead Scavenger or Militiaman: `infection_conversions.json`), `hordes:zombie_player` (a dead player) | the home bank: the town, the settlement, the farm, the Line; the river line: Skadowsky; the lake's shallows and the cooling pond (drowned) | mass, infection, doors and glass, hear a shot at ten blocks |
| **The Scavengers** | living raiders | `pillager` (guns), `vindicator` (axes), `evoker` (a captain's escort), `ravager` (a breacher's mount, Act III+), `witch` (the cook, the sewers) | the district: Novo, the plaza, Bio Gen, the bus depot; the roads (patrols); the Woods outpost | fire from cover, flank, break doors |
| **The Militia** | the unit that never stood down | `immersiveengineering:commando`, `fusilier`, `bulwark` | the far bank: FR-06, the rail yard, the waterworks' approaches, the plant complex's gates | ranks, shields, a railgun |
| **The Machines** *(new)* | what the plant left running and the city built | `pomkotsmechs:pmss01…03` (tiny), `pms01…10` (walkers and drones), `pmt01…04` (turrets), `pmb01…08` (bosses) | the two edges: the hub (the Custodian's city) and the plant complex (its turrets and the Overseer); a drone over the district | no fear, no doors, ranged from the air; the only enemy that flies |
| **The Horrors** | the dark | `the_knocker:knocker` (+ stalk forms), `man:manfromthefog` (+ forms), `eyesinthedarkness:eyes` | between fights: the Woods (the fog man), Skadowsky's hospital and the sewers (the Knocker), any dark place (the Eyes) | one at a time, never in a wave |
| **The Camp** | the players' | the villagers, `guardvillagers:guard`, every `recruits:` id, `iron_golem` | the camp, every held site | Pillagers Gun arms guards and recruits alike |

`MobFactions.toml` as the design needs it (enemies §2 plus the sixth): `zombie` (the Dead: the vanilla family,
`zombie_horse`, `hordes:*_player`, the Knocker's four registered ids); `skeleton` (background); `illager` (the
Scavengers: pillager, vindicator, evoker, vex, ravager, witch, illusioner); **`militia`** (the three IE ids —
missing today); **`machine`** (every `pomkotsmechs:pms*`, `pmss*`, `pmt*`, `pmb*` id); `civilian` (villager,
iron golem, `guardvillagers:guard`, **all thirteen `recruits:` ids** — missing today). Enemies: everyone hates the
civilians; the Dead hate everyone; the Scavengers hate the Dead and the Militia; the Militia hates the Dead, the
Scavengers and the Machines; the Machines hate everything that breathes. Allies: none. What it buys on the map: the
plant complex's gates are a standing fight between the Militia and the Machines the players can watch from the
viaduct; the district's ambient Scavengers and the Dead from the town's south edge meet on the bus depot's forecourt.

## 3. Ranks

`gscraft-enemies.md` §3 gives the Dead, the Scavengers, the Militia and the Horrors with shares, gear and health;
those tables stand. Additions and the Machines:

### 3.1 The Dead — two more ranks

| Rank | Base | Share | Where | Notes |
|---|---|---|---|---|
| **Rider** | `zombie_horse` with a `zombie` passenger | 3 % | the far bank's fields and the Line at night | Hordes makes the horse aggressive; the first thing that outruns a player |
| **The Converted** | `zombie_villager` with Hordes' pillager / militia skins | replaces Shamblers 1:1 at a held site | Novo and the plaza after their takes, FR-06 after its | a site's dead defenders return as the Dead: the history is visible |
| **The Drowned** | `drowned` (trident) | the lake's Dead | the lake's shallows, the river, the cooling pond; the waterworks' garrison | the reason the boat crossing is not free |

### 3.2 The Scavengers — the mount

| Rank | Base | Share | Act | Notes |
|---|---|---|---|---|
| **Wrecker** | `ravager` with a `pillager` rider | 1 per wave 5–6 | III+ | breaks crops and leaves, charges the gate; the Wrecker is the Scavengers' answer to Walls 2 |

### 3.3 The Machines

| Rank | Ids | Share | Behaviour | Answers |
|---|---|---|---|---|
| **Crawler** | `pmss01…03` | 50 % | tiny, fast, swarm | shotguns, the autocannon |
| **Walker** | `pms01`, `pms02`, `pms05`, `pms07` (ground) | 30 % | rifle and grenade walkers; no doors, no fear | the gun, explosives, AP rounds |
| **Drone** | `pms03`, `pms04`, `pms06`, `pms08…10` (flying) | 15 % | hover, search, dive | the only enemy the autocannon nests exist for |
| **Turret** | `pmt01…04` | placed, not spawned | continuous fire at a fixed post | the plant complex's gates and the hub's wall: approach from the flank, or shell it |
| **Boss** | `pmb01` the **Custodian** (the hub), `pmb03` the **Overseer** (the plant's control room; drops the red boss box), `pmb02` the **Sentinel** (the finale's Machine Captain) | one each | dash, drill, aerial dive | the gun |

Block destruction stays denied (`gscraft_mech_griefing.js`); `targetLockPlayers` on; the mechs never leave their
areas (In Control denies `pomkotsmechs:*` outside `hub`, `plant` and the district's `drone` sphere).

## 4. Where they are

| Land / area (In Control `areas.json`) | Ambient (spawner rules, caps per player) | Occupiers (the sites' garrisons) | Horrors allowed | Patrols |
|---|---|---|---|---|
| **home** — the camp, the town's east blocks, the settlement, the farm, the Line's fields (inside 1.5 km) | the Dead, thin: Shamblers 3, Workers 1; nothing inside the camp outline (the torches) | — | none by day; the Eyes at night beyond the torches | none |
| **town** — the rest of the town | the Dead, dense: Shamblers 8, Workers 2, Runners 1; the Converted in the blocks near the district | the town's landmarks each carry a placed garrison (the palace of culture: a Scavenger squad; the tallest block: the roof boss) | the Knocker in the cellars | a Scavenger road patrol (`ic_patrol`) on the town's south road by day |
| **river** — Skadowsky and the Line's ford | the Dead: Shamblers 6, Workers 2, Runners 2, the Matron's brood | **Skadowsky:** the Dead (the Matron) | the Knocker in the hospital at night | none |
| **district** — Novo, the plaza, Bio Gen, the hempcrete compound, the bus depot | Scavengers: Runners 4, Shooters 2, Breachers 1; the Dead from the town's edge (the faction war) | **Novo:** Scavengers (the Foreman); **the plaza:** Scavengers + a Drone (the Broker); Bio Gen: a Scavenger post; the bus depot: the Scavengers' ammunition dump (W-A5) | the Eyes in the plaza's vault | Scavenger patrols on the district road and the town's south road |
| **farbank** — the rail yard, FR-06, the waterworks, the east-bank road | the Militia: Troopers 3, Shields 1; the Drowned along the shore; Riders at night | **the waterworks:** the Drowned + a Militia post (Rust); **FR-06:** the Militia (Sergeant Kell); the rail yard: a Militia checkpoint (the train's first obstacle) | the fog man on the east-bank road at night | a Militia patrol between the yard and FR-06 |
| **hub** — the walled city | Machines: Crawlers 4, Walkers 2, Drones 1; the mech bay's trader | **the hub:** the Machines (the Custodian) | none | none — the walls |
| **plant** — the plant complex | Machines at the gates (turrets placed, Walkers 2), the Militia inside (their last stand), the Drowned in the cooling pond | **the control room:** the Overseer; the switchyard: a Militia squad | the Eyes in the turbine hall | the Militia vs the Machines at the gates, all day |
| **woods** — the Woods and the farmsteads | Scavengers thin (Runners 2), the Dead thin; wolves | **the outpost:** Scavengers (the outpost captain) until R-W1; the bunkers: the Dead + cave spiders | **the fog man** (his only land by day) | none |

Rules that go with the table: the ambient stops inside a held site's rectangle (`EntityEvents.checkSpawn`, design
§6.1); the ambient of a land never enters the camp outline; no natural spawn anywhere (`doMobSpawning` off) — the
spawner rules are In Control's own, per area, with `maxcount` caps, so an empty area stays empty; horror mods keep
their timers but In Control denies each outside its allowed areas (their summons pass `onjoin`).

## 5. Waves

The composition rule of enemies §4 stands (Body / Breacher / Shooter / Anchor by wave). The v8 order and each site's
faction pair:

| Site (take order) | Assault faction | Counterattack (at the gate) | Elite | Entry point at the camp |
|---|---|---|---|---|
| Skadowsky (Act I) | the Dead only; no Shooter share (the Matron a wave early) | the Dead + Riders in wave 3 | **the Matron** (husk) | the south-east fields |
| Novo (II) | Scavengers | Scavengers + the Converted (the town's Dead follow them) | **the Foreman** (pillager) | the town's east avenue |
| the plaza (II) | Scavengers + one Drone | Scavengers + Drones | **the Broker** (pillager) | the town's east avenue |
| the waterworks (III) | the Drowned + a Militia post | the Militia + the Drowned | **Rust** (drowned) | the lake road |
| FR-06 (III) | the Militia | the Militia + a Wrecker | **Sergeant Kell** (commando) | the lake road |
| the Woods outpost (II, R-W1) | Scavengers, no marker, no counterattack | — | the outpost captain | — |

The finale (finale doc) keeps its five waves and four Captains; the four Captains are now the four fighting
factions' answers: **the Matron's kin** (the Dead), **the Broker's brother** (a Scavenger), **the Colonel** (the
Militia's last officer, `commando`), **the Sentinel** (`pmb02`, the Machines) — one per wave 2–5 — and the Sleeper
rises with the Sentinel. Waves are spawned by `/hordes spawnWave <n>` against per-site tables
(`horde_data/tables/gscraft_<site>.json`, entries with NBT for gear and names) where that command proves to work with
the event disabled (test item T1, §8), else by the loop's `summon` with In Control `finalize` rules dressing each mob.

## 6. Elites and bosses

| Name | Base | Where | Summoned by | What it is |
|---|---|---|---|---|
| the Matron | `husk`, Apotheosis rare, size ×1.5 | Skadowsky's assault | the loop, wave 5 | the first named enemy; she calls Bodies |
| the Foreman | `pillager`, rare, shotgun | Novo | wave 6 | a brawler |
| the Broker | `pillager`, epic, sniper | the plaza | wave 6 | invisibility on hit |
| Rust | `drowned`, rare, trident | the waterworks | wave 6 | retreats into the cooling water |
| Sergeant Kell | `commando`, epic | FR-06 | wave 6 | two Bulwarks escort him |
| the outpost captain | `pillager`, rare, AR | the Woods outpost | R-W1 | Teddy's introduction |
| **the Custodian** | `pomkotsmechs:pmb01` | the hub's plaza | J-H1's approach (the hub's set piece, mod caps §5d) | the hub's guardian; its wreck is W-M2's story |
| **the Overseer** *(new)* | `pomkotsmechs:pmb03` | the plant complex's control room | entering the control room (Act IV) | drops the red boss box; the reactor control module's container opens when it dies |
| the roof boss | Apotheosis overworld zombie boss, rare | the tallest block's roof | W-A6 | the town's one Apotheosis boss |
| the four Captains | as §5 | the finale | the finale script | one per faction |
| the Sleeper | `warden`, named | the finale | the finale script | the boss |

Natural Apotheosis bosses stay off; **minibosses** (`data/apotheosis/minibosses/`) are switched off by a datapack
override, so no random undead knight walks out of the town (inventory §2).

## 7. Drops

Enemies §6 stands (the Dead: cloth, duct tape; Scavengers: casings, gunpowder, scrap, a dog tag; the Militia: IE
revolver parts, plates; Horrors: nothing; elites ×3 + a component). The Machines drop **mech scrap** (`gscraft:mech_scrap`,
a small item Walker salvages into metal scrap and circuit assemblies) at 40 %, a **servo** (a mechanical item) at 10 %;
the Custodian drops its core stone (W-M2), the Overseer the red boss box (the mod's own table). The Rider's horse
drops leather; the Converted drop their old faction's material (a dead Scavenger still has his casings). Marshall's
dog-tag bounty (enemies §9 E2) is a vendor barter: 10 dog tags for a claymore.

## 8. Config and script changes this asks for

| # | Change | File |
|---|---|---|
| C1 | `MobFactions.toml`: add `militia` (the three IE ids) and `machine` (every `pomkotsmechs:` combat id); add all thirteen `recruits:` ids to `civilian`; drop the unregistered `knockerdeadanimal` | `config/MobFactions.toml` |
| C2 | In Control: `areas.json` with `home`, `town`, `river`, `district`, `farbank`, `hub`, `plant`, `woods` (box areas from the objectives doc's rectangles); every `minx/maxx` rule rewritten on `area`; spawner rules per area with the caps of §4; deny each horror id outside its areas; deny `pomkotsmechs:*` outside `hub`/`plant`/the district's drone sphere; the `hostile → deny` `onjoin` rule narrowed to `spawntype natural` so summons, waves and bosses pass (**test T1** first) | `config/incontrol/*.json` |
| C3 | Improved Mobs: `Difficulty Increase` two steps (`0-0`, `1500-6`); add `pomkotsmechs:` ids to the exclusion list (the mod must not arm a mech); keep the Knocker's stalk forms excluded | `config/improvedmobs/common.toml` |
| C4 | Hordes: per-site wave tables `gscraft_<site>.json`; remove `bogged` from `skeletons.json`; keep the event off | `config/hordes/data/hordes/horde_data/tables/` |
| C5 | Apotheosis: `gscraft:elite_<site>`, `gscraft:captain_<n>` boss definitions; minibosses overridden to empty | `data/gscraft/bosses/`, `data/apotheosis/minibosses/` |
| C6 | Recruits: `ShouldRecruitPatrolsSpawn=false`; `MountWhitelist` keeps `boat`; hire prices as §1.3; `AllowClaiming=false` | `serverconfig/recruits-server.toml` |
| C7 | Guard Villagers: `Villager Spawn With Gun=true`; Pillagers Gun: `Bazooka Chance` 0 | `config/guardvillagers-common.toml`, `config/PillagersGun-common.toml` |
| C8 | The Man From The Fog: `break_blocks=false` (the camp's buildings are locked but the farmsteads are not) | `config/man_config.toml` |
| C9 | Zombie Awareness: `enhancedMobs` gains the drowned and husk (they already hear); the mechs are not added (they lock on anyway) | `config/zombieawareness/` |
| C10 | The NPC summons: `Rotation`, the seat entity, the profession ids of §1.1; `npc_teddy` with Man's `cultist` | camp spec §1 functions, `camp.py`, `site.py` |
| C11 | Mob drop tables: `gscraft:mobs/machine` added to enemies §6's sheet; the Converted use their old faction's table | `data/gscraft/loot_tables/mobs/` |
| C12 | The loop: the site guard's `patrol_leader`; the Overseer's summon on entering the control room and the container it opens; the Custodian's existing hook | `gscraft_loop.js` |

**Test T1 (before any of this is built):** with `doMobSpawning=false` and In Control's `onjoin` deny rule, confirm
that `/summon`, `/hordes spawnWave`, `/apoth spawn_boss` and a datapack template's entities actually appear on the
local server; the inventory suspects the rule swallows them. Everything in §4–§6 depends on the answer.

## 9. Open decisions

| # | Question | Default |
|---|---|---|
| D1 | The Machines as a sixth faction, or the mechs kept as the hub's set piece only | a faction: two edges need an owner and the pack has 37 mech ids |
| D2 | The Overseer (`pmb03`) as the plant complex's boss and the reactor module's gate | yes — the far edge needs a fight, and the mod's only boss loot table is his |
| D3 | The Converted at held sites (Hordes' re-skinned zombie villagers as the site's dead defenders) | yes; it costs one NBT line per summon |
| D4 | Riders on the far bank | yes, 3 %, night only |
| D5 | The fog man's land: the Woods only, or the Woods and the east-bank road at night | both |
| D6 | Teddy's cultist skin | yes (the profession exists; it is the joke the Woods deserves) |
| D7 | Recruits riding boats to FR-06 | allowed; a squad in a rowing boat is the Act III picture |
