# GSCraft Wasteland — Map and Systems Design

Draft 6, 2026-09-03. **This is the version the systems build (Phase C onward) is made from;**
the world build was made from draft 5 and is unchanged by this draft.
One build, one border; everything with a plan behind it is in it; seasons stay a future idea.

**Decision log (owner):** draft 3 — strongpoints are player-built structures, radio tower custom;
medical at the residential block, Bio Gen a loot site; sewers are dungeons; water pad re-cut; air
ring expedition-only; tower second-closest; vehicle speeds as shipped; no custom mod. Draft 4 — item
catalogue, bulky rule, storage as a base function, the five tower recipes, crafting at the IE
workbench with blueprints: all accepted. Draft 5 — the contacts are **NPCs living in the starting
area, each with a building**: Walker the Foreman, Tony the Medic, Michael the Engineer, Tune the
Technician, James the Scout, and Marshall, who opens the tower questline once each of the five has had
their starting tasks done. Draft 6 — **each NPC's building has three tiers**, one upgrade quest
each, every tier a visible rebuild of their site (§3.6); and **every strongpoint is visited
several times before it is taken**: scouted, looted on two or three trips, then cleared in one assault that the players start
by placing the marker; holding it starts that site's own defence countdown to a first attack that
always comes; **attacks only ever target the site being contested** — a defended site is safe for
good, there is no random cycle, and the loop quests run R2 → R6 in order up to every site held; a
site is lost when its marker falls or nobody is there at the end of its defence, never on one
death.

**Draft 6 addendum (owner, 2026-09-04):** the complicated military vehicles (Humvee RWS, UH-60 Black Hawk, M3A3
Bradley) are **blueprint-gated quest rewards, mid and late game** - W-M1 in Act III, W-B3 and X6 in Act IV - never
unlocked by a yard tier alone (`gscraft-crafting.md` §2.1, `gscraft-quests.md`).

**Onboarding (2026-09-04):** how all of this is taught in play rather than read - `gscraft-onboarding.md`.

**Vendors (owner, 2026-09-04):** the six NPCs are also traders — consumables as a floor, guns and gear as a priced
shortcut, loot buy-back as a sink, access by building tier and quest stage, on vanilla merchant offers - `gscraft-vendors.md`.

---

## 1. The game in one paragraph

Five players wake in a crater camp run by six survivors. Around them is a Lost Cities wasteland with a
custom-built district two kilometres east and five player-built strongpoints scattered between 1
and 2.5 km. Every ruin is full of small useful junk; the camp's NPCs teach the players to turn it into
parts at the stations and to grow their own hideout. Taking a strongpoint starts a clock; holding it
means beating the one attack that follows, after which the site is yours for good; each strongpoint yields one
complex component nothing can craft. Four of those and the hub's, built into five complete parts, repair the radio
tower stage by stage until its beacon lights. That starts the countdown to the finale: waves on the
players' own base, the last one carrying the boss. Cars get the parts home; the plane reaches the one
site that holds the last component.

The loop, in order: **scavenge → craft → upgrade the hideout → scout → loot → take → hold →
repair the tower → defend the base**. A strongpoint is four trips at least before it is held
(§6.1), so the map is crossed many times before anything is claimed.

---

## 2. The map

> **Placement revision (v6, 2026-09-03):** the coordinates below are draft 5's first cut. The
> revised placements — the radio tower in the camp (north-east corner, locked), Novo on the spine
> 1.1 km east, the old substation pad restored, offsets and pad levels for every transplant — are
> in `gscraft-map-layout-v6.md`, which the world build uses. Where the two differ, the sheet wins.

### 2.1 Border and ranges

**10 km square, centred on (1900, 1250)**: x −3100 … 6900, z −3750 … 6250. About 390,000 chunks,
~2.4 h of Chunky, ~6 GB, pre-generated in full before the first test. Set once with
`/worldborder center 1900 1250` and `/worldborder set 10000`.

| Range | From the camp | Owned by | What lives there | Attackable? |
|---|---|---|---|---|
| **Foot** | 0 – 1.5 km | walking | the camp, glass tower, acacia hall, Novo on the spine | strongpoints only |
| **Road** | 1.5 – 4 km | cars, boats | the district, Financial Plaza, the settlement, Bio Gen and the runway | strongpoints only |
| **Air** | 4.5 – 6.5 km | aircraft | the hub and generated cities kept as found; the only source of the rare loot-only parts | never |

### 2.2 The camp (starting area)

The 384×384 cleared area around the crater, x/z −176…207, with the Warium structure on its lake
island in the pit (plaza y 93, world spawn 19 94 26) and the rebuilt surface on the rim. The camp is
**neutral ground**: the NPC buildings are protected, spawns are suppressed inside the outline by **ten
diamond Magnum Torches** (64-block ellipsoid each; one at each of the five NPC pads away from the gate, one at Marshall's gate, four on a
ring — `tools/camp_torches.py`, placed by `gscraft:camp_torches`), and the players' own hideout is
wherever they claim. The torches are the visible reason the camp is safe; each NPC's tier-1 rebuild
keeps its torch inside the building. The recommended claim is the crater floor: a pit
with one ramp is the best wave-defence ground on the map, and it is where they woke up.

**The camp has its own ruins.** The v6 build cleared the starting area to natural ground, so Act I
would have had nothing to loot within 300 m. `tools/camp_ruins.py` scatters 24 small wrecks — burnt-out
cars, two buses on their sides, collapsed sheds, container stacks, fuel-drum piles, scrap heaps, tents
and two checkpoints — as eight sparse templates placed by `gscraft:camp_ruins` at ground level (heights
read from the built world), clear of every NPC pad, the tower compound, the crater and the gate approach.
Each piece carries one or two chests bound to `gscraft:ruins/{hardware,electrical,medical,mixed}`, the
loot tables that go live with the items in Phase C; positions are in `tools/camp_ruins.json`. The
pieces are built from **Doomsday Decoration**'s props — jeep, van, sedan and station-wagon wreck
segments, sandbags, oil drums, wire mesh, traffic cones, a forklift and a motorcycle — and that set is
the vocabulary for every camp building and checkpoint from here on (`gscraft-mod-capabilities.md` §1).

Six NPC buildings sit on the rim in a ring, 60–230 blocks from the crater centre, each with a yard.
Positions are first cut, to be adjusted on the visual pass against the rebuilt surface:

| NPC | Building | Footprint (blocks) | Where on the rim | What is in it |
|---|---|---|---|---|
| **Marshall** | the gatehouse | 24×16 | east gate, x 150…173 × z 0…15, where the spine leaves the camp | the map table, the tower parts rack (empty until parts arrive), the strongpoint board; players pass him on every trip east |
| **Walker the Foreman** | the yard | 40×32 | south-east, x 60…99 × z 80…111 | the workshop benches (crafting §4), garage bays, a vehicle lot, scrap piles |
| **Tony the Medic** | the clinic | 20×16 | north-west, x −100…−81 × z −100…−85 | beds, the med station, a PlayerRevive point |
| **Michael the Engineer** | the plant | 32×24 | south, x −40…−9 × z 100…123, at the crater edge above the lake | generator shed, water collector, tanks, the fuel pump |
| **Tune the Technician** | the radio shack | 16×16 with a 12-block mast | at the tower compound's west gate, x 40…55 × z −120…−105 | the small mast (a visible echo of the tower), the map board, the intel desk |
| **James the Scout** | the lookout | 8×8 tower, 20 tall | north-west corner, x −150…−143 × z −150…−143 | the expedition board, a view over the approach |

Each building is a structure template placed by a generator (Phase C, on the positions the visual pass fixes) in the style of
`tools/tower.py` (a `camp.py`, to write), so the camp can be re-cut without hand building. What is
placed is **tier 0** of four: every building has three upgrade tiers, each its own template on
the same footprint, placed by the NPC's upgrade quests (§3.6).

### 2.3 Strongpoints and sites

| # | Strongpoint (holdable) | Where | From the camp | Role | NPC |
|---|---|---|---|---|---|
| 1 | **Novo Expograd Industrial Zone** (transplant 144×160) | on the spine, x 992…1135 × z 96…255 | 1.06 km ENE | Heavy industry | Walker |
| 2 | **Residential block** (district) | from 1328, 1376 | 1.9 km | Medical | Tony |
| 3 | **Industrial plant** (district 464×272) | 1904…2367 × 864…1135 | 2.4 km | Fuel and water | Michael |
| 4 | **FR-06 complex** (district 384×528) | 2192…2575 × 400…927 | 2.5 km E | Power and hangar | Michael |
| 5 | **Financial Plaza Quarantine** (transplant 160×144) | dry land west, x −1952…−1793 × z 848…991 | 2.1 km W | Electronics | Tune |
| — | **Radio tower** (custom) | in the camp, x 64…191 × z −144…−17 (pad y 99) | 0.1 km | Endgame | Marshall |

**Generated sites, counted** (`tools/structures_v6.json`, every structure start in the 10 km box): 45 villages — Lukis Grand Capitals' versions, hostile under Hostile Villages — and 21 pillager outposts, the bandit settlements of the map; 284 Underground Bunkers; 439 Apotheosis boss towers (the elites of §6.3 can simply be the towers nearest each site); 23 ancient cities; 35 Man-From-The-Fog houses; 2 mansions; 8 strongholds; 107 smaller starts (trail ruins, igloos, pyramids, monuments) — 964 in all. Nearest to the camp: villages (800, -2352), (2416, -672), (3216, 912); outposts (-1392, 1632), (-1952, 1232), (-512, 2368); bunkers (16, -368), (448, -384), (-784, -384); boss towers (32, -368), (832, -816), (1312, 64). James's J9 sends the players to four of the capitals, and the bunkers are the U-chapter's side dungeons. **Owner's verdict on the census: far too dense.** `gscraft-structure-plan.md` keeps **67** of the 964 sites
(11 towers, 14 bunkers, 10 capitals, 6 outposts, 4 ancient cities, the rest expedition finds), none within 350 m of
a designed site, spaced by type, capped per range ring, nearest the roads first; the world is regenerated as **v7**
with the pruned structure sets disabled and the kept ones placed back (`buildmap/structure_plan_v7.json`).

**Dead military vehicles dress the strongpoints** (vvp and MCSP, kept): a BMPT and two Strykers on FR-06's reactor
plaza, a Typhoon-K convoy at the plant, an Mi-24 on the runway apron, a Pantsir at the hub — placed by the site
dressing pass (Phase C, alongside `camp.py`), battery-less so they never move, their inventories the component containers. Immersive Weathering
ages them and every tier-0 building on placement; a rebuilt tier is placed clean.

Loot sites, never attacked: **Bio Gen Offices** (two groups, 64×64 and 16×32) at the runway pad's west end;
**the settlement** (272×288) on the water-treatment pad re-cut to 288×304; **the sewers** (96×96)
under Financial Plaza; **the hub** (832×640, the Novo Expograd city) in the air
ring at x 5600…6431 × z 1184…1823, 6.2 km E, James's territory; the library, hempcrete compound, stone complex (a
spawner dungeon) and the small district builds — all located in `gscraft-map-layout-v6.md` §3.1 and given loot roles in
`gscraft-loot-tables.md` §5 (2026-09-04). If a transplant fails its remap, the hempcrete
compound takes its role.

### 2.4 Roads and water

The roads as built (v6/v7) are the four of `gscraft-map-layout-v6.md` §4: the spine camp → Novo → the district's
north-west corner; the west road camp → Financial Plaza; district → runway; district → settlement, plus the Woods
spur (woods plan). All routed around water by `tools/roads.py`; none has water on its line. The district → tower
road of draft 5 is gone: the tower is in the camp. The crater ramp still has to be driven (Phase A).

### 2.5 Travel (vehicles at their shipped speeds)

| Distance | Walk | Sprint | Boat | Car street | Car rubble | Aircraft |
|---|---|---|---|---|---|---|
| 1 km | 3.9 | 3.0 | 2.1 | 0.8 | 2.1 | 0.3 |
| 2 km | 7.7 | 5.9 | 4.2 | 1.7 | 4.2 | 0.6 |
| 4 km | 15.4 | 11.9 | 8.3 | 3.3 | 8.3 | 1.2 |
| 6 km | 23.1 | 17.9 | 12.5 | 5.0 | 12.5 | 1.8 |

Minutes one way; a Minecraft day is 20 real minutes.

---

## 3. The NPCs

**Implementation.** Named villager entities with no AI, invulnerable, persistent and silent, placed by
a datapack function (`gscraft:camp_npcs`) so they can be respawned in one command. A KubeJS
entity-interact handler makes right-click open the quest book and print the NPC's line; each NPC's
chapter is tagged with their name. Villager skins give each a look (Tony a cleric, Walker a
toolsmith, Michael an armorer, Tune a librarian, James a fletcher, Marshall a nitwit in a helmet is
the joke, or a cartographer if not). The Recruits mod supplies the hireable guards of D2 (Walls 2, at the gatehouse);
it is not used for these six. No gameplay mod is added (EMI, a client-side recipe viewer, was added on 2026-09-03).

**Who unlocks what.** The full chains, 121 quests across the six chapters, scaled by act and distance, are in `gscraft-quests.md`; the trip table in §3.5 shows which of them one outing clears.

| NPC | Owns | Starting tasks (the introduction) | Unlocks when done | Their chain |
|---|---|---|---|---|
| Walker the Foreman | Workshop, Garage, Storage | bring 8 bolts, 8 nuts | a wrench, the fastener-kit and hand-tool blueprints, the personal station | take and hold Novo; motor assembly; vehicles; the mast section kit |
| Tony the Medic | Medical | bring 4 bandages, 2 painkillers | med-kit blueprint | hold the residential block; revive a teammate; medical analyzer; finale readiness |
| Michael the Engineer | Generator, Water | bring 3 wire spools, a power cord, a water filter | wiring-harness and filter blueprints | hold the plant; coolant; hold FR-06; the cooling loop, then the generator kit |
| Tune the Technician | Radio / intel | bring a circuit board, 2 capacitors, a broken radio | circuit-assembly blueprint | hold Financial Plaza; antenna elements; the transmitter, then the antenna array |
| James the Scout | expeditions | visit the glass tower and the acacia hall | waypoints; the expedition board | the settlement by car; the hub by air; the phased array element |
| Marshall | the strongpoint loop and the tower | **none: he talks once all five introductions are done, and the tower chapter opens with him (owner, 2026-09-04)** | the tower chapter and the strongpoint board | take → hold → defend; five parts in order; the beacon; the finale |


### 3.6 NPC building tiers

Every NPC's building has **four states, tier 0 to tier 3**, and three upgrade quests in that NPC's
chapter (`*-B1`, `*-B2`, `*-B3`) climb them. Each hand-in **rebuilds the building where it stands**:
the reward runs a datapack function that places the next tier's structure template over the same
footprint and re-summons the NPC at their new spot, exactly as the tower stages work (§7). The camp
therefore grows visibly with the players' progress, and each NPC's site is a readout of how far their
chain has come. Tiers are separate from the hideout function levels of §5 — the functions are the
players' claim, the tiers are the NPCs' own places — but their gates line up so neither runs ahead of
the other: tier 1 after the introduction, tier 2 after that NPC's strongpoint is defended, tier 3 with a
hub component (the gatehouse: FR-06's reactor control module).

| NPC | Tier 0 (as placed) | Tier 1 — Repair | Tier 2 — Expand | Tier 3 — Complete | What the tier adds |
|---|---|---|---|---|---|
| **Walker** — the yard (**the workshop**) | scrap piles, a lean-to (personal stations only) | roofed workshop, one garage bay, a fenced lot, the IV vehicle bench | second bay, gantry crane over the lot, fuel-drum rack, lights, the SW assembling table, the Apotheosis Salvaging Table | steel shed with a vehicle lift, floodlit painted lot, truck bay | crafting speed ×0.85 / ×0.7 / ×0.5 and 1 / 2 / 3 shared benches by tier (crafting §4); T2: vehicle repair at the bay; T3: aircraft parking |
| **Tony** — the clinic | a tarp over a wreck, one bed | walls, four beds, the med station | surgery room, its own generator, the lit red cross | two storeys, a ward, a quarantine tent, a marked helipad | T2: faster PlayerRevive at the clinic; T3: full revive without a surgical kit |
| **Michael** — the plant | one generator on a pallet | generator shed, water collector | tank farm, pump house, pipe run down to the lake, the fuel pump, the charging station | wind mast, transformer yard, biodiesel column, lit pipes | T2: fuel cans refill at the pump; T3: the camp outline is lit and powered |
| **Tune** — the radio shack | shack and a 12-block mast stub | mast to 24 with a dish, the map wall | antenna field beside the shack, intel desk | mast to 40 with an aviation light, second dish, receiver on the roof | T2: the board shows the contested site's whole countdown (Radio 2's readout); T3: the coming attack's composition |
| **James** — the lookout | 8×8 tower, 20 tall | platform, ladder, a flag | 30 tall, a spotlight that sweeps at night | 40 tall, glass cabin, telescope, waypoint beacon | T2: the night spotlight (waypoint sharing is Radio 1's); T3: every named site marked |
| **Marshall** — the gatehouse | a gap in the wall, a table, the parts rack, the strongpoint board | the gate, wall stubs | walled gate, two watchtowers, barricades | blast doors, floodlights, the strongpoint board as a lit wall map | T2: guard villagers at the gate; T3: the finale's first wave breaks on the gate, not the crater |

Two mods carry the tiers' promises: **Guard Villagers** supply the armed guard each building gets at
tier 2 (Marshall's tier-2 gate gets two), and **Recruits** supplies the hireable soldiers behind
Marshall's D2 — hired at the gatehouse from Walls 2 (D2), ranks from recruit to captain, and the mod's
own claim-and-siege logic is kept switched off so the loop stays the only attack calendar. Hordes'
**player infection is on** (`hordes-common.toml`, `infectPlayers = true`, 75 % per zombie hit): the
clinic cures it from T1 and the med kit cures it in the field from Medical 2, which is the medical
function's reason to exist.

Hand-ins scale with the acts and reuse what the loop already produces: tier 1 is camp junk and the
first intermediates; tier 2 needs bulk building material (concrete, steel frames) plus **one more**
of the strongpoint's loot-only components — a second item of the same site (the engine, the membrane, the encrypted radio,
the analyzer), respawning while the site is held, so each upgrade is another trip to a site the players already own; tier 3 needs
one hub item (the gatehouse's R-B3 takes FR-06's reactor control module instead). `camp.py` generates the 24 templates (six buildings × four tiers) and their placement
functions `gscraft:camp_<npc>_<tier>`; tier 0 is placed first, by `camp.py` after the visual pass (Phase C).

**Every building is locked the way the tower is.** The tower lock (`gscraft_tower_lock.js` and its
native startup twin) refuses block breaking, placing, explosions and fluid flow inside one rectangle
unless the change comes from a quest function. The same script takes a list of rectangles, so each
NPC site gets one — the **largest tier's footprint plus its yard**, fixed now so the lock never has to
move — and the camp's six buildings cannot be griefed, burned, blown up or mined out by players or
by mobs. Containers inside stay usable; the NPCs are already invulnerable. The rectangles live
beside the pads in `tools/pads_camp.json` so `camp.py`, the lock script and the map page read one
source.

---

## 3.5 Trips: what each area clears at once

The quest chapters are written against the same areas, so one outing closes quests for several
NPCs at once. Quest ids are from `gscraft-quests.md`. "Haul" is the number of slots the trip's
hand-ins need if everything is found, and bulky items take a hand or a vehicle seat each; neither is
a limit. A trip that does not fit is simply two trips: the sites stay where they are and a held
site's component containers respawn every two in-game days, so nothing is lost by coming back.

| Trip | Act | Area (from the camp) | Quests it serves | Haul (slots) | Bulky | Get there |
|---|---|---|---|---|---|---|
| 1 | I | the camp's own ruins (0–300 m) | W1, T1, M1, U1 hand-ins; X1's briefing once the five are done; D1 concrete later | 11 | — | foot |
| 2 | I | glass tower + acacia hall (1.3–1.55 km) | J1 locations; W3 metal scrap; M2 light bulb; T2 med items | 6 | — | foot |
| 3 | I | Novo (1.06 km E on the spine) | J-S1 dossier; W5 loot (spark plugs, scrap, oil) over two or three runs; R2 marker and assault; hardware and spark plugs for W7; after the hold: W11 heavy anchor cable, W9 heavy diesel engine | 8 | 2 (after the hold) | foot; the bulky parts one per carrier, or the first car |
| 4 | II | the west edge: residential block, hempcrete compound, library (1.9–2.5 km) | J2 locations, J-S2 dossier; T3 loot (blood bags, syringes, antiseptic); R3 marker and assault; U3 hard drive, J3 folders; electrical items for U2 and U8; D3's seeds and bowls at the hempcrete compound | 14 | — | foot, then the first car |
| 5 | II | the industrial plant (2.4 km) | J-S3 dossier; M4 loot (hoses, fins, fuel cans); R4 marker and assault; hoses, tubes and fins for M3 and M6; fuel cans for M7 and W8; after the hold: M6 industrial pump | 9 | 1 | car |
| 6 | III | FR-06 (2.5 km E), with the factory annex and hopper array on the way | J-S4 dossier; M8 loot (relays, motors, a battery); R5 marker and assault; electrical items; after the hold: M10 transformer core, M11 avionics module and reactor control module | 10 | 3 | car |
| 7 | III | Financial Plaza and the sewers under it (2.1 km W) | J-S5 dossier; U4 loot (circuit boards, computer parts, a hard drive); R5 marker and assault; U6 sewers and encrypted radio; electrical and valuables; after the hold: U7 military circuit board; D4 concrete | 12 | 1 | car |
| 8 | III | the far ring by road: stone complex, mud village, the settlement, Bio Gen, the runway (2.8–3.9 km) | J4 locations, J5 valuables, W12 pressure gauge, T7 surgical kit, J6 hard drive; W10 second anchor cable on the way back past Novo; M12 membrane at the plant | 9 | 3 | truck, or boat to the settlement |
| 9 | IV | the hub (6.2 km E) and the four generated cities | J7, J9 locations; J8 phased array element and satellite receiver; T9 and M13 military power filters | 6 | 4 | aircraft |
| 10 | II–IV | home: the gatehouse and the claim | X2–X6 hand-ins, T10 ready room, D1–D6, R6; the eighteen `*-B` building upgrades as their hand-ins come together | — | the five complete parts, one at a time | — |

What the table fixes is the pairing: which NPCs' quests point at the same place in the same act, so
the group decides together where to go next and everyone has a reason to be there. How many trips
it takes is the players' business — with a floor: each strongpoint row above is at least four
visits, because scouting, looting and the take are separate quests in three different chapters
(§6.1), and the loot quests ask for items that only drop at that site.

---

## 4. Items, crafting and space

> **Crafting revision (2026-09-03):** how crafting runs — timed work orders, one server-placed
> station per player, the workshop in Walker's yard with its tier bonuses, the vehicle roster and
> the equipment recipes that replace loot — is `gscraft-crafting.md`. The item ladder below is
> unchanged; the workbench-on-click of §4.3 is superseded by the station.

### 4.1 Three tiers, one rule

| Tier | How you get it | Stack |
|---|---|---|
| **Small items** (42, §4.2) | loot only, everywhere, by building type | 4–8, tools and valuables 1 |
| **Intermediates** | ordered at the stations (crafting §4) from blueprints the NPCs hand out per base-function level | 4 |
| **Complete parts** | intermediates **plus one loot-only component** | 1, bulky |
| **Loot-only components** | at the strongpoint that owns the role, or the hub; no recipe exists | 1, bulky |

**Nothing complete is ever loot; nothing complex is ever crafted.** Every complete part needs a
crafting chain and a trip.

### 4.2 Small items

| Category | Items | Drop mostly in | Stack |
|---|---|---|---|
| Hardware | bolts, nuts, screws, nails, metal scrap, duct tape, insulating tape | garages, workshops, factories, Novo, the plant | 8 |
| Electrical | wire spool, power cord, light bulb, capacitor, relay, circuit board, electric motor, car battery | offices, Financial Plaza, FR-06 decks, the library | 4 (motor, battery 1) |
| Mechanical | corrugated hose, silicone tube, radiator fin, pressure gauge, spark plug | the plant, garages, Novo, the sewers | 4 |
| Filters and chemicals | water filter, gas-mask filter, bleach, antifreeze, motor oil, solvent, gunpowder (vanilla) | stores, the plant, apartments, Bio Gen; gunpowder at the stone complex and military chests | 4 |
| Medical | bandage, painkillers, syringe, antiseptic, blood bag | apartments, the residential block, Bio Gen | 4 |
| Tools | wrench, pliers, screwdriver set, hand drill, welding torch | garages, Novo, FR-06 hangar | 1 |
| Valuables | broken radio, computer parts, hard drive, folder of documents, emerald (vanilla; the Recruits' hire currency) | offices, Financial Plaza, the hub | 1 |

**Food is outside the ladder:** canned goods (`gscraft:canned_goods`, a KubeJS food item) and Farmer's Delight crops drop
beside the small items (`gscraft-loot-tables.md`) and feed hunger; they count for no collection quest.

### 4.3 Intermediates (blueprints = team stages `bp_<recipe>`, ordered at the stations; the "blueprint from" column follows the quest tables)

| Intermediate | Recipe | Blueprint from |
|---|---|---|
| Fastener kit | 4 bolts + 4 nuts + 4 screws + 4 nails | Walker, W1 |
| Steel frame | 6 metal scrap + 1 fastener kit, welding torch held | Walker, W3 (Workshop 1) |
| Toolbox | wrench + pliers + screwdriver set + hand drill | Walker, W3 (Workshop 1) |
| Motor assembly | 1 electric motor + 1 spark plug + 1 wiring harness | Walker, W6 (Workshop 2) |
| Wiring harness | 3 wire spool + 1 power cord + 1 duct tape | Michael, M1 |
| Filter cartridge | 1 water filter + 1 corrugated hose + 1 bleach | Michael, M1 |
| Coolant | 2 antifreeze + 1 water bucket | Michael, Water 1 |
| Sealed tubing | 1 silicone tube + 2 insulating tape | Michael, Water 1 |
| Circuit assembly | 1 circuit board + 2 capacitor + 1 relay + 1 wire spool | Tune, U1 |
| Antenna element | 2 metal scrap + 1 wire spool + 1 insulating tape | Tune, Radio 2 |
| Med kit | 2 bandage + 1 painkillers + 1 antiseptic + 1 syringe | Tony, T1 |

### 4.4 Complete parts and loot-only components

| Stage | Complete part | Intermediates | Loot-only component | Found at | Needs |
|---|---|---|---|---|---|
| 1 | Mast section kit | 6 steel frame + 2 fastener kit | Heavy anchor cable | Novo | Workshop 2 |
| 2 | Cooling loop | 2 filter cartridge + 2 coolant + 2 sealed tubing | Industrial pump | the plant | Water 2 |
| 3 | Generator kit | 2 wiring harness + 1 motor assembly | Transformer core | FR-06 reactor plaza | Generator 2 |
| 4 | Transmitter | 2 circuit assembly + 1 wiring harness | Military circuit board | Financial Plaza | Radio 2 |
| 5 | Antenna array | 4 antenna element + 1 circuit assembly | Phased array element | the hub only | Radio 3 |

Other loot-only components, first cut: heavy diesel engine (Novo); purification membrane (the
plant); reactor control module, avionics module (FR-06); encrypted radio (Financial Plaza); medical
analyzer, surgical kit (residential block, Bio Gen); satellite receiver, military power filter (the
hub). They spawn in specific containers at their site, one or two per visit, and respawn on the
respawn timer, so a held strongpoint keeps producing. Base upgrade kits have the same shape: a kit of
intermediates, from level 2 one component from the role's strongpoint, at level 3 one from the hub or a second held-site component (B3: the blanket hub rule is dropped).

**The hub's economy (C17, 2026-09-04).** The game needs 3 phased array elements (X6, U9, J8), 6 satellite receivers
(J8, W-B3, U-B3, J-B3, Storage 4, the Black Hawk) and 4 military power filters (T9, M13, T-B3, M-B3): thirteen hub
items. The hub is never held, so they sit in shared `gscraft:hub/*` component containers that the loop script refills every 5 in-game days (B29; not Lootr-instanced, so five players still get five items), not
the held-site timer — one array container, two receiver containers, two filter containers, one item each per refresh:
five a visit, so the list is **three hub runs** across Act IV's three sessions, one a session (`gscraft-loot-tables.md` §6).
U-D3's satellite receiver saves one of the six.

### 4.5 Space

36 slots and an offhand; a fighting kit takes 10–12; the rest is the loot budget, and a complete
part's shopping list is 6–10 different items, so the budget is spent on **variety**.

- Small items stack 4–8; intermediates 4; complete parts and components **stack 1 and are bulky**:
  no backpack, Slowness and no sprint while carried (KubeJS item + player tick; backpack exclusion
  through the backpack mod's config if it has one, else a KubeJS insert check).
- Death drops everything except the secure pack (keepInventory off; PlayerRevive makes it rare). **Rules of play (owner defaults, 2026-09-04):** respawn is the camp (world spawn 19 94 26; a bed at the clinic from T-B1 moves it); a downed player bleeds out in 5 minutes unless revived (PlayerRevive `bleedTime` 6000 and `maxDistance` 6 — one global value each, the mod has no runtime config command, so Medical 1 and the clinic tiers act through the script instead: the camp revive point at Medical 1, a 3-second clinic revive at T-B2, full health at T-B3 — C18, 2026-09-04); infection kills 20 minutes after the bite (Hordes: four 5-minute phases, `ticksForEffectStage` 6000) unless cured at the clinic (T1) or by a med kit (Medical 2), and that death is a real death, not a bleed-out (`hordes:infection` bypasses PlayerRevive); a late joiner or sixth player receives the team's stages (all progress stages are **team** stages via FTB Teams; only the first-time onboarding lines and `revives_3` are per player), the starting kit and the introductions as a tour; the fortify clock, warning and defence tick only while **two or more** team members are online - a defence that would start with fewer waits for the next login; a restart mid-assault keeps the contested slot, the clocks and the marker, and the interrupted wave restarts from its beginning; pvp and friendly fire are off; the sleep percentage is 100 so nights are never skipped; hunger stays on and is fed from Marshall's kitchen (D3) and canned goods in the loot tables; the world border warns at 200 blocks and does no damage.
- **Storage is Walker's function**, on Sophisticated Backpacks in the Curios slot:

| Storage | Unlocks | Carried |
|---|---|---|
| 1 | basic backpack; the stash crates at the claim | +27 |
| 2 | iron backpack; stack upgrade ×2, magnet upgrade (the cargo crate is W7's, Garage 1) | +54, +27–54 in the car |
| 3 | gold backpack; **everlasting upgrade** (survives death: the secure container); truck cargo | +81, +108 in the truck |
| 4 | diamond backpack; aircraft cargo | +108 |

Bulky items ride in vehicle cargo or in hand. The garage is how tower parts get home.

---

## 5. The hideout

The players' claim (FTB Chunks, one team). Functions: Workshop, Garage, Storage (Walker);
Generator, Water (Michael); Medical (Tony); Radio / intel (Tune); Walls and defences, Farm and
kitchen (Marshall's chapter). Three levels each: level 1 from small items and intermediates, level 2
needs the role's strongpoint held and one of its components, level 3 needs one component from the
hub (Radio, Medical, Generator, Storage 4) or a second held-site component (Water 3: the plant's membrane; Storage 3 and Walls 3: Novo's anchor cable; Garage 3: FR-06's avionics module — B3). Each level is a quest in the owning NPC's chapter; the reward flips a KubeJS stage that gates
recipes, hands out the next blueprint, and applies the effect (guard villagers, warning length,
vehicle recipes). Between them the level 3s need held ground and a plane: the
whole map, used once.

---

## 6. The strongpoint loop and the timers

Marshall's chapter, with James (scouting) and the owning NPC (looting, holding) on each site.

### 6.1 The site ladder

Every strongpoint climbs the same five states, each a KubeJS stage the quest book reads. Nothing
skips a rung: the marker cannot be placed on a site that has not been scouted and looted.

| State | Stage | What the players do | Trips | Quest |
|---|---|---|---|---|
| **Scouted** | `<site>_scouted` | reach the site; find its **dossier** (a valuables item that only spawns in one container there) and hand it to James; the strongpoint board then shows the site's garrison type (its strength from U3), its component container, and — once held — its timer | 1 | James, `J-S*` |
| **Looted** | `<site>_looted` | the owning NPC's hand-ins of items that drop **only at that site's building types** (Novo: hardware, spark plugs; the plant: hoses, fins, fuel cans; the block: blood bags; FR-06: electrical; the plaza: valuables and circuit boards). Two or three trips with the loot budget of §4.5; Lootr refreshes the containers between visits | 2–3 | owning NPC |
| **Cleared → Held** | `<site>_held` | Marshall's take. The team places the **claim marker** at the site's anchor point. That starts the **assault**: the garrison spawns in waves from the site's edges for 5 minutes; the marker must survive and at least one player must be inside the site rectangle when the 5 minutes end. Win → held, the fortify clock starts, the component container arms. Fail → the marker breaks, the garrison respawns, try again | 1, repeatable | Marshall, `R*` |
| **Defended** | `<site>_defended` | the site's defence (§6.2), which always comes and is the only attack the site will ever see. Win → the site is safe for good and its components respawn on their timer | 1+ | owning NPC |
| **Lost** | `<site>_held` cleared, `<site>_lost` set | the marker was broken, or the rectangle was empty of players when the defence ended. Components stop; the garrison respawns; the site is Looted again — re-take it from the marker step, no re-scouting | — | — |

The garrison before the take is In Control!'s ambient spawn for the site, thin enough to loot
through with care; the assault is the fight. One player dying does not lose a site.

### 6.2 Timers

A site is **contested** from the moment its marker is placed until its defence is won. Attacks
happen only on contested sites; a defended site is never attacked again. There is no random cycle
and no site is ever drawn while the players are elsewhere — the only fights are the ones they start.

| Timer | Value | Note |
|---|---|---|
| Assault (the take) | 5 min from marker placement | waves every 45 s from the site edges; garrison scaled to players present |
| Fortify clock | 2 in-game days (40 min) after `held` | build up, run the loot; nothing attacks during it |
| **The defence** | the warning starts when the fortify clock ends, **on this site only** | warning = a flat 10 minutes (owner, 2026-09-04; every built site is under 10 min on foot); the board shows the warning from Radio 1 and the whole countdown (fortify + warning) from the moment the site is held once Radio 2 is in (U5) |
| Component respawn | every 2 in-game days while the site is **held** (the one rule; Lootr's 5-day refresh is for ordinary loot only - owner, 2026-09-04) | doubled once every site is held (R6) |
| Finale countdown after the beacon lights | 3 in-game days (60 min) | waves at the base, the last one carries the boss (`gscraft-finale.md`) |

**One contested site at a time.** The marker is refused while another site is still contested, so
the players finish one fight before starting the next and the map is taken in order — the pasted
progression of R2 → R6. Clocks run on **online time** only (they advance while two or more team members
are on — the rules of play, §4.5), so a defence never fires into an empty world. Hordes' horde event is off (the pack ships it disabled, B6); only its
infection runs, wherever the players are, and nothing random ever targets a site. Tune's Radio levels read
the contested site: Radio 1 shows the warning, Radio 2 the whole countdown from `held`, Radio 3 the
attack's composition (wave count and mob types) as soon as the marker is placed.

The tower's components come from four held sites and the hub, so the loop is the tower's supply
line; a component container arms on `held` and refills on its timer while the site is held.

### 6.3 Garrisons — the mob tables Phase D builds from

Three layers per site, all from mobs the pack already has. **Ambient** is what In Control! spawns
inside the site rectangle before the take (thin enough to loot through with care, per §6.1);
**assault** is the six 45-second waves after the marker goes down; **defence** is the attack at the
end of the fortify clock. Counts are for five players present and scale by the number inside the
rectangle (×0.6 for one or two, ×0.8 for three or four); every wave enters from the site's edges,
never inside its buildings. Mob ids, checked against the jars: neither the Bandits mod nor Pillagers Gun registers an entity —
"bandits" and "gun pillagers" are vanilla **pillagers and vindicators**, which Pillagers Gun arms;
Hordes adds only the zombie-player variants, so zombies, husks and drowned are vanilla; IE's Fusilier /
Commando / Bulwark (`immersiveengineering:*`), The Knocker (`the_knocker:knocker`), The Man From The
Fog, Eyes in the Darkness, spiders and cave spiders. Improved Mobs' scaling stays on so garrisons harden
with distance. **Mob Factions** makes the illager faction and the zombie faction enemies of each other
(the carried `MobFactions.toml` already does; the Knocker rides with the zombies), so a site's ambient
garrison fights itself and a patient team can watch it thin. **The Bandits mod's own random raids are
switched off** (`bandits.json`, `enableMod: false`): they attack players anywhere on a 5–15 day roll,
which is exactly what §6.2 forbids. **Zombie Awareness** stays on at sound strength 10: gunfire and
block-breaking draw the ambient garrison, which is why loot trips are quiet work, the take is loud,
and the suppressor of W-A4 is worth its price.

| Site | Theme | Ambient (In Control! rule inside the rect) | Assault, six waves | Defence, three waves | Elite |
|---|---|---|---|---|---|
| **Novo** (Act I) | industrial squatters | zombies 6, bandits 2 at a time | zombies 8 → 10 → 12, bandits 2 per wave from wave 3 | zombies 15, then bandits 4 + zombies 10, then bandits 6 | a bandit captain with a shotgun (wave 6, defence 3) |
| **Residential block** (Act II) | the dense dead | zombies 10, husks 4, Eyes at night | zombies 12 per wave, husks 4 from wave 2, spiders 6 on waves 4–6 | zombies 20, then 25, then 30 with 8 spiders | The Man From The Fog stalks the block from the take onward |
| **Industrial plant** (Act II) | wet ground, armed | zombies 6, drowned 6, bandits 3 | drowned 8 + zombies 6, bandits 3 from wave 2, a Fusilier on 4 and 6 | drowned 12 + zombies 10, then bandits 6 + Fusiliers 2, then Commandos 3 | a Bulwark on defence 3 |
| **FR-06** (Act III) | the militia | gun pillagers 6, Commandos 2 | gun pillagers 8 per wave, Commandos 2 from wave 2, Bulwark on 5 | gun pillagers 12 + Commandos 4, then Bulwarks 3, then everything plus 2 Bulwarks | The Knocker inside the hangar from the take onward |
| **Financial Plaza** (Act III) | organised bandits | bandits 6, gun pillagers 4 | bandits 8 + gun pillagers 4 per wave, Commandos 2 on 3 and 6 | bandits 12 + gun pillagers 8, then Commandos 6, then bandits 15 + Bulwarks 2 | The Man From The Fog and The Knocker together on defence 3 |
| **The sewers** (dungeon, never held) | the dark | cave spiders 10, zombies 8, Eyes always | — | — | — (U6's kill count of 20 is the ambient) |

Ambient rules are In Control! `spawn.json` entries keyed to the site rectangle (`minx/maxx/minz/maxz`)
with a `maxcount` cap; assault and defence waves are the loop script summoning at edge points, with
the Hordes wave types for the zombie mixes. The camp's own suppression rule (no hostile spawns inside
the outline) stays; the finale's waves at the base are §7.1.

**Elites (C14, 2026-09-04).** Each site's elite is an Apotheosis boss definition `gscraft:elite_<site>` in the datapack
(the site's mob type, a TaCZ gear set, rarity rare–epic, +40…+80 HP, knockback resistance 0.5), summoned by the loop
script with `/apoth spawn_boss gscraft:elite_<site> <rarity>` at the wave the table names — the same call the Boss
Spawner block makes, with no block to place. Natural bosses stay off (`Boss Spawn Cooldown` at its maximum), so an
affixed mob is always a designed moment. **The Woods** (x 400…2400, z −3500…−1500) has its own In Control! rule:
zombies capped at 4, no husks, drowned 2 at water, bandits only inside the outpost's rectangle until R-W1, spiders
below y 40 (the bunkers), the fog man and the eyes at night as their mods spawn them (quests §7.5).

---

## 7. The radio tower

Six sparse structure templates in the datapack (`gscraft:tower_stage_0…5`, `tools/tower.py`, render
`docs/renders/radio_tower_stages.png`), origin (107, 100, −101) on the camp pad at y 99. Stage 0 is placed at world build;
each hand-in to Marshall runs the next stage's function.

| Stage | Hand in | Appears |
|---|---|---|
| 0 | — | ruined plinth, three leg stubs, wrecked hall, broken fence, rubble |
| 1 | Mast section kit | lattice mast to 64, braces, platforms, four guy anchors with chain wires |
| 2 | Cooling loop | two coolant tanks, pipe run, radiator bank |
| 3 | Generator kit | generator shed, relays up the mast, aviation lights and floodlights on |
| 4 | Transmitter | hall repaired and fitted out, dish on the roof |
| 5 | Antenna array | iron cap, spire, dipoles, and the **beacon** whose beam starts the countdown |

### 7.1 The finale and the boss

The countdown ends in five waves at the players' claim: waves 1–4 are the defence tables of §6.3
stacked (Novo's, then the plant's, then FR-06's, then the plaza's, each ×1.5), waves 2–5 each bringing a named
Apotheosis-boss **Captain** (the fourth beside the Sleeper), and **wave 5 is the boss: the Sleeper, a named Warden** that rises at the
gate — the thing under the crater that the beacon's pulse woke. It was chosen over the Ender Dragon
after research (`gscraft-finale.md` §2): outside the End the dragon never lands and cuts gun damage to a
quarter, and the Wither becomes immune to projectiles at half health, which in this pack means immune to
guns. The Warden is ground-bound, one hitbox, hunts the shooters by their gunfire, its sonic boom ignores
armour, and it breaks no blocks, so `mobGriefing` stays untouched. Health scales with the players online
by one `/attribute` command; fail, retry and the reward are `gscraft-finale.md` §4. The numbers are
Phase E's to confirm.

---

## 8. Tech stack (no custom mod)

KubeJS (items, blueprint recipes, the work-station block and its timer, stages, the loop, the bulky rule, NPC interaction), EMI (recipe viewer, client side, added 2026-09-03), FTB Quests
(chapters, tasks, rewards), FTB Chunks and Teams (claim, per-team state), Immersive Engineering (power and
machines), Sophisticated Backpacks and Curios (storage), In Control! and Hordes
(waves), Lootr (instanced loot), datapacks (loot tables, tower and camp templates, NPC summons). All
of it edits live on the server without a client reinstall.

---

## 9. Build order, and the tests it unblocks

Each phase ends in a test with a pass condition; nothing in a later phase starts until the earlier
test passes.

**Phase A — Visual pass on the v7 world (after the v7 build; gaps C16).** Local server, `start-visual.bat`, five players or
one. Fly the camp rim and mark the six building sites on the rebuilt surface; drive out of the
crater; walk the spine line and note every water crossing; check each landing pad's fit; look at the
generated cities between the camp and the district. *Pass:* a marked-up list of terrain fixes and
final building positions.

**Phase B — World build (v6 built and deployed 2026-09-03; v7 = the structure prune and the Woods, in progress).**
Done in v6: border set; pads laid as foundations without outlines; the transplants (the settlement, Novo, Financial
Plaza, Bio Gen, the sewers, the hub) through the 1.12 → 1.20 pipeline (`anvil112.py`, `remap112.json`, `transplant.py`);
the four roads routed by `roads.py`; tower stage 0, the camp ruins and the torches placed by function. Coming with v7
(`gscraft-structure-plan.md`, `gscraft-woods-plan.md`): the kept structures placed back, the Woods regenerated, the
Novo → sawmill spur, the runway lights (`runway_lights`). `camp.py`'s tier-0 buildings follow Phase A's positions (Phase C, as HANDOFF §5 orders it). *Pass:* a clean boot; every site reachable on foot or by road.

**Phase C — Systems v1.** KubeJS items (small, intermediate, complete, components, the five
dossiers, the claim marker; stack sizes; bulky rule), the station recipes and their `bp_*` stages, datapack loot tables by
building type and site (dossier and component containers keyed to their site), Lootr refresh on,
NPC interaction, the five introduction chapters, James's scout quests, Walker's storage levels,
and the tier-1 building upgrades (`camp.py` tier templates 0 and 1 at least).
*Test 2, five players, foot range only:* find items, craft at the stations, reach Storage 1 and
Workshop 1, scout Novo and hand its dossier to James, and get Marshall to talk.

**Phase D — The loop and vehicles.** The site ladder as stages, the marker and the assault, the
per-site fortify clock and defence, the one-contested-site rule, warnings, garrison and component
respawn, the loss condition; the garage tier and fuel chain. *Test 3:* loot Novo twice, take it
by assault, survive its first attack at the end of the fortify clock, bring a heavy anchor cable
home in a car, build the mast section kit.

**Phase E — The tower, the air ring and the finale.** Stages 1–5 wired to Marshall's chapter; the
hub's rare loot; aircraft; the beacon countdown and the base waves. *Test 4:* the beacon lights and
the finale runs to the boss (`gscraft-finale.md` §5 is the build and test list).

---

## 10. Open items (small)

- Exact rim positions of the six buildings: after Phase A.
- The full base-upgrade recipe sheet: written with Phase C, in the shape fixed in §4.4.
- Whether the crater ramp takes a car: Phase A; the fallback is a second, shallower ramp cut on the visual pass.
- Lootr refresh: set (`refresh_value` 120000 = 5 in-game days for `gscraft:` tables; mod-capabilities §5b). Done.
- The five anchor points for the claim markers, one per strongpoint: chosen on the visual pass.
- The dossier chests are placed: `tools/dossiers.json` and `gscraft:dossiers` (Novo 1028 78 158 new; the
  block 1330 84 1386 existing; the plant 2126 105 963 new; FR-06 2425 126 838 new; the plaza −1841 100 971
  new), each an enclosed upper-floor spot found by `tools/dossiers.py`; confirm the rooms read as their
  names on the visual pass.
- The 24 camp templates: tier 0 and 1 for Phase C, tiers 2 and 3 can follow in Phase D and E as
  long as the footprints are fixed now, since every tier is placed over the same rectangle.

Related: `gscraft-quests.md` (every quest and task), `gscraft-crafting.md` (stations, timers, vehicles, equipment), `wasteland-server-blueprint.html` (the original design record),
`notes/gscraft-scale-and-travel.md`, `notes/gscraft-foreign-worlds.md`, `wasteland-district-map.html`,
`build/tower_parts.json`.
