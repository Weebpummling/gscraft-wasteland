# GSCraft Wasteland — Teaching the game (onboarding without a manual)

Draft 2, 2026-09-04 (draft 1 the same day; rewritten for plain wording and for any number of players).
The design (draft 6), the quests (draft 3) and the crafting sheet describe a game nobody has played
yet: a hundred mods, a custom loop, work stations instead of crafting tables, sites that are scouted,
looted, taken and held, a tower repaired in stages. New players meet all of it within a few evenings.
This document describes how they learn it **by playing** rather than by reading: where each system is
first met, what is said at that moment, and what is deliberately left unsaid. It applies to any team
size, from one player to a full server; nothing below depends on how many people are online.

## 1. The rule

**A player meets every rule as a situation before reading its name.** They do the thing, see the
result, and only then read a short line that names it. Nothing is explained before it is needed,
nothing is explained twice, and nothing takes more than two sentences. The quest book is a journal:
what was done and the one thing to do next. It is never a rulebook. The six survivors in the camp do
the teaching, the camp is where it happens, and the first strongpoint is where it is tested.

Three consequences for everything below:

- **One new action at a time.** The first hour teaches *find*, then *hand in*, then *order* (craft),
  then *carry*, then *travel*. Taking a site, holding it, defending it, building and flying each get
  their own hour later.
- **Ask, do not instruct.** A quest asks for eight bolts; it never says "loot the ruins". The player
  looks around, sees a wrecked car with a chest in it, and has learned looting without a sentence
  about it.
- **Show the object before the system.** Whatever a system is about is already standing in the world
  before the system is introduced: the tower ruin is visible from the first minute, Walker's lot has a
  dead quad on it, the parts rack at the gate has five empty hooks, the strongpoint board has six dark
  columns. Players ask about what they can see.

## 2. The first session, minute by minute

Act I is the tutorial. Nothing extra is bolted on; this is simply the order in which the game's own
quests bring things up. Times are approximate and assume a player who wanders a little.

| When | What happens | What it teaches | What is said (all of it) |
|---|---|---|---|
| 0:00 | Spawn on the plaza of the Warium structure in the crater. **Custom Starting Gear** puts the personal work station, a pistol with one magazine, a flashlight with one battery, a bandage and the survivor's notebook (§6) in the inventory. Night is ten minutes away. | the inventory; that this is a game with guns | Title card: *WASTELAND*. Then the first of Tune's three radio lines, twenty seconds apart: "You're up. The ramp's on the east side of the pit — six of us on the rim." |
| 0:02 | The crater ramp. At the top, the camp: six lit buildings, ten Magnum Torches, 24 ruin pieces (wrecks, sandbag checkpoints, a shed, tents). The gate and the radio tower ruin stand against the sky. | the camp is the safe place; the ruin on the rim matters | Nothing spoken. A **sign** on every NPC building: name, role, one line ("WALKER — the yard. Bring me anything with a thread on it."). |
| 0:05 | Right-click any survivor: the quest book opens on that survivor's first quest. It asks for things (8 bolts, 8 nuts). | hand-ins; that the survivors want junk; where the book is | The NPC's one line, in their own voice, then the task in one line. |
| 0:06–0:25 | The camp's own ruins. **Lootr** chests glow for a player who has not opened them yet; the wrecks hold hardware, the tents bandages, the shed wire. | looting; instanced loot (each player has their own chest contents); the item names | Item tooltips carry one line each ("Bolt — Walker wants these"). No quest text. |
| 0:10 | Dusk. Nothing spawns inside the torches; the Man From The Fog is heard once, far off. | the camp is safe **because of the torches**; the horror is outside | — |
| 0:25 | First hand-in to Walker. Reward: a wrench and two blueprints; the station from the kit binds itself to its owner. | the reward loop; **stations** exist | Walker: "Good. Set your station down somewhere inside the wire. It'll only ever answer to you." |
| 0:27 | Placing the personal station. The fastener-kit recipe is in it; an order takes two minutes (the Intermediate class). The player waits, or walks off and comes back. | **timed orders** (the tool slot comes up at W3, when the steel frame needs the torch) | Station UI header: "Order — 1:58". Nothing else. |
| 0:30 | W2 asks for two fastener kits; the second order runs while the player loots for Tony. | orders run while you do other things | — |
| 0:35–1:00 | Three more introductions from the same ruins (Tony's bandages, Michael's wire and filter, Tune's circuit board and broken radio). James's two locations (J1) wait for the first walk out. | each survivor owns one thing; rewards are visible in the world | Each NPC: one line. Michael: "There. Now we can see what's coming." |
| 1:05 | James's J1: the glass tower (1.3 km) and the acacia hall (1.55 km). The first walk out along the spine. **Xaero** shows the road; **Ping Wheel** is explained by Tune's line. | the map, waypoints, pings; roads lead somewhere; distance costs time | Tune: "Press M for the map. Middle-mouse pings a spot for everyone." (the only control ever explained in chat) |
| 1:30 | Back at camp with a backpack from W2 (Storage 1). The fifth introduction is done, so Marshall **speaks** for the first time: the camp outline lights up and the map wall is revealed (R1, a datapack function); the strongpoint board lights one column — Novo, the industrial yard 1.06 km east along the spine, state *unknown*; the tower chapter appears in the book, and X1's briefing names its five hooks. | the loop exists; there is one target; the tower is the long game | Marshall: "A whole town's worth of ruins out there. Start with the industrial yard east along the road. Ask James what's in it first." |
| Session 2 | James J-S1: reach Novo, find the dossier (the board turns *scouted* and shows the garrison). Walker W5: two or three loot runs (*looted*). Marshall R2: the marker, the five-minute assault, the friendly garrison that appears when it is won, the fortify clock, and the counterattack that arrives at the camp gate when it ends (*held*, then *defended*). | the whole **site ladder**, one state per trip, each state a colour on the board (the watchtower banners come later, with gatehouse tier 2) | Each state change is one radio line from Tune and a board column changing colour. |

By the end of session two the team has looted, ordered, carried, walked, scouted, taken, held and
defended (at their own gate) — every action the game has — without one paragraph of instructions. A player who joins
later gets the same introductions as a tour: the team's progress stages are shared, but the first-time
lines and the introductions are per player.

## 3. Each system's teaching moment

| System | First met | How it is shown | What names it (two sentences at most) | The failure that teaches |
|---|---|---|---|---|
| Looting / Lootr | camp ruins, minute 6 | glowing chests; wrecks with visible props | tooltip on the first item picked up | opening a chest a friend already opened still has loot in it: instanced loot is learned, not read |
| Stations and timed orders | W1 reward | the station block the player placed; a countdown in its UI | Walker's one line | ordering a steel frame without the torch in the tool slot (W3): the UI says "needs: welding torch" |
| Blueprints as stages | W1, W3 | recipes appear in the station only after the quest | the quest reward line "blueprint: steel frame" | trying to order something not yet unlocked: the recipe is simply not listed |
| Backpack, bulky items | W2 (Storage 1), W11 (the kit) | the pack in the Curios slot; the first bulky item gives Slowness and no sprint | one chat line, the first time only: "Too heavy to run with. Cars carry these." | walking home slowly once |
| Map, waypoints, pings | J1 | the Xaero map with the road drawn on it; Radio 1 (U2) shares waypoints | Tune's control line | getting lost does not last: the spine is visible from any hill |
| Roads and distance | J1, W5 | the spine to Novo; the walk takes four minutes | nothing; the clock does it | the walk back at dusk |
| Safety, torches, the horror | first dusk | ten torches; the fog man's sound | nothing | a player who sleeps outside the wire meets the fog man |
| The site ladder | J-S1 → R2 | the strongpoint board (six columns, six colours); later the watchtower banners | one radio line per state change | the marker refused before scouting: Marshall says "James hasn't been. Neither have you." |
| The assault and the fortify clock | R2 at Novo | a boss bar for the five minutes; the board shows the ten-minute warning (the whole clock once Radio 2 is in); the counterattack arrives at the camp gate exactly when it ends | Marshall: "Hold it five minutes and it's ours. My people will keep it. Then dig in here — they'll come for the camp when the clock runs out." | losing the counterattack: the column turns red and the wave comes again after the next clock; the site stays ours |
| Infection | first zombie hit | the Hordes infection icon; Tony's clinic cures it | Tony's T1 line: "If one bites you, come to me before it spreads." | dying of it once, near the clinic |
| Noise (Zombie Awareness) | first shot fired at a site | the site's garrison converges | Walker W-A4: "A suppressor is the difference between a quiet run and a fight." | one loud run |
| Vehicles | W7 (Garage 1) | a dead quad on Walker's lot from minute 2 (tier 0 dressing); the first bay arrives with W-B1 | Walker: "The bench builds it from a kit. The kit takes a trip." | the first drive out of the crater ramp |
| The tower | minute 2 (the ruin), X1 (the briefing), X2 (stage 1) | the ruin on the rim; each stage visibly grows; the parts rack fills hook by hook | Marshall, per stage: one line naming the part | none needed |
| Flying | W13, the runway | the runway lights at night, visible from the settlement road | Walker: "Take off into the wind. Land the same way." | a crash: PlayerRevive and a second airframe |
| Revive | first time someone goes down | PlayerRevive's downed state; a teammate holds right-click | a Field note the first time anyone goes down: "Hold right-click on a downed friend." | nobody nearby: the five-minute bleed-out. Inside the camp outline the camp revives a downed player after ten seconds (Medical 1); a player alone elsewhere respawns at the camp. |

## 4. What the book is, and is not

The quest book (FTB Quests) is the **journal**. Rules for every quest in `gscraft-quests.md`:

1. **Title:** four words or fewer, in the NPC's phrasing ("Nuts and bolts", "East, a mile").
2. **Body:** one sentence in the NPC's voice plus one sentence of task. No lists, no numbers the task
   line does not need, no explanation beyond the voice. The trip table and the ladder live in the
   design, not in the book.
3. **Reward line:** names the thing it changes in the world ("the camp lights", "Storage 2: the iron
   pack"). The reward is the explanation.
4. **No chapter is visible before its NPC has spoken.** Marshall's chapter and the tower chapter both
   appear the moment the five introductions are done (owner, 2026-09-04); the tower's stages then stay
   locked behind their parts. The book grows with the game. A full book on day one is a manual.
5. **Field notes:** one extra chapter that fills itself, two lines per entry, written when something
   happens for the first time (first infection, first bulky item, first attack warning, first vehicle,
   first death). This is where the rules get their names, after the fact.
6. **Nothing in the book explains a control.** Controls are the notebook's job (§6).

## 5. The world does the telling

- **Signs** at every NPC building: name, role, one line. Placed by `camp.py` with the tier templates.
- **The strongpoint board** at Marshall's gatehouse: six columns (the five strongpoints and the Woods'
  outpost), six states, six colours (dark / scouted / looted / held / defended / lost), rebuilt by
  function on each state change. It is the loop's whole UI.
- **The map wall** at Tune's: the box, the roads, the sites as they are scouted (banner blocks placed
  by function). Tune's radio lines announce state changes and attack warnings.
- **The parts rack** at the gate: five hooks, empty until the kits arrive. The tower is "what is missing".
- **Banners on the gatehouse watchtowers** (tier 2+): one per held site, lime once defended, gone when lost.
- **The tower stages**: the only progress bar the endgame needs.
- **Dead vehicles at the strongpoints** (crafting §2.1): the military tier is seen long before it can be built.
- **Road signs** at the three junctions (Doomsday Decoration props): "NOVO 1 km →", "PLAZA ←".
- **Ping Wheel** for the team; **Xaero** waypoints from James.

## 6. The one piece of paper: the survivor's notebook

Patchouli is in the pack. It gets exactly one book, six pages, given at first join and never required:
**Controls** (quest book key, map M, ping middle-mouse, voice V, backpack key, the station's UI),
**The camp** (the six names and what each wants), **Reading the board** (the six colours), **Carrying**
(packs, bulky items, cars), **Getting hurt** (revive, infection, the clinic), **Where things are** (one
line per site as it is scouted; the page grows). No rules text, no lore. Each page is under sixty words
and a picture. That is the entire written manual of the game.

## 7. Failure is the second teacher

Early failures are cheap and close to the clinic. The design keeps them that way and lets them explain:

| Failure | Cost | What it teaches | Where it can first happen |
|---|---|---|---|
| Dying in the camp ruins | nothing (keepInventory is off, but the ruins are 100 m from spawn; PlayerRevive) | revive, the clinic | Act I |
| Infection | a walk to Tony | the medical function's purpose | Act I |
| Carrying a bulky item on foot | a slow walk | why the garage exists | W11, the first kit |
| A loud run at Novo | a fight | noise, suppressors | W5 |
| Losing Novo's counterattack at the gate | the wave comes again after the next clock; nothing is lost | the walls matter; defended sites are safe for good | R2 |
| A crash | the airframe | flying is late-game for a reason | Act IV |

## 8. What this asks of the build (Phase C)

- **First-join script** (KubeJS): the title card, Tune's three lines twenty seconds apart, the notebook
  and the starting kit (Custom Starting Gear config: personal station, pistol + magazine, flashlight +
  battery, bandage, notebook). It runs for every new player, whenever they join.
- **Signs and the board** in `camp.py` tier templates; board and banner colour functions
  `gscraft:board_<site>_<state>`; Tune's radio lines as `tellraw` from the loop script.
- **Quest text pass** over `gscraft-quests.md`: every body to the two-sentence rule; the Field notes
  chapter with its advancement triggers; chapter visibility gates as written.
- **The notebook**: `build/patchouli_books/survivors_notebook/`, six pages.
- **Item tooltips**: one line per small item (KubeJS item builder `tooltip`).
- **The first-time lines**: bulky, infection, first warning, once per player, via a player stage.

## 9. Playtest measures (Test 2, foot range)

Run it with whoever is available, from one player up. Watch, do not ask: time to the first hand-in;
time to the first order; whether anyone opens the book unprompted; whether anyone asks a question in
voice chat that a line above should have answered. Every such question is a gap in this document, not
in the player. Pass: everyone who plays reaches Marshall's first line inside two sessions without a word
from the operator.

Related: `gscraft-map-design.md` §2.2, §3, §3.6, §4.5 (the rules of play, including late joiners);
`gscraft-quests.md` §1, §8; `gscraft-crafting.md` §4; `gscraft-mod-capabilities.md` (Custom Starting
Gear, PlayerRevive, Lootr, Ping Wheel, Patchouli).
