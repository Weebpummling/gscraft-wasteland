
**Approach (2026-09-02):** no wipe. Old content renamed aside (`/mods_old_20260902`,
`/config_old_20260902`, `/defaultconfigs_old_20260902`); new world under a new level name. Every
step reverses with a rename. Old worlds untouched on the server; full local snapshot in `pull\`.

**Phase 02 (15:12) PASSED** — six infra jars, new `server.properties` (view 10 / sim 6, whitelist
on, spawn-protection 0, watchdog 60000, sync-chunk-writes off, `level-type=minecraft\:normal`),
`AIKARS_ENABLED=1` + Aikar `-XX` set in `CUSTOM_ARGS` (egg rejects `-Xms/-Xmx` there).

**Phase 03 (15:37) PASSED** — Lost Cities **7.5.3** alone (LC²H + Quantified cut: version
coupling). LC 7.5 has no world preset: city is switched on by `selectedProfile` in
`/defaultconfigs/lostcities-server.toml` before a new world's first boot. Never carry old
`profiles/*.json` (old `improved.json` referenced Pomkots World → crash). Profile scans:
rarecities 0 city / onlycities wall-to-wall / improved crashes on 7.5.3 / **wasteland chosen**.
**Real world `/wasteland`, seed `2404991234066556536`, profile wasteland.** Test worlds deleted.

**Phase 04–05 (15:40–15:43) PASSED** — full pinned set uploaded (96 → 95 jars after dropping
orphan `berezka_api`); boot: **102 mod IDs, Done, 2.9 GB idle**. Carried configs uploaded over
the generated defaults (`build\phase05\config\`: In Control! spawn/spawner/loot with mech rules
stripped, MobFactions with mech refs stripped, dynamicview, tacz, superbwarfare, bandits,
hostilevillages, guardvillagers, zombieawareness, hordes, PillagersGun, Eyes cycle 600/300 &
max 1, Knocker rare). Second boot: 48 WARN (from 1,437 first-run config corrections), 19 ERROR —
**known-benign set:** 11 `mts` model quirks in the two official IV packs (cosmetic), 6 Keerdm
dead `_vics` tables, 1 `RuntimeDistCleaner` HumanoidModel$ArmPose probe, 1
`factory_blocks:mason_table` recipe (Chipped 2.x type) → **fixed by KubeJS**
`/kubejs/server_scripts/gscraft_fixes.js` (shaped recipe). Anything outside this set on a future
boot is new.

**Transplant (16:31) LANDED** — write pass 14,430 chunks clean; region (41) + entities (27) uploaded
into `/wasteland/`, `/wasteland/poi` deleted; library region byte-identical on the server, chunk
(131,90) = 1,603 placed / 402 BEs. **Cleanup pass `fixspawners.py <world>`** (16:40): spawners
with cut-mod mobs -> `minecraft:zombie` (47), legacy in-chunk `entities` and entity-file records
of cut namespaces dropped (35), `LootTable` ids of cut namespaces remapped (1,168; big one:
`chaoszpack_lc_loot:chests/bigbuildings` x677 -> `lostcities:chests/lostcitychest`; 1.21-only
`trial_chambers` tables -> simple_dungeon). Cut-mod ITEMS in containers are left: the game turns
them to air silently. Boot after: 43 WARN, no skipped-entity / unknown-block lines.
**Server datapack `/wasteland/datapacks/gscraft`** (source `build\datapacks\gscraft`): overrides
`factory_blocks:mason_table` in the Chipped 3.x format (KubeJS then removes the duplicate; the
shipped `mason_table_old` is the working one) and empties Keerdm's six `_vics` tables. Benign
error set is now 12: 11 `mts` model quirks + 1 dist-cleaner probe.

**Phase 09 items done (17:00-17:15):** whitelist OFF (`whitelist off` + `white-list=false`,
`enforce-whitelist=false`; user: 5 players, no whitelist). **Chunky pregen** of every transplanted
rectangle + 2-chunk margin (`pregen.py <plan>` -> 14 merged rects, 19,369 chunks, ~7 min; Chunky
console verbs `chunky world/shape rectangle/corners/start`, "Task finished" in latest.log).
**Client pack** `build\client\GSCraft-Client.zip` (452 MB, Prism Launcher instance: mmc-pack.json
1.20.1 + forge 47.4.10, instance.cfg 6 GB, `.minecraft/{mods 95 jars, config, tacz, kubejs,
defaultconfigs, servers.dat}` pulled live from the server) + `GSCraft Install Guide.html/.md`
(Prism import route + manual official-launcher route). Public address **199.115.76.82:9150**
(alias gamesla308.bisecthosting.com); voice chat on the same port.

**Terrain tools** (`anvil.py` section codec + `terrain.py gaps|smooth|pad`, `strongpoints.py`,
`spawnmap.py`, `roofgrid.py`): gap survey found 68% of 13,072 transplanted edge columns off by
>=3 blocks, tails past 40 both ways (old-world ground ~60-70 vs wasteland 90-140). Spawn rect is
the old LAKE (surface 62) with the Warium structure (x 7-31, z 7-31, plaza roof y 93) inside a
40-80 block pit. Fix = ramps proportional to the gap (1.5 columns/block, 8-96 wide), built
columns skipped, lake columns re-flooded to 62; hempcrete counts as terrain (LC old-city ground).
Strongpoint pads (`strongpoints.json`, yellow-concrete border + corner posts): radio tower 48x48
x1815-1862 z1007-1054; substation 64x64 x1331-1394 z506-569; water treatment 80x64 x2883-2962
z691-754; hospital 96x80 x1321-1416 z1980-2059; airfield 224x96 x2773-2996 z1828-1923. Starting
area = spawn rim pad x/z -64..95 (crater -16..47 protected). World spawn to set: 19 94 26.
Map artifact: Wasteland District Map `c76b1bb4-c845-4252-9ab8-17ee4fc10c3f`.

**Terrain pass LANDED (17:31 boot, benign-12 error set, 43 WARN):** on the pre-generated world:
5 strongpoint pads levelled (radio 63, substation 63, water treatment 72, hospital 63, airfield 64
- each lifted above any water within 48 blocks), starting area x/z -64..95 CLEARED to natural
ground (crater -16..47 protected) and OUTLINED at ground level (not levelled - a levelled rim
became a 40-block wall around the basin); `smooth` ramped every transplanted edge (313k columns
planned / 230k adjusted, 1,614 chunks) and `ramp` around each pad. Gaps >=3 blocks: 68% -> 19.6%
of 13,072 edge columns, 2,374 of the remaining 2,561 are building columns (skipped by design).
Uploaded all 50 region files (sizes verified), POI deleted, `setworldspawn 19 94 26` (structure
plaza) confirmed in level.dat. Pass v1 and v2 were discarded: **`World.clear_column(x, z, from_y)`
- callers had passed (x, from_y, z)**, carving shafts in the wrong columns; always restore from
`pull
egion.zip` (pristine post-pregen server copy) before re-running a pass.
Not done in-game: flight through sites and pads (visual), still owed.

**Sizes review (user, 17:35): pads and starting area were "exceedingly small" -> resized as
COMPOUNDS, not buildings** (the mega-base is 384x528, industrial district 464x272): radio tower
128x128, substation 160x160, water treatment 192x160, hospital 192x192, airfield 512x192; starting
area 384x384 (x/z -176..207). Nothing that size fits between the builds, so the compounds sit in
the wasteland RING around the district (`strongpoints.py` search chunks 10..250 x -20..175):
radio x2023-2150 z-184..-57; substation x215-374 z1415-1574; water x3570-3761 z711-870;
hospital x675-866 z2367-2558; airfield x2959-3470 z2519-2710. Sequence used: upload the
pristine 50 files back, Chunky the new footprints (+8 chunks; 6 rects, 6,563 chunks), pull again
-> **`pullegion.zip` is now the post-pregen-v2 pristine (67 files, 418 MB)**; `runpass.py`
drives the whole pass. Map regenerated by `scratchpad\makemap.py` from
`worldsuildmap\site_inventory.json`: 409 clusters = 15 named player builds + 320 small
scatters + 74 generated ruin clusters (cracked-stone-brick/spawner/blast-furnace, or
campfire/sign/decorated-pot fingerprint) carried inside the district rectangle.

**Rollback:** `mv` the `_old_20260902` folders back, restore `server.properties` from `pull\`,
clear `CUSTOM_ARGS`, `setvar AIKARS_ENABLED 0`, delete `/wasteland` and `/kubejs`, restart.

**Still to do (phases 06–10):** blood-moon/horde test on staging base; strongpoints (KubeJS);
client `.mrpack`; Chunky pregen; whitelist names; delete the remnant worlds/zip/hs_err at launch.

Related: [[gscraft-bisect-server]], [[gscraft-rebuild-manifest]], [[gscraft-player-builds]].

**2026-09-02 evening - ACTIVATED FOR TESTING.** v5 world (compound pads 128x128..512x192 in the
ring, 384x384 starting area cleared to a rebuilt local surface and outlined, ramps everywhere)
uploaded (67 region files verified), boot benign-12, `mcping.py 199.115.76.82 9150` reachable with
forgeData; MOTD "GSCraft Wasteland - test build"; whitelist off; spawn 19 94 26. **Public repo:**
https://github.com/Weebpummling/gscraft-wasteland (tools, build configs, datapack, kubejs, client
instance files + guide, buildmap, docs pages, renders; no jars/zips/worlds/tokens; workstation paths
scrubbed by `scrub_repo.py`; staged by `stage_repo.py` into `C:\GSCraft\repo`). **Full server
backup** `C:\GSCraft\server-backup\2026-09-02\` (41 entries, 3.1 GB incl. both old worlds).
**Endgame loop (user's design, 18:0x):** taking a location starts a clock to fortify; each cycle the
game draws ONE held location at random and warns ahead (7DTD blood-moon style); defeat/death = lost,
retake it; win = held, more time to explore; every cleared POI joins the pool; all locations drop
radio-tower repair loot; tower done -> countdown -> wave defence AT THE PLAYERS' MAIN BASE, final
wave = boss. Never "hold all five". Location pool = FR-06 complex, industrial plant, hempcrete
compound, stone complex, residential block, library + the five pads.
**Testing needs a human player:** I cannot log in (no account; Forge handshake needs a real modded
client). What I can verify from here: status ping, boot log, file state. Phases 07 (KubeJS state
machine), 08 (horror measurement), in-game flight: still owed.
