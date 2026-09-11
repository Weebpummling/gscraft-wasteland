# Handoff: picking the work up in another session

State as of 2026-09-04 (v6 live on the hosted server; **v7 built, reviewed and released**, deploy = section 6). Everything needed is in this repository plus the two GitHub releases;
the working machine's paths are given so a session on it can continue directly, and section 2 says
how to rebuild the same state elsewhere.


> **2026-09-09 — KROT, and mob griefing is off.** The hempcrete compound is now **KROT** (owner). The name
> is renamed everywhere in `docs/`, `buildmap/` and `tools/` (119 places); the three v6/v7 HTML snapshots keep
> the old name because they describe the superseded district at x 1568..1887, not this site. The IE block ids
> `immersiveengineering:hempcrete*` are the building material and are untouched.
>
> **KROT's extent is now wrong and nothing can safely use it.** `sectors_v8.json` still carries the old
> 320 x 320 box (x -3392..-3073, z -1344..-1025) and the owner says the site is massively expanded by hand.
> Until someone measures the new footprint, that box under-states it: any In Control area, loot route, waypoint
> or quest anchored on it points at a fraction of the place. **Needs new bounds before it is used for anything.**
>
> **Mob block destruction is off** until the designers finish building (`tools/griefing_off.py`, `--on` reverses
> it). Four levers, because the vanilla gamerule is not the only one: `mobGriefing=false` in the world's
> level.dat, Improved Mobs `Flag Blacklist = [BLOCKBREAK, LADDER]`, and the fog man's `break_blocks=false` in
> `man_config.toml`. `gscraft_mech_griefing.js` is a separate per-entity denial and is unaffected.

> **2026-09-07 — the camp moved into Skadowsky. READ THIS FIRST.** The camp, its NPCs, the world spawn and the
> radio tower are no longer on the plateau. They are in Skadowsky, east of the south-west bridge, and the tower is
> the sector's own standing mast. Skadowsky is the starting zone and becomes the camp by being cleared; medical
> moves to the sector's hospital at x -865..-698, z -1312..-1242. Nothing had been built, so this cost documents
> and no world work. The doc is `docs/gscraft-skadowsky-camp.md`; every superseded section now carries a banner
> pointing at it. **Do not trust any plateau coordinate you find elsewhere.**
>
> **2026-09-07 — the routing rule.** Questing and gameplay route only to the Pripyat base map, the Skadowsky
> sector and KROT. Novo Industrial, the Financial Plaza, Bio Gen, the desert city hub, the
> mega-base FR-06 and the waterworks are **deferred to a later quest line** and no quest in the current design may
> point at them.
>
> **2026-09-06 — MCSP and the Vintage Vehicle Pack were dropped** for the Frontline Combat Pack and
> DragonRise: Reforge. The three military-tier ids re-point to `fcp:hmmwv_armored_m2`,
> `dragonrise_reforge:uh60` and `dragonrise_reforge:m3a3`. The jar swap itself is **not applied to
> `server/mods` or the pack yet** — it needs Superb Warfare 0.8.9-final and Kotlin for Forge, and it forces every
> player to update. Test results and the exact version trap: `docs/gscraft-sbw-addon-test-2026-09-06.md`.
>
> **2026-09-05 — design integration.** The design documents were rebased on the v8 geography and the Create fork was
> adopted as a chapter; the player interface is `docs/gscraft-player-interface.md` (mockups: the "GSCraft Player
> Interface" artifact). The eighteen decisions the rebase forced are `docs/gscraft-design-gaps.md` §E, each with its
> default — read that table before any Phase C work.
>
> **Designer tools (owner, 2026-09-05):** WorldEdit stays and the players get it — `server.properties`
> `op-permission-level=2` (done locally; **hand-run on the hosted panel**: the same key, then `/op <name>` for each
> designer; the owner stays level 4 in `ops.json`); WorldEdit CUI `WorldEditCUI-1.20+01.jar` is client-only in the pack
> (`CLIENT_EXTRA_JARS`, packwiz 2026.09.05). The researched kit (Lighty, IBE Editor, Jade, Freecam, FTB Ultimine by hand)
> is `docs/notes/gscraft-designer-tools.md`. Owner preference, not a design dependency: nothing in the
> design waits on it, and the default is to add none (2026-09-07).
>
> **Objectives on the v8 map (proposal, 2026-09-05):** `docs/gscraft-objectives-v8.md` — the map read as three lands
> (home bank, the river line, the far bank) plus the district; acts and strongpoints re-placed from real road distances
> (`docs/renders/v8_geography.png`); its §5 lists the crossings and roads the objectives need (for the map session) and
> §7 the ten changes, all ruled on and applied 2026-09-05 (the reactor module moves to the plant complex; the farm role is
> the collective farm in the fields south of the town). **Realigned 2026-09-07** onto the Skadowsky camp, so §0 to §6 now
> read from the camp square at (−940, −979). **For the map session:** the camp's two gates (the south-west bridge and
> the rail embankment's level crossing), the east-bank road south to the plant's outer works, the plant's west gate, and
> the collective farm's fields to plant (wheat gone wild, hay, a barn at the farmstead (−2112, −896)), which is now the
> Line's west end rather than a side trip. The Line's ford is gone: the corridor crosses on the bridge.
>
> **Everyone and everything that moves (v8), 2026-09-05:** `docs/gscraft-entities-v8.md` — the survivors and keepers
> as seated villagers, guards, the Recruits ranks and where each is hired, the site guard, placed animals, six factions
> (the Machines added), ranks, where each faction lives (In Control areas), waves by site, elites and bosses (the
> Overseer added at the plant complex), drops, the twelve config/script changes and **test T1** (does In Control's
> `onjoin` deny rule swallow summons and waves with `doMobSpawning` off — **re-run 2026-09-09: it **DOES**. A summoned zombie vanishes in under two seconds; with spawn.json emptied the same summon survives. Cause: spawn.json rule 3 denies every hostile in the overworld unconditionally, ahead of every allow rule, which also makes rules 4-15 unreachable. See docs/gscraft-design-review-2026-09-08.md section 4b. The 2026-09-05 result was wrong**;
> `docs/notes/gscraft-incontrol-onjoin-test.md`. Watch instead: the local server's `difficulty=peaceful` removes every
> hostile; the In Control rules with `minx/maxx` keep loading with those **keywords** rejected, so they run with no bounds at all (tested 2026-09-08, `docs/gscraft-design-review-2026-09-08.md` §3; fixed locally onto named areas, and the hub mech spawner disabled). RCON is now enabled on the local server
> (`rcon.password` in `server.properties`, local only; client `scratch/incontrol_test/rcon.py`).
> Inventory behind it: `docs/notes/gscraft-entity-inventory.md`.
>
> **The underused mods put to work, 2026-09-05:** `docs/gscraft-mod-utilization-plan.md` — 49 hooks by land (the camp
> 27, the home bank 6, the river line 3, the far bank 3, the district 7, the two edges 3), the audit's five wins as
> Phase C tasks with file paths (§7), Bandits / Lukis / Waterframes as background jars (§8), every new task, order,
> loot row and config line it adds (§9), and the rulings (§10).
>
> **Gap sweep 2026-09-06 (`docs/gscraft-design-gaps.md` §H):** eight gaps found and closed the same day — the fifteen
> keeper quests, the three rail quests, Teddy's H8, the eighteen counter pages, what a keeper's counter does when a
> site falls back, the boat's act (J5 hands out the boat, W-V1 the speedboat, W12 crosses to FR-06), NATO's
> home. **The two-camp-rectangle question is closed (2026-09-07):** the map plan used to carry two plateau rectangles
> and an argument about which was right. Neither is live. Nothing was ever built on either, and the camp is now in
> Skadowsky at x −978…−770 × z −1060…−845, matching `buildmap/plan_v8/sectors_v8.json`. No mod is missing; the only
> jars still queued are the designer tools (`notes/gscraft-designer-tools.md`, owner's pick).
>
> **The local Prism instance is packwiz-managed from 2026-09-06.** It never was: it had no pre-launch command and no
> `packwiz.json`, so every jar in it was hand-copied and it sat 17 jars behind (including both Sophisticated mods) on
> Forge 47.4.10. Now: the bootstrap jar is in `.minecraft`, `instance.cfg` carries
> `OverrideCommands=true` + the packwiz pre-launch command against the raw GitHub pack, the Forge component is 47.4.23,
> and one manual run brought it to 106 jars (103 server + the three client-only). The superseded jars are in
> `scratch/instance_backup_2026-09-06/retired_mods` with the old `instance.cfg` and `mmc-pack.json`.
> **Consequences:** never hand-copy a jar into that instance again — add it to the pack and rebuild; and remember
> `packwiz_build.py` reads its client-only jars and configs *from* this instance, so the pack now feeds itself (fine
> while the three client-only jars stay in the pack). Prism's Forge component is not managed by packwiz: a future Forge
> bump is still a hand edit in Edit, Version, Forge.
>
> **Releases cleaned 2026-09-06.** Three live: **`client-installer-<date>`** — one 0.26 MB
> `GSCraft-Client-Install.zip` (START HERE.txt, INSTALL.md, Setup.cmd, VanillaLauncher.cmd, Instance.zip, mrpack),
> marked Latest; **`pack-files`** — a **stable tag** carrying the 26 non-Modrinth jars, the 2 gun packs, the instance
> zip and the bootstrap, updated in place so the URLs baked into the pack never move; **`build-v7-2026-09-04`** — the
> last published world. Deleted: both old client installers (the 09-05 one had all 150 MB of jars attached to it),
> `pack-files-2026-09-04`, `build-v6-2026-09-03`, and v7's superseded `GSCraft-Client.zip`.
>
> **For the map session (from the design review, 2026-09-05, rewritten 2026-09-07; `docs/gscraft-design-gaps.md` §F9):**
> the plateau camp ring that used to straddle its own rectangle is gone with the plateau, and so is the world-spawn-y
> question — the spawn is the paved junction at (−940, −979), ground y 65. What is left for the walk: pace the eight
> Skadowsky lock rectangles (`tools/pads_camp.json`, first cut, measured but not walked) and adjust them; add the
> east-bank road south to the step-8 connector list; pick the town's landmark buildings from the measured candidates in
> `docs/gscraft-skadowsky-camp.md` §12; put an electric motor in the depot's chest; replace the v6 junction road-sign
> text. The Line's ford is retired with the old corridor.

## 1. Where things stand

**Hosted server (2026-09-06 02:25): running the v8 world with the road rework** (`/wasteland-v8`), the 2026-09-05 mod set on Forge 47.4.10,
`difficulty=peaceful` + `spawn-monsters=false` (owner: enemies off while gameplay is worked on locally), KubeJS scripts moved
aside (`/kubejs_off_20260905`), MOTD "test build v8 (map review, enemies off)". Deployed with `tools/deploy_v8.py`; old
folders kept as `*_old_20260905`. Client pack: release `client-installer-2026-09-05` (Forge 47.4.23 client, 17 mod updates).
The local server (`G:/GSCraft/server`) keeps the scripts and runs 47.4.23 for the gameplay work.

> **Road rework, 2026-09-06** (`docs/gscraft-road-review-v8.md`; tools `roadpatch.py`, `roadrelay.py`, `roadmask.py`,
> `worldborder.py`, `worldmap.py`; review scripts in `tools/roadreview/`). The cell's roads were in 21 disconnected
> pieces and are now one network with all 34 builds on it: 19 breaks closed, 32 wiped spans re-laid, the six north-east
> farm spokes and the four eastern ones replaced by a farm belt and an east trunk, and a ring closed with a new 48 m
> viaduct at (466..514, -2450). `roads.py` gained three classes (trunk 9 / road 7 / track 5), a `--meander` term and
> flared junctions, and now writes a protect mask per road which `river.py`, `shoreline.py`, `lakefill.py` and
> `smoothcliffs.py` honour with `--protect-roads`.
>
> **The world border was wrong.** level.dat still carried Pripyat's border (west edge x -3099.5, north edge z -3749.5) -
> the wall the owner hit near (-3100, 583). It left the Financial Plaza and farmsteads 14 and 26 outside the playable
> area and cut five more builds. `tools/worldborder.py` set it to centre (-1350.5, -1600.5) size 5200, which contains
> the cell with a 50-block margin.
>
> Current maps are in `docs/maps/` (`gscraft-wasteland-v8.png` is the labelled world map from `tools/worldmap.py`).
> 30 region files and level.dat were uploaded with the server stopped; it restarted clean, Done in 1.6 s, and
> `worldborder get` reports 5200 blocks.

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
ruin pieces in the camp, `gscraft:camp_ruins`, loot tables under `ruins/`; **retired 2026-09-07** — the camp moved into a standing town and needs no scattered wrecks, and the generator now refuses to run; the file survives only because `camp_torches.py` and `theline.py` import its helpers). **EMI 1.1.24 added** to the
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
furnishing). Spawns stay off until the owner's Phase A pass on v7 is done — that also keeps the boss spawners quiet. Owner also ruled: Immersive Weathering, the server tools and the TaCZ fire-control extension all STAY
(vvp and MCSP were dropped on 2026-09-06 for the Frontline Combat Pack and DragonRise: Reforge —
`gscraft-sbw-addon-test-2026-09-06.md`) (uses in `gscraft-mod-capabilities.md`
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
Scavengers, NATO, the Horrors, the Camp), ranks with per-act equipment set through In Control!'s rule
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
(`v8_cell_pass3_inspect.png`). Pass 3b: `river.py` carved the region's main river (lake -> along Skadowsky's west side -> out of the cell at z 700), `bridge.py` carried the Skadowsky highway viaduct across it, `statusfix.py` made all 1.12-upgraded chunks `full` (the tools had been skipping 7 k of them), `edgeaudit.py` lists every linear feature running off a footprint edge for step 8, `unroad.py` strips a mis-laid road. Pass 4: every sector integrated (`integrate_all.sh`), settlement removed, all 27 connectors built (Skadowsky style), two viaducts where the river cuts the Pripyat roads, stub connectors (`edgeroads.py`), water ends (`edgewater.py`), `regrade.py`; pass 5 `smoothcliffs.py` (cell-wide cliff and shore smoothing, terrain only); world staged to `server/wasteland-v8`; review `docs/gscraft-map-review-v8-pass4.md`. Plan `docs/gscraft-map-plan-v8.md` §5.
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

**v8 (2026-09-05): `python tools/deploy_v8.py plan | upload | swap | status`** wraps the whole recipe below for the v8 world
(`server/wasteland-v8`), the 2026-09-05 mod set and configs, `build/phase03/server.properties.v8` (peaceful, no monster
spawns - owner: enemies off while gameplay is worked on locally) and moves `/kubejs` aside (scripting off until final).
Forge stays 47.4.10 on the host for now. Run `upload` while the old server runs, then `swap`, then `status` after two minutes.
Note (2026-09-05): the v8 world's `level.dat` inherited the Pripyat source's **superflat** generator; it was replaced by the
v7 level.dat's settings (noise generator, seed 2404991234066556536, Forge/mod data) with LevelName wasteland-v8 and the v8
spawn (-2555, 72, -2539). The superflat copies are kept as `level.dat.superflat.bak` beside both worlds.

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

## The War mod goes live (2026-09-10, owner: "push the current version on live")

Backup verified and no players online by the owner. The server side is `tools/deploy_war.py upload` then `swap`
(hand-run, HANDOFF section 6 rules): `/mods_20260910` (108 jars: In Control, Improved Mobs and TenshiLib out,
gscraft-0.1.0.jar in), `/config_20260910` (the local config without `*.bak*`, `pauseEventServer = true`), and
`build/phase03/server.properties.war` (difficulty hard - the mod's bodies are Monsters and peaceful removes them;
spawn-monsters stays false, the director places). No world files. The player side is pack 2026.09.10.1
(`build/packwiz`, commit 23f0623, pushed after the swap so no client updates ahead of the server), the pack-files
release (gscraft-0.1.0.jar, GSCraft-Instance.zip) and `client-installer-2026-09-10` (Latest). Live's world datapack
keeps `spawns_on`/`spawns_off`; they are inert without In Control. Rollback: the reverse renames in the script's
docstring and `/server.properties.v8-live`.

What live now runs that it did not: enemies (the hold in the mod refuses everything the director does not place),
the strongpoint loop with the clocks on online time, groups of 2-4, the locks on the mast field. What live does not
have: RCON (local only), creative (local only), `pauseEventServer = false` (local only).

## Local test server differs from live (2026-09-09)

- `server/config/hordes-common.toml`: `pauseEventServer = false` locally so headless tests tick (backup
  `hordes-common.toml.bak-pause-true`). Live keeps `true`. Never carry this file to live.
- `server/config/improvedmobs/common.toml`: `gscraft` namespace excluded (backup `common.toml.bak-war-mod`).
- `gscraft-0.1.0.jar` (GSCraft War, `mod/`) is on the local server, in the pack and (from 2026-09-10) on live.
  Prism instance `GSCraft-WarTest` (local only, no packwiz sync, servers.dat = localhost:9150) carries the jar under test.

## Old enemy stack retired locally (2026-09-09)

- `server/config/incontrol/spawn.json` (2026-09-10): a second pass rule after `mod: gscraft`,
  `scoreboardtags_any: gs_placed -> allow`, so Dead the mod places (the Converted, later the director) get through
  the hold. Backup `spawn.json.bak-phase2`.


The enemy system now lives in `mod/` (GSCraft War). On the local test server the In Control faction rules, the
KubeJS area spawner / Scavenger neutrality / terrorist drop scripts, the Improved Mobs illager exemptions and the
Hordes phase 2 changes are off; details in `docs/gscraft-war-mod-design.md` ("Retired locally"). Backups:
`server/retired-2026-09-09/`. In Control holds every hostile except `mod: gscraft`.

**Pack rebuild trap:** `tools/packwiz_build.py` copies `server/config` into `build/packwiz` wholesale. Before any
pack rebuild, set `pauseEventServer = true` back in `server/config/hordes-common.toml`, or the local-only value
ships to every player.

## Improved Mobs removed (owner, 2026-09-10)

"There is no need to keep a mod when it serves no purpose." The GSCraft War mod owns enemy gear, targeting and
placement; Improved Mobs' remaining effects were liabilities: rolled gear on the Dead (measured: 20 of 30 fresh zombies
holding something, lava buckets and ender pearls among it), 30 % container stealing, 5 % neutral aggro. Distance
scaling was its one useful effect and is not needed for the design pass. Removed from the local server and the test
instance at the next restart; its jar and config go to `server/retired-mods-2026-09-10/`. `packwiz_build.py` reads
`server/mods`, so the next pack build drops it for players - that is a pack change and waits for the deploy gate.

RUAF's Skadowsky post moved (owner, 2026-09-10) from the riverbank bridgehead to the brick block between the camp and
the hospital: `sk_out_w` x -784..-720, z -1148..-1100 (centre -752, -1124). The jar carries it now; the local-only `gscraft_war_dev` datapack is retired to
`server/retired-mods-2026-09-10/`.

## Director by ground, area creatures, varied kit (2026-09-10, local only)

- **Ground kinds** (`world/Env.java`): read from what is overhead. Rock or earth = underground; a built ceiling with 3+
  blocks of rock or earth over it = underground too (bunkers, tunnels); other solid = indoor; nothing for 24 = open.
  Open: cap x0.75, placed 28-52 blocks out. Indoor and underground: cap x1.5, placed 6-24 out, on the same ground,
  and only where a zombie could walk to the player (shut doors used to fill the cap) - except one placement in
  five, which may stand behind shut doors (tag `gs_sealed`), held to a quarter of the cap (owner, 2026-09-10). Caps count per ground kind.
- **Zone pools**: `spawns` (open), `indoor_spawns`, `underground_spawns`, `lair`, horrors with `envs`. Generated by
  `tools/war_zones.py`; zone order matters (first box wins) - `farm` now precedes `woods`, which had hidden it.
- **Area creatures**: Bloater (plant), Matron (hospital lair, persistent, one), Riders (farm, farbank, open ground,
  night), cave spiders under the Woods, the town and open ground, Runners among the Dead.
- **Kit**: every rank slot is a weighted choice. Scavengers roll each slot; NATO and RUAF wear their side's uniform at every rank
  and vary the rifle. RUAF uses the CIBR gun pack (`cib:ak105`, `ak103`, `asval`, `pkp`, `svd`; `cib:ak24` is broken (owner, 2026-09-10) - never issue it), which ships
  in the player pack's `tacz/` folder already.
- **Commands** added: `/gscraft env <x y z>`, `director passat <x y z> <n>`, `director survey <x y z> <samples>`
  (first version against layered placement), `director room <x z> <radius>` (nearest ground-floor room).
  `pass`/`passat`/`survey` were unreachable before this fix (Brigadier builds a child when it is attached).
- **Tests**: `tools/war_phase4b.py`, then `war_phase4.py`, `war_phase3.py`, `war_phase2.py`. Needs a ticking world
  with nobody online (the 128-block despawn removes far-away test mobs).
- **Fold-in step 1 (2026-09-10, owner: "fold in everything", "let In Control go"):** the hold, the locks, the mech
  griefing rule, the Dead's drops and the projectile sweep are the mod's (`world/Hold`, `Locks`, `LockEvents`,
  `Drops`, `ProjectileSweep`; data `gscraft_locks/`, `gscraft_drops/`). In Control and the four KubeJS files it
  replaces are in `server/retired-mods-2026-09-10/` (not in the pack build yet - deploy gate). The hold is In
  Control's three live rules verbatim: a bare `/summon` of a hostile is refused unless tagged `gs_placed`; the
  Hordes player zombie is refused too, as before. `/gscraft hold off` lifts it for a test. The lock is the mast
  field only; add the NPC pads to `gscraft_locks/camp.json` when `camp.py` builds them. The v6 tower rect the old
  script locked (x 64..191 z -144..-17) protected nothing on v8. Test: `tools/war_phase5.py` first.
- **Fold-in step 2 (2026-09-10): the strongpoint loop** is in the mod (`world/Loop`, sites as data in
  `gscraft_sites/`). `/gscraft sites` shows every site's rung and clock; `/gscraft site <id> set scouted|looted|held`
  climbs the ladder (held = the marker, starts the assault); `clock <seconds>` jumps the current phase's end;
  `/gscraft clock free` lets the clocks run with nobody online (tests only - restore `online`). Quest stages are
  player tags set by the mod and re-applied on join (`/gscraft stages`, `stage add|remove`). The wave tables live in
  the site files; the camp's approaches are a first cut `[needs measurement]`. Test: `tools/war_phase6.py` first,
  then 5, 4b, 4, 3, 2. TRAP: a site left held or contested by a broken test run suppresses its zone's ambient
  placement and refuses other markers - `/gscraft site <id> set unknown` resets it.
- **Armies hostile to Scavengers (owner, 2026-09-10):** `gscraft_factions/nato.json` and `ruaf.json` list `scavengers`; a
  Scavenger only fights a soldier that struck it.
- **Sharper fighters, step A (2026-09-10, feasibility doc §9):** doors, rubble, sprint, sidestep, crouch/prone stances,
  suppression from TACZ's hit events, callouts, grenades (reflection on Superb Warfare), open range 36-72 with
  persistent placements and the director's own despawn past 160. `wasteland-v8/serverconfig/superbwarfare-server.toml` (the world's - a Forge server config; `config/` is only the
  template) has `explosion_destroy = false` locally (backup `.bak-explosion`) - **this must go to live's
  `/wasteland-v8/serverconfig/` with the next deploy** or NPC grenades break blocks (two did, locally, before the
  right file was found). Test: `tools/war_phase7.py` first, then 6, 5, 4b, 4, 3, 2. TRAP: a `Goal` must not read a
  body's fields in its constructor - `Mob` registers goals before the subclass's fields exist (it crashed the server).
- Eyes in the Darkness natural spawn is off locally (`eyesinthedarkness-server.toml`, backup `.bak-director`); the
  director places the Eyes instead.
