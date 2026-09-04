# GSCraft Wasteland — The Woods (wilderness zone), plan

Draft 1, 2026-09-04. Owner's ask: a Tarkov-style "Woods" — a large wilderness area with no city, a
few scattered structures, the focus of certain quests, and a deliberate contrast to the cityscape
everywhere else. This is the plan; it is built after the v7 pre-generation finishes (section 5).

## 1. What it is for

The rest of the map is ruin: Lost Cities on a fifth of the land, highways across all of it, the built
sites as landmarks inside it. The Woods is the opposite: forest, hills, water, silence, sightlines. It
changes how the game plays without a new mechanic - no streets to funnel through, no rooftops, no
loot on every corner, cover that is trees and folds in the ground, sound that carries. It is where the
horror layer works best (the Man From The Fog's houses, Eyes in the Darkness at night), where the
rifles matter (long sightlines, no walls), and where a trip means carrying what you find back out.

## 2. Where

Scored over the pre-generated box in 2 × 2 km windows for forest cover, generated city (to be
removed), water and snow, at 1.5–4.5 km from the camp and clear of every site:

| Window (blocks) | Forest | City now | Water | Snow | From camp | Verdict |
|---|---|---|---|---|---|---|
| **x 400…2400, z −3500…−1500** | **65 %** | 23 % | 5 % | 0 | 2.9 km NNE | **chosen** - densest forest, dry, no snow, north-north-east of Novo |
| x 650…2650, z −3500…−1500 | 64 % | 21 % | 7 % | 0 | 3.0 km | same forest, wetter east edge |
| x 400…2400, z −3250…−1250 | 63 % | 23 % | 6 % | 0 | 2.7 km | 250 m closer; touches the LC belt north of the district |
| x 2900…4900, z −3250…−1250 | 60 % | 18 % | 8 % | 0 | 4.5 km | far north-east; air-ring distance |

**The Woods = x 400…2400, z −3500…−1500**, centre (1400, −2500), 4 km². Its south edge is 1.6 km
north-north-east of Novo's pad; the rest of the map is south and east of it, so it is an end of the world, not a
thoroughfare. No kept generated site falls inside it (structure plan check).

## 3. What is in it

- **Terrain and biomes exactly as the seed makes them** — the regeneration keeps the generator and
  only removes Lost Cities (section 5), so the hills, rivers and forest are the ones already there.
- **No city, no highways, no railways, no scattered LC buildings.**
- **A sparse set of structures**, chosen from the census positions inside the rectangle so they sit
  where the generator would have put them: two Underground Bunkers, two Man-From-The-Fog houses, one
  pillager outpost as the bandit camp. Nothing else. (The structure plan's ring caps apply: this is road
  range, so nothing here counts against the ring's totals; the Woods has its own list.)
- **Custom sites, to build later with the camp tooling** (templates placed by function, like the camp
  ruins): a sawmill on the south edge, a ranger cabin on high ground, a downed aircraft (a dead
  Immersive Vehicles airframe, per the crafting draft's dead-vehicle dressing), a hunters' hide by
  water. These are the quest anchors below.
- **One road**: a spur from Novo's north gate (1064, 88) to the Woods' south edge near (1400, −1500),
  ending at the sawmill; inside the Woods, tracks only (the road tool at width 3, gravel).
- **Spawning**: In Control! rules for the rectangle - fewer zombies, more animals, the fog man and the
  eyes at night; bandits only at the outpost. The rectangle is the rule's `dimension`/`minx…maxz`.

## 4. Quest hooks (adopted 2026-09-04 as `gscraft-quests.md` §7.5: nine quests, season 1)

The Woods is the focus of a chain, not a stop on the way. Candidates by NPC:

| NPC | Hook | Why the Woods |
|---|---|---|
| James the Scout | the Woods expedition: reach the ranger cabin, map the two bunkers, find the downed aircraft | his chapter is exploration; the Woods is the one place the map is not a grid |
| Tune the Technician | a relay: climb the high ground, plant an antenna element, receive a signal only the Woods is quiet enough for | radio in the hills; ties to the tower's antenna stage |
| Walker the Foreman | the sawmill: timber for the Walls and defences function; the mill's own drop is the **saw blade** (W-W1); Novo keeps the heavy diesel engine (B22) | lumber is the Woods' resource; the base's walls come from here |
| Tony the Medic | herbs and the hunters' hide: foraging tasks, the surgical kit in the crashed aircraft's medkit | medical from the wild, not the ruin |
| Michael the Engineer | the hunters' water and a generator in the ranger cabin | fuel and water sources outside the plant |
| Marshall | the bandit outpost as a strongpoint-lite: the marker and the 5-minute assault, no fortify clock, no defence (R-W1); the Woods bunkers as the horror chapter's dungeons | contrast: an attack that comes through trees, not streets |

Decided (owner default, 2026-09-04): **no sixth strongpoint** — the Woods is a loot-and-quest region; its nine quests are
J-W1–3, W-W1, T-W1, M-W1, U-W1, R-W1 and R-W2 in `gscraft-quests.md` §7.5.

## 5. How it is built (after the v7 pre-generation)

Lost Cities cannot be switched off by region in its config, but the pre-generation pipeline can: the
world is regenerated chunk by chunk from the seed, so a rectangle generated under a profile with no
cities gives identical terrain with the city gone.

1. **Profile** `woods` — `config/lostcities/profiles/woods.json`, a copy of `wasteland` with
   `cityChance 0`, `scatteredChanceMultiplier 0`, railways off (highways need two cities, so none).
   Created 2026-09-04 (repo `build/phase05/config/lostcities/profiles/woods.json`).
2. **Carve** the Woods rectangle out of the finished v7 world: `carve_regen.py --drop-rect 400 -3500
   2400 -1500` (drops the chunks inside the rectangle only).
3. **Switch** the world's `serverconfig/lostcities-server.toml` `selectedProfile` to `woods`, delete
   Chunky's saved task, run `localpregen.py --center 1400 -2500 --radius 1000` (15,625 chunks, about
   6 minutes), **switch back** to `wasteland`.
4. **Structures**: `place_kept.py --test` with the five chosen positions (from
   `tools/structures_v6.json` positions inside the rectangle, spaced ≥ 500 m).
5. **Road spur** Novo → sawmill in `buildmap/roads_v6.json`, `roads.py route` then `build`.
6. Then the unchanged v6 pipeline (pads, transplants, roads, camp functions, review); the review's
   water/road checks pick the spur up from `routes_v6.json`.
7. Custom sites (sawmill, cabin, aircraft, hide) come with the camp-building tooling (`camp.py`),
   templates placed by function; spawning rules with Phase C.

Cost: about 20 minutes of machine time on top of the v7 build. Nothing else in the layout moves.

Related: `gscraft-map-design.md` §2, `gscraft-structure-plan.md`, `gscraft-map-layout-v6.md`,
`tools/carve_regen.py`, `tools/localpregen.py`, `tools/place_kept.py`.
