# GSCraft wasteland — the finale

*Design doc, 2026-09-04. Answers gap audit B30 ("a research-backed finale design, not the dragon by default").
Sits under design §7.1 and quests X6–X9. Everything here was checked against the jars in the local server
(`G:\GSCraft\server\mods`) and the mods' documentation; each number that Phase E still has to test is marked
**(E)**.*

## 1. What the finale has to do

The beacon lights at stage 5 (X6) and a 60-minute countdown starts. Then five waves come to the players'
claim: waves 1–4 are the four defence tables of design §6.3 stacked, and wave 5 carries the boss. The boss fight
has to work with what the players actually have by then: guns (TaCZ), the gatehouse at tier 3 (blast doors,
floodlights), the M3A3 Bradley built during the countdown (crafting §2.1), Tony's med kits, and a team of
two to six. So the boss must

1. be **hittable by guns** and take that damage honestly,
2. **come to the gate** — the walls, the doors and the vehicle have to matter,
3. **not erase the base** while it fights,
4. **scale** to the number of players online, by one command,
5. be summonable, named and removable by the KubeJS finale script with no End mechanics involved.

## 2. The candidates, checked

| Candidate | Source | What was found | Verdict |
|---|---|---|---|
| **Ender Dragon** | vanilla | Outside the End it flies to (0, 0) — the crater — and dives at the ground, "does not perch" and "continues to fly around forever" (Minecraft Wiki, Ender Dragon). Damage to every part but the head is cut by ~75 %, and a Java bug gives the head the same reduction, so **every gun does a quarter of its damage**. Block breaking follows `mobGriefing` (Forge routes it through a per-entity event, so a startup-script handler like the tower lock's could deny it for the dragon alone — **(E)**). No portal, no egg outside the End. Whether TaCZ's own bullet raycast registers hits on the dragon's multipart hitboxes at all is **unknown (E)** — some gun mods shoot straight through it. | **No.** Fails 1 and 2: guns feel broken against it, and nothing about the base matters to a boss that never lands. Keep only as the story of the crater (it is the impact site; nothing needs to come back to it). |
| **Wither** | vanilla | 300 HP; below half health it gains "wither armor" and is immune to arrows and other projectiles. TaCZ damage types are tagged `is_projectile` (that is what the pack's armour balance relies on), so **the guns stop working at 150 HP**. A CurseForge mod exists only to rebalance this pairing. Skulls explode with `mobGriefing` on. | **No.** Fails 1 outright and 3. |
| **Warden** | vanilla | 500 HP, one hitbox, ground-bound, 2.9 tall. Melee 30 (kills an unarmoured player in one hit — Tony's chapter matters), **sonic boom 10 that ignores armour and enchantments** with a 15–20 block reach — the answer to players shooting from the wall. Applies Darkness. Hunts by vibration and smell, so **gunfire draws it**: the shooters are the targets. Digs down and despawns after 60 s without a disturbance unless it has a custom name / persistence — a named summon stays **(E: confirm a named warden does not dig)**. | **Yes** — the boss of wave 5. Fits 1–5. |
| **Apotheosis boss** | Apotheosis 7.4.8 | Boss definitions are JSON (`data/<ns>/bosses/*.json`: entity, gear sets, rarity range, per-rarity attribute modifiers, effects, enchant levels); the pack ships 24 for zombie/husk/skeleton/witch/… Summoned by `/apoth spawn_boss <boss> [rarity]` (`BossCommand`), by the **Boss Spawner** block or the **Boss Summoner** item. Random surface bosses are already off (`Boss Spawn Cooldown` = 2147483647 in `config/apotheosis/adventure.cfg`). Human-sized, armoured, affixed mobs. | **Yes, as the escort** — four named Captains, one with each of waves 2–5, and the elite of every design §6.3 table (B21 unchanged). Not the boss: nothing here is bigger than a man. |
| **Man From The Fog** | The Man From The Fog 1.4 | A stalker that watches, follows and flees; not designed to be killed in a stand-up fight. | No. Stays ambient (structure plan: its house is not in the foot range). |
| **Hordes** | The Hordes 1.5.4c | The horde event ships **disabled** (`enableHordeEvent = false`; only infection is on). It has a command-started mode (`hordesCommandOnly`) that could drive waves 1–4 if the script's edge spawns prove too thin — an option, not the plan (B20 stands). No boss entity. | Backup wave engine only. |
| **In Control!** 9.3.3 | spawn rules | `spawn.json` rules fire `onjoin` (so on summoned mobs too) with `healthmultiply`, `healthadd`, `damagemultiply`, `speedmultiply`, `customname`, `nbt`, `potion`, `helditem`, `armor*`, `angry`; `phases.json` exists (empty). | Not needed for the boss (one `/attribute` command does the scaling); useful if the wave captains need pack-wide rules. |
| **Superb Warfare / Immersive Vehicles** | | No hostile AI vehicles or bosses. | Player side only (the Bradley). |

## 3. The design: "what the beacon woke"

**Story.** The crater is an impact site; the beacon's pulse is a vibration the whole map can feel. Something
under the crater feels it first. Wave 5 is that thing walking up out of the ground at the gate — the
**Sleeper** (a Warden, named) — with four **Captains** (Apotheosis bosses of the pack's own zombie types)
who came for the same signal. The Warden's whole kit reads as this story: it hunts by vibration, the
guns are what it hears, it does not stop for walls, and its boom goes through armour.

**Telegraph.** When stage 5 is placed, the tower function also lays a ring of sculk around the tower's plinth (the
compound, x 64…191 × z −144…−17 — one place, one function) and one sculk shrieker (inert — `can_summon` false) at the gate. Players who know the
game read it at once; players who do not get Tune's line: *"Whatever's under us heard that."* Radio 3
shows wave 5 as "unknown, one, large" for the whole countdown.

**The fight, wave by wave** (the 60-minute countdown ends → waves 45 s apart, design §6.2's cadence):

| Wave | Content | Where | Notes |
|---|---|---|---|
| 1 | Novo's defence table ×1.5 | breaks on the gate (R-B3) | the gate's tier-3 doors hold; players shoot from the walls |
| 2 | the plant's table ×1.5 | gate + the crater's north lip | first Captain |
| 3 | FR-06's table ×1.5 | both approaches | second Captain; Tony's between-wave med kits (X7) |
| 4 | the plaza's table ×1.5 | the whole rim | third Captain; 90 s pause after it, the sculk shrieker screams |
| 5 | **the Sleeper** + the fourth Captain | rises at the gate (summoned 8 blocks outside the doors) | the boss; the doors are what it hits first |

**The Sleeper's numbers (E decides the final values):**

| Item | Value | Mechanism |
|---|---|---|
| Health | 500 + 250 per player online, cap 2000 | `/attribute @e[type=warden,tag=gscraft_boss,limit=1] minecraft:generic.max_health base set <n>` then `/effect … instant_health` or set `Health` NBT on summon |
| Damage | vanilla (30 melee, 10 boom) | untouched; armour and med kits are the counter, as designed |
| Persistence | named, `PersistenceRequired:1b`, tag `gscraft_boss` | `summon minecraft:warden <x> <y> <z> {CustomName:'{"text":"The Sleeper"}',PersistenceRequired:1b,Tags:["gscraft_boss"]}` |
| Aggro | maximum anger at the nearest player on summon | `anger` NBT on summon, or simply the first shot |
| Griefing | none — the Warden breaks no blocks | nothing to switch; `mobGriefing` stays as it is (the zombies still need doors) |
| Boss bar | yes | KubeJS boss bar bound to the tagged entity's health |
| Death | Warden dies normally | drops: vanilla sculk catalyst; the script adds the finale reward (§4) |

**Vehicles.** The Bradley's 25 mm is the intended answer to 2000 HP; whether the sonic boom hits the
vehicle, the passenger, or both is **(E)** and decides whether the vehicle is a tank or a coffin. Either
outcome is a fair rule as long as Marshall's X6 text says which.

**Darkness.** The Warden's Darkness pulse is a screen effect and floodlights do not counter it in
vanilla. The gatehouse's floodlights (R-B3) are still worth building for the earlier waves and for
seeing the Captains; Marshall's line should not promise more than that.

## 4. Win, fail, retry, afterwards

- **Win:** the Sleeper dies → stage `finale_won`; X8 completes (kill task on `minecraft:warden` with tag
  `gscraft_boss`, or a stage set by the script's death hook); the finale chest appears at the plinth:
  the season flag item, a **Warium** decoration set. X9 opens (free play; the board stays live).
- **Fail** (B30): a wave **overruns the tower compound** (five or more attackers inside its rectangle for 30 s, the script's check — the base has no claim marker, its claim is FTB Chunks'), or every player online is
  dead at once → the script kills every `gscraft_boss`-tagged entity and the remaining wave, the beacon
  beam goes dark (stage 5's beacon block swapped for the unlit variant), stage `finale_failed`.
- **Retry:** one in-game day later Marshall's **X6b Relight** (a repeatable, no hand-in) restarts the
  60-minute countdown; Radio 3 shows the same composition, so a team can prepare for exactly what beat
  them. No part is lost.
- **Season 2** (B31): a second part list and a new region (the Woods chain is season 1's); the Sleeper does not return — a season-2
  boss is a later doc.

## 5. What the finale script needs (Phase E build list)

1. `gscraft_finale.js` (server script): countdown from `beacon_lit`; five wave timers; `summon` calls
   for tables and Captains (`/apoth spawn_boss gscraft:captain_<n> rare`); the Sleeper's summon +
   `/attribute` scaling; boss bar; death hook → stages, chest; fail hook (compound overrun / all dead);
   the relight repeat.
2. Four boss definitions `build/datapacks/gscraft/data/gscraft/bosses/captain_1..4.json` (husk, zombie,
   drowned, zombie_villager bases; TaCZ gear sets from Keerdm's items via `valid_gear_sets`; rarity
   rare–epic; +40..+80 HP; knockback resistance 0.5).
3. `tower_stage_5` gains the sculk ring and the inert shrieker; a `tower_beacon_dark` function for the fail state.
4. Quests: X7 unchanged; **X8 "The Sleeper"**: kill task; **X6b Relight**: repeatable, visible after
   `finale_failed`; Tune and Marshall first-time lines for the telegraph and the fail.
5. Tests **(E)**: named warden does not dig down; `/attribute` health holds after summon; TaCZ damage
   registers on it (single hitbox — expected fine); sonic boom vs Bradley occupant; boss bar; the fail
   hook fires when the compound is overrun; the retry countdown; five-player run time (target 12–18 minutes for
   the whole finale).

## 6. What changed elsewhere because of this doc

- Design §7.1 rewritten: the Warden-led wave 5 replaces the dragon; the dragon paragraph is history.
- Quests X8 targets the Sleeper; X6b added (retry).
- Gap audit B30: decided by this doc.
- Mod capabilities: Apotheosis row — the finale's *Captains* (not the dragon) get affixes; Hordes row
  notes the event ships disabled.

Sources: [Minecraft Wiki — Ender Dragon](https://minecraft.wiki/w/Ender_Dragon) (out-of-End behaviour,
damage reduction, `mobGriefing`), [Minecraft Wiki — Wither](https://minecraft.wiki/w/Wither) (wither
armor projectile immunity), [Wither TaCZ Balance](https://www.curseforge.com/minecraft/mc-mods/wither-tacz-balance),
[TaCZ is_projectile compatibility](https://www.curseforge.com/minecraft/data-packs/tacz-is-projectile-compatibility),
Apotheosis 7.4.8 jar (`BossCommand`, `BossEvents`, `data/apotheosis/bosses/*.json`), In Control 9.3.3 jar
(rule keys), the local server's `config/hordes-common.toml` and `config/apotheosis/adventure.cfg`.
