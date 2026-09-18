# GSCraft Wasteland — the start moves into Skadowsky's south compound

*Design doc, 2026-09-12. Owner's decision: "update the starting area to be within the southern walled off compound
of Skadowsky, and set the player spawns there by default." This is a design change only; nothing on either server
has been touched. It supersedes `gscraft-skadowsky-camp.md` §3 (the world spawn, the perimeter as the start),
`gscraft-onboarding.md` §2 (the opening), and the "camp pocket" rows of `gscraft-entities-v8.md` §4 and
`gscraft-objectives-v8.md` §0. Section 8 lists what other documents need.*

*Every coordinate was read from the local copy of the deployed world (`G:/GSCraft/server/wasteland-v8`, the v8
region files) with the census tools, not taken from an earlier document.*

---

## 1. The decision in one paragraph

The team no longer starts holding the whole pocket. It starts inside the **south compound** — the walled yard and
hall at the pocket's south end, Walker's yard in the old design — and holds nothing else. The paved junction, the
bridge gatehouse, the north complex with its 24 beds, the signal box and the mast's field are all outside the walls
and are Act I's first ground: each is taken, and a survivor moves into it, before the pocket is the camp the old
design started with. The world spawn moves from the junction to the yard.

Why it is better: the old start handed the players a 209 × 216 perimeter with six lit buildings and asked them to
feel besieged. A compound of one yard and one hall with a gap in its wall makes the first hour a real thing to do —
close the gap, take the square, get the clinic — and it puts the design's own principle ("clearance grows the
perimeter; quests improve the interior") into the first ten minutes instead of session two. It also fits the new
enemy layer: squads and armour roll on the roads and fronts around Skadowsky now, and a start with walls is the
only start that survives them (§6).

## 2. The compound, as measured

The south complex is not one walled box. It is a yard closed on three sides and open on the fourth, which is the
whole design opportunity.

| Feature | Extent | Ground | What it is |
|---|---|---|---|
| **The yard** | x −972…−938, z −895…−858 (35 × 38) | y 64 (andesite, diorite, gravel — hard surface) | open paving with a row of low sheds along its west wall (x −971…−958 at z −895…−891 and z −885…−883, roofs y 70) and a few props (benches, a car at x −950…−948 × z −880…−878, y 65–68) |
| **The west wall and quays** | x −973, z −895…−857 | y 65–69 solid | a full-height wall; behind it the river quays at x −980…−974 stand over water at y 53 — nothing walks in from the west |
| **The hall** | x −979…−937, z −858…−834; roofs y 74–78 at x −967…−959, y 79–84 at x −958…−937; a raised deck at x −978…−968 (y 69–70) | y 64 | the deepslate-trimmed structure: the compound's south side and its only interior; the "standing floors" of the old yard design |
| **The hall's annex** | x −960…−937, z −834…−820 | — | the southern extension; the compound's back |
| **The brick block** | x −938…−924, z −869…−831, roof y 85 | y 64 | Michael's plant in the old ring; its west face (x −936) closes the yard's east side south of z −870 |
| **The gap** | z −895 from x −959 to −938 (the north edge east of the sheds), and x −937 from z −895 to −870 (the east edge north of the brick block): an L of about 47 blocks with a few posts in it | y 64 | **open**. Paving runs straight out of it north-east to the junction. This is the gate the players build. |

So the compound is: river and wall to the west, the hall to the south, the brick block to the south-east, sheds to
the north-west, and one open corner to the north-east. The rail embankment is 35 blocks further east across grass
(x −917 and beyond), which is why the east edge was never walled: the town's own street ran through here.

**Compound box for the systems:** x −980…−920, z −897…−818 (61 × 80). That takes in the quays, the yard, the hall,
the annex and the brick block, and stops short of the embankment.

## 3. The world spawn

**(−956, 65, −876)**, in the middle of the yard on andesite at y 64, with air to y 69 and more above. It faces
north-east, at the gap. `spawnRadius` 4 keeps every fresh spawn inside the paving (the vanilla default of 10 would
put some players on the shed roofs or in the hall). The old spawn at the junction is 104 m away, in sight through
the gap.

**A finding on the way:** the world's `level.dat` still carries the pack's original spawn, **(−2555, 80, −2539)** in
the town, on the far bank. The 2026-09-07 decision to put it on the junction was written into four documents and
never applied to the world. The local copy is what was read; the live world is the same v8 build and should be
checked, not assumed. The onboarding gear script and Improved Mobs' distance curve both key off the world spawn, so
until it is set, anyone who has not slept spawns 2.5 km from the camp.

**How it is set (for the deploy session, not this one):** `/setworldspawn -956 65 -876` and `/gamerule spawnRadius
4` on the console. Both are commands, not world files: they change `level.dat` in place on the running server and
need no upload, so the world-deploy rule does not come into it. Players who already have a bed keep it.

## 4. What the start holds, and what it does not

| Inside the walls at 0:00 | Outside, to be taken |
|---|---|
| the yard, the hall, the annex, the brick block | the paved junction, 104 m (the old spawn) |
| **Walker** (the yard is his) and **Michael** (the brick block is his plant) | **Marshall's gatehouse** at the bridge's east end, 74 m |
| the players' first stations, set down inside the wire | **Tony's clinic** in the north complex with the 24 beds, 150 m |
| two Magnum Torches: `yard` at (−957, 66, −862) stays; one new at the gap's inside corner, about (−945, 65, −890) | **Tune's shack** at the north complex's east end, 160 m |
| the quest book, the notebook, the map wall (moved from the square to the hall's ground floor) | **James's signal box** on the embankment, 112 m |
| | the gun pit and **the mast's field**, 165–200 m |
| | the hospital, 438 m |

> **2026-09-13 (owner: every survivor inside the south compound):** all six start inside the walls - Marshall on the hall's floor by the board, Tony in the sheds, Tune in the annex, James at the gap (`tools/camp.py` START); the four still move out to their buildings when the site loop takes those (gatehouse, north, crossing).

Walker and Michael are the two survivors whose buildings the compound already is; the other four are met where they
are found. That changes nothing in their chains (quests §2–§7) except the order the first-time lines come in.

**The torches.** The five of the old design covered the pocket at 64 blocks. Now two cover the compound and the other
three light when their building is taken: `gatehouse` with Marshall's, `clinic` with Tony's, `crossing` with James's,
and `square` with the junction. A torch is placed by the same datapack function that moves the survivor in.

## 5. Act I re-cut: the pocket is taken building by building

The site ladder is unchanged (scouted, looted, held, defended). What changes is that **the pocket itself is the
first site**, and it is taken in pieces rather than as one rung, so the first hour has five visible wins:

| Step | Where | What the players do | What it pays |
|---|---|---|---|
| 0 | the compound | set stations; Walker's and Michael's introductions from the hall's and the block's own rooms | the loop |
| 1 | **the gap** | Marshall's first ask, moved from the parts rack: close the corner with sandbags and a gate (W-kit items already in crafting §4) | `compound_closed`: the gap is a gate; the torch at the corner lights; the counterattack rule (§6) arms |
| 2 | **the junction** | clear the square and the streets off it; first Lootr rooms | `square_taken`: the `square` torch; the map wall reveals; the board lights Skadowsky *unknown* |
| 3 | **the gatehouse** | the bridge's east end: Marshall moves in | `gatehouse_taken`: the `gatehouse` torch; the west gate exists; every trip west crosses him |
| 4 | **the north complex** | the clinic (Tony, 24 beds) and the shack (Tune) | `clinic_taken`: the `clinic` torch; beds; Radio 1 |
| 5 | **the signal box and the crossing** | James | `crossing_taken`: the `crossing` torch; the east gate; J1's first walk out |
| 6 | the mast's field | the gun pit; the mast, dead | camp ground; `skadowsky_held` when the sector's clearance rung is reached |

Each "taken" is the existing held-site mechanism at building scale: a small rectangle, a marker, the occupiers gone,
the survivor's summon function and the torch. No new system. The onboarding's minute-by-minute (§2 of that doc)
keeps its beats and its lines; the places move: 0:00 is the yard, 0:02 is the hall and the gap, 0:25's first hand-in
is Walker in his own yard, and the first walk out is to the square rather than past it.

The rest of Act I is as before: north through the town to the hospital.

## 6. Why the walls matter now: squads and armour at the door

This is the part the old start could not survive. Since 2026-09-10 the enemy layer places NATO and RUAF squads by
zone with garrisons, patrols and hearing, and since 2026-09-11 it places armour on the roads. Read against the new
spawn:

| Zone (map.json) | Box | Nearest edge to the yard | What it rolls |
|---|---|---|---|
| `front_en` (NATO front, north) | x −995…−880, z −1250…−700 | **0 m — the compound is inside it** | ambient soldiers, **armour 0.06** |
| `farbank` | x −1050…−600, z −1000…−380 | 0 m | ambient, armour 0.04 |
| `sk_south` | x −980…−660, z −1000…−760 | 0 m | the Dead, Scavengers |
| `front_wn` (RUAF front, north) | x −1290…−1100, z −1250…−700 | 144 m (across the river) | ambient, armour 0.06 |
| `sk_out_e` (rail yard outpost) | x −768…−640, z −1000…−820 | 188 m | NATO garrison 3 |
| `out_e1` | x −900…−780, z −600…−480 | 282 m | NATO garrison 4, armour |
| `sk_out_w` (RUAF post) | x −784…−720, z −1148…−1100 | 282 m | RUAF garrison 3 |
| `out_e2` | x −700…−580, z −1150…−1030 | 299 m | NATO garrison 4, armour |

The `camp` exclusion (x −978…−770 × z −1060…−845) stops placement inside the pocket, but an armour roll is placed 96
to 140 blocks from a player on a road stand, and the road east of the embankment and the bridge road are both inside
that ring from the yard. A fresh team can therefore hear a Bradley on its first night. **Ruled 2026-09-12 (owner): that is fine.** The
front stays as mapped; the walls are what a fresh team has, and an early tank is something to hide from.

**Rules this asks for (the system pass, `gscraft-system-design-pass-2026-09-12.md` §5, has the whole set):**

1. *(No armour gate near the start — rejected by the owner, 2026-09-12; the rolls stand.)*
2. **The compound gate is the counterattack's target.** Design §6.2's rule stands — every counterattack comes to
   the base, never the site — and "the base" is now the compound: the wave's target point is the gap, (−948, −893),
   and the approaches are the ones the pocket already has (the bridge from the west, the road east over the
   crossing, the rail corridor north and south), 48 blocks outside the compound box. A wave that reaches the gate
   is fought in a 23-block opening with walls either side; that is a defensible thing, which the old 200 m
   perimeter never was.
3. **The finale stays at the mast.** By Act IV the mast's field is camp ground and the fail rectangle
   (x −840…−770 × z −1040…−960) is unchanged; the compound is where the team retreats to if it falls.

## 7. The distances, re-measured from the yard

Straight lines from (−956, −876). Road figures remain unmeasured, as before.

| Objective | Straight | Was (from the junction) |
|---|---|---|
| the bridge's east end (Marshall) | 74 m | 45 m |
| the paved junction | 104 m | 0 |
| the level crossing (the east gate) | 112 m | — |
| the gun pit | 165 m | — |
| the mast | 198 m | 135 m |
| the rail yard outpost `sk_out_e` (centre) | 254 m | — |
| the RUAF post `sk_out_w` (centre) | 321 m | — |
| the hospital (centre) | 438 m | 340 m |
| the plant switchyard | 991 m | 1,090 m |
| the collective farm | 1,156 m | 1,170 m |
| the confinement hall | 1,429 m | 1,530 m |
| the turbine hall | 1,997 m | 2,060 m |
| the intake works | 2,119 m | 2,160 m |
| KROT (centre) | 2,297 m | 2,300 m |
| the town's central square | 2,536 m | 2,460 m |

Nothing changes act. The plant gets 100 m nearer, the hospital 100 m further; both are noise against the land gating.

## 8. Corrections other documents need

**Applied 2026-09-12 (plan step 1):** every row below is done - the documents carry dated in-place corrections, `camp.json` has the compound box and the gate, `map.json` the six `camp_*` boxes by stage, `camp_torches.json` two at the start and four by stage, `sectors_v8.json` a `compound` rectangle, and the local world's spawn is set by console (live's at the step 5 window).

| Document | What is now wrong |
|---|---|
| `gscraft-skadowsky-camp.md` §3 | the world spawn; "at the start the team holds the pocket" (§5) — it holds the compound; the torch count and job |
| `gscraft-onboarding.md` §2 | 0:00 on the junction; 0:02's six lit buildings; the map wall on the square |
| `gscraft-entities-v8.md` §4 | the **home** row's "nothing inside the camp outline" — the outline is the compound until the buildings are taken |
| `gscraft-objectives-v8.md` §0, §1 | the distance table's anchor; Act I's first line |
| `gscraft-quests.md` §7, §8 | Marshall's first ask (the gap), the map wall's reveal (R1) on `square_taken`, Act I's opening paragraph |
| `gscraft-finale.md` | unchanged in substance; add that the compound is the fall-back |
| `gscraft_sites/camp.json` | `square` becomes the compound box; the approaches' target is the gap |
| `gscraft_zones/map.json` | the `camp` exclusion shrinks to the compound box at the start and grows by stage (a zone with a `stage` gate — a new field) |
| `tools/camp_torches.json` | two torches at the start, three by stage |
| `buildmap/plan_v8/sectors_v8.json` | a `compound` rectangle |
| level.dat, both worlds | the spawn (§3) — a console command at the deploy |

Supersession notes were added at the top of `gscraft-skadowsky-camp.md` and `gscraft-onboarding.md` pointing here.

## 6. The start moves again: the walled compound (owner, 2026-09-17)

> Owner: "update where the main compound is, correct it to the walled compound around (-900, -920) and (-720, -835). Not
> where it's corrected to." The south yard and hall of §2 were the wrong place. Everything §2–§5 fixed to the south
> compound now points here; §2's measurements stay as the record of what was built first.

**The compound, as measured** (scratchpad surveys from the world's regions, 2026-09-17): the owner's rectangle
x −900…−720, z −920…−835 is the bounding box of a walled enclosure.

| Part | Where | Floor (block y; stand +1) | Notes |
|---|---|---|---|
| The north wall | along z −912, x −896…−738, bone block with bars and fences; the railway fence runs along z −919/−917 outside it | — | **the north gate**: the one opening, where the road enters, x −835…−830 |
| The west wall | x −896, z −912…−843 | — | the river side beyond |
| The south wall | z −836 in the west (x −896…−883), then a wall running east from about (−855, −868) to (−770, −850) | — | the compound is a pentagon, not the box |
| The east wall | x −728, z −908…−877 | — | the brick works straddle it |
| **The big hall** | x −787…−750, z −903…−874; roof y 87 | 70 | pillars and windows inside: no flat wall long enough for the board |
| **The yard** | the paving west of the hall, x −840…−820, z −906…−880; the road x −840…−826 runs north–south through it to the gate | 70 | the start |
| The gate shed | x −844…−836, z −911…−904 | 70 | beside the gate, west of the road |
| The annex | x −792…−774, z −884…−874 | 70 | south of the hall |
| The brick works | x −746…−730, z −905…−872 (the building runs on to x −705, outside the wall) | 70–72 | Michael's |
| A raised stone stand | x −826…−814, z −901…−893, y 71–75 | — | between the yard and the hall |

**The layout** (`tools/camp.py`, `tools/camp_torches.py`, `tools/board.py`, `tools/chests.py`; the world functions
`camp_npcs`, `camp_torches`, `yard_mortar`, `board_place`):

| Thing | Where | Rule |
|---|---|---|
| World spawn | **(−829, 71, −893)**, `spawnRadius` 4 | the yard, looking west at the board |
| The board | free-standing at (−834, 71, −899) along +z, facing east | no wall in the hall fit it (`board.py` `free_standing`, `FREE`): its own concrete rows are the wall |
| Walker | the yard's south end, (−832, 71, −883) | `camp_npc_walker`, his building is the yard itself |
| Michael | the brick works, (−741, 72, −890) | `camp_npc_michael` |
| Marshall (start) | the hall's floor, (−769, 71, −889) | `camp_start_marshall`; the gatehouse when it is taken |
| Tony (start) | the annex, (−788, 71, −879) | `camp_start_tony`; the clinic when the north complex is taken |
| Tune (start) | the gate shed's door, (−836, 71, −904) | `camp_start_tune`; the shack when the north complex is taken |
| James (start) | the road inside the gate, (−832, 71, −900) | `camp_start_james`; the signal box when the crossing is taken |
| Torches | `yard` (−838, 72, −895); `gap` (−826, 72, −904), just inside the gate east of the road | `camp_torches` at the deploy |
| The mortar | (−826, 71, −881), the yard's south-east | `yard_mortar` (Marshall's The tube); it also clears the old tube |
| Lootr chests | the hall 8 (workshop), the brick works 6 (garage), the gate shed 3 (office), the annex 4 (apartment) | `chests.py --place` |

**The systems' box** is the owner's rectangle: zone `camp_compound` [−900, −720, −920, −835] (the zone boxes are x0, x1, z0, z1) (excluded, margin 32), the
camp site's `square` (the loss check), the quests' compound box. The square (the paved junction, x −966…−914,
z −1000…−958) is now north-west of the compound across the rails; its quest text says so. R0 "The gap" became **"The
north gate"** (`compound_closed`: the gate barred with sandbags). Tune's three join lines and the wake page describe this
compound. The old south compound keeps its two torches (spawn-free ground behind the players) and its old board on the
old hall's wall (static now); the old survivors, mortar and spawn are gone.

