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
