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

Next: step C (squads, formations, patrol routes, bounding overwatch, fall-back).

Related: `gscraft-enemy-review-2026-09-10.md` §5 (behaviour by value and cost) and §11 (phase 5), `gscraft-war-mod-design.md` §5–6 (squads in SavedData), `gscraft-fold-in-review-2026-09-10.md`.
