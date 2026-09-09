# GSCraft Wasteland — the camp moves into Skadowsky

*Design doc, 2026-09-07. Owner's decision: the camp and its systems move into Skadowsky just past the
south-west bridge; the sector's own mast replaces the built radio tower; Skadowsky is the starting zone and
becomes the camp by being cleared. Medical stays inside the Skadowsky sector. Questing routes only to the
Pripyat base map, Skadowsky and KROT; the transplanted district and the far-bank builds are
deferred to a later quest line.*

*Every coordinate here was measured from the deployed world (census render `v8_cell_pass16`), not taken from an
earlier document. This doc supersedes design §2.2 (the camp), §7 (the radio tower), §2.6 (the Line) and the
strongpoint table of `gscraft-objectives-v8.md` §2. Section 10 lists every correction other documents need.*

*Re-verified 2026-09-07 against the region files themselves. Four figures in the first draft were wrong and have
been corrected in place: the bridge deck height and its clearance, the north complex's bed count, the shape of
the south complex, and the hospital's glass and bone counts. Everything else re-measured as written, including
the mast's whole column and the hospital roof at y 115.*

---

## 1. Why now, and what it costs

Nothing has been built. `tools/camp.py` was never written, and the plateau tower pad at x −1560…−1433 ×
z −2460…−2333 is bare ground at y 57 to 88. The only camp tooling that exists is `camp_ruins.py`,
`camp_torches.py`, `tower.py` and `theline.py`, none of which has been run against the world.

The cost of this change is therefore documentation, not construction. After Phase C it would have been 25
structure templates and 24 datapack functions.

## 2. The site, as measured

| Feature | Extent | Ground | Notes |
|---|---|---|---|
| The south-west bridge | x −1104…−981, deck z −957…−936 | y 89 deck | stone-brick masonry, iron railings, truss sides to y 94; water at y 53, so the deck stands 36 blocks above it; the only crossing on Skadowsky's west side |
| North complex | x −966…−898, z −1090…−1000 (69 × 91) | y 63 | stone and iron railings; **holds 24 beds already** (48 bed blocks, x −956…−933 × z −1033…−1006, y 63–71) |
| Paved junction | x −962…−918, z −996…−962 (45 × 35) | y 65 | stone, andesite and gravel; already hard surface |
| South complex | x −978…−922, z −900…−822 (57 × 79) | y 66 | two buildings, not one hall: a brick block 15 × 39 at x −938…−924 × z −869…−831, roof y 85, and a deepslate-trimmed structure west of it at x −971…−937 × z −893…−822 whose polished deepslate sits on the upper floors, y 74–84 |
| The pocket | x −978…−902, z −1000…−900 (77 × 101) | y 66 | river west, rail embankment east |
| The mast | −808, −1008 | y 66 | 71 blocks tall, tip y 137, aviation light on top |
| The mast's field | x −840…−770, z −1040…−960 (71 × 81) | y 62 | 78 % open grass, easy ground to wall |

The mast's own column, read from the world: yellow concrete from y 104, cobblestone wall at 121, spruce fence
at 125, iron bars at 132, an end rod at 137. It stands on a building whose roof is y 104.

**The pocket is a stronger defensive position than the plateau.** Water to the west with one bridge, a rail
embankment to the east, two solid building groups north and south. The plateau's selling point was the crater
as a one-ramp pit; this is a one-bridge isthmus.

## 3. The camp

**Perimeter:** x −978…−770, z −1060…−845 (209 × 216). That takes in the pocket, both building complexes, the
mast and its field, and crosses the rail embankment, whose level crossing becomes the east gate. It is about
half the plateau camp's 400 × 400, because the buildings already exist and do not need spacing out.

*(Corrected 2026-09-07. The first draft read z −1040…−900, which left Tony's clinic outside to the north and
Walker's yard and Michael's plant outside to the south — three of the eight rectangles below fell outside
their own perimeter. The box above is the bounding box of all eight, and it is 99.3 % dry: 308 water columns
of 45,144, all of them the river edge on the west.)*

**World spawn:** the paved junction, (−940, −979). It is already hard surface and it faces the bridge.

| Function | Where | Why there |
|---|---|---|
| Marshall — the gatehouse | the bridge's east end, x −978…−955 × z −955…−940 | every trip west crosses him, which is the role design §2.2 gives him |
| Tony — the clinic | the north complex, x −966…−930 × z −1060…−1020 | 24 beds are already in this building |
| Tune — the radio shack | the north complex's east end, x −925…−905 × z −1040…−1020 | nearest the mast, with line of sight to it |
| Walker — the yard | the south complex, x −975…−940 × z −880…−845 | the deepslate-trimmed structure gives a walled yard with standing floors |
| Michael — the plant | the south complex's east side, x −938…−910 × z −900…−870 | beside the yard, off the square |
| James — the lookout | the rail embankment's signal box, x −905…−897 × z −975…−967 | it already overlooks both approaches |
| The gun pit | the mast field's west edge, x −846…−835 × z −1000…−989 | fires east over 70 blocks of open grass |
| The tower compound | the mast's field, x −840…−770 × z −1040…−960 | the finale's fail rectangle |

The lock rectangles above are first cut and are for the visual pass to adjust, exactly as design §2.2's were.

**Neutral ground.** The Magnum Torches keep their job but not their count. Five cover the pocket at 64-block
radius; they do **not** cover the sector. That is deliberate and is the whole of section 5.

**`camp_ruins.py` is retired.** It exists only because the plateau had nothing to loot inside 300 m. Skadowsky
is a 464 × 752 town with a hospital, a station and a level crossing. Delete the tool, the 24 wrecks and
`gscraft:camp_ruins`.

## 4. The mast replaces the tower

The mast stands. It is dead: no power, no feed, no array, and its lattice is cut where it was salvaged.

The five tower stages survive unchanged in count, gating and reward, because a dead mast still needs everything
stages 2 to 5 add. Only stage 1's fiction changes.

| Stage | Was | Is |
|---|---|---|
| 0 | ruined plinth, leg stubs, wrecked hall | the standing mast, dead; the hall at its foot derelict; the cut lattice section |
| 1 | erect the lattice mast to 64 | **repair the cut section so the mast can be climbed** — same Mast section kit, same quest X2, same gate |
| 2–5 | cooling, generator, transmitter, array | unchanged |

`tools/tower.py` keeps its six templates but changes origin from (−1517, −2417) to the mast's foot, and stage 1
becomes a repair patch rather than a 64-block mast. Stage 5 still lights the beacon and still starts the
countdown.

**The finale.** `gscraft-finale.md` §4's fail check — five or more attackers inside the tower compound for 30
seconds — now reads on x −840…−770 × z −1040…−960. Because the perimeter in §3 takes the mast in, this stays a
single defended box and the team is not split between a gate and a mast 144 m away.

## 5. Clearing Skadowsky is Act I

The best part of this change is that the starting location becomes the home base by player action instead of
being handed over.

At the start the team holds the pocket and nothing else. The torches suppress spawns inside 64 blocks of the
square; the rest of Skadowsky is hostile and is where the loot is. The players are squatting in their own town.

The existing site ladder (design §6.1) runs the clearance without modification, but it pays out **perimeter**
rather than a keeper:

| Rung | Stage | What it gives |
|---|---|---|
| scouted | `skadowsky_scouted` | the sector's dossier; the board's Skadowsky column lights |
| looted | `skadowsky_looted` | normal loot runs, north through the town |
| **held** | `skadowsky_held` | spawn suppression extends to the whole sector; the mast's field becomes camp ground; NPC buildings unlock tier 2 |
| defended | `skadowsky_defended` | the first counterattack, fought at the bridge; the sector is safe for good |

Keep this axis separate from the NPC building tiers, which run 0 to 3 across all four acts. **Clearance grows
the perimeter; quests improve the interior.** Both run at once and neither gates the other.

**Approaches for the counterattacks:** the bridge from the west, the main road east, and the rail corridor
north and south. Three, the same count the plateau had, but the west approach is a single 8-block deck.

## 6. Medical stays in Skadowsky

The sector is 464 × 752, which is room enough for the camp and a strongpoint that is not the camp.

**The medical strongpoint is the hospital at x −865…−698 × z −1312…−1242** (168 × 71, roof y 115, ground y 64).
It was identified from the world, not guessed: it holds **372 of the sector's 425 white stained glass blocks**
and **935 of its 1,785 bone blocks**, which read as the morgue and the mass grave of a quarantine that failed.
(An earlier draft of this table read 144 and 1,785 for the building; the second figure was the whole sector's
count, and the sector has white stained glass in one other place, so "the only building with it" was wrong.)

It is 363 m due north of the camp square, so Act I is a walk north through your own town to the building at the
end of it. Tony's chain and keeper Vera move here unchanged. `residential_*` stages should be renamed
`hospital_*` to stop the sector and the strongpoint sharing a name.

## 7. The routing rule

**Quests and gameplay route only to the Pripyat base map, the Skadowsky sector, and KROT.**
KROT is included for theming and is work in progress. Everything else transplanted is
deferred to a later quest line and no quest in this design may point at it.

| In scope | Why |
|---|---|
| The Skadowsky sector | the camp, the hospital, the station, the rail yard, the level crossing |
| The town (Pripyat) | the ruin field and its landmarks: the stadium (−2395, −3482), the park (−2380, −2975), the tallest block (−2529, −2492), the microdistricts |
| The plant complex (Pripyat) | the confinement hall (−642, 518, roof y 198), the turbine hall (405, 590, 837 long), the switchyard halls (−888/−743/−890/−775 at z 167 and 54), the intake works (893, 156) |
| The rail line and yard | the east-bank spine |
| The collective farm and the Woods | the fields south of the town, the forest |
| KROT | x −3392…−3073 × z −1344…−1025, the one walled holdout across the river |

| Deferred to a later quest line | Was |
|---|---|
| Novo Expograd Industrial Zone | Walker's strongpoint |
| Financial Plaza and the sewers | Tune's strongpoint |
| Bio Gen offices | an Act II loot site |
| The desert city hub | the Act IV prize |
| The mega-base, FR-06 | Michael's power strongpoint |
| The industrial district, "the waterworks" | Michael's fuel-and-water strongpoint |

The library (a transplant) and the runway (an unbuilt project pad) are deferred with the district; §11.1.

## 8. What this does to the act structure

Two measured facts drive this section.

**The plant complex is on Skadowsky's own bank.** A straight line from the camp to the confinement hall crosses
no water at all; the switchyard, turbine hall and intake works cross only narrow marsh channels. Everything
west — the settlement, the town, the collective farm, KROT — crosses the river.

So the banks swap. The home bank is now the **east** bank, running from your town south to the power station it
served. The bridge is the way out to everything else. That is the Pripyat story told the right way round.

**The distance ordering inverts against the old camp.**

| Objective | From the plateau | From the camp square |
|---|---|---|
| the hospital (medical) | — | 0.34 km |
| the collective farm | — | 1.17 km |
| the plant switchyard | — | 1.09 km |
| the town's east avenue | 0.47 km | 1.52 km |
| the plant confinement hall | — | 1.53 km |
| the plant turbine hall | — | 2.06 km |
| the plant intake works | 2.15 km | 2.16 km |
| KROT | 2.16 km | 2.30 km |
| the town centre (the central square, −2380, −2975) | 1.36 km | 2.46 km |
| the runway (deferred) | 1.54 km | 2.85 km |
| the library (deferred) | 1.88 km | 3.16 km |

*(Re-measured 2026-09-07 from the world spawn at the paved junction, (−940, −979). The first draft's
right-hand column was a few tens of metres out because it never named its anchor, and its settlement row
has been replaced by the collective farm: the settlement sector is group `removed` and the ground there is
bare grass.)*

This matters less than it looks. `gscraft-objectives-v8.md` §6 already abandoned distance as the act gate:
every site but Skadowsky sat 2.0 to 2.4 km from the plateau, the Improved Mobs rings could not separate the
acts, and difficulty was moved onto the land. Under land gating the shape holds.

**Proposed act shape** (§9 has the calls this still needs):

| Act | Where | Gate |
|---|---|---|
| I — the town you woke in | the pocket, then north to the hospital | on foot, inside the sector |
| II — the line south, and the first crossing | the rail line and road down the east bank to the plant's outer works; west over the bridge to the collective farm and KROT | the first vehicle |
| III — the station | the plant complex proper: turbine hall, intake works | the truck, the marsh channels |
| IV — the reactor | the confinement hall, and the town across the river | air, or the bridge road |

**The five strongpoints, re-homed inside the scope:**

| Role | NPC | Site | Straight from camp |
|---|---|---|---|
| Medical | Tony | the Skadowsky hospital | 0.36 km |
| Electronics | Tune | the plant's switchyard and admin block | 1.06 km |
| Power | Michael | the plant's turbine hall | 2.04 km |
| Fuel and water | Michael | the plant's cooling intake works | 2.14 km |
| Heavy industry | Walker | KROT | 2.31 km |

The tower's five parts follow the same order: mast repair from Skadowsky, transmitter from the switchyard,
generator from the turbine hall, cooling loop from the intake works, array from the confinement hall, with the
reactor control module still the gatehouse tier 3's input from the reactor block.

## 9. The decisions this raised (all closed in §11)

1. **The runway and the library.** Both are outside the Pripyat base map — the library is a transplant, the
   runway an unbuilt pad. From Skadowsky they are the two furthest things on the map at 2.88 and 3.18 km. Keep
   them in scope, or defer them with the district? If deferred, Act IV loses the aircraft and the plant is
   reached by road.
2. **The Line.** Its six stops and quests L1 to L6 were the walking route from the plateau to Skadowsky. That
   route no longer exists. Re-cut the corridor westward from the bridge to the settlement, or retire it and
   give L1 to L6 to the rail line south?
3. **Act II's vehicle.** With the plant on the same bank the car may not be needed until Act III. Confirm or
   move the garage chain.
4. **Strongpoint count.** Three of the five now sit inside the plant complex. Acceptable, or should one move to
   the town or the rail yard for variety?

## 10. Corrections other documents need

Nothing below has been applied. This is the list a future session must work through before treating any other
document as current.

| Document | What is now wrong |
|---|---|
| `gscraft-map-design.md` §2.2 | the entire camp section: the plateau box x −1690…−1290 × z −2480…−2080, the crater, the six building positions, the ten torches, the camp ruins, the world spawn (−1490, −2230) |
| `gscraft-map-design.md` §2.6 | the Line runs from the plateau's south-east gate to Skadowsky's north edge; that gate no longer exists |
| `gscraft-map-design.md` §7 | the tower's origin (−1517, −2417), the pad x −1560…−1433 × z −2460…−2333, and stage 1 erecting the mast |
| `gscraft-map-design.md` §6.1, §6.2 | "every counterattack comes to the camp gate" still holds, but the gate is the bridge; the `<site>_lost` check reads the plaza rectangle x −1522…−1459 × z −2262…−2199 |
| `gscraft-objectives-v8.md` §0, §1, §2, §5 | the three lands (the home bank is now east), every distance in the table, the act table, the five strongpoints, the crossings list |
| `gscraft-quests.md` §7.3, §7.5, T3–T6, T-B2, J-S2, R2, R3, L6, G5, S-residential-1…3, J-T1 | every quest that names Skadowsky as the strongpoint or the plateau as the camp |
| `gscraft-camp-spec.md` | `pads_camp.json`, the 24 NPC templates, the board wall, the parts rack, the runway lights, `camp_ruins` |
| `gscraft-finale.md` §3, §4 | the sculk ring at the plateau compound x −1560…−1433 × z −2460…−2333; the fail rectangle |
| `gscraft-onboarding.md` | the opening walk, the first ruins, "Where things are" |
| `gscraft-enemies.md`, `gscraft-entities-v8.md` | the counterattack entry points and the In Control area definitions, which key off the plateau |
| `buildmap/plan_v8/sectors_v8.json` | the `camp` sector rectangle x −1792…−1409, z −2492…−2109 (annotated 2026-09-07) |
| `tools/camp_torches.py`, `tools/camp_ruins.py`, `tools/tower.py`, `tools/theline.py`, `tools/pads_camp.json` | all keyed to the plateau |

**A standing discrepancy this doc does not fix.** Design §2.2 says the camp box is x −1690…−1290 ×
z −2480…−2080 and that plan §4's sector row, x −1792…−1409 × z −2492…−2109, is the one to correct. Both are now
obsolete, but any future session reading either will find two different plateau camps and no note that neither
is live. That is what §10 exists to prevent.

## 11. Decisions settled, 2026-09-07

Section 9 listed four calls and the gaps ledger carried one more. All five are closed here. Nothing in
this design is now waiting on a decision; what remains is build work, and §12 says which is which.

### 11.1 The runway and the library are deferred with the district

Both fall outside the routing rule: the library is a transplanted compound and the runway is a project
pad that was never built. From Skadowsky they are also the two furthest things on the map, at 2.88 and
3.18 km.

**The aircraft becomes rotary and the runway is not needed.** Three things make this the cheap answer
rather than a loss. The plant complex sits on Skadowsky's own bank, so the lake crossing the fixed-wing
plan existed to serve is gone. The pack's vehicle stock after the 2026-09-06 swap is overwhelmingly
helicopters, all verified present in the shipped jars: `dragonrise_reforge:uh60`, `fcp:huey` with its
three gunship variants (`huey_rockets`, `huey_door_gunner_m60`, `huey_door_gunner_m134`), `fcp:mi17`,
`fcp:venom` and `fcp:viper`. And a helicopter lifts from the mast field inside the camp perimeter, so
Act IV needs no airfield at all.

`runway_lights` and the runway pad are retired with `camp_ruins`. W-B3 keeps the UH-60 as written.

### 11.2 The Line is re-cut west to the collective farm

Its old route, the plateau to Skadowsky, no longer exists at either end, and its old destination is gone
twice over: the settlement sector is group `removed` and the ground there is 91 % grass.

**The Line now runs west over the bridge to the collective farm** at (−2112, −896), 1.17 km. The six
stops and quests L1 to L6 keep their owners and their shapes; only the direction reverses. The fit is
better than the original: L1 is already Tony's seeds and herbs, and D3 and D5 are already the farm's
kit, seeds and crops, so three of the corridor's quests were pointing at this destination anyway. L6's
switching station becomes the farm's own substation at the west end, and clearing it opens the farm
rather than the block.

The corridor stays deliberately empty between stops, as design §2.6 requires, and the pylons now lead
away from home instead of toward it, which is the right shape for Act II.

### 11.3 The car stays in Act II

Act II runs west over the bridge to the farm and the town, and south down the east bank to the plant's
outer works. The town centre is 2.46 km and the town's east avenue 1.52 km. That is a car's range and
not a walk, so Walker's garage chain keeps its act. No change.

### 11.4 Three strongpoints in the plant complex is correct

The concern was that three of the five sit in one place. Measured, they do not: the plant complex is a
2.3 by 1.1 km industrial landscape and its three sites are as far apart as the old district's were.

| From | To | Distance |
|---|---|---|
| switchyard | turbine hall | 1.31 km |
| turbine hall | intake works | 0.66 km |
| switchyard | intake works | 1.71 km |

Each is also thematically exact rather than assigned by convenience, which the old district placements
were not: the switchyard is relays and transformers, the turbine hall is generators, the intake works is
cooling water.

**The five strongpoints are settled as:**

| Role | NPC | Keeper | Site | Centre | Straight from camp | Act |
|---|---|---|---|---|---|---|
| Medical | Tony | Vera | the Skadowsky hospital | −782, −1277 | 0.36 km | I |
| Electronics | Tune | Ilya | the plant's switchyard and admin block | −815, 105 | 1.06 km | III |
| Power | Michael | Rook | the plant's turbine hall | 400, 590 | 2.04 km | III |
| Fuel and water | Michael | Oksana | the plant's cooling intake works | 895, 155 | 2.14 km | III |
| Heavy industry | Walker | Kessler | KROT | −3233, −1185 | 2.31 km | II |

The confinement hall at (−642, 518), roof y 198, is **not** a strongpoint. It is Act IV's prize: the
reactor control module for the gatehouse tier 3 and the antenna array for tower stage 5. That keeps the
map's largest ruin as the finale's source rather than one more take.

The tower's five parts come from the sites in this order: the mast repair from Skadowsky, the transmitter
from the switchyard, the generator kit from the turbine hall, the cooling loop from the intake works, and
the array from the confinement hall.

Note that this is the order the parts are *found* in, not the order the stages are *installed* in: section
4 keeps stages 2 to 5 as cooling, generator, transmitter, array. The two do not run in step, and they do
not need to, because all three plant sites belong to Act III and a part can sit in the rack until its
stage comes up.

### 11.5 Gunpowder's source (gaps ledger F11)

The stone complex that held it is gone from the v8 map. Gunpowder now comes from **the town's military
chests and the plant complex's four storage halls** at (−888, 167), (−743, 167), (−890, 54) and
(−775, 54). Both are in scope under §7, both are already loot-table locations, and neither needs a
building invented for it. Teddy's H8 propellants are unaffected.

## 12. What is left, and it is not design

| Item | Kind |
|---|---|
| Gaps ledger F9 — the map and dressing session: NPC rectangles walked and adjusted, the town's landmark buildings picked from the measured candidates, the road signs | build task |
| Gaps ledger F10 — the Phase C config wins from the mod audit | build task |
| Design §10's small list — the claim-marker anchor points, the base-upgrade recipe sheet, the camp templates | build task |
| The client designer-tool kit (HANDOFF) | owner preference, no design depends on it |

The town's landmark roles have a selection rule rather than a pending decision: pick from the measured
building stock by shape. The palace of culture is the broad civic block at (−2650, −2889), 131 × 114 in
grey concrete rather than the blackstone of the housing. The tallest block is any of the 4,044 columns
standing at y 118 or above; the town has no single tallest building and does not need one. The central
square is the park with the radiating avenues at (−2380, −2975). The four microdistricts are the
repeated 89 × 124 and 107 × 108 blocks at (−2088, −1967), (−1937, −2184), (−2337, −1791) and
(−2350, −2289). The stadium is at (−2395, −3482).

**A check that runs.** `tools/checkdocs.py` fails if a live design document asserts a plateau camp
coordinate, names MCSP or the Vintage Vehicle Pack without saying what replaced it, or quotes a
`fcp:`, `dragonrise_reforge:` or `superbwarfare:` id that is not in the jar the server actually ships.
That last check exists because this document asserted two helicopter ids that did not exist until it
caught them. Dated audit snapshots and the v6 documents are exempt and carry a banner instead. Run it
after any doc edit: it reads 25 live documents and currently clears 70 assertions.
