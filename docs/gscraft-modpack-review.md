# GSCraft wasteland — mod pack review against the design

*Review 1, 2026-09-04 (owner: "review our mod packs and update to the degree the design requires").
Inputs: `build/manifest.json` (108 entries, the pinned set), the local server (`G:\GSCraft\server\mods`,
95 jars), the Prism client instance (95 jars, identical to the server), `build/additions.json`, and
every design document. Rule carried from 2026-09-03: **nothing is cut** — mods without a design role stay
for the worlds and the builds that use their blocks. So this review adds and aligns; it removes nothing.*


> **Version column superseded (2026-09-05).** Seventeen jars and Forge 47.4.23 were applied and boot-tested on the
> local server — `gscraft-modpack-update-applied-2026-09-05.md` (its §4 is the conflict review); Lost Cities is 7.5.4;
> Superb Warfare is held at 0.8.8 by its two vehicle add-ons. **Create 6.0.8, Create Big Cannons 5.11.4 and
> Ritchie's Projectile Library 2.1.1 are installed** (the Create chapter, adopted the same day) — §3's "not installed"
> for `ritchiesprojectilelib` no longer holds.

## 1. Verdict in one table

| Finding | Action |
|---|---|
| The design needs a **flashlight** in the starting kit and the pack had none (`notes/gscraft-flashlight-and-nvg.md`) | **Dynamic Flashlight 2.1.0 added 2026-09-04** (Forge 1.20.1, 93 KB, no dependencies) to server, client, manifest and the client zip — §4 |
| **EMI 1.1.24** is in the manifest, on the hosted server and in the rebuilt client zip (`release-v7/GSCraft-Client.zip`, 2026-09-03) but was **missing from the local test server and the local Prism instance** | synced 2026-09-04 from the release-v7 copy — §4 |
| Twelve **conditional libraries** are listed in the manifest and present nowhere | correct as is: they are the libraries other candidate mods would have pulled in; keep the entries as a reference list, do not install — §3 |
| Every other capability the design names is already installed (§2) | nothing to add |
| Lost Cities **7.5.4** was published on 2026-09-03 (railway level offset; no fix for the palette null) | **do not update** during the v7 build; the world is generated with 7.5.3 and the `gscraft_lcfix` datapack carries the fix — revisit for a v8 world |
| No mod in the set contradicts the design | nothing to remove |
| **Pomkot's Mechs 0.0.1-alpha.8 + Leawind's Third Person 2.1.0** added 2026-09-04 (owner) after the isolated server test — hub and FR-06 only (`notes/gscraft-pomkots-mechs.md`) | in `server/mods`, the Prism instance, the manifest and the packwiz pack; the hosted `/mods` by hand |

## 2. What the design asks for, and what supplies it

Every system in the design was traced to the jar that delivers it. "Verified" means the class or
config was read in the jar on this machine.

| Design system | Mod(s) | State |
|---|---|---|
| Quest book, chapters, stage tasks, choice rewards | FTB Quests 2001.4.22, FTB Library, FTB Teams (team stages), Item Filters | installed |
| Claim, one team | FTB Chunks 2001.3.8, FTB Teams | installed |
| Scripting: items, blocks, stages, the loop, NPC interaction, vendors' offers, boss bars | KubeJS 2001.6.5 + Rhino | installed; `BlockEntityBuilder` verified; **no villager-trade events** (vendors use vanilla `Offers` NBT — vendors doc §7); **no custom menu screens** — the station's UI is a Phase C check (§5) |
| Stations' recipes stripped from every bench | KubeJS (`gscraft_recipes.js`) | done |
| Storage on a Curios slot | Sophisticated Backpacks 3.24.13 + Sophisticated Core, **Curios 5.14.1** | installed |
| Guns, attachments, salvage | TaCZ 1.1.8 + default gun pack, Keerdm ZAE (TaCZ) 1.41, TaCZ fire control extension, Cyber Armorer and CIBR packs in `tacz/` | installed |
| Vehicles | Immersive Vehicles 24.0.0 + MTS Official Pack V29 + OAmP V3; Superb Warfare 0.8.8 + vvp 0.2.0 + MCSP 1.0.8 | installed |
| Defences (Walls 1–3), batteries, charging station | Superb Warfare | installed |
| Power, machines, floodlights, scaffolding | Immersive Engineering 10.2.0 | installed |
| Elites, Captains, salvaging table, gems | Apotheosis 7.4.8 + Placebo + Apothic Attributes | installed; `Boss Spawn Cooldown` at max |
| Garrisons, ambient rules, the Woods rule | In Control! 9.3.3 | installed |
| Infection (20 min, four phases); horde event off | The Hordes 1.5.4c | installed; `enableHordeEvent = false`, `infectPlayers = true` |
| Bleed-out and revive | PlayerRevive 2.0.31 + CreativeCore | installed; `bleedTime` 6000, `maxDistance` 6 |
| Distance difficulty | Improved Mobs 1.13.7 + TenshiLib | installed; DISTANCESPAWN |
| Noise draws mobs | Zombie Awareness 1.13.1 + CoroUtil | installed |
| Factions fight each other | Mob Factions 1.0.0 | installed |
| Horror set | Eyes in the Darkness, The Knocker, The Man From The Fog | installed |
| Armed pillagers ("bandits") | Pillagers Gun 3.1.0, Bandits (`enableMod` false, kept for gear) | installed |
| Guards, recruits | Guard Villagers 1.6.15, Recruits 1.14.0 | installed |
| Camp suppression | Magnum Torch 8.0.2 + Puzzles Lib | installed; ten torches placed |
| Instanced loot, refresh | Lootr 0.7.35 | installed; `refresh_modids` gscraft, 120000 |
| Starting kit | Custom Starting Gear 2.0.3 | installed |
| Notebook | Patchouli 84.1 | installed |
| Farm and kitchen, rations | Farmer's Delight 1.2.9 | installed |
| Ziplines, movement | ParCool 3.4.2 | installed |
| Party xp share | sedparties 2.0 | installed; `useFTBTeams` |
| Camp props, wrecks, signs, streetlamps, floodlights | Doomsday Decoration 1.1.3; Refurbished Furniture 1.0.20 (+ Framework); Chipped, Chisel, Factory Blocks, Antiblocks (the transplanted builds' palettes) | installed |
| Weathering / aging | Immersive Weathering 2.0.5 + Moonlight | installed |
| World: Lost Cities, capitals, bunkers, hostile villages | Lost Cities 7.5.3, Lukis Grand Capitals 1.1.2, Underground Bunkers 1.0.5, Hostile Villages 5.7 | installed; **never remove** — the v7 world is generated with them |
| Maps, pings, voice, recipe viewer | Xaero minimap + world map, Ping Wheel 1.12.0, Simple Voice Chat 2.6.22, EMI 1.1.24 (synced locally 2026-09-04) | installed |
| Performance and server tooling | ModernFix, Canary, FerriteCore, Let Me Despawn, Get It Together Drops, chunksending, LongNbtKiller, Fast Furnace/Suite/Workbench, Recipe Essentials, AI Improvements, Dynamic View, Chunky, spark, BHStats, WorldEdit | installed |
| Melee, HUD | Better Combat (+ player animation lib), AppleSkin, Almanac | installed; no design role, kept |
| Libraries | GeckoLib, AzureLib, Architectury, Cloth Config, Resourceful Lib, Athena, Atlas Lib, Cupboard, Cryonic Config | installed as required |
| **Flashlight** (starting kit, onboarding §8, camp spec §5) | Dynamic Flashlight 2.1.0 (`flashlight`) | installed 2026-09-04 — §4 |
| Night vision (Tune's vendor item), thermal | none needed: a KubeJS goggles item; thermal stays vehicle-only (vvp) | design decision, no mod |

## 3. The manifest's twelve conditional libraries

`kotlinforforge`, `fzzy_config`, `uilib`, `collective`, `supermartijn642corelib`, `supermartijn642configlib`,
`balm`, `citadel`, `TerraBlender`, `caelus`, `txnilib`, `ritchiesprojectilelib` are in the manifest as
`conditional-library` and in neither local set nor (per the 2026-09-03 audit) on the hosted server. Nothing
installed requires them (`requires` lists checked). They are the dependency closure of mods that were
considered and not taken; the entries stay as documentation and are **not installed**.

## 4. The two updates the design requires

| Jar | Source | Size | Hashes | Goes to |
|---|---|---|---|---|
| `flashlight-2.1.0-forge-1.20.1.jar` (Dynamic Flashlight 2.1.0, 2026-08-02) | `https://cdn.modrinth.com/data/SemszBhn/versions/dkQtiEhc/flashlight-2.1.0-forge-1.20.1.jar` | 93,543 B | sha1 `bcb2b2085c55015279ac96113ee8b12e65ebffaf`; sha512 `45e97d9f…611530` | **done 2026-09-04** (owner-approved): hash-verified, in `server/mods`, the Prism instance, `build/manifest.json` (sha256 from the file), `build/additions.json`, appended to `release-v7/GSCraft-Client.zip`; still to do by hand: the hosted `/mods` (HANDOFF §6) and the Drive re-issue |
| `parties_xaerominimap_fix-1.0.0.jar` (Parties Xaero Minimap Fix 1.0.0, CurseForge 1589418, unusualgravy, 2026-06-27) | `https://www.curseforge.com/api/v1/mods/1589418/files/8327208/download` | 4,703 B | sha256 `5f2b55cb4b28cae8625e96f5adecf2f010c1f08cd9d70d5760658a1f6c1ea1d3` | **client only, done 2026-09-04** (owner-approved): Parties 2.0-beta-p.7.1 crashes every client at mod setup with Xaero's Minimap >= 25.3.2 (`xaero/common/gui/IScreenBase` moved); one mixin over Parties' `XMCompatManager`. Prism instance `mods`, `release-v7/GSCraft-Client.zip`, packwiz pack. Not in `server/mods`. |
| `emi-1.1.24+1.20.1+forge.jar` (EMI 1.1.24, already pinned) | local copy `G:/GSCraft/release-v7/` (sha256 checked against the manifest) | 1,121,750 B | `server/mods`, the Prism instance `mods` — **done 2026-09-04**; the hosted server and the client zip already had it |

Distribution moved to the packwiz pack and the `client-installer-2026-09-04` release on 2026-09-04 (`notes/gscraft-one-click-install.md`); the old `GSCraft-Client.zip` is superseded. Re-issue nothing on Drive,
and add one line to `client/GSCraft Install Guide.md` ("Flashlight: right-click to switch on, sneak +
right-click with a battery to reload"). The manifest's `sha256` for the flashlight jar is computed
from the downloaded file, never copied from a listing.

**Flashlight configuration (Phase C):** server-side light blocks on, range 8–12, slow refresh; the
mod's battery recipe replaced by ours (crafting §5.6: 1 car battery recharges); the Custom Starting
Gear kit gets one flashlight and one battery; measure the light-update cost with five players on the
local server before the hosted deploy.

## 5. Risks found on the way (no mod change, Phase C checks)

- **The station's screen.** KubeJS 1.20.1 builds blocks and block entities with inventories but has
  no custom menu/screen builder. Phase C must confirm how players put items into the station; the
  fallback needs no mod: the station is a container block (a barrel-class block with the station's
  look), the script reads its inventory on a timer, matches the order and writes the result back, and
  the order's countdown is shown as the block's name/tooltip and a chat line. Crafting §4 stands either way.
- **Villager trade screen for vendors** is vanilla and works on a NoAI villager; the sneak-right-click
  split from the quest-book click is a KubeJS interact handler (vendors doc §7) — test both clicks.
- **Two extra gun packs** (Cyber Armorer, CIBR) sit in `tacz/` beside the default pack. Their guns are
  not in any recipe or loot table; they only exist for creative/testing. Leave them, or drop them from
  the client zip to save download size — an owner call, no design impact.
- **Lost Cities 7.5.4** exists (2026-09-03). Not for this world; note for v8.

## 6. What this changes in the documents

- `build/additions.json`: a Dynamic Flashlight entry (this commit); `build/manifest.json` after the jar lands.
- Camp spec §5 and the flashlight note already point at this decision; the onboarding kit line is unchanged.
- HANDOFF: this review in the design list; the two jars in the "next" list.
