# GSCraft mod pack - update applied to the local server (2026-09-05)

Follow-up to `gscraft-modpack-updates.md` (the audit). Owner's call: "we have no clients yet, go ahead and apply the
updates completely and lets test it out later, once completed do a code review of the mods to see if they would conflict
each other." This is what was applied, what was held back and why, the boot result, and the conflict review.

## 1. Applied (local server `G:/GSCraft/server`, old jars in `server/mods_backup_2026-09-05/`)

| Mod | From | To | Source |
|---|---|---|---|
| Forge | 47.4.10 | **47.4.23** | forge installer (`--installServer`); `start.bat`/`run.bat` now point at `1.20.1-47.4.23/win_args.txt` |
| Lost Cities | 7.5.3 | 7.5.4 | Modrinth |
| ModernFix | 5.25.2 | 5.27.83 | Modrinth |
| Moonlight | 2.16.15 | 2.16.34 | Modrinth |
| AzureLib | 3.1.2 | 3.1.12 | Modrinth |
| GeckoLib | 4.8.2 | 4.8.4 | Modrinth |
| CreativeCore | 2.12.32 | 2.12.39 | Modrinth |
| Guard Villagers | 1.6.15 | 1.6.19 | Modrinth |
| The Knocker | 1.5.0 | 1.5.2 | Modrinth |
| Patchouli | 84.1 | 85 | Modrinth |
| Simple Voice Chat | 2.6.22 | 2.6.23 | Modrinth |
| Ping Wheel | 1.12.0 | 1.12.1 | Modrinth |
| Farmer's Delight | 1.2.9 | 1.3.4 | Modrinth |
| Recruits | 1.14.0 | 1.15.2 | Modrinth |
| Sophisticated Backpacks | 3.24.13.1433 | 3.24.67.2109 | Modrinth (also on CurseForge) |
| Sophisticated Core | 1.2.109.1271 | 1.3.84.2308 | Modrinth (also on CurseForge) |
| In Control | 9.3.3 | 9.5.0 | CurseForge (mod 257356, file 8790496) |
| The Hordes | 1.5.4c | 1.6.3g | CurseForge (mod 485779, file 8527818) |

17 jars swapped, sha1 verified for every Modrinth download. Class C (ParCool alpha, leawind beta, WaterMedia/Waterframes
betas, Luki's 1.1.3) skipped as planned.

## 2. Held back: Superb Warfare stays at 0.8.8

`superbwarfare-0.8.9.1-hotfix` was installed and the boot failed twice over:
- it now requires the **Kotlin for Forge** language provider (`kotlinforforge [4.11.0,)`), a new dependency the pack does not
  carry;
- the two Superb Warfare add-ons pin the base mod exactly: **MCSP 1.0.8** (`superbwarfare [0.8.8,0.8.8]`, newest build,
  Dec 2025) and **Vintage Vehicle Pack 0.2.0** (same pin). VVP 0.2.1 (Aug 2026, beta) targets the newer base but pulls in
  Kotlin for Forge and two more libraries; MCSP has no newer build at all.

So Superb Warfare cannot move without dropping MCSP, and the design's vehicle roster comes from the add-ons. 0.8.8 restored
from the backup; the 0.8.9.1 jar is parked in `scratch/mods_update/`. Revisit when MCSP publishes a 0.8.9 build.

## 3. Boot test

`start.bat` with the swapped set: **"Dedicated server took 26 s to load"**, no new errors. The error set is the known benign
one (mixin class-not-found lines for mods that are not installed - Quark, Ars Nouveau, Iron's Spellbooks, FramedBlocks;
pomkots mixin config without `minVersion`; client classes refused on the dedicated server). 236 warnings, all of that kind.

Config migrations written by the new versions on first boot (picked up by `packwiz_build.py`, now in `build/packwiz/config`):
- **The Hordes 1.6**: `hordes-common.toml` schema changed - `playerInfectChance = 0.75` became
  `playerInfectionResistance = 0.25` (the same 75 % infection chance), `infectVillagers`/`villagerInfectChance` moved out of
  the toml; the datapack files `horde_data/immune_wearables.json`, `immunity_items.json`, `infection_conversions.json` and
  the `infection_entities` tag were replaced by a new `data/hordes/infection/` folder (data_version 6 -> 12). The old files
  were the mod's defaults (leather 0.95, enchanted golden apple cure), nothing of ours was in them. The design's infection
  behaviour (20-minute clock, zombie players as graves) is unchanged.
- **Farmer's Delight 1.3**: `farmersdelight-common.toml` rewritten (132 lines changed; meal rebalance keys). Loot-table ids
  still to be re-checked in `gscraft_recipes.js` / the KubeJS loot stand-ins.
- Lost Cities profiles re-serialised (no value changes that matter: the v8 cell is pre-built), Moonlight, Sophisticated Core,
  Recruits client, ModernFix mixins, Zombie Awareness mob lists: default re-writes.

Client pack: `scratch/modrinth_files.json` refreshed (`tools/modrinth_hashes.py`, 79 Modrinth-hosted jars) and
`packwiz_build.py --version 2026.09.05` rebuilt `build/packwiz` (mods + configs). The 26 release-hosted jars are unchanged,
so the `client-installer-2026-09-04` release assets still serve. **The hosted Bisect server was not touched** (hand-run
deploy, HANDOFF §6): it still runs Forge 47.4.10 with the old jars; server and client must move together.

## 4. Conflict review (`tools/modcheck.py`, `buildmap/audit/modcheck_2026-09-05.json`)

Static review of all 103 jars (124 mod files including jar-in-jar, 110 mod ids): every `mods.toml` dependency range against
the installed versions, duplicate mod ids, mixin target overlap, loader ranges.

- **Dependency ranges: all satisfied.** No mandatory dependency missing, no installed version outside a declared range
  (bare versions read as Maven soft requirements, as Forge does; PlayerRevive's `creativecore 2.11.20` is met by 2.12.39).
  Sophisticated Backpacks 3.24.67 declares `sophisticatedcore [1.3.80.+,)` - satisfied by 1.3.84. Recruits 1.15.2, Farmer's
  Delight 1.3.4, In Control 9.5.0, The Hordes 1.6.3g carry no cross-mod requirements beyond Forge/Minecraft.
- **Loader ranges:** every declared Forge/Minecraft range accepts 47.4.23 / 1.20.1.
- **Duplicate mod ids:** only libraries shipped jar-in-jar by several mods - `mixinextras` (0.3.5 in The Hordes, 0.3.6 in
  Farmer's Delight and TaCZ, 0.4.1 in AzureLib, Create, ModernFix, Puzzles Lib) and `xaerolib` (1.7.1 twice). Forge's
  jar-in-jar picks the highest version (0.4.1), which is what the boot log shows; not a conflict.
- **Optional dependencies not installed (28):** JEI (EMI is the recipe viewer), Embeddium/Sodium, Open Parties and Claims,
  Shoulder Surfing, Better Third Person, Epic Fight, Paraglider, Feathers, GeckoAnimFix, Real Camera, CraftTweaker,
  Create add-ons, WaterMedia (client side, for the mech-test Waterframes jar). All optional; nothing breaks.
- **Mixin hotspots** (classes patched by 3+ mods; 72 jars carry mixins, 876 mixin classes, 51 names shared): `LivingEntity`
  17 mods, `Entity` 15, `ItemStack` 10, `Player` 10, `Minecraft` 10, `ServerLevel` 9, `LevelRenderer` 8, `Camera` 7,
  `Mob` 7, `ClientPacketListener` 7. The heavy overlappers are Create + Create Big Cannons, Superb Warfare, TaCZ, ParCool,
  ModernFix, Canary, KubeJS, Sedparties, pomkots (alpha). These are the places where a crash after any of these mods
  updates would come from; today's boot and the earlier v7 play sessions ran this exact combination without a mixin
  failure. Note for the future: **Canary and ModernFix both patch `LevelChunk`, `PalettedContainer`, `StateHolder`,
  `BlockStateBase`** - two performance mods on the same internals; ModernFix's mixin toggles
  (`modernfix-mixins.properties`) are the knob if chunk or state bugs appear.
- **Left as found (not from this update):** the other session's mech-test jars `pomkotsmechs 0.0.1-alpha.8` (mixin config
  warning at every boot, patches LivingEntity/Player/Camera/LevelRenderer), `leawind_third_person` (client-only mod on the
  server) and `waterframes` (needs WaterMedia on clients).

## 5. Still to do before a client update

1. `gscraft_recipes.js` / loot stand-ins: re-check Farmer's Delight 1.3 item ids.
2. In Control 9.5.0: re-validate `config/incontrol/spawn.json` against the new rule syntax on a play test.
3. The Hordes 1.6: one infection play test (the resistance key, the new `infection/` datapack folder).
4. Sophisticated Core 1.3: open a backpack with upgrades from a v7 save (item NBT migration).
5. Bundle with the v8 release: hosted server jar swap + Forge 47.4.23 install by hand, packwiz push, one client refresh.
