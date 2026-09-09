# GSCraft - point-of-interest coordinates

Every named place in the v8 wasteland, measured from the world as deployed on 2026-09-06
(census render `v8_cell_pass16`). Coordinates are the footprint centre, which is what a waypoint
wants. The ground sits at y 65 over most of the cell; the highest point is the tallest block anywhere
inside the footprint, which is what you spot from a distance.

World spawn: **-2555, 80, -2539**.
World border: centre **-1350.5, -1600.5**, size **5200** - playable x -3950..1249, z -4200..999.

## 1. Placed builds

| Place | Centre (x, z) | Footprint | Highest point |
|---|---|---|---|
| Camp (moved 2026-09-07; see `gscraft-skadowsky-camp.md`) | -940, -979 | x -978..-770, z -1060..-845 (209x216) | y 137 |
| Bio Gen offices | -2321, -585 | x -2352..-2289, z -640..-529 (64x112) | y 109 |
| Financial Plaza + sewers | -2273, -937 | x -2352..-2193, z -1008..-865 (160x144) | y 204 |
| Novo Expograd (expanded) | -2977, -154 | x -3568..-2385, z -1008..700 (1184x1709) | y 178 |
| Novo Expograd Industrial Zone | -2281, -753 | x -2352..-2209, z -832..-673 (144x160) | y 87 |
| Skadowsky sector | -857, -1113 | x -1088..-625, z -1488..-737 (464x752) | y 137 |
| KROT | -3233, -1185 | x -3392..-3073, z -1344..-1025 (320x320) | y 126 |
| Industrial district | 567, -1241 | x 336..799, z -1376..-1105 (464x272) | y 178 |
| Library | -2433, -3761 | x -2480..-2385, z -3808..-3713 (96x96) | y 108 |
| Mega-base | 559, -1865 | x 368..751, z -2128..-1601 (384x528) | y 219 |
| Runway (pad) | -1809, -3697 | x -2064..-1553, z -3792..-3601 (512x192) | y 75 |
| farmstead 1 | -2177, -577 | x -2208..-2145, z -608..-545 (64x64) | y 108 |
| farmstead 2 | -1713, -1745 | x -1744..-1681, z -1776..-1713 (64x64) | y 97 |
| farmstead 4 | -1281, -817 | x -1312..-1249, z -848..-785 (64x64) | y 73 |
| farmstead 5 | -2113, -897 | x -2144..-2081, z -928..-865 (64x64) | y 109 |
| farmstead 6 | -1473, -257 | x -1504..-1441, z -288..-225 (64x64) | y 72 |
| farmstead 8 | -2193, 319 | x -2224..-2161, z 288..351 (64x64) | y 110 |
| farmstead 9 | -2321, 31 | x -2352..-2289, z 0..63 (64x64) | y 78 |
| farmstead 10 | -1553, -1489 | x -1584..-1521, z -1520..-1457 (64x64) | y 93 |
| farmstead 11 | -2241, -1345 | x -2272..-2209, z -1376..-1313 (64x64) | y 112 |
| farmstead 12 | -273, -2865 | x -304..-241, z -2896..-2833 (64x64) | y 108 |
| farmstead 13 | -2753, -1057 | x -2784..-2721, z -1088..-1025 (64x64) | y 108 |
| farmstead 14 | -3793, -2849 | x -3824..-3761, z -2880..-2817 (64x64) | y 108 |
| farmstead 15 | -1825, -273 | x -1856..-1793, z -304..-241 (64x64) | y 95 |
| farmstead 16 | -529, -2641 | x -560..-497, z -2672..-2609 (64x64) | y 80 |
| farmstead 19 | -1185, -3745 | x -1216..-1153, z -3776..-3713 (64x64) | y 76 |
| farmstead 20 | -65, -2337 | x -96..-33, z -2368..-2305 (64x64) | y 86 |
| farmstead 22 | -2081, 591 | x -2112..-2049, z 560..623 (64x64) | y 112 |
| farmstead 23 | 191, -2401 | x 160..223, z -2432..-2369 (64x64) | y 112 |
| farmstead 24 | -721, -2401 | x -752..-689, z -2432..-2369 (64x64) | y 70 |
| farmstead 25 | -2481, -1153 | x -2512..-2449, z -1184..-1121 (64x64) | y 73 |
| farmstead 26 | -3777, -3713 | x -3808..-3745, z -3744..-3681 (64x64) | y 93 |
| farmstead 27 | -81, -2577 | x -112..-49, z -2608..-2545 (64x64) | y 72 |
| farmstead 29 | 671, -2353 | x 640..703, z -2384..-2321 (64x64) | y 72 |

## 2. Named areas

| Area | Extent | What it is |
|---|---|---|
| The town (Pripyat) | x -3750..-1800, z -3750..-1400 | the ruin field; the base map's own city, with no generated structures inside it |
| The plant | x -1150..1200, z -400..700 | the power station complex on the east side of the cell |
| The Woods | x -2450..-1600, z -1350..100 | standing forest between the desert city and Skadowsky |

## 3. The base map's own landmarks

These are the Pripyat pack's structures, not builds the project placed. The repo has never given them
names - that is open item F9 in the design-gaps document - so they are listed here by what they are
and where they stand, measured rather than named.

### The power station

| Structure | Centre (x, z) | Size | Roof y |
|---|---|---|---|
| Confinement hall over the reactor, west end of the turbine row | -642, 518 | 202 x 362 | 198 |
| Turbine hall, the long east-west building | 405, 590 | 837 x 88 | 122 |
| Reactor annexe on the turbine hall's north side | 539, 560 | 155 x 28 | 122 |
| Administration and workshop block | 88, 204 | 574 x 336 | 96 |
| Quartz-faced hall north of the turbine row | 168, 370 | 127 x 236 | 87 |
| Four identical low halls in a 2x2 (switchyard and storage bays) | -888, 167; -743, 167; -890, 54; -775, 54 | 134 x 34 each | 76 |
| Cooling-water intake works | 893, 156 | 573 x 514 | 77 |
| Chimney and stack line, west approach | -781, -86 | 39 x 73 | 87 |
| Perimeter fence, the long east-west run | 568, -112 | 1234 long | 91 |
| Plant road viaducts, west approach | -1125, -515 and -1180, -202 | 327 and 205 long | 76 and 74 |

### The town

| Structure | Centre (x, z) | Size | Roof y |
|---|---|---|---|
| Stadium, running track and grandstand | -2395, -3482 | 216 x 203 | 116 |
| Park with the radiating avenues and the roundabout | -2380, -2975 | about 320 x 260 | - |
| Tallest standing block | -2529, -2492 | 82 x 104 | 118 |
| Long slab block, north-west quarter | -2978, -2792 | 23 x 155 | 112 |
| Long slab block, west quarter | -3598, -2936 | 103 x 163 | 112 |
| Long slab block, north quarter | -2978, -3173 | 22 x 155 | 112 |
| Wide block, central | -2650, -2873 | 130 x 77 | 104 |
| Microdistrict blocks, the repeated 89 x 124 type | -2088, -1967; -1937, -2184; -2337, -1791 | 89 x 124 each | 93 |
| Courtyard blocks, the repeated 107 x 108 type | -2350, -2289; -2354, -2028 | 107 x 108 each | 94 |
| Rail bridge over the water, south approach | -904, -2202 | 44 x 302 | 65 |

## 4. Footprints that are no longer there

These rectangles were turned back into landscape during the v8 integration pass. Nothing stands at
them now. They are listed so the coordinates in older documents do not send anyone on a walk for
nothing.

| Former place | Centre (x, z) | Footprint |
|---|---|---|
| Settlement | -1145, -1873 | x -1280..-1009, z -2016..-1729 |
| farmstead 3 | -2305, 559 | x -2336..-2273, z 528..591 |
| farmstead 7 | 431, -2449 | x 400..463, z -2480..-2417 |
| farmstead 17 | -2753, -1281 | x -2784..-2721, z -1312..-1249 |
| farmstead 18 | -2049, -145 | x -2080..-2017, z -176..-113 |
| farmstead 21 | -2689, 207 | x -2720..-2657, z 176..239 |
| farmstead 28 | -785, -2721 | x -816..-753, z -2752..-2689 |
