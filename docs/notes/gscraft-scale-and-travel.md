
# Scale and travel: how big the map should be (2026-09-03)

Design review requested by the owner: look at the gameplay as designed, then reconsider the map size
against player speed, distance, and the fact that the pack has vehicles.

## 1. The gameplay as designed (blueprint + phase log)

- **Loop:** scavenge the city (Lost Cities loot, Lootr-instanced) → take a garrisoned location → a
  clock starts to fortify it → each cycle the game draws ONE held location, warns ahead (blood-moon
  style), and attacks it → lose or die and retake it, win and it stays held → every location drops
  radio-tower loot → tower repaired → countdown → wave defence at the players' own base → boss →
  season increments.
- **Pacing already in config:** a Minecraft day is 20 real minutes (night about 7). The Hordes event
  fires every 10 days (every 200 real minutes), lasts 5 minutes, 8 mobs a wave, and grows 5% a time.
  Eyes in the Darkness cycles 600/300 ticks, max 1. Horror is a layer, not the threat.
- **Population:** five players. One site attacked per cycle. Never "hold all five".
- **Map today:** spawn at 19 94 26 in the crater (starting area 384×384). Player district at blocks
  896…3103 × 384…2079, its west edge ~900 m east of spawn. Five pads in the ring: substation 1.5 km
  S, radio tower 2.1 km E, hospital 2.5 km SE, water treatment 3.6 km E, airfield 3.9 km SE.
  Farthest pad-to-pad leg: water treatment ↔ substation, ~3.4 km. Only the district rectangles and the
  pads (+8 chunks) are pre-generated; everything else is generated when a player arrives.
- **Generator:** Lost Cities `wasteland` profile, cityChance 0.01, city radius 50–128 blocks,
  buildings 0–8 floors, rubble layer on, explosions in cities only. Cities are scattered islands of
  ruin in open wasteland, not a continuous city. The overview render also shows a lot of open WATER
  around the district and the southern pads: the seed is wet.
- **View distance** is 10 chunks (160 m). Nothing is "visible from home": the radio mast, the pads, and
  the district are all beyond render range from the crater. Navigation is Xaero's map and waypoints.

## 2. Speeds

Vanilla numbers are exact. Vehicle numbers are the ranges the Immersive Vehicles official packs are
known for and MUST be measured on the visual pass (three vehicle classes, on a Lost Cities street, on
open wasteland, and across the rubble layer) before any timer is set from them.

| Mode | m/s | km/h | Note |
|---|---|---|---|
| Walk | 4.3 | 15.5 | |
| Sprint | 5.6 | 20 | hunger-limited |
| Sprint-jump | ~7.1 | ~26 | what players actually do |
| Horse (typical) | ~9 | ~32 | max 14.5; useless in rubble |
| Boat / minecart | 8 | 29 | water is plentiful here; rails are LC's own |
| Car, on a street | 17–33 (assume 20) | 60–120 | official automobile pack, to measure |
| Car, over rubble/wasteland | ~5–8 (assume 8) | ~20–30 | 1-block steps and craters; may be no faster than a horse |
| Truck / APC | ~14 | ~50 | cargo is the point, not speed |
| Aircraft | 40–80 (assume 55) | 150–300 | needs a runway = the airfield tier |

## 3. Travel time (minutes, one way)

| Distance | Walk | Sprint | Horse | Car street | Car rubble | Aircraft |
|---|---|---|---|---|---|---|
| 0.5 km | 1.9 | 1.5 | 0.9 | 0.4 | 1.0 | 0.2 |
| 1 km | 3.9 | 3.0 | 1.9 | 0.8 | 2.1 | 0.3 |
| 2 km | 7.7 | 5.9 | 3.7 | 1.7 | 4.2 | 0.6 |
| 3 km | 11.6 | 8.9 | 5.6 | 2.5 | 6.3 | 0.9 |
| 4 km | 15.4 | 11.9 | 7.4 | 3.3 | 8.3 | 1.2 |

Read against the clock: one in-game day is 20 minutes. On foot, the airfield (3.9 km) is a whole
day's round trip; by car on a road it is a seven-minute errand; by air it is ninety seconds. **A map
that is right for walking is trivial for cars and pointless for aircraft.** So the map cannot be sized
for one mode; the modes have to be tiered, and the border has to grow with the tier.

## 4. What distance is for, in this design

Distance is the only cost the engine gives us reliably (the blueprint's own argument), and it has three
jobs:

1. **Make vehicles matter.** A pad within 1.5 km is walkable (six minutes) and no one builds a garage
   for it. A pad at 3–4 km is a car trip, and a car trip means fuel, which means the water plant and the
   biodiesel chain. The garage tier only has a reason to exist if two or three targets sit past
   walking range.
2. **Make the warning a decision.** When the game names the next site under attack, the warning
   length should be about the FOOT travel time to the farthest held site (12–15 minutes for today's
   ring), so that without a vehicle a far site is a genuine "go or abandon", and with one it is
   comfortable. That is the lever that turns the garage into a strategic upgrade rather than a
   convenience. Set it in the state machine as a function of distance from the marked home, not a
   constant.
3. **Keep attacks local.** Sites must be far enough apart (≥500 m) that an attack on one does not spill
   into another, and far enough from home (≥1 km) that the finale at the base is a different fight.

## 5. The reconsidered size

**Superseded the same day.** The owner ruled out seasonal border growth: everything with a plan goes into
this build, seasons are a future idea. Re-analysed on that basis in `docs/gscraft-map-design.md`: a
**10 km square border centred (1900, 1250)**, one map with three ranges (foot 0–1.5 km, road 1.5–4 km,
air 4.5–6.5 km), only foot- and road-range sites holdable, the air ring expedition-only and the home of
the rare material tier. ~390,000 chunks, ~2.4 h of Chunky, ~6 GB. The 5 km box (no air ring) and the
4.2 km disc are both withdrawn. Sections 2–4 and 6–8 of this note still hold and feed that document.

## 6. What the map needs for vehicles to work at all

*Superseded 2026-09-04 where it names pads or a tower road: the roads as built are `gscraft-map-layout-v6.md` §4.*

- **Roads.** Cars are only cars on a surface. Build a spine with the terrain tools: crater → district
  west edge (900 m), and district → the two nearest pads (substation, radio tower). Lost Cities' own
  streets carry traffic inside cities; between them it is rubble and water. The two old rail causeways
  west of the district (chunks x 40–135, z ~36/44) are candidate roadbeds.
- **Water.** The render shows the substation pad in water and open water south and east of the
  district. Every road crossing needs a causeway (terrain `pad`/`ramp`), or the pad moves. Check
  water depth at each crossing on the visual pass. Boats are a legitimate second vehicle class here,
  and cheap.
- **The crater.** Home is in a pit. The v5 ramps exist; confirm a car can drive out of it, or the
  garage sits on the rim.
- **Chunk loading.** A car at 20 m/s crosses a chunk every 0.8 s; with simulation distance 6 the
  server keeps up only over pre-generated ground. Another reason to pre-gen the whole box.

## 7. Pads: distance is tier, with one exception

**Superseded (draft 3 of the map design):** the four custom compounds are dropped; the pads become landing zones for foreign transplants (Novo Expograd on the substation pad, Financial Plaza on the hospital pad, Bio Gen on the airfield pad), the radio tower stays. Distance still orders the tiers: 1.5 km → 2.4 → 2.5 → 3.9.

## 8. Timers to set from this (for the KubeJS loop)

*Superseded 2026-09-04: design draft 6 has no random attack cycle - only the contested site is attacked; the warning is a flat 10 minutes (gap audit B5).*

- Fortify clock after taking a site: 2 in-game days (40 min).
- Attack warning: max(10 min, foot travel time from home to the target) — 12–15 min for the ring.
- Attack cycle: every 5 in-game days; Hordes stays at 10 days as the background threat, or is folded
  into the loop so there is one calendar, not two.
- Finale countdown after the tower: 3 in-game days; waves at the base.

Related: [[gscraft-phase-log]] (pads, ramps, pregen numbers), [[gscraft-player-builds]],
the blueprint page (endgame loop, base upgrades, map plans).
