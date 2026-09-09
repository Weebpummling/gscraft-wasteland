# GSCraft Wasteland — design review (2026-09-08)

The map is finished. The layer that makes it a game is, with two exceptions, not on the server.

Twenty-nine documents and roughly 7,700 lines specify 105 quests, 55 loot rows, six factions, ranks,
waves, a finale and a player interface. Read against what the live server actually holds, the gap is
not a matter of polish: **no quest exists, no custom loot table is loaded, five of six KubeJS scripts
are absent, and the wave mechanism cannot fire at all.** None of that is a surprise given the order the
work was done in — the world had to exist first — but it means the next phase is content, not terrain,
and that the design is now well ahead of the thing it describes.

The good news is that the four defects below are small, confirmed against the live server, and testable
locally in an evening.

## 1. What is actually live

| Layer | Designed | On the server | Evidence |
|---|---|---|---|
| Terrain and builds | v8 | **live**, deployed 02:37 today | 99.7 % of the desert city converted |
| Mods | 119 | **live**, pack `2026.09.08.1` | boot log, "Loading 119 mods" |
| Map waypoints | 46 | **shipped** | `GSCraft-Map-Waypoints.zip` |
| KubeJS server scripts | 4 | **1** (`gscraft_recipes.js`) | `/kubejs/server_scripts` |
| KubeJS startup scripts | 2 | **0** | `/kubejs/startup_scripts` |
| Custom loot and recipes | 13 files | **0** | `/wasteland-v8/datapacks` |
| FTB Quests | 105 quests | **0 chapters** | `/wasteland-v8/ftbquests` holds 5 per-player progress files and nothing else |
| Waves | per-site and finale | **cannot fire** | see D2 |
| Enemy dressing | six factions, ranks | **not started** | see D4 |

`gscraft_fixes.js`, `gscraft_tower_lock.js`, `gscraft_projectiles.js`, `gscraft_tower_lock_native.js`
and `gscraft_mech_griefing.js` all exist in `server/kubejs` on this machine and none of them has ever
been uploaded.

## 2. Four defects, all confirmed on live

**D1 — the `gscraft` datapack never made the v7 to v8 move.** `wasteland-v7/datapacks` holds three
packs; `wasteland-v8` holds two. The missing one is 13 files: six `keerdm_zombie_essentials` chest
overrides, four ruins loot tables, two site tables, and the `factory_blocks` mason table recipe. It is
absent from the v8 world both locally and on the server, so this was lost in the world rebuild rather
than in a deploy.

Those six chest overrides are the ones that rewrite tables referencing `pointblank:*`, and PointBlank is
not in the pack. That is exactly the error in tonight's boot log — "Couldn't parse element
loot_tables:keerdm_zombie_essentials:chests/apartment_bathroom_vics", on an unknown item
`pointblank:glock17`. I called that pre-existing and unrelated when I first saw it. It is neither: it is
a regression, and the fix has been sitting in the v7 world folder since the rebuild. Every affected
chest currently generates empty.

**Fixed locally 2026-09-09, and two corrections to the paragraph above.**

First, I said only eleven of the thirteen were wanted, holding back the `financial` and `novo` site
tables because the routing rule defers those sites. That was wrong. Both sites are built, deployed and
walkable — a player can stand in either today — and a loot table is inert unless a chest references it.
Excluding them bought nothing and left something to remember later.

Second, and more important: **the datapack was never lost from version control.** `build/datapacks/gscraft`
is tracked in this repo and is where `camp_ruins.py` and `theline.py` generate. Only the *world folder*
copy went missing in the v8 rebuild. Restoring from `wasteland-v7` — the obvious move, and the one this
review originally proposed — would have installed a **stale** pack: the repo source carries 55 files and
v7 only 47, the difference being the Line's `theline.mcfunction`, its loot table and six structures, all
generated after the v7 world was cut.

So the fix is `build/datapacks/gscraft` into `wasteland-v8/datapacks/`, not v7 into v8. Done locally and
verified: `datapack list enabled` reports 127 packs including `[file/gscraft (world)]` — a new world pack
auto-enables on load, no `level.dat` edit needed — and the PointBlank parse error is gone. The three
`Couldn't parse data file` lines that remain are `dragonrise_reforge` and `fcp` reading vehicle JSON out
of their own jars, unrelated and not new.

**This exposes a shipping gap.** `deployguard.py` pushes only region, entity and poi files, so it cannot
put this datapack on the host. The same limitation blocks the FTB Quests work in Phase 3. Whatever
carries quest data to the server has to carry world datapacks too, and neither exists yet.

**D2 — waves are unreachable.** `entities-v8` section 5 and the finale both drive waves through
`/hordes spawnWave`. `HordeCommands.registerCommands` only registers that command when
`enableHordeEvent` is true, and live is `enableHordeEvent = false`, `hordesCommandOnly = false`. The
command does not exist on the server. Every wave, every site defence and the finale are blocked behind
a two-line config change.

**D3 — the horde config is one mod update from being deleted.** `config/hordes/hordes-info.json` has
`"data_version": 12`. The mod deletes `config/hordes/` wholesale when that number is behind, and it has
already happened once here: `hordes-backup/` sits at version 6. Any wave table written before this is
set to `-1` is written on sand.

**D4 — nothing an enemy carries is prevented from dropping.** "Nothing an enemy carries ever drops" is
load-bearing across the enemy design: it is why military kit is worth taking sites for. No In Control
rule sets `ArmorDropChances` or `HandDropChances` anywhere, on live or locally. The moment factions are
dressed, every rank becomes a gun piñata and the scarcity the economy rests on is gone.

## 3. The contradiction, settled by test — and it was worse than either doc said

`HANDOFF.md` recorded that the In Control rules carrying `minx/maxx/minz/maxz` are **rejected at load**.
The 2026-09-08 enemy pass (section 2.6, E7d) recorded that they **load as unconditional catch-alls**.

Booted locally 2026-09-08. In Control says:

```
ERROR [incontrol]: Invalid keywords for spawn.json: minx maxz maxx minz     (twice)
ERROR [incontrol]: Invalid condition 'minx' for spawner rule!
```

**The enemy pass is right.** The *keywords* are rejected, not the rule: each rule loads and keeps every
other condition, so the bounds simply do not exist. `HANDOFF.md` was wrong and has been corrected.

Three things the review missed until the test ran:

1. **A third file is affected.** `spawner.json` carries the same defect and neither document mentions
   it. It matters far more than the other two, because a spawner does not gate spawns — it *causes*
   them. Rule 4 spawned `pomkotsmechs:pms01` and `pms03` at `persecond: 0.02` with `attempts: 10`,
   40 to 110 blocks from any player, anywhere in the overworld. It is tagged `ic_hub_mechs`, so it was
   written for the hub alone. It is on the live server in that state today.
2. **The bounds were stale as well as ignored.** All three rules carry `x 5600..6431, z 1184..1823`.
   The v8 map spans `x -3824..799, z -3808..700`. Even with working keys they would have pointed at
   empty space well off the map — these are v6 coordinates that survived two rebuilds.
3. **In Control spawner rules cannot be geofenced at all.** `SpawnerConditions` accepts `biome`,
   `block`, `dimension`, `gamestage`, `inbuilding`, `incity`, `instreet`, `inliquid`, `mindist`,
   `maxdist`, `minheight`, `maxheight`, `minlight`, `maxlight`, `mintime`, `maxtime`, `norestrictions`,
   `phase`, `seesky`, `structure`, `sturdy` and `validspawn`. There is no coordinate key and no `area`
   key — `area` was tried and rejected. `entities-v8` section 154 says "the mechs never leave their
   areas (In Control denies `pomkotsmechs:*` outside `hub`, `plant` and the district's `drone` sphere)".
   For the two `spawn.json` gating rules that is now true. For the spawner it is not achievable as
   written, and the design needs to know that.

Only `difficulty=peaceful` has been hiding this. The moment hostiles are switched on, mechs appear
across the whole map.

### What was changed locally to fix it

- `config/incontrol/areas.json` — was `[]`. Now defines `plant` (x -1150..1200, z -400..700, from
  `poi-coordinates` line 55) and `hub` (x -3568..-2385, z -1008..700, from `sectors_v8.json`) as BOX
  areas. In Control's area schema is `name`, `dimension`, `type` (BOX / SPHERE / CYLINDER), `center`
  and `dimx/dimy/dimz` — centre plus extent, which is why the old min/max keys were never valid.
- `config/incontrol/spawn.json` — the two mech rules re-written onto `"area": "plant"` and
  `"area": "hub"`, each keeping its count cap, plus a third rule denying `pomkotsmechs` everywhere
  else. That is the containment section 154 describes, and it now exists.
- `config/incontrol/spawner.json` — the hub mech spawner removed, since no correct geofence is
  available for it. Kept at `config/incontrol/spawner.disabled-hub-mechs.json` for when the hub ships.
  The hub is deferred and no quest points at it, so nothing is lost meanwhile.

The server now boots with **zero** In Control errors, from three before.

These files live in `G:/GSCraft/server/config`, which is what `packwiz_build.py` builds the pack's
config from — so the fix reaches the pack and the host on the next build, and nothing is stranded on
one machine. It has **not** been shipped: local only, as instructed.

## 4. What to implement and test, local first

Ordered so that each phase is provable before the next depends on it.

### Phase 0 — settle the two facts (one evening)

1. Take the local server `difficulty` off `peaceful`. It is `peaceful` today, which removes every
   hostile and makes all spawn testing meaningless.
2. Resolve section 3 with In Control's own debug output: are rules 0 and 1 rejected, or unbounded?
3. Confirm `enableHordeEvent = true` plus `hordesCommandOnly = true` registers `spawnWave` and still
   suppresses natural hordes. RCON is already enabled locally.

Phase 0 changes one config line and answers two questions that decide what Phases 2 and 4 look like.

### Phase 1 — restore what was lost (small, and it fixes a live bug)

4. Bring the eleven wanted files of the `gscraft` datapack forward from `wasteland-v7` into
   `wasteland-v8`, leave the two deferred site tables out, and confirm the loot error is gone from a
   local boot.
5. Upload the five KubeJS scripts that have never been deployed — after reading each against the
   current design, since three of them predate the Skadowsky move.

Phase 1 is the highest value per hour on this list: it is mostly a file copy, it removes a real error,
and it restores content that was already designed, written and reviewed.

### Phase 2 — make waves possible

6. E1 and E2 together: turn the commands on, then immediately set `data_version` to `-1`.
7. Write one site's table in the section 4 format and fire it locally. One is enough to prove the
   format, the NBT dressing and the drop-chance suppression in D4 all work together, before nine more
   are written against an unproven shape.

### Phase 3 — the first quest line

8. Nothing exists in FTB Quests yet, so the first chapter is also the test of the whole toolchain:
   authoring, `ftbquests` in the world folder, and whether quest data survives a world deploy — which
   matters, because `deployguard` currently pushes only region, entity and poi files.

That last point is a real gap in the deploy tooling, and it is better known before quest work starts
than after.

### Phase 4 — enemies

9. E7a and E7b first (drop chances, and exempting dressed mobs from Improved Mobs), because every later
   rank depends on both.
10. Then sections 3.1 to 3.5 of the enemy pass, one faction at a time.

## 4a. Phase 2 result (2026-09-09): the wave mechanism works, and it can be pinned to a site

E2 applied first and deliberately. The file argues its own case — `hordes-info.json` carries the comment
"for modpack authors: setting the value to -1 will prevent the config folder regenerating when updating
the mod". The risk was live, not theoretical: the installed jar is `1.6.3g` and the config said `1.6.3f`,
so the folder was already a version behind. `data_version` is now `-1`.

E1 applied and confirmed. With `enableHordeEvent = true` and `hordesCommandOnly = true`, `help hordes`
now answers:

```
/hordes spawnWave (<count>|<player>)      /hordes start (<length>|<player>)
/hordes stop [<player>]                   /hordes reset [<player>]
/hordes debug                             /hordes listEntities
/hordes spawnZombie <username> <pos> [<type>]
```

D2 is closed: the command the entire wave design drives now exists.

**Per-site waves are achievable, and this is the good news of the pass.** Table selection runs through
`horde_data/scripts/default.json`, a rule list of `hordes:set_spawntable` functions gated by conditions —
and the condition set includes `hordes:player_pos`. Unlike In Control's spawner rules (section 3), a
horde table *can* be geofenced. `gscraft_skad.json` was written for Skadowsky's box
(x -1088..-625, z -1488..-737) and pinned to it; the server loads both with zero errors:

```
loaded horde table hordes:gscraft_skad
loaded horde script hordes:default
```

### The script schema, because it is undocumented and cost three attempts

Nothing in the jar or the shipped files uses `hordes:comparison`, so this was read out of
`ComparisonCondition.deserialize` with `javap` after two wrong guesses:

```json
{"name": "hordes:comparison",
 "value": {"type": "double", "operation": "GREATER_OR_EQUAL",
           "value1": {"type": "hordes:player_pos", "value": "x"},
           "value2": -1088.0}}
```

- `type` on the comparison is the **atlas `DataType`**, lowercase: `byte`, `short`, `int`, `long`,
  `float`, `double`, `string`, `boolean`. **Omitting it is the whole of "Incorrect parameters for
  condition hordes:comparison"** — the error names the condition, not the missing key.
- `operation` is atlas's `ComparableOperation`: `EQUALS`, `NOT_EQUALS`, `GREATER_THAN`,
  `GREATER_OR_EQUAL`, `LESS_THAN`, `LESS_OR_EQUAL`.
- the position getter's axis field is **`value`**, not `axis`. `axis` is only a local name inside
  `PosGetter.get`.

### Dressing and drops, in the table rather than a script

The dressed entry carries `ArmorItems`, `HandItems`, `ArmorDropChances:[0.0f x4]` and
`HandDropChances:[0.0f, 0.0f]` in its `nbt`, and loads. For **wave** mobs this is a cleaner answer to D4
than In Control drop chances: the rank and its drop suppression live in one place, in the same file that
defines the wave. `hordes:set_entity_loot_table` also exists, which is the lever for F3 (armour dropping
at low rates) without touching "no working guns from corpses".

E7a still stands for everything In Control dresses; this only covers what a wave spawns.

### What is not yet proven

`spawnWave` takes a count or a player, so firing one needs somebody in the world — it cannot be driven
from RCON on an empty server. Everything up to the moment of spawning is verified: commands registered,
table loaded, script loaded, geofence parsed, NBT accepted. What still needs one in-game check is that
the wave actually draws from `gscraft_skad` inside the box and from `hordes:default` outside it, and
that the dressed Scavenger drops nothing. Stand in Skadowsky and run `/hordes spawnWave 1`.

## 5. Decisions worth taking now

The enemy pass leaves six open (F1 to F6) and recommends a default for each. Five can be taken as
recommended without further work. The one worth pausing on is **F4, infinite NPC ammunition**: it is
`false` today by a mod default rather than by a decision, and it is the only one of the six that changes
how every firefight in the game feels.

## 6. What is not wrong

Worth stating plainly, because everything above is a defect list: the map, the roads, the builds, the
mod list, the pack delivery and the deploy guard are all in good order. The desert city conversion is
complete, the pack updates itself on launch, and the deploy path now refuses to overwrite a world it did
not just pull. The problem is not quality. It is that the content layer has not started.
