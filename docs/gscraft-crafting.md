# GSCraft Wasteland — Crafting, Stations and Vehicles

Draft 1, 2026-09-03. Companion to `gscraft-map-design.md` (draft 6) and `gscraft-quests.md`
(draft 3). Five things are settled here: the capability audit of the quest book, the vehicle roster
and how each is built, the crafting timer, server-placed crafting with an upgradable workshop, and
the equipment crafting system that replaces looting as the source of gear.

**Decisions (owner, 2026-09-03):** every capability a quest needs is taught by an earlier quest;
every vehicle the game uses has a recipe; small items craft in seconds, mission-critical items take
about one trip so the results are waiting when the players get back; crafting happens only at
server-placed stations, one per player, plus the workshop in the camp, which upgrades; and every
piece of equipment — weapons, ammunition, armour, tools, packs, vehicles — is crafted from the
item ladder, so loot supplies parts and not products.

---

## 1. Capability audit of the quest book

Every quest that needs the players to *have* something was traced back to the quest that gives
them the way to make it. Five holes and one loop, all fixed in quests draft 2; two more (the motor-assembly blueprint, the battery-pack gates) on 2026-09-04.

| Capability | First quest that needs it | Taught by | Finding |
|---|---|---|---|
| Motor assembly | W7 (hand in 1) | **was Garage 1 = W7's own reward, a loop**; the blueprint is now W6's (Workshop 2) — fixed 2026-09-04 | fixed |
| Battery packs (truck, speedboat, drones, LAV-150, Humvee, Black Hawk, Bradley) | W9, J5, D2, D4, W-M1, W-B3, X6 | M-B2 (small), M9 (medium), M13 (large) — **the consuming quests now gate on them** (2026-09-04); the truck takes a small pack | fixed |
| Workbench and blueprint crafting | W2 (craft fastener kits) | W1 binds the personal station (§4) and hands out the first blueprints | fine |
| Backpack | W2 onward | W2, Storage 1 | fine |
| Hand tools (wrench, welding torch, hand drill) | W-A1 (wrench in the tool slot), W3 (torch), steel frame (torch held) | **were loot only** | **fixed:** W1 now also gives the hand-tool blueprints; tools remain a rare loot find but are never required from loot |
| Med kits, harnesses, filters, circuit assemblies | T2, M2, M3, U2 | T1, M1, U1 | fine |
| Concrete (D1, D4, every `*-B` tier) | D1 | vanilla recipe, runs at any station | fine |
| A car | J4 (by car), M8 and U4 (gate W7), R5 (`car_built`) | W7, Garage 1 | fine; W7's reward now includes a full tank and 2 fuel cans so the first car moves before the fuel chain (W8/M5) exists |
| Fuel | every vehicle | M5 → W8 (biodiesel chain, fuel cans) | fine; fuel cans also drop at the plant as before |
| A truck | W10 (truck cargo), the bulky hauls | W9, Garage 2 | fine |
| A boat | W12 ("reach the settlement by water"), J5 | **J5 handed out a boat as a gift; no recipe anywhere** | **fixed:** new W-V1 "Something that floats" (boat blueprint, Garage 1); J5's reward is now the speedboat blueprint |
| Aircraft | J7 (reach the hub **by air**), W13 (aircraft recipe) | **W13 was gated on J7 and J7 on W13 — a loop nobody could enter** | **fixed:** W13 gates on W9, M11, **J6** (the runway); J7 stays gated on J6 and W13 |
| Firearms, ammunition, attachments | from the first night; the assaults and defences | **nothing taught them; the pack's own gun-smith and reforge tables were the implied route** | **fixed:** Walker's armoury line W-A1…W-A4 (§5), plus a starting sidearm and 30 rounds from Custom Starting Gear |
| Body armour | the assaults | nothing | **fixed:** W-A2 |
| The claim marker | R2 and every re-take after a loss | R1 handed out one item | **fixed:** R1 gives the marker *blueprint*; a lost site's marker is re-crafted, not begged from Marshall |
| Guard villagers, PlayerRevive, waypoints | D2, T8, U2 | rewards flip stages | fine |

Rule going forward: **a quest may ask for an item only if an earlier quest in some chapter has
handed out its blueprint, or it is a loot-only component.** The trip table in the design (§3.5)
and the gates in the quest book are the check.

---

## 2. Vehicles

Every vehicle in the two Immersive Vehicles packs and in Superb Warfare was enumerated from the
jars. The game uses eleven (eight civilian below, three military in §2.1); the rest are removed from crafting and never appear in loot.

| Tier | Vehicle | Id (verified in the jar) | Seats / cargo | Role | Recipe from |
|---|---|---|---|---|---|
| Garage 1 (W7) | **Quad** | `mts:mtsofficialpack.quad` | 1 / small | the first wheels: fast over rubble, no cargo | W7 |
| Garage 1 (W7) | **Runabout** (2CV-class) | `mts:oamp.cagouille` | 2 / a crate | the first car: the spine, the west edge | W7 |
| Garage 1 (W-V1) | **Boat** | `minecraft:oak_boat` → `superbwarfare:speedboat` (J5) | 2 / — | the settlement by water; the lakes between the district and the runway | W-V1, J5 |
| Garage 2 (W9) | **Van** | `mts:oamp.ecoline` | 3 / 27 slots | the loot hauler | W9 |
| Garage 2 (W9) | **Truck** | `superbwarfare:truck` | 2 / bulky bay | complete parts and components home | W9 |
| Garage 3 (W13) | **Light aircraft** (Cessna-class) | `mts:mtsofficialpack.mc172` | 4 / 27 slots | the runway to the hub | W13 |
| Garage 3 (W-B3) | **Light helicopter** | `mts:mtsofficialpack.bell47g` | 2 / small | the hub and the cities without a runway | W-B3 (the shed) |
| Walls 3 (D4) | **Armoured car** | `superbwarfare:lav_150` | 4 / — | the finale's gate defence; optional | D4 |

Two further Superb Warfare add-on packs are in the jar set — **vvp** (56 entities: Mi-24, Black Hawk,
Strykers, Bradleys, Pantsir) and **MCSP** (25: Humvees, BMD-4, Bradleys) — 44 more
`vehicle_assembling` recipes between them. Three of them are the military tier of §2.1 (blueprint-gated);
every other one is stripped.

Removed from the game's recipes (KubeJS strips their recipes; their containers are not in any loot
table): the fighting vehicles and artillery (`bmp_2`, `yx_100`, `type_63`, `plz_05`, `tom_6`,
`ah_6`, `mi_28`, `a_10a`, `prism_tank`, `annihilator`, `bl_132`, `mle_1934`, `hpj_11`, the two
towers, `mk_42`) and the IV vehicles with no role (`ft17`, `firetruck`, `gmcbrig`, `merc230`,
`fordmustang69`, `scout`, `bell206`, `comanche`, `e500`, `pzlp11`, `pzl37los`, `skyhawk`,
`trimotor`, `vulcanair`, `camaro`, `escargot`, `highwayman`, `luxorama`, `stationmerc`, `vwbus`,
`wheel_chair`).

**How the recipes exist.** Immersive Vehicles crafts at its own benches from `materialLists` in
each pack, and the mod ships a **`config/mts/craftingoverrides.json`** (the class is in the jar)
that replaces those lists per vehicle — so the five IV vehicles get our intermediates without
touching the packs. Superb Warfare's vehicles are plain datapack recipes
(`superbwarfare:vehicle_assembling`, 24 of them in the jar), so KubeJS rewrites the three we keep
and removes the rest. Both benches — the IV vehicle bench and the SW assembling table — live
**only in Walker's yard**, appearing at tier 1 and tier 2 respectively (§4). Both benches craft
on click, so the timer lives one step earlier: the station's trip-length order produces a
**vehicle kit** (one KubeJS item per vehicle, from the recipe below), and the kit is the only
ingredient the bench recipe asks for. The trip is spent on the kit; the bench turns it into the
vehicle in a second.

| Vehicle | Recipe (intermediates from the design §4.3, plus the new ones in §5.1) |
|---|---|
| Quad | 2 steel frame, 1 motor assembly, 4 wheel, 1 fuel tank |
| Runabout | 4 steel frame, 1 motor assembly, 4 wheel, 1 fuel tank, 1 wiring harness, 2 glass |
| Boat | 12 planks, 1 fastener kit (speedboat: + 1 motor assembly, 1 small battery pack, 2 steel frame) |
| Van | 6 steel frame, 1 motor assembly, 4 wheel, 1 fuel tank, 1 wiring harness, 1 cargo crate |
| Truck | 8 steel frame, 1 **heavy diesel engine** (Novo), 6 wheel, 1 small battery pack, 1 cargo crate |
| Light aircraft | 8 steel frame, 1 **avionics module** (FR-06), 2 motor assembly, 2 wheel, 2 fuel tank, 2 circuit assembly, 4 glass |
| Light helicopter | 6 steel frame, 1 **avionics module**, 1 **transformer core**, 2 motor assembly, 2 fuel tank, 1 circuit assembly |
| Armoured car | 12 steel frame, 4 plate (§5.1), 1 heavy diesel engine, 6 wheel, 1 medium battery pack, 1 **reactor control module** |

Every vehicle from the truck up needs a loot-only component, so the upper garage tiers are trips
to a held site — the same rule as the tower parts.

### 2.1 The military tier (vvp, MCSP — kept, owner 2026-09-03)

Three vehicles from the two Superb Warfare add-on packs sit above the civilian garage; everything
else in those packs is a static wreck at a strongpoint (design §2.3), placed dead and never craftable.

| Blueprint from (owner, 2026-09-04: quest rewards, mid/late game) | Vehicle | Id | Role | Bench |
|---|---|---|---|---|
| **W-M1 Motor pool** (Act III, after FR-06 and the plaza are both defended) | **Humvee RWS** | MCSP `humvee_rws` (green) | the gate's armed car, turret on the roof; beside the LAV-150 | SW assembling table, yard tier 2 |
| **W-B3 The shed** (Act IV) | **UH-60 Black Hawk** | vvp `uh60` | the heavy helicopter: six seats and cargo, the whole team to the hub | SW assembling table, yard tier 3; the Bell 47 stays as the two-seat scout |
| **X6 Antenna array** (Act IV, the beacon) | **M3A3 Bradley** | MCSP `m3a3` | the armoured vehicle for the finale's base defence - built, not given | SW assembling table, yard tier 2 (the table exists from tier 2; the blueprint is the gate) |

The military tier is **blueprint-gated, never tier-unlocked**: the three vehicles have recipes (below), but each
recipe is locked behind a blueprint item that only a quest hands out, in the same way the IE workbench
blueprints work for the intermediates. No blueprint, no recipe in the bench - so the yard's tier says what the
bench can do and the quest book says when. Reaching a yard tier never unlocks a military vehicle by itself.

| Vehicle | Recipe |
|---|---|
| Humvee RWS | 10 steel frame, 6 plate, 1 heavy diesel engine, 4 wheel, 1 medium battery pack, 1 **military circuit board**, 1 gun frame + barrel (the turret) |
| Black Hawk | 12 steel frame, 2 **avionics module**, 1 **transformer core**, 4 motor assembly, 1 large battery pack, 2 circuit assembly, 1 **satellite receiver** |
| M3A3 Bradley | 16 steel frame, 8 plate, 1 heavy diesel engine, 1 large battery pack, 1 **reactor control module**, 1 **military circuit board**, 1 gun frame + barrel (the 25 mm), 2 wiring harness |

All three are electric under Superb Warfare and draw from the battery packs of §5.4 - so their recipes carry battery packs, not fuel tanks (owner default, 2026-09-04); the exact registry ids are
read off the jars at Phase D (`vvp:` and `mcsp:` namespaces, 81 entities between them).

---

## 3. The crafting timer

There was no timer: the Engineer's Workbench crafts on click. This replaces it. Every recipe is a
**work order** at a station (§4): ingredients in, order placed, a countdown runs on the server,
the result appears in the output slots. The player leaves; the station works.

The lengths are set from the trip table (design §2.5 and §3.5). A round trip with looting is
about 20 minutes in every act — 1.5 km on foot in Act I, 2.5 km by car in Act II, the far ring by
truck in Act III, the hub by air in Act IV all land there — so a "trip-length" order is 20 min,
and the results are waiting when the team comes home.

| Class | What | Time at a personal station | Feel |
|---|---|---|---|
| Quick | ammunition, bandages, concrete, planks, wheels, cloth, casings, powder | 10–30 s | done while you stand there |
| Intermediate | fastener kit, steel frame, harness, filter cartridge, circuit assembly, med kit, gun frame, barrel | 2 min | start it, sort the loot, collect |
| Equipment | firearms, armour, tools, attachments, packs | 5 min (tier 1 gear) to 10 min (tier 3) | start it before a short errand |
| Trip-length | complete parts, vehicles, base upgrade kits, the claim marker | **20 min** | one trip out and back |
| Tower parts | the five hand-ins for stages 1–5 | 20 min (a trip-length order) | a long trip, or two |

Workshop tiers (§4) cut these: ×0.85 at tier 1, ×0.7 at tier 2, ×0.5 at tier 3 — so a tower part
is 10 minutes at the finished workshop, still a trip. Nothing ever crafts instantly except the
Quick class; there is no way to buy time back with more ingredients.

---

## 4. Stations, and the workshop

**Crafting happens only at server-placed stations.** The vanilla crafting table is inert (its
recipe is removed and right-clicking one does nothing — Lost Cities is full of them), the
Engineer's Workbench recipe is removed, and no other mod's bench is craftable. Three kinds of
station exist:

| Station | How many | Where | Who |
|---|---|---|---|
| **Personal work station** | one per player, bound to that player by W1's reward | anywhere inside the camp outline or the team's claim | given on first join by Custom Starting Gear (already in the pack), re-issued by Walker if lost; a second one cannot be placed while the first exists |
| **Workshop benches** | tier 1: 1, tier 2: 2, tier 3: 3 | Walker's yard | shared; anyone on the team may place or collect an order |
| **Vehicle benches** | the IV bench (tier 1) and the SW assembling table (tier 2) | Walker's yard | shared; vehicle orders only |

Every station has a **tool slot**: recipes the design wrote as "torch held" or "wrench held" read
the tool from that slot and take one point of its durability per order, since nobody is standing
there when the order finishes. A **blueprint** is not an item any more: it is a team stage
(`bp_<recipe>`) that the quest reward sets, and a station only accepts orders for recipes whose
stage the team holds. The book shows the recipe on the quest that grants it.

A personal station takes one order at a time. A workshop bench takes one order at tier 1, a
queue of two at tier 2 and three at tier 3. For a team of five, a tier-3 yard is eight
orders in flight plus the vehicle benches, which is the ceiling the timers were tuned against (a smaller team has fewer stations and the same timers, so it simply runs fewer orders at once): a
full tower stage (six steel frames, eight fastener kits counting the frames' own, the kit itself) is fourteen
intermediate orders across the team's stations and one trip-length order, and a team that plans it starts the intermediates before leaving and
the kit when they return.

**The workshop is Walker's yard, tiers 0–3 as already designed (design §3.6).** Its tiers now
carry the crafting bonuses, so the building the players see grow is the one that works faster:

| Yard tier | Benches | Queue per bench | Speed | Efficiency |
|---|---|---|---|---|
| 0 — scrap piles | none; personal stations only | 1 | ×1.0 | — |
| 1 — roofed workshop, one bay | 1, plus the IV vehicle bench | 1 | ×0.85 | — |
| 2 — two bays, gantry, lights | 2, plus the SW assembling table and the Salvaging Table | 2 | ×0.7 | 25 % chance an order refunds one small item |
| 3 — steel shed, vehicle lift | 3 | 3 | ×0.5 | 50 % refund chance; Quick orders yield double |

The efficiency roll is the balancing lever: it is applied per order, on the output side, and never
reduces a recipe's stated cost, so the recipe sheet stays true and the yard's value is felt in
volume over a session rather than in cheaper single crafts. The bonuses apply to every station
the team owns, personal ones included, because the tier is a property of the team's workshop
stage, not of the block.

**Implementation, no custom mod.** The station is a KubeJS custom block with a block entity
(KubeJS 2001.6.5 ships `BlockEntityBuilder`, an inventory and a server ticker — verified in the
jar): nine input slots, one output row, an order in NBT (recipe id, ticks remaining, owner). A
server script matches the inputs against the `gscraft` recipe list, sets the countdown from the
class and the workshop stage, ticks it, and moves the result out. Personal binding and the
one-per-player rule are the same script; the workshop stage is a team stage set by the `W-B`
quests. IV and SW vehicles keep their own benches because their items are placed as entities by
their mods; the yard template places those benches and the lock keeps them there.

---

## 5. Equipment crafting

**Loot supplies parts; the station supplies products.** Working guns, attachments, armour, packs
and vehicles come out of loot tables; small items, the new intermediates below, and *salvage*
go in. The pack's own routes — the TaCZ gun-smith table, Superb Warfare's reforge table and
blueprints, the IV benches outside the yard — are closed: their recipes are removed and their
blocks are not craftable.

### 5.1 The new intermediates

| Intermediate | Recipe | Blueprint from |
|---|---|---|
| Gun frame | 3 metal scrap + 1 fastener kit; wrench in the tool slot | Walker, W-A1 |
| Barrel | 2 metal scrap; hand drill in the tool slot | Walker, W-A1 |
| Trigger group | 4 screws + 2 nails + 1 metal scrap; screwdriver set in the tool slot | Walker, W-A1 |
| Plate | 4 metal scrap + 1 duct tape; welding torch in the tool slot | Walker, W-A2 |
| Concrete (×8) | 4 gravel + 4 sand + 1 water bucket | any station, no blueprint; Quick |
| Wheel | 2 metal scrap + 1 silicone tube | Walker, W7 |
| Fuel tank | 4 metal scrap + 1 sealed tubing | Walker, W7 |

**Salvage** is what loot gives instead of a gun: a *damaged* weapon, one item per class (e.g. "damaged rifle"), that counts as a gun frame + barrel in any recipe of its class. The **Apotheosis Salvaging Table in Walker's yard (tier 2)** is where salvage is broken down into parts (owner default, 2026-09-04: the mechanic is the mod's, the input is ours). Ammunition drops
in loot in small amounts as before; casings and powder are craftable so it never runs dry.

### 5.2 Weapons — Walker's armoury line

TaCZ's default pack is the source of guns (54 in the jar across pistols, rifles, shotguns,
SMGs, snipers, MGs and launchers). One gun per class per tier is craftable; ids are the default
pack's and are pinned in the recipe file at Phase C.

| Tier | Quest | Unlocks | Recipe shape |
|---|---|---|---|
| 1 | **W-A1 Sidearm** (Act I, after W1) | pistol, pump shotgun; pistol and shotgun ammunition; the salvage rule | gun frame + barrel + trigger group + 4 planks (stock); ammo: 8 casings + 1 powder + 2 metal scrap → 30 rounds (Quick; casings and powder §5.6) |
| 2 | **W-A2 Plates** (Act I–II, after W3) | scrap vest and helmet (§5.3); rifle ammunition | plate ×4 + duct tape → vest |
| 2 | **W-A3 Long guns** (Act II, after `novo_defended`) | assault rifle, SMG; iron sights, extended magazine | 2 gun frame + barrel + trigger group + 1 steel frame; attachments: circuit-free, metal scrap and tape |
| 3 | **W-A4 Precision** (Act III, after W9) | sniper rifle, machine gun, the launcher; optics, suppressor | + 1 circuit assembly (optics), + 1 **military circuit board** (the launcher, from Financial Plaza) |

### 5.3 Armour, tools, packs

| Item | Tier | Recipe | Notes |
|---|---|---|---|
| Scrap vest / scrap helmet | 1 (W-A2) | 4 plate + 1 duct tape / 2 plate + 1 cloth | KubeJS armour items, leather-to-chain protection |
| Plated vest / plated helmet | 2 (after `plant_defended`) | 6 plate + 1 steel frame / 3 plate + 1 steel frame | iron-class |
| Composite vest / composite helmet | 3 (after `fr06_defended`) | 8 plate + 2 steel frame + 1 **transformer core** / 4 plate + 1 circuit assembly | diamond-class; the core is the FR-06 trip |
| Hand tools | 0 (W1) | wrench 3 metal scrap; pliers 2; screwdriver set 2 + 1 planks; hand drill 4 metal scrap + 1 wire spool + 1 duct tape (hand-cranked); welding torch 4 metal scrap + 2 silicone tube (gas torch) — all from the camp's ruins (C2 fix, 2026-09-04) | tools stay in loot as rare finds |
| Backpacks | Storage 1–4 (W2, W6, W10, W13) | basic: 6 cloth + 2 duct tape; iron: + 4 plate; gold: + 1 steel frame + 1 **heavy anchor cable**; diamond: + 1 **satellite receiver** | Sophisticated Backpacks' own recipes are replaced |
| Cloth | Quick | 2 wool or 4 string → 1 cloth | the one new Quick item |

### 5.4 Power for the electric vehicles

Superb Warfare's truck, speedboat and LAV-150 carry no fuel: they run on **battery packs** charged at the
**Charging Station**, which is Michael's — it appears in his plant at tier 2 (M-B2) and draws from
the IE power the Generator function provides. Packs are crafted at the station like anything else:

| Item | Recipe | Class | Blueprint |
|---|---|---|---|
| Battery (SW `superbwarfare:battery`) | 2 metal scrap + 1 car battery + 1 wire spool | Intermediate | Michael, M-B2 |
| Small battery pack | 4 battery + 1 steel frame + 1 wiring harness | Equipment | Michael, M-B2 |
| Medium battery pack | 2 small packs + 1 steel frame + 1 circuit assembly | Equipment | Michael, Generator 2 |
| Large battery pack | 2 medium packs + 1 **transformer core** | Trip-length | Michael, Generator 3 |

A charged small pack drives the truck one round trip to the district, or the speedboat for a session;
the LAV-150 and the Humvee take a medium pack, the Black Hawk and the Bradley a large one. SW's own pack-assembly recipes are replaced by these; the Charging Station
itself is placed by the M-B2 template, never crafted.

### 5.5 What changes in the loot tables

- The `keerdm_zombie_essentials` `_tacz` chest tables — the ones that put working guns in Lost
  Cities chests — are overridden by the datapack (as the `_vics` tables already are) to drop
  salvage, ammunition and small items.
- Attachment and armour loot is removed; SW's containers, blueprints and material packs are
  removed from every table.
- Tools keep a rare slot. Components keep their site containers. Nothing else changes.

### 5.6 The rest of the sheet (C1, C2 — 2026-09-04)

Recipes the quests assumed and no sheet carried, plus the three sequencing fixes of gap audit C2.

| Item | Recipe | Class | Blueprint from |
|---|---|---|---|
| Empty fuel can | 2 metal scrap + 1 sealed tubing | Intermediate | Walker, W7 (W7 is now gated on **M3**, Water 1, so sealed tubing exists — C2) |
| Fuel can (full) | empty can at the plant's pump (M-B2), or the ranger's still: 1 motor oil + 1 empty can (M-W1) | — | Walker, W8 (refill at Michael's pump, M-B2) / Michael, M-W1 |
| Cargo crate | 4 planks + 2 metal scrap + 1 fastener kit | Intermediate | Walker, W7 |
| Boat cargo | 1 cargo crate + 2 planks + 1 fastener kit | Intermediate | Walker, W12 |
| Truck cargo | 2 cargo crate + 2 steel frame | Intermediate | Walker, W10 |
| Aircraft cargo | 1 cargo crate + 1 steel frame + 1 cloth | Intermediate | Walker, W13 |
| Claim marker | 4 steel frame + 1 circuit assembly + 1 wiring harness + 1 white banner | Trip-length | Marshall, R1 (re-crafted after a loss) |
| Casings (×16) | 2 metal scrap | Quick | Walker, W-A1 |
| Powder (×4) | 1 gunpowder + 1 solvent | Quick | Walker, W-A1 (gunpowder is a small item: the stone complex, military chests) |
| Ammunition (×30) | 8 casings + 1 powder + 2 metal scrap | Quick | per class with the gun's blueprint |
| Timber barricade | 6 planks + 1 fastener kit | Quick | Walker, W-W1 (the Woods) |
| Poultice | 2 sweet berries + 1 bandage | Quick | Tony, T-W1 |
| Ration pack | 4 Farmer's Delight meals | Quick | Marshall, D6 (Farm 3) |
| Flashlight battery | 1 car battery → recharge | Quick | any station; or the charging station (M-B2) |

**Sequencing fixes (C2):** the welding torch is now 4 metal scrap + 2 silicone tube and the hand
drill 4 metal scrap + 1 wire spool + 1 duct tape (§5.3), both from the camp's ruins, so W3 and W-A1
need nothing from Act II; the fuel tank's sealed tubing is covered by W7's new gate.

### 5.7 Station orders for the mods' items (C15)

| Group | Orders (Superb Warfare / Sophisticated Backpacks / ParCool ids verified in the jars) | Blueprint from |
|---|---|---|
| **Walls 1** | `superbwarfare:sandbag` ×4: 2 cloth + 4 sand; `superbwarfare:barbed_wire` ×2: 3 metal scrap; `superbwarfare:claymore_mine`: 2 metal scrap + 1 gunpowder + 1 wire spool | Marshall, D1 |
| **Walls 2** | the mortar (`mortar_barrel` 2 steel frame; `mortar_base_plate` 1 steel frame + 4 metal scrap; `mortar_bipod` 4 metal scrap; the `mortar_deployer` from the three) and `mortar_shell` ×2: 2 metal scrap + 2 powder (Quick); `superbwarfare:drone`: 1 circuit assembly + 1 motor assembly + 1 small battery pack; `swarm_drone` ×2: 1 circuit assembly + 4 metal scrap | Marshall, D2 |
| **Walls 3** | the laser tower (`superbwarfare:laser_unit` + 4 plate + 2 circuit assembly + 1 transformer core); `superbwarfare:fumo_25` (radar): 4 steel frame + 2 antenna element + 1 military circuit board; `superbwarfare:c4_bomb`: 4 powder + 1 circuit assembly + 1 duct tape; `superbwarfare:jump_pad`: 2 steel frame + 1 medium battery pack | Marshall, D4 |
| **Storage 1** | `sophisticatedbackpacks:backpack` (basic: 6 cloth + 2 duct tape) | Walker, W2 |
| **Storage 2** | iron backpack (basic + 4 plate); `stack_upgrade_tier_1` ×2: 2 steel frame + 1 fastener kit; `magnet_upgrade`: 1 circuit assembly + 2 metal scrap | Walker, W6 |
| **Storage 3** | gold backpack (+ 1 steel frame + 1 heavy anchor cable); `everlasting_upgrade`: 1 circuit assembly + 1 transformer core; `feeding_upgrade`: 1 circuit assembly + 4 canned goods; `pickup_upgrade`: 2 metal scrap + 1 wire spool | Walker, W10 |
| **Storage 4** | diamond backpack (+ 1 satellite receiver); `tank_upgrade`: 2 steel frame + 1 sealed tubing; `void_upgrade`: 1 circuit assembly + 1 solvent; `inception_upgrade` is J11's reward only | Walker, W13 / J8 |
| **Ziplines** | `parcool:zipline_rope`: 4 string + 2 metal scrap (Quick); `parcool:iron_zipline_hook` ×2: 2 metal scrap + 1 fastener kit — the lookout tier 3 and the tower's 64-metre platform get hooks placed by their functions; the rope is the players' | James, J-B2 |

Every other Sophisticated Backpacks, ParCool and Superb Warfare recipe stays stripped (`gscraft_recipes.js`).
The Immersive Vehicles override file is still Phase C's in-game find (mod-capabilities §5b); if none
materialises, the fallback is that the station order for an IV vehicle yields the vehicle item itself
(KubeJS gives it on completion) and the IV bench is removed from the yard.

---

## 6. What this adds to the quest book

Six quests and seven reward/gate edits, all in quests draft 2: W-A1…W-A4, W-V1, W-M1; W13's gate, W7's
reward, R1's reward, J5's reward, W1's reward, W-B3's and X6's rewards (the military blueprints). One hundred and twenty-nine quests (the Woods chain, the bunker side quests, Farm 2/3, X6b and the placed-structure quests added 2026-09-04).

Related: `gscraft-map-design.md` §3.6 (Walker's yard tiers), §4 (the item ladder),
`gscraft-quests.md` §2 (Walker), `build/kubejs/` (the station script, Phase C).
