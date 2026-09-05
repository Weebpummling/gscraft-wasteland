# GSCraft wasteland — vendors

*Design doc, 2026-09-04 (owner: "a vendor system for firearms, ammunition and gear in general, with
access unlocked by quest progress"). Companion to design §3 (the NPCs), §3.6 (building tiers),
crafting draft 1 (the station-only rule) and `gscraft-loot-tables.md`. Mechanism checked against
the jars: no trade mod is in the pack and KubeJS 2001.6.5 has no villager-trade events (no MoreJS),
so the vendors run on **vanilla merchant offers** written onto the NPC villagers by the loop script —
no mod added.*

## 1. What vendors are for, and what they must not break

The design's spine is *loot supplies parts, the station supplies products* (crafting §5). Vendors do
not replace that; they add the three things Tarkov's traders add to a loot game:

1. **A floor under consumables.** Ammunition, bandages, fuel and batteries can always be bought in
   small daily amounts, so a bad night never strands the team with empty guns.
2. **A shortcut with a price.** Working guns, armour and attachments are sold — at roughly **twice**
   what crafting them costs in loot value — so a team rich in coin and poor in time can buy, and a
   team that crafts is always ahead. Crafting stays the cheap route; the vendor is the impatient one.
3. **A sink for surplus loot.** Every vendor *buys* their category, which turns a full backpack of
   junk into coin and gives the forty-two small items a value beyond their recipes.

What vendors never sell for coin: complete parts, loot-only components, the tower's five hand-ins,
blueprints (those are quest stages), vehicles, the claim marker, dossiers. Nothing sold skips a trip; the
barters of §5 are the one exception, and each returns a component the team has already earned once.

## 2. The coin

**Emeralds.** They are already the Recruits' hire currency (camp spec §4) and a Valuables small item
in the loot tables (loot sheet §1); no villager in this world trades (Hostile Villages), so emeralds
have no other exit. Sources: the Valuables rows (offices, Financial Plaza, the hub, the mud village,
military chests), the valuables bag (J3), the outpost's cache (R-W1), and selling to vendors.
Sinks: buying (Teddy's rockets are the dearest ammunition), hiring recruits. A loot trip's sellable surplus is worth about 10–20 emeralds; a
rifle costs 40 (§4), so the shortcut is two or three trips of junk — a real choice, not a freebie.

## 3. Seven counters, four loyalty levels

Each camp NPC is a vendor of their own category, and their **loyalty level is their building tier**
(design §3.6): LL1 at tier 1 (after the introduction and the `*-B1` quest), LL2 at tier 2, LL3 at
tier 3. Tier 0 sells nothing but buys junk — the first coin comes from selling. Individual items
are also gated by the quest that teaches them (a vendor sells assault rifles only once W-A3 has
handed out their blueprint), so the counter never runs ahead of the book. The player sees exactly
what Tarkov shows: a trader whose stock grows as the relationship does, and a few items marked
"locked until…".

| Vendor | Category | Buys (sink) | LL1 sells | LL2 adds | LL3 adds |
|---|---|---|---|---|---|
| **Walker** — the yard | guns, ammunition, tools, armour | hardware, mechanical items, salvage weapons | pistol & shotgun ammunition (daily cap), casings, powder, basic tools, scrap vest/helmet; **pistol, pump shotgun** (after W-A1) | rifle ammunition; **assault rifle, SMG** (after W-A3); plated vest/helmet (after `plant_defended`); basic backpack (after Storage 1) | **sniper, MG** (after W-A4); composite armour (after `fr06_defended`); the Foreman's odd lots: 1 random tool a day |
| **Tony** — the clinic | medical | medical items, blood bags | bandages, painkillers, poultice (after T-W1) | med kits (daily cap 4), antiseptic, syringes (the infection cure is free from T1 and never a trade) | blood bags, ration packs, the surgical-kit barter (§5) |
| **Michael** — the plant | fuel, power, water | filters and chemicals, car batteries | empty fuel cans, coolant | fuel cans (full, daily cap 6), small battery packs, flashlight batteries | medium battery packs, the transformer-core barter (§5) |
| **Tune** — the shack | electronics, attachments, optics | electrical items, valuables | iron sights, extended magazines, wire spools | optics, suppressor (after W-A4), **night-vision goggles** (§6), flashlight batteries | thermal? **no** — thermal stays vehicle-only (§6); laser sights, the encrypted-radio *decrypt* barter |
| **James** — the lookout | maps, expedition kit | folders, hard drives | compass, map, torches, zipline rope (after J-B2) | site dossier *copies* (a bought dossier does **not** count for J-S quests — the original must be found) | the Cartographer's odd lots: 1 random Valuables item a day |
| **Teddy** — the Woods outpost (after R-W1) | explosives | gunpowder, powder | hand grenades, smoke grenades (after H1/H2) | RGO grenades, 40 mm grenades (after H4) | rockets, standard and TBG (after H5/H6) — loyalty = his quests, he has no building tiers |
| **Marshall** — the gatehouse | defences, recruits | gunpowder, powder, plates | sandbags, barbed wire (after D1); recruits (after D2, the mod's own hire) | claymores, drones (after D2) | drones, C4 (after D4); rifle and MG ammunition at double the daily cap from X6 onward (the finale's stockpile) |

**The site keepers (Create chapter §3, adopted 2026-09-05).** Each held strongpoint's keeper is a counter too; their
loyalty level is the **site's tier** (S-<site>-1…3), and they sell what the site makes:

| Keeper | Site | Buys | Tier 1 sells | Tier 2 adds | Tier 3 adds |
|---|---|---|---|---|---|
| **Vera** — the hospital | Skadowsky (the residential block) | blood bags, medical items | the gunner's manual pages, poultice | bandages, painkillers (a second clinic; the cure is free here too) | train tickets: nothing — the train is a hauler, not fast travel (owner default E12) |
| **Kessler** — the foundry | Novo | scrap, cast iron | casting sand, cast-iron nuggets | cast-iron ingots (4 a day), blaze cakes | bronze ingots |
| **Ilya** — the fuze lab | Financial Plaza | valuables, redstone | redstone dust, quartz | fuze heads | proximity fuzes (2 a day) |
| **Rook** — the steel works | FR-06 | steel scrap, plates | steel plates | big cartridges (empty) | autocannon barrels (1 a day) |
| **Oksana** — the power house | the plant | filters, chemicals | boiler water, packed gunpowder | nitrate (H8's input), drill bits | coolant, boiler parts |

## 4. Prices (first cut; Phase C tunes against the loot value table)

The rule: **a sold product costs twice its crafting inputs' sale value.** Loot value = what the same
vendor pays for the items. Buy prices are per stack of the item's normal stack size.

| Item class | Vendor buys at | Vendor sells at |
|---|---|---|
| Hardware (8) | 1 | — |
| Electrical (4) | 2 | 3 (wire spool, capacitor only) |
| Mechanical (4) | 2 | — |
| Filters and chemicals (4) | 2 | 3 (bleach, antifreeze) |
| Powder (4), gunpowder (4) | 2 (Teddy, Marshall) | — |
| Medical (4) | 2 | bandage 1, painkillers 2, med kit 4 |
| Valuables (1) | 4 (hard drive 8) | — |
| Salvage weapon | 6 | — |
| Ammunition (30 rounds) | — | pistol/shotgun 3, rifle 5, sniper/MG 8 |
| Guns | — | pistol 15, shotgun 20, SMG 30, assault rifle 40, sniper 60, MG 80 |
| Armour | — | scrap 10 / 6, plated 25 / 15, composite 60 / 35 (vest / helmet) |
| Attachments | — | sights 5, extended mag 8, optics 20, suppressor 25, laser 15 |
| Fuel, power | — | empty can 2, full can 5, small pack 15, medium pack 40, flashlight battery 2 |
| Kit | — | tools 4, compass 2, map 3, zipline rope 3, torches (8) 1, poultice 2, ration pack 3 |
| Night-vision goggles | — | 60 (LL2, Tune) |
| Defences | — | sandbag (4) 2, barbed wire (2) 2, claymore 6, HE shell (G7, Ilya) 3, drone 30, C4 12 |
| Explosives (Teddy) | — | hand grenade 3, smoke 2, RGO 5, 40 mm (2) 4, standard rocket 12, TBG rocket 20; nitropowder (2) 4, guncotton (2) 6 (H8) |
| The keepers' goods | casting sand 1, cast-iron nugget 1, redstone 1, quartz 1, steel scrap 2, boiler water 1, nitrate 2 (the keepers buy) | cast-iron ingot 3, bronze ingot 4, blaze cake 6, fuze head 3, proximity fuze 8, steel plate 3, big cartridge 4, autocannon barrel 20, packed gunpowder 2, drill bit 6, coolant 3, manual page 2 |

Daily caps (Tarkov's limited stock) keep the vendor a floor and not a faucet: ammunition 4 stacks a
day per class, med kits 4, fuel cans 6, one gun of each unlocked class, one armour piece each; at Teddy's, grenades
2 a day (4 after H3), 40 mm rounds 4 stacks, rockets 4.

## 5. Barters (the Tarkov trade that is not money)

A few offers take items instead of coin — the vanilla trade UI supports two input items:

| Vendor | Give | Get | Why |
|---|---|---|---|
| Walker | 4 salvage rifles | 1 assault rifle | the salvage rule in reverse; four broken guns are one working one |
| Michael | 1 medium battery pack + 2 circuit assemblies + 4 relays | 1 transformer core | a slow second source of FR-06's component between its respawns |
| Tune | 1 encrypted radio + 1 hard drive | 1 military circuit board | a second route to the transmitter's component between the plaza's respawns |
| Tony | 2 blood bags + 1 med kit | 1 surgical kit | the far-ring item from near-ring loot, once T7 is done |
| James | 2 folders of documents | 1 site dossier copy | the copy marks the site on the board but completes no quest |

## 6. Night vision, thermal, the flashlight

Checked in the jars: **no player night-vision or thermal item exists in the pack.** The only such
features are vvp's vehicle-view keybinds (`key.vvp.toggle_nvg`, `key.vvp.thermal_vision`;
`ThermalVisionHandler`, `ThermalEntityGlowHandler`) — inside vvp vehicles only, which vehicles is a
Phase E check. TaCZ's default pack has laser sights and "white light" (illuminated-reticle) sights, no
weapon light, no thermal scope.

- **Flashlight:** a real dynamic-light flashlight needs a mod (`notes/gscraft-flashlight-and-nvg.md`
  has the candidates; *Dynamic Flashlight 2.1.0* was added 2026-09-04 (camp spec §5), no
  dependencies). Until it is added the KubeJS Night-Vision flashlight of the camp spec stands.
- **Night-vision goggles:** a KubeJS Curios/helmet item (`gscraft:nvg`) giving Night Vision while
  worn, draining a battery bar; sold by Tune at LL2 for 60, never crafted, never looted — the one
  item that is vendor-only, so Tune's counter has a reason to exist.
- **Thermal:** **not for players** — the dark is a design tool (Eyes in the Darkness, the fog man,
  the Warden's Darkness). Thermal stays in the vehicles that have it.

## 7. Mechanism (Phase C/D)

- **Offers:** the loop script keeps a stock table per vendor (`build/kubejs/data/gscraft/vendors/<npc>.json`:
  item, price or barter, LL, unlock stage, daily cap) and writes the villager's `Offers` NBT from it
  with `/data merge entity @e[tag=gscraft_npc_<npc>,limit=1] {Offers:{Recipes:[…]}}` — `buy`, `buyB`,
  `sell`, `maxUses` = the daily cap, `priceMultiplier:0`, `demand:0`, `rewardExp:0b`. A sink offer is
  the same record reversed (`buy` = 8 metal scrap, `sell` = 1 emerald).
- **Opening the counter:** right-click on an NPC keeps opening the quest book (design §3); **sneak +
  right-click** lets the vanilla villager interaction through, which opens the trade screen. A NoAI
  villager trades normally; it never restocks on its own, so —
- **Restock:** once per in-game day (online time) the script rewrites every vendor's Offers, which
  resets `uses` to 0. Tune's Radio 1 line at dawn: *"Counters are open."*
- **Unlocks:** the rebuild runs on every change of `camp_<npc>_<tier>`, `bp_*`, `storage_*`,
  `<site>_defended` and the W-A / D stages, so a new item appears the moment its quest completes.
- **The book shows the stock:** EMI does not list villager trades, so each NPC's chapter gets a
  "Counter" quest per loyalty level whose description is that level's stock list (checkmark,
  no reward) — the same page the player already reads.
- **Counters as blocks:** Doomsday Decoration's vending-machine and shop-counter props† dress each
  NPC's tier-1 template so the counter is visible; the trade itself is with the NPC.
- **Fixed prices:** `priceMultiplier` and `demand` at 0 disable vanilla's reputation and demand
  pricing; gossip is irrelevant to a NoAI villager.

## 8. What this changes elsewhere

- Design §3 gains the pointer to this doc; emeralds are already a small item (loot sheet).
- Quests: three "Counter" checkmark quests per camp NPC chapter (one per LL) — 18 quests; Teddy's counter levels are his own quests, listed in the
  quests doc when Phase C writes the book; not counted in the 138 until then.
- Crafting §5: unchanged — the station stays the cheap route; the vendor price rule (§4) is the check.
- Camp spec §6: a counter prop per tier-1 template (written); Teddy's counter prop is placed by `npc_teddy` beside him in the outpost's tower.
- The five keepers' counters (§3) need five more `build/kubejs/data/gscraft/vendors/<keeper>.json` files and a loyalty rule keyed to `site_<site>_<tier>` instead of `camp_<npc>_<tier>` (Phase C).
- Lost blueprint cards: every camp NPC's counter carries a "re-issue" offer per card they gave out, 4 emeralds, gated on the team's `bp_<recipe>` stage (crafting §4).
