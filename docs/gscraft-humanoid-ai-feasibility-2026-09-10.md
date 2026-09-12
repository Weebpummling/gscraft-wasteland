# GSCraft — Sharper humanoid enemies: feasibility (2026-09-10)

Owner's question: how far can the humanoid enemies (NATO, RUAF, the Scavengers on the mod's soldier body) be taken
in scripting, movement and action. Everything below was checked against the jars on the local server (Forge
1.20.1-47.4.23 mapped, TACZ 1.1.8, Superb Warfare 0.8.9, Recruits 1.15.2, GeckoLib 4.8.4) or against our own code;
nothing is assumed from memory. `[in person]` marks what only a client can prove.

## 1. Where the fighters stand today

`entity/Soldier.java`, `Scavenger.java`, `GunAttackGoal.java`, `Role.java`, on vanilla's goal system:

| Layer | What exists |
|---|---|
| Movement | float, wander, return to a post, walk to a heard shot (`InvestigateGoal`), melee approach; the Marksman backs off inside 16 blocks (`DefaultRandomPos`) |
| Fire | `IGunOperator` draw, aim, burst, reload, bolt; roles set range, aim time, burst length and spread; the Gunner fires at the last seen position for two seconds; the Shield raises a shield while closing |
| Senses | sight (vanilla), gunfire heard at 64 blocks / 12 suppressed, the Sergeant's call to allies within 20 |
| Memory | rank, magazines, out-of-ammo, home and radius (`FighterState`) |
| Groups | placed in groups of 2–4; garrisons and site guards; waves |
| Measured | a 34-strong fight: 2.35 → 4.7 ms per tick (0.07 ms per fighter) |

What they cannot do: take cover, react to being shot at, move as a unit, flank, throw anything, open a door, crouch,
or say anything.

## 2. What the engine gives for free (verified in the mapped jar)

- **Goal system.** Priority-ordered, cheap, and what we use. Vanilla's Brain/Behavior system (villagers, piglins,
  the Warden) is heavier and buys nothing here. Recommendation: stay on goals.
- **Strafing.** `MoveControl.strafe(forward, right)` moves a mob sideways while it keeps facing its target; the
  skeleton's `RangedBowAttackGoal` circle-strafes with it (`strafingClockwise`, `strafingBackwards`, `strafingTime`).
  Peeking from cover and sidestepping after a burst are this call.
- **Obstacles.** `Entity.setMaxUpStep(1.0F)` lets a body step over one-block rubble without jumping.
  `GroundPathNavigation.setCanOpenDoors(true)` plus vanilla's `OpenDoorGoal` lets soldiers use doors (the Dead
  cannot, which keeps a shut door meaningful). Ladders `[in person]`: ground navigation does not plan through them.
- **Sprint.** `LivingEntity.setSprinting(true)` applies the sprint speed modifier and the sprint pose.
- **Poses on the player body.** `setPose(Pose.CROUCHING)` renders a crouch on `HumanoidModel` (`crouching` is read
  from the pose). `Pose.SWIMMING` renders the body flat — a player crawling — which is a prone soldier for free;
  the hitbox follows `getDimensions(Pose)`. `[in person]` on the WarTest client.
- **Item use.** `startUsingItem` (the shield today), swing, off-hand.
- **Vanilla behaviours worth copying:** the pillager's `HoldGroundAttackGoal` (hold at a point and fire), the
  raider patrol (`PatrollingMonster`: a leader with waypoints and followers), `MoveToBlockGoal` (walk to a chosen
  block: a cover spot), `AvoidEntityGoal`, `LeapAtTargetGoal`.

## 3. What the other mods give (verified in their jars)

| Mod | Gives | Usable |
|---|---|---|
| **TACZ** | `IGunOperator` (draw, aim, shoot, reload, bolt, aiming progress); events `GunShootEvent` (we use it for hearing), `EntityHurtByGunEvent` (attacker, hurt entity, gun, headshot) and `AmmoHitBlockEvent` (level, block state, the bullet) | yes — the two hit events are exactly the "under fire" signal a suppression system needs |
| **Superb Warfare** | `HandGrenadeEntity(LivingEntity owner, Level)` on `FastThrowableProjectile` — a grenade a mob can throw; `SmokeDecoyEntity(Level)`; `RgoGrenadeEntity`; its own `GunShootGoal`/`MobGunData` for SW guns (not needed, ours are TACZ) | yes, behind W11's block-damage test |
| **Recruits** | a complete owner-ordered soldier AI: follow / hold / patrol states, formations (`formationPos`, `isInFormation`, `holdFormation`), a leader entity with waypoints and patrol speed, `RecruitDodgeGoal`, `RecruitStrategicFire`, `UseShield` | as a design reference only — it is bound to its own recruit entity and owner model; it proves formations and patrols run fine at this scale |
| **GeckoLib / AzureLib** | animated models with animation files | the route to real animations (reload, lean, vault) — means replacing the player body with a modelled one and making the animations; art, not code |
| **player-animation-lib** | third-person player animations (TACZ uses it) | players only; not for mobs |
| **ParCool** | player parkour | players only |
| **AI Improvements** | trims vanilla look/wander goals for performance | check it leaves our classes alone `[test]` |

## 4. The capabilities, one by one

Effort: S under a day, M a few days, L longer. Every row's test is on the local ticking server unless marked.

| # | Capability | How | Effort | Risk | Test |
|---|---|---|---|---|---|
| A1 | **Doors, rubble, sprint** | `setCanOpenDoors` + `OpenDoorGoal` for soldiers and Scavengers; `setMaxUpStep(1.0)`; sprint while closing or falling back | S | none | path through a door; a 1-block wall crossed without a jump |
| A2 | **Strafe and sidestep** | in `GunAttackGoal`, at mid range in the open: strafe during aim, sidestep 2–3 blocks after a burst | S | none | position change between bursts |
| A3 | **Crouch and prone** | crouch when firing from cover or beyond 24 blocks; prone under heavy suppression and for marksmen; hitbox 0.6×1.5 / 0.6×0.6 | S | the look `[in person]` | pose and hitbox in NBT/`getDimensions` |
| A4 | **Suppression** | a 0–1 value per fighter: +0.3 when a bullet hits a block within 3 blocks (`AmmoHitBlockEvent`), +0.5 when it or a squadmate within 8 is hit (`EntityHurtByGunEvent`), decays over 3 s. Effects: spread ×(1+2s), longer aim, prefer cover, crouch; above 0.8 no fire, head down | M | none | fire near a NoAI soldier: value rises, spread widens, it goes to cover |
| A5 | **Callouts** | chat subtitles on events: contact, reloading, grenade, falling back, man down — lang keys, throttled per squad | S | none | lines appear |
| B1 | **Cover-seeking and peeking** | every 20 ticks in combat: sample 12–16 candidate spots 4–12 blocks away; keep those where a clip from the target's eyes to chest height is blocked and from a 0.6-block lean position is clear; `MoveToBlockGoal` there; fire from the lean, strafe back; leave cover when the target moves out of its arc | M | placement in rubble-heavy Lost Cities ground `[in person]` | probe: a target behind a wall; the soldier ends up with the clip blocked |
| B2 | **Hold and advance** | a Sergeant's order: hold ground at a spot (`HoldGroundAttackGoal` pattern) or advance to a spot; members obey | S | none | order via command, positions checked |
| C1 | **Squads** | leader (the Sergeant) + members with slots; formations wedge / line / column as offsets from the leader's heading; members path to their slot; leaderless squads elect | M | none | slots held while the leader walks |
| C2 | **Patrol routes** | waypoints in zone data (`patrols: [[x,z],…]`), the leader walks them, members in formation; the front's contacts happen where routes cross | M | route authoring | a squad completes a route |
| C3 | **Bounding overwatch** | in contact: half the squad fires while the other half moves 6–10 blocks, then swap | M | none | movement alternation logged |
| C4 | **Fall back** | under half strength or suppressed: withdraw to the last cover spot, then the post; the Sergeant calls it | S | none | withdrawal seen |
| D1 | **Flanking** | when the target has been in cover for 6 s: one fireteam paths to a point 90° off the target's facing, 12–20 blocks out, doors allowed, path length capped at 64 | M | path cost — capped | probe with a NoAI target behind a wall |
| D2 | **Grenades and smoke** | `HandGrenadeEntity(owner, level)` lobbed at a target in cover, one per fighter, 20 s cooldown; smoke from Grenadiers before an advance | S–M | **block damage** — W11's test must pass first (`EXPLOSION_DESTROY` covers grenades or not) | a grenade lands at the target; no block lost |
| E1 | **Data-driven doctrine** | per faction and rank JSON: engage range, cover preference, suppression thresholds, burst pattern, retreat threshold, patrol speed, formation; `/reload`able | S | none | values read back |
| E2 | **Behaviour trees in JSON** | composing behaviours from data instead of Java | L | designers may never need it | — |
| E3 | **Embedded scripting (Rhino is in the pack via KubeJS)** | a JS API for behaviours | M | brings back the silent-failure class of KubeJS bugs | **no** |
| F1 | **Real animations** | GeckoLib bodies and animation files: reload, vault, lean, death | L | art pipeline | `[in person]` |
| F2 | Surrender and capture | a state after suppression + no ammo + outnumbered | M | design | — (review §5 "later") |
| F3 | Vehicles | none in the pack has AI | — | — | **no** (review §5) |

## 5. Performance

Per fighter in combat: one cover search every 20 ticks (16 raycasts, each some microseconds), one path per
2–3 seconds, strafing is free. At five players and ~20 fighters engaged, the additions stay well under the 0.07 ms
per fighter measured today; the one thing to cap is flanking paths (64 blocks) and to throttle cover searches when
more than ~30 fighters are in combat. The Brain system would cost more and give nothing. Measure with spark after
each step, on a ticking server, as with phase 4.

## 6. Testing

Everything but the poses, the animations and "how it feels" tests headless: paths, cover choice, suppression
values, squad slots, grenade landing. The regression suite grows by one phase file per step. The poses and the
cover placement in real ruins need the WarTest client; the grenade block test is the gate for D2.

## 7. Recommended order

1. **Step A** (one session): doors, rubble, sprint; strafing; crouch; suppression from the TACZ hit events; callouts.
   Immediate feel gain, no design risk, all headless-testable except the crouch's look.
2. **Step B**: cover-seeking, peeking, prone, hold/advance. The firefight gets shape.
3. **Step C** — the review's phase 5: squads, formations, patrol routes, bounding, fall-back. The front gets shape.
4. **Step D**: flanking; grenades and smoke after the block test.
5. **Step E**: doctrine as data, so tuning stops needing a build. Behaviour trees only if the designers ask.
6. **Later**: GeckoLib bodies when there is art; surrender after the standing system.

## 8. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| H1 | Stay on the goal system (no Brain) | yes |
| H2 | Crouch and prone as poses on the player body, judged in person | yes, cheap; drop if it looks wrong |
| H3 | Suppression from TACZ's hit events as the core of "under fire" | yes |
| H4 | Grenades gated on the block-damage test (W11) | yes |
| H5 | No embedded scripting language; doctrine as JSON, behaviours in Java | yes |
| H6 | Order A → B → C → D → E | confirm |

## 9. Ruled and built (owner, 2026-09-10)

**H1–H6 all yes; "grenades are definitely going in"; and widen the spawn range.** Step A plus D2 built the same night
(`tools/war_phase7.py` 7 of 7; phases 6, 5, 4b, 4, 3, 2 as regression: 8, 9, 14, 13, 8, 8 of each):

- A1 doors, rubble, sprint: `setCanOpenDoors`/`setCanPassDoors` + `OpenDoorGoal` on both bodies, `setMaxUpStep(1.0)`,
  sprint when the target is well beyond the holding distance. Measured: a Rifleman ordered across a one-block wall
  crossed in 3 s; ordered through a shut oak door, the door was open in 3 s.
- A2 a sidestep of 12 ticks after each burst when standing still in the open (not the Marksman or the Shield).
- A3 stances: crouched from a standstill beyond 16 blocks (the holding distance of every gun rank is past that) or
  from suppression 0.4; flat (`Pose.SWIMMING`, box 0.6×0.6) and silent from 0.8; standing when moving. `[in person]`
  the look.
- A4 suppression: `AmmoHitBlockEvent` within 3 blocks +0.3, `EntityHurtByGunEvent` on the fighter +0.5 and on
  squadmates within 8 +0.25, decaying 1.0 in 3 s; spread ×(1+2s), aim ticks ×(1+s). Measured: a Gunner under a
  Gunner's fire reached 1.0; a fighter with nobody firing stayed at 0.
- A5 callouts: contact, reloading, grenade, pinned - `gscraft.callout.*`, players within 24 blocks, one per key per
  fighter per 5 s.
- D2 grenades: `GrenadeGoal` on Superb Warfare's `HandGrenadeEntity(owner, level)` by reflection (the mod needs
  neither the jar nor the mod), `setLife(100)` for the fuse the item sets, a lob at 8-28 blocks, one per 30 s, at a
  target that went behind cover or one in four at a target in the open; Riflemen carry 1, Sergeants 2, the Scavenger
  Captain 1 (`grenades` in the rank data). The W11 gate: Superb Warfare `explosion_destroy = false` in the
  **world's** `serverconfig/superbwarfare-server.toml` - a Forge server config; the copy in `config/` is only the template,
  and with it alone two grenades that fell off the test platform dug a 7-block crater in the Woods. With the world's
  file set, a detonation on a rimmed platform must leave every block (`war_phase7.py` test 5). That line goes to live
  with this build, into `/wasteland-v8/serverconfig/` - it also stops players' explosives breaking blocks, which the
  builders' ruling wants anyway.
- The range: open ground places 36-72 blocks out (was 28-52) in an 80-block count box at the full cap. Director
  placements are persistent now and the director sweeps its own back past 160 blocks from every player; vanilla was
  despawning anything beyond 32 blocks at random, which the wider ring would have made worse.
- `/gscraft fighter <who>` reads rank, magazines, grenades, suppression, pose, sprint, target; `… goto <x y z> now`
  orders a walk (the first piece of B2). The per-shot debug log line is gone.

**Step B built the same night** (`tools/war_phase8.py` 6 of 6; 7, 6, 5, 4b, 4, 3, 2 as regression: 7, 8, 9, 14, 13, 8, 8 of each):

- B1 cover (`entity/Cover.java`): sixteen candidates 3–10 blocks out on the fighter's side of the target; a spot
  counts when the target's eyes cannot see its chest height and a lean 0.8 blocks beside it can see out from head
  height; nearest wins. The gun goal walks there, crouches, steps to the lean for a burst and back for the pause;
  cover is dropped after two seconds of the target seeing into it. Measured: a Rifleman with a wall to one side chose
  the spot behind it, was hidden from the target in 15 of 24 seconds and took the target's health down through the
  lean. Not for the Shield; an advancing fighter takes none; a holding one only within six blocks of its point.
- B2 orders (`FighterState.Order`, `OrderGoal`): HOLD never chases and fires from its point (measured: 0.0 blocks of
  drift over fifteen seconds at a target 40 off); ADVANCE walks to the point at speed and becomes HOLD on arrival
  (6 s over 24 blocks with a target in view). `/gscraft fighter <who> hold|advance <x y z> now`, `free`,
  `squadhold|squadadvance` for the fighter and every ally within twenty blocks (the Sergeant's call). The old
  `goto` is an advance.
- A3: the Marksman goes flat to fire beyond 32 blocks, once its aim is complete. Two findings from ground-level
  tests: a lowered eye over rough ground blinks, so the aim counter now decays on a blink rather than restarting,
  and a lowered stance that loses sight stands back up for five seconds. Target memory is fifteen seconds unseen
  (vanilla's three made cover cost the target); the Soldier's follow range is 64, the Scavenger's 40, since
  targeting is capped by it.
- Readout: `/gscraft fighter` adds order, cover spot, and whether the fighter is hidden from its target.

**Step C built 2026-09-11** (`tools/war_phase9.py` 6 of 6; 8, 7, 6, 5, 4b, 4, 3, 2 as regression, see HANDOFF):

- C1 squads (`entity/Squad.java`): a squad is a shared id and a slot on each body, nothing else stored (no SavedData -
  the design's registry is not needed while the bodies carry it). Slot 0 goes to a Sergeant if there is one; the
  leader is the lowest slot alive. Everything the director places together is a squad (a group, a garrison, a wave in
  sixes). Out of a fight the members walk to their slots around the leader (`SquadFollowGoal`, priority 5, below the
  gun, order and grenade goals): wedge (pairs two back and two out, alternating sides), line (2.5 apart abreast),
  column (2.5 apart behind). Measured: three of three in the wedge within seven blocks behind the leader after an
  advance, three of three abreast within eight seconds of `formation line`.
- C2 patrol routes (`PatrolGoal`, zone `patrols` in `gscraft_zones/map.json` from `tools/war_zones.py`): an idle
  leader in a zone with routes takes the nearest one from its nearest waypoint and loops it at speed 0.9; y is found
  on arrival at each column. Routes on the two fronts (x -1200 and -940, z -1230 to -720), a loop round the town
  centre and one round the switchyard. Measured: two waypoints reached in order at 11 and 22 s; a director group at
  the switchyard picked up the route by itself.
- C3 bounding overwatch (`Squad.leaderTick`, once a second): with a target beyond 1.2x the hold distance the leader
  splits the squad by slot parity; one team gets ADVANCE eight blocks toward the target, the other HOLD where it is,
  and the teams swap every four seconds. Measured against a target 45 blocks off: in 10 of 16 seconds some moved
  while others held, and the squad's mean distance went 42 to 24.
- C4 the fall-back: under half strength, or the leader at suppression 0.6 with half the squad at 0.5, everyone gets
  ADVANCE to a point twenty blocks away from the target (which becomes HOLD on arrival) and the leader calls
  "Fall back!"; a squad that fell back does not bound again for a minute. Measured: two of four killed, mean
  distance to the target 40 to 52 in twelve seconds. Squad-issued orders are marked (`orderBySquad`) and released
  when the target is gone; an operator's order is never overridden.
- `/gscraft squad <who>` reads squad, slot, leader, alive, formation, route; `form` (allies within twenty),
  `disband`, `formation wedge|line|column`, `route <x z x z ...>`, `patrol` (take the zone's route now).
- Found by the regression run, both from step B: a fighter looked for cover as soon as the target was inside 1.2x its
  range, so a Rifleman dug in forty blocks out and never advanced - cover is now taken only inside 1.2x the holding
  distance (the squad bounds beyond it; the Marksman's hold is its whole range). And the pause between bursts only
  counted down while the target was in sight, so a fighter whose pause outlasted its step back behind cover never
  leaned out again (the Marksman, every time: pause 30-50 ticks, one shot). The pause is time now. A cover spot the
  body cannot reach in five seconds, or is not actually hidden at once it stands there, is given up. The Marksman goes
  flat in the open only: a cover's lean is judged from the crouched eye, and flat behind it he saw nothing and never
  fired. A lean has to have room for the body (the search only asked for a line of sight, and a lean inside a bush
  left the fighter pinned behind its cover); a lean not reached in two seconds drops the spot. A garrison is not
  a squad: guards that followed a leader left their posts and the garrison refilled behind them.

**Resource handling (owner, 2026-09-11: "run the improvements and test the performance cost")** - `tools/war_phase10.py`
8 of 8, the rest as regression:

- The ambient cap counts ambient creatures only: garrisons, lairs and waves are kept by their own rules and no longer
  eat a zone's cap (the camp's garrison took 5 of 7, so ambient groups there were refused or arrived as pairs).
- Two ceilings over the per-ground caps: at most 12 director creatures within 80 blocks of a player whatever the
  ground types stack to, and at most 96 on the server. Both are counted on the sweep's walk, once a pass.
- The sweep is 128 blocks (was 160) with one pass of grace: a placement has to be out of range on two passes
  running (20 s) before it is taken back, so a player who sprints or falls back keeps the group behind them.
- A garrison or lair with nobody within 256 blocks for three passes is taken back and its refill clock cleared, so
  it is re-placed the moment someone comes within 128 again (measured: 4 -> 0 -> 4 in one pass on return).
- An assault or counterattack with nobody within 128 of the fight freezes its clocks (deadline and next wave move
  with the time) and after a minute takes the wave back; the next wave comes when someone is back (measured: clock
  4:56 before and after 66 s away, wave 5 -> 0 -> 7 after the return).
- A patrol only walks with a player within 96 blocks of the leader; otherwise the squad waits where it is instead of
  walking its 500-block route into the sweep and being refilled behind.
- Corpses: a creature killed in a chunk that is loaded but not ticking (the border ring of the simulation distance)
  never finishes dying - the body sits there for good, invisible to `@e` selectors, and every count that did not ask
  `isAlive` took it for a living one. Seventeen of them at the camp held the ambient cap at 17 of 7 for an
  afternoon of tests. Every count asks `isAlive` now, horrors have their own tag and do not count against the
  ambient cap either, and the sweep takes any dead director body back at once. `/gscraft director census <x y z>`
  lists what the cap is counting.
- Phantoms: `/gscraft director phantom set|add <x y z>|clear` stand in for players on a server with none (the
  director, the sweep, the garrisons, the loop's away rule and the patrols all read them), and
  `/gscraft director bench <passes>` runs full director passes for everyone present and times them.

How it scales with players, measured on the bench (a pass is what the director does every 10 s; the fighters' own
AI is not in these numbers):

| present | ms per pass (mean / worst) | director creatures at the steady state |
|---|---|---|
| one player | 0.06 / 0.5 | 8 around them |
| four together (within 6 blocks) | 0.09 / 0.3 | 7 around them - one shared count box |
| four spread 250 apart | 0.12 / 1.2 | 29 across the four boxes, under the server ceiling of 96 |

So the director's own cost is nothing; the entity count is what scales, and it scales with how far apart the
players are, not how many there are: a party shares one cap, a spread-out server tops out at the ceiling.

**Settings as data (owner, 2026-09-11: "what else can go into settings instead of a jar update")** -
`tools/war_phase11.py` 5 of 5:

- `data/gscraft/gscraft_settings/*.json` (`world/Settings.java`, a reload listener like the zones). Every file is
  applied in name order over the code's own numbers, so the jar's `defaults.json` documents the baseline and a
  world datapack's `zz_live.json` carrying only the keys to change overrides it; `/reload` applies it, no jar.
  Unknown keys are logged and ignored. `/gscraft settings [prefix]` prints what is in force, with the default
  beside anything changed.
- 117 values: the director (interval, sweep, both ceilings, the garrison wake and rest, horrors, the sealed share),
  the three grounds (cap scale, radii, count box), the strongpoint loop's clocks and counts, the squads (size,
  bounding, fall-back, patrol range), the fight (hold factor, reload, stances, cover timers), cover search,
  grenades, callouts, how far a shot is heard, projectile age, and the whole role table (range, aim, bursts, pauses,
  spread, hold-at for each of the six roles).
- Not here: anything fixed on a body at spawn (follow range, health, kit) - those are attributes and rank data.
- The server ceiling is 48 now (a five-player server on shared cores; 12 per player stays).

The Bisect host, read from the panel: node la308, 8 GB, 8 vCPU threads (cpu limit 800 %), Java 17 image, Forge
47.4.10 on live against 47.4.23 locally, 3.9 GB in use and 0.16 ms per tick with nobody on. The CPU model is not
exposed by the panel.

**Measured on the host, 2026-09-11 19:11** (`tools/live_loadtest.py`, the server empty, Hordes' pause off for the
run and restored after):

| on the platform | ms per tick (overworld) |
|---|---|
| idle, platform loaded | 1.6 |
| 24 fighters standing, no enemy | 2.25 |
| 24 v 24 in a firefight | 3.8 - 4.0 |
| 48 v 48 in a firefight | 5.1 - 6.0 |

About 0.05 ms per fighter in combat, 0.03 idle: the whole server ceiling of 96 fighting at once is 4-5 ms of the
50 ms tick. The enemy layer is not what will lag the host; chunk loading and the players' own traffic are. The
ceiling can be set by gameplay, not by the CPU.

Next: step D (flanking, smoke) and E (doctrine as data) when the owner asks; the fold-in order continues with the
quest-book stage bridge, survivors and vendors.

Related: `gscraft-enemy-review-2026-09-10.md` §5 (behaviour by value and cost) and §11 (phase 5), `gscraft-war-mod-design.md` §5–6 (squads in SavedData), `gscraft-fold-in-review-2026-09-10.md`.
