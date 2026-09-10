# GSCraft — what equipment the pack actually has (2026-09-09)

Read out of the **live item registry**, not from assets and not from the design. Asset scanning cannot
tell an armour item from a block model and cannot tell which slot a piece goes in; the registry can. The
dump script is `tools/kubejs_equipment_dump.js` — drop it in `server/kubejs/server_scripts`, boot the
local server once, and read `EQUIPDUMP` and `CLASSDUMP` out of `logs/latest.log`. It is not part of the
shipped pack.

Of 13,911 mod items in the registry, **142** are vanilla-class equipment (armour, swords, bows, tools,
shields). The rest are blocks, blueprints, perks, ammunition and materials.

## Armour — 82 pieces, 57 of them not vanilla

| namespace | head | chest | legs | feet | note |
|---|---:|---:|---:|---:|---|
| `minecraft` | 7 | 6 | 6 | 6 | leather to netherite, plus the turtle helmet |
| `dragonrise_reforge` | 10 | 9 | 6 | **0** | the modern tactical wardrobe; **no boots at all** |
| `immersiveengineering` | 2 | 2 | 2 | 2 | two complete sets: faraday (insulated rubber) and steel |
| `create` | 3 | 3 | 1 | 3 | cardboard, copper diving, netherite diving |
| `pomkotsmechs` | 2 | 2 | 2 | 2 | two complete sets: wanderer and pomkots — the only soft kit |
| `superbwarfare` | 3 | 2 | **0** | **0** | US, Russian and a WW2 shell; helmets and vests only |
| `immersive_weathering` | 1 | 0 | 0 | 0 | a flower crown |

**Complete four-slot sets exist only in** `immersiveengineering` (faraday, steel), `create` (cardboard,
copper diving, netherite diving) and `pomkotsmechs` (wanderer, pomkots). Everything else has to be mixed.

### Corrections to the design's §2.1

- **Dragon Rising ships no boots — but it does ship six leggings**: `desert07_pants`, `gorka3_leggings`,
  `kr06_pants`, `msv_pants`, `ocean07_pants`, `pants21`. The design records the missing boots and stops
  there, which left every dressed enemy bare-legged. They are dressed now.
- `army07hat` is registered as a **CHEST** piece despite the name — confirmed, as §2.1 warned.
- `cn21` and `cnfast` are HEAD items — the §2.1 note that they give zero protection stands; they are not
  used for armour.
- The only shield in the pack is `minecraft:shield`.

## Weapons

### Guns — five separate systems, and they do not share ammunition

| system | count | what it is |
|---|---:|---|
| **TACZ** | **54 guns** | all behind one item, `tacz:modern_kinetic_gun`, selected by a `GunId` tag: `ak47`, `type_81`, `m4a1`, `hk416d`, `kar98`, `m107`, `spas_12`, `uzi`, `p90`, `rpg7` and 44 more |
| **Superb Warfare** | **21 guns** | real items: `ak_47`, `ak_12`, `hk_416`, `sks`, `svd`, `qbz_95`, `qbz_191`, `vector`, `glock_17`, `glock_18`, `trachelium`, `marlin`, `ntw_20`, `devotion`, `minigun`, `rpg`, `bocek`, `taser`, `hunting_rifle`, `homemade_shotgun`, `secondary_cataclysm` |
| **Pillager's Gun** | **5** | `assault_rifle`, `shotgun`, `pistol`, `snipers_rifle`, `bazooka` — the NPC gunner set, and the only one an enemy uses by itself |
| **Pomkots** | 3 | `magazinerifle`, `magazinemachinegun`, `magazineshotgun` — mech weapons |
| **Immersive Engineering** | 1 | `railgun`, the Fusilier's |

### Melee — 17 pieces outside vanilla

`superbwarfare`: `knife`, `crowbar`, `steel_pipe`, `electric_baton`, `t_baton`, `beast`, and five hammers
(`hammer`, `steel_hammer`, `golden_hammer`, `diamond_hammer`, `netherite_hammer`,
`cemented_carbide_hammer`). Plus `immersiveengineering:sword_steel`, `create:cardboard_sword`,
`immersive_weathering:ice_sickle`, `refurbished_furniture:knife` and `spatula`.

`superbwarfare:military_shovel` and IE's four steel tools register as tools rather than weapons, along
with Farmer's Delight's five knives.

## What the factions are using now

Out of that inventory, `tools/spawn_rules.py` assigns:

| rank | head | chest | legs | feet | hand |
|---|---|---|---|---|---|
| Militia Shield | PASGT | IE steel | IE steel | IE steel | — |
| Militia Gunner | sniper21 | IOTV | kr06 pants | — | — |
| Militia Trooper | PASGT | IOTV | kr06 pants | — | — |
| Militia Rifleman | PASGT | IOTV | kr06 pants | — | `tacz:type_81` |
| Plant Worker | faraday | faraday | faraday | faraday | crowbar |
| The Infected | — | med21 vest | — | — | — |
| Yard Hand | — | Gorka 3 | Gorka 3 | — | military shovel |
| The Dead | — | — | — | — | — |
| The Drowned | copper diving | copper backtank | — | copper diving | — |
| Scavenger | wanderer | wanderer | wanderer | wanderer | steel pipe |
| Scavenger Raider | ge M35 | Gorka 3 | Gorka 3 | wanderer | crowbar |
| Scavenger Elder | bandana | rags | rags | rags | — |

The roster below (`tools/spawn_rules.py`) spends **39 of the 57** non-vanilla pieces across 16 ranks.

| faction | rank | head | chest | legs | feet | hand |
|---|---|---|---|---|---|---|
| Militia — the spine | Sergeant *(12 %)* | fast | kr06 vest | kr06 | — | — |
| | Shield | PASGT | IE steel | IE steel | IE steel | — |
| | Gunner | sniper21 | IOTV | kr06 | — | — |
| | Trooper | PASGT | IOTV | kr06 | — | — |
| | Rifleman | PASGT | IOTV | kr06 | — | `tacz:type_81` |
| Militia — the plant | Sergeant *(12 %)* | fast | kr06 vest | msv | — | — |
| | Shield | **6B47** | IE steel | IE steel | IE steel | — |
| | Gunner | sniper21 | **6B43** | msv | — | — |
| | Trooper | **6B47** | **6B43** | msv | — | — |
| | Rifleman | **6B47** | **6B43** | msv | — | **`tacz:ak47`** |
| The Dead | Containment Crew *(35 %, reactor)* | **gas mask** | faraday | faraday | faraday | crowbar |
| | Plant Worker | faraday | faraday | faraday | faraday | crowbar |
| | The Infected *(hospital)* | — | med21 | — | — | — |
| | Yard Hand *(the yard)* | — | Gorka 3 | Gorka 3 | — | shovel |
| | Peacekeeper *(8 %, town)* | **UN** | msv | msv | — | — |
| | The Dead | — | — | — | — | — |
| | The Drowned *(intake)* | copper diving | backtank | — | copper diving | — |
| | Drowned Patrol *(bridge)* | **ocean07** | **ocean07** | **ocean07** | — | — |
| Scavengers | Captain *(6 %)* | **kr06** | **msv** | Gorka 3 | wanderer | crowbar |
| | Scrapper *(18 %)* | **cardboard** | **cardboard** | **cardboard** | **cardboard** | cardboard sword |
| | Scavenger | wanderer | wanderer | wanderer | wanderer | steel pipe |
| | Raider | ge M35 | Gorka 3 | Gorka 3 | wanderer | crowbar |
| | Elder | bandana | rags | rags | rags | — |

Two decisions worth recording. **The Militia's two detachments** wear different kit on purpose: the
spine's checkpoint is in US gear with a Type 81, the plant's garrison in Russian gear with an AK. They
are one army in whatever the plant's armoury held, not two armies — and crossing from one to the other
is a visible cue that the player has left the checkpoint and reached the last stand. **The rare variants**
use In Control's `random`, and unlike the common ranks they carry a `maxcount` rather than a deny: past
the ceiling they fall through to the ordinary rank below, so a full site is never an empty one.

Still unspent: the **desert07** set, whose ground is the desert city and therefore denied and deferred;
`cnchest`, `cnjustchest`, `aljin_helmet`, `t21_helmet`, `army07hat`, `pants21`, the netherite diving and
backtank pieces, and `flower_crown`. `cn21` and `cnfast` will stay unspent — they give zero protection.
