# Handoff: picking the work up in another session

State as of 2026-09-04 (v6 live on the hosted server; **v7 built, reviewed and released**, deploy = section 6). Everything needed is in this repository plus the two GitHub releases;
the working machine's paths are given so a session on it can continue directly, and section 2 says
how to rebuild the same state elsewhere.


> **2026-09-05 — design integration.** The design documents were rebased on the v8 geography and the Create fork was
> adopted as a chapter; the player interface is `docs/gscraft-player-interface.md` (mockups: the "GSCraft Player
> Interface" artifact). The eighteen decisions the rebase forced are `docs/gscraft-design-gaps.md` §E, each with its
> default — read that table before any Phase C work.
>
> **Designer tools (owner, 2026-09-05):** WorldEdit stays and the players get it — `server.properties`
> `op-permission-level=2` (done locally; **hand-run on the hosted panel**: the same key, then `/op <name>` for each
> designer; the owner stays level 4 in `ops.json`); WorldEdit CUI `WorldEditCUI-1.20+01.jar` is client-only in the pack
> (`CLIENT_EXTRA_JARS`, packwiz 2026.09.05). The researched kit (Lighty, IBE Editor, Jade, Freecam, FTB Ultimine by hand)
> is `docs/notes/gscraft-designer-tools.md`, owner's pick pending.

## 1. Where things stand

**The hosted server (Bisect, 199.115.76.82:9150, panel id 493d6256) RUNS v6** since 2026-09-03 evening:
world `wasteland-v6`, MOTD "GSCraft Wasteland - test build v6", the rebuild pack with EMI added, the KubeJS
scripts, camp ruins v2, Magnum torches, dossier and site chests placed; **mob spawning is OFF** (owner) until the
designs are done and v7 lands. The rolled-back folders sit beside it as `*_old_20260902`. The deploy recipe that
was used is section 6.

**The finished v6 world** is `G:/GSCraft/server/wasteland-v6` on the working machine (the local test
server's world; tower stage 0 placed, roads laid, three KubeJS scripts armed, boot clean) and GitHub
release `build-v6-2026-09-03` (three region zips under 1.9 GB + a meta zip; unpack all four into one
`wasteland-v6` folder). The design it implements is `docs/gscraft-map-design.md` (draft 6) with the
placements of `docs/gscraft-map-layout-v6.md`; the whole-world audit is `docs/gscraft-map-review-v6.md`.

What v6 contains: the 10 km pre-generated box (border 10,000 centred 1900,1250); the camp with the
radio tower compound (x 64..191, z -144..-17, pad y 99, locked) and six NPC building pads; Novo Expograd
Industrial Zone on the spine 1.06 km east; Financial Plaza + sewers on dry land 2.1 km west; the
settlement 3.7 km east; Bio Gen + the runway 3.9 km south-east; the Novo Expograd hub 6.2 km east in
the air ring; four routed roads (camp-Novo-district, camp-plaza, district-runway, district-settlement)
with no water on their lines; the old substation and hospital pads restored to terrain.

**Owner decisions on record (2026-09-03):** tower in the camp, locked so only the quest changes it;
sites re-evaluated on merit, not bound to the old pads; plaza on dry land; keep the generated cities,
make the roads connect; plant/FR-06 spacing (418 m) accepted; camp rim sites get pads; the players'
frozen-projectile complaint fixed (KubeJS sweep + simulation distance 10).

**Design revised 2026-09-03 (draft 6, quests draft 3 on 2026-09-04, crafting draft 1):** the site ladder and contested-site attacks (since 2026-09-04 every attack comes to the base), NPC building tiers with the grief lock, timed crafting at server-placed stations, the vehicle
roster, equipment crafting, garrison tables, the finale (now the Sleeper, `docs/gscraft-finale.md`), batteries for the electric vehicles.
New tools: `dossiers.py` (dossier chests, `tools/dossiers.json`, `gscraft:dossiers`), `camp_ruins.py` (24
ruin pieces in the camp, `gscraft:camp_ruins`, loot tables under `ruins/`). **EMI 1.1.24 added** to the
server's `/mods` (client-side mod; the dedicated server skips it) and to `additions.json` / `manifest.json`;
**Dynamic Flashlight 2.1.0 added 2026-09-04** (owner-approved; hash-verified; in `server/mods`, the Prism instance, `build/manifest.json`, and appended to `G:/GSCraft/release-v7/GSCraft-Client.zip` — the previous zip is kept as `GSCraft-Client-2026-09-03-emi.zip`; uploaded to the hosted `/mods` by the owner on 2026-09-04, live at the next restart; no Drive re-issue — owner 2026-09-04: the client zip goes up as a GitHub release asset with the full install). Before that, the client pack was rebuilt with EMI on 2026-09-03 (`G:/GSCraft/release-v7/GSCraft-Client.zip`, 453 MB, EMI 1.1.24
sha512-verified; goes up with the v7 release and replaces the Drive copy). `camp_ruins` has been run on the hosted world (24 pieces, read back from the region files). `tools/furnish.py`
places loot chests in sites that came across without any (Novo has none above ground: its 1.12 source had
34 k blocks and no containers; the plaza has one) — `gscraft:furnish_novo` and `gscraft:furnish_financial`, 12
chests each, tables `gscraft:sites/*`. All loot tables carry vanilla stand-in items with the intended
`gscraft_item` beside each entry until Phase C. `docs/gscraft-mod-capabilities.md` is the pack review.

**Cheap work done 2026-09-03 evening, all on the hosted world and read back:** the 24 camp ruins rebuilt from
Doomsday Decoration wrecks, sandbags, drums, wire and cones (`camp_ruins.py` v2; `gscraft:camp_ruins_clear` took
the v1 blocks out first, 1,222 setblocks); ten diamond Magnum Torches (`gscraft:camp_torches`, `tools/camp_torches.json`)
make the camp's spawn suppression physical; `hordes-common.toml` now has `infectPlayers = true` and `bandits.json`
`enableMod = false` — both uploaded to `/config`, **both take effect only at the next server restart**. Design §2.2
and §6.3, quests D2/T1/T5 and `gscraft-mod-capabilities.md` §5 record it. `tools/structures_v6.json` is the census of
every generated structure start in the 10 km box (Lukis capitals, outposts, bunkers) for the loot-site list.

**MOB SPAWNING IS OFF on the hosted server (owner, 2026-09-03) until the designs are done:** `gamerule doMobSpawning
false` + `doPatrolSpawning false` (persisted in the world), a deny-all-hostile rule at the top of `config/incontrol/spawn.json`
(loads at the next restart, or when an op runs `/incontrol reload` in-game — the console cannot: it needs a player),
and `enableHordeEvent = false` in `hordes-common.toml` (the horde event stays off for good — design decision B6; only
infection runs). Until that restart the gamerule alone is what stops spawns. To turn spawns back on for Phase D: run
`function gscraft:spawns_on`, delete the first rule of `spawn.json`, run `/incontrol reload` as an op (or restart). `function gscraft:spawns_off` re-applies the off state and kills the loose hostiles.

**World build v7 was built on 2026-09-04** (below, and `docs/gscraft-map-review-v7.md`). The reason it exists (owner, 2026-09-03): the generated structures are too dense (964 sites);
`docs/gscraft-structure-plan.md` and `buildmap/structure_plan_v7.json` keep 67 and prune 897. Route: datapack override
disabling the pruned structure sets, re-run the 10 km pre-generation on the build machine (20 GB heap), place the 67 back
at their census coordinates, then the v6 pipeline unchanged (pads, transplants, roads, camp ruins, torches, dossiers,
furnishing). Spawns stay off until the owner's Phase A pass on v7 is done — that also keeps the boss spawners quiet. Owner also ruled: vvp, MCSP,
Immersive Weathering, the server tools and the TaCZ fire-control extension all STAY (uses in `gscraft-mod-capabilities.md`
§4 and `gscraft-crafting.md` §2.1: the military vehicle tier and the dead-vehicle site dressing).

**The Line (this workstation, 2026-09-04):** a rural power-line corridor from the camp's south edge to the residential
block's west gate — farmstead, pump house, substation A on the freed pad, depot, substation B, switching station, 56
pylons — `tools/theline.py` → `gscraft:theline`, `buildmap/theline_v7.json`, loot `gscraft:sites/line`; design §2.6,
quests §7.5 (L1–L6, L6 gates R3; 144 quests). Placed on the hosted v6 world with force-loading. **For v7 add
`gscraft:theline` to the camp-functions step** (after roads: it reads ground from the built world, so re-run
`theline.py` against the v7 region set first and re-upload `line_*.nbt` + the function). `tools/landuse.py` measures
city/wilderness per chunk (§5 of the structure plan): 6 % of the land is city by the building fingerprint, so the
balance stands and the lower-density LC profile that was staged is withdrawn.

**Enemy design (this workstation, 2026-09-04): `docs/gscraft-enemies.md` draft 1.** Five factions (the Dead,
Scavengers, the Militia, the Horrors, the Camp), ranks with per-act equipment set through In Control!'s rule
fields, four wave roles, six elite definitions, mob drop tables, difficulty by ring. **Four config defaults are
wrong and want fixing before the next player test** (enemies §8): Improved Mobs' `Stealer Chance` (mobs open
containers — `StealGoal` verified in the jar), its empty `Item Blacklist` (a mob can pick up a dropped rocket
launcher), Pillagers Gun's bazooka at the camp gate, and the ten `recruits:` ids missing from Mob Factions'
civilian faction. The config edits are not applied yet — they are one file each in `build/phase05/config`.

**Handoff state:** the hosted server runs v6 with EMI in `/mods` (client pack rebuilt with EMI on 2026-09-03: `G:/GSCraft/release-v7/GSCraft-Client.zip`), ruins v2, torches, dossier
and site chests in place; the datapack on the server matches `build/datapacks/gscraft` except `dossiers_fill`, parked
in `build/phase_c/`. Loot tables carry vanilla stand-ins until Phase C. Pending on the working machine: the owner's Phase A flight on v7 (local server up in the visual profile), then the hosted deploy of v7 (section 6).

**World build v7 - DONE 2026-09-04 (this is the sequence that was run; `README-local.md` on the working machine has the timings):** `tools/carve_regen.py <pregen> <carved>` (keeps the v5 rects +
camp, drops 405,699 chunks), copy `build/datapacks/gscraft_worldgen` into `<carved>/datapacks`, `tools/localpregen.py`
on it (2 h 15 min, cycling), `carve_regen.py --drop-rect -1024 -1536 4607 4095` (the inner rings Chunky generated before the palette fix landed in
life 5; the v5 rectangles and the camp are spared) + one more `localpregen.py` pass over the box to regenerate them - the
error chunks are HOLES with no city at all, about a third of the city chunks generated before the fix,
then `tools/place_kept.py <server>` (batches of six: force-load, wait, place, release; never as one function), then `buildv6.py`, `roads.py
build`, the camp functions (`gscraft:camp_ruins`, `camp_torches`, `dossiers`, `furnish_novo`, `furnish_financial`, `runway_lights`),
`reviewv6.py`, release, deploy (section 6). Details: `docs/gscraft-structure-plan.md` section 3, route A'.
Result: 421,775 chunks, 0 LC errors after the fix, 67/67 kept + 5/5 Woods sites verified, 0 edge gaps, five roads (52,134 columns), spawn 19 94 26. World: `G:/GSCraft/server/wasteland-v7` (server copy, has the player flight's chunks after Phase A) and `scratch/worlds/wasteland-v7-final` (release master); release `build-v7-2026-09-04`. Three tool fixes went in: `roads.py route` now bounds its search (the spur's A* had reached 23 GB), a city scan must skip sections below y 32 (geodes), and Lost Cities keeps street/highway modes in `<world>/data/LostCity*.dat` so a profile switch on an existing world changes only city/scatter/railway settings.

**The Woods (owner, 2026-09-04):** a Tarkov-style wilderness zone, x 400..2400 z -3500..-1500 (2 x 2 km, 2.9 km NNE of the
camp, 65 % forest, no snow), built AFTER the v7 pre-generation: carve the rectangle, regenerate it under the `woods` Lost
Cities profile (no cities/highways/railways/scattered buildings; identical terrain), five sparse structures, a road spur
from Novo. Plan and quest hooks: `docs/gscraft-woods-plan.md`. **Built in v7** (0.5 % city-fingerprint chunks inside vs 48 % outside; bunkers at 1264,-2400 and 1632,-2752, outpost 720,-3440, fog-man houses 2048,-2672 and 1900,-2000; spur 2,352 m). The custom sites (sawmill, cabin, aircraft, hide) wait for `camp.py`.

**Design addendum (owner, 2026-09-04):** military vehicle blueprints (Humvee RWS, Black Hawk, Bradley) are mid/late quest
rewards (W-M1, W-B3, X6), never tier unlocks - crafting §2.1, quests draft 2.

**Client crash fixed 2026-09-04:** Parties 2.0-beta-p.7.1 + Xaero's Minimap 26.4.2 crash every client at mod setup (`xaero/common/gui/IScreenBase`). `parties_xaerominimap_fix-1.0.0.jar` (CurseForge 1589418, client-side only, owner-approved) is in the Prism instance, `release-v7/GSCraft-Client.zip`, the packwiz pack (`mods/parties-xaerominimap-fix-1-0-0.pw.toml`, side client, asset on `pack-files-2026-09-04`) and the manifests; `tools/packwiz_build.py` carries it in `CLIENT_EXTRA_JARS` (client-only jars that live in the Prism instance, not in `server/mods`), so a pack rebuild keeps it. The installer bundle, mrpack and instance zip on `client-installer-2026-09-04` were refreshed with it. Never put it in the server's `/mods`.

**Startup-script crash fixed 2026-09-04 02:07 - HOSTED SERVER NEEDS THE FILE:** `build/kubejs/startup_scripts/gscraft_tower_lock_native.js` called `entity.level()` in the mob-griefing handler; Rhino exposes Java accessors as properties, so the first ticking animal near a player (a dolphin) threw `TypeError: Cannot call property level` and crashed the server (the hosted v6 has been safe only because `doMobSpawning` is off there). The script now reads accessors either way and wraps every handler in try/catch; tested with a summoned dolphin, cow and creeper. Uploaded to the hosted `/kubejs/startup_scripts` on 2026-09-04 late; takes effect at the next restart.

**V8 IS THE LIVE LINE OF WORK (2026-09-05).** Plan and build log: `docs/gscraft-map-plan-v8.md`. Basis = the owner-supplied
"Pripyat After the Accident" world (1.16.5 -> 1.20.1 by `upgrade112.py`, `scratch/upgrade/pripyat_after/world`), border A
x -3900..1200 z -3900..700, relief authored from zones (`heightplan.py`) and applied by whole-column shifts (`applyheight.py`),
40 transplants placed by the art-pass placer (`place_sectors.py` -> `buildmap/plan_v8/sectors_v8.json`,
`plan_v8.py` -> `transplant_plan_v8.json`, `runplan.py` with block-exact shifts), edges graded (`grade_v8.py`, dirt/grass). Pass 3
(2026-09-05): `integrate.py` rebuilds a sector footprint keeping only the build's own columns on the restored landscape
(hub, Skadowsky done; mega/indu/settle pending), `river.py` v2 carves the meandering stepped river to the lake, and
`anvil.py` `Chunk.set` creates empty sections on demand (an old silent block-loss bug). Renders in `incoming/census/`
(`v8_cell_pass3_inspect.png`). Pass 3b: `river.py` carved the region's main river (lake -> along Skadowsky's west side -> out of the cell at z 700), `bridge.py` carried the Skadowsky highway viaduct across it, `statusfix.py` made all 1.12-upgraded chunks `full` (the tools had been skipping 7 k of them), `edgeaudit.py` lists every linear feature running off a footprint edge for step 8, `unroad.py` strips a mis-laid road. Plan `docs/gscraft-map-plan-v8.md` §5.
Mod pack (2026-09-05): the local server runs Forge 47.4.23 with 17 updated jars (Superb Warfare held at 0.8.8 by its
add-ons' exact pins); boot clean; conflict review clean (`tools/modcheck.py`); `docs/gscraft-modpack-update-applied-2026-09-05.md`.
The hosted server still runs 47.4.10 with the old jars - it moves with the v8 release (hand-run, §6).
Build world `scratch/worlds/v8-build`; staged copy `server/wasteland-v8` with `server.properties.v8visual`. The owner's
fly-through is the review; steps 6-9 of the plan (clean-up, road hooks in the Skadowsky vocabulary, Lost Cities modules
inside city zones, props) follow. The second Pripyat pack (1.21.8 town centre) is the detail donor, remap `remap121.json`.

**MAP REPLAN (owner, 2026-09-04 late): v7 is parked, no more edits to it.** The owner's flight found the camp cut into a Lost Cities grid at seven pad heights (the design's 384x384 cleared area was never cleared), terraces at every pad edge, generated buildings in senseless places, too much relief in the generator, and a 10 km box that is far too big to traverse. Decision: design the map again, roads first, denser and smaller. Tools that came out of it: `tools/grade.py` (one continuous surface: core level, smoothstep falloff, crater bowl, buildings removed - replaces every pad ramp; wired into `buildv6.py` as `campgrade` + the `ramps` step, tested on the camp only), and the **Wasteland Road Plan** page `tools/planner/` (build_planner.py + template + plan_defaults.json), published as a Claude artifact with the `db` capability at https://claude.ai/code/artifact/5e91332d-e204-4c97-8905-64ebfb9de8f3 - rebuilt the same night as a BLANK CANVAS (owner: redesign from the ground up): the world border, every element at its real footprint (camp, Skadowsky sector, each preserved player build, pads) at a default position, city/wilderness zones, and a road generator (spanning tree from the camp's gates + rings, bends around other elements; roads are bound to element gates so they follow moves); the owner repositions everything, and Save writes `plans/current`, which the assistant reads with the Artifact tool's `read_db`. New source material: **Region Skadowsky: Sector 0 v1.2** by _Tu4ka_ (Planet Minecraft, free world download, 1.20.1, vanilla blocks + 16 TaCZ gun smith tables), a 500x800 hand-built Tarkov-style sector (factory, housing, lab strip, river + bridge, highway, rail) in `G:/GSCraft/incoming/skadowsky/` with a census (`clusters_1.2.json`, `skadowsky_1.2_topdown.png`) - to be transplanted whole. Next: the owner's plan from the page -> terrain plan (flatter relief, Lost Cities only inside drawn city zones - verify LC 7.5.3 predefined cities) -> 2 km test cells -> the box.

**Create + Create Big Cannons added 2026-09-04 (owner: SW artillery is unfun; Create Big Cannons was immersive):** `create-1.20.1-6.0.8.jar` (embeds Flywheel 1.0.5, Ponder, Registrate), `createbigcannons-5.11.4-mc.1.20.1-forge.jar`, `ritchiesprojectilelib-2.1.1+mc.1.20.1-forge.jar` — Modrinth-hosted, in `server/mods`, the Prism instance, `build/manifest.json` (115 entries), `build/additions.json`, `scratch/modrinth_files.json`, the packwiz pack and the installer assets. Isolated boot test clean. Design fork: `docs/gscraft-create-and-artillery.md` (Create by NPC, six **site keeper** NPCs with tier 1–3 rebuild chains per strongpoint, the Big Gun chain G1–G10); parent docs carry pointers, merge when adopted. **Uploaded to the hosted `/mods` on 2026-09-04 late (panel `put` from the working machine went through); the hosted server still needs a RESTART to load them (owner).**

**Water Frames restored 2026-09-04 (owner):** `waterframes-FORGE-mc1.20.1-v2.1.22.jar` was in the pre-rebuild pack and the rebuild dropped it; back in `server/mods` and the client, with `watermedia-2.1.37.jar` CLIENT ONLY (the jar's own dependency declaration; `CLIENT_EXTRA_JARS` in `packwiz_build.py`). Uploaded to the hosted `/mods` the same night; restart pending (owner).

**Startup-script scope trap (found by that boot):** KubeJS startup scripts share one scope. `gscraft_mech_griefing.js` and `gscraft_tower_lock_native.js` both declared `const Result` → "redeclaration of const" → KubeJS refuses to load → **the server does not boot**. The tower lock now uses `TL_Result`; never declare a bare `Result`/`Java` alias at top level in a startup script. Other boot noise from the same session's additions, unfixed: In Control `Invalid keywords for spawn.json: minx maxz maxx minz`, Keerdm `*_vics` loot tables failing to parse, `pomkots.forge.mixins.json` without `minVersion`.

**Not started:** `tools/runway_lights.py` → `gscraft:runway_lights` (camp spec §5, Phase B); Phase A (the owner's mob-free visual pass on the local server, `start-visual.bat`);
`camp.py` (the six NPC buildings as templates onto their pads); the systems (KubeJS items, blueprints,
stages, the strongpoint loop and timers; FTB Quests chapters from `docs/gscraft-quests.md`; loot tables
by building type); the Superb Warfare small-arms toggle (done 2026-09-04: `gscraft_recipes.js` 2c strips every SW table recipe; the §5.2 station orders are the way back); old-world housekeeping on the hosted server
after the flight.

## 2. Setting up

1. Python 3.11+ with `numpy` and `pillow`. Java 17 (Temurin). Nothing else for the tools.
2. Clone this repo. Panel access: `~/.bisect/config.json` =
   `{"panel": "https://games.bisecthosting.com", "token": "<ptlc_ client API key>", "server": "493d6256"}`.
   The key comes from the panel's Account > API Credentials; never commit it, never paste it in chat.
3. Release `handoff-2026-09-02`: `GSCraft-Client.zip` (Prism instance for players),
   `gscraft-server-mods-1.20.1.zip` (the pinned jars -> `tools/build/mods/`), `wasteland-region-pristine-v2.zip`
   (pre-edit region set -> `scratch/worlds/wasteland/region/`), `wasteland-region-edited-v5.zip`, the non-world
   server backups. Release `build-v6-2026-09-03`: the finished world.
4. A local test server: Forge 1.20.1-47.4.10 installer + the mod zip + `build/phase05/config` + `build/kubejs`
   + the world; `eula=true`; heap 20 GB for pre-generation (8 GB is enough for play). The working machine's
   layout is `G:/GSCraft/{repo, server, scratch, incoming, release, release-v6}` and `G:/GSCraft/README-local.md`
   is its running log.
5. Panel link test: `python tools/bisectpanel.py resources` (Git Bash needs `export MSYS_NO_PATHCONV=1`).

## 3. The tools, in the order the work uses them

| Stage | Tool | Notes |
|---|---|---|
| Read a 1.20 world | `topdown.py`, `worldscan.py`, `scanregion.py`, `renderv6.py` | `renderv6.py <region> <out>` renders the box and every planned site with terrain stats. |
| Read a 1.12.2 save | `anvil112.py info/census/topdown` | names blocks from the save's FML registry. |
| Convert 1.12 builds | `extract112.py` -> `upgrade112.py` -> `makeremap112.py` -> `merge112.py` -> `verify112.py` | vanilla layer by the vanilla server's `--forceUpgrade`, modded layer by `remap112.json`; verified block by block. Details `docs/notes/gscraft-foreign-builds-plan.md`. |
| Pre-generate | `localpregen.py <server> --center 1900 1250 --radius 5000 --border` | cycles the server every ~12k chunks (Lost Cities' caches OOM it otherwise); 2 h 15 min for the box. `pregen.py` is the old panel-driven version. |
| Build the world | `buildv6.py <pregen world> <build dir>` | copy, restore, pads (`pads_v6.json`), transplants (`buildmap/transplant_plan_v6.json`, dy + section stacking), smooth, clear-ring, ramps, camp pads (`pads_camp.json`), gaps. ~11 min. |
| Roads | `roads.py route/build/check` | waypoints `buildmap/roads_v6.json`, routed polylines `buildmap/routes_v6.json`. Route on 8-block cells (~13 min), build ~5 min. |
| In-game steps | `localconsole.py <server> "<cmd>" ...` | boots the local server, runs commands (tower stage 0, spawn), stops; prints the error/warn counts. |
| Audit | `reviewv6.py <world> <out prefix> --pristine <pregen world>` | ~35 min, whole world; report .md + .json. |
| Radio tower | `tower.py build` | six stage templates + functions into `build/datapacks/gscraft`; PAD/GROUND_Y are the camp pad. |
| Map page | `makemap.py` | `docs/wasteland-district-map.html`, with the v6 layer from the plan and pads. |
| Terrain primitives | `terrain.py pad/ramp/smooth/outline/gaps`, `runpass.py`, `strongpoints.py` | used by `buildv6.py`; tower and crater rects are protected. |
| Hosted server | `bisectpanel.py` (verbs ls cat get put putdir mkdir mv rm power cmd setvar pull backup), `mcping.py`, `backup.py` | see section 6. |

Traps, all documented in `docs/notes/`: Git Bash path conversion (`MSYS_NO_PATHCONV=1`); backslashes and
apostrophes inside Bash heredocs get mangled - put scripts in files; the two superflat saves have ground at y 230
(Novo) and y 54 (plaza), never trust the spawn point; the pre-gen OOM; KubeJS 2001 exposes `ForgeEvents` to
startup scripts only; Chunky's saved task must be deleted before a fresh box (`config/chunky/tasks`); the Lost Cities
`state is null` chunk errors come from the Keerdm palette override missing the `{`/`\` characters the stuff generators use -
the world datapack `build/datapacks/gscraft_lcfix` fixes it and belongs in every world's `datapacks/` (v7 has it; v6 worlds
do not, but they are fully generated so it no longer matters there).

## 4. The design documents

- `docs/gscraft-mod-capabilities.md` - what each mod supplies to the design; the config changes made (§5b, §5c).
- `docs/gscraft-structure-plan.md` - the generated-structure prune (67 of 964 kept) behind world build v7.
- `docs/gscraft-woods-plan.md` - the Woods: where, what is in it, how it is built, the adopted quest hooks.
- `docs/gscraft-map-design.md` - THE design (draft 6): the game in one paragraph, the map's three ranges,
  the camp and its six NPCs, strongpoints, the item ladder, storage, hideout functions, the loop and
  timers, the tower, tech stack, build order with test gates.
- `docs/gscraft-crafting.md` - stations and timed orders, the vehicle roster and recipes, equipment crafting, the capability audit (draft 1 + the 2026-09-04 sheet §5.6–§5.7).
- `docs/gscraft-quests.md` - all 138 quests, seven NPC chapters (Teddy the Hermit at the Woods outpost: explosives), what FTB Quests needs from KubeJS.
- `docs/gscraft-modpack-review.md` - the mod set against the design (2026-09-04): everything the design names is installed; two updates required (Dynamic Flashlight 2.1.0 to add, EMI to sync locally); twelve manifest conditional-libraries are reference only; nothing removed.
- `docs/gscraft-vendors.md` - the vendor system (2026-09-04): seven counters (Teddy's loyalty = his quests), loyalty = building tier for the camp six, prices, barters, night vision, the merchant-offers mechanism.
- `docs/notes/gscraft-one-click-install.md` - the one-click client install (research + **built 2026-09-04**): `tools/packwiz_build.py` writes `build/packwiz/` (the pack manifest, served raw from main — the pack self-updates on every launch) and the release assets; GitHub release `client-installer-2026-09-04` (marked Latest) carries ONE asset, `GSCraft-Installer-<date>.zip` (the two setup cmds, `GSCraft-Instance.zip`, `GSCraft.mrpack`, README); the prerelease `pack-files-2026-09-04` hosts what the pack downloads by itself (the 28 non-Modrinth jars, the TaCZ packs, the bootstrap, the import files) — players never open it. **Acceptance test passed by the owner on 2026-09-04** (fresh machine, `GSCraft-Setup.cmd`, sign-in, first Play). **Official-launcher route** added the same day: `GSCraft-VanillaLauncher.cmd` (private Temurin 17 JRE into `%LOCALAPPDATA%\GSCraft\java`, Forge 47.4.10 `--installClient`, packwiz into `.minecraft`, forge profile renamed GSCraft with 6 GB) — tested against a scratch `.minecraft` (97 mods, 115 configs, profile set); its players re-run the file for updates. The bundle `GSCraft-Installer-2026-09-04.zip` holds the two cmds, the instance zip, the mrpack and a README. **Any pack change now = edit the sources, run the tool, commit `build/packwiz`, re-upload changed assets to `pack-files-*`** (a changed jar → that release; a changed cmd/instance → rebuild the bundle on the installer release).
- `docs/notes/gscraft-pomkots-mechs.md` - Pomkot's Mechs (2026-09-04): **added** after the isolated server test — hub ambient (In Control rules), the PMB01 Custodian (J-H1), one PMV01B (W-M2), dormant units at FR-06 and the hub, griefing denied by `gscraft_mech_griefing.js`; Leawind's Third Person on every client. Hosted `/mods` needs both jars, `/kubejs/startup_scripts` the new script, `/config/incontrol` the two rule files — by hand (§6).
- `docs/notes/gscraft-flashlight-and-nvg.md` - flashlight / night vision / thermal research; recommends adding Dynamic Flashlight 2.1.0 (owner's call).
- `docs/gscraft-loot-tables.md` - every loot table by building type and site, the hub economy, the reward containers (2026-09-04).
- `docs/gscraft-camp-spec.md` - camp.py's spec: function names, the board's blocks and colours, the rack, signs, guards, runway lights, flashlight, notebook (2026-09-04).
- `docs/gscraft-finale.md` - the finale (2026-09-04): candidates checked against the jars, the Sleeper (named Warden) + Captains design, fail/retry, the Phase E build and test list.
- `docs/gscraft-design-gaps.md` - the cross-document audit (2026-09-04): 18 stale facts fixed, 40 owner decisions with defaults, 18 items assigned to phases.
- `docs/gscraft-onboarding.md` - how the game teaches itself: the first session minute by minute, each system's
  teaching moment, the book as a journal, the survivor's notebook (Patchouli), what Phase C must build for it.
- `docs/gscraft-map-layout-v6.md` - every rectangle, offset, vertical shift and pad level as built; the
  tower lock; roads.
- `docs/gscraft-map-review-v6.md` - the audit, the issues raised and the decisions taken.
- `docs/notes/gscraft-scale-and-travel.md` - speeds, travel times, why 10 km.
- `docs/notes/gscraft-foreign-worlds.md` and `gscraft-foreign-builds-plan.md` - the 1.12.2 saves and how
  they were brought across.
- `docs/wasteland-server-blueprint.html` - the original design record; `docs/gscraft-server-audit.html` -
  the server as found; `docs/wasteland-district-map.html` - the map page.

## 5. Systems still to build (the next sessions' work)

In the design's order (design section 9): Phase A visual pass -> `camp.py` (NPC buildings + the summon
function `gscraft:camp_npcs`) -> Phase C systems v1 (KubeJS items with stack sizes and the bulky rule,
the station recipes and `bp_*` stages, datapack loot tables by building type, NPC right-click -> quest book, the five
introduction chapters, Walker's storage levels) -> Phase D (held flags, the site guard per held site, fortify clock, warnings, the counterattacks at the base — owner 2026-09-04,
the site guard, occupier and component respawn, garage tier) -> Phase E (tower stages 1-5 wired to Marshall's chapter,
the hub's rare loot, aircraft, the beacon countdown and base waves). The KubeJS scripts that exist: `gscraft_recipes.js` (the bench-recipe strip),
`build/kubejs/server_scripts/gscraft_fixes.js` (recipe fix), `gscraft_tower_lock.js` + `startup_scripts/
gscraft_tower_lock_native.js` (the lock), `gscraft_projectiles.js` (projectile sweep).

## 6. Deploying a world build to the hosted server (hand-run; this is how v6 went up)

The working-machine assistant is not permitted to run panel calls that change the hosted server (the
auto-mode permission classifier blocks them, uploads included), so this is run by a person from
PowerShell in `tools/` with `~/.bisect/config.json` in place. `W` = `G:/GSCraft/server/wasteland-v6` (for v7: `G:/GSCraft/scratch/worlds/wasteland-v7-final`, folder `/wasteland-v7`, properties `B/phase03/server.properties.v7`, and the datapacks now include `gscraft_worldgen` and `gscraft_lcfix` — mirror all three),
`B` = the repo's `build/` folder. Uploads can be done first, while the old server is still running.

1. World folders and upload (about 5.3 GB; `putdir` uploads every file in one folder, `put` one file):
   `python bisectpanel.py mkdir /wasteland-v6`; then `mkdir` for `/wasteland-v6/region`, `/entities`, `/data`,
   `/serverconfig`, `/datapacks`, `/datapacks/gscraft`, `/datapacks/gscraft/data`, `/datapacks/gscraft/data/gscraft`,
   `.../functions`, `.../structures`, and the loot-table and recipe folders that exist under
   `B/datapacks/gscraft/data` (mirror the tree). Then `putdir W/region /wasteland-v6/region` (441 files),
   `putdir W/entities /wasteland-v6/entities`, `putdir W/data /wasteland-v6/data`,
   `putdir W/serverconfig /wasteland-v6/serverconfig`, `put W/level.dat /wasteland-v6`, and `putdir` for each
   datapack folder into its mirror; `put B/datapacks/gscraft/pack.mcmeta /wasteland-v6/datapacks/gscraft`.
2. Scripts: `mkdir /kubejs`, `/kubejs/server_scripts`, `/kubejs/startup_scripts`; `putdir B/kubejs/server_scripts
   /kubejs/server_scripts`; `putdir B/kubejs/startup_scripts /kubejs/startup_scripts`.
3. Properties: `put B/phase03/server.properties.v6 /`.
4. `python bisectpanel.py power stop`; wait until `resources` says offline.
5. Swap the folders: `mv /mods /mods_old_20260902`, `mv /mods_wasteland_20260902 /mods`; the same two renames
   for `config` and `defaultconfigs`. Then `mv /server.properties /server.properties.old`,
   `mv /server.properties.v6 /server.properties`.
6. Startup: `setvar AIKARS_ENABLED 1`; `setvar CUSTOM_ARGS "<the Aikar -XX set in docs/notes/gscraft-phase-log.md,
   phase 02>"`.
7. `power start`. After two minutes `cat /logs/latest.log` shows Done, the benign error set (11 Immersive
   Vehicles model quirks + 1 dist probe) and three `[gscraft]` lines (tower lock native, tower lock, projectile
   sweep); `python mcping.py 199.115.76.82 9150` answers with MOTD "GSCraft Wasteland - test build v6".
8. Later, after the flight: remove the old worlds (`Escape From Minenkrafte`, `Escape From Minecraft`, `world`,
   `region`, the 557 MB zip) and the `*_old_20260902` folders.

Rollback is the reverse: `scratch/rollback/rollback.py` on the working machine holds the recipe used on
2026-09-03 (stop, swap back, delete the rebuild world and kubejs, old properties, Aikar off, start).

## 7. Release assets

`handoff-2026-09-02` was deleted on 2026-09-04 (owner: not needed); every one of its 15 assets is kept on this machine in `G:\GSCraft
elease\` (sizes verified before deletion). `build-v6-2026-09-03` (4 assets): the finished v6 world. `build-v7-2026-09-04` (5 assets): the finished v7 world (three region parts + meta, unpack into one `wasteland-v7` folder) and the client pack with the Parties/Xaero fix. `pack-files-2026-09-04` carries the packwiz-hosted jars including `parties_xaerominimap_fix-1.0.0.jar`. Player identity files
(ops, whitelist, user caches) are deliberately not published. `tools/release_upload.py` re-uploads a folder
of zips to a tag, skipping what is already there.
