# Handoff: picking the work up in another session

State as of 2026-09-03 09:00. Everything needed is in this repository plus the two GitHub releases;
the working machine's paths are given so a session on it can continue directly, and section 2 says
how to rebuild the same state elsewhere.

## 1. Where things stand

**The hosted server (Bisect, 199.115.76.82:9150, panel id 493d6256)** is running the OLD pack and world
(`Escape From Minenkrafte`, rolled back 2026-09-03 morning). The rebuild's folders sit beside it as
`/mods_wasteland_20260902`, `/config_wasteland_20260902`, `/defaultconfigs_wasteland_20260902`; the
rebuild's `/wasteland` world and `/kubejs` were deleted there (copies exist locally and in the releases).
**Deploying v6 to it is the open task** - section 6.

**The finished v6 world** is `G:/GSCraft/server/wasteland-v6` on the working machine (the local test
server's world; tower stage 0 placed, roads laid, three KubeJS scripts armed, boot clean) and GitHub
release `build-v6-2026-09-03` (three region zips under 1.9 GB + a meta zip; unpack all four into one
`wasteland-v6` folder). The design it implements is `docs/gscraft-map-design.md` (draft 5) with the
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

**Not started:** Phase A (the owner's mob-free visual pass on the local server, `start-visual.bat`);
`camp.py` (the six NPC buildings as templates onto their pads); the systems (KubeJS items, blueprints,
stages, the strongpoint loop and timers; FTB Quests chapters from `docs/gscraft-quests.md`; loot tables
by building type); the Superb Warfare small-arms toggle; old-world housekeeping on the hosted server
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
startup scripts only; Chunky's saved task must be deleted before a fresh box (`config/chunky/tasks`).

## 4. The design documents

- `docs/gscraft-map-design.md` - THE design (draft 5): the game in one paragraph, the map's three ranges,
  the camp and its six NPCs, strongpoints, the item ladder, storage, hideout functions, the loop and
  timers, the tower, tech stack, build order with test gates.
- `docs/gscraft-quests.md` - all 77 quests, six NPC chapters, what FTB Quests needs from KubeJS.
- `docs/gscraft-map-layout-v6.md` - every rectangle, offset, vertical shift and pad level as built; the
  tower lock; roads.
- `docs/gscraft-map-review-v6.md` - the audit, the issues raised and the decisions taken.
- `docs/notes/gscraft-scale-and-travel.md` - speeds, travel times, why 10 km.
- `docs/notes/gscraft-foreign-worlds.md` and `gscraft-foreign-builds-plan.md` - the 1.12.2 saves and how
  they were brought across.
- `docs/wasteland-server-blueprint.html` - the original design record; `docs/gscraft-server-audit.html` -
  the server as found; `docs/wasteland-district-map.html` - the map page.

## 5. Systems still to build (the next sessions' work)

In the design's order (draft 5 section 9): Phase A visual pass -> `camp.py` (NPC buildings + the summon
function `gscraft:camp_npcs`) -> Phase C systems v1 (KubeJS items with stack sizes and the bulky rule,
IE blueprint recipes, datapack loot tables by building type, NPC right-click -> quest book, the five
introduction chapters, Walker's storage levels) -> Phase D (held flags, fortify clock, warnings, attacks,
garrison and component respawn, garage tier) -> Phase E (tower stages 1-5 wired to Marshall's chapter,
the hub's rare loot, aircraft, the beacon countdown and base waves). The KubeJS scripts that exist:
`build/kubejs/server_scripts/gscraft_fixes.js` (recipe fix), `gscraft_tower_lock.js` + `startup_scripts/
gscraft_tower_lock_native.js` (the lock), `gscraft_projectiles.js` (projectile sweep).

## 6. Deploying v6 to the hosted server (hand-run)

The working-machine assistant is not permitted to run panel calls that change the hosted server (the
auto-mode permission classifier blocks them, uploads included), so this is run by a person from
PowerShell in `tools/` with `~/.bisect/config.json` in place. `W` = `G:/GSCraft/server/wasteland-v6`,
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

`handoff-2026-09-02` (15 assets): client pack, server mod set, pristine v2 and edited v5 region sets, the
non-world server backups. `build-v6-2026-09-03` (4 assets): the finished v6 world. Player identity files
(ops, whitelist, user caches) are deliberately not published. `tools/release_upload.py` re-uploads a folder
of zips to a tag, skipping what is already there.
