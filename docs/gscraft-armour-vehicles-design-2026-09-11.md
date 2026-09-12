# Armour as enemies: BMP-2, Bradley, T-90, M1A2 — design (2026-09-11)

Owner's brief: four vehicles as special entities with their own scripting — in wave attacks, as a rare random
patrol (an APC with foot infantry, a single tank, rarer a tank with an APC or two APCs), in event attacks, as
quest bosses. Immune to small arms, killed by explosives, with armour part damage as far as we can, and the
vehicle's state told to the players in chat.

Read from the Superb Warfare 0.8.9 jar and its data on the server; nothing here was tried in the game yet.

## 1. What the pack already has

All four exist in Superb Warfare as vehicle entities, player-driven today, with GeckoLib models, engine sounds,
turrets, weapons and a destruction sequence:

| entity | id | health | main gun (data) | secondary | seats |
|---|---|---|---|---|---|
| BMP-2 | `superbwarfare:bmp_2` | 300 | 30 mm 2A42, auto, 65 a hit, 250 rpm, 40-tick shells | ATGM, coax MG | 7 (troop bay) |
| M2 Bradley | `superbwarfare:bradley` | 300 | 25 mm, auto | TOW, coax | 7 (troop bay) |
| T-90A | `superbwarfare:t_90a` | 500 | 125 mm, one in the tube, 700 AP / 250 HE, 5 s reload | commander's MG station | 3 |
| M1A2 | `superbwarfare:m_1a_2` | 500 | 120 mm, same shape | commander's MG station | 5 |

Everything about them is data in `data/superbwarfare/sbw/vehicles/<id>.json` — health, the weapons above,
turret speed, mass, step height, a **damage modifier list**, the **parts** (hull boxes, `Turret`, `WheelLeft`,
`WheelRight`, `MainEngine`, each an oriented box with its own health), and `DestroyInfo` (the wreck's blast, 160 or
200 damage in 8 or 16 blocks, sympathetic detonation). A world datapack file at the same path overrides any of it.

The damage modifiers are exactly the immunity rule the brief asks for, and they are already there. The T-90's
list starts `arrow 0, trident 0, mob_attack 0, player_attack 0, #superbwarfare:projectile 0` — its own bullets
do nothing — then `All - 20` (twenty points off every hit), `All * 0.2`, and multipliers for what should hurt:
TNT ×4, aerial bombs ×12, vehicle strike ×2.5, explosions ×2, mines ×0.5, cannon hits ×1.3. The BMP-2's is
softer: no zeros, `All - 13`, `All * 0.2`, explosions ×6, mob attacks ×2.5, SW bullets ×0.1. Two gaps for our
guns and grenades:

- TACZ bullets are not in the lists. They arrive as TACZ's own damage types (`tacz:bullet`, `tacz:bullet_ignore_armor`)
  and fall to `All - 13` / `All * 0.2`: a 5.56 round does nothing to a BMP (6.5 − 13 < 0) and a .338 does
  (42 − 13) × 0.2 = 5.8, which over 52 rounds kills it. The override file adds `tacz:bullet 0` and
  `tacz:bullet_ignore_armor 0` to all four, and that is the small-arms immunity: no code.
- Superb Warfare's own explosions (`custom_explosion`, `projectile_explosion`) are ×2 on the APCs and ×0.65 on
  the tanks; TACZ's 40 mm and the Superb Warfare hand grenade go through `custom_explosion`. Numbers to set at the
  table: what a grenade, a claymore, an RPG and C4 should each be worth against an APC and against a tank (§5).

Angle counts already: the tanks' modifiers end in a custom rule that reads the hit's angle to the hull
(`getSourceAngle`, 0.15 for the rear arc), so a shot from behind does more. Part hits are already resolved
(`OBBHitter` gives the part the hit landed on; each part has its own health; `TURRET_DAMAGED`, `L_WHEEL_DAMAGED`,
`MAIN_ENGINE_DAMAGED` flags exist and the vehicle slows, stops steering one side, or loses its turret when they
trip). We do not build part damage; we surface it.

What the mod does not have is a driver that is not a player. The enemy review of 2026-09-10 was right about that
("no vehicle in the pack has AI"). But the vehicle reads its controls from synced entity data — `setForwardInputDown`,
`setLeftInputDown`, `setFireInputDown` and the rest are public — and it already has an **AI turret**:
`AI_TURRET_TARGET_UUID` is a synced field and, when set, the vehicle's tick calls `turretAutoAimFromUuid` and lays
the turret on that entity by itself (the sentry towers use it). `vehicleShoot(LivingEntity, UUID, Vec3)` fires the
selected weapon for a given gunner. So a driver is a controller that sets inputs and a target each tick; the
vehicle does the driving, the turret and the shooting.

## 2. The shape: a crew, not a new vehicle

We do not make our own tank. We spawn Superb Warfare's vehicle and give it a **crew**: an invisible, silent,
un-hittable `gscraft:crew` mob that rides the driver's seat. The crew is a `Mob` on our side (a faction member like
a Soldier, so the players' targeting, the hold, the sweep, the director and the squads all already know it), and its
AI is a handful of goals that write to the vehicle:

- **Drive**: a path to a goal point (a patrol waypoint, a site's edge, the squad's leader) turned into forward /
  back / left / right inputs each tick from the heading error — a vehicle is not a pathfinding mob, so the crew
  plans with the mob navigator on its own body position (it has one, it is a mob) and steers the hull to follow the
  path's next node; a node it cannot reach in ten seconds is skipped, a wall it cannot pass is reversed from. Speed
  by the `sprint` input on roads, off it in a fight. Roads are what the map is built on, and the vehicles stay on
  them by preference (the pathfinder's own road weighting) — an APC climbing a hillside is the thing to avoid.
- **Fight**: the crew picks targets the way a Soldier does (hostile factions, players, follow range 64) and sets
  `AI_TURRET_TARGET_UUID`; when the turret has laid (`getTurretYRot` within tolerance of the bearing and a clear
  line) it calls `vehicleShoot` at the weapon's own rate. The BMP and Bradley pick the cannon for infantry, the
  missile for another vehicle; the tanks fire HE at infantry and AP at armour, and the T-90's commander MG station
  is worked as a second gunner (`AI_PASSENGER_WEAPON_TARGET_UUID`).
- **Halt and cover**: a tank that has a target stops to shoot (`forward` off) and creeps to keep the bearing; an
  APC halts, drops its infantry (§3) and covers them from twenty blocks back; a crew that loses its engine sits and
  fights as a pillbox; one that loses the turret drives away at full speed.
- **Retreat**: below a third of health, or with the turret and engine both gone, the crew drives for the nearest
  map edge in its faction's direction and the director takes the vehicle back past the sweep; a wreck stays (the
  mod's own wreck entity) and is loot (§6).

The crew is the entity the rest of the mod deals with. It carries `FighterState` like a Soldier (faction, squad,
orders, suppression — a tank's suppression is what the commander feels, and a pinned crew buttons up and stops
firing the MG). It dies with the vehicle (`IS_WRECK` on the vehicle removes the crew). Killing the crew any other
way is impossible: it is `invulnerable`, no hitbox, never targeted.

## 3. Where they appear

Four ways in, all through the systems that exist:

**A rare random patrol** — a new zone entry, `armour`, next to the ambient pools:
```
"armour": {"chance": 0.06, "compositions": [
    {"weight": 6, "vehicles": ["superbwarfare:bmp_2"], "infantry": 4},
    {"weight": 3, "vehicles": ["superbwarfare:t_90a"]},
    {"weight": 1, "vehicles": ["superbwarfare:t_90a", "superbwarfare:bmp_2"], "infantry": 4},
    {"weight": 1, "vehicles": ["superbwarfare:bmp_2", "superbwarfare:bmp_2"], "infantry": 6}]}
```
The director rolls it on a pass, in open ground only, on a road stand (a new `roadStand` search: a placement
column whose block is one of the road materials, within the placement ring), never inside 96 blocks of a player
(a tank should be heard first) and at most one armour group per 400 blocks. NATO zones roll Bradley / M1A2, RUAF
zones BMP-2 / T-90. The infantry is a squad of that faction formed around the vehicle and told to walk with it
(`SquadFollowGoal` on the crew as leader; the vehicle is slot 0). It patrols the zone's route if it has one, else
the road it stands on, both ways. It counts one vehicle as four against the ceilings (settings), and the sweep
takes it back past 128 like anything else. The APC's troop bay is a real mechanic here: its four riders sit in the
bay (`Seats`, hidden passengers) until the crew halts for a fight, then dismount — the mod's own seat handling does
the mounting, we call it.

**Waves** — the site files gain an optional `armour` per wave (`"armour": ["superbwarfare:bmp_2"]`). The loop
places it at the wave's edge point on a road stand, with the wave's infantry as its riders where they fit. The
counterattack's third wave at the camp gate is the natural place for a tank and it is the one that turns the gate
fight into an event: no rifle stops it, the players need the mine, the RPG or the C4 they were told to build.

**Event attacks** — the strongpoint loop's assault on a held site already has the shape; an armour entry on an
assault wave is the same code. A "convoy" event (a truck with an escort along a road between two sites, loot in
the truck) is the next one and needs only the drive goal and a route; it is out of scope here and noted.

**Quest bosses** — a boss is a vehicle with a `boss` tag in its spawn: a named vehicle (a name over it), a boss
bar (the loop already draws one for the assault), a fixed position until engaged, and a stage tag on death
(`Stages.add`) so the quest book reads it. The T-90 at the plant gate, the M1A2 the NATO column lost at the bridge.

## 4. What the players are told

Vehicle state goes out in chat, from the crew, to every player within 64 blocks, throttled like the callouts:

- **Contact**: "[T-90A] Engine noise to the north" when a vehicle first comes within 96 of a player (before it is
  seen; the mod has the vehicle's engine sound, this is the text).
- **Hits**: each hit that does damage prints what it did, in the players' terms:
  "[BMP-2] Hit — hull, 24 damage (276 left)", "[BMP-2] Hit — left track damaged, it is slowing",
  "[T-90A] Turret hit — the gun is out", "[T-90A] Engine hit — it is burning", "[T-90A] Hit — the shell bounced
  (front armour)" for a zero or near-zero result, "[T-90A] Rifle fire does nothing to it" once per fighter per
  minute for small-arms hits so the players learn the rule from the game.
- **State**: "[BMP-2] Withdrawing" on the retreat rule, "[T-90A] Destroyed" with the killer's name, and the
  dismount "[BMP-2] Infantry dismounting".

Under the messages, the same information as a boss bar for the engaged vehicle (health as the bar, the parts as
letters in the name: `T-90A  ▮▮▮▮▯  T E L R`, a letter dimmed when the part is gone). The bar shows to players
within 64; it is the loop's bar code with a second key.

## 5. Numbers to settle, and where they live

| lever | where | starting value |
|---|---|---|
| small arms | `sbw/vehicles/*.json` override, `tacz:bullet 0`, `tacz:bullet_ignore_armor 0` | immune |
| hand grenade vs APC / tank | override, `superbwarfare:custom_explosion * n` | APC 2 (120 → 60 after `- 13`, ×0.2 … the list is applied in order; the table needs the mod's order, which is the order written) |
| RPG, C4, claymore, mines | override | RPG a third of an APC, a sixth of a tank; C4 kills either; a claymore scratches; a mine takes a track |
| 40 mm and the Bradley/BMP cannon vs each other | override `superbwarfare:projectile_hit` | as shipped (×1.35 / ×1.3) |
| tank cannon vs a player | the weapon's own `Damage` 700 AP / 250 HE | a hit is a death; the HE blast of 120 in 10 blocks is what the players dodge |
| how many, how often | zone `armour.chance`, compositions, one per 400 blocks, four ceiling points each | rare: a 6 % roll per pass in open ground |
| crew behaviour | `gscraft_settings` `armour.*`: engage range, halt distance, retreat share, dismount distance, message throttle | 64 / 30 / 0.33 / 24 / 30 s |

The exact grenade and RPG figures need the modifier order confirmed in the prototype (a `- 13` before a `* 0.2`
and a `* 2` after it is not the same as the other way round), which is an hour with `/gscraft hit` extended to
vehicles.

## 6. Loot and the wreck

A destroyed vehicle leaves Superb Warfare's wreck (the mod's own, with its blast), and the drops file gains
entries for the crew: the vehicle's ammunition type (30 mm, 125 mm shells), fuel cans, a vehicle part item
(military materials for the crafting design's vehicle tier), and for a boss its quest item. The wreck is a
landmark for a day (the mod's wreck entity persists) and the director's sweep leaves wrecks alone.

## 7. Order and cost

| step | work | proves |
|---|---|---|
| V1 | the override datapack file for the four vehicles (small-arms zeros, the explosive multipliers); `/gscraft hit` on a vehicle; a summoned T-90 shot with an M4, an AWP, a grenade, an RPG | the immunity and the explosive numbers, no code |
| V2 | `gscraft:crew`: the invisible mob, mounting the driver's seat, the drive goal on a fixed route; the road stand search | a BMP drives a road loop by itself |
| V3 | the fight goal: targets, the AI turret, firing, halt-to-shoot, the second gunner; the retreat rule | a T-90 stops, lays and fires at a fighter, withdraws when hurt |
| V4 | the chat messages and the bar from the hurt event on vehicles (part flags, angle, zero results) | the players read the fight |
| V5 | the zone `armour` roll, compositions, riders and the dismount, the ceiling weight, the sweep | a patrol with infantry appears and walks a road |
| V6 | waves and bosses: the site file entry, the boss tag, the stage on death; the drops | the gate fight with a tank |

Two to three days for V1–V6 on the local server, with a test file per step in the usual way. V1 is an hour and
answers the two questions that decide the rest: whether the vehicle drives on inputs with no player aboard, and
what a grenade is worth after the modifier list. If a vehicle refuses to move without a player in the seat, the
crew mob becomes the passenger the mod checks for (it is `Entity`, the seat takes any entity) and the inputs are
written under its name; if the movement code demands a `Player`, the fallback is to move the vehicle ourselves
(`setDeltaMovement` along the path with the mod's terrain and collision helpers, which are public) — slower to get
right, still no new model.

## 8. Risks

- **The driver check.** The vehicle's tick reads the first passenger in a few places (the HUD, the camera, the
  seat swap). If one of them gates `travel`, V2 finds it on day one and takes the fallback above.
- **Pathing.** A vehicle is a 4 × 3 box that does not jump; the mob navigator plans for a 0.6 body. The drive goal
  plans wide (a custom `PathNavigation` with a large node width is the proper fix if roads alone do not keep it
  out of trouble) and the road preference is the cheap fix. Off-road stuck vehicles are the likely first bug.
- **Cost.** A vehicle ticks its own physics and GeckoLib animation whether or not anyone drives it; ten of them are
  not ten fighters. The ceiling weight of four and the one-per-400-blocks rule keep it to one or two in a player's
  world at a time.
- **Friendly fire.** The 30 mm and the tank gun hit whatever is in the line; the fight goal holds fire when a
  faction ally or a rider is inside the cone, the way the Soldier's `hurt` refuses allied rounds — but blasts
  through `custom_explosion` do not check sides, so an APC firing HE into its own dismounted squad is a real case
  to test in V3.
- **Superb Warfare updates.** The crew touches the vehicle only through public setters, synced data and one
  method, all by reflection the way the grenade does, so a jar update breaks the crew, not the server.

## 9. V1 results (2026-09-12, local server)

Probe: `/gscraft vehicle status|fuel|input|drive|target|hit` (`armour/VehicleCommands`, on `armour/Vehicles`, all by
reflection), test `tools/war_phase16.py`, override `tools/armour_override.py`.

**The driver question.** A vehicle with nobody aboard does not move on the forward input, whatever its energy and
however healthy its parts: `travel()` runs every tick, but the engine's power follows the passengers. With any
`Mob` mounted in seat 0 (`/ride` in the test) the same T-90A drives 30 blocks in 80 ticks at a sprint and coasts on
after. The AI turret is gated the same way, on the seat: `baseTick` lays the turret by `AI_TURRET_TARGET_UUID` only
when the entity in the turret controller's seat is a `Mob` (a `Player` there gets manual control); with the mob
aboard the target field takes and the turret turned 22 degrees in three seconds. The fire input with the mob aboard
hurt the target (2000 → 1979 in three seconds - the coaxial MG; the cannon needs the weapon selected). So the crew
of §2 is the passenger the mod checks for, not a fallback: V2 mounts the crew mob in seat 0 and writes the inputs.

**Spawning.** `/summon` with no NBT arrives with the parts at a tenth (turret 10 of 100, engine 15 of 150) and the
damaged flags set - the save-data read of an empty tag. Spawn with `TurretHealth:100f,MainEngineHealth:150f,
LeftWheelHealth:100f,RightWheelHealth:100f` and the four `*Damaged:0b`, plus `Energy`, or set them after; the T-90A's
maxima are 100 / 100 / 150 (`getTurretMaxHealth` and kin, per vehicle class). `Energy` is the fuel: 10 000 000 on
the T-90A, and the drive above cost 6 272 of it.

**The hit gate.** `hurt` refuses a source with no attacker (the friendly check against the last driver reads it as
friendly), so `/damage` from the console says "invulnerable"; the probe's `hit` names an attacker.

**The damage table** (the mod's own lists; what a hit of that amount takes off the vehicle):

| source (amount) | BMP-2 | T-90A |
|---|---|---|
| `tacz:bullet` 6.5 (5.56) | 0 | 0 |
| `tacz:bullet` 42 (.308) | 0.5 | 0 |
| `tacz:bullet_ignore_armor` 42 | 3.5 | 0.5 |
| `superbwarfare:custom_explosion` 120 (hand grenade) | 36.6 | 9.2 |
| `superbwarfare:projectile_explosion` 200 (rocket) | 63.9 | 16.6 |
| `minecraft:explosion` 100 | 89.2 | 22.7 |
| `superbwarfare:mine` 300 | 34.3 | 19.9 |
| `superbwarfare:projectile_hit` 65 (30 mm) | 12.0 | 8.3 |

Against 300 and 500 health: a BMP-2 dies to eight grenades or five rockets, a T-90A to fifty-four grenades or
thirty rockets. The override (`#tacz:bullets 0` in front of each list, world datapack `gscraft_armour`, `/reload`)
makes every TACZ round exactly 0 on both, confirmed live. The explosive multipliers are the mod's until the §5
table is settled; they go into `armour_override.py`'s CHANGES.

## 10. V2 results (2026-09-12, local server)

`gscraft:crew` (`armour/Crew`): an invisible, silent, invulnerable, unpickable `Mob` of `MobCategory.MISC` with a
synced faction, a looped route (NBT) and one goal, `armour/DriveGoal`. It sits in seat 0 and discards itself two
seconds after its vehicle is gone or a wreck. `armour/Armour.spawn` places a vehicle whole (`Vehicles.whole`: every
part at its maximum, no damaged flag, full health) and fuelled, and mounts the crew; `/gscraft vehicle spawn <type>
<faction> [pos]`, `crew <vehicle> <faction>`, `route <vehicle> add <x> <z> | clear | show`. Steering (V1 probe): the
left input turns the hull left about two degrees a tick, driving or standing, so the drive goal is heading error →
steer, forward while the waypoint is ahead, sprint when far and lined up, a reverse-and-turn after two seconds
without movement, the waypoint skipped after three of those. Test `tools/war_phase17.py`: a BMP-2 with a four-corner
80 x 40 route drove the loop in 22 s on the flat, no waypoint given up. The crew shows in `/gscraft fighter`-style
readouts as a faction member, so fighters and players target it (and so shoot the immune hull - V3's business).

## 11. V3 results (2026-09-12, local server)

**The mod has the gunner already.** `baseTick` walks the seats: an entity that is a `Mob` with a mob target, whose
seat has a weapon with ammunition, is turned to look at its target and, once the barrel is within four degrees of
it, `vehicleShoot` fires at the weapon's own rate. The commander's station does the same for its seat. So the crew
never fires anything: `armour/FightGoal` picks the target (nearest hostile within `armour.engage` with a line from
the turret), gives it to the mod as the turret's or the station's aim target and as the crew's own mob target,
halts the hull (the driver), picks the weapon (a missile for armour where the seat has one, else the cannon) and the
mod does the rest. A tank with a commander's station gets two crews: the driver in seat 0 and a gunner in the
station's seat, each with its own target.

**Ammunition.** An empty vehicle fires nothing: `canShoot` reads the vehicle's own 54-slot inventory. `Armour.arm`
loads it at spawn (`/gscraft vehicle arm` for one already there): tanks 64 HE and 16 AP large shells, rifle and
heavy rounds for the two machine guns; IFVs 128 HE and 64 AP small shells, 8 anti-ground missiles, rifle rounds.
HE first in the slots, so the gun fires HE at infantry.

**The hold.** An ally within `armour.friendly_radius` of the line of fire and short of the target clears both the
mob target and the aim target (the laid turret fires by itself at its aim target); with them cleared the target's
health stayed flat for six seconds with the ally in the line. A halted hull coasts for a couple of seconds, so a
hold declared while it coasts can release as the line moves - real, and right.

**The retreat.** Below `armour.retreat_share` of health, or with the turret gone, the driver drives away from the
last target at a sprint for `armour.retreat_ticks` and does not fight for `armour.calm_ticks` after; an engine that
is gone means it sits and fights. A 900 explosion took a T-90A to 165 and it drove from 30 to 68 blocks off in ten
seconds. A 1 800 explosion is a kill (the list is not linear: 100 → 23, 900 → 335, 1 800 → 712).

**Both gun mods.** The override now zeroes `#tacz:bullets` and the four Superb Warfare gunfire types (plain,
headshot, and the two armour-piercing "absolute" ones). TACZ's explosive rounds explode as `minecraft:explosion`
(`ExplodeUtil` passes no damage source), so a 40 mm or an RPG-7 keeps its ×2 on the tanks and ×6 on the IFVs;
Superb Warfare's grenades, rockets and mines have their own types and keep theirs. Confirmed by `tools/war_phase18.py`
part 5 on a live T-90A: five gun types 0.0, three blast types 9 to 23.

**Test traps.** `/fill` refuses more than 32 768 blocks and a script never sees it: three vehicle arenas left a
two-block stone slab that the tank drove onto and that blocked the sight line. `localtest.fill` slices every fill.

## 12. Detection, priority and distances (owner, 2026-09-12)

- **Acquire time** `armour.acquire_ticks` (40): a threat must stay in sight that long before the crew engages; a
  target the other crew of the same vehicle already engages is taken at once.
- **Cones** `armour.view_cone_driver` (120°) and `armour.view_cone_gunner` (200°) about the hull's heading: what
  lies outside is not seen. A hit on the vehicle (`armour.alert_ticks`, 20 s) opens the cone all round. This is why
  armour goes out with infantry (V5).
- **Sight rechecked** every half second while engaged; out of sight for `armour.lost_ticks` and the target is
  dropped. Every `armour.retarget_ticks` a better target in view replaces the current one.
- **Priority**: enemy armour 3, players 2, gunners and marksmen 1.5, the rest 1, plus up to 0.4 for nearness.
- **Distances**: `armour.engage` is 96 now. The mod registers its vehicles with a 512-chunk tracking range, so a
  client is sent a tank as far as the server's view distance loads chunks (10 chunks, 160 blocks, locally and on
  live); the vehicle renders out to about 250 blocks by its size. So the view distance is the one cap on seeing a
  tank early, and raising it is a server-wide cost; nothing on the mod side limits it.

## 13. V4 results (2026-09-12, local server)

Owner: no hit numbers, only a module that breaks; no "rifle fire does nothing". `armour/Reports`, from the driver's
tick: the turret, the engine, a track (the mod's damaged flags flipping), the withdrawal, the destruction with the
killer's name (the vehicle's own last attacker; an overkill removes the vehicle in the same tick before any wreck
flag, so the crew's loss of its vehicle is the report then), and the first contact - "[T-90A MBT] Engine noise to the
north" - to a player inside `armour.contact_range` of a crewed vehicle, once per player and vehicle per five minutes.
Lines reach players inside `armour.earshot`. The bar (`ServerBossEvent`, notched) shows while a crew is engaged:
the vehicle's name and the module letters T E L R, dimmed when gone, health as the fill. `tools/war_phase19.py`.

## 14. V5 results (2026-09-12, local server)

The zone file carries `armour` (`tools/war_zones.py`: the fronts and outposts each side, the plant, the town and
the far bank at 4-6 % a pass, the open roads a 3 % mix; compositions an APC with four infantry, a tank alone, a
tank and an APC with four, two APCs with six). `armour/Patrols.roll` runs in every director pass for every player:
open ground, the zone's chance, no other armour within `armour.spacing` (400), the ceilings with a vehicle at
`armour.weight` (4), then a road stand in the ring `armour.place_min`..`place_max` (96..140) from the player - a
column whose block below is one of the road mod's surfaces (they are not full cubes, so the general standing test
refuses them: the road stand has its own), with a 5 x 4 x 5 hull's room over it, found by scanning a small square
round each ring point since a point seldom lands on a road - and never within the minimum of anyone. The route
is the zone's patrol where it has one, else the road followed both ways up to 60 blocks (`roadRoute`); a stub
under 24 long means it sits. The infantry is placed beside the lead vehicle, formed as a squad and listed on the
driver as its escort: every two seconds the driver orders them to a point `armour.escort_behind` behind a moving
hull and frees them when it halts to fight; the hull never sprints with infantry and waits when the slowest is
more than `armour.escort_wait` behind. A crew swept by the director takes its vehicle with it (a wreck stays);
the vehicle's driver counts as four against the ceilings. `/gscraft director armour <x> <y> <z> <vehicle>
<infantry>` forces a placement within 40 of a point; `tools/war_phase20.py` on a laid road strip.

Not yet: riders in the APC's bay and the dismount (the infantry walks behind instead), the road preference in
the drive (routes are roads, so the hull stays on them by construction), the convoy.

## 15. V6 results (2026-09-12, local server)

A wave entry naming a vehicle (`{"entity": "superbwarfare:bradley", "count": 1}`) is armour in the wave:
`Loop.sendWave` hands it to `Armour.wave`, which stands it beside the wave point (a road stand where there is one,
else any stand with a hull's room), crewed and armed, tagged like the wave (so the sweep leaves it and the wave's
end takes it), and drives it for the wave's target - the site's anchor for an assault, the camp square for the
counterattack. A route of one point is a destination: no sprint inside forty blocks, coasting the last twelve (a
hull at a sprint rolls twenty past), and it holds where it stops. The three NATO sites carry a Bradley in their
last assault wave and an M1A2 with a Bradley in their last counterattack wave (the hospital is the Dead's: none).
A **boss** is a wave entry with `"boss": "<stage>"` and a `"name"`: named over the hull, it holds where it is
placed, its bar shows to players within earshot, and its destruction sets the stage `<site>_<stage>`
(`Stages.add`, so the quest book reads it). `/gscraft director wave <x> <y> <z> <tx> <tz> <vehicle> <boss|none>`
places one for the site `test`; `tools/war_phase21.py`. Left of §6: the wreck's loot entries.

Trap found: on alternate ticks the goal selector ticks a running goal before re-checking it, so a goal that
empties its own state must guard its tick (the drive goal crashed the server once on a cleared route).

## 16. Riders and loot (2026-09-12, local server)

**Riders.** A patrol's infantry boards the vehicle's bay a second and a half after placement (`Crew.board` on
tick 30: a mount in the vehicle's first tick, before its seats are set up, displaces the crew) and rides without AI
- hidden, and the BMP-2's firing-port seats silent - while the drive waits for the boarding and then goes at a
sprint, since nobody is walking. When the driver halts to fight (`FightGoal.start`) the riders dismount
(`Crew.dismount`): out beside the hull, alternating sides, AI back, the crew's target as theirs, and
"[BMP-2] Infantry dismounting" to the players. An escort beside a moving hull climbs back in (`escortTick`). The
BMP-2 and Bradley carry six; a tank has no bay. RCON truncates a vehicle's passenger NBT: the status line carries
`passengers N, riders M` instead.

**Loot.** `gscraft_drops/armour.json` keys the four vehicles: their shells, rifle and heavy rounds, missiles for the
IFVs, iron as scrap. `Drops.spawn` drops them at the wreck (the wreck flag, or the crew's loss of the vehicle on an
overkill), invulnerable so the wreck's own blast does not eat them. A boss's quest item is the quest's to add.

**The convoy** stays out of scope, as §3 said; the road graph the census tool wrote (`incoming/census/roadnet/
roadnet.json`: 17 255 nodes, 28 586 edges, a noisy skeleton) is what a convoy route would be planned on.

## 17. The damage pass and the bail-out (owner's play-test, 2026-09-12)

The owner's findings on the first play-test: rockets did too little to a BMP-2, the TACZ rocket cratered the ground,
the bar showed health after "destroying" a vehicle, and a disabled vehicle should lose its crew.

**Why rockets did too little.** Superb Warfare's own lists take 13 off every hit, then a fifth of the rest, then the
type multipliers; an RPG round (450 direct, `projectile_hit` x1.35) left a BMP-2 at two thirds. Worse, TACZ explosive
rounds are a vanilla explosion whose damage falls with the distance from the blast to the entity's *feet*: a rocket into
the side of a hull, three blocks from its centre, did a fifth of its blast (and the round's own bullet damage is a
TACZ bullet type, which the list makes nothing).

**The lists (`tools/armour_override.py`).** Replaced whole, by weight: LIGHT (BMP-2, Bradley, 300 health) and HEAVY
(T-90A, M1A2, 500). Immunities first (both gun mods' bullets, arrows, melee, fire, fall), then a plain multiplier per
source, applied in order. Final shares of the raw damage - light: `projectile_hit` 0.35 (an SW RPG 160, a Javelin
230-330, a tank shell 245, an ATGM 210), explosions 0.4 (a hand grenade 50, C4 180 with `@c4 * 1.5`, a mortar round
100), a 30 mm AP round 11 (`@small_cannon_shell * 0.5`), TNT x2, a ram x2.5; heavy: `projectile_hit` 0.28 (an RPG
125, a shell 195), explosions 0.25, `@javelin_missile * 1.3` (a top attack ~300: two Javelins kill a tank), 30 mm AP
4, C4 300 (`@c4 * 4`). The mod's own code then scales by the angle of the hit (0.85 from the front on the BMP), which
is why phase 22 reads 134 for a 160 hit. `minecraft:player_explosion` is left alone on purpose - see next.

**TACZ explosives (`armour/ArmourDamage.java`).** A direct hit on a vehicle by an explosive round does a flat amount
by the round's class and the vehicle's weight, sent in as a player explosion by the shooter (so the list, the angle and
the last-attacker record see it): rocket (a blast of 100 or more: the RPG-7) 160 light / 130 heavy; grenade (a blast
radius of four or more: the M320) 60 / 20; other (HE rifle rounds) 30 / 8. The blast that follows adds nothing to a
vehicle it hit directly; a blast that only lands beside a vehicle does the splash share (0.5). The vehicle is removed
from the explosion's own entity list either way. Settings `armour.rocket_*`, `grenade_*`, `blast_*`, `splash`,
`heavy_health`.

**Griefing.** TACZ's `ExplosiveAmmoDestroysBlock` is now false in the server's `tacz-common.toml` (the mod's rocket
file also asks to destroy; the config wins). Superb Warfare's `explosion_destroy` was already false.

**The bar and the burn.** A Superb Warfare vehicle under its self-hurt share bleeds health every tick until the wreck
(then on to minus its maximum, when the wreck goes). That was the "health winding down from fire" - not destroyed yet.
Now a vehicle that is *disabled* - burning (under a tenth of health, or the mod's share where higher) or with engine
and turret both gone - loses its crew (`Crew.disabled/bail`): a crewman per crew seat climbs out beside the hull, a
faction soldier in the crewman's kit (`NATO Crewman` / `RUAF Crewman`: trousers, a Glock 17, no armour; weight 0 so
the director never rolls one), on the crew's last target; the riders dismount with them; the seat empties; "Crew
bailing out" is told within earshot and the bar drops. The driver crew stays by the hull unseen (`bailed`, watching
the vehicle by id) only to report the wreck and drop the loot, and gives up after `armour.bail_watch_ticks` (2400).

**Placing anywhere.** `/gscraft director armour <x y z> <vehicle> <infantry>` takes a block position (`~ ~ ~`) and
places at that point: on a road it patrols the road, on open ground it holds (`Patrols.placeAt`). The old form
wanted a road stand 96 blocks from every player, so it never worked from where a player stood.

**Results (`tools/war_phase22.py`, 5/5).** Light: 300 -> 166 on a 450 `projectile_hit` (134: 157 x the front angle),
nothing on a TACZ bullet type. Heavy: 500 -> 412. A BMP-2 hit to 11 health: one crewman with a Glock and no helmet,
rank "NATO Crewman", the seat empty, "bails out" logged; the finishing blast still logged "destroyed" and dropped
loot. Phases 16, 20 (the off-road placement check updated), 21 rerun green.

**Tooling.** Superb Warfare is Kotlin; ForgeFlower crashes on it and Vineflower refuses some classes. CFR
(`G:/GSCraft/tooling/cfr-0.152.jar`) decompiles them all; Vineflower (`vineflower-1.10.1.jar`) is there for the rest.

## 18. The cannon only, chat off, the explosive pass (owner's second play-test, 2026-09-12)

**APCs not engaging each other.** They were: both crews logged the engagement and laid their turrets. They did not
fire because `chooseWeapon` picked the APC's missile for an armour target, and the missile has a magazine of one. The
mod's reload lives in the gun data and is started for a player (the reload key, or the empty-magazine reload on the
player's tick); a mob in the seat never starts one, so `canShoot` stayed false after the first missile and the crew sat
laid on its target for good. The crew now always uses the seat's first weapon, the cannon, which feeds straight from
the container (`superbwarfare:small_shell_ap/he`; the tanks' `large_shell_*`). Phase 23: a RUAF BMP-2 and a NATO
Bradley placed 50 blocks apart facing each other wreck each other inside 30 s, the cannon selected throughout.

**Chat.** All the armour chat lines are off by default (`armour.chat 0`): contact, module hits, dismount,
withdrawing, bail, destroyed. They still go to the log at the same points; the boss bar is not chat and stays.

**The explosive pass.** There is no "immersive explosions" mod in the pack (the immersive-named mods are Vehicles,
Engineering and Weathering), so this went at the blasts themselves, whose radii in Superb Warfare's data run 5 to 16
blocks against TNT's 4. `tools/armour_override.py` tames every `ExplosionRadius` and `ExplosionDamage` it copies out
of the jar: a radius over 3 keeps 40% of the excess (5 -> 3.8, 8 -> 5, 10 -> 5.8, 16 -> 8.2), a blast damage over 60
keeps 60% of the excess (120 -> 96, 160 -> 120). That covers the four vehicles' weapons (the tank HE shell 10 -> 5.8,
the ATGM 8 -> 5) and wreck blasts (the tanks 16 -> 8.2, the APCs 8 -> 5), and every gun file whose rounds carry a
blast (the RPG's thermobaric round 11 -> 6.2, the standard 5 -> 3.8, the Javelin 9 -> 5.4, the M79 5 -> 3.8, the
grenade launcher). The same two formulas go over the `[explosion]` section of the server's
`superbwarfare-server.toml` (the hand grenades 5/6 -> 3.8/4.2, the mortar 9 -> 5.4, C4 10 -> 5.8, the drone's RPG
10 -> 5.8, the aircraft bombs 11 -> 6.2), which the mod reads at start. Direct-hit damage is untouched, and the
armour lists of §17 work on the direct hit, so a rocket still does what §17 says to a vehicle; only the blast around
it shrinks. TACZ's own rounds (the RPG-7's blast radius 3, the M320's 6) are in the gun pack and left alone.

**Results.** Phase 23 (3/3), phase 22 (5/5) and phase 20 (6/6) rerun green. The tests now remove wrecks by setting
their health under minus the maximum: a wreck ignores `/kill` and would otherwise burn down for a minute, and a
lingering one answered the next test's `limit=1` selector.

## 19. The blasts' look (owner, 2026-09-12: "visually the explosions are very strong")

**Where the look comes from.** Superb Warfare picks a blast's particle show from its radius, not from the weapon:
a projectile's own blast (`FastThrowableProjectile.explosionParticleType`) is mini under 2, small from 2 to 4, medium
from 4 to 7, large from 7 up; the shared routine grenades and shells use (`ProjectileTool.causeCustomExplode`) is small
under 4, medium from 4 to 10, huge from 10 to 16, giant beyond. Huge and giant also shake every screen within 192 and
384 blocks. Each blast further sends its own screen shake sized by its radius (4x the radius wide, amplitude 50 plus
half the radius), which the client scales by `explosion_screen_shake`.

**What the passes do.** The radius pass of §18 already moves most blasts down a band: the RPG's standard round from
medium to small, its thermobaric round, the Javelin, C4, the mortar and the tank's HE shell from large/huge to
medium. The vehicles' wreck blasts are data (`DestroyInfo.ParticleType`: the APCs "Huge", the tanks "Giant") and the
override datapack now writes them "Large", the biggest show without the 200-400 block shake. The client's
`superbwarfare-client.toml` gets `explosion_screen_shake = 40` (of 100), set in both Prism instances and shipped with
the pack (`CLIENT_CONFIG_EXTRA` in `tools/packwiz_build.py`, so a player's own later change is kept).

**The tamer is idempotent now.** The first version scaled whatever value it found, so a second run shrank the server
config again (RPG 10 -> 5.8 -> 4.1). It now computes from the pack's pre-pass values (the
`superbwarfare-server.toml.bak-explosion` backup an earlier session left; the AH-6 cannon's 4 is the one deliberate
pack value there) or, failing that, the mod's `# Default:` comment above each value, and a rerun changes nothing.

**Applied locally.** The override datapack reinstalled and reloaded; the server config holds the intended numbers
(the same ones the running server started with). TACZ's vanilla-style blasts are unchanged.
