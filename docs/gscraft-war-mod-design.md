# GSCraft War: the enemy system as one mod (design, 2026-09-09)

## Why

Every faction so far has stood up on a borrowed body, and each layer patches the one below it:

- **Kit is invisible.** NATO, RUAF and the Scavengers are illagers (pillager, IE commando/fusilier/
  bulwark, vindicator). `IllagerRenderer`, `PillagerRenderer`, `VindicatorRenderer` and IE's three
  renderers add only `CustomHeadLayer` / `ItemInHandLayer`, with no armour layer. The armour is on the
  entity (a RUAF Grenadier carries a 6B47, a 6B43 and MSV trousers) and nobody can see it.
- In Control dresses by type and place, so a Scavenger pillager placed in the town became RUAF.
- Mob Factions works per type, so NATO and RUAF could never fight.
- The KubeJS spawner needed a tag to get past In Control; neutrality lives in a startup script keyed on
  names; Improved Mobs needs per-type exemptions; `/reload` reloads none of it.

One mod owns bodies, loyalty, loadout, placement and memory.

## What the mod owns

1. **Bodies.** Humanoid entities on `HumanoidModel` with `HumanoidArmorLayer`, so every armour item in
   the pack renders (vanilla, SBW, dragonrise, GeckoLib armour through Forge's armour-model hook).
   Types: `gscraft:nato_soldier`, `gscraft:ruaf_soldier`, `gscraft:scavenger`, separate per faction
   so loot tables, Jade, spawn eggs and other mods can tell them apart. Skins start as vanilla's default
   player skins referenced by resource location (nothing copied); faction skins later.
   The Dead stay vanilla zombie / husk / zombie_villager / drowned: they already render armour and carry
   the infection ladder. The mod places and dresses them.
2. **Guns.** TACZ mixes `IGunOperator` into every `LivingEntity` (`draw`, `aim`, `shoot(pitch, yaw)`,
   `reload`, `ShootResult`). A ranged goal draws the issued gun, aims, fires at the target and reloads
   on `NO_AMMO`. SuperbWarfare has its own `MobGunData` + `GunShootGoal` for SBW guns; second. Melee
   ranks (Digger's shovel, Raider's crowbar) use a melee goal. No block breaking, by design.
3. **Loyalty.** Factions and relations as datapack JSON:
   NATO and RUAF hostile to each other; both armies hostile to the Dead; Scavengers hostile to the Dead;
   armies hostile to players; Scavengers neutral to players until struck, the grudge stored on the
   entity. Mob Factions is no longer involved for these types.
4. **Loadouts.** Ranks with weights and per-slot items as datapack JSON, ported from the
   `spawn_rules.py` tables (NATO US kit + M4A1, RUAF Russian kit + AK-47, Scavenger looted kit).
5. **Placement: the director.** Replaces the In Control faction block and the KubeJS area spawner.
   - Zones as JSON generated from `incontrol_areas.py` BOXES: builds (no spawn, KROT and every player
     build), bases, outposts, fronts, the Skadowsky / plant / town sub-zones.
   - Ambient: the Dead and Scavengers around players by local density, a budget per player.
   - Garrisons: each outpost holds a squad of persistent soldiers, recorded in SavedData, so an unloaded
     outpost is never spawned twice and a wiped one refills after a cooldown.
   - Patrols: squads led by a Sergeant walking waypoint routes along the river front, members following.
   - Vanilla suppression: natural monster spawns cancelled in the managed overworld by spawn type;
     spawners and structures untouched. The `gs_placed` tag and In Control's Dead gate retire.
6. **Memory.** SavedData: squads (id, faction, zone, member UUIDs, alive count, respawn timer); later,
   outpost ownership.
7. **Faction war (later).** An outpost changes hands when its defenders are gone and attackers hold the
   ground; the garrison refills with the owner's faction; the front moves.
8. **Admin.** `/gscraft zone here|list`, `/gscraft squad spawn <faction> <x> <z>`,
   `/gscraft director pause|resume|stats`. Data is datapack JSON, so `/reload` reloads it.

## What retires, each only after its phase passes locally

In Control faction rules (the builds deny moves into the director), `gscraft_area_spawner.js`,
`gscraft_scavenger_neutral.js`, the Improved Mobs exemptions for illager types, the Mob Factions entries
for army types, `gscraft_terrorist_drops.js` once the Gunman is a Scavenger body. Hordes waves stay; their
tables can point at the new types.

**Retired locally, 2026-09-09 (owner, after the in-person phase 1 test: "turn off our hackjob spawn rules and
everything else").** The local test server is back to the hold, the same state as live: no natural hostiles.
- In Control `spawn.json` = `{mod: gscraft, allow}` + the hold + the pre-existing apocalypse rules behind it;
  `areas.json` = `[]`. The other session's two mech rules with rejected `minx`/`maxx` keys were not restored.
- KubeJS area spawner, Scavenger neutrality and terrorist drop filter removed (repo copies in `retired/kubejs`).
- Improved Mobs illager exemptions removed; the `gscraft` exclusion stays.
- Hordes events off again (`enableHordeEvent = false`), its data files restored, the Skadowsky table removed.
  Hordes returns, if at all, with the director phase and the new types.
- Kept, because they are standing rulings rather than spawn rules: mob griefing off (gamerule, Improved Mobs
  flags, `break_blocks = false`) and the fog man's random trigger off (`enable_spawning = false`; he returns
  with a location trigger in the director). The hold also covers "nothing spawns at KROT or player builds".
- Backups of every removed or changed file: `server/retired-2026-09-09/`. `spawn_rules.py`, `area_spawner.py`
  and `incontrol_areas.py` refuse to run without `--retired-ok`.

## Distribution

Entities need client renderers, so the jar goes on the server and every client (packwiz side `both`).
Players get it through Prism's pre-launch update. The deploy gate is unchanged: comprehensive local
spawn without errors, owner's in-person test, owner's say-so.

## Phases, local and one at a time

| # | Step | Passes when |
|---|------|-------------|
| 0 | Toolchain: Forge MDK 47.4.23, official mappings, Gradle 8.8; TACZ compile-only | jar builds, server boots with it |
| 1 | One soldier: `ruaf_soldier` renders armour, draws and fires a TACZ AK-47, fights zombies | owner sees the kit in person |
| 2 | Factions: NATO vs RUAF fight; Scavenger neutral until struck; the Dead hostile to all | scripted duel tallies + in person |
| 3 | Loadouts JSON ported from `spawn_rules.py` | probe: every rank dressed |
| 4 | Director: zones, ambient density, garrisons in SavedData, vanilla suppression; retire the In Control block and KubeJS spawner | probes + tick-lag test |
| 5 | Squads and patrols on the river front | in person |
| 6 | Outpost control | in person |

## Open, to rule on later

- Grudge scope: this Scavenger only, or the whole faction toward that player.
- Whether the Dead get a mod body later.
- NPC ammunition (F4): TACZ's `needCheckAmmo` / `consumesAmmoOrNot` decide it for NPCs; measured in phase 1.

## Testing notes

- **The local server pauses when empty.** The Hordes' `pauseEventServer = true` stops world ticking with no
  player online, so a headless test sees frozen mobs. The local test server runs `false`
  (backup `hordes-common.toml.bak-pause-true`); live keeps `true`. Never carry the local value to live.
- **Phase 1, first run (paused world):** dressing verified: plain `/summon gscraft:ruaf_soldier` came out
  as RUAF Rifleman with 6B47, 6B43, MSV trousers, and an AK-47 with 30 rounds. Combat untested until the
  world ticks.
- **Mob Factions** lists only vanilla-type factions; `gscraft:*` is in none, so it does not block targeting.
  The Dead will not target soldiers by themselves; phase 2 gives them that goal.
