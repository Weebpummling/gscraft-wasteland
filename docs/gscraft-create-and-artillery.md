# GSCraft Wasteland — Create and the Big Gun (design fork)

Draft 2, 2026-09-05 (draft 1 the day before; the first gun moved into the camp). Owner's ruling: player feedback finds Superb Warfare's artillery undeveloped and unfun; Create with
Create Big Cannons was far more immersive. **Create and Create Big Cannons come back.** The players build the map's
artillery through a quest chain, and every strongpoint gets its own rebuild questline, given by an NPC who appears
there once it is captured. Superb Warfare stays for guns, vehicles and the roster items (owner rule: nothing is
removed); its artillery, mortar and defence-turret content stays stripped (`gscraft_recipes.js` §2) and Create Big
Cannons takes that role. This document forks `gscraft-map-design.md` §3.6, §6.1 and §8, `gscraft-quests.md` §7.2 and
`gscraft-crafting.md` §2.1/§4; the parent documents get one-line pointers here and are not rewritten.

## 1. The mods

| Mod | Version (Forge 1.20.1) | Role | Notes |
|---|---|---|---|
| **Create** | 6.0.8 (`create-1.20.1-6.0.8.jar`, 19.2 MB) | kinetic machines, trains, contraptions | embeds Flywheel 1.0.5, Ponder 1.0.91, Registrate 1.3.3, MixinExtras 0.4.1 (already in the pack, jar-in-jar dedupes) |
| **Create Big Cannons** | 5.11.4 (`createbigcannons-5.11.4-mc.1.20.1-forge.jar`, 4.1 MB) | big cannons, autocannons, casting, ammunition | needs Create and RPL |
| **Ritchie's Projectile Library** | 2.1.1 (78 KB) | CBC's projectile physics | library only |

All three are Modrinth-hosted (packwiz `modrinth` entries; the hash lookup covers them). Both sides. The isolated boot test
of the pack with the three jars is recorded in `HANDOFF.md` and `README-local.md` on the working machine; nothing goes
into `server/mods` or the client pack until that boot is clean.

**Station-only rule and Create.** Create's machines are stations too: nothing about them is craftable at a bench; they
are ordered at the NPC stations like every other intermediate (crafting §4.1), and the machines that make cannon parts
stand at the strongpoints (section 3), not in the camp. Create's own bench recipes (andesite alloy, casings, shafts,
cogs, belts, pipes) become **blueprint recipes at Walker's workshop** from Workshop 2, so the kinetic tier opens with the
workshop and not on day one.

**Ores in an authored world.** The v8 terrain is built by WorldPainter (map plan §2), so Create's zinc does not generate
and copper is whatever the terrain layers carry. Zinc, copper and brass therefore enter the way every material does:
loot tables (Novo and the plant drop zinc and copper ingots; the plaza drops brass sheets) and station orders. No mining
progression is added.

## 2. Create in the game (design)

Create is not a second tech tree beside Immersive Engineering; it takes the **moving** half of the base and the sites
while IE keeps the electrical half.

| Where | What Create adds | Gate |
|---|---|---|
| **Michael — the plant** (Generator/Water functions) | tier 1: the water wheel on the lake outlet and a hand crank (the first rotation); tier 2: the windmill on the wind mast, the encased fan; tier 3: the **steam engine** (boilers fed by the pump house) as the big rotational source; the mechanical pump replaces the pipe run | M-B1…B3 as today; the steam engine's boiler is the plant strongpoint's rebuilt product (section 3) |
| **Walker — the yard** (Workshop/Garage) | tier 1: the mechanical press and the millstone under the lean-to; tier 2: the **basin + blaze burner** (the camp's small foundry: brass, andesite alloy, melting scrap), the deployer line; tier 3: the gantry crane becomes a real Create crane (a rope-pulley contraption) and the mechanical crafters | W-B1…B3; the burner's blaze cake is a Novo loot drop |
| **Marshall — the gatehouse** (Walls) | tier 1: the gate is a **piston-driven bar**; tier 2: the drawbridge over the crater ramp (a bearing contraption) and the two watchtowers' spotlights on a gearshift; tier 3: the blast doors are a sliding-door contraption on a clutch, the floodlights on a rotation speed controller; the **autocannon nest** on each watchtower (section 4.6) | R-B1…B3; Walls 2 hands out the autocannon instead of the mortar |
| **James — expeditions** | the **train**: Skadowsky's rail line and Pripyat's station are real Create track once the sectors are placed (map plan §5); J-W-series trip = restore the line, build the first locomotive (steam, Create's train system), run it between the sector stations as the team's heavy hauler; the schedule block runs it unattended | after `skadowsky_held` and the plant's tier 2 (boiler) |
| **Tune — radio** | the display links and display boards for the strongpoint board (Create's display link replaces the sign-writing script for the board's clock), the nixie tubes on the radio shack | U-B2 |
| **Tony — the clinic** | nothing kinetic; the clinic's tier-3 helipad stays a pad | — |
| **The hideout** (§5 functions) | Storage: Create's item vaults and the mechanical arm for the players' own sorting; Farm (R-F1..F3): the harvester contraption and the tree fell, replacing the manual farm | Storage 3, Farm 2 |
| **Sites** | the elevator pulleys in Novo's silos and FR-06's reactor hall (rope pulley contraptions on a gearshift) as the vertical routes the loot tables assume; Pripyat's ferris wheel is a bearing contraption that turns once the town's power is restored (a J quest) | dressing pass, section 3 |

The Ponder screens Create ships are the tutorial; no quest text explains a machine the ponder already shows.

## 3. Strongpoint rebuild questlines (the site NPCs)

**Rule (owner, 2026-09-04): every strongpoint, once captured, gets its own NPC and a rebuild chain.** When the assault is
won (`<site>_held`, design §6.1) the site guard function also summons the **site keeper**, an invulnerable no-AI
villager like the camp NPCs (design §3), at the site's anchor point. The keeper gives three quests, `S-<site>-1…3`,
that climb the site through **tier 1 Repair, tier 2 Works, tier 3 Fortify**, each hand-in placing the next template
over the site's core building with `gscraft:site_<site>_<tier>` exactly as the camp tiers do (§3.6), and the tiers
gate the artillery chain of section 4. The keepers' names and looks are first cut; the owner renames.

| Strongpoint | Keeper | Tier 1 — Repair | Tier 2 — Works (what the site now makes) | Tier 3 — Fortify | Artillery piece it unlocks |
|---|---|---|---|---|---|
| **Novo Expograd Industrial Zone** (heavy industry) | **Kessler**, the foundryman | rubble cleared from the main hall, roof patched, the yard lit | the **foundry**: the mould bench (Create saw), three basins on blaze burners, casting-sand pit — cast iron and bronze pour here four barrels at a time (the camp's yard pours one) | walled yard, two site-guard posts, a **crane** over the cast pit (rope pulley) | bulk cast iron and bronze for the steel gun (4.6) |
| **Industrial plant** (fuel and water) | **Oksana**, the plant chief | pump house cleared, one boiler relit | the **power house**: steam engine on the rebuilt boilers, the shaft run to the **boring mill** (cannon drill + drill bit) | fence, a guard tower, the water intake fortified | fast boring: the steel barrels of G6 (the camp's hand-cranked frame bores cast iron only) |
| **FR-06 complex** (power and hangar) | **Rook**, the millwright | reactor hall floor cleared, the hangar door freed (a Create sliding door) | the **steel works**: the cannon builder (built-up layers), the mechanical press line for cartridges, the hangar as the gun shed | blast wall, autocannon nest on the roof | steel guns (4.4), big cartridges |
| **Financial Plaza Quarantine** (electronics) | **Ilya**, the clerk | ground floor cleared, the lifts (rope pulleys) running | the **fuze lab**: mechanical crafters for shells, the fuze bench (impact, inertia, delayed, proximity) | shutters, a guard post in the lobby, the sewers sealed behind a bar | shells and fuzes (4.5) |
| **Residential block** (medical) | **Vera**, the nurse | the school building cleared as the field hospital | the hospital: a second PlayerRevive point on the map, the cure at the site | fenced yard | the **gunner's manual** (a book item): the sighting quest of 4.3 needs it |
| **Skadowsky sector** (new, map plan §5) | **Danylo**, the stationmaster | the station cleared, the level crossing freed | the **rail yard**: the train's depot, the schedule block, the fuel bunker | the highway viaduct's checkpoint | the train (section 2, James) |

Hand-ins follow §3.6's rule: tier 1 = camp junk and first intermediates (planks, metal scrap, fastener kits); tier 2 =
bulk material (concrete, steel frames) plus one more of the site's own loot-only component; tier 3 = one hub item. The
keeper also sells the site's product at a counter (vendors doc): Kessler sells casting sand and cast-iron nuggets,
Oksana boiler water and packed gunpowder, Rook steel plates, Ilya redstone dust and quartz, Vera the manual's pages,
Danylo train tickets (the fast-travel token). Tier 2 doubles the site guard (design §6.1) so a working site is a
defended site.

## 4. The Big Gun — the artillery chain

One quest chain, in Marshall's chapter as **7.6 The Gun**, builds the map's artillery. **The first gun is built in the
camp** (owner, 2026-09-05): G1–G4 happen at Walker's yard and the gun pit on the crater rim, with materials looted from
Novo, so the team fires a gun before it holds a single site; the strongpoints then scale it up (steel, boring, shells,
the battery, the carriage). The gun is fired from the camp (the gun pit, a fixed cannon mount) and, later, from a
carriage the team tows. Recipes are Create Big Cannons' own (read from the mod's data, 5.11.4); the quest gates are
ours.

| Quest | Name | Act | Where | Gate | Task | Reward / unlock |
|---|---|---|---|---|---|---|
| G1 | Sand and iron | II | **camp — Walker's yard** | W-B2 (the basin and blaze burner), `novo_looted` | hand in 16 casting sand (2 sand + dirt + clay each), 8 cast-iron ingots (Novo's loot table; later Kessler's counter), 4 logs | the **cannon cast** and the very-small and cannon-end moulds (the yard's Create saw cuts them from logs); the yard's basins pour molten cast iron |
| G2 | The first pour | II | camp — the yard | G1 | pour a cast in the yard: cannon cast + mould + molten cast iron → an unbored cast-iron barrel and a cannon end | `gun_cast` stage; Walker's crane (the rope pulley over the cast pit) |
| G3 | The bore | II | camp — the yard | G2 | the **cannon drill** (andesite casing, piston pole, fluid pipe) and a drill bit on the yard's hand-cranked boring frame (slow: a barrel takes four minutes; the plant's boring mill does it in one after S-plant-2); bore two barrels and a chamber | bored cast-iron barrel, chamber, end; `gun_bored` |
| G4 | Mount and charge | II–III | camp — the gun pit | G3, Walls 1 | the **cannon mount** in the gun pit with a hand crank on its pitch face and a **yaw controller**, the **cannon loader** with a ram head and a worm head, a lever on the firing face, 8 powder charges (packed gunpowder = 3 gunpowder compacted, in a wool charge), 4 solid shot | the first gun: end + chamber + 2 barrels; **fire it**: CBC's own advancement is the task. Laid by rotation, fired by redstone, read on goggles — no seat, no sight (owner, 2026-09-05) |
| G5 | The gunner's manual | III | the block | S-block-1, G4 | hand in the manual (Vera) and 2 spyglasses | the **range card**: a Patchouli book per gun, pitch and charges to range (the mod ships none); the pit's display board (a Create display link from the mount, Tune's U-B2) and the range rings on the map wall |
| G6 | Steel | III | FR-06 T2 (the cast iron now pours at Novo's foundry, S-novo-2, four barrels a pour) | S-fr06-2, S-novo-2, G5, `fr06_defended` | 24 steel ingots (IE steel, `forge:ingots/steel`) melted at Novo, poured as steel barrels; the **cannon builder** at FR-06 wraps built-up layers | the long gun: steel chamber + 5 barrels; the quick-firing breech |
| G7 | Shells | III–IV | the plaza T2 | S-plaza-2, G6 | mechanical crafters: 4 HE shells, 2 AP shells, 2 shrapnel; fuzes: impact (fuze head + redstone), proximity (iron bars, quartz, iron, redstone) | shells and fuzes as station orders; the smoke shell for the Woods |
| G8 | The battery | IV | FR-06 T3, the gatehouse T3 | S-fr06-3, R-B3 | a bronze **autocannon** with handles (breech extractor by sequenced assembly, recoil spring, 3 barrels; big cartridges pressed from brass sheets) on each watchtower — the one gun a player holds, the mod's point-defence design; an ammo container of AP rounds | Walls 3 = the autocannon nests (they replace the laser tower); the crater's last line has guns on it |
| G9 | The carriage | IV | Walker T3 | G6, W-B3 | the **cannon carriage** (shafts, planks, a pair of cannon wheels from the yard) and a second gun for it; tow it with the truck (IV); emplaced, it is laid and fired like the pit gun | a mobile gun for the counterattack fields and the finale |
| G10 | Nethersteel (optional) | IV | the tower | tower stage 4 | nethersteel (steel + nether material mixed superheated) — the finale gun: thick chamber, nethersteel layers | the shot that opens the Sleeper's vault (finale doc): the finale's shell is the gun's last job |

Ammunition economy: gunpowder is Superb Warfare's/vanilla's; **nitropowder and guncotton** (CBC's better propellants,
mixed from nitrate and cotton) are Teddy's (7A) — his explosives chapter already owns everything that goes bang, so the
propellant blueprints are his H-series rewards, not a new vendor.

**Operating the gun is the mod's, not ours** (owner, 2026-09-05: no direct control). Laying is rotation on the
mount (crank or gearshift) and the yaw controller; assembly and firing are redstone on the mount's faces; the lay is
read on goggles or a display board; the crew is players — one lays, one loads, one fires — and fall of shot is watched
by eye and on voice. No seat, no sight, no spotter NPC. What the design adds is the gates, the range card (G5), the pit
board and the wall's rings; every mechanism has the mod's own Ponder scene.

What the gun is for in play: the counterattacks arrive at the camp gate (design §6.2) along known lines; a gun in the
pit with shrapnel shells makes the fortify clock's last ten minutes an artillery problem, which is the immersive part
the feedback asked for. The finale (the Sleeper) needs G10's shot to breach; without the gun the tower's last stage
stays closed — the gun is the map's second spine after the tower.

## 5. What changes elsewhere (pointers, applied when the fork is adopted)

- `gscraft-map-design.md` §2.3: keeper column added to the strongpoint table; §3.6: the site tiers reference this doc;
  §6.1 "held" adds the keeper summon; §8 tech stack lists Create, CBC, RPL.
- `gscraft-quests.md`: §7.2 Walls 2 mortar → autocannon (G8); new §7.6 The Gun (G1–G10) and §8 site chains S-*;
  quest count 136 → 136 + 10 + 18 = 164.
- `gscraft-crafting.md` §2.1: the CBC parts as station orders and blueprints (Create's bench recipes → Walker's
  blueprints); §4.3 propellants under Teddy.
- `gscraft-vendors.md`: the six keepers' counters.
- `gscraft-camp-spec.md`: `site.py` (templates per site and tier, keeper summons) beside `camp.py`; the gun pit on the
  crater rim in the camp's tier-0 layout.
- `gscraft-modpack-review.md` and `build/manifest.json`, `build/additions.json`, `build/packwiz`: the three jars.
- `gscraft_recipes.js`: Walls 2 mortar strip stays; Create's crafting-table recipes for machines are removed and come
  back as Walker blueprints (Phase C); CBC's crafting-table recipes for mounts, loaders, fuzes and shot are removed and
  come back as the keepers' station orders.
