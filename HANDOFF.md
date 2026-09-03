# Handoff: picking the work up on another machine

State as of 2026-09-02 evening. Everything below is reproducible from this repository plus the
release assets; nothing needed lives only on the original workstation.

## 1. What exists right now

- **Server**: Bisect Hosting, Forge 1.20.1-47.4.10, 102 mod IDs, world `wasteland` (Lost Cities
  7.5.3, profile `wasteland`, seed 2404991234066556536). Public address 199.115.76.82:9150.
  Whitelist off, MOTD "GSCraft Wasteland - test build", world spawn 19 94 26 on the spawn structure.
- **World content**: the player district and 29 old-world sites transplanted through a 354-entry
  block remap; the FR-06 complex verified pixel-identical; five compound pads (radio tower 128x128,
  substation 160x160, water treatment 192x160, hospital 192x192, airfield 512x192) levelled,
  outlined in yellow concrete and ramped; a 384x384 starting area cleared and outlined; every
  transplant edge ramped (residual gaps of 3+ blocks: 19.6% of edge columns, all but 187 at buildings).
- **Boot gate**: 12 error lines, all benign (11 Immersive Vehicles pack model quirks, 1 Forge dist
  probe); 43 warnings. Anything else on a future boot is new.
- **Backup**: the whole server root as of 2026-09-02 (3.1 GB) is in the release assets.
- **2026-09-03**: the hosted server was ROLLED BACK to the pre-rebuild pack and world (`Escape From
  Minenkrafte`, old mods, Aikar flags off); the rebuild folders sit beside it as `*_wasteland_20260902`.
  All rebuild work now happens on a local test server (see `README-local.md` on the working machine).
  Order of work from here: (1) a mob-free **visual pass** over the v5 world; (2) decide the map plan and the
  base/hideout upgrade system (both in `docs/wasteland-server-blueprint.html`); (3) intake of the foreign
  1.12.2 worlds (`docs/notes/gscraft-foreign-worlds.md`); then the items below.
- **2026-09-03 late (this machine):** the 10 km box is pre-generated (tools/localpregen.py cycles the server
  every ~12k chunks; Lost Cities' caches OOM it otherwise) and the **v6 world is built** by `tools/buildv6.py`
  (substation pad restored, six pads, seven transplants with vertical shift, smooth, ramps) and staged on the
  local server as `wasteland-v6` with tower stage 0 placed and the lock scripts armed. `tools/reviewv6.py`
  audits the whole world; its report and the findings are in `docs/gscraft-map-review-v6.md`. Phase A (the
  owner's visual pass) is next, then roads and the camp buildings.
- **Still to do**: KubeJS state machine for the location loop (clock, target draw, countdown,
  waves, boss); FTB Quests book and home-claim marker; horror rates measured in play; an in-game
  flight through every site and pad; Superb Warfare small-arms toggle; old-world housekeeping on the
  server (`mods_old_20260902`, `config_old_20260902`, `defaultconfigs_old_20260902`, the two old
  world folders, the 557 MB zip) only after the flight.
- **Open question**: the custom cyberpunk city the owner remembers is not in any world copy that
  was on this server. The only custom cityscape found is the FR-06 complex. When the city's file
  turns up, the transplant pipeline below takes it.

## 2. Setting up at home

1. Python 3.12 with `numpy` and `pillow` (`pip install numpy pillow`). Nothing else.
2. Clone this repo. Create `~/.bisect/config.json`:
   ```json
   {"panel": "https://games.bisecthosting.com", "token": "<your ptlc_ client API key>", "server": "493d6256"}
   ```
   The key comes from the panel's Account > API Credentials page. Never commit it.
3. Download the release assets you need (see section 4) and unpack:
   - `GSCraft-Client.zip`: the Prism Launcher instance for players (import as-is).
   - `gscraft-server-mods-1.20.1.zip`: the pinned server jar set, into `tools/build/mods/`.
   - `wasteland-region-pristine-v2.zip`: the pre-edit, post-pregen region files, into
     `scratch/worlds/wasteland/region/`.
   - the `server-backup-2026-09-02-*.zip` files: the old server, every folder as a zip.
4. Test the panel link: `python tools/bisectpanel.py resources` (Git Bash: `export MSYS_NO_PATHCONV=1`
   first, or use PowerShell).

## 3. The tools, in the order the work uses them

| Step | Tool | Notes |
|---|---|---|
| Read a world | `scanregion.py`, `worldscan.py`, `topdown.py` | `topdown.py <region dir> out.png --scale 2` renders any region folder. |
| Find builds | `buildmap.py` | Produces the site list and the transplant plan. |
| Remap blocks | `planblocks.py`, `makeremap.py` | `KEEP` in `planblocks.py` is the namespace set of the current mod list. |
| Transplant | `transplant.py`, `runplan.py` | Dry-run first (`--dry-run`), then write; runs long, background it. |
| Clean up | `fixspawners.py <world>` | Cut-mod spawners, stray entities, dead loot tables. |
| Pre-generate | `pregen.py <plan.json>` | Drives Chunky through the panel console. |
| Terrain | `runpass.py`, `terrain.py`, `strongpoints.py` | Always start from the pristine region set; upload with the server stopped; delete `/wasteland/poi`. |
| Server | `bisectpanel.py`, `backup.py`, `mcping.py` | `pull` compresses server-side and downloads; `putdir` uploads a folder. |
| Map page | `makemap.py` | Regenerates `docs/wasteland-district-map.html` from `buildmap/`. |
| Radio tower | `tower.py build` | Writes the six repair-stage structure templates + functions into `build/datapacks/gscraft` and the stage render. |

Traps that cost time, all documented in `docs/notes/`: Git Bash path conversion, the panel's
Cloudflare user-agent check, the `files/contents` POST, archives that are ZIP regardless of name,
the apostrophe problem in shell heredocs, and the `clear_column(x, z, from_y)` argument order.

## 4. Release assets (GitHub Releases, tag `handoff-2026-09-02`)

Large binaries are not in git. Fifteen assets (the five old-world/map archives were removed on 2026-09-03; they live on the working machine and the office box), put up by `tools/release_upload.py`
(re-runnable; it skips what is already there). If an asset is missing from the release page, run it
again from a machine with the GitHub CLI signed in and the files in a local folder. The release carries the client pack, the server mod set, the
pristine world region set, the edited v5 region set, and the non-world server backup archives. Player
identity files from the server root (ops, whitelist, user caches) are deliberately not published.

## 5. The design

`docs/wasteland-server-blueprint.html` is the design and the phase-by-phase record;
`docs/gscraft-server-audit.html` is the audit of the server as found;
`docs/wasteland-district-map.html` is the map with every build named, the location pool and the pads;
`docs/notes/gscraft-foreign-worlds.md` is the intake plan for builds arriving from 1.12.2 saves, with the census
results and the six candidate rectangles; `docs/notes/gscraft-scale-and-travel.md` sizes the map against travel times
(5 km square border, roads, timers for the loop); `docs/notes/gscraft-foreign-builds-plan.md` is the step-by-step plan for
bringing the 1.12.2 builds (the Novo Expograd city and its districts, ships excluded) into the wasteland world.
`docs/gscraft-map-design.md` is THE design the world build and tests are made from (draft 5: 10 km border, three ranges, camp with six NPC buildings, strongpoints are player-built structures, Tarkov-style item ladder with bulky loot-only components, storage as a base function, trips table, build order with test gates);
`docs/gscraft-map-layout-v6.md` is the placement sheet behind the design (every rect, offset, dy and pad level; tower in the camp, locked);
`docs/gscraft-quests.md` is every quest and task (77, six NPC chapters, scaled by act and distance, tower gated on progress);
`docs/notes/gscraft-scale-and-travel.md` holds the speed and travel tables behind it.
The endgame loop in force: take a location, a clock starts to fortify it; each cycle the game draws
one held location and warns; lose or die and retake it; every location drops radio-tower loot; tower
done starts a countdown; waves come to the players' own base; the last wave brings the boss.

## 6. Deploying v6 to the hosted server (panel commands, run by hand)

The panel client tool refuses nothing, but the working-machine assistant is not allowed to run
destructive panel calls, so the deploy is a hand-run sequence from PowerShell in `tools\`
(`~\.bisect\config.json` holds the key). `<W>` is the finished world folder
(`G:\GSCraft\server\wasteland-v6` - the staged copy, which also has tower stage 0 placed), `<B>` the repo's `build\` folder.

1. `python bisectpanel.py power stop` - wait until `python bisectpanel.py resources` says offline.
2. Swap the rebuild folders back (the rollback left them beside the old ones):
   `python bisectpanel.py mv /mods /mods_old_20260902` ; `python bisectpanel.py mv /mods_wasteland_20260902 /mods`
   and the same two renames for `config` and `defaultconfigs`.
3. `python bisectpanel.py mkdir /kubejs/startup_scripts` then
   `python bisectpanel.py putdir <B>\kubejs\server_scripts /kubejs/server_scripts` and
   `python bisectpanel.py putdir <B>\kubejs\startup_scripts /kubejs/startup_scripts`.
4. The world (about 5.3 GB, resumable - `putdir` uploads every file in one folder):
   `python bisectpanel.py mkdir /wasteland-v6` then `putdir` for `<W>
egion -> /wasteland-v6/region`,
   `<W>\entities -> /wasteland-v6/entities`, `<W>\data -> /wasteland-v6/data`,
   `<W>\serverconfig -> /wasteland-v6/serverconfig` (take the local server's copy of serverconfig:
   `G:\GSCraft\server\wasteland-v6\serverconfig`), `put <W>\level.dat /wasteland-v6`, and the datapack:
   `mkdir` + `putdir` for each folder under `<B>\datapacks\gscraft` into `/wasteland-v6/datapacks/gscraft/...`
   (pack.mcmeta at the top, then data/gscraft/functions, data/gscraft/structures, and the loot-table and
   recipe folders).
5. `python bisectpanel.py put <B>\phase03\server.properties.v6 /` then rename it on the server:
   `python bisectpanel.py mv /server.properties /server.properties.old` ;
   `python bisectpanel.py mv /server.properties.v6 /server.properties`.
6. `python bisectpanel.py setvar AIKARS_ENABLED 1` and `setvar CUSTOM_ARGS "<the Aikar -XX set from
   docs/notes/gscraft-phase-log.md phase 02>"`.
7. `python bisectpanel.py power start`; after two minutes `python bisectpanel.py cat /logs/latest.log`
   should show Done with the benign error set (11 Immersive Vehicles model quirks + 1 dist probe) and the
   two `[gscraft]` lines from the KubeJS scripts; `python mcping.py 199.115.76.82 9150` answers with
   MOTD "GSCraft Wasteland - test build v6". Tower stage 0 is already in the region files.
8. Afterwards: the old world folders (`Escape From Minenkrafte`, `Escape From Minecraft`, `wasteland`
   if present, `world`, `region`, the 557 MB zip) can go once the flight has happened.
