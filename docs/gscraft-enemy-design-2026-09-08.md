# GSCraft Wasteland — Enemy design pass (2026-09-08)

A design pass over the enemy roster, run because the pack changed under the design. `gscraft-enemies.md`
is draft 1 of 2026-09-04 and `gscraft-entities-v8.md` draft 1 of 2026-09-05; the Superb Warfare addon
swap landed 2026-09-06 and brought a new armed hostile, seven auto-turrets and a wardrobe of military
kit that neither document knows about. This pass asks three questions and answers them from the jars:
what can an enemy in this pack actually **do**, what can it **wear and carry**, and what should it **be**.

It layers on `gscraft-entities-v8.md`, which stays the roster of record. Where this document and the two
above differ on a **capability** claim, this one wins — those were re-read from the jars and the live
configs on 2026-09-08. On placement and the map, entities-v8 wins.

Nothing proposed here needs a mod the pack does not carry.

## 1. Can an enemy use a gun? The four mechanisms, settled

There are exactly four ways a non-player in this pack can end up shooting, and they are not
interchangeable.

| # | Mechanism | Works? | Cost |
|---|---|---|---|
| 1 | **Pillager's Gun's own guns** | **Yes — in use today** | nothing; already on |
| 2 | **Pillager's Gun driving a TACZ gun** | **Yes — capability live, spawn table empty** | two config lines |
| 3 | **Superb Warfare's own mob-gun system** | Works, but **rejected** (§1.4) | a flag the author says not to set |
| 4 | **Improved Mobs holding a gun** | **No.** It cannot fire one at all | — |

### 1.1 Pillager's Gun is the pack's NPC gunner, and the tag is the lever

`EventHandler.onEntityJoin` tests the Forge entity-type tag **`forge:pillager_gunner`** and attaches
`GunAttackGoal`, plus `TaczGunAttackGoal` when TACZ is loaded and `TACZ Compat` is true. The goal is a
real gunner: it reloads, works the bolt, honours fire mode, checks ammunition, and arbitrates friendly
fire via `GuardUseGun.checkFriendlyFire` / `RecruitUseGun.checkFriendlyFire`.

The shipped tag — unmodified on this server, verified by grepping every json/js/toml under
`G:/GSCraft/server` — is `minecraft:pillager`, six `recruits:` ids and `guardvillagers:guard`. **Only one
of those eight is hostile.** Adding hostile entity types to that tag via datapack is the highest-leverage
change available in this document, and it is a tag file, not code.

Two things the standing design should record explicitly:

- **The camp's own guns depend on this tag.** entities-v8 §1.2 and C7 arm guards and recruits via
  `Villager Spawn With Gun`. That works *only* because those ids are in `forge:pillager_gunner`.
  **MusketMod is not installed**, so Recruits' and Guard Villagers' own gun compat
  (`IWeapon.isMusketModWeapon` matching six `item.musketmod.*` translation keys,
  `ModCompat$UseMusketGoal`) is dead code against items that do not exist. Nobody should remove
  Pillager's Gun on the theory that Recruits has its own gun support. It does not, here.
- **`SbwCompat` is cosmetic only.** It maps Pillager's Gun's five guns onto `ModItems.AK_47 / M_1911 /
  M_870 / M_98B / RPG` for model and fire sound, behind `"Gun Model Switch"` (currently `false`). The
  projectile stays Pillager's Gun's. A free silhouette upgrade with no ballistics change (§3.2).

### 1.2 TACZ: 164 guns, reachable, unused

`"TACZ Compat" = true` already, but `"Spawn With TACZ" = false` and `"TACZ Gun Type" = []`, so no NPC
ever spawns with one. The capability is live; the table is empty.

Three gun packs are installed under `G:/GSCraft/server/tacz/` — the default pack, `CIBR_GunsPack_v0.2`
and `Cyber Armorer-1.1.4.3.1`. Every weapon is one item, `tacz:modern_kinetic_gun`, with the gun as NBT
`GunId`, so anything that supports "a TACZ gun" supports all of them at once:

| pack | pistol | smg | rifle | sniper | shotgun | mg | rpg | total |
|---|---|---|---|---|---|---|---|---|
| `tacz` (default) | 14 | 5 | 17 | 6 | 6 | 4 | 2 | 54 |
| `cib` (CIBR) | 8 | 4 | 30 | 10 | 6 | 6 | 1 | 65 |
| `cibs` (skins) | 1 | — | 8 | 1 | — | — | — | 10 |
| `cyber_armorer` | 13 | 5 | 5 | 5 | 5 | — | 2 | 35 |

**164 ids.** Period-appropriate picks for this map are in the default and CIBR packs — `tacz:ak47`,
`type_81`, `sks_tactical`, `m16a1`, `kar98`, `m870`, `rpk`, `cib:ak103`, `svd`, `ppsh41`. The Cyber
Armorer pack is cyberpunk and tonally wrong for the wasteland; it should be excluded from enemy tables
by choice rather than left to a weight roll.

**Three traps for whoever writes the tables:**

1. Pillager's Gun reads accuracy and laser behaviour off the TACZ **`type` string**, and three packs
   mis-declare melee weapons: `cib:batons` and `cib:katana` are typed `sniper`; `cyber_armorer:mantis_blade`
   and `mantis_blade_maxtac` are typed `rpg`. A mob handed a katana is treated as a sniper.
2. **`"Gunner Needs Ammo In TACZ" = false`** cancels the ammo check by mixin — armed NPCs have
   **infinite ammunition and never reload-starve**. That is a difficulty decision being made by a default,
   not by the design. Setting it `true` gives gunners a finite magazine and spare mags, which is what a
   scavenging fiction wants.
3. `"TACZ Render Laser" = ["sniper"]` draws a visible laser for sniper-type guns — exactly the fairness
   tell `gscraft-enemies.md` §3.2 wanted for its Marksman, for free.

### 1.3 Improved Mobs cannot fire a modded gun — the standing design overstates this

`ItemAITasks.initVanilla()` is the entire registry: `instanceof` tests for bow, crossbow, shield and the
two potion classes, plus seven hardcoded vanilla items (snowball, ender pearl, lava bucket, flint and
steel, TNT, trident, enchanted book). `ItemUseGoal.canUse()` ends `return this.ai != null`, so an
unregistered item never starts the goal, and there is no fallback to `Item.use`. Its TACZ compat exists
only on the 1.21.1 branch, which is Fabric/NeoForge — unreachable from here.

So `gscraft-enemies.md` §8 row 2 needs restating. Its stated danger — "a mob can pick up and use anything
dropped in a fight, including a player's rocket launcher on death" — is wrong twice:

- `Item Blacklist` sits under `[equipment]` and is documented in the file itself as *"Blacklist items from
  whole mods. Add modid to prevent items from that mod being **equipped**."* It governs the equipment
  pool, not battlefield pickup.
- **No gun is in the pool.** The live `equipment.json` MAINHAND list is 37 items: vanilla melee, bow,
  crossbow, TNT, trident, potions, and Superb Warfare's melee family. Not one firearm from any mod.

The row still earns a place, but as **hygiene against regeneration** — `equipment.json` is generated by
sweeping the item registry, so a regeneration after a mod change could sweep guns in. Keep the modid
blacklist, drop the emergency framing. It is not one of the four wrong defaults.

What Improved Mobs *can* drive is worth more than the design uses: TNT, lava buckets, flint and steel,
ender pearls and splash/lingering harming potions are all on its working list and all already in the
pool. That is a usable toolkit — §3.5.

### 1.4 Superb Warfare's mob guns: real, and rejected

SBW 0.8.9 ships a complete data-driven mob gunner — `entity/goal/GunShootGoal`, `data/mob_guns/*`,
`event/EntityUseGunEventHandler`, datapack files at `data/<namespace>/sbw/mob_guns/<mob>.json`. The
firing chain is `Entity`-typed throughout, so it is genuinely not player-gated, and the goal aims, paths,
reloads and honours RPM.

**Recommendation: leave it off.** The reasons are specific:

1. The config comment is, verbatim in the shipped jar: `this feature is under development, DO NOT TURN
   THIS ON!` — `spawn_mob_with_guns`, default false.
2. `GunShootGoal.tick()` compares a **squared** distance against the raw `ShootDistance`, so the default
   30 has mobs closing to about 5.5 blocks before firing, with a `// TODO` on it upstream. A gunner that
   walks into melee to shoot is worse than no gunner.
3. The goal attaches only on `EntityJoinLevelEvent` with `!loadedFromDisk()` — spawn-time only.
4. The shipped example is inert: `skeleton.json` sits under `data/superbwarfare/`, keying as
   `superbwarfare:skeleton`, while lookup uses `EntityType.getKey()` = `minecraft:skeleton`.

**Config-path warning:** `G:/GSCraft/server/config/superbwarfare-server.toml` is a **stale leftover** from
a pre-0.8.9 build — its `[spawn]` section has only `spawn_senpai`. The live file is
`wasteland-v8/serverconfig/superbwarfare-server.toml`. Editing the former does nothing. Worth recording,
because it will waste somebody's afternoon.

Note that constraint 3 may apply to the Pillager's Gun path too: both goals are attached on entity join.
Whether `TaczGunAttackGoal` re-reads the main hand each tick — and so whether a gun handed to a mob
already in the world works — is **not settled**; the two investigations disagreed. It does not affect
this design, which dresses everything at spawn or `finalize` through In Control, but test it before
relying on hand-off at runtime.

## 2. What an enemy can wear and carry

All ids verified present in the shipped jars on 2026-09-08.

### 2.1 The wardrobe, by what it reads as

| Look | Head | Chest | Note |
|---|---|---|---|
| **US military** | `superbwarfare:us_helmet_pasgt` | `superbwarfare:us_chest_iotv` | the cleanest "real soldier" silhouette in the pack |
| **Russian military** | `superbwarfare:ru_helmet_6b47` | `superbwarfare:ru_chest_6b43` | a second army that is not the first |
| **Older / looted mil** | `superbwarfare:ge_helmet_m_35` | — | a WW2 shell: reads scavenged, not issued |
| **Modern tactical** | `dragonrise_reforge:fast_helmet`, `t21_helmet`, `kr06_helmet`, `sniper21_helmet`, `aljin_helmet`, `cnfast` | `dragonrise_reforge:kevlar`, `kr06_chest`, `msv_chest`, `med21_chest`, `cnjustchest` | six helmets and five vests — enough for ranks *within* one faction |
| **Peacekeeper** | `dragonrise_reforge:un_helmet` | — | a blue helmet on a corpse tells a story for free |
| **Camouflage** | — | `dragonrise_reforge:desert07_*`, `ocean07_*`, `gorka3`, `cn21` | terrain-specific dress |
| **Industrial / electrical** | `immersiveengineering:armor_faraday_helmet` | `armor_faraday_chestplate` (+ legs, boots) | insulated rubber — reads as plant worker, and is thematically exact at the switchyard |
| **Heavy industrial** | `immersiveengineering:armor_steel_*` | full set | the Militia's current look |

This is the pass's plainest finding: **the design specifies leather and iron while a full military
wardrobe sits unused in the pack.** `gscraft-enemies.md` principle 3 — "every faction is legible at fifty
metres" — is currently carried by silhouette and noise alone. It does not have to be.

### 2.2 Melee, and why it matters more than it sounds

`superbwarfare:steel_pipe`, `crowbar`, `knife`, `military_shovel`, `t_baton`, `electric_baton`, the
hammer family, plus `immersive_weathering:ice_sickle`, IE's `axe_steel` / `sword_steel`, and Farmer's
Delight's five knives.

A Scavenger with a steel pipe and a Scavenger with an iron sword are different characters. The Dead's
Worker rank currently carries `minecraft:iron_shovel`; `superbwarfare:crowbar` or `military_shovel` says
the same thing better and both are already in the equipment pool.

### 2.3 The armed human the design does not have

**`dragonrise_reforge:terrorist`** — `extends Monster implements GeoEntity, RangedAttackMob`,
`MobCategory.MONSTER`, hitbox 0.6 × 2.0.

| | |
|---|---|
| Health / armour | 20 / **12** |
| Speed / attack / follow | 0.28 / 8 / 64 |
| Ranged goal | `RangedBowAttackGoal`, interval 30, **radius 35** |
| Fire pattern | 3-round bursts, one round per 2 ticks, next burst 20 + rand(20) ticks |
| Projectile | `superbwarfare:projectile`, damage 4, **zero gravity**, velocity 15, inaccuracy 2 |
| Targeting | `NearestAttackableTargetGoal(Player, mustSee=false, mustReach=false)` — unprovoked |
| Variant | 30 % **Runner**: speed ×1.4, +3 attack |
| Spawning | **no biome modifier, no `SpawnPlacements`, no structure** — spawn egg or `/summon` only |

It holds a `minecraft:bow` cosmetically to satisfy the bow goal; the actual shot is the SBW bullet. So
none of §1.4 applies to it — it needs no flag and no datapack.

Three things to fix before it is used:

1. **No lang entry.** It displays as `entity.dragonrise_reforge.terrorist`. A lang override in the pack's
   own datapack is required — an untranslated name on screen reads as a broken install.
2. **Its drop table is `enchanted_golden_apple` 1 % / `golden_apple` 20 % / `apple`.** Golden apples are
   the `hordes:infection_cures` tag. An enemy that drops the infection cure at 20 % quietly dismantles the
   infection economy that defines the Dead. It needs a `DeathLootTable` override to
   `gscraft:mobs/scavenger` — non-negotiable if it ships.
3. Its model is a fixed skin, so unlike a pillager it cannot be re-dressed from §2.1.

### 2.4 Auto-turrets — seven of them, and they will not shoot players

| Mod | Self-engaging ids |
|---|---|
| Superb Warfare | `laser_tower`, `hpj_11`, `waveforce_tower` |
| Dragon Rising | `npds114`, `npds514`, `npds810` |

All six extend `AutoAimableEntity`; the three DR classes are empty subclasses inheriting SBW's logic
verbatim. `autoAim()` runs when there is **no passenger** and `ACTIVE == true` — riding one disables it.

**The correction that matters.** Target selection accepts a candidate if it is a `LivingEntity`
implementing `net.minecraft.world.entity.monster.Enemy` with health > 0 — *any hostile mob, no owner or
team needed* — or a threatening projectile. Players and vehicles go through `basicEnemyFilter`, which
reads:

```
if (e instanceof Projectile) return false;
owner = getOwner(); if (owner == null) return false;
if (e.getTeam() == null) return false;          // no scoreboard team => never an enemy
if (e.isAlliedTo(owner) || e.isAlliedTo(this)) return TDMSavedData.enabledTDM(e);
return true;
```

**With no scoreboard teams in use — and Mob Factions does not use them — these turrets can never target a
player.** They shoot hostile mobs and incoming projectiles. The mod's own manual says as much: the laser
tower is "ideal for keeping zombies out of your backyard".

So they are **not** an enemy emplacement. They are a *player-side* defence and a faction-war prop. §3.6
is written accordingly.

Other details for whoever places them: `ACTIVE` defaults `false` and is armed by sneak + right-click,
which also stamps `OWNER_UUID` (both NBT-persisted, so a summon can set them). Seek range 72 / 128 / 256
blocks; every acquisition costs 500–5,000 FE, and `hpj_11` and the NPDS trio also need physical shells.
`annihilator`, `mortar` and every other SBW/DR vehicle are player-crewed or player-designated and never
autonomous.

### 2.5 Two hostiles that exist but are switched off

`superbwarfare:senpai` — a `Monster` with `NearestAttackableTargetGoal(Player)`, 24 HP, speed 0.23,
attack 5, follow 64, knockback resistance 0.5. It ships a biome modifier but is gated behind
`spawn.spawn_senpai = false`. `superbwarfare:steel_coil` is neutral-until-hit, gated the same way.

**Recommendation: leave both off,** on tone rather than capability. "Beast Senpai" is an anime joke mob;
it would be the only thing on the map that is not taking itself seriously. Noted here so the next person
who finds the flag knows it was a decision, not an oversight.

## 3. Proposed designs

### 3.1 The Militia becomes the pack's real soldiers

They are the faction the wardrobe was made for, and today they are three IE entities in IE's own kit —
three elite units with **no line infantry**, which is why they read as a checkpoint rather than an army.

| Rank | Base | Head | Chest | Weapon | Change |
|---|---|---|---|---|---|
| Trooper | `commando` | `superbwarfare:us_helmet_pasgt` | `us_chest_iotv` | own revolver | dressed |
| Shield | `bulwark` | `us_helmet_pasgt` | `immersiveengineering:armor_steel_chestplate` | chemthrower + shield | dressed |
| Gunner | `fusilier` | `us_helmet_pasgt` | `us_chest_iotv` | railgun | dressed |
| **Rifleman** *(new)* | `minecraft:pillager` in the gunner tag | `us_helmet_pasgt` | `us_chest_iotv` | **`tacz:type_81` / `ak47`** | new rank |
| Sergeant (Act IV) | `commando` | `dragonrise_reforge:fast_helmet` | `kevlar` | revolver | dressed; the helmet marks him |

The Rifleman is the point: a pillager in US kit with a real rifle is a *soldier*, not an illager, and it
gives the Militia the body rank it lacks. It needs `"Spawn With TACZ" = true` and a populated
`"TACZ Gun Type"`, or an In Control `held` field carrying the NBT directly — the latter is better,
because it keeps the weapon a per-rank design decision rather than a global roll.

Note the IE trio arrive through **village raids** (`canTriggerEngineerRaid`, and they sit in
`minecraft:raiders`), not natural spawn. With Hostile Villages running `vanillaVillageChance = 80`, that
is a spawn path the design does not control. Spawn eggs exist for scripted placement.

### 3.2 The Scavengers get worse guns, deliberately

Keep them on Pillager's Gun's own weapons — no ammunition economy, no drops, tuned inaccuracy — but set
`"Gun Model Switch" = true` so the models become SBW's. Same ballistics, better silhouette.

Dress them as looted, never issued: `ge_helmet_m_35` or a leather cap, one mismatched vest
(`dragonrise_reforge:msv_chest` on the captain only), `superbwarfare:steel_pipe` and `crowbar` on the
melee ranks. The contrast with §3.1 *is* the design — **the Militia matches, the Scavengers do not** —
and it is readable at fifty metres for the price of equipment fields.

`dragonrise_reforge:terrorist` joins them as a **Gunman** rank for the Woods outpost and the district
road patrols, where the illager silhouette has always been the weakest part of the Scavenger fiction. Its
35-block reach and burst fire make it a genuine Shooter, and at 20 HP it dies to a magazine. Subject to
the drop-table fix in §2.3.

### 3.3 The Dead get their history back

Hordes' `infection_conversions.json` already ships textures for a converted pillager, vindicator, evoker,
illusioner, witch, wandering trader and piglin brute, applied through its own `texture` and `chat_name`
NBT keys. entities-v8 §3.1's **Converted** rank is therefore not an aspiration — it is a shipped feature,
one NBT line per summon, with the art already in `config/hordes/assets/`.

Add to it: the **Worker** rank wears `immersiveengineering:armor_faraday_*` and carries a
`superbwarfare:crowbar` or `military_shovel`. At the switchyard and the turbine hall, those are the
people who worked there. The Dead's story is told by what they are still wearing.

### 3.4 Infection resistance becomes the reason to want military kit

`wearables_protection.json` maps a worn item to the `hordes:infection_resistance` attribute. It lists
vanilla armour only, on a ladder of leather 0.05 → netherite 0.2 per piece, all `add_multiplied_total`.

**Proposal: add the §2.1 headgear and vests above vanilla iron, at 0.15–0.2.** A gas-mask-shaped helmet
that does nothing against infection is a wasted mechanic; one that resists it makes every Militia corpse
worth searching and gives players a reason to dress like the enemy. One JSON file, no mod.

It also gives the drops table something to do without breaking "nothing an enemy carries ever drops": the
**armour** can drop where the **weapon** never does. That is F3.

### 3.5 Two enemies built from Improved Mobs' working item AI

TNT, lava buckets, flint and steel and harming potions are what Improved Mobs can genuinely use (§1.3),
and all four are already in the pool:

- **The Torch** (Scavenger, Act III+) — a vindicator with flint and steel. It burns the farm's crops and
  a wooden palisade. It is the argument for Walls 2 being stone, made by an enemy instead of a document.
- **The Chemist** (Scavenger, rare) — a pillager with splash harming potions. Ranged pressure that armour
  does not answer, forcing something other than "shoot back harder".

Both require `Item Use Blacklist` staying permissive for those items — the reason not to zero Improved
Mobs' *item use* when zeroing its *equipment* (C3).

### 3.6 Turrets: the players' problem solved, not a new one

Given §2.4, an auto-turret cannot threaten a player without scoreboard teams. Two honest uses remain:

- **A faction-war set piece.** A live `superbwarfare:hpj_11` at the plant complex's gate shoots the Dead
  and the Scavengers on sight, because both implement `Enemy`. entities-v8 §4 already wants "the Militia
  vs the Machines at the gates, all day" as something players watch from the viaduct. A turret makes that
  fight visible and permanent without any AI work — and it is *ignoring the players standing next to it*,
  which is its own kind of unsettling.
- **A prize.** It is owner-stamped on arming, so a turret taken intact becomes camp defence. That is a
  better reward than another gun.

`superbwarfare:turret_wreck` goes at sites already taken — the emplacement that used to be there.

If an anti-player emplacement is genuinely wanted later, it needs scoreboard teams, which is a separate
piece of design and touches Mob Factions, PvP and the finale. Not proposed here.

## 4. The wave mechanism is broken today

entities-v8 §5 plans per-site waves and the finale on `/hordes spawnWave <n>` against
`horde_data/tables/gscraft_<site>.json`, noting the command must be proven to work with the event
disabled.

**It does not work.** `HordeCommands.registerCommands` registers `spawnWave`, `start`, `stop`, `debug`
and `reset` **only when `enableHordeEvent` is true**. The live config has `enableHordeEvent = false`, so
the command is not registered at all.

The fix is two lines and preserves the intent exactly:

```
enableHordeEvent  = true      # registers the commands
hordesCommandOnly = true      # and suppresses every natural horde
```

Worth having, because the table format is stronger than the design assumed. Entries are either
`"<entity>{SNBT}-<weight>-<first_day>[-<last_day>]"` or an object with `entity`, `weight`, `first_day`,
`last_day`, `min_spawns`, `max_spawns`, `nbt`. The entity id is a free-form resource location — **any
mod's mob** — and the NBT goes to `EntityType.loadEntityRecursive`, so `ArmorItems`, `HandItems`,
`Attributes`, `CustomName`, `ActiveEffects`, `DeathLootTable` and recursive `Passengers` all work. Every
rank in §3 is expressible as a table entry, which makes a wave one file instead of a script.

Two traps: `-` is the shorthand delimiter, so no negative numbers and no hyphen in an id — use the object
form; and `last_day: 0` means **forever**, not day zero.

## 5. Config and datapack changes this pass asks for

Layered on entities-v8 §8 (C1–C12), which stands.

| # | Change | File | Kind |
|---|---|---|---|
| **E1** | `enableHordeEvent = true`, `hordesCommandOnly = true`. Without both, §4's waves and the finale cannot fire | `config/hordes-common.toml` | config |
| **E2** | `data_version` → `-1`. It is `12` today, and the next mod update **deletes `config/hordes/` wholesale** — it has already happened once, `hordes-backup/` is at version 6 | `config/hordes/hordes-info.json` | config |
| **E3** | Add the §2.1 helmets and vests to the infection ladder above vanilla iron (§3.4) | `.../infection/wearables_protection.json` | datapack |
| **E4** | Militia Rifleman's weapon: In Control `held` NBT, or `"Spawn With TACZ" = true` + `"TACZ Gun Type"` (§3.1) | `config/PillagersGun-common.toml` | config |
| **E5** | `"Gun Model Switch" = true` — SBW models on Scavenger guns, no ballistics change (§3.2) | `config/PillagersGun-common.toml` | config |
| **E6** | Decide `"Gunner Needs Ammo In TACZ"`. `false` today = infinite NPC ammo, set by a default rather than the design (§1.2) | `config/PillagersGun-common.toml` | config |
| **E7** | Add chosen hostile ids to `forge:pillager_gunner` — only one of the shipped eight is hostile (§1.1) | `data/forge/tags/entity_types/pillager_gunner.json` | datapack |
| **E8** | `entity.dragonrise_reforge.terrorist` lang entry **and** a `DeathLootTable` override off golden apples (§2.3) | pack datapack | datapack |
| **E9** | Per-site tables `gscraft_<site>.json` in the §4 format, ranks expressed as NBT | `.../horde_data/tables/` | datapack |
| **E10** | Exclude the `cyber_armorer` pack from every enemy gun table on tone (§1.2) | design decision | — |
| **E11** | Restate `gscraft-enemies.md` §8 row 2 as pool hygiene, not an emergency; it is not one of the four wrong defaults (§1.3) | `docs/gscraft-enemies.md` | doc |
| **E12** | Record that the camp's guns depend on `forge:pillager_gunner`, MusketMod being absent (§1.1) | `docs/gscraft-entities-v8.md` §1.2 | doc |
| **E13** | Record that `config/superbwarfare-server.toml` is stale; the live file is under `wasteland-v8/serverconfig/` (§1.4) | `docs/gscraft-entities-v8.md` §8 | doc |
| **E14** | Note ChaosZ Bandits is inert — `config/bandits.json` has `"enableMod": false`. entities-v8 lists it as a Scavenger source | `docs/gscraft-entities-v8.md` §2 | doc |
| **R1** | **Rejected:** `spawn_mob_with_guns` stays `false` (§1.4) | — | — |
| **R2** | **Rejected:** `spawn_senpai`, `spawn_steel_coil` stay `false` — tone, not capability (§2.5) | — | — |
| **R3** | **Rejected:** auto-turrets as anti-player emplacements; impossible without scoreboard teams (§2.4) | — | — |

E1 and E2 are the two that can quietly cost work: without E1 nothing in §4 fires, and without E2 every
table written under E9 is deleted by the next mod update.

## 6. Open decisions

| # | Question | Recommendation |
|---|---|---|
| F1 | Does the Militia get TACZ rifles, or stay purely IE? | TACZ. A faction with no line infantry does not read as an army, and the Rifleman is the cheapest fix |
| F2 | Is `dragonrise_reforge:terrorist` a Scavenger rank or its own faction? | a Scavenger rank. One entity does not earn a seventh faction, and the Scavengers need a human silhouette more than the map needs another flag |
| F3 | Do enemy **armour** pieces drop, given §3.4 makes them worth wanting? | yes, at low rates, armour only — the one thing that can drop without touching "no working guns from corpses" |
| F4 | Infinite NPC ammunition (E6)? | make it finite. A scavenging world where only the enemy never runs dry is the wrong way round |
| F5 | The Torch and the Chemist (§3.5) — flavour, or a real answer to walls? | real. They are the only enemies in the pack that punish a wooden wall specifically |
| F6 | Scoreboard teams, to make turrets and TDM work against players? | not now. It touches Mob Factions, PvP and the finale; revisit if fixed emplacements become a design need |

Related: `gscraft-entities-v8.md` (the roster of record), `gscraft-enemies.md` (waves, drops, numbers),
`gscraft-loot-tables.md` (sheet 2), `gscraft-finale.md` (the four Captains and the Sleeper).
