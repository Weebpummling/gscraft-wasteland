# GSCraft Wasteland — The player's interface

Draft 1, 2026-09-05 (mockups: the "GSCraft Player Interface" artifact, same day; its §8 decisions are carried into
crafting §4, onboarding §2 and §6, camp spec §5 and the gaps ledger §E on the same day). Scope: what a player sees, presses and reads, and how every system of the game shows its
state and takes the player's input. It sits on top of the onboarding doc (draft 2: the teaching rule, the first
session, the notebook), the camp spec (§2 the board, the rack, the map wall), the quests (draft 3), the vendors
and the crafting sheet (§3–§4 stations). Nothing here changes what those documents say the game *is*; this is
the layer between the game and the player. Facts about the mods were read from the jars on 2026-09-05
(KubeJS 2001.6.5, FTB Quests 2001.4.22, FTB Chunks 2001.3.8, Xaero 26.4.2, Ping Wheel 1.12.1, Hordes 1.6.3g,
PlayerRevive 2.0.31); a few key defaults are marked *verify* and get checked when the key map is generated.

## 0. Five rules

1. **The world is the screen.** Any state that lasts lives on a block: the strongpoint board, the parts rack,
   the banners, the clock sign, the contested lamp, the signs on the doors. Screens (the book, the map, the
   station, the counters) are for *doing* something, never the only place a fact can be read.
2. **One channel per urgency.** A ladder, §3: tooltip → block → action bar → radio line → title → boss bar.
   Nothing is announced on two rungs at once, and nothing skips a rung on the way up.
3. **The HUD at rest is vanilla plus two things:** the minimap and the gun. Everything else appears only
   while it matters and leaves when it stops mattering.
4. **The game never speaks.** Every line comes from one of the seven survivors in their own voice, in their
   own colour, behind a radio click. No "[Server]", no system text, no rule text.
5. **One control is explained, once, in chat** (Tune: the map and the ping). Every other control is the
   notebook's job and the key map's job (§2), and both are readable without anyone asking.

## 1. The screen at rest (the HUD)

| Layer | Where | When | Mod / how | Ship as |
|---|---|---|---|---|
| Hotbar, health, hunger + saturation, armour, air | vanilla positions | always | vanilla + AppleSkin | — |
| Minimap, 100 px, north-up, no entity dots for hostiles (they are the game), team dots on, waypoints on | **top-left** | always | Xaero's Minimap; the default top-right corner is where vanilla draws potion effects, and the Hordes infection icon *is* a potion effect (§5.6) — the two must not overlap | `config/xaerominimap.txt` in the pack, preserved on update (verify the key names when generated) |
| Second minimap | — | never | **FTB Chunks ships its own minimap and an "Open Map" key; both are switched off** (`ftbchunks/client-config.snbt`: minimap enabled = false; key unbound). Its claim map stays reachable from the team screen | packwiz `defaultconfigs/ftbchunks/client-config.snbt` |
| Gun: ammo, fire mode, reload | bottom-right | a gun is in hand | TaCZ's own HUD; the fire-control extension's aim assist has no HUD | — |
| Voice: who is talking | bottom-left, small icons | someone talks | Simple Voice Chat | `config/voicechat/voicechat-client.properties` (icon position) |
| Potion effects (incl. infection) | top-right | active | vanilla / Hordes | — |
| Parkour stamina | above the hotbar | only while a move is in progress | ParCool (its "show stamina only when changed" option) | ParCool client config |
| Party members nearby | — | off; `P` toggles the party screen | sedparties | — |
| Pings | in the world, 5 s, with distance | on a ping | Ping Wheel | — |
| Boss bar | top centre | the assault (5:00), the gate (waves), the finale (the Sleeper) — **nothing else, ever** | loop script `bossbar` commands | — |
| Action bar | above the hotbar | a look-at readout (§3.3) or a first-time note | KubeJS | — |
| Title / subtitle | centre | four moments (§3.5) | KubeJS `title` | — |
| Crosshair | centre | vanilla; TaCZ replaces it while aiming | — | — |
| Downed screen | full overlay | while bleeding out | PlayerRevive (shader on, message tracking-only, as configured) | — |

What is deliberately **not** on the HUD: a quest tracker (the book is opened, not watched; FTB Quests' pinned-quest
overlay stays available for a player who wants it, off by default), a compass, coordinates (the minimap's
coordinate line is on, small, under the map — that is the one number on screen), a clock, a stage list, a
kill feed, damage numbers (Better Combat's are off), party health bars.

## 2. The keys

The pack ships one key map in `options.txt`, placed on first install and never overwritten (packwiz `preserve`),
and the same map is the notebook's **Controls** page. The rule of the map: the right hand of the keyboard and
the mouse are the gun and the body; the letter row next to WASD is movement and parkour; screens live on the
far right of the letter rows; nothing a player needs in a fight is more than one key from WASD.

| Action | Key | Mod | Note |
|---|---|---|---|
| Move / jump / sneak / sprint | WASD, Space, Shift, Ctrl | vanilla | ParCool's fast run is bound to the sprint key, not a second key |
| Shoot / aim / reload / fire mode / melee / inspect | LMB, RMB (hold), R, B, Z, I | TaCZ | *verify* TaCZ defaults; **B is taken from the backpack** — see below |
| Open backpack | **G** | Sophisticated Backpacks (default B) | moved off B: the fire-mode key is pressed in fights, the pack is opened in calm |
| Vault / roll / wall-run / cling | automatic | ParCool | ParCool's "vault", "fast run", "breakfall" and "cling" are set to automatic; its dodge, flip, crawl, hide-in-block and horizontal wall-run are **disabled** (TaCZ owns crawl; the rest are toys) |
| Ride zipline / hang | automatic on contact | ParCool | James's ziplines |
| Map | **M** | Xaero World Map | FTB Chunks' "Open Map" is unbound; Xaero's world map is the only M |
| Minimap zoom in / out | `[` `]` | Xaero Minimap | *verify* defaults (they ship as `-` and `=`?) |
| New waypoint / waypoint list | **N** / **U** | Xaero Minimap | Xaero's "new waypoint" ships on **B** and collides with the backpack and fire mode; moved to N |
| Ping | **middle mouse** | Ping Wheel | the one control Tune explains |
| Push to talk | **V** (hold) | Simple Voice Chat (ships CapsLock) | open-mic is a per-player choice in the voice menu, off by default; whisper unbound |
| Voice menu | **'** (apostrophe) | Simple Voice Chat (ships V) | |
| Journal (quest book) | **J** | FTB Quests (ships unbound) | the book also opens by right-clicking any survivor |
| Party screen | **P** | sedparties | the party *is* the FTB team; this is the one place to see who is on |
| Recruits: command screen | **K** | Recruits | only after D2; faction and claim screens unbound (both features are off) |
| Third person | F5 | vanilla | Leawind's camera is client-side and keeps its own defaults; its "toggle mod" key is unbound so nobody switches it by accident |
| Recipe viewer (in screens) | R view recipes, U view uses, A favourite | EMI | screen-only keys, no clash with reload |
| Curios screen | unbound | Curios | the back slot is visible in the inventory; the extra screen adds nothing |
| Vehicle controls | mod defaults | Immersive Vehicles, Superb Warfare, vvp | documented on the notebook's **Driving** page, which appears with Garage 1 (a seventh page, added by this pass) |
| Everything else | unbound | Apotheosis radial mining, IE glove, Create big cannons, ModernFix, backpack upgrade toggles 1–5, backpack tool swap, FTB Teams GUI, FTB Chunks claim/waypoint keys | the mods keep working; the keys are noise |

Conflicts this resolves (all found in the jars): M (Xaero map vs FTB Chunks map), B (backpack vs TaCZ fire mode
vs Xaero new waypoint), V (voice menu vs the doc's "voice V"), two minimaps, two crawls (TaCZ, ParCool).

## 3. The channels, lowest to highest

### 3.1 Tooltip — the noun
One line per small item, KubeJS `tooltip`: what it is for and who wants it. *"Bolt — Walker wants these."*
*"Blueprint: steel frame — put it in a station."* Never a number, never a rule. The blueprint card's tooltip is the
one exception that lists things: its needs (§4.3), because that list *is* the recipe.

### 3.2 Block — the state
The strongpoint board (six columns, six colours, each column's gloss four words or fewer — the full sentence is the
notebook's), the clock sign, the composition sign, the contested lamp, the parts rack's five hooks, the tower's stages, the watchtower banners, the door signs, the road signs, the map wall,
the Lootr glow, a station's lit texture while it works. Rebuilt by function on the change; never animated,
never blinking. A player who wants to know where the game stands walks to the gatehouse and looks.

### 3.3 Action bar — the readout, only while looking
KubeJS server tick, every 10 ticks, for the block under the crosshair within 5 blocks; the text vanishes when the
player looks away. This is how a screen-less block answers a question without a screen:

| Looking at | Readout |
|---|---|
| a station with an order running | `STEEL FRAME — 1:58` (then `STEEL FRAME — done` until taken) |
| a station missing something | `steel frame — needs: welding torch` / `— needs: 2 more iron plate` (when some are loaded) |
| a board column | `NOVO — held — clock 31:20 — garrison 3/5` |
| the clock sign or the lamp | `next attack: 09:40 — the gate` (Radio 2+; before that, the sign alone) |
| a rack hook | `COOLING — Michael's kit, not yet` |
| a survivor | `WALKER — sneak + right-click to trade` (once the counter exists) |
| the tower ruin from inside the lock rectangle | `Marshall's ground. The tower is built from the rack, not by hand.` |
| a downed teammate (within 6 m) | `hold right-click — 40 %` |

The tower lock's cancels are silent today (`gscraft_tower_lock.js`); the readout above is their only feedback and it
is enough: the player was looking at what they tried to break.

### 3.4 Radio line — the event, in a voice
A chat line is a survivor speaking. Format, fixed for every line in the game:

    ♪ [TUNE]  You're up. The ramp's on the east side of the pit — six of us on the rim.

- A radio click first: `minecraft:block.note_block.hat`, pitch 0.5, volume 0.4, at the player (a resource-pack
  static sample can replace it later; the id stays).
- The name in small caps in the survivor's colour, then two spaces, then the text in white. Colours: Walker gold,
  Tony red, Michael yellow, Tune aqua, James green, Marshall white, Teddy dark green. Nobody else ever speaks
  in chat: no "[Server]", no `say`, no yellow "joined the game" (it is replaced by Tune's line when the join is
  the first; later joins print nothing).
- One line, two sentences at most, no numbers unless the sentence is the number (a distance, a count).
- **Rate:** one line per player per 20 s; later lines queue; nothing is dropped; a queue longer than three
  collapses to the newest per speaker. A line never plays during a title, and never while a look-at readout is
  showing (the readout sits one line above the hunger row, chat one line above that; the mockups showed the two
  colliding). Chat is capped at four visible lines; the voice icons stay on the hotbar's baseline below it.
- `tellraw` from the loop script (`gscraft:say <npc> <key>` — the text lives in a lang file, not in the script).

### 3.5 Title — the four moments
Titles are the loudest thing on screen and are used exactly four times in the game, with fade 10/60/20 ticks:

| Title | Subtitle | When |
|---|---|---|
| **WASTELAND** | — | first join, before Tune's first line |
| **THEY'RE COMING** | *the gate, two minutes* | the two-minute mark of every counterattack clock |
| **NOVO IS OURS** (the site's name) / **THE GATE HELD** / **THE GATE FELL** | *hold five minutes* / *nothing lost — they'll be back* | the assault won; the counterattack won; the counterattack lost |
| **THE SLEEPER** | *sixty minutes* | the beacon lit (finale) |

Nothing else is a title. Not a stage, not a tier, not a quest, not a death. A title and a boss bar never share the
screen: the two-minute title fires before the gate bar exists, the result title after the bar is removed.

### 3.6 Boss bar — the clock you cannot look away from
Three bars, one at a time, coloured to match the board: the assault (blue, `NOVO — hold — 4:12`), the gate (red,
`THE GATE — wave 2 of 3`), the finale (purple, the Sleeper's health). The fortify clock is **not** a boss bar; it
lives on the clock sign and the board readout, because forty minutes of bar is a bar nobody sees.

### 3.7 Sound — three cues
The radio click (§3.4); the gate bell (`minecraft:block.bell.use` three times from the gatehouse, heard within
64 m) at the ten-minute warning; the completion chime of a station (`minecraft:block.note_block.chime`) at the
block. Nothing else is added; the mods' own sounds (guns, the fog man, the sculk) carry the rest.

### 3.8 The book — the name, after the fact
The **Field notes** chapter (onboarding §4.5): two lines when something happens the first time, written by the
same stage that fires the first-time radio line. The book is where a rule gets its name; it is never where a
rule is announced.

### 3.9 The notebook — the reference
The Patchouli book, given once, never required: Controls, The camp, Reading the board, Carrying, Getting hurt,
Where things are, and (new) **Driving**, which appears with Garage 1. Under sixty words and one picture per page.

## 4. The screens

### 4.1 The journal (FTB Quests)
- **Opening it:** `J`, or right-click any survivor (KubeJS entity interact → `/ftbquests open_book` on that
  survivor's chapter; the subcommand exists in 2001.4.22). There is **no quest book item**: the survivors are
  the book, and the kit's five slots stay for tools.
- **Chapters, in order:** Walker, Tony, Michael, Tune, James, Marshall, The tower, Field notes, Counters. The
  first five are visible from the start (their NPC is on the rim); Marshall's and the tower's appear after the
  five introductions; Field notes appears with its first entry; Counters with the first vendor tier.
- **What a page shows:** the title (≤ 4 words, the NPC's phrasing), the body (one voice sentence, one task
  sentence), the tasks as FTB draws them, the reward line naming the change in the world. Dependencies are
  drawn as FTB's lines; nothing else is decorated. Quest icons are the item asked for or the thing built.
- **The one thing to do next:** the newest quest that became available is auto-pinned by the loop script
  (`ftbquests` pin via the team data) so the pinned-quest overlay, if a player turns it on, shows one line.
- **Late joiner:** a player who joins after session two sees every completed quest ticked (team progress) and
  the same five introductions un-ticked for themselves (per-player quests, onboarding §2). Their book opens on
  Walker's page; the board tells them the rest. Nothing replays in chat except Tune's three first-join lines.

### 4.2 The map (Xaero)
- The **world map** (`M`) fills as the team walks; the roads draw themselves. The **map wall** at Tune's is the
  view of the parts nobody has walked to — the two never disagree because the wall shows sites and roads only.
- **Waypoints from the game:** James's quests (J1, J-S1…) and Radio 1 push waypoints to every team member with
  Xaero's chat protocol: a `tellraw` whose text is `xaero-waypoint:NOVO:N:-2808:65:-736:9:false:0:Internal-overworld-waypoints`
  arrives on the client as a clickable *add waypoint* line (the client parses `xaero-waypoint:` messages; **verify
  in Phase C on the Prism instance**, fallback: the coordinates in the quest body and Tune's line). Waypoint
  colour follows the board: scouted yellow, held blue, defended lime, lost red — the loop script re-sends the
  waypoint on each state change and the client's edit replaces it.
- **Pings** (middle mouse) are the five-second layer: a dossier room, a marker anchor, "here". They are never
  used for state.
- The minimap shows teammates, waypoints, the claim outline; no hostile entity dots (Xaero's entity radar is off
  for hostiles and neutrals, on for players and vehicles) — noise and the fog do the warning, not a dot.

### 4.3 The station (the work station block)
KubeJS 2001.6.5 has block entities with an inventory attachment and `rightClickOpensInventory`, so the station is
a real block with a real screen and no GUI mod. The decision this pass makes: **there is no recipe menu. The
blueprint is a card, and the card is the order.**

- **The screen:** a plain 3×4 container screen titled with the station's name (`WALKER'S STATION` when
  bound). Row 1: the **blueprint slot** (slot 0), the **tool slot** (slot 1), the **output** (slot 2, take-only).
  Rows 2–4: nine input slots. Yard tier 2 and 3 add a second and third blueprint slot (queue depth 2/3) by
  swapping the block for its tier variant when the yard is rebuilt.
- **Ordering:** put the blueprint card in slot 0; the card's tooltip already listed the needs; put the parts in
  rows 2–4 and the tool in slot 1 if the card asks for one. Every second the block entity checks the card
  against the slots; the moment they match it consumes the parts (not the card, not the tool — the tool loses one
  durability), lights its working texture, and starts the countdown. The output lands in slot 2; the chime plays;
  the block stays lit until the output is taken. The card stays in the station: a station full of cards *is* the
  player's recipe list, and locked recipes do not exist because the card was never handed out.
- **Owner binding:** the first player to open it owns it; anyone else sees the screen but the block ignores their
  items (`needs: Walker's station — this one is Tune's`). Team stages gate the cards, not the blocks.
- **Readouts:** the action bar (§3.3) while looking; the lit texture from across the yard; the chime. A player
  away from the block has no readout and does not need one: an order is two to ten minutes, and the block is
  inside the wire.
- **Failure text**, all on the action bar, all in the same shape: `steel frame — needs: welding torch`,
  `— needs: 2 iron plate`, `— the tool is broken`, `— output full`. Never a chat line, never a sound.
- **EMI** cannot list these orders (custom block, no recipe type); it is not asked to. EMI stays for looking up
  what an item is and where vanilla-type things come from. The card's tooltip is the recipe.

### 4.4 The backpack
`G`. The pack sits in the Curios back slot and shows as a slot in the inventory; upgrades arrive as Storage
orders and are dropped into the pack's own upgrade slots (Sophisticated's screen, unchanged). Bulky items: the
first one picked up gives Slowness, blocks sprinting and refuses the pack, and prints the one-time line *"Too
heavy to run with. Cars carry these."* on the action bar, not in chat; the Field note follows.

### 4.5 The counters (vendors)
Sneak + right-click a survivor opens the vanilla merchant screen written by script (vendors §7). Daily caps use
the offer's own `maxUses`, so a sold-out line shows vanilla's red cross — no text needed. The **Counter** quest
page (three per NPC) is the stock list, because EMI cannot show trades. The dawn restock is Tune's *"Counters
are open."* — one line for all seven counters, never one per counter.

### 4.6 The Recruits screen
`K`, from D2 on. Hired at the gatehouse with emeralds through Recruits' own hire screen; orders are follow /
hold / return. The site guards at held strongpoints are the loop's, not the player's, and do not appear in the
command screen (they are spawned without an owner). The Guard Villagers at the buildings take no orders.

### 4.7 The party screen
`P`. The party is the FTB team (sedparties `useFTBTeams`); this screen shows who is online, xp share is on,
friendly fire is off. Team invites happen here once, on the first evening, and never again.


### 4.8 The gun and the site keepers (the Create fork)
- **The first gun is the camp's.** G1–G4 happen at Walker's yard and the gun pit on the crater rim (create doc §4,
  owner 2026-09-05); the sites make it bigger, faster and mobile from G5 on.
- **Nothing about operating the gun is ours** (owner, 2026-09-05: no direct control, that is not how artillery
  works; the mod's own mechanics, read from Create Big Cannons 5.11.4). A big cannon sits on a **Cannon Mount** that
  is laid by rotation — a hand crank or gearshift on its pitch face, a **Yaw Controller** for traverse — assembled by
  powering the mount's hammer face and fired by powering its firing face (a lever). There is no seat, no sight, no
  reticle and no key that aims it. The lay is read on Engineer's goggles (`Cannon Pitch: 11°`, `Cannon Yaw: 42°`,
  `Cannon Strength`) or on a Create display board fed by a **display link from the mount** — the pit board, Tune's
  U-B2. The only gun a player holds is an autocannon with handles (G8, the watchtower nests), the mod's own design
  for point defence. The cannon carriage (G9) moves a gun; emplaced, it is laid and fired the same way.
- **A gun is served by a crew:** one lays, one loads (the cannon loader, ram head; charges and shot), one fires.
  Fall of shot is watched by eye and by the players at the lookout on voice; nobody in the game calls corrections.
- **What we add:** the quest gates; the **gunner's manual** (G5, Vera): a Patchouli range card per gun — pitch and
  charges to range — because the mod ships none; the range rings on the map wall (G5); the keeper's counters.
- **The site keeper is a survivor** (five of them: Vera at Skadowsky — the residential block in v8 — Kessler, Ilya, Rook, Oksana): same door sign, same right-click for the journal (chapter `S-<site>`), same
  sneak-click for the counter. The site's core building carries the readout sign: name, tier, what the keeper sells,
  rebuilt with the tier like the camp's door signs.
- **Ponder is the tutorial.** Casting, boring, building, welding, loading, mounting, firing, fuzing and the
  autocannon each have a Ponder scene in the mod; no quest, note or line repeats one.


### 4.9 Designer tools (owner, 2026-09-05)
The five players are also the map's designers and repair crew, so the convenience tools stay in the pack and in their
hands: **WorldEdit 7.2.15** (both sides; op-gated, so every designer is opped at **level 2** — `op-permission-level=2`,
the owner alone at 4 in `ops.json`), with **WorldEdit CUI** (client-only) so a selection is visible, and the vanilla
`/tp`, `/gamemode` and `/give` that level 2 carries. WorldEdit sets blocks directly, so the tower and building locks
do not stop it — that is the point of a hand repair. Nothing about play changes: a designer in creative or with a wand
is a designer, and the counters, stations and quests behave as before. The rest of the kit (Lighty, IBE Editor, Jade
hidden by default, Freecam unbound, FTB Ultimine by hand) is researched in `docs/notes/gscraft-designer-tools.md`.

## 5. Each system: state → interface → input

| System | The player sees | The player does | Failure feedback | Where it is built |
|---|---|---|---|---|
| **Site ladder** (unknown → scouted → looted → held → defended → lost) | the board column's colour; the watchtower banner (tier 2+); the Xaero waypoint colour; one radio line per change (Tune) | scouts (James's dossier task ticks it), loots, places **Marshall's marker** (a banner item from R2) at the site's flag point, holds five minutes | marker refused: Marshall *"James hasn't been. Neither have you."* and the marker drops back into the hand | loop script + `gscraft:board_<site>_<state>` functions |
| **Assault** (5 min) | boss bar `NOVO — hold — 4:12`; the waves; the elite | fights; stays inside the site's rectangle | leaving the rectangle pauses the bar and Marshall says *"Get back in there."* once | loop script |
| **Fortify clock** (40 min) | clock sign at the gatehouse; board readout; contested lamp lit | nothing (it is time) | — | `data merge` each minute |
| **Counterattack** | 10 min: gate bell + Tune's line + the sign; 2 min: title THEY'RE COMING; arrival: boss bar `THE GATE — wave 1 of 3`; result title | defends the gate | lost: title THE GATE FELL, column red, banner red; the site stays ours | loop script |
| **Tower** | the rack's five hooks fill; each stage's geometry grows; the lock rectangle's action-bar line; Marshall's one line per stage | hands the kits to Marshall (X2–X6 quests) | breaking inside the rectangle: the readout only | tower functions + `gscraft_tower_lock.js` |
| **Camp tiers** | the building is replaced by its next tier with a 10-second scaffold in between (a function pair, so the rebuild is *seen*); the door sign gains a line; a new Magnum Torch appears; Marshall's line names it | completes the NPC's tier quest | — | `camp.py` tier templates |
| **Stations / orders** | §4.3 | §4.3 | §4.3 | KubeJS block entity |
| **Blueprints** | a card item in the reward line and the inventory, tooltip = the needs | keeps it in a station | no card, no recipe; nothing to say | KubeJS items + team stage `bp_<recipe>` (the stage stays for the vendors' gates) |
| **Infection** | the Hordes potion icon (top-right) from the hit; at each 5-minute stage the icon's amplifier rises (Hordes) ; at the last stage the action bar says `you're burning up — Tony's clinic` every 30 s; Tony's T1 line the first time; Field note | walks to the clinic (T1) or uses the med kit (Medical 2) | death by infection respawns at the camp with the Field note already written | Hordes config (as shipped) + KubeJS effect watch |
| **Revive / death** | PlayerRevive's downed overlay; a teammate's action bar `hold right-click — 40 %`; inside the camp outline the ground itself revives after 10 s (Medical 1) and the action bar says `the camp has you`; Field note the first time | holds right-click on a downed friend | five-minute bleed-out → respawn at spawn, inventory dropped except the everlasting pack; no title, no chat line — death is not an event the radio reports | PlayerRevive (as configured) + KubeJS |
| **Noise** (Zombie Awareness) | the garrison converges; nothing on screen | uses a suppressor | one loud run | config as shipped |
| **Loot** | Lootr glow on unopened chests; shared containers do not glow | opens | an emptied shared container stays open-lidded (a block state) until it refreshes | Lootr + loop script |
| **Carrying** | §4.4 | | | KubeJS |
| **Vehicles** | Walker's dead quad (tier 0); the bay; the vehicle's own HUD when driven | builds from a kit at the bench | a crash | Immersive Vehicles / SBW / vvp, the notebook's Driving page |
| **Recruits / guards** | §4.6; guards at doors by tier | hires | — | Recruits, Guard Villagers |
| **Vendors** | §4.5 | trades | sold out (vanilla) | script-written offers |
| **Artillery** (Create fork) | the mod's own: pitch and yaw on goggles and on the pit's display board, the loader, the lever; ours: the range card, the map wall's rings (G5), the keeper's sign; Ponder as the tutorial (§4.8) | lays by crank and yaw controller, loads, fires by lever; builds G1–G4 in the camp, then the site chains | the mod's own messages (an unsafe load bursts the gun; a misassembled cannon refuses with its reason) | Create Big Cannons |
| **Finale** | the sculk ring and the shrieker as the telegraph; the beacon; title THE SLEEPER; the boss bar; Marshall's lines per wave | lights the beacon, holds | fail → `finale_failed`, X6b Relight in the book; no title for the failure, the dark beacon is the title | finale script |
| **World border** | vanilla's red vignette from 200 blocks | turns around | none (no damage) | vanilla |
| **The team / late joiner** | Tune's three lines; the notebook; a full board; James's waypoints re-sent on join; the book with the team's ticks and their own five introductions | plays | — | first-join script (per-player stage `joined`) |
| **The operator and the designers** | `/gscraft` (KubeJS command): `state` (the board as text), `site <id> <state>`, `tower <n>`, `say <npc> <key> [player]`, `tour <player>` (replays the first-join sequence), `clock <minutes>`; WorldEdit with its CUI for hand repairs (§4.9) | fixes things from the console or in place; the hosted panel needs no more than this | every command answers in one line on the console, nothing in the players' chat | server script |

## 6. Copy rules (the voices)

- Walker (gold): short, mechanical, verbs first. Tony (red): dry, medical. Michael (yellow): technical, pleased
  with himself. Tune (aqua): the radio operator — every system line that is not one survivor's own is Tune's.
  James (green): distances and directions. Marshall (white): commands, never explanations. Teddy (dark green):
  the Woods, later.
- A line is at most two sentences; a title is at most three words; an action-bar readout is one phrase in the
  shape `THING — state — detail`; a tooltip is one phrase with an em dash.
- Numbers appear only where the number is the point: a countdown, a distance, a wave count. Never a percentage
  except the revive bar.
- Every line lives in `assets/gscraft/lang/en_us.json` under `gscraft.line.<npc>.<key>` and is referenced by key
  from scripts and quests, so the text can be edited without touching a script.

## 7. What this asks of the build (Phase C, added to onboarding §8)

- `options.txt` with the key map of §2 (packwiz, preserved) and the client configs of §1: Xaero minimap
  (top-left, radar off for hostiles), FTB Chunks minimap off and its map key unbound, voice icons bottom-left,
  ParCool moves on/off, Better Combat damage numbers off.
- The station block: KubeJS block + block entity (`inventory(3,4)`, `rightClickOpensInventory`, a server tick
  that matches the card against the slots, a lit block state, the chime); the tier-2/3 variants; the blueprint
  card items with tooltips; the owner binding.
- The look-at readout: one server-tick script (`gscraft_readout.js`) for the station, the board, the sign, the
  rack, the survivors, the lock rectangle, the downed teammate.
- The radio line helper: `gscraft:say` (click + formatted tellraw, the per-player 20-second queue), the lang file
  of lines, the join-message replacement.
- The titles and boss bars in the loop script at the moments of §3.5–§3.6; the gate bell.
- James's waypoint push (`xaero-waypoint:` tellraw) and its colour re-send on state changes; verify on the client.
- The `/gscraft` operator command.
- The notebook's seventh page (Driving) and the Controls page generated from the same key map.
- Quest text pass: every chapter's icons and the auto-pin of the newest quest.

## 8. Decisions this pass makes (say if any is wrong)

1. **No recipe menu in the station; the blueprint card is the order.** The alternative — a recipe list in the
   block's screen — needs a GUI mod or Java. The card model needs neither and matches "the world does the telling".
2. **No quest book item.** Right-click a survivor or press J.
3. **Backpack on G, fire mode on B, new waypoint on N, voice on V.** The three B's could not coexist.
4. **FTB Chunks' minimap and map key are off.** Xaero is the only map (the design already said so).
5. **The minimap is top-left.** Infection sits top-right and must be seen.
6. **Four titles, three boss bars, three sounds, one explained control.** Anything more is noise.
7. **Death is silent.** No chat line, no title; the Field note and the respawn say it.
8. **Every text is a lang key.** Scripts and quests reference keys; the writing pass edits one file.
