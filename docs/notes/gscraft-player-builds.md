
**Instruction (user, 2026-09-02):** the old world folders on the server are player-made 3D
sceneries — *save them, recover them, and place them onto the new overworld, dependencies
matching.* Nothing that holds a build gets wiped without a local copy first.

**Local copies (`Documents\Minecraft Server Tools\pull\`):** `worlds\` = July 2025 original
(near-empty), Oct–Dec 2025 world (438 MB) + a Sept 2025 zip of it from the server root (531 MB),
the orphaned root `region/`, and the **live world** (315 MB). `snapshot\` = mods, libraries,
tacz, tacz_backup, serverconfig, modernfix, root files. With config/logs/crash-reports this IS the
rollback — **this Bisect plan has 0 panel backup slots** (`TooManyBackupsException`).

**Where the builds are — the live world is the superset.** The previous admin moved old chunks
x −84…53, z −64…40 into the live world at **chunk offset (+140, +89)** (blocks +2240, +1424) →
live chunks x 56…193, z 25…129; 479 chunks identical, 891 edited since. Live sites: mega-base
(2192…2575, 400…927; 432 k `factory_blocks:factory` platform, 964 bookshelves, 885 sculk sensors),
industrial district (1904…2367, 864…1135), hempcrete compound (1568…1887, 1152…1471), acacia hall,
library (2032…2127, 1392…1487), Warium spawn structure (0…31, 0…31), ~20 small vanilla sites.
Old sites never moved: the beacon/hopper array at old blocks (336…367, −1056…−1025) — 253
beacons, 325 hoppers — plus ~28 small ones.

**Transplant plan (`scratchpad\worlds\buildmap\transplant_plan.json`, 32 rectangles, 14,966
chunks):** live district **chunks x 56…193, z 24…129** (blocks 896…3103 × 384…2079) at the same
coords + spawn (−1…2, −1…2) + outlier (71…77, 8…13) + 29 old sites at (+140,+89). Runs AFTER the
new world generates (blueprint phase 04) via `runplan.py --plan … --dst <new world>` (no
`--dry-run`). Reports: `scan-overworlds.txt`, `buildmap.txt`, `builds.json`, `dryrun.log`.

**Block remap — `Minecraft Server Tools\remap_full.json`, 354 entries** (built by `makeremap.py`
from `remap.json` + `remap_todo.json`): 9.9 M blocks map explicitly (Warium tar→blackstone,
bauxite→terracotta, all cut-mod ores→stone/deepslate, Create strata→stone/tuff/granite/
deepslate/blackstone, Iron's arcane debris→deepslate, Spore infested→clean equivalents, Alex's
Caves cinder block→light gray concrete, TF planks/towerwood→jungle/dark oak…), 814 by suffix
rule, **3,210 to air** (Spore fungal growths, Horror Element Mod corpses/blood, Alex's Caves
machines, TF fireflies). Target namespaces: minecraft, immersiveengineering, factory_blocks only.
Rebuilt-pack namespace set lives in `planblocks.py::KEEP` — update it if the mod list changes.

**Dependencies of placed blocks** (ores, LC hempcrete filler, Backrooms, repeating generated
structures excluded): IE 79 k (kept); **factory_blocks 511 k, chisel 96 k, antiblocksrechiseled
14 k — moved from cut to KEEP** (+ athena/cryonicconfig libs, + Chipped so factory blocks craft).
Already-missing (holes today, worldgen not builds): spore, dimdoors, modern_structures.

**Classifier lessons (so they are not re-learned):** in this pack Lost Cities fills city ground
with `immersiveengineering:hempcrete(_pillar)` — millions of blocks, ores embedded — and
`backrooms:roof` is the Backrooms dimension; both are terrain. Apocalypse-pack buildings recur
(chest + spawner + blast furnace ×26; sign + campfire + decorated pot ×3; 33-chest loot houses) —
a repeating block-entity fingerprint or ≥5 spawners means generated. Adjacent halves of one build
share a fingerprint, so never apply the repeat rule to neighbours; the old-only plan therefore
keeps every strong-signal site unless spawner-heavy.

**Tools** (all in `Documents\Minecraft Server Tools\`): `scanregion.py` (Anvil reader, numpy
palette counting), `buildmap.py` (sites, offset vote, plan, remap skeleton), `planblocks.py`
(every cut-mod block inside the plan, with counts), `makeremap.py`, `transplant.py` (typed NBT,
byte-exact `--selftest` over 29,273 live chunks; chunk copy with shift, remap, property-family
rule, orphan block-entity drop, entities, POI), `runplan.py` (all rectangles; `--dry-run`
aggregates namespaces — **takes >10 min, run it in the background**). Trial: 4 chunks moved and
re-scanned with identical signatures.

**Cleanups done:** the four `[1.21]` datapacks deleted from the live world; a stray `C:\c\`
tree from a mis-extraction removed. Git Bash note: with `MSYS_NO_PATHCONV=1` set, local paths
must be given Windows-style (`C:/...`) or python writes to `\c\Users\...` on the current drive.

Related: [[gscraft-bisect-server]].

**Full re-read of every old-world copy (2026-09-02 evening, user asked for the cyberpunk
cityscape):** `worldscan.py` (per-chunk material layers) + `topdown.py` (block-resolution colour
render; renders in `scratchpad\scan\` and the repo `docs\renders\`). Findings: the October world
and the 531 MB September zip are ONE seed and differ only in explored terrain (zip: 3,945 built
chunks that October lacks, all forest/rivers; October: 2,665 the zip lacks) - no lost districts.
The old worlds are NOT Lost Cities; they are vanilla-ish landscape with ONE custom complex in the
north: **the FR-06 complex** = starship hangar labelled FR-06 on its own island + walled reactor
plaza with a stadium + a cyan/magenta refinery wing (= the map sites "FR-06 complex" 2192-2575 x
400-927 and "Industrial plant" 1904-2367 x 864-1135). That IS the cyberpunk cityscape; it was
moved by the admin into the live world and is inside the transplanted district; rendered from the
new world it is identical. The live world (an ocean map, the LC one) also has generated LC towns
and two long player rail causeways WEST of the district (x chunks 40-135, z ~36/44) - not carried.
"Placed" in worldscan counts trees (leaves/logs are not NATURAL) - do not read it as built.
Location pool for the endgame = the custom structures (FR-06, plant, hempcrete compound, stone
complex, residential block, library) + the five compound pads.
