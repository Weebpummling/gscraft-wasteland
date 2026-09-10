# GSCraft — What folds into the mod (review, 2026-09-10)

The design was written under "no custom mod" (map design §8; the draft-3 verdict of 2026-09-03). Since 2026-09-09 the
enemy system is our own Forge mod, GSCraft War: on the server and on every client, data-driven (factions, ranks, zones
as JSON), with SavedData, its own `/gscraft` commands and a regression suite on a ticking local server. This review
reads the design docs for every function assigned to KubeJS, datapack functions, In Control, Hordes waves or Apotheosis
bosses, and sorts each one: **fold** into the mod, **keep** where it is, or **retire**.

Sources: map design §3, §4.4–4.5, §6, §8–9; quests §9; player interface §3–7; vendors §7; camp spec §1–4; crafting §4;
finale §5; onboarding §8; loot tables §3, §8; mod capabilities §5; mod utilization plan; design gaps; enemy review §5–11;
war mod design; `docs/notes/gscraft-kubejs-traps.md`; the server's `kubejs/`, `config/incontrol/` and the world datapack.

## 1. Why the line moves

- **The planned "loop script" is the game.** The site ladder, the assault and fortify clocks, the waves, the site
  guards, the component refills, the vendors, the station, the bulky rule, the readouts, radio lines, titles and boss
  bars, the first-join sequence, the finale and the operator command are all assigned to KubeJS (quests §9, interface §7,
  design §6, finale §5, vendors §7, crafting §4, onboarding §8). None of it is built.
- **KubeJS has cost this server more than any other layer.** The traps note records a startup-script error that blocks
  a dedicated server's boot (§1.1), an uncaught throw in a Forge handler that crashes it (§1.2), `const` broken inside
  blocks (§2.1), `event.cancel()` swallowed inside `try` (§2.2), `checkSpawn` inverted and blind to scripted spawns
  (§2.3), `Math.PI` undefined (§2.4) and one shared scope per script type (§2.5). The 2026-09-08 review found five of
  six scripts had never run; the projectile sweep is still parked; the tower lock's native half has three unguarded
  Forge handlers and a `prop()` that always returns `null` (traps §5).
- **The loop leans on what the mod already owns.** Waves are placements of faction bodies; a site guard is a garrison;
  a site's occupiers are a zone pool; the finale's Captains are mod elites (enemy review §9); "every clock counts online
  ticks" is SavedData the director already keeps.
- **It can be tested.** The mod builds with Gradle and is proven by `tools/war_phase*.py` on a ticking server; a script
  can only be proven on an isolated server by hand.

What the mod should **not** take: data that designers edit and that works (the recipe strip, loot tables, structure
templates, the quest chapters), and other mods' features that work (Hordes infection, PlayerRevive, Lootr, Recruits and
Guard Villagers as bodies, Magnum Torch, Zombie Awareness, Create's display links, Apotheosis' Salvaging Table).

## 2. How the mod talks to the quest book

Read from the jars: FTB XMod Compat is not installed, so FTB Library's `StageHelper` uses its fallback,
`EntityTagStageProvider` — **a stage is a vanilla entity tag on the player**. `StageTask` checks the team's members
(`TeamData`) and can auto-submit on the player tick; `StageReward` adds or removes the tag. The mod can therefore set
every stage of quests §9 itself (`player.addTag`), with no KubeJS in between. Quest rewards that run commands keep
working: `function gscraft:tower_stage_N` as now, and `/gscraft site <id> <state>` for the ladder.

One rule follows: tags live on players, so a team stage set while a member is offline would be missed. The mod keeps
the team's state in SavedData as the record and re-applies the tags to every member on join; the tags are a projection,
never the source. `[needs in-game check]` that KubeJS's own stage store on this pack is the same tags, so the existing
`kubejs stage add` reward lines agree with the mod's.

## 3. The sort

### 3.1 Fold into the mod

| # | Function | Planned in | Planned as | Why the mod |
|---|---|---|---|---|
| F1 | **Site ladder and clocks**: scouted → looted → held → defended → lost; assault 5 min; fortify 40 min of online time; the 10-minute warning; one contested site; the loss check (5 attackers in the camp square for 30 s) | design §6, quests §9, interface §5 | KubeJS loop + stages | persistent state and online-time clocks are SavedData; every transition drives waves the director places |
| F2 | **Assault and counterattack waves**: the four roles, team scaling ×0.4–1.2, 45-second cadence, entry 48 blocks outside the perimeter on the attacking site's approach | design §6.2–6.3, enemies §4, enemy review §6 | KubeJS summons, or Hordes `SpawnHordeWave` (mod utilization C19, gaps F10) | the review already rules director-run waves; the bodies, ranks and placement checks are the mod's |
| F3 | **Site guard and keeper**: 4 Recruits + 2 Guard Villagers at the anchor, `Owner` = the marker's placer, re-summoned when below target, doubled on `defended`; the keeper villager | design §6.1, camp spec §4 | datapack function + KubeJS count check | it is a garrison: persistent members, a target size, a refill timer, a tag — already built; it needs foreign entity ids and NBT |
| F4 | **No hostile spawns inside a held site** | design §6.1 | KubeJS `EntityEvents.checkSpawn` | `checkSpawn` is inverted and misses scripted spawns (traps §2.3); in the mod it is the zone's state switching its pools off |
| F5 | **Occupiers** (a site's garrison before the take) | design §6.3 table, "In Control! rule inside the rect" | In Control | already folded — zone pools; the design table's column still names In Control |
| F6 | **Site elites and the finale's Captains** | design §6.3, finale §5, mod capabilities | Apotheosis boss JSON + `/apoth spawn_boss` | W9 ruled elites native; a rank with health and speed multipliers, a name and a boss bar |
| F7 | **The finale**: countdown from `beacon_lit`, five waves, the Sleeper (Warden) with health 500 + 250 per player to 2000, a boss bar on its health, the fail check (5 attackers in the mast field for 30 s), the retry | finale §5 | `gscraft_finale.js` | the same clock, wave and loss machinery as F1–F2 |
| F8 | **Component containers**: armed on `held`, refilled every 2 in-game days while held and every 5 at never-held sites, shared (not Lootr) | design §6.2, loot tables §3 | loop script | a SavedData timer that re-sets the container's loot table and its lid state |
| F9 | **The Custodian**: the PMB01 appears when a player first enters the confinement hall's core; `custodian_dead` on death | quests J-H1 | loop script | the Matron's lair with an "on first entry" trigger |
| F10 | **Player checks**: by car / boat / air location flags; the `revives_3` counter | quests §9.1, T8 | KubeJS player check | player tick reads the vehicle type; PlayerRevive's `PlayerRevivedEvent` (in its jar) counts revives |
| F11 | **Camp revive**: a downed player inside the camp outline is revived after 10 s; the hospital as a second point | design §4.5, quests T2, gaps E14 | script | PlayerRevive's `IBleeding` capability, compile-only, and a zone rectangle |
| F12 | **Titles, boss bars, radio lines** (`gscraft:say`, the per-player 20-second queue), the gate bell, first-time lines, the first-join sequence and the late joiner's re-send | interface §3.5–3.6, §7; onboarding §8 | KubeJS `title`, `tellraw`, boss bar commands | they fire at F1's moments; the lang file interface §6 names (`assets/gscraft/lang/en_us.json`) is the mod's own path |
| F13 | **James's waypoint push** (`xaero-waypoint:` chat line) and its colour re-send | interface §4 | loop script | a chat line sent on a state change |
| F14 | **Board, clock sign and look-at readout** | camp spec §2, interface §3.3 | loop script writing signs; a server tick raycasting every 10 ticks per player | the text comes from F1's state; the readout could be a client overlay fed by synced state instead of a server raycast. Create's display link (create-and-artillery, Tune) can still render the board |
| F15 | **The operator command**: `state`, `site`, `tower`, `say`, `tour`, `clock` | interface §5 | KubeJS command | it shares the mod's `/gscraft` root (Brigadier merges them, so it would register), but every subcommand reads F1's state |
| F16 | **Locked rectangles**: the tower compound, the NPC buildings, mech griefing | tower lock scripts, design §3.6, quests §9, mech griefing script | two KubeJS files + one startup script | a `lock` flag on a zone and seven Forge handlers in Java; retires every startup script |
| F17 | **Projectile sweep**: gun-mod projectiles retired at the simulation edge or after 30 s | `gscraft_projectiles.js` | KubeJS tick, parked, never ran | projectiles registered on join and checked on the server tick; closes an open problem |
| F18 | **Survivors and keepers**: invulnerable, no AI, right-click opens the quest book, sneak + right-click trades | camp spec §1, design §3, vendors §7 | villagers summoned by functions + KubeJS interaction + `Offers` NBT rewritten by script | a mod NPC on the soldier body with no AI: the interaction lives in the entity; offers come from `data/gscraft/gscraft_vendors/<npc>.json` |
| F19 | **Vendor stock**: unlock stages, daily caps, restock every three in-game days of online time | vendors §7 | script rewriting NBT | with F18, a SavedData day counter; no villager NBT, gossip or profession to fight |

### 3.2 Fold after the loop (recommended, larger)

| # | Function | Planned in | Planned as | Note |
|---|---|---|---|---|
| C1 | **The work station**: `inventory(3,4)`, an order in NBT, a ticker matching the card, a lit state, tier variants, the owner binding | crafting §4, interface §4.3, §7 | KubeJS `BlockEntityBuilder` | a block entity with a menu; the menu needs client code, which the mod already ships; the KubeJS block-entity builder is untested on this server |
| C2 | **The bulky rule**: Slowness, no sprint, not in a backpack | design §4.4 | KubeJS item + player tick + insert check | an item tag and a player tick; the backpack exclusion through Sophisticated Backpacks' own config if it has one |
| C3 | **Items**: small items, intermediates, complete parts, components, dossiers, the claim marker, canned goods, scrap / plated / composite armour, blueprint cards, NVG | crafting, loot tables, design | KubeJS items (a startup script: an error blocks boot, traps §1.1) | the items with behaviour (claim marker, dossier, card, bulky parts, armour) belong with F1 and C1–C2; plain materials could stay, but one registry keeps lang, textures and tags in one place |
| C4 | **Tooltips**, one line per small item | interface §3.2 | KubeJS `tooltip` | a lang key per item, with C3 |

### 3.3 Keep where it is

| # | What | Why |
|---|---|---|
| K1 | `gscraft_recipes.js` (the bench and roster strip) and `gscraft_fixes.js` | recipe removal is a server script that reloads with `/reload` and touches no Forge event; traps §5 finds it correct |
| K2 | Loot tables and the chest furnishing functions (`furnish_*`, `dossiers`) | data |
| K3 | Template functions: `tower_stage_N`, `camp_<npc>_<tier>`, `site_<site>_<tier>`, `theline`, `place_kept_structures` | designers edit them; quest rewards and the mod call them |
| K4 | FTB Quests chapters, stage barriers and rewards | only their stage source changes (§2) |
| K5 | Hordes infection; PlayerRevive; Lootr instancing and refresh; Recruits and Guard Villagers as bodies; Magnum Torch (the director already asks it); Zombie Awareness for the Dead; Create display links; Apotheosis' Salvaging Table; sedparties; Xaero; Farmer's Delight | they work, and the mod uses them rather than copying them |

### 3.4 Retire

| # | What | Why |
|---|---|---|
| R1 | **In Control** | `spawn.json` has 15 rules; the only live ones are the two allows (`mod: gscraft`, tag `gs_placed`) and the hold. Rules 3–14 sit behind the hold and never fire for a hostile. `spawner.json` still runs four apocalypse spawners (zombies 0.55 a second, skeletons 0.14, spiders 0.1, pillagers 0.025), and the hold then denies every mob they make — work for nothing, every second. `loot.json` adds 65 drop rules to the Dead (string, spider eyes, ender pearls 4 %, gunpowder, bones, Superb Warfare ammo boxes 2 %, food), which enemy review §7 wants as `gscraft:entities/<rank>` corpse tables. **Fold** the hold into the director's vanilla suppression (war mod design §5 already plans it) and the drops into the mod's loot tables, then remove the mod. Measured today: the director's Dead are not touched by the `finalize` rule (a placed husk has 20 health, not 25) |
| R2 | Hordes wave tables and `/hordes SpawnHordeWave` as the wave engine (mod utilization C19, gaps F10) | superseded by W14 and enemy review §6; Hordes stays for infection |
| R3 | `spawns_on.mcfunction`, `spawns_off.mcfunction` | they toggle the In Control deny rule; `/gscraft director pause|resume` replaces them |
| R4 | `gscraft:elite_<site>` Apotheosis boss definitions | F6 |
| R5 | The stale KubeJS copies in `build/packwiz/kubejs` and the client instance (traps §5) | once F16 and F17 fold, the pack ships no startup scripts |
| R6 | "No custom mod" (map design §8, the draft-3 verdict) | superseded 2026-09-09 |

## 4. Order

1. **Now, small and independent (one session):** F16 locks and mech griefing, F17 projectile sweep, R1 In Control
   (suppression and corpse loot in the mod, then the removal test: spawners, structures, Magnum Torches), R3. This
   retires every KubeJS startup script and one mod.
2. **Enemy review phase 6 (director waves):** F2, the skeleton of F1 (site states in SavedData, `/gscraft site`), F3,
   F4, and the assault's boss bar and titles from F12. Testable at one site with no quests: commands drive the states.
3. **The stage bridge (§2):** state to tags on every team member, re-applied on join; quest rewards call
   `/gscraft site …`. Test with one chapter.
4. F18–F19 survivors and vendors; F8 components; F10–F11 player rules; F13–F14 board and waypoints; F15.
5. C1–C4 station, bulky rule, items (map design Phase C) — the largest data and art load.
6. F7 finale, F9 Custodian (Phase E).

## 5. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| D1 | The loop (F1–F15) in the mod instead of a KubeJS loop script | **yes** |
| D2 | In Control removed once its hold and drops live in the mod and the removal test passes | **yes** |
| D3 | Survivors, keepers and vendors as a mod NPC with trade data, instead of villagers with rewritten NBT | **yes** |
| D4 | Station, bulky rule and items in the mod (C1–C4) | **yes, after the loop**; plain material items may stay in KubeJS if the art pass prefers |
| D5 | Elites and Captains native (W9), so Apotheosis keeps only the Salvaging Table | **confirm** |

## 6. Documents to update once ruled

Map design §6.1 (the `checkSpawn` line), §6.3 (the In Control column), §8 (tech stack), §9 Phase C–E; quests §9 (its
title and the stage mechanism); player interface §5 and §7; vendors §7; camp spec §1 and §4; crafting §4
(implementation); finale §5; mod utilization plan C19; design gaps F10; loot tables §8 (the `LootEvents` line);
HANDOFF §5.
