# GSCraft — entity inventory (what the pack can field)

Reference for the entity/faction roster, built 2026-09-05 from the 103 jars in `G:\GSCraft\server\mods`
(each `assets/<modid>/lang/en_us.json`, `data/<modid>/` tags and loot tables, class-string scans where a lang
file lies) and the shipped configs. It lists what exists; the design lives in `gscraft-enemies.md`, map design
§3/§6.3, camp spec §4 and the Create chapter §3. Citation shorthand: **mods/** =
`server/mods`, **config/** = `server/config`, **sc/** = `server/wasteland-v8/serverconfig`, **lang** = that jar's
`en_us.json`.

**Natural spawning today is off everywhere.** `server.properties` has `spawn-monsters=false`; the v8 `level.dat`
carries `doMobSpawning=false` and `mobGriefing=false` (v7 still has both `true`); and `config/incontrol/spawn.json`
rule 3 is `{"when":"onjoin","hostile":true,"result":"deny"}` with no `spawntype` filter. The "spawns naturally"
column below therefore means *would spawn once those three are lifted, under the mod's own config*. Test item:
`onjoin` fires on every join (hence rule 4's `spawntype` exemption for zombies) and rules are first-match unless
`continue` is set, so rule 3 may also swallow `/summon`, Hordes waves and `/apoth spawn_boss` for hostiles.

## 1. Living entities by mod

Kinds: **H** hostile, **N** neutral, **P** passive, **A** ally/ownable, **B** boss, **V** vehicle (no AI),
**E** emplacement/device, **X** projectile or utility (ignore).

### Vanilla (`minecraft:`) — the base of every faction

| Group | Ids | Kind | Behaviour | Spawns naturally |
|---|---|---|---|---|
| the dead | `zombie`, `zombie_villager`, `husk`, `drowned` (trident, ranged in water), `zombie_horse` (aggressive per Hordes `aggressiveZombieHorses`) | H | melee, break wooden doors on Hard, target villagers; Zombie Awareness and Improved Mobs enhance them | In Control `spawner.json` rule 1 (weights 10/3/2/1, 0.55/s, cap via `mincount` 24 per player) |
| bones | `skeleton`, `stray`, `wither_skeleton`, `skeleton_horse` | H | bow (Improved Mobs `Entity Item Use Blacklist` keeps their bows) | spawner rule 2 (0.14/s, cap 4) |
| crawlers | `spider`, `cave_spider` (poison, small gaps) | H/N | neutral in light | spawner rule 3 (cap 3) |
| illagers | `pillager` (crossbow → gun via Pillagers Gun), `vindicator` (axe, breaks doors), `evoker` (fangs, vexes), `vex` (flies, phases), `illusioner`, `ravager` (rideable by illagers, breaks crops/leaves), `witch` | H | raid party; `#minecraft:raiders` | spawner rule 4 `ic_patrol` (0.025/s, day only, not in villages); Recruits `PillagerSpawn=false`, `ShouldPillagersRaidNaturally=false` (sc/recruits-server.toml) |
| others | `creeper`, `phantom`, `slime`, `enderman`, `zombified_piglin`, `piglin`/`piglin_brute`/`hoglin`/`zoglin` (Nether; Hordes `piglinsHoglinsConvert=false`), `guardian`, `warden` (the Sleeper — finale doc) | H/N | as vanilla | none |
| civilians | `villager` (5 IE professions + Man's `Cultist` + Recruits' noble also register), `wandering_trader`, `iron_golem`, `snow_golem` | P/A | trades, golem defends | villages (Hostile Villages `vanillaVillageChance` 80, `allowVanillaVillagerSpawn` true); `OverrideIronGolemSpawn=true` in Recruits |
| animals | `cow`, `pig`, `sheep`, `chicken`, `horse`/`donkey`/`mule`, `llama`, `camel`, `goat`, `wolf`, `cat`, `fox`, `rabbit`, `polar_bear`, `bee`, fish, `frog`, `axolotl`, `sniffer`, `allay`, `bat` | P/N | food, mounts (Recruits `MountWhitelist`: mule, donkey, horse, llama, pig, boat, minecart) | `spawn-animals=true` but blocked by `doMobSpawning=false`; all are in Improved Mobs' exclusion list |

### The Hordes 1.6.3g (`hordes:`) — 3 living

`zombie_player`, `husk_player`, `drowned_player` (mods/The-Hordes…/config_defaults lang: "Zombie Player" etc.; class
`HordesEntities`). Kind H. A dead infected player's corpse-zombie carrying their drops (`zombiePlayersStoreItems`),
never burns, survives peaceful. Spawn: only from a player's infection death (`infectionSpawnsZombiePlayers=true`) or
`/hordes spawnZombie <username> <pos> <type>`. The mod adds no other mob; its "zombie pillager/vindicator/evoker/
illusioner/witch/wandering trader/piglin brute" are **zombie_villager with a texture + `chat_name` NBT**
(`config/hordes/data/hordes/infection/infection_conversions.json`), so a converted Scavenger is a re-skinned villager
zombie.

### Recruits 1.15.2 (`recruits:`) — 13 living

| Id (lang name) | Kind | Behaviour (classes in mods/recruits…/entities) |
|---|---|---|
| `recruit` (Recruit), `recruit_shieldman`, `bowman`, `crossbowman`, `horseman` (rides a horse, `HorsemanAttackAI`), `nomad` (mounted archer) | A when hired, N unhired | melee/bow/crossbow/shield; follow, wander, hold, patrol, mount any `MountWhitelist` entity incl. boats/minecarts (`RecruitMountEntityGoal`), open doors, eat from upkeep chest, dodge, flee TNT/fire |
| `captain` | A | leader; sail/ship control (SmallShips, absent), strategic-fire orders |
| `commander` | A | leader with `AttackController` |
| `patrol_leader` (unnamed in lang) | A/N | `AbstractLeaderEntity`: waypoints, patrol speed, states IDLE/PATROLLING/RETREATING/ENEMY_CONTACT; the friendly patrols of `ShouldRecruitPatrolsSpawn=true` (15 %, every 30 min, despawn 45) |
| `messenger` | A | walks/teleports to another player with a message or treaty (`IsTreatyMessenger`) |
| `scout` | A | scouts an area, reports by compass direction (`ScoutingResult`) |
| `siege_engineer` | A | crews ballista/catapult controllers (siege blocks not in pack) |
| `villager_noble` | P | a trading villager variant (`TRADES`, `TraderLevel`); spawns in villages (`NobleVillagerSpawns=true`) |

`AssassinEntity` exists as a class only (no registry entry). Pillagers Gun tags the recruit types into
`#forge:pillager_gunner`, so recruits spawn with its guns.

### Guard Villagers 1.6.19 (`guardvillagers:`) — 1 living

`guard` (Guard). Kind A. Made by handing a sword or crossbow to an unemployed villager (advancement text in lang);
armour from `data/guardvillagers/loot_tables/entities/guard_armor.json` (iron sword or crossbow, chainmail/iron
pieces at low chances). Config (`config/guardvillagers-common.toml`): 6 per village, health 20, phalanx on, patrol
off, follow only with Hero of the Village, teleport-follow, opens doors, clerics heal 3×/day, smiths repair, attacks
all hostiles except creeper/enderman/villager/golem, converts to zombie villager when killed by a zombie, inventory
locked below reputation 15. Spawns only in villages. The jar also ships spawn eggs for vanilla illusioner, iron golem,
snow golem.

### Immersive Engineering 10.2.0 (`immersiveengineering:`) — 3 living (+14 X)

`fusilier` (railgun), `commando` (revolver), `bulwark` (shield). Kind H. Tagged into `data/minecraft/tags/entity_types/
raiders.json`, so they **join vanilla raids** and count as illagers for Guard Villagers/Mob Factions purposes. Their
loot tables (`data/immersiveengineering/loot_tables/entities/*.json`) drop revolver parts when killed by a player. No
natural spawn outside raids. Non-living: `skylineHook`, `explosive`, `fluorescentTube`, four storage minecarts,
`chemthrower_shot`, `railgun_shot`, `sawblade`, four revolver shots.

### The Knocker 1.5.2 (`the_knocker:`) — 4 living

`knocker`, `knockerstalk`, `knockerstalklooked`, `knockerswim` (all "Knocker"; `TheKnockerModEntities`). Kind H.
Stalk → observed → attack states; the swim form is `#minecraft:aquatic`; knocks on doors/windows, cannot be slept
through (advancement). `knockerdeadanimal`, listed in `MobFactions.toml` and Improved Mobs' `Entity Configs`, **is not
registered** in this build. Spawn: `config/knocker.toml` `spawn_rate="rare"`, `respect_difficulty=true` (vanilla
biome spawner, so gated by `doMobSpawning`).

### The Man From The Fog 1.4 (`man:`) — 4 living

`manfromthefog` (stalking), `managgresive` (chasing), `manfromthefogback` (retreating), `mftfhang` (the hanging
figure; own natural-spawn condition). Kind H. Own timer, not the vanilla spawner: `config/man_config.toml`
`enable_spawning=true`, `min/max_spawn_rate` 5000–20000 ticks, `spawn_at_day=true`, `climbing`, `break_blocks=true`
(hardness 2, 5 when searching), jumpscare, darkness effect, lightning, vanish at 30 m, chase 400–1000 ticks. Also
registers the villager profession **Cultist** (`entity.minecraft.villager.man.cultist`), the fog house worldgen, a
cassette recorder and "Cassette 1: Safety Instructions".

### Eyes in the Darkness 1.3.10 (`eyesinthedarkness:`) — 1 living

`eyes`. Kind H. Approaches in the dark, screech/jumpscare (off: `Jumpscare=false`), can attack while lit
(`EyesCanAttackWhileLit=true`). Own spawn cycle (`config/eyesinthedarkness-server.toml`): `EnableNaturalSpawn=true`,
every 600 ticks (300 at midnight), max 1 per player, 15 per dimension, within 64 blocks.

### Pomkot's Mechs alpha.8 (`pomkotsmechs:`) — 28 in lang, ~9 more registered

| Series (tag) | Ids | Kind | Behaviour (class bases) |
|---|---|---|---|
| `#pomkotsmechs:pms_series` | `pms01`…`pms10` | H | `BaseSmallMonsterEntity`: walking/flying drones (`FlyingMobGoal`, `MaintainAltitudeGoal`, `SearchDroneGoal`, `RollerDashGoal`), rifles/grenades/missiles |
| `#pmss_series` | `pmss01`…`pmss03` | H | `BaseTinyMonsterEntity` |
| `#pmb_series` | `pmb01`, `pmb01mk2`, `pmb02`…`pmb08` (+ unnamed `pmb99`, `pmc01`, `pmc02`) | B | `BaseBossEntity`: dash, drill, aerial dive, helicopter hover, orbital fly; `pmb03` drops `pomkotscube/factory/red_boss_box` (only entity loot table) |
| `#pmt_series` (unnamed) | `pmt01`…`pmt04` | E | `BaseTurretEntity`, continuous fire |
| player mechs | `pmv01`, `pmv01b`, `pmv02`, `pmv03`, `pmvc01` (+ `pmvt01`) | V | `PomkotsVehicleBase`; ridden, parts/weapons from 200 items; core stones |
| NPCs | `mech_trader` ("Wondering Mech Trader", `TraderInventory`), `mech_pilot`, `arena_receptionist` (spawn eggs only) | P/A | trader has trades; pilot is a `PathfinderMob` that enters mechs (`FindAndEnterMechGoal`) |

`#scan_targets` = pmvc01 + the four series (radar/lock-on). Config `config/pomkotsmechs.json`:
`enableEntityBlockDestruction=false`, `targetLockPlayers=true`, `survivalModeEnabled=false`. Spawn: only the hub
rules in `spawn.json`/`spawner.json` (`pms01`, `pms03`, cap 4, tag `ic_hub_mechs`) — which use `minx/maxx` keys In
Control rejects (see §2), plus the datapack's `summon pomkotsmechs:pms…` placements.

### Superb Warfare 0.8.8 (`superbwarfare:`) — 1 living, 24 V, 9 E, 25 X

- Living: `senpai` ("Beast Senpai", `SenpaiEntity` Monster) — `spawn_senpai=false` (`config/superbwarfare-server.toml`).
- Vehicles (`entity/vehicle/*Entity`, no AI, player-driven): `speedboat`, `wheel_chair`, `truck`, `lav_150`, `bmp_2`,
  `yx_100`, `prism_tank`, `plz_05`, `type_63`, `ah_6`, `mi_28`, `a_10a`, `tom_6`, `drone`, `mortar`, `tow`, `mk_42`,
  `mle_1934`, `bl_132`, `annihilator`, `laser_tower`, `hpj_11`, `waveforce_tower`, `vehicle_assembling_table`.
  `AutoAimableEntity` base: the laser tower, HPJ-11 CIWS and wave-force tower aim themselves — the only automated
  defences in the pack; targets exclude `#superbwarfare:seek_blacklist`.
- Emplacements/devices: `claymore`, `c4`, `tm_62`, `blu_43`, `ptkm_1r` (`#mine`), `target`, `dps_generator`
  (`#no_experience`), `medical_kit`, `smoke_decoy`/`flare_decoy` (`#decoy`).
- The rest are shells, rockets, missiles, bombs, grenades (`#aerial_bomb`, `#at_rocket`, `#destroyable_projectile`).

### vvp 0.2.0 (`vvp:`) — 28 V registered (56 lang keys)

`ModEntities` registers: `mi_24`, `mi_28`, `cobra`, `ah_64`, `bmp_2`, `bmp_2_bakhcha`, `bmp_2m`, `bmp_3`,
`bradley`, `brm`, `btr_4`, `centauro`, `challenger`, `gaz_tigr`, `leopard_2a4`, `leopard_2a7v`, `m1a2_sep`,
`pantsir_s1`, `puma`, `stryker`, `stryker_m1296`, `t72_b3m`, `t90_m`, `terminator`, `ural`, `varta`, `varta_ptrk`,
`ags_30`, `kornet` (+ `pantsir_missile` X). The other lang keys (`uh60`, `f_16`, `su_25`, `tu22m3`, `toyota`,
`m60`, `humvee`, `mi_8*`, `zu23`…) have **no registry entry** — the mod-utilization audit has it backwards: `mi_24`
is registered, the Mi-8s are not. SW vehicle framework (`data/vvp/sbw/vehicles`), no AI.

### MCSP 1.0.8 (`mcsp:`) — 25 V

Typhoon-K ×2, Humvee RWS ×3 (`humvee_standart_camo`, `humvee_carc`, `humvee_sand`), BMD-4 ×2, Sprut-SD ×2, M3A3
Bradley ×6 (BUSK II/III, sand), M1A2 ×4, Ural-4320 ×2, TOS-1A ×2, T-90A ×2; projectiles `cannon_shell`,
`small_cannon_shell`, `swarm_drone`. SW framework, no AI.

### Immersive Vehicles 24.0.0 + MTS Official Pack V29 + OAmP V3 (`mts:`) — 0 living

IV registers builder entities only (`builder_existing`, `builder_seat`, `builder_rendering`, `builder_base`,
`builder_charger`, `builder_fluidtank`, `builder_inventory`; `InterfaceLoader`). Vehicles are pack JSON:
MTS Official = `ft17` (Renault FT), `bell206`, `comanche`, `mc172`, `pzlp11`, `bell47g`, `trimotor`, `scout`,
`gmcbrig`, `e500`, `quad`, `vulcanair`, `merc230`, `pzl37los`, `fordmustang69`, `skyhawk`, `firetruck` (17) plus 88
parts (guns are parts), 30 poles, 16 decors, 24 bullets. No driver AI; a vehicle without a player is scenery.

### Everything else

| Mod | Living | Non-living entities / note |
|---|---|---|
| Create 6.0.8 | 0 | `contraption`, `carriage_contraption`, `gantry_contraption`, `stationary_contraption`, `seat`, `package`, `super_glue`, `crafting_blueprint`, `potato_projectile` |
| Create Big Cannons 5.11.4 | 0 | `cannon_carriage` (V), `pitch_contraption`, 20 shells/shot/bursts, `smoke_emitter`, `traffic_cone` |
| Apotheosis 7.4.8 | 0 | 4 arrows; **24 boss definitions** `data/apotheosis/bosses/{overworld,the_end,the_nether,twilight}/` (overworld: husk, skeleton, stray, vindicator, witch, zombie), **5 minibosses** `data/apotheosis/minibosses/` (craig, honeyed_archer, undead_knight, fast_enderman, withering_archer), 14 gear sets |
| Farmer's Delight | 0 | `rotten_tomato` |
| TaCZ 1.1.8 | 0 | `target_minecart`; `#tacz:whitelist` lists villager/wandering_trader/boats as click-through |
| Lootr | 0 | `lootr_minecart` |
| GeckoLib 4.8.4 | 0 | 9 lang example entities (`mutant_zombie`, `gremlin`…), not registered in release |
| Mob Factions, Hostile Villages, Bandits (`enableMod=false`, five classes, no lang), Keerdm ZAE (13 loot tables + LC buildings), Underground Bunkers, Lost Cities (`generateSpawners=true` in `profiles/wasteland.json` → vanilla spawner blocks in buildings), Refurbished Furniture (652 lang keys, 0 entities), Custom Starting Gear, Player Animation, Better Combat | 0 | — |

**Living count per mod:** vanilla ~70 (listed by group), hordes 3, recruits 13, guardvillagers 1,
immersiveengineering 3, the_knocker 4, man 4, eyesinthedarkness 1, pomkotsmechs 28 named (+ ~9 unnamed),
superbwarfare 1; vehicles: superbwarfare 24, vvp 28, mcsp 25, mts 17+8 JSON, createbigcannons 1, pomkotsmechs 6.

## 2. The tools that shape them

**In Control 9.5.0** (`mods/incontrol-1.20-9.5.0.jar`, class `rules/support/RuleKeys`). Accepted keys, by file:
- *conditions*: `mob`, `hostile`, `passive`, `mod`, `dimension`, `dimensionmod`, `biome`, `biometags`, `biometype`,
  `structure`, `structuretags`, `hasstructure`, `incity`, `instreet`, `inbuilding`, `inmultibuilding`, `insphere`,
  `building`, `multibuilding`, `cave`, `block`, `blockoffset`, `blocktest`, `light`, `minlight`/`maxlight`
  (`_full`, `_sky`), `minheight`/`maxheight`, `mindist`/`maxdist`, `minspawndist`/`maxspawndist`, `mintime`/`maxtime`,
  `mindaycount`/`maxdaycount`, `mindifficulty`/`maxdifficulty`, `mincount`/`maxcount` (number or
  `{amount,mob,perplayer}`), `seesky`, `weather`, `random`, `spawner`, `spawntype`, `baby`, `player`, `realplayer`,
  `fakeplayer`, `helditem`/`playerhelditem`/`offhanditem`/`bothhandsitem`, `lack*`, `helmet`…`boots`, curio slots,
  `nbt`, `scoreboardtags_all`/`_any`, `state`/`pstate`/`phase`, `gamestage`, seasons, `slime`, `notcolliding`,
  `canspawnhere`, `area`, `kubejs`, `continue`.
- *actions*: `result` (allow/deny/default), `when` (`onjoin`/`finalize`), `healthset/add/multiply`, `speed*`,
  `damage*`, `armor*`, `armortoughness*`, `attackspeed*`, `followrange*`, `knockback*`, `knockbackresistance*`,
  `size*`, `customname`, `helditem`/`offhanditem`/`armor*` (equip), `potion`/`potionnoparticles`, `angry`, `fire`,
  `nodespawn`, `addscoreboardtags`, `addstage`/`removestage`, `setblock`, `message`, `customevent`, `eventspawn`,
  `setphase`/`clearphase`/`togglephase`, `setstate`/`setpstate`, `remove`/`removeall`, `item`/`itemcount`/`drop`,
  `addxp`/`setxp`/`multxp`, `give`, `setheldamount`/`sethelditem`, `timeout`.
- **Not keys: `minx`, `maxx`, `minz`, `maxz`, `miny`, `maxy`.** The audit's finding stands; the hub-mech rules in
  `spawn.json` and the conditions block of `spawner.json` rule 5 carry them. Rectangles go in
  `config/incontrol/areas.json` (`AreaParser`: `name`, `type` box/sphere/ellipsoid/cylinder, `dimension`, `center`,
  `dimx`/`dimy`/`dimz`) and rules reference `"area":"<name>"`. `phases.json` (`PhaseRule`: `name`, `conditions`) and
  `/incontrol setphase|clearphase|phases` drive `phase`. `spawner.json` (`SpawnerRule`): `mob`/`weights`,
  `mobsfrombiome`, `persecond`, `attempts`, `amount{minimum,maximum,groupdistance}`, `addscoreboardtags`, `phases`,
  `conditions{dimension, mindist/maxdist, minheight/maxheight, min/maxverticaldist, min/maxdaycount, norestrictions,
  validspawn, sturdy, inwater/inlava/inliquid/inair, maxthis/maxlocal/maxtotal/maxhostile/maxpeaceful/maxneutral,
  and/or/not}`. `loot.json` is live (zombie-family drops: string, gunpowder, SW ammo boxes 2 %, food). `effects.json`,
  `events.json`, `summonaid.json`, `experience.json` are `[]`. `sc/incontrol-server.toml`: `perPlayerRadius=100`.

**Mob Factions 1.0.0** (`config/MobFactions.toml`, classes `Factions`, `FactionAttackGoal`, `Events`). Four
parallel strings: `Factions`, `Entities` (bracketed per faction), `Enemies`, `Allies`. Mechanically: on entity setup
every `Mob` whose type is in a faction gets a `FactionAttackGoal` (a nearest-attackable-target goal) that targets any
mob whose faction is on its enemy list and skips allies; a hurt event retargets the attacker. "Civilian" members
(villager, golem, guard) therefore get targeted but only fight if they already have attack AI. Runtime commands
`/faction create|addEntity|addEnemy|addAlly|remove|display|reset` edit saved `FactionData`. Shipped: zombie (+ the
Knocker's five ids, one dead), skeleton, illager, piglin, civilian; **no `recruits:` or `immersiveengineering:` id
is in any faction.**

**Improved Mobs 1.13.7** (`config/improvedmobs/common.toml`, `equipment.json`). Affects Monster-class mobs unless
listed. `[general]`: `Difficulty type=DISTANCESPAWN`, `Difficulty Increase=["0-0","1500-3","2500-6","4000-10",
"4500-15"]` (distance rings), `Ignore Spawner`, `Punish Time Skip`. `[list] Entity Configs`: ids with optional flags
`ALL, ATTRIBUTES, ARMOR, HELDITEMS, BLOCKBREAK, USEITEM, LADDER, STEAL, GUARDIAN, PARROT, TARGETVILLAGER,
NEUTRALAGGRO, PEHKUI, REVERSE` — bare id = excluded from everything (the shipped list excludes every recruit, guard,
villager, animal and the Knocker's stalk forms); the `* Whitelist` booleans flip each flag to whitelist. `[ai]`:
`Block Break Whitelist` (glass, panes, fence gates, wooden doors), `Breaker Chance` 0.3, `Breaking items`, `Break
BlockEntities`, `Stealer Chance` 0.3, `Neutral Aggressive Chance` 0.05, `Guardian/Phantom Chance` 0.5, `TNT Block
Destruction` false. `[equipment]`: `Equipment Chance` 0.1, `Weapon Chance` 0.5, `Enchanting Chance` 0.2, `Item
Blacklist`/`Item Use Blacklist`, `Entity Item Use Blacklist` (keeps vanilla ranged mobs' own weapons), `Should drop
equipment` false; `equipment.json` = per-slot item → `[weight, quality]` (weight + quality × difficulty; SW hammers,
batons, IE steel tools, potions, TNT are in it). `[attributes]`: max health +5, damage +3, speed +0.1, knockback,
magic/projectile/explosion resistance caps.

**Recruits** (`sc/recruits-server.toml`; NBT from `AbstractRecruitEntity`). Hire: right-click an unhired recruit →
"Hire for <n> emeralds" (`RecruitCurrency=minecraft:emerald`; recruit 4, bowman 6, crossbowman 8, shieldman 10,
horseman 20, nomad 19; `MaxRecruitsForPlayer` 100). NBT: `OwnerUUID`, `Hired`, `Group`, `AggroState`
(passive/neutral/aggressive/raid), `FollowState` (follow/wander/hold/protect/back), `HoldPos*`, `MovePos*`,
`MountUUID`, `PROTECT_ID`, `Level`/`Xp` (`RecruitsMaxXpLevel` 20, 250 xp per level), `Kills`, `Moral`, `Hunger`,
`Team`. **Ranks are separate entity types**, not promotions; levels only raise stats. `Owner` unset = neutral
hireable; `RecruitsPayment=false`, `RecruitsStarving=false`, chunk loading on. Factions: banner + 10 emeralds, 5
players, 500 NPCs, diplomacy. Claims: `AllowClaiming=true`, 64 + 15/chunk, 50 chunks, siege = 10 recruits for 10 min,
`ExplosionBreaksBlocksInClaims=false`, fog of war. Patrols on (§1). Start kits per type in `[Equipments]`.
`TargetBlackList` = creeper, ghast, enderman, zombified piglin, corpse.

**Guard Villagers** — behaviour in §1; the levers are `config/guardvillagers-common.toml` (`Guards attack all
mobs?`, `Mob Blacklist`/`Whitelist`, patrol, follow) and `PersistenceRequired` on summon (camp spec §4).

**Apotheosis 7.4.8** (`mods/Apotheosis…/data/apotheosis/bosses/overworld/zombie.json`). Definition shape:
`entity`, `weight`, `quality`, `size{width,height}`, `valid_gear_sets` (`"#overworld"` or gear-set ids),
`dimensions`, `min_rarity`/`max_rarity`, `stats{<rarity>: {enchant_chance, enchantment_levels[4], effects[{effect,
chance}], attribute_modifiers[{attribute, operation ADDITION|MULTIPLY_BASE, value <n> or {min,steps,step}}]}}`;
optional `nbt`, `mount`, `name`. Gear sets (`data/apotheosis/gear_sets/*.json`): `weight`, `quality`, `mainhands`/
`offhands`/`boots`/`leggings`/`chestplates`/`helmets` as weighted `{stack:{item,nbt}}`, `tags`. Command
(`BossCommand`): `/apoth spawn_boss <boss> [<rarity>]`; also `item.apotheosis.boss_summoner` and the `boss_spawner`
block. `config/apotheosis/adventure.cfg`: `Boss Spawn Cooldown=2147483647` (natural bosses off), `Random Affix
Chance` 0.075, `Gem Drop Chance` 0.045, boss glow + announce 96 m. **Minibosses** (`data/apotheosis/minibosses/`)
replace ordinary mobs at random and are not governed by the boss cooldown — a datapack override to empty is the
switch if unwanted.

**Hordes** (`config/hordes-common.toml`, `config/hordes/data/hordes/`). Event: `enableHordeEvent=false`,
`hordesCommandOnly=false`, 8 per wave ×1.05, interval 600, max 30, speed 1.1, multiplayer ×0.8. Wave tables
`horde_data/tables/{default,drowned,illagers,mixed_mobs,skeletons}.json`: entries are `"id{nbt}-weight-first_day-
last_day"` strings or `{entity, weight, first_day, last_day, nbt}` (jockeys via `Passengers`; `bogged` in
`skeletons.json` is a 1.21 id that will not resolve). `horde_data/scripts/default.json` picks a table by conditions
(`hordes:biome`, `hordes:not`, `set_spawn_type prefer_water`). Commands (lang): `/hordes spawnWave <n>`, `/hordes
start <ticks>`, `/hordes stop`, `/hordes reset [player]`, `/hordes spawnZombie`, `/hordes listEntities` — the design
docs' `SpawnHordeWave` is the class name; the literal is `spawnWave`. Whether `spawnWave` works with the event disabled
is untested. Infection: `infection_entities.json` (zombie family 0.7–0.8 per hit), `playerInfectionResistance` 0.25,
4 stages × 6000 ticks, `wearables_protection.json` (armour 5–20 %), `immunity_items.json` (enchanted golden apple),
`infection_conversions.json` (villager/horse/piglin/hoglin/illagers → zombie forms), `infectionEntitiesAggroConversions
=true`, `zombiesBurn=false`, `zombieVillagersCanBeCured=false`, `illagersHuntZombies=true`.

**Custom Starting Gear 2.0.3**: `/csg_config give|login|wipe|item_deletion_blacklist` saves the executor's inventory
to `config/brandon3055/CSG/Config.json` (empty today); `/csg_kits <name> give|kits` for named kits; players are
tagged `csg:receivedInventory`. **Zombie Awareness** (`config/zombieawareness/*.toml`): `awareness_Sound=true`,
`awareness_Scent=false`, `awareness_Light=true`, `noisyZombies=true`, `wanderingHordes=false`, strengths 10, sight
16, `enhancedMobs` = zombie, husk, creeper, skeleton, stray, witch, zombie_villager (`enhanceableMobs` names the
mech, fog-man, IE and Knocker ids as candidates). **Pillagers Gun 3.1.0**: arms every entity in
`#forge:pillager_gunner` (`data/forge/tags/entity_types/pillager_gunner.json` = `minecraft:pillager` + the recruit
types) at `Armed Chance` 1.0, and `guardvillagers:guard`/recruits via mixins when `Villager Spawn With Gun=true`;
roll pistol 0.5 / shotgun 0.2 / AR 0.2 / sniper 0.05 / bazooka 0.05; `Drop Chance` 0; `Break Glass` true; TaCZ compat
on but `Spawn With TACZ` false; no flamethrower item exists. **Lootr**: container instancing only (`refresh_modids=
["gscraft"]`, 120000 ticks). **Player Animation Lib / Better Combat**: player-side animation and
melee; recruits' swords use Better Combat reach, nothing else here is affected.

## 3. Vanilla villagers as NPCs

A villager summoned with `NoAI:1b, Invulnerable:1b, PersistenceRequired:1b, Silent:1b, CustomName, CustomNameVisible,
VillagerData:{profession,level,type}` **can**: hold a name and profession skin (14 vanilla + IE's engineer,
machinist, electrician, outfitter, gunsmith + Man's cultist + Recruits' noble), open the vanilla trade screen on
right-click with `Offers:{Recipes:[…]}` written by `/data merge` (vendors doc: sneak+right-click reaches the vanilla
interaction; KubeJS 1.20.1 has no villager-trade events), give trade XP and honour Hero-of-the-Village discounts, be
seated by riding a seat entity (Refurbished Furniture chairs, `create:seat`, a minecart), face a fixed direction via
`Rotation`. It **cannot**: restock (restocking is a brain task, so the script rewrites `Offers`), look at players
(look controller is part of AI — the head is fixed), path, sleep, gossip, level up on its own, wear or render armour,
pose (no pose NBT for villagers), or resist being pushed by players and pistons. It **still**: draws zombies,
Knockers-with-Mob-Factions and IE raiders as a target (they will crowd it; invulnerability only stops the damage),
is click-through for TaCZ guns (`#tacz:whitelist`), and counts for Guard Villagers' "protect villagers" goal. Hordes
infection on an invulnerable villager is untested (the hit is cancelled before the hurt event).

**Talking/quest NPC mods: none** — no Custom NPCs-style mod, no dialogue tree. Nearest substitutes: Recruits'
entities open a GUI (hire screen unhired, order inventory hired) and speak canned lines (`chat.recruits.text.*`:
"Hello my friend."); the messenger carries a player-written message; Pomkot's `mech_trader` trades and
`arena_receptionist` runs the arena; FTB Quests carries the text; KubeJS `EntityEvents.interact` on a tagged
villager is the design's mechanism (map design §3).

## 4. Building each kind

| Entity kind | Build from |
|---|---|
| shambling infected | `minecraft:zombie`/`husk`/`drowned` + Hordes infection (already on) + In Control `finalize` rule for health/speed/name; Improved Mobs breaker whitelist for door-breaking |
| runner / bloater / named zombie | same base + In Control `speedmultiply`, `sizemultiply`, `healthmultiply`, `customname`, `potion` |
| a zombie that infects players | any id in `infection_entities.json` (add an id there to make anything infect) |
| a dead player | `hordes:zombie_player` via `/hordes spawnZombie` |
| armed human bandit | `minecraft:pillager` (+Pillagers Gun automatic) or `vindicator` (axe); dress with In Control `helditem`/`armor*`; a `recruits:recruit` with `Owner` unset and `AggroState` raid is the alternative when it must use a real sword/crossbow and hold a post — but Pillagers Gun arms it too |
| bandit captain / site elite | Apotheosis boss JSON `gscraft:elite_<site>` on the base mob + `/apoth spawn_boss`; or In Control `customname` + multipliers for a cheap elite |
| disciplined soldiers with guns | `immersiveengineering:commando`/`fusilier`/`bulwark` (ship armed; `#raiders`) — add to a Mob Factions faction to make them fight others |
| friendly guard that holds a point | `guardvillagers:guard` (`PersistenceRequired`, patrol point) or `recruits:*` with `OwnerUUID` set, `FollowState` hold, `AggroState` neutral |
| hireable mercenary | `recruits:recruit`/`bowman`/`crossbowman`/`recruit_shieldman`/`horseman`/`nomad` unhired at the gatehouse (`RecruitCurrency` emerald) |
| mounted scout / messenger | `recruits:horseman`, `nomad`, `scout`, `messenger` |
| roaming friendly patrol | `recruits:patrol_leader` + followers (or the mod's own patrols, `ShouldRecruitPatrolsSpawn`) |
| horror (lone stalker) | `the_knocker:knocker`, `man:manfromthefog`, `eyesinthedarkness:eyes` — own spawners; summon the aggressive forms (`managgresive`, `knocker`) for a scripted appearance |
| mech (ambient/boss) | `pomkotsmechs:pms01…10` walkers/drones, `pmss01…03` small, `pmb01…08` bosses, `pmt01…04` turrets; block-breaking already denied |
| automated defence | `superbwarfare:laser_tower`, `hpj_11`, `waveforce_tower` (auto-aim), `claymore`, `tm_62`; IE gun turret block; CBC autocannon on a mount |
| player vehicle / wreck | `mts:` pack vehicles (17+8), `superbwarfare:` 24, `vvp:` 28, `mcsp:` 25, `pomkotsmechs:pmv*`; unmanned = scenery with health |
| animal / livestock | vanilla animals (placed, not spawned while `doMobSpawning` is off; Magnum emerald torch for CREATURE suppression) |
| trading / quest NPC | `minecraft:villager` NoAI+Invulnerable with `Offers` and a KubeJS interact handler; Recruits' `villager_noble` or Pomkot's `mech_trader` for a mod-driven trader |
| faction war on a site | `MobFactions.toml` factions + In Control `spawner.json` per area (`area` from `areas.json`) with `maxcount` caps |
| wave attack | `/hordes spawnWave <n>` against a custom `horde_data/tables/<site>.json`, or In Control `eventspawn`/datapack `summon` with `finalize` rules dressing each mob |
| finale boss | `minecraft:warden` named (finale doc) + Apotheosis Captains (`/apoth spawn_boss`) |
