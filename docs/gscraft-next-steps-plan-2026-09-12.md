# GSCraft Wasteland — the next steps, planned (2026-09-12)

*Plan, 2026-09-12 (owner: "lets move on and start working on the next steps, go ahead and plan this out"). This
turns the ruled order of work of `gscraft-system-design-pass-2026-09-12.md` §9 into sessions, files, tests and the
few decisions still open. Nothing here is built yet. What it reads against: the system pass (S1–S10 ruled), the
compound start (`gscraft-start-compound-2026-09-12.md`), the camp spec (`gscraft-camp-spec.md` §1), HANDOFF §5,
and the mod as it stands (phases 2–24 green; armour live since 14:42 today with pack 2026.09.12.7).*

---

## 0. Where we are

The enemy layer is live and complete for now: fighters, the director, the sites, and since today armour with
riders, the bail-out and the tamed blasts. The system pass's step 5 (S10, the live push) therefore happened
**before** its step 4 (the owner's in-person pass), by the owner's call on the day. Everything below is the player
side of the loop and the small rules that connect the two layers. The order stays the pass's order; the live push
at the end carries data only (spawn, zones, sites, the datapack), no new entity, so it needs no pack.

Five pieces of work, in order, each with its test gate:

| Step | What | Size | Gate |
|---|---|---|---|
| 1 | The start: spawn, the gate datum, zone growth by stage, the torches | one session | phase 25 |
| 2 | The five building takes as sites; the survivors' summon functions | one session | phase 26 |
| 3 | Stage gates on compositions and waves; bosses placed by the site loop | half a session | phase 27 |
| 4 | The owner's in-person pass on local, budget measured | owner | notes in HANDOFF |
| 5 | Live: the data push and the spawn commands | an empty window | boot log |
| 6 | Phase C, the player layer (KubeJS + FTB Quests), Act I chain first | several sessions | per chapter |

## 1. The start

*Built 2026-09-12, phase 25 green (5/5), phases 6/20/21 green. Two findings on the way: the counterattack's infantry
had never been ordered to walk anywhere (it stood at the approach) - `sendWave` now marches it to the gate and the
Dead's waves are walked a leg at a time; and the defended check counted the wave within 128 of the square's centre,
which misses the north approach from the compound - it counts within 400 of the gate now. Boxes measured from the
skadowsky-camp §2-3 rectangles with a few blocks' margin; the gap torch sits at (-947, -890) on the paving.*

**1a. The spawn.** Console commands, no world upload, on each server: `/setworldspawn -956 65 -876` and
`/gamerule spawnRadius 4`. Local first; live in the step 5 window. Checked by `cat level.dat` is not possible
through the panel, so the check is the command's own reply and a fresh join by the owner (step 4).

**1b. The gate datum** (`gscraft_sites/camp.json`, `Sites.CampDef`, `Loop.counter`): `square` becomes the
compound box `[-980, -920, -897, -818]` (the loss check: five attackers inside for 30 s); a new `gate: [-948, -893]`
is the counterattack's target (armour drives there, infantry walks there); the four approaches stay as the wave
points. `Loop.sendWave` already takes a target; `counter()` passes the gate when the file has one, else the
square's centre as now.

**1c. Zone growth by stage** (`Zone`, `Zones.at`, `tools/war_zones.py`, `map.json`): a zone gains an optional
`stage`; `Zones.at` ignores a zone whose stage is not set (`Stages` already keeps the set on the server), so the
director's denial grows with the players' ground. The single `camp` exclusion becomes six boxes:

| Zone | Box | Stage |
|---|---|---|
| `camp_compound` | −980…−920 × −897…−818 (the compound doc §2) | none — always |
| `camp_square` | the junction and the streets off it, around (−940, −979) `[needs measurement]` | `square_taken` |
| `camp_gatehouse` | the bridge's east end `[needs measurement]` | `gatehouse_taken` |
| `camp_north` | the north complex: clinic and shack, around (−948, −1026) `[needs measurement]` | `clinic_taken` |
| `camp_crossing` | the signal box x −905…−897 × z −975…−967 and the crossing | `crossing_taken` |
| `camp` | the old pocket −978…−770 × −1060…−845 | `skadowsky_held` |

The boxes come from the v8 census tools against the local world copy (the compound doc did the same), not from
older documents. A zone with a stage that is not set is also not an exclusion for `Patrols.roll` and the ambient
pass, which both go through `Zones.at` — one change covers both.

**1d. The torches** (`tools/camp_torches.json`, `tools/camp_torches.py`, datapack functions): two at the start —
`yard` (−957, 66, −862) stays, `gap` new at the gap's inside corner about (−945, 65, −890) — and four by stage:
`square`, `gatehouse`, `clinic`, `crossing`, each its own function `gscraft:torch_<name>` that places the Magnum
Torch on its ground block, run by the loop when the building's site goes `held` (step 2 gives the loop that hook).

**Phase 25 (`tools/war_phase25.py`):** the director's bench with a phantom in the yard places nothing inside the
compound box; with the phantom on the square it places there before `square_taken` and nothing after
`/gscraft stage add square_taken`; a counterattack wave sent by the director command with the gate as its target
arrives at the gap (the drive's "reached waypoint" line, the infantry within 12 of the gate); the torch functions
place their blocks and are idempotent.

**Doc pass with it:** the compound doc's §8 table — `gscraft-skadowsky-camp.md` §3/§5, `gscraft-onboarding.md` §2,
`gscraft-entities-v8.md` §4 (the home row), `gscraft-objectives-v8.md` §0–§1, `gscraft-quests.md` §7–§8,
`gscraft-finale.md` (the compound is the fall-back), `sectors_v8.json` (a `compound` rectangle).

## 2. The building takes as sites

**2a. Five site files** (`gscraft_sites/`): `square`, `gatehouse`, `north` (the clinic and the shack together —
one take, two survivors), `crossing`, and `mast` (the gun pit and the field; its `held` is the pocket's). Each:
box, anchor, faction, `approach`, no assault waves, one defence wave. The occupiers are the Dead (the home
sector's faction in `gscraft-entities-v8.md` §4; D1).

**2b. The loop with no assault** (`Loop`): today the ladder climbs by assault waves. A site whose `assault` is
empty goes `scouted` when a player is inside (as now) and `held` when its box has held no hostile fighter for 60 s
of online time with a player inside it — a clear, not a fight to a table. The defence wave and the counterattack
then work as for any site, so a taken building can be lost and retaken. Stages `<id>_held` are what everything
else keys on; the compound doc's names (`square_taken` …) are aliases the loop also sets, so the quests and the
zones can use the readable name.

**2c. The held hook** (`Loop`, site file): an optional `"held": ["gscraft:camp_npc_marshall", "gscraft:torch_gatehouse"]`
list of functions the loop runs once when the site first goes `held`, and `"lost": [...]` for the reverse. That is
the survivor moving in and the torch lighting, with no KubeJS in the path.

**2d. The functions** (`tools/camp.py`, new, writing `build/datapacks/gscraft/data/gscraft/functions/`): the camp
spec §1 pared to what these steps need — `camp_npc_<npc>` (6) and `camp_npcs` (1) with the NBT shape the spec gives
(NoAI, invulnerable, persistent, silent, named, tagged), the six `torch_*` (1d), and `camp_signs`. The `camp_<npc>_<tier>`
building templates (24), the board columns, the rack and the gun pit stay Phase C/D work. Positions: Walker in the
hall, Michael in the brick block, Marshall in the gatehouse, Tony in the clinic, Tune in the shack, James in the
signal box — each `[needs measurement]` to the block, from the local world copy.

**Phase 26:** the five sites load (`/gscraft sites`); a site with no assault goes `held` after the clear; its held
functions ran (the villager with the tag exists, the torch block is there); the readable stage is set; the
defence wave and the loss put it back; the zone box opens and closes with it (ties to phase 25).

## 3. Stage gates and placed bosses

- **`stage` on a composition** (`ArmourDef.Composition`, `Patrols.roll`, `war_zones.py`): a composition whose
  stage is unset is skipped when the roll picks. The plant's zones get the tank compositions gated on
  `switchyard_scouted`; the APC-only ones stay open (S3: armour near the start is fine).
- **`stage` on a wave entry** (`Sites.WaveEntry`, `Loop.sendWave`): an entry whose stage is unset is not sent.
  The Skadowsky sector's defence wave 3 carries one APC gated on `line_depot` (S4).
- **`boss` on a site file** (`Sites.SiteDef`, `Loop`): `{"vehicle", "name", "at": [x, y, z], "tx", "tz", "stage"}`;
  the loop places it once through `Armour.wave` when the site is `scouted` and the stage is set, and remembers it in
  the site data so a restart does not place a second. S6: the T-90 at the plant gate on `switchyard_scouted`; the
  M1A2 at the bridge in Act IV; the finale's last wave carries a tank (that one is a wave entry, not a boss block).
  Names go to `gscraft-quests.md`.
- The crewman rule (§5.8 of the pass) is done.

**Phase 27:** thirty forced rolls on a gated composition place nothing until the stage is set and place within a
few after; a gated wave entry is absent from the wave's count and present after; the boss appears once on
`scouted` + stage, named, holding, and not again after a `/reload`.

## 4. The owner's in-person pass

On local, from the yard through the square to the hospital with the armour on: does the compound read as a
start, does the first APC land where the pass says, do the bail-out and the riders behave in a real fight, is the
chat's silence right. The budget of the pass §7 measured with two APC patrols and a firefight (spark's tick
report). Numbers that may move afterwards, all settings: `armour.bail_share`, `armour.bail_chance`,
`armour.dismount_range`, `armour.view_cone_*`, `armour.engage`.

## 5. Live

An empty window (`list` first): the jar (steps 1–3 are code too: the zone stage, the loop's clear and hooks, the
gates) into `/mods`; the datapack functions into `/wasteland-v8/datapacks/gscraft/` (a datapack folder, as today's
override went); the two console commands of 1a; the boot log. No new entity type, so the pack build is optional —
build it anyway so the client jar matches.

## 6. Phase C, the player layer

Built against the system pass and the compound doc, Act I's chain first because steps 1–3 give it its stages:
Marshall's gap (`compound_closed`), the square, the gatehouse, the clinic and the shack, the crossing — then the
five introduction chapters, the items with stack sizes and the bulky rule, the stations and the `bp_*` stages, the
loot tables by building, the NPC right-click to the quest book, Walker's storage levels, and the board's clock
and warning signs (HANDOFF §5, `gscraft-quests.md`, `gscraft-onboarding.md`, `gscraft-loot-tables.md`). Each
chapter is its own session with the quest book opened on WarTest as the gate. KubeJS work runs
`tools/kubejs_trapscan.py` first (the traps note).

## 7. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| D1 | Who occupies the pocket's buildings at the start | **the Dead**, as `gscraft-entities-v8.md` §4's home row has it for the whole sector (the site files' `faction: dead`; the defence wave and the counterattack from the Dead's tables); the living factions arrive with the sites beyond the pocket |
| D2 | How `compound_closed` is set | by the quest hand-in in Phase C; until then a `/gscraft stage add` — no block detector |
| D3 | The clear timer for a building take | 60 s of online time with a player inside and no hostile; a setting `site.clear_ticks` |
| D4 | The clinic and the shack as one take or two | **one** (`north`): one clear, two survivors, one torch |
| D5 | Step 4 before step 5 | **yes** for this push — the data goes live after the owner has walked it once |

## 8. Order of the sessions

1. Step 1 (measure the five boxes, the zone stage, the gate datum, the torches, phase 25, the doc pass).
2. Step 2 (the five site files, the loop's clear and hooks, `tools/camp.py`, phase 26).
3. Step 3 (the three gates, the boss block, phase 27).
4. Step 4, the owner; then step 5 in an empty window.
5. Step 6, chapter by chapter.
