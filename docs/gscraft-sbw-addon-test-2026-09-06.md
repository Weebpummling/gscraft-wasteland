# Frontline Combat Pack and DragonRise: local compatibility test

Run 2026-09-06 on an isolated copy of the local server (`scratch/modtest`, 8 GB heap, Forge 47.4.23),
booted once per change against a fresh world and again against a copy of `server/wasteland-v8`. The
live server and the staged world were not touched.

## Verdict

Both addons work, but only on Superb Warfare **0.8.9-final**, and only if two mods already in the pack
are upgraded and two new libraries are added. The newest build of each addon does **not** work.

## The version trap

Superb Warfare ships three 1.20.1 builds that matter here: 0.8.8-final (what GSCraft runs), 0.8.9-final
(May 2026) and 0.8.9.1 (August 2026). The addon ecosystem is split across the last two, and three mods
pin the dependency to *exactly* `[0.8.9]` rather than `[0.8.9,)`:

| Mod | Declared Superb Warfare range | Works on 0.8.9 | Works on 0.8.9.1 |
|---|---|---|---|
| Frontline Combat Pack 1.2.1 | `[0.8.9]` | yes | refused at load |
| Vintage Vehicle Pack 0.2.1 | `[0.8.9]` | yes | refused at load |
| MCSP 1.0.9 / 1.0.10 | `[0.8.9]` | loads, 4 files fail | refused at load |
| DragonRise:Reforge 1.4.1.01 | `[0.8.9,)` | yes | untested |
| DragonRise:Reforge 1.5.0-beta | `[0.8.9,)` | **crashes** | presumably yes |

DragonRise 1.5.0-beta passes the declared version check on 0.8.9 and then dies during mod construction:

```
java.lang.IncompatibleClassChangeError: class com.redabysslucia.dragonrise_reforge.entities.projectile.Aim120Entity
  overrides final method com.atsuishio.superbwarfare.entity.projectile.Mis...
    at com.redabysslucia.dragonrise_reforge.init.ModEntities.<clinit>(ModEntities.java:511)
```

It was compiled against 0.8.9.1. Going to 0.8.9.1 to satisfy it is not possible, because the loader then
refuses three other mods:

```
Mod ID: 'superbwarfare', Requested by: 'vvp',  Expected range: '[0.8.9,0.8.9]', Actual version: '0.8.9.1'
Mod ID: 'superbwarfare', Requested by: 'mcsp', Expected range: '[0.8.9,0.8.9]', Actual version: '0.8.9.1'
Mod ID: 'superbwarfare', Requested by: 'fcp',  Expected range: '[0.8.9,0.8.9]', Actual version: '0.8.9.1'
```

So 0.8.9-final is the only version the whole set agrees on, and DragonRise has to stay at 1.4.1.01.

## The mod changes this needs

Nine jar changes, taking the pack from 111 to 115 entries.

| Change | From | To |
|---|---|---|
| Superb Warfare | 0.8.8-final, 25.7 MB | 0.8.9-final, 31.7 MB |
| MCSP | 1.0.8 | 1.0.9 (CurseForge only; Modrinth stopped at 1.0.8) |
| Vintage Vehicle Pack | alpha 0.2.0 | alpha-beta 0.2.1, 26.7 MB |
| Kotlin for Forge | absent | 4.12.0, 7.4 MB (0.8.9 uses `modLoader = "kotlinforforge"`) |
| SnAssets Library - Particles | absent | 1.0.1, 0.6 MB (Vintage Vehicle Pack 0.2.1 requires it) |
| Frontline Combat Pack | absent | 1.2.1, 56.1 MB |
| DragonRise:Reforge | absent | 1.4.1.01-hotfix1, 35.3 MB |

MCSP and the Vintage Vehicle Pack are not optional here. Both pin Superb Warfare to a single version, so
upgrading the core without upgrading them stops the server at the mod-sorting stage.

## What the addons bring

Counted from each jar's language file, so this is registered content, not marketing copy.

| Mod | Entities | Items | Blocks |
|---|---|---|---|
| Frontline Combat Pack | 96 | 4 | 0 |
| DragonRise:Reforge | 108 | 37 | 1 |
| Superb Warfare 0.8.9 (for scale) | 80 | 328 | 32 |

Both are almost entirely entities. For prop work that means vehicles that tick, take damage and can be
driven off, not placeable scenery. Only one new block between them.

## Registry effects on the existing world

The pack references 29 Superb Warfare ids across the ImprovedMobs equipment table, the InControl loot
table, two KubeJS scripts and the Zombie Awareness list. All 29 still exist in 0.8.9. Eleven items were
removed between 0.8.8 and 0.8.9 (`ap_5_inches`, `cm_5_inches`, `gs_5_inches`, `he_5_inches`,
`small_shell`, `aurelia_sceptre` and its blueprint, `bread_bullet`, `butterfly_bullet`,
`curse_flame_bullet`, `special_material_pack`); none of them is referenced by the pack, but any that a
player is holding will be dropped on first load. 69 entries were added.

The first boot after the swap logs `There are unidentified mappings in this world` and rewrites the
registry. That is the expected one-time migration, and it did not repeat on later boots.

## Known damage

MCSP's M1A2 Abrams is broken on 0.8.9, in both 1.0.9 and 1.0.10:

```
Couldn't parse data file mcsp:m1a2 from mcsp:sbw/vehicles/m1a2.json
kotlinx.serialization.SerializationException: com.atsuishio.superbwarfare.tools.OBB.Part
  does not contain element with name 'WeaponStationBarrel' at path $.OBB[8].Part
```

Four skins fail (`m1a2`, `m1a2_sand`, `m1a2_sep`, `m1a2_sep_sand`). The part name exists only in 0.8.9.1,
so both MCSP builds are really written for the newer core. Everything else in MCSP loads. There is no
build of MCSP that works correctly on 0.8.9, and 1.0.8 cannot be kept because it pins 0.8.8.

DragonRise also logs `Entity dragonrise_reforge:nukerbomb has no attributes` 153 times per boot. It is
noise, not a failure, but it is 153 lines of it every start.

## Boot and memory

Peak resident memory of the server process, sampled every 5 s, and the time from launch to `Done`.

| Configuration | Mods | Boot | Peak RSS |
|---|---|---|---|
| Current pack, real world | 107 | 2.0 s | 2912 MB |
| Full stack, real world | 111 | 2.7 s | 3224 MB |
| Current pack, fresh world | 107 | 7.3 s | 3233 MB |
| Full stack, fresh world | 111 | 2.1 s | 3741 MB |

The cost on the real world is about **310 MB**. The host's plan is 8192 MB with the container OOM killer
enabled, and it has been sitting at 7.0 GB idle, so the headroom question is about the existing footprint
rather than about these two mods. Client-side cost is larger and was not measured here: 97 MB more jar
content, mostly models and textures, on instances the install guide sets to 4 GB on an 8 GB machine.

Error counts per boot, for comparison: 24 on the current pack (pre-existing Immersive Vehicles and
InControl noise), 33 after the Superb Warfare upgrade, 280 with DragonRise (153 of them the nukerbomb
line, plus the 4 MCSP parse failures).

## Reproducing

The tested set is in `scratch/modtest/mods` and the jars in `scratch/modtest_jars`, with one log per
stage in `scratch/modtest`. `boot.py` boots the isolated server once, waits for `Done`, samples memory
and stops it.

---

# Second pass: MCSP and the Vintage Vehicle Pack dropped

Owner's call, 2026-09-06: MCSP and the Vintage Vehicle Pack duplicate too many vehicles and can go. That
removes two of the three `[0.8.9]` pins and most of the mess above. Retested from a clean boot.

## The set that works

Six jar changes, and the server ends up with one more mod than it has today, not five.

| Change | Detail |
|---|---|
| Superb Warfare | 0.8.8-final -> 0.8.9-final |
| Kotlin for Forge | added, 4.12.0 (0.8.9 uses it as its mod loader) |
| Frontline Combat Pack | added, 1.2.1 |
| DragonRise:Reforge | added, 1.4.1.01-hotfix1 |
| MCSP | removed |
| Vintage Vehicle Pack | removed |

SnAssets Particles is no longer needed; only the Vintage Vehicle Pack wanted it. The M1A2 parse failure
is gone with MCSP. Server mod jars go from 107 to 108, 415 MB to 487 MB.

The Frontline Combat Pack still pins `[0.8.9]`, so DragonRise stays at 1.4.1.01 and Superb Warfare cannot
go to 0.8.9.1. Dropping the two duplicating packs does not change that.

## Nothing was lost from the world

A scan of all 46 entity region files in `server/wasteland-v8` found no `mcsp:` or `vvp:` entity anywhere.
Every Superb Warfare entity present is core content (`hpj_11` turrets, `laser_tower`, ammo boxes,
blueprints), none of it among the eleven items removed in 0.8.9. The first boot after the swap logs the
registry migration for the retired ids and does not repeat it.

For the record, the rosters overlapped less by name than by type: only 1 of MCSP's 37 vehicle names and
12 of the Vintage Vehicle Pack's 52 appear in the Frontline Combat Pack or DragonRise. What actually goes
is the main-battle-tank line those two carried and the new packs do not: T-80, T-90A, Challenger 2,
Leopard 2A7V, M1A2 Abrams, TOS-1A, HIMARS.

## Two config edits this needs

Both were applied to the test copy and verified.

- `config/improvedmobs/equipment.json` referenced seven MCSP armour pieces and logged
  `No items with following names exist` on boot. Swapped for DragonRise equivalents at the same weights:
  the three CHEST entries to `msv_chest`, `kevlar` and `kr06_chest`, the four HEAD entries to
  `fast_helmet`, `kr06_helmet`, `t21_helmet` and `un_helmet`.
- `kubejs/server_scripts/gscraft_recipes.js` stripped the vehicle-assembling recipes for `vvp` and
  `mcsp`. Repointed at `fcp` and `dragonrise_reforge` so the station-only rule still covers every
  military vehicle. The script reports 121 rules stripped.

After both edits: zero ImprovedMobs errors, zero mentions of the removed mods.

## What still logs errors

Nothing fatal, but the new mods are noisy, and all of it traces to the same cause as the M1A2: parts of
both packs are written against Superb Warfare 0.8.9.1.

| Symptom | Count per boot | Effect |
|---|---|---|
| `Entity dragonrise_reforge:nukerbomb has no attributes` | 153 | none, log noise |
| `Failed to load wreckage loot data for dragonrise_reforge:<vehicle>` | about 70 | destroyed DragonRise vehicles drop nothing |
| `dragonrise_reforge:sd905` and `test_ship`: `EngineType does not contain element with name 'Airship'` | 2 | one airship unavailable; `test_ship` is a dev leftover |
| `[FCP] Failed to load trailer_driver config fcp:trailer_driver/kamaz.json` and `trailer_towed/seeder.json` | 2 | malformed JSON inside the mod; those two trailers will not tow |

## Boot and memory, final set

Same harness, same copy of the real world.

| Configuration | Server jars | Boot | Peak RSS |
|---|---|---|---|
| Current pack | 107 | 2.0 s | 2912 MB |
| Final set, before the config edits | 108 | 1.9 s | 2900 MB |
| Final set, after the config edits | 108 | 1.8 s | 3076 MB |

Dropping two mods to add two leaves memory where it was, within the noise of GC timing. The 310 MB the
first pass measured came from keeping MCSP and the Vintage Vehicle Pack alongside the new packs.
