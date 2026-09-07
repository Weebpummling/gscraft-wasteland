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
