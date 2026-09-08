# Desert city — 1.12 block conversion (2026-09-08)

The desert city hub was built in 1.12 against Chisel, Fureniku's Roads, HBM's Nuclear Tech, MrCrayfish's
Furniture and Simply Light. None of those five has a 1.20.1 jar with the same block ids, so the transplant
mapped every one of them onto something the pack does ship. Where a mod's own successor existed the block
kept its character; where it did not, the block fell to a vanilla lookalike — a stand-in that holds the
shape and roughly the colour but reads as plain stone or concrete up close.

This is the ledger of how much of the city is itself and how much is still standing in.

## Where it stands

Measured against the original 1.12 save as the base, over the 147,416 modded block positions that both
survive in the deployed world and still hold a value the re-skin recognises:

| | blocks | share |
|---|---:|---:|
| converted to a mod block | 146,941 | 99.7 % |
| left as a vanilla stand-in | 475 | 0.3 % |

| source mod | faithful | stand-in |
|---|---:|---:|
| Fureniku's Roads | 64,173 | 0 |
| Chisel | 61,552 | 475 |
| HBM | 14,623 | 0 |
| Simply Light | 6,422 | 0 |
| MrCrayfish's Furniture | 170 | 0 |

Before the 2026-09-08 pass the stand-in count was 4,437 (3.0 %). Two changes closed the gap.

**The roads, 64,173 blocks.** Fureniku's Roads has a 1.20.1 port, so every road, sidewalk and kerb goes
back to being a road block instead of a Chisel concrete tile. This is the one part of the conversion that
needs jars the server does not run yet: `furenikusroads-0.1.0` and `metropolis-0.1.0`. Fureniku's Roads
does not declare its own library in `mods.toml`, so shipping it without Metropolis crashes the server with
`NoClassDefFoundError: com/fureniku/metropolis/utils/Debug`. Both are staged, neither is deployed.

**The decoration, 5,858 blocks.** Fifteen HBM and MrCrayfish families that had collapsed onto four vanilla
blocks, re-pointed at mods already installed — no new jar, no extra memory:

| was standing as | now | count |
|---|---|---:|
| `industrial_deco:lab_wall` | `chipped:massive_stone_bricks` | 1,896 |
| `minecraft:cracked_stone_bricks` | `chipped:cracked_disordered_stone_bricks` | 1,183 |
| `minecraft:cracked_stone_bricks` | `chipped:vertical_disordered_stone_bricks` | 972 |
| `minecraft:mossy_stone_bricks` | `chipped:eroded_mossy_stone_bricks` | 690 |
| `minecraft:iron_bars` | `immersive_weathering:rusted_iron_bars` | 378 |
| `minecraft:iron_bars` | `immersiveengineering:steel_fence` | 290 |
| `minecraft:iron_bars` | `immersiveengineering:alu_fence` | 170 |
| `minecraft:smooth_stone` | `chipped:smooth_light_gray_concrete` | 171 |
| `minecraft:smooth_stone` | `chipped:stacked_light_gray_concrete` | 60 |
| `minecraft:smooth_stone` | `chipped:sanded_smooth_stone` | 48 |

The three concrete damage states had been sharing one cracked-brick texture, so a ruined wall and a merely
weathered one looked identical; they are three distinct blocks again. The railings, the steel fence and the
wire fence had all been iron bars, which is the right shape but the wrong story for a dead city — the
railings now carry their own rust, and a wire fence no longer reads as a window grille.

## What is deliberately left

The remaining 475 are `chisel:antiblock` in purple and light grey, sitting as vanilla purple and light grey
concrete. That is not a compromise: an antiblock **is** a flat single-colour block, and vanilla concrete is
exactly that. AntiBlocks Rechiseled ships only nine "bright" colours and neither of these is among them, so
the vanilla block is the closer match. Nothing further is gained by moving them.

## Two things that will bite again

**Never map anything to `industrialdeco:metal_fence_block`.** Its `getShape` asks the level for its
neighbours' states, the sky-light engine calls it while lighting a chunk, and if a neighbour sits in an
unloaded chunk the light worker blocks on the chunk the main thread is waiting to finish. The server
deadlocks until the watchdog kills the tick. 838 of them cost six crashes on 2026-09-06. Vanilla
`iron_bars`, IE's fences and Immersive Weathering's bars all take their shape from their own blockstate and
never touch the level.

**Table order decides the winner.** `reskin112.py` builds one `IMPROVED` dict through a series of updates,
so a later table silently overrides an earlier one. The decoration mappings were first written above the
`HBM` table and seven of the fifteen were swallowed without any error — the dry run simply reported no
change. They now sit below every hbm and cfm rule, immediately before `new_resolve`, and record what they
replace into `DECOR_PREV` rather than naming it by hand. That matters because the re-skin only touches a
position that still holds what the previous pass wrote: guess that value wrong and the block is skipped.

## Status

Verified by dry run against the sandbox world, not deployed. Nothing has been written to the live server.
