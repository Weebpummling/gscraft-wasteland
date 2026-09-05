# GSCraft mod pack - update status (2026-09-05)

Audit of every jar in `server/mods` (103) against the newest **1.20.1 Forge** builds: 75 Modrinth-hosted jars through the
Modrinth API (`buildmap/audit/modpack_update_audit_2026-09-05.json`, changelogs included), Forge through its promotions
file, and the CurseForge-only mods that matter through their files pages. Owner's question: what is out of date, and
does applying the updates affect the server.

## 1. Summary

- **56 of the 75 Modrinth-hosted jars are current.** 19 have newer 1.20.1 Forge builds: 13 are drop-in library or
  bug-fix updates (class A), 4 change content or configs and need work before they go in (class B), and 5 are
  betas/alphas or removals to skip (class C).
- **Forge 47.4.10 -> 47.4.23** (latest; 47.4.10 is still the *recommended* build). The changes: a handshake fix (a
  client could miss the last login packet), an event-bus upgrade with leak fixes, support for multiple access-transformer
  configs, TOML parse errors written to the log, a RegistryObject equality change. Nothing touches worldgen or the chunk
  format. Worth taking with a boot test; the RegistryObject and event-bus changes are the compatibility risk.
- **CurseForge-only mods:** FTB Quests 2001.4.22, FTB Teams 2001.3.2, FTB Chunks 2001.3.8, FTB Library 2001.2.13 and
  Refurbished Furniture 1.0.20 are the newest 1.20.1 builds. **Sophisticated Backpacks 3.24.13 -> 3.24.67** (54 builds,
  with **Sophisticated Core 1.2.109 -> 1.3.84**, a major core jump), **In Control 9.3.3 -> 9.5.0** (the spawn rules file
  must be re-validated), **The Hordes 1.5.4c -> 1.6.3g** (a 1.6 line: config schema and infection behaviour to re-test;
  the design's 20-minute infection clock depends on it). Not checked (slug unknown or page missing, manual pass needed):
  Keerdm Zombie Apocalypse Essentials 1.41, Eyes in the Darkness, Framework, Doomsday Decoration, TaCZ Fire Control
  Extension, Dynamic View, cupboard, chunksending, Hostile Villages, Recipe Essentials, LongNbtKiller, BHStats, Custom
  Starting Gear, Pillager's Gun, Bandits, vvp, sedparties, FastSuite, Item Filters.
- **Does updating affect the server?** Class A: no behaviour change, but client and server jars must match, so every
  change means a packwiz refresh (the installer picks it up on the next launch). Class B: yes - Superb Warfare 0.8.9.1
  adds vehicles the design has not placed (each needs a strip rule and a blueprint decision), Recruits 1.15 changes AI
  and adds routes (helps the site-guard design), Farmers Delight 1.3 rebalances meals and tags, Lost Cities 7.5.4 only
  matters for new chunks (v8 pre-builds its cell). The three CurseForge jumps (Sophisticated, In Control, Hordes) are the
  ones most likely to change behaviour the design relies on: backpack upgrades as station orders, the spawn deny rule,
  infection.
- **Observation:** `server/mods` carries three jars from the other session's mech test that are not in the design:
  `pomkotsmechs-forge-0.0.1-alpha.8.jar` (alpha; a mixin config warning at every boot), `leawind_third_person` (a
  client-side camera mod) and `waterframes` (needs WaterMedia). Manifest entries found: pomkots 1, leawind
  1, waterframes 1.

## 2. Recommendation

Do not update the live v6 server piecemeal. Bundle: take class A, Forge 47.4.23 and Lost Cities 7.5.4 with the v8
release (one client refresh), test-boot on the local server (5 server + 2 startup scripts, the benign error set, one
play session), then decide class B one mod at a time with its design work: Superb Warfare after the vehicle roster and
strip list are extended; Recruits with the site-guard build (Phase C); Sophisticated Backpacks + Core, In Control 9.5.0
and Hordes 1.6.3g each with a config diff and a test; Farmers Delight after the loot-table ids are checked. Skip class C.
Never mix: a partial update leaves clients and server on different versions of a networked mod.

## 3. Modrinth-hosted jars with newer 1.20.1 Forge builds

| Jar | Installed | Latest | Newer | Class | Impact |
|---|---|---|---|---|---|
| modernfix-forge-5.25.2+mc1.20.1.jar | 5.25.2+mc1.20.1 (2025-12-08) | 5.27.83+mc1.20.1 (2026-08-31, release) | 38 | A | 38 bug-fix/performance builds; drop-in |
| watermedia-2.1.37.jar | 2.1.37 (2025-12-01) | 3.0.0.23 (2026-07-27, beta) | 20 | C | 3.0 beta with API breaks; not in server/mods (audited via the hash lookup only) |
| moonlight-1.20-2.16.15-forge.jar | 1.20-2.16.15-forge (2025-10-18) | 1.20-2.16.34-forge (2026-06-16, release) | 16 | A | library backports; drop-in (Immersive Weathering dependency) |
| azurelib-neo-1.20.1-3.1.2.jar | 3.1.2 (2025-11-28) | 3.1.12 (2026-07-04, release) | 10 | A | 3.1.11 rendering pipeline overhaul (client CPU), 3.1.12 fixes; drop-in |
| leawind_third_person-v2.1.0-mc1.20.1-forge.jar | 2.1.0 (2024-08-31) | 3.0.3-beta+forge-1.20.1 (2026-08-08, beta) | 10 | C | 3.0.x beta; skip (added to server/mods by the mechs test, client-side mod) |
| FarmersDelight-1.20.1-1.2.9.jar | 1.20.1-1.2.9 (2025-08-23) | 1.20.1-1.3.4 (2026-08-29, release) | 8 | B | 1.3.x rebalances meals (Fried Rice, Chicken Soup) and changes tags; our loot-table stand-ins reference FD items - re-check ids after the jump; otherwise safe |
| superbwarfare-1.20.1-0.8.8-final-6a6b54795.jar | 0.8.8 (2025-12-04) | 0.8.9.1-hotfix (2026-08-20, release) | 8 | B | 0.8.9.1 adds vehicles (AC-130H, Kirov airship, Archer SPG, Air Sheep, Happiest Ghast), perks, tools, ammo, a catapult controller, vehicle keys and skin sprays: every new vehicle needs a line in gscraft_recipes.js (off-roster strip) and a place in the blueprint design; configs re-check; client and server must match |
| ParCool-1.20.1-3.4.2.0.jar | 1.20.1-3.4.2.0 (2025-11-21) | 1.20.1-4.0.0.3 (2026-08-30, alpha) | 7 | C | 4.0.0.x is alpha; skip until a release |
| recruits-1.20.1-1.14.0.jar | 1.14.0 (2025-12-06) | 1.15.2 (2026-06-29, release) | 7 | B | 1.15: routes on the world map, siege fixes, better target finding - good for the site-guard design; a crash fix for non-living projectile hits (guns) is in 1.15.1; check recruits-server.toml keys after the jump |
| CreativeCore_FORGE_v2.12.32_mc1.20.1.jar | 2.12.32 (2025-04-04) | 2.12.39 (2026-06-23, release) | 6 | A | config crash fixes; drop-in (PlayerRevive dependency) |
| waterframes-FORGE-mc1.20.1-v2.1.22.jar | FORGE-mc1.20.1-v2.1.22 (2025-10-21) | FORGE-mc1.20.1-v2.2.0-beta.6 (2026-06-22, beta) | 6 | C | 2.2.0-beta needs WaterMedia 3 beta; skip |
| guardvillagers-1.20.1-1.6.15.jar | 1.6.15 (2025-12-08) | 1.6.19 (2026-08-23, release) | 4 | A | patrol stutter and a rare crash fixed; drop-in |
| the_knocker-1.5.0-forge-1.20.1.jar | 1.5.0 (2025-06-20) | 1.5.2 (2026-06-15, release) | 2 | A | natural spawn fix, player disguise when lurking; drop-in |
| geckolib-forge-1.20.1-4.8.2.jar | 4.8.2 (2025-09-23) | 4.8.4 (2026-06-20, release) | 2 | A | math.pi animation fix; drop-in |
| lostcities-1.20-7.5.3.jar | 1.20-7.5.3 (2026-08-31) | 1.20-7.5.4 (2026-09-03, release) | 1 | B | new profile option (railwayLevelOffset) and an in-game profile editor; no format change; v8 pre-builds its cell so only chunks beyond the border are generated - take it at the v8 server start, not into the live v6 world |
| lukis-grand-capitals-1.1.2.jar | 1.1.2+mod (2025-07-19) | 1.1.3+mod (2026-01-13, release) | 1 | C | 1.1.3 removes mansions from the structure pack; v8 places structures by hand, so no gain - keep 1.1.2 |
| voicechat-forge-1.20.1-2.6.22.jar | forge-1.20.1-2.6.22 (2026-08-08) | forge-1.20.1-2.6.23 (2026-09-04, beta) | 1 | A | 2.6.23 beta: shutdown error and off-thread camera fixes; wait for the release tag |
| Ping-Wheel-1.12.0-forge-1.20.1.jar | 1.12.0 (2025-10-22) | 1.12.1 (2026-01-02, beta) | 1 | A | localisation and Distant Horizons compat; drop-in (beta) |
| Patchouli-1.20.1-84.1-FORGE.jar | 1.20.1-84.1-forge (2025-02-06) | 1.20.1-85-forge (2026-03-08, release) | 1 | A | maintenance; drop-in |

Class A = drop-in bug fixes / libraries; B = content or config change, needs work; C = skip.

## 4. Current (no newer 1.20.1 Forge build on Modrinth)

AI-Improvements-1.20-0.5.2.jar, Apotheosis-1.20.1-7.4.8.jar, ApothicAttributes-1.20.1-1.3.7.jar, Atlas Lib-1.20.1-1.1.12.jar, Chunky-1.3.146.jar, FastFurnace-1.20.1-8.0.2.jar, FastWorkbench-1.20.1-8.0.4.jar, Immersive Vehicles-1.20.1-24.0.0.jar, ImmersiveEngineering-1.20.1-10.2.0-183.jar, LeavesBeGone-v8.0.0-1.20.1-Forge.jar, MCSP-1.20.1-V1.0.8.jar, MTS Official Pack-1.20.1-V29.jar, MagnumTorch-v8.0.2-1.20.1-Forge.jar, OAmP-1.20.1-V3.jar, Placebo-1.20.1-8.6.3.jar, PlayerRevive_FORGE_v2.0.31_mc1.20.1.jar, PuzzlesLib-v8.1.33-1.20.1-Forge.jar, The-Man-From-The-Fog-1.4-1.20.1.jar, UndergroundBunkers-1.0.5-1.20.x-forge.jar, almanac-1.20.x-forge-1.0.2.jar, antiblocksrechiseled-0.4.8.jar, appleskin-forge-mc1.20.1-2.5.1.jar, architectury-9.2.14-forge.jar, athena-forge-1.20.1-3.1.2.jar, bettercombat-forge-1.9.0+1.20.1.jar, canary-mc1.20.1-0.3.3.jar, chipped-forge-1.20.1-3.0.7.jar, chisel-forge-2.0.0+mc1.20.1.jar, cloth-config-11.1.136-forge.jar, coroutil-forge-1.20.1-1.3.7.jar, create-1.20.1-6.0.8.jar, createbigcannons-5.11.4-mc.1.20.1-forge.jar, cryonicconfig-forge-1.0.0+mc1.20.1.jar, curios-forge-5.14.1+1.20.1.jar, emi-1.1.24+1.20.1+forge.jar, factory_blocks-forge-1.4.0+mc1.20.1.jar, ferritecore-6.0.1-forge.jar, flashlight-2.1.0-forge-1.20.1.jar, getittogetherdrops-forge-1.20-1.3.jar, immersive_weathering-1.20.1-2.0.5-forge.jar, improvedmobs-1.20.1-1.13.7-forge.jar, kubejs-forge-2001.6.5-build.26.jar, letmedespawn-1.20.x-forge-1.5.0.jar, lootr-forge-1.20-0.7.35.94.jar, mob_factions-1.0.0-forge-1.20.1.jar, player-animation-lib-forge-1.0.2-rc1+1.20.jar, pomkotsmechs-forge-0.0.1-alpha.8.jar, resourcefullib-forge-1.20.1-2.1.29.jar, rhino-forge-2001.2.3-build.10.jar, ritchiesprojectilelib-2.1.1+mc.1.20.1-forge.jar, spark-1.10.53-forge.jar, tacz-1.20.1-1.1.8-hotfix.jar, tenshilib-1.20.1-1.7.6-forge.jar, worldedit-mod-7.2.15.jar, xaerominimap-forge-1.20.1-26.4.2.jar, xaeroworldmap-forge-1.20.1-1.45.0.jar, zombieawareness-1.20.1-1.13.1.jar
