# The underground network: sewers, tunnels and rail as the connective layer

Research note, 2026-09-04. Source: the co-creator who supplied the old server maps (Adriǡn, via the owner), plus a
census of every save we hold. Written for the map replan (roads-and-terrain-first, 9-step process): the underground
is the second spine, under the roads.

## 1. The creator's vision, as stated

Quoted points, lightly ordered:

1. There are many sewer and subterranean sections spread across the builds and the PvP maps; they were meant to be
   **interconnected through the train areas and the sewer systems**.
2. The **Sewer PVP map** was to be one of the central "underground" zones connecting everything. In the video
   (`M I N E P U N K`, blvck_poltergvst, unlisted, 3:02, "three maps from my minecraft/cyberpunk/2020 lockdown era",
   HBM + VMW mods) its opening section shows a piece of that central sewer system **with slums and a railway**,
   intended as a **smuggling hub**.
3. "Zone 2" in the video is the **industrial zone**; it can connect to anything **via a railway on the far edge of
   the map**, or through a more official **railyard stop where loading at the storage area occurs**. Rail is the
   versatile connector: "it can connect any sections of a map just via rail". The industrial-zone PvP map has
   **two rail connections**.
4. The last map shown is the **financial district**; it can sit next to Bio Gen or in a high-security / high-income
   zone; it **contains a small rail system that can be extended** to other areas.
5. One of the old-world builds had a "REALLY cool sewer section" with a **room built for a boss fight**; the
   creator could not find screenshots of it.
6. The creator offers to help by hand or to guide the vision.

## 2. What the saves actually contain (census 2026-09-04, `scratch/underground/`)

Method: for the 1.12 saves, `scan112.py` (built blocks by depth band, every rail block with coordinates,
per-chunk underground air) over the save's own block registry; for the 1.20 worlds, `scan120.py`. Vanilla
`minecraft:rail` in small scattered clusters at y 10–40 is abandoned mineshafts, not player work; the player rail
in this pack is `hbm:rail_highspeed` and `minecraft:golden_rail` (powered rail), and Lost Cities 2.0's own
railways are the long straight grid lines at y 48–63.

| Save | Underground finding | Player rail |
|---|---|---|
| **SewerPVP** (vanilla terrain, spawn −124 64 −248) | One compact hand-built complex, chunks x −59…−54 z −21…−16 = blocks **x −944…−849, z −336…−241 (96×96)**, built y 14…60 (20,740 blocks below y 40 in the modded core), HBM steel grates and rusted pipe runs, IE stone decoration, Chisel; the ring of vanilla stone-brick chunks around the core is the same complex. Everything else in the save (890 "built" chunks) is natural caves and 12 mineshafts. This is what `scratch/upgrade/sewers` already holds. | none of its own (9 mineshaft rails inside the box) |
| **world** (Lost Cities 2.0 + BoP, spawn −790 151 1675) | Two hand-built underground rooms south of spawn: **x −960…−929, z 1808…1855 (32×48), y 14…63**, ~10,000 built blocks: HBM factory and laboratory blocks, illuminant blocks, red sandstone (an underground lab / bunker; the best candidate for the "boss fight" room); and **x −1040…−1025, z 1840…1855**, y 27…63, ~2,500 blocks of factory, steel grate, tungsten ladders. The 498 other underground chunks are Lost Cities 2.0 cellars and railways. | **`hbm:rail_highspeed`: a straight double track at y 61, x −985…−751, z 1903…1910 (235 blocks)**, 230 m south of spawn, next to the lab; **`golden_rail`: 566 blocks at y 54, a powered minecart line running x −1545…151 along z ≈ 1104…1119 with branches** (a 1.7 km east–west minecart route) |
| **Financial Plaza Quarantine** (superflat) | The plaza has a full basement level, y 35…63, concrete / antiblock / road blocks, **x −384…−321, z −1152…−1121** core (8,759 built blocks below y 60) | **`hbm:rail_highspeed`: 140 blocks at y 40, x −367…−360, z −1141…−1069**: the "small rail system" under the plaza, 72 blocks long, dead-ends both ways (the stub to extend) |
| **Novo Expograd Industrial Zone** (superflat, ground y 230) | 31,000 blocks built below y 60 relative to its own datum (basements and pits under the refinery yard) | no rail blocks of any kind in this save; the "two rail connections" the creator remembers are not in this copy (a different export, or built as roads/pipe runs rather than rail blocks) |
| **Bio Gen offices** | 7,861 blocks below y 40: the three offices are dug in, no tunnels | none |
| **Live world district** (2025 builds, kept in v7 at x 896…3103 z 384…2079) | 31,877 rails, of which the 15,265 at y 48…55 and the ramps at y 58…62 are Lost Cities 7 railways and stations, and the clusters below y 40 are mineshafts; the deep block counts are unusable (the scanner counts deepslate as built). The **4,352 rails at y ≥ 58** are the player's: see the next column. | **A rail yard on the district's east edge**: four parallel N–S tracks at **y 66 along x 2954, 2986, 3002 and 3018**, 100–207 rails each, running the length of the district (z 384…1900) - this is the "railway on the far edge of the map" beside the industrial zone; an **E–W line at y 72 along z 771, x 1792…1919** (160 rails, into the industrial district); short elevated pieces at y 92 (x 2048…2111, z 896…959) and **y 129 (x 2368…2431, z 832…895)** over the mega-base; a y 64 run at x 1920…1983, z 896…959 |
| **Old server worlds** (`Escape_From_Minecraft` = the Oct–Dec 2025 world at its original coordinates; `Escape_From_Minenkrafte` = the live world, the district at the same coordinates as in v7) | Nothing beyond what the district already carries: the 12,986 rails at y 48…55 and the 300…1,792-block straight runs at y 54 in Minenkrafte are Lost Cities 7 railways; the deep clusters are mineshafts. The player rail features are the same ones listed above (the old world's cells map onto the live district's at the known +2240/+1424 block offset). No separate sewer complex or boss room turned up in either world by depth census; if the creator's "REALLY cool sewer section" was in a 1.20 world, it is not in these two backups. | same as the district |

## 3. What this means for the new map

- **The underground spine is rail, not sewer.** The creator says so, and the saves agree: the only long player-built
  lines are rail (the 1.7 km minecart route and the high-speed track in `world`), and the sewer content is compact
  rooms (SewerPVP's 96×96 core, the plaza basement, the lab south of spawn). Sewers are **nodes**; rail is the
  **edge**.
- **Lost Cities gives the rail for free.** LC 7.5.3's railway system (on in the `wasteland` profile: `railwaysEnabled`,
  stations, `railwayDungeonChance`) already lays straight rail tunnels between cities with underground stations. In
  the replan Lost Cities only generates inside the drawn city zones; its railways then run between those zones and
  give the network its trunk lines. What we add by hand are the **spurs**: from the nearest LC station to each
  hand-placed sector's rail stub.
- **Each sector gets a rail gate**, the same way it gets a road gate: the plaza's y-40 stub, a railyard stop at the
  industrial zone's storage area (built, since the save has none), Skadowsky's own rail line (it has one, N–S along
  x ≈ −300 in its source, with a viaduct over the highway), a platform in the Sewer PVP core. The rail level has to be
  agreed: LC railways sit near y 48–63; the plaza stub is at y 40, the world's high-speed line at y 61, the minecart
  route at y 54. One trunk level (LC's) and short grades to each sector's stub.
- **The Sewer PVP core becomes the central underground hub** as intended: slums + railway + smuggling economy. In
  quest terms that is Teddy's world and the smuggler counter; in map terms it sits under the middle of the map
  where three trunk lines meet, with surface access from a Lost Cities station, a manhole in the plaza district and
  the storm drain at the river.
- **The boss room** is the lab at world x −960…−929, z 1808…1855: transplant it whole (32×48×50, HBM blocks remap to
  our factory/IE vocabulary) as a dead-end off the rail trunk, the finale of an underground chapter.
- **Vertical layering** to avoid: our surface sites use pads down to y 67…82 and the plaza's sewers were stacked
  below y 48 in v6; the rail trunk at LC's level would cut through them. The terrain plan must reserve a rail
  corridor band (say y 44…52) under every sector before grading.

## 4. Open questions for the creator (through the owner)

1. Which save held the industrial zone with the two rail connections? The copy we have has no rail blocks.
2. Is the lab south of spawn in `world` (HBM factory + laboratory blocks, red sandstone, y 14…63) the boss room?
3. Slums + railway in the video's first section: is that inside the SewerPVP 96×96 core, or a part of the world
   that was not exported?
4. Preferred rail level and gauge: HBM high-speed (double track) or vanilla powered rail; one trunk level for the
   whole map?

## 5. Files

- `scratch/underground/scan112.py`, `rails112.py`, `scan120.py` (the census tools, to move into `tools/` once stable);
  `*_underground.json` (per-chunk depth bands + rail coordinates), `*_air.json`, `*_rails.png` (rail positions by
  depth over underground-air / built maps).
- Source saves: `incoming/Maps/*` (1.12), `scratch/oldworlds/*` (2025 server worlds), `scratch/worlds/wasteland-v7-final`.
- The transplanted sewer core: `scratch/upgrade/sewers/world` (already 1.20.1).
