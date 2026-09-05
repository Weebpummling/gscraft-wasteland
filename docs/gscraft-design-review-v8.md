# GSCraft Wasteland — design review on the final v8 sectors

2026-09-05. Sources: `gscraft-map-plan-v8.md` (plan), `gscraft-map-design.md` (design), quests, crafting, vendors, camp spec, enemies, finale, loot, onboarding, the Create chapter (create), interface, gaps §E. Distances are straight-line from the camp centre (−1600, −2300); minutes from design §2.5.

## 1. Verdict

1. The loop holds on the final geography: every strongpoint is 1.0–2.4 km out, every counterattack comes home, and design §4.4 still maps one site to one tower stage.
2. What breaks it is the documents E1 did not reach: quests §7.1 still runs R2 = Novo first and gates R3 on `novo_defended`; T3–T5, J-S2 and design §6.3 label the block Act II; onboarding §2 "Session 2" sends the team to Skadowsky with Novo's W5/W6. As written, Act I ends 2 km out on foot.
3. The crater is gone (plan §9: "open ground at y 88") but six documents still build on it (§7, N2).
4. The camp ring (plan §9, design §2.2) sits on plan §9's box x −1690…−1290; on the final rectangle (x −1792…−1409) the gatehouse, the lookout, the gun pit and half the yard are outside the camp.
5. Four strongpoints and the hub sit at 2.0–2.4 km, so enemies §7's distance rings no longer separate acts.
6. The river, not the lake, is the barrier: it runs from the lake down Skadowsky's west side (plan §5), so the Line crosses it in Act I, and FR-06 and the plant sector are on Skadowsky's bank, reachable by road.
7. The v6 small-site layer (loot §5: glass tower, acacia hall, copper tower, prismarine hall, stone complex, mud village) was never rebased; nine quests point at buildings v8 lacks.
8. The blueprint-card model (E15) starves parallel crafting unless every player holds a card (§4).
9. The economy, the gun chain, the site chains and the interface ladder are sound and need only the label pass.
10. §8 ranks the fixes; the first four block Phase C.

## 2. Pacing on real distances

| Act | Trip, one way | km | Walk min | Car street / rubble | Session estimate (quests §1) |
|---|---|---|---|---|---|
| I | the settlement; the runway; the library; Skadowsky (edge / centre, down the Line) | 0.6; 1.4; 1.7; 1.0 / 1.4 | 2.3; 5.5; 6.6; 4 / 5.5 | — | 1–2 holds: trip 2 (settlement → runway → home) is 4 km, 16 min; Skadowsky is four or five walks plus the 40-min clock |
| II | Novo; Financial Plaza; hempcrete; Bio Gen; Teddy | 2.0; 2.4; 2.0; 1.9; 1.8 | 7.7; 9.3; 7.7; 7.7; 7 | 1.6 / 4.2 (Novo); 1.9 / 5.0 (plaza) | 3–5 holds but is front-loaded: the first car needs `novo_defended` (W6 → W7), so Novo's scout, loot runs and take are five foot round trips of 16–19 min |
| III | FR-06 / the plant sector: straight; by road through Skadowsky | 2.2 / 2.4; ~3.0 | 11.7 by road | boat 4.6 straight; car 2.4 / 6.3 | 6–9 is long: two sites at 2.4 min by car, two 40-min clocks and the S-chains are three sessions |
| IV | the hub (edge / centre); the plant complex | 1.9 / 2.4; 2.9–4.1 | — | 1.9; 2.3–3.3; aircraft 0.9–1.2 | 10–12 holds only because loot §6's 100-min refresh forces three hub visits; the far band has one quest, U-D3 |

**The Line as the Act I spine.** 1.2 km, six stops (design §2.6, E6): the right length. The final map puts the river between the camp and Skadowsky (plan §5), so the pump house (L2) is at the crossing and the Line needs a ford no step-8 item lists; and R3 must stop gating on `novo_defended` (quests §7.1).

**The lake as the Act III barrier.** It is not one. FR-06 and the plant sector lie 1.6 and 1.4 km from Skadowsky's centre along the plant road (plan §3–4); the car route is 3 km at 2.4 min, the boat 2.2 km straight at 4.6 — slower. The boat quest is early enough (W-V1 at Garage 1) but has no job the runabout's crate does not do (design §4.5): give it the pre-truck bulky haul across the lake, or cut W12 and J5.

## 3. The strongpoint ladder per site

| Site (plan §4) | Scout / loot / take / hold | Component, demand (design §4.4, the recipes) | Keeper (create §3) | Fit |
|---|---|---|---|---|
| **Skadowsky** 1.4 km SE | J-S2 / T3 / R3 / T4–T5 | medical analyzer ×3 — the clinic only | Vera: field hospital → hospital (second revive) → rail yard, the train | Fits: the Line, the rail and the viaduct end here. T3 says "1.9 km", Act II; design §6.3 gives it the heaviest counterattack (20/25/30 + 8 spiders) though it is now the first fight at a tier-0 gate |
| **Novo** 2.0 km SW | J-S1 / W5 / R2 / W6 | anchor cable ×4, diesel engine ×7 — one each per 40 min held | Kessler: the foundry | Fits, feeds G1/G6. Its south edge is 33 blocks from the hub's |
| **Financial Plaza** 2.4 km SW | J-S5 / U4 / R5 / U5–U7 | military circuit board ×8, encrypted radio ×3 | Ilya: the fuze lab | Fits. R5 bundles it with FR-06 behind R4 and `car_built`; under E1 it is Act II, its own take |
| **FR-06** 2.2 km E | J-S4 / M8 / R5 / M9–M11 | transformer core ×9, reactor control ×5, avionics ×6 — three per 40 min | Rook: the steel works | Fits: the biggest build as the Militia's base, the hangar, the mechs |
| **The plant sector** 2.4 km ESE | J-S3 / M4 / R4 / M5, M6, M12 | pump ×2, membrane ×3 | Oksana: power house, boring mill | Fits fuel and water (its own canals, plan §5). 700 m north of the pack's complex, Act IV's far band; three things are "the plant" |

**Three sites in one district.** Plaza – Novo – Bio Gen stand in a row on z −800…−449 with the hub south of all three (plan §4). A feature by design §3.5's rule on three conditions: the hub's "approaches" (enemies §3.3) are a rectangle that excludes Novo; the hub's wall (design §2.3) has its gate facing south or west; J7's "by air" (quests §6) becomes "by truck or by air" (E3). The problem is enemies §7: its hub ring is "4,000+ air" and the hub is at 2.4 km with the plaza. Difficulty must ride on the act-gated equipment rules (enemies §3), with Improved Mobs steps at 0–1,000 / 1,000–1,800 / 1,800+.

## 4. The economy

- **Emeralds in** (vendors §2, loot §3–6): loot weights 3–8 per roll, quest rewards 4–8, Militia drops, a trip's junk 10–20. **Out:** guns 15–80, ammunition 3–8, NVG 60, drones 30, rockets 12–20, cards 4, Recruits at the mod's price (camp spec §4 names no price). Coin is the limiter, as intended.
- **Caps flood.** A day is 20 real minutes and the restock is per in-game day (vendors §7): four stacks of ammunition per class, four med kits and six fuel cans every 20 minutes is a faucet. Restock per three in-game days.
- **Timers vs trips.** Trip-length 20 min (crafting §3) matches Act I; from Act II car round trips are 3–5 min, so the team waits at home for tower parts (14 and 10 min at yard tiers 2–3). Acceptable.
- **The card model starves.** One card slot per station (interface §4.3): if a reward hands the team one card, one station at a time runs each recipe, and crafting §4's "fourteen intermediate orders across the team's stations" cannot happen. Cards must be per-player or a 4-emerald copy (vendors §8).
- **Components.** Novo's engine is wanted seven times, FR-06's three items twenty; at one and three per 40 min held, neither starves over eight sessions. The hub is short: loot §6 counts thirteen items for three runs, but the five S-chain tier 3s each take a hub item (create §3) — eighteen, four runs.
- **Inputs with no source.** G1's cast iron is "Novo's loot table" (create §4) but loot §4 lists none; G1's casting sand needs clay in a WorldPainter world; G6's 24 IE steel ingots have no producer (create §1 adds no mining); gunpowder's source, the stone complex (design §4.2, loot §5), is not in v8.

## 5. The gun and the site chains

G1 needs W-B2 (`novo_defended`, one diesel engine, 32 concrete) and `novo_looted`; G2–G3 are yard work; G4 needs Walls 1 (Act I), 24 gunpowder and 4 shot. With Novo defended in session 3 or 4 the first shot lands mid-Act II as create §4 intends, if the engine is not spent on the truck (W9) first and §4's missing inputs exist.

The S-chains give five players a reason to be at a held site: hand-ins go to the keeper on site, and G6–G8 happen at Novo's foundry, FR-06's cannon builder, the plaza's fuze lab and the plant's boring mill (create §3–4). Missing: the hand-in rows (gaps §E, open) and the train's job — it runs "between the sector stations" (create §2) and the camp is not on the rail; name the stations and the cargo.

## 6. The interface

State a player cannot read from the world or the book:

1. **The fortify clock before Radio 2.** Design §6.2 shows the whole clock only from U5; interface §3.3's board readout (`NOVO — held — clock 31:20`) shows it from the start. Two rules, and the first two counterattacks are the ones to time.
2. **Component and hub refresh:** when the next engine appears (design §6.2, loot §1) is on no block or page.
3. **The marker's anchor point** (design §6.1; gaps C16 open): nothing in the world marks it.

Two channels at once (interface §0 rule 2): the assault won fires the title `NOVO IS OURS` (§3.5) and Tune's state-change line (§5); the 10-minute warning fires the bell, Tune's line and the sign (§5); the beacon fires `THE SLEEPER`, Tune's line and the sculk ring (finale §3). FTB Quests' completion toasts are a channel no document switches off.

## 7. Decisions

| # | Verdict |
|---|---|
| E1 | Confirm; apply it to quests §2–7.1, design §6.3, onboarding §2. |
| E2 | Confirm; re-rank its counterattack to first-fight size; use enemies §5's Matron. |
| E3 | Confirm the placement; J7 "by truck or by air"; move loot §6's two power-filter containers to the plant complex so the far band is used. |
| E4 | Confirm; extend design §2.7 to the v6 small sites named by W3, J1, J4, W-A5, M-P1 (the finale's first telegraph), U-C1, H3, D3, T7, loot §5. |
| E6 | Confirm; add the river crossing at the pump house to step 8. |
| E8 | Confirm at 173: crafting §5.8 adds H8, quests §7A stops at H7. |
| E10 | Confirm the pit; at x −1340…−1329 it is outside the §4 rectangle (east edge −1409). |
| E12 | Confirm; name the stations and the cargo (§5). |
| E15 | Challenge: per-player cards or a 4-emerald copy (§4). |
| E17 | Confirm; set y now from plan §9 (ground 88 plus the platform); design §6.1's "crater" loss rectangle is already the structure ±16 — rename it. |
| E5, E7, E9, E11, E13, E14, E16, E18 | Confirm as written. |

New decisions the final map forces:

- **N1 The camp rectangle.** Plan §4 is final at x −1792…−1409; plan §9 and design §2.2 put Marshall (x −1350), James (−1370), the gun pit (−1340) and Walker's east half beyond it. Re-cut the ring inside §4's box, or the locks, torches, lit outline and entry points straddle the edge.
- **N2 No crater.** The base's last line is the plaza (E17; design §6.1, G8); cut the ramp from onboarding §2; Marshall's drawbridge (create §2) spans a dry ditch at the gate; the zipline (camp spec §1) runs to the gatehouse; the finale's story (finale §3) is "under the plateau".
- **N3 Entry points.** Design §6.3 says "the east road and the north rim"; north is the tower pad and the lake (plan §9). Attackers come from the south-east, west and east: use the east gate road and the town edge.
- **N4 Which crossings exist at build:** the Line's ford (Act I), the viaduct (car, plan §5), the cut roads at z −520 and −205. Act III's road depends on the viaduct.
- **N5 The town's landmarks** (defaults): palace of culture = U-A1; tallest block = W-A6; central square = J-C1; four microdistricts = J9; swimming pool = the prismarine hall's role (M-P1); hotel = the glass tower's; bus depot = the stone complex's (W-A5, H3); the four farmsteads south of the Woods (z 224…576) = the mud village's (D3).
- **N6 The Woods' bearing.** x −2450…−1600, z −1350…100: its north edge is 950 m due south of the camp and none of it lies east of the camp. Quests §1 and loot §5 say "2.9 km NNE"; camp spec §3's road signs ("NOVO 1 km →", "WOODS ↑ 1.6 km") are v6.
- **N7 Three "plants".** Rename the plant sector (say "the waterworks").
- **N8 Bio Gen** is 1.9 km inside the district, not "3.9 km" (T7, loot §5) nor a far-ring stop (J4); T7's full revive arrives in Act II.

## 8. Top ten fixes

1. Re-sequence quests §7.1 (R2 = Skadowsky after L6 with no `novo_defended` gate, R3 = Novo, R4 = the plaza, R5 = the plant and FR-06), relabel T3–T6, J-S2, M4–M6, X3 and §8 to E1's acts, and rewrite onboarding §2 "Session 2" with J-S2/T3/R2/T5.
2. Re-cut the camp ring of plan §9 and design §2.2 inside the §4 rectangle (Marshall, James, Walker, the gun pit) and fix the spawn y from ground 88.
3. Remove the crater from design §2.2/§6.1, onboarding §2, create §2, camp spec §1, finale §3 and G8 per N2.
4. Rebase loot §5 and design §2.7 onto the town's landmarks (N5) and re-point W3, J1, J4, W-A5, M-P1, U-C1, H3, D3 and T7 at them.
5. Put the first car before the district walk: gate W6/W7 on `residential_defended` (or give the motor-assembly blueprint at L4, the depot) and add an electric motor to the depot's chest in loot §2.
6. Rewrite enemies §7's rings for a map where every site is 2.0–2.4 km out, and re-rank design §6.3's tables in E1's take order with Skadowsky's the lightest.
7. Make blueprint cards per-player rewards or a 4-emerald copy at the counter (crafting §4, interface §4.3, vendors §8).
8. Add the Line's river crossing and the east-bank road to plan §7–8's step-8 list, and rewrite quests §1's Act III as "beyond Skadowsky, by road; the lake is the boat's shortcut".
9. Give create §4's inputs a source: cast iron in loot §4's Novo table, clay or a Kessler-free casting-sand recipe, an IE steel route for G6, and a v8 building for gunpowder in place of the stone complex.
10. Set the vendors' restock to three in-game days (vendors §4, §7), count the S-chain tier-3 hub items in loot §6 (eighteen, four runs), and move the power-filter containers to the plant complex.
