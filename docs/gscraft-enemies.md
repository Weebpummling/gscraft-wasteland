# GSCraft Wasteland — Enemies: factions, ranks, equipment

Draft 1, 2026-09-04. What the design has had until now is **counts**: design §6.3 says "zombies 8,
bandits 2" per wave and leaves who they are, what they carry and how they fight to the pack's
defaults. This document is the other half — the five factions, their ranks, the equipment each rank
carries, how a wave is composed out of them, and the exact config changes that make it true. Every
capability named here was checked in the jars; §8 lists what has to change and the four defaults
that are actively wrong for this design.

## 0. Principles

1. **Equipment is designed, never rolled.** In Control! sets a mob's held item, off-hand, four
   armour slots, potion effects, name and health per spawn rule (verified: the rule keys exist in
   the jar). Improved Mobs' random equipment is switched off so no zombie turns up in netherite
   because the RNG said so; Improved Mobs keeps only the jobs it is good at — attribute scaling by
   distance, block-breaking, ladders.
2. **Nothing an enemy carries ever drops.** Pillagers Gun `Drop Chance` is 0 and Improved Mobs
   `Should drop equipment` is false, and both stay that way. Working guns and armour come from the
   station or they do not come at all (crafting §5). Enemies drop **materials**, never products.
3. **Every faction is legible at fifty metres.** A player should name what is coming from its
   silhouette and its noise: the Dead shamble and moan, Scavengers shout and shoot, the Militia
   marches in line and reflects light, the Horrors are alone and quiet.
4. **Factions fight each other.** Mob Factions is configured so an unclaimed site is a three-way
   war the players can watch, wait out, or start.
5. **Difficulty is distance, then act.** Improved Mobs scales attributes by distance from the crater;
   the equipment tables step up per act. A zombie at the hub is not the zombie outside the gate.

## 1. The five factions

| Faction | Who they are | Entity ids | Where | How they fight | Signature |
|---|---|---|---|---|---|
| **The Dead** | the infected: what the city became. No leadership, no equipment, endless | `minecraft:zombie`, `zombie_villager`, `husk` (dry ground), `drowned` (the plant, the lake), `minecraft:spider` / `cave_spider` (sewers, bunkers) | everywhere; the residential block is theirs | mass, no ranged, break glass and wooden doors, hear gunfire at 10 blocks per Zombie Awareness | infection (Hordes): every hit rolls 75 % on a player, curable at Tony's clinic |
| **Scavengers** | living raiders in dead men's clothes — the faction the players could have become | `minecraft:pillager` (guns, via Pillagers Gun), `minecraft:vindicator` (axes, breachers), `minecraft:evoker` (rare, a captain's escort) | Novo, Financial Plaza, the road outposts, the Woods outpost | fire from cover, flank, break doors; a captain rallies them | the only faction that uses guns from the first act |
| **The Militia** | a surviving military unit that never stood down; they hold FR-06 and answer to nobody | `immersiveengineering:fusilier` (railgun), `immersiveengineering:commando` (revolver), `immersiveengineering:bulwark` (shield, armour) | FR-06, the reactor plaza, the hub's approaches | disciplined ranks: Bulwarks forward, Commandos behind, a Fusilier holding the long line | armour that shrugs off pistols; the only faction with a shield wall |
| **The Horrors** | whatever the end of the world left behind. Not a faction that holds ground — they hunt | `the_knocker:knocker` (+ `knockerstalk`, `knockerstalklooked`, `knockerdeadanimal`, `knockerswim`), `man:manfromthefog` (+ `managgresive`, `manfromthefogback`, `mftfhang`), `eyesinthedarkness:eyes` | the block after dark, the sewers, the Woods, any site's elite slot | alone, at night, from behind; they do not join waves | no drops, no reason, no negotiating |
| **The Camp** (the players') | the six survivors, their guards and hired soldiers | `guardvillagers:guard`, the ten `recruits:` ids (recruit, recruit_shieldman, bowman, crossbowman, captain, commander, horseman, nomad, scout, messenger), `minecraft:villager`, `iron_golem` | the camp, and every held site's guard | Pillagers Gun arms guards and Recruits too (`Villager Spawn With Gun` = true) | the only faction that respawns for free |

**Wildlife** is not a faction: the pack's passive mobs are food and Tony's tallow, and Improved Mobs'
"neutral aggro" chance is left at its 5 % so the wasteland occasionally bites back.

## 2. The faction war

`MobFactions.toml` already defines five factions; two corrections make it read the way §1 describes:

| Faction | Entities | Enemies | Note |
|---|---|---|---|
| zombie | zombie, zombie_villager, husk, drowned, zombified_piglin, zoglin, the Knocker's five | illager, **militia**, civilian | the Knocker rides with the Dead, as now |
| skeleton | skeleton, stray, wither_skeleton | illager, militia, civilian | background only; no site is theirs |
| illager | pillager, vindicator, ravager, evoker, vex | zombie, skeleton, militia, civilian | the Scavengers |
| **militia** (new; replaces `piglin`) | `immersiveengineering:fusilier`, `commando`, `bulwark` | zombie, skeleton, illager, civilian | the piglin faction's only member that appears here is the zombified piglin at a ruined portal, and it is already listed with the Dead |
| civilian | villager, iron_golem, `guardvillagers:guard`, **all ten `recruits:` soldiers** | zombie, skeleton, illager, militia | Recruits are missing from the shipped list, so hired soldiers are currently invisible to every hostile faction — the fix that matters most in this file |

What it buys: an unclaimed site thins itself. A team that scouts Financial Plaza at dusk and waits
sees Scavengers and the Dead fight over it; the assault is easier for the patience. It also means a
site's ambient population is never a fixed number, which is the texture In Control! caps alone cannot
give.

## 3. Ranks and equipment

Each faction has three or four ranks. The **rule** column is the In Control! `spawn.json` entry that
dresses it: a rule matched on mob type + the site rectangle, with the equipment fields set. Armour is
listed helmet/chest/legs/boots; `—` is bare. Act columns give what the rank carries when the players
first meet it and what it upgrades to; the upgrade is a second rule gated on the act's stage.

### 3.1 The Dead

| Rank | Share | Act I–II | Act III–IV | Health | Notes |
|---|---|---|---|---|---|
| Shambler | 70 % | — | leather helmet 20 % | ×1.0 | the baseline; Improved Mobs adds the distance scaling |
| Worker | 20 % | iron helmet, held: `minecraft:iron_shovel` | iron helmet + chest | ×1.2 | the ones that were digging when it happened; these are the block-breakers |
| Runner | 8 % | — | — | ×0.8, speed ×1.3 | husk model, sprints; the reason a wall matters |
| Bloater | 2 % | — | — | ×3.0, size ×1.4, slowness I | dies loudly; Act III onward only |

The Dead never carry a ranged weapon and never carry a gun. Their pressure is numbers, the block
break whitelist, and infection.

### 3.2 Scavengers

Pillagers Gun arms every pillager (`Armed Chance` 1.0) with **its own** guns, not TaCZ's — no ammo
economy, no drops, and the mod's inaccuracy tuning already reads as human. The roll per pillager is
the mod's: pistol 50 %, shotgun 20 %, assault rifle 20 %, sniper 5 %, bazooka 5 %.

| Rank | Entity | Share | Act I–II | Act III–IV | Notes |
|---|---|---|---|---|---|
| Runner | pillager | 45 % | pistol (mod), leather chest | pistol + chainmail chest | the numbers |
| Shooter | pillager | 30 % | assault rifle, leather chest/legs | AR + iron chest, Speed I | fires from cover; the reason to bring a suppressor |
| Breacher | vindicator | 20 % | held `iron_axe`, leather helmet | `diamond_axe`, iron helmet/chest | doors, gates and fences; the wall's actual test |
| Marksman | pillager | 4 % | — | sniper (mod), leather chest, Invisibility off, `customname` "Marksman" | one per wave at most; laser sight renders, so it is fair |
| Captain | pillager | 1 % | shotgun, iron helmet, `customname` "Scavenger Captain", health ×2 | + Apotheosis affixes (§5) | the elite slot at Novo and the Plaza |

**Bazooka rank is cut.** `Bazooka Chance` goes to 0: an explosion level 5 at the camp gate would take
out Marshall's gatehouse, which the grief lock cannot stop because mob explosions are cancelled only
inside the locked rectangles (design §3.6). The flamethrower stays at 5 %, `Break Block` false.

### 3.3 The Militia

The three IE entities need no dressing — they ship armoured and armed, and their drops (§6) are the
only source of IE revolver parts in the world.

| Rank | Entity | Share | Behaviour | Health |
|---|---|---|---|---|
| Trooper | `commando` | 60 % | revolver at range, closes to melee | ×1.0 |
| Shield | `bulwark` | 30 % | walks in front, blocks projectiles | ×1.5, knockback resistance 0.6 |
| Gunner | `fusilier` | 10 % | railgun; the longest reach any enemy has | ×1.2 |

The Militia never spawns ambient outside FR-06 and the hub's approaches: they are a *place*, not a
weather. Act IV adds a fourth rank, **Sergeant** (`commando`, health ×2.5, `customname`, an Apotheosis
rare affix), one per FR-06 wave.

### 3.4 The Horrors

No ranks, no equipment, no scaling — the mods' own configs govern them (`knocker.toml`,
`eyesinthedarkness-server.toml`, and The Man From The Fog's defaults). Design rule: **one horror per
site at a time, and never inside a wave.** They are the reason the sites are frightening between
fights, not a difficulty dial.

## 4. Wave composition

An assault is six 45-second waves; a counterattack at the base is three (design §6.2). Each wave is
built from four **roles**, and each role is answered by a different part of the players' preparation —
that is the point of the composition.

| Role | Who fills it | What it does | What answers it |
|---|---|---|---|
| **Body** | Shamblers, Runners, Scavenger Runners | walks in, absorbs, occupies the guns | Walls 1 barricades, the site guard, a machine gun |
| **Breacher** | Workers, Vindicators | breaks glass, fence gates and wooden doors (the Improved Mobs whitelist) | Walls 2 blast doors and steel fence — neither is on the whitelist, so a stone wall is genuinely safe |
| **Shooter** | Scavenger Shooters, Commandos, Fusiliers | ranged pressure from outside melee | cover, the guards' own guns, killing them first |
| **Anchor** | Bulwarks, Bloaters, the wave's elite | slow, tough, forces the team to commit | explosives (Teddy's chapter), the Humvee's turret, focus fire |

Composition by wave, as a share of that wave's count:

| Wave | Body | Breacher | Shooter | Anchor |
|---|---|---|---|---|
| 1–2 | 80 % | 20 % | — | — |
| 3–4 | 55 % | 20 % | 25 % | — |
| 5 | 45 % | 15 % | 30 % | 10 % |
| 6 (and counterattack 3) | 35 % | 15 % | 35 % | 15 % + the elite |

The counterattack's three waves use waves 2, 4 and 6 of the site's own table, at the camp gate. A
site's faction decides which entity fills each role; a site with no Shooter faction (the residential
block) fills the Shooter share with more Body and its elite arrives a wave earlier — the block is
meant to feel like drowning, not like a firefight.

## 5. Elites and named enemies

Every site's elite is an Apotheosis boss definition (`gscraft:elite_<site>`, design §6.3 / gap C14),
summoned by the loop script at the named wave. Definitions to write in Phase D:

| Site | Elite | Base | Rarity | Gear set | Affix flavour |
|---|---|---|---|---|---|
| Novo | **The Foreman** | pillager | rare | shotgun, iron helmet | knockback, thorns — a brawler |
| Residential block | **The Matron** | husk | rare | — , size ×1.5 | summons Bodies, slowness aura |
| Industrial plant | **Rust** | drowned | rare | trident, chainmail | wet ground, ranged, retreats to water |
| FR-06 | **Sergeant Kell** | commando | epic | revolver, iron chest | armour piercing, escorted by two Bulwarks |
| Financial Plaza | **The Broker** | pillager | epic | sniper, leather | invisibility on hit, calls one wave early |
| The Woods outpost | **the outpost captain** | pillager | rare | AR | plain — the Woods is Teddy's introduction, not a boss fight |

Rules: **natural Apotheosis bosses stay off** (`Boss Spawn Cooldown` at maximum), so an affixed mob is
always a designed moment; an elite never spawns twice on the same site; killing one drops its
faction's material at ×3, never its gear.

## 6. Drops and the economy

| Faction | Drops | Why |
|---|---|---|
| The Dead | rotten flesh (vanilla), **cloth** 20 %, **duct tape** 5 % | the bandage chain has a floor that does not depend on containers |
| Scavengers | **casings** 40 %, **gunpowder** 25 %, **metal scrap** 20 %, a **dog tag** 5 % | ammunition never runs dry if you fight for it; the dog tag is Marshall's bounty (§7 open) |
| Militia | vanilla emerald + IE `gunpart_barrel` / `drum` / `hammer` (their own tables), **plate** 15 % | the only source of IE revolver parts — deliberate: the Militia is where a revolver comes from |
| Horrors | nothing | by design |
| Elites | their faction's material ×3, plus one **component** at the sites whose container the design already names | the elite is worth the fight without being the only route |

`gscraft:mobs/<faction>` loot tables, added to the loot sheet as sheet 2. No table drops a working
gun, armour piece, intermediate or complete part — the same rule the container tables follow.

## 7. Difficulty

Improved Mobs' `DISTANCESPAWN` scaling is centred on the world spawn, which v8 puts on the Warium plaza at (−1490, −2230): the design's rings
and the mod's steps already agree, and the steps are tuned to them —

| Distance | Improved Mobs level | Ring | What it means |
|---|---|---|---|
| 0–1,500 | 0 → 3 | foot | the camp's own ruins and Novo: no attribute bonus worth naming |
| 1,500–2,500 | 3 → 6 | road (near) | the block, the plant: +health, occasional armour |
| 2,500–4,000 | 6 → 10 | road (far) | FR-06, the Plaza: enemies that survive a magazine |
| 4,000+ | 10 → 15 | air | the hub: everything is harder than anything on the ground |

Act progression rides on top through the equipment tables (§3): the same pillager that met the
players with a pistol outside Novo meets them with an assault rifle and iron armour at the Plaza.
Improved Mobs' own caps stay as shipped (max +5 health, +3 damage, +0.1 speed) so the curve is
*equipment*, not arithmetic.

## 8. Config changes, and four defaults that are wrong

| # | File | Change | Why |
|---|---|---|---|
| 1 | `improvedmobs/common.toml` | `Stealer Chance` 0.3 → **0.0** | **Wrong today.** Verified in the jar: `StealGoal` holds `blackListedContainerBlocks` and `lootRandomItem` — mobs open containers and take an item. Every loot container, every dossier chest, the players' own base storage and the component containers are open to them; the loot design assumes a chest still holds what it rolled |
| 2 | `improvedmobs/common.toml` | `Item Blacklist` = every TaCZ, Superb Warfare, vvp and MCSP weapon tag; `Item Whitelist` false | **Wrong today.** A mob can pick up and use anything dropped in a fight, including a player's rocket launcher on death |
| 3 | `improvedmobs/common.toml` | `Equipment Chance` 0.1 → **0.0**, `Weapon Chance` 0.5 → **0.0**, `Enchanting Chance` → 0.0 | equipment is In Control!'s job (§0.1); leaving both on means two systems dressing the same mob |
| 4 | `PillagersGun-common.toml` | `Bazooka Chance` 0.05 → **0.0** | an explosion at the camp gate outside a locked rectangle; §3.2 |
| 5 | `MobFactions.toml` | replace the `piglin` faction with `militia` (the three IE ids); add the ten `recruits:` ids to `civilian` | §2 — hired soldiers are currently not in any faction |
| 6 | `incontrol/spawn.json` | the per-site, per-rank rules of §3 (each with `mob`, the site rectangle, `maxcount`, and the equipment fields) | the tables above are only real when the rules exist |
| 7 | `improvedmobs/common.toml` | `Difficulty Increase` steps → `["0-0","1500-3","2500-6","4000-10","4500-15"]` | already correct; recorded here so a later edit does not undo the ring alignment |
| 8 | `apotheosis/adventure.cfg` | boss spawn cooldown at maximum; the six `gscraft:elite_*` definitions | §5, gap C14 |

Rows 1, 2, 4 and 5 are the four wrong defaults. Rows 1 and 2 are also the two that can quietly ruin a
session, so they go in before the next player test, ahead of the rest of this document.

## 9. Open questions

| # | Question | Recommendation |
|---|---|---|
| E1 | **Do Scavengers talk?** A captain that shouts before a wave (a `say` from the loop script, or signs left at their camps) gives the faction a voice; silence keeps them animal | one line per wave from the captain, written like radio chatter, off by a config flag if it grates |
| E2 | **Dog tags as a bounty** — Marshall pays per tag (a vendor barter, `gscraft-vendors.md`) | yes: it makes killing Scavengers anywhere worth something without touching the loot economy |
| E3 | **Does the Militia ever talk to the players?** A surrendered Commando as a vendor, or a truce quest, is a whole chapter's worth of design | not in this build; note it as the season-two hook the finale doc already wants |
| E4 | **Infection on Scavengers** — should the Dead convert killed Scavengers into more Dead? Hordes can do it (`infectionEntitiesAggroConversions`) | yes at sites the players have not taken, no during a counterattack (the wave would grow while they fight it) |
| E5 | **Horror frequency** — one per site is the design rule; the mods' own configs currently decide | set each mod's spawn chance from the site rules in Phase D and measure it on the first play test |

Related: `gscraft-map-design.md` §6 (the loop, the garrison tables these ranks fill),
`gscraft-loot-tables.md` (sheet 2 is §6 above), `gscraft-crafting.md` §5 (why nothing drops),
`gscraft-finale.md` (the Sleeper and its waves), `gscraft-vendors.md` (E2's barter).
