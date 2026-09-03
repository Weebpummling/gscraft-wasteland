
**`Documents\Minecraft Server Tools\build\`** — `mods\` (the rebuild's jar set, ~90 jars),
`manifest.json` (sha256 + modids + mandatory deps read from each jar's `META-INF/mods.toml`,
jar-in-jar included), `additions.json` (resolutions: version, filename, url, hash, deps).

**Audit calls overturned by data (2026-09-02):**
- **txnilib's only dependent is `chunkactivitytracker`** (not From The Fog — that was inferred).
  Chunk Activity Tracker is cut; txnilib and its bundled Fabric API go with it.
- **chaoszpack 1.3.7 declares MANDATORY deps on create, createdeco, horror_element_mod,
  minetraps, survival_instinct** — five cut mods. Replaced by TaCZ's default gun pack; Keerdm
  keeps the Lost Cities loot/structures. Fallback: patch its `mods.toml` (maintenance trap).
- **Keerdm's six failing `_vics` loot tables are unused.** Its Lost Cities conditions
  (`data/lostcities/lostcities/conditions/car_loot.json`, `chestloot.json`) reference only the
  `_tacz` twins. The audit's "empty chests" headline was wrong — it is log noise. No datapack
  needed (one was built and then deleted).

**Conditional libraries settled by manifests:** KEEP cloth-config (bettercombat), architectury
(factory_blocks, chisel, KubeJS), Atlas Lib (Hordes), almanac (letmedespawn), Placebo (Fast*
trio, Apotheosis). DROP kotlinforforge, fzzy_config, uilib, collective, supermartijn642 libs,
balm, citadel, terrablender, caelus, ritchiesprojectilelib, txnilib.

**Additions — Modrinth (1.20.1 Forge, sha512-verified):** Lootr 0.7.35.94; Improved Mobs 1.13.7
(+tenshilib 1.7.6); Canary 0.3.3; Xaero Minimap 26.4.2 + World Map 1.45.0; The Man From The Fog
1.4; KubeJS 2001.6.5-build.26 (+rhino 2001.2.3); Simple Voice Chat 2.6.22; Apotheosis 7.4.8
(+ApothicAttributes 1.3.7, Placebo 8.6.3); Chipped 3.0.7 (+resourcefullib 2.1.29); Immersive
Vehicles 24.0.0 + Official Content Pack V29 + Official Automobile Pack V3; TaCZ 1.1.8-hotfix;
LC²H 3.5.0. Modrinth API needs only a User-Agent.
**Additions — CurseForge (FTB does NOT publish on Modrinth; both slug patterns 404):** download by
file id from `https://edge.forgecdn.net/files/{id//1000}/{id%1000}/{filename}` — FTB Quests
2001.4.22 (8078538), FTB Library 2001.2.13 (8226927), FTB Teams 2001.3.2 (7499810), Item
Filters build.59 (4838266), FTB Chunks (id from its files page). CurseForge file pages are
readable by WebFetch; verify each jar by its `mods.toml` modId, record sha256 locally.
Open Parties and Claims was pinned as a fallback and dropped once FTB was reachable.

**Still open:** the Superb Warfare small-arms toggle (phase 05 config work); the client `.mrpack`.

Related: [[gscraft-bisect-server]], [[gscraft-player-builds]].
