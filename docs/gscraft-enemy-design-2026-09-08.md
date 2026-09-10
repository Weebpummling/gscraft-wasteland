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
4. The shipped example is inert: `skeleton.json` sits under `data/superbwarfare/`, so it keys under
   the **superbwarfare** namespace while lookup uses `EntityType.getKey()` = `minecraft:skeleton`. The
   two never match. A working file has to live under the mob's own namespace.

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
| **Modern tactical** | `dragonrise_reforge:fast_helmet`, `t21_helmet`, `kr06_helmet`, `sniper21_helmet`, `aljin_helmet` | `dragonrise_reforge:kr06_chest`, `msv_chest`, `med21_chest`, `cnjustchest`, `cnchest` | five helmets and five vests — enough for ranks *within* one faction |
| **Peacekeeper** | `dragonrise_reforge:un_helmet` | — | solid UN blue, lettered. A blue helmet on a corpse tells a story for free |
| **Camouflage** | — | `dragonrise_reforge:desert07_chest`, `ocean07_chest`, `gorka3` | desert tan, blue digital, Russian olive Gorka — terrain-specific dress |
| **Scavenger rags** | `pomkotsmechs:wandererarmorhelmet` (a face wrap), `pomkotsarmorhelmet` (a bandana) | `wandererarmorchestplate` (a jacket), `pomkotsarmorchestplate` | **the pack's only non-military soft kit**, and the best wastelander look in it — full four-slot sets |
| **Sealed / hazmat** | `createbigcannons:gas_mask` (the **only** true respirator in the pack), `create:copper_diving_helmet` | `create:copper_backtank` | helmet + backtank is a complete sealed-suit silhouette |
| **Junk armour** | `create:cardboard_helmet` | `cardboard_chestplate` (+ legs, boots) | reads as scrap-armoured at distance, and takes trims |
| **Industrial / electrical** | `immersiveengineering:armor_faraday_helmet` | `armor_faraday_chestplate` (+ legs, boots) | insulated rubber — reads as plant worker, and is thematically exact at the switchyard |
| **Heavy industrial** | `immersiveengineering:armor_steel_*` | full set | NATO's current look |

This is the pass's plainest finding: **the design specifies leather and iron while a full military
wardrobe sits unused in the pack.** `gscraft-enemies.md` principle 3 — "every faction is legible at fifty
metres" — is currently carried by silhouette and noise alone. It does not have to be.

Four traps in that table, all bytecode-verified, all of which would otherwise be found the hard way:

- **`dragonrise_reforge:kevlar` is not armour.** No item class, no slot — it is a recipe ingredient. An
  earlier reading of this pass listed it as a chest piece; it is not one.
- **`cn21` and `cnfast` are registered `Type.HELMET` but gate their attribute modifiers on
  `EquipmentSlot.CHEST`**, so they give **zero armour points** on the head. Cosmetic only. Fine for a
  rank marker, useless as protection.
- **`army07hat` is registered as a CHESTPLATE** despite the name, and has no translation.
- **Dragon Rising ships no boots at all.** Every faction dressed from it wears vanilla boots.

**Armour trims** (16 patterns × 10 materials, verified from the server jar; no mod adds any) are a free
rank ladder — the same silhouette with a readable colour band, e.g. `sentry/copper` for grunts,
`sentry/iron` for NCOs, `sentry/gold` for officers, as
`minecraft:iron_chestplate{Trim:{material:"minecraft:gold",pattern:"minecraft:sentry"}}`. But they render
**only on vanilla-model armour**, plus IE steel and Create cardboard. They will not show on the GeckoLib
3D sets (Dragon Rising, Superb Warfare, Pomkots), which replace the humanoid model outright. So a faction
is dressed *either* in 3D military kit *or* in trimmed vanilla — not both.

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

## 2.6 What In Control can actually set, and three things it cannot

Read from `RuleKeys` and `SpawnRule`'s attribute factory in the shipped jar, so this is exactly what
`spawn.json` accepts.

**The keys that dress a mob** are `armorhelmet`, `armorchest`, `armorlegs`, `armorboots` and `helditem`.
**`helmet` / `chestplate` / `leggings` / `boots` are conditions, and they test the *player*** —
`GenericRuleEvaluator.addArmorCheck` calls `Player.getItemBySlot`. Writing a rule with `helmet` expecting
to dress a mob silently tests the wrong entity.

Each equipment key takes a string, an object, or a weighted array:

```json
"armorhelmet": [ {"item": "dragonrise_reforge:fast_helmet", "factor": 3.0},
                 {"item": "dragonrise_reforge:aljin_helmet", "factor": 1.0} ]
```

**It can set NBT**, which is what makes §3.1 possible — `Tools.parseStack` runs the `nbt` element through
vanilla `TagParser`. A TACZ rifle in a mob's hand is one rule field:

```json
"helditem": { "item": "tacz:modern_kinetic_gun",
              "nbt": { "GunId": "tacz:type_81", "GunFireMode": "AUTO", "GunCurrentAmmoCount": 30 } }
```

Three limits that matter to the standing design:

1. **`sizemultiply` and `sizeadd` do nothing.** `RuleBase.addSizeActions` logs `Mob resizing not
   implemented yet!` and installs a no-op, and Pehkui is not installed. **The Matron is specified at
   size ×1.5 and the Bloater at ×1.4** (`gscraft-enemies.md` §3.1, entities-v8 §6). Neither will be any
   bigger than an ordinary mob. Both need re-specifying on health, armour and speed — or the Matron needs
   a different base mob to read as large.
2. **There is no off-hand action.** Only `helditem` (mainhand) can be set. The off-hand route is the
   `nbt` action writing `HandItems`, which is *inferred* from `readAdditionalSaveData` and should be
   tested before the Bulwark's shield or a banner-carrier depends on it.
3. **Equipped gear keeps vanilla's 8.5 % per-slot drop chance.** `setItemSlot` does not touch drop
   chances, so **every rank dressed by §3 currently violates "nothing an enemy carries ever drops"**
   (`gscraft-enemies.md` §0.2). Every dressing rule needs the `nbt` action setting
   `ArmorDropChances: [0.0f,0.0f,0.0f,0.0f]` and `HandDropChances: [0.0f,0.0f]` — except where F3
   deliberately wants armour to drop.

**Two live rules are broken worse than test T1 recorded.** `spawn.json` rules 1 and 2 (the
`pomkotsmechs` box) use `minx`/`maxx`/`minz`/`maxz`, which are `spawner.json` keys and do not exist in
`SpawnRule`. `GenericAttributeMapFactory.validate()` returns false on an unknown key and `parse()` then
returns an **empty attribute map** — so those rules load with every condition *and* every action
stripped: no dimension filter, no mob filter, no count cap, no `result`. They are unconditional
catch-alls, not ignored lines. They must move to the `area` key with `areas.json` populated (C2).

**Improved Mobs will contest the same slots.** Its `equipment.json` is populated and it equips at
spawn-finalize, the same moment In Control's `finalize` rules run, with no guaranteed ordering. Faction
mobs need exempting through `"Entity Configs"` in `improvedmobs/common.toml` using the
`<entityid>|FLAG` syntax — `"minecraft:pillager|ARMOR|HELDITEMS"` — which is how the `recruits:*` and
`guardvillagers:guard` entries are already handled.

**One id family to avoid:** GeckoLib's `mutant_zombie` and `parasite` appear in a lang sweep but
`GeckoLibMod.shouldRegisterExamples()` is false in production, so they do not exist on a real server.

## 3. Proposed designs

### 3.1 NATO becomes the pack's real soldiers

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
gives NATO the body rank it lacks. **Written 2026-09-09** (`tools/militia_rules.py`): the rank spawns in the `farbank` and `plant` areas only, dressed at `finalize`, holding `tacz:modern_kinetic_gun` with `GunId: tacz:type_81`, with drop chances zeroed. `helditem` is confirmed correct - `SpawnRule` rejects `sethelditem` - and its `nbt` must be a JSON object. It is best delivered by an In Control `helditem` carrying the `GunId` NBT (§2.6) rather than
`"Spawn With TACZ" = true` plus a `"TACZ Gun Type"` roll, because that keeps the weapon a per-rank design
decision instead of a global weight table.

Note the IE trio arrive through **village raids** (`canTriggerEngineerRaid`, and they sit in
`minecraft:raiders`), not natural spawn. With Hostile Villages running `vanillaVillageChance = 80`, that
is a spawn path the design does not control. Spawn eggs exist for scripted placement.

### 3.2 The Scavengers get worse guns, deliberately

Keep them on Pillager's Gun's own weapons — no ammunition economy, no drops, tuned inaccuracy — but set
`"Gun Model Switch" = true` so the models become SBW's. Same ballistics, better silhouette.

Dress them as looted, never issued. Pomkots' **`wandererarmorhelmet`** (a face wrap) and
**`wandererarmorchestplate`** (a jacket) are the pack's only non-military soft kit and are exactly this
faction — a wastelander, not a soldier. Mix in `ge_helmet_m_35` on some, a plain leather cap on others,
one mismatched military vest (`dragonrise_reforge:msv_chest`) on the captain alone, and
`superbwarfare:steel_pipe` or `crowbar` on the melee ranks. The contrast with §3.1 *is* the design — **NATO matches, the Scavengers do not** —
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
that does nothing against infection is a wasted mechanic; one that resists it makes every NATO corpse
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
  and the Scavengers on sight, because both implement `Enemy`. entities-v8 §4 already wants "NATO
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
| **E4** | NATO Rifleman's weapon: In Control `held` NBT, or `"Spawn With TACZ" = true` + `"TACZ Gun Type"` (§3.1) | `config/PillagersGun-common.toml` | config |
| **E5** | `"Gun Model Switch" = true` — SBW models on Scavenger guns, no ballistics change (§3.2). **Applied 2026-09-09, local only.** Server boots clean with it | `config/PillagersGun-common.toml` | config |
| **E6** | Decide `"Gunner Needs Ammo In TACZ"`. `false` today = infinite NPC ammo, set by a default rather than the design (§1.2) | `config/PillagersGun-common.toml` | config |
| **E7** | Add chosen hostile ids to `forge:pillager_gunner` — only one of the shipped eight is hostile (§1.1) | `data/forge/tags/entity_types/pillager_gunner.json` | datapack |
| **E7a** | Every dressing rule sets `ArmorDropChances`/`HandDropChances` to 0 via the `nbt` action — without it all of §3 breaks "nothing an enemy carries ever drops" (§2.6) | `config/incontrol/spawn.json` | config |
| **E7b** | Exempt every dressed faction mob from Improved Mobs with `"<id>|REVERSE|ARMOR|HELDITEMS"`, or it contests the same slots at finalize (§2.6). **Corrected 2026-09-09:** this row said `"<id>|ARMOR|HELDITEMS"`, which is the inverse. The flag list after an id is the set *not* applied — the mod's own example reads "<minecraft:sheep|ATTRIBUTES> will add sheep to everything except attributes", and `EntityModifyFlagConfig` XORs set membership with `REVERSE` ("Having no flags is equal to ALL"). Without `REVERSE` the entry leaves Improved Mobs equipping the mob, which is the contest this row exists to prevent, and switches off the attribute scaling that is wanted | `config/improvedmobs/common.toml` | config |
| **E7c** | Re-specify the Matron and the Bloater without size multipliers — `sizemultiply` is a logged no-op and Pehkui is absent (§2.6) | `docs/gscraft-enemies.md` §3.1, entities-v8 §6 | doc |
| **E7d** | Move `spawn.json` rules 1–2 off `minx/maxx/minz/maxz` onto `area`; they currently load as unconditional catch-alls, not as ignored keys (§2.6) | `config/incontrol/spawn.json` | config |
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
table written under E9 is deleted by the next mod update. E7a and E7d are the two that are wrong on the
live server right now — enemy gear is droppable, and two spawn rules have lost every condition they were
written with.

## 6. Open decisions

| # | Question | Recommendation |
|---|---|---|
| F1 | Does NATO get TACZ rifles, or stay purely IE? | **RULED 2026-09-09 (owner): TACZ.** `tacz:type_81` and `tacz:ak47` both verified present in `tacz-1.20.1-1.1.8-hotfix.jar`. Delivered per rank through an In Control `helditem` carrying the `GunId` NBT, **not** through `"Spawn With TACZ" = true`, which stays `false`: the global flag rolls from a weight table and would arm every gunner in the pack, where the design wants the weapon to be a per-rank decision |
| F2 | Is `dragonrise_reforge:terrorist` a Scavenger rank or its own faction? | **RULED 2026-09-09 (owner): a Scavenger rank.** Its cure drop is fixed (`kubejs/startup_scripts/gscraft_terrorist_drops.js`, §2.3 item 2), so the rank is safe to place. Item 1 of §2.3 stands: it still has no lang entry and shows as `entity.dragonrise_reforge.terrorist`. Item 3 stands too - its skin is fixed, so it cannot be dressed from §2.1 and reads the same wherever it appears |
| F3 | Do enemy **armour** pieces drop, given §3.4 makes them worth wanting? | yes, at low rates, armour only — the one thing that can drop without touching "no working guns from corpses" |
| F4 | Infinite NPC ammunition (E6)? | make it finite. A scavenging world where only the enemy never runs dry is the wrong way round |
| F5 | The Torch and the Chemist (§3.5) — flavour, or a real answer to walls? | real. They are the only enemies in the pack that punish a wooden wall specifically |
| F6 | Scoreboard teams, to make turrets and TDM work against players? | not now. It touches Mob Factions, PvP and the finale; revisit if fixed emplacements become a design need |

Related: `gscraft-entities-v8.md` (the roster of record), `gscraft-enemies.md` (waves, drops, numbers),
`gscraft-loot-tables.md` (sheet 2), `gscraft-finale.md` (the four Captains and the Sleeper).
