# A damage model of our own: limbs, heads, plates — feasibility (2026-09-11)

Owner's brief: time to kill and balance are off, and vanilla health leaves too few levers. Research limb and
head damage modifiers, armoured enemies absorbing more shots in the chest, and a separate health system for
enemies (simple) and players (fuller) — and say how it works with the guns we have and with explosives.

Everything below was read from the jars in the pack (TACZ 1.1.8, Superb Warfare 0.8.9, PlayerRevive 2.0.31),
the gun pack data on the server, and measured on the local server.

## 1. Why it feels off: the numbers as they are

Every bullet in the pack ends in vanilla's `LivingEntity.hurt`, and vanilla armour is what decides the damage.
The fighters wear a lot of it.

| body | armour / toughness | health | chest item |
|---|---|---|---|
| NATO and RUAF ranks | 17 / 12 | 24 | SW IOTV or 6B43 (SW "cemented carbide", the vests carry the toughness) |
| Scavenger | 12 / 6 | 20 | leather or a Pomkots wanderer chest |
| Scavenger Captain | 20 / 15 | 20 | DragonRise MSV chest |
| Scrapper | 4 / 0 | 20 | cardboard |
| player | whatever is worn | 20 | |

The vanilla formula: reduction = clamp(max(armour / 5, armour − damage / (2 + toughness / 4)), 0, 20) / 25.
At armour 17 and toughness 12 a 6.5-damage 5.56 round loses 63 % of itself. TACZ splits each bullet into an
armour-ignoring part (`armor_ignore`, 20–60 % by gun) and a normal part, and multiplies the base by
`head_shot_multiplier` (1.33–2.0) when the hit lands in the head box. For an entity with no configured box the
head box is a half-block slab centred on the eyes.

Shots to kill today, body / head (computed with the formula above, gun data from `tacz_default_gun`):

| gun (damage, armour ignore, head ×) | NATO / RUAF | Scavenger | Captain | Scrapper | no armour |
|---|---|---|---|---|---|
| Glock 9 mm (6, 0 %, 1.5) | 11 / 7 | 6 / 4 | 14 / 9 | 4 / 3 | 4 / 3 |
| M4A1 5.56 (6.5, 20 %, 1.5) | 8 / 5 | 5 / 3 | 8 / 6 | 4 / 3 | 4 / 3 |
| AK-47 7.62×39 (9, 25 %, 1.5) | 6 / 4 | 4 / 3 | 6 / 4 | 3 / 2 | 3 / 2 |
| Mk14 .308 (16, 50 %, 1.75) | 3 / 2 | 2 / 1 | 2 / 2 | 2 / 1 | 2 / 1 |
| AWP .338 (42, 60 %, 2.0) | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |

What the table says:

- A head shot on a soldier is worth one and a half body shots. The half-block head box and the multiplier get
  swallowed by armour, so aiming barely matters below .308.
- A Scavenger in leather takes five 5.56 rounds; a Scrapper in cardboard four. Leather is 40 % of a plate carrier.
- Nothing distinguishes the chest from the legs from the arms. Nothing wears out.
- The only levers are health, armour, toughness, per-gun damage, armour-ignore and one head multiplier, and they
  all pull the same rope: a bigger number everywhere.

## 2. What the pipeline gives us to hook

**TACZ** posts `EntityHurtByGunEvent.Pre` on the server before it calls `hurt`, with the bullet entity, the
target, the attacker, the gun id, the base amount, the two damage sources (normal and armour-piercing), the
head-shot flag and its multiplier — and every one of those has a setter. We can replace the amount, swap both
sources for the piercing one (which is how vanilla armour is switched off for a hit), and clear the head flag.
The bullet's position at that moment is the start of its step, not the impact, and a bullet moves 12–28 blocks a
tick; but its velocity is on it, so the impact is the target's box clipped by the segment
`position → position + velocity`. That gives the impact point to the centimetre, and from it the zone (§3). The
per-entity head box (`HeadShotAABB` in `tacz-server.toml`) is a fallback we do not need once we judge zones
ourselves.

**Superb Warfare** bullets carry their own head and leg multipliers and an armour-bypass rate, do their own
distance falloff in `LivingHurtEvent`, and — for hits from an SW gun only — read an `ArmorPlate` value on the
target's chest item, spend it, and reduce the damage; the plate is a consumable item and the HUD already draws
it. SW explosions are `CustomExplosion` with a distance falloff and a config `explosion_penetration_ratio` (15 %
of the blast ignores armour); the grenades in the fighters' hands do 90–120 at radius 5–6 and the world config
already has `explosion_destroy = false`.

**Forge** posts `LivingHurtEvent` for everything (bullets, blasts, melee, fire) with the damage source, the
amount and a setter — the one place a rule can see every kind of harm together.

**PlayerRevive** already intercepts a player's death into a downed state (five minutes of bleeding, 10 bleed
health, revive by a friend). Whatever our model does to a player, the second life stays.

The bodies are ours: `Soldier` and `Scavenger` carry `FighterState`, saved with the entity, so a plate's
remaining points, a crippled leg or a broken arm live there with no new saved data.

## 3. The model

One rule set, in data, applied to fighters in full and to players with more effects. No second health bar:
vanilla health stays the pool, and the zones, the plates and the wounds decide how much of a hit reaches it.

**Zones**, from where the segment enters the box, as fractions of the entity's height and half-width:

| zone | where | multiplier | fighter effect | player effect |
|---|---|---|---|---|
| head | above the eyes − 0.2 | ×3.5 | dead unless the helmet's class stops the round | as fighter; PlayerRevive catches the death |
| thorax | 0.55 – 0.85 of height, inner 70 % of width | ×1.0 | the vest and its plate decide | as fighter |
| stomach | 0.4 – 0.55 | ×1.1 | bleeds (1 per 2 s for 10 s) | bleeds until bandaged; hunger drains |
| arms | thorax band, outer 30 % of width | ×0.6 | aim slowed (aim ticks ×2) for 20 s, cannot throw grenades | reload ×1.5 and weapon sway for 20 s (via a mob effect) |
| legs | below 0.4 | ×0.5 | drops to a crawl (prone, speed ×0.4) for 15 s, cannot sprint | slowness III, no sprint, until bandaged |

**Armour classes and plates.** Each helmet and vest in the pack gets a class 0–6 and plate points in a data
file (`gscraft_armor/*.json`); each ammunition gets a penetration class from its calibre. The comparison decides
what a hit through that piece does:

- penetration ≥ class: the round goes through, the target takes 85 % of the zone damage, the plate loses the
  round's base damage in points;
- penetration < class: the round is stopped, the target takes 30 % (blunt trauma), the plate loses the same
  points;
- plate at zero: the piece protects nothing until it is replaced. For players the points are Superb Warfare's own
  `ArmorPlate` NBT on the chest item, so their HUD shows it and their plate items refill it; for fighters the
  points sit in `FighterState`, and a dead fighter drops its vest with the points it had left.

Starting classes: 9 mm and buckshot 1, 5.45 / 5.56 / 7.62×39 3, .308 / .30-06 4, .338 5, .50 6; cardboard 0,
leather and wanderer 1, the German M35 and the Pomkots helmets 2, PASGT / 6B47 / FAST helmets 3, IOTV / 6B43 /
MSV 4. Plate points 40 on a carrier, 25 on a helmet, 10–15 on leather.

**Explosives and melee.** A blast has no zone; it is treated as a thorax hit at a fraction the vest's class sets
(class 4 keeps 60 %, class 1 keeps 90 %, plate points spent), plus suppression 1.0 (pinned) for anyone within
the radius and bleeding at the edge. TACZ's explosive rounds (40 mm) and SW's grenades and mines all arrive as
explosion damage in `LivingHurtEvent`, so one rule covers them. Melee (the Dead's bites, knives, the Shield's
club) is left to vanilla armour, which is what leather and vests are good at anyway.

**Where the rule runs.** `EntityHurtByGunEvent.Pre` for TACZ (zone from the clip, amount replaced, both sources
set to the piercing one so vanilla armour does not double-count); `LivingHurtEvent` for SW bullets (same clip,
their own projectile) and for blasts. The fighters' armour attribute is not touched — it still counts for melee.

## 4. What it does to the numbers

Shots to kill under the model, thorax / head / legs, with the classes above and today's damage values:

| gun | NATO / RUAF | Scavenger (leather) | Captain (MSV) | Scrapper | no armour |
|---|---|---|---|---|---|
| Glock 9 mm | 9 / 5 / 8 | 4 / 2 / 7 | 7 / 4 / 7 | 4 / 2 / 7 | 4 / 2 / 7 |
| M4A1 5.56 | 9 / 2 / 8 | 4 / 1 / 7 | 4 / 2 / 7 | 4 / 1 / 7 | 4 / 1 / 7 |
| AK-47 7.62×39 | 7 / 2 / 6 | 3 / 1 / 5 | 3 / 1 / 5 | 3 / 1 / 5 | 3 / 1 / 5 |
| Mk14 .308 | 2 / 1 / 3 | 2 / 1 / 3 | 2 / 1 / 3 | 2 / 1 / 3 | 2 / 1 / 3 |
| AWP .338 | 1 / 1 / 2 | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |

The shape is the point, not the exact figures: a plate carrier eats a magazine of 5.56 in the chest and the
seventh round breaks it; two rounds in the helmet or one in the face end it; a leg hit does not kill but takes
the fighter out of the fight; a Scavenger in leather dies to four rounds anywhere in the body; .308 is the
answer to armour. Every number is a setting (§6), so the owner tunes this at the table, not in a jar.

## 5. Enemy side simple, player side fuller

The enemy gets zones, plates and three wounds (bleed, slowed aim, crawl), all of which the fighter AI already
has words for (prone pose, aim ticks, suppression). The player gets the same zones and plates plus wounds that
persist until treated: bleeding (damage over time, hunger drain), a leg wound (no sprint, slowness) and an arm
wound (slow reload, sway), each a mob effect the mod adds so the HUD shows it, cleared by a bandage. The pack has
no bandage item — the crafting design lists bandages and poultices as quick crafts, but nothing provides the
item — so the mod adds one (and a tourniquet for legs), or the design's recipes stay on paper. Head hits keep
their lethality; PlayerRevive turns the death into a downed state as it does now.

Not proposed: a per-limb health pool with its own HUD (First Aid-style). It would be a third health system on
top of vanilla's and PlayerRevive's, its HUD fights with SW's, and the wounds above give the same decisions
(where was I hit, what do I fix first) for a tenth of the work.

## 6. Cost and order

| step | work | proves |
|---|---|---|
| A. zones | the clip, the zone table, `/gscraft fighter` shows the last hit's zone and damage; a test fires a pinned rifleman at a NoAI target set at heights that put the head, chest and legs in the line | the hit point is right |
| B. plates | armour data file, classes, points in `FighterState` and SW's NBT, the two events, vanilla armour bypassed for bullets | the table in §4 on the range |
| C. wounds | fighter crawl / slowed aim / bleed; player effects and the bandage item | the fight reads differently |
| D. blasts | the explosion rule, suppression on the blast | grenades against vests |
| E. settings | every multiplier, class and point value into `gscraft_settings` and `gscraft_armor` | tuning without a jar |

About two days for A–E with tests, on the local server. Nothing here touches TACZ or SW files, and the gun
packs' damage numbers stay as they are — the model sits on top of them, which is also why it keeps working
when a gun pack updates.

## 7. Risks

- The bullet's velocity at event time must be the step's velocity; if TACZ has already moved the bullet the clip
  needs the previous position (`xo, yo, zo`). Step A settles it in an hour on the range.
- SW's plate reduction runs for SW-gun hits in the same `LivingHurtEvent`; ours must run once, so SW's is left
  alone for SW guns and ours handles TACZ, or ours takes over both and SW's is neutered by keeping the event
  amount it expects. Decide in step B.
- Shotguns: TACZ's `damage` on the M870 is 36 per shell spread over pellets by `applyShotgunDamageSpread`; the
  zone rule sees each pellet, so buckshot to the chest of a plate is many small blunt hits — right by design.
- The Dead do not wear plates and keep vanilla health; the model applies to them only through zones (head ×3.5),
  which is the zombie rule everyone expects.

## 8. Built (2026-09-11, local only)

Steps A-E in one pass, `tools/war_phase12.py` 9 of 9 on the local server; the rest of the suite as regression.

- `combat/Ballistics.java`: the impact from the projectile's step (position -> position + velocity, then the
  previous position -> position, then a longer segment; the box's nearest point if nothing clips) and the zone
  from it. The arms are judged sideways to the line of fire, not radially - the first cut measured the impact's
  distance from the axis, and since an impact is always on the surface every chest hit read as an arm.
- `combat/ArmorData.java` (`gscraft_armor/pack.json`, a reload listener): 24 pieces with a class and plate points,
  21 calibres with a penetration class, a default of 3 for anything unlisted.
- `combat/Damage.java`: the rule. Plate points live on the worn item - the chest under Superb Warfare's own
  `ArmorPlate` key (a player's HUD shows it, their plate items refill it), the helmet under `GscraftPlate`; a piece
  never hit carries its full points. A body wearing any known piece is judged by the model alone for bullets;
  one wearing none keeps the zone multiplier and vanilla armour.
- `combat/DamageEvents.java`: TACZ's pre-hurt event (amount replaced, head flag cleared, both sources set to the
  piercing one for a modelled body); Superb Warfare bullets and blasts in `LivingHurtEvent` with the model's number
  applied in `LivingDamageEvent`, after vanilla armour and in its place.
- Wounds: `FighterState.crawlUntil / armUntil / bleedTicks` (saved); `Fighters.tickWounds` bleeds, slows (a
  transient −60 % speed modifier) and lays the body flat whether or not the gun goal is running; the gun goal
  doubles a wounded arm's aim and never sprints a crawler; the grenade goal sits out a wounded arm.
  `combat/PlayerWounds.java` keeps a player's in persistent data: slowness and no sprint, weakness, a point of
  bleeding every two seconds with hunger; death clears them. `gscraft:bandage` (paper + 2 string -> 2; two seconds
  held) clears them and heals four.
- Commands: `/gscraft zone <who> <from xyz> <to xyz>`, `/gscraft hit <who> <zone|blast> <damage> [pen]` (the rule
  applied, by magic damage so vanilla armour stays out of it), `/gscraft wound <who> leg|arm|bleed|clear`,
  `/gscraft armor <who>`; the fighter readout adds wounds and the last hit. 22 settings under `damage.*`.

Measured (phase 12): 5.56 into an IOTV leaves 1.95 and costs 7 points; .308 through it 13.6; the plate at 0 lets
the next round land in full; 5.56 through a PASGT 19.3, into a bare head 22.75; through leather 5.5; live AK fire
judged hit by hit with the zone in the readout; a leg wound is flat and slow, a bleed 3 points in six seconds; TNT
beside a vest 22.2 of 37 and the plate down 19, the fighter pinned.

Not exercised without a player: the player's wounds, the bandage, and Superb Warfare's plate HUD reading our
points - the first thing to look at in person. Melee is untouched. The Dead take the zone multiplier only.
