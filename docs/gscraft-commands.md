# GSCraft Wasteland — the commands

*2026-09-13. Every `/gscraft` command the mod registers, the FTB Quests, Lootr and datapack commands the slice leans on,
and the play-test recipes. All `/gscraft` commands need op (permission 2). Coordinates are block coordinates; `~ ~ ~`
works anywhere a position is asked for in-game; from the console give numbers. Sites are the mod's ids (`hospital`,
`switchyard`, `intake`, `turbine`, `krot`; the building takes `square`, `gatehouse`, `north`, `crossing`, `mast`).
Survivors are `walker`, `tony`, `michael`, `tune`, `james`, `marshall`. The source is
`mod/src/main/java/gscraft/war/**/*Commands.java`, `WarEvents`, `StationEvents`, `SurvivorEvents`.*

## 1. Play-test recipes (start here)

| Want | Do |
|---|---|
| Reset everything for a fresh run (everyone online) | `/gscraft reset all` — quest progress, stages, the ladder, every player's tags and advancements; then everyone to survival, emptied, healed, at the world spawn with the first join again (title, kit, Tune's lines); then Lootr's opened-chest memory cleared |
| Only the quest sequence | `/gscraft reset quests` |
| Only the players | `/gscraft reset players` |
| Watch the first join again | `/gscraft join @s` |
| The starting kit again | `/gscraft kit @s` |
| Spawn armour where I stand, facing my way | `/gscraft director armour ~ ~ ~ superbwarfare:bmp_2 4` (light: `bmp_2`, `m3a3`; heavy: `t_90a`, `m_1a_2`; the last number is the riders, 0-8) |
| Spawn a squad of fighters | `/gscraft director ambient ~ ~ ~ 3` (three director passes at that spot from the zone's own pool) or `/gscraft vehicle spawn <type> <faction> [x y z]` |
| Take the hospital without the quests | `/gscraft site hospital set scouted`, `/gscraft site hospital set looted`, then use the claim marker inside it (`/give @s gscraft:claim_marker`) or `/gscraft site hospital marker` |
| Shorten a clock (assault, fortify) | `/gscraft site hospital clock 30` |
| Light a take by hand | `/gscraft stage add square_taken` (the torch, the survivor, the zone) |
| See what the world knows | `/gscraft sites`, `/gscraft stages`, `/gscraft board`, `/gscraft station list`, `/gscraft survivors` |
| Stop the enemy layer for a quiet look | `/gscraft director pause` (and `resume`); `/gscraft hold on` freezes every fighter (`off`) |
| Open a chapter | `/ftbquests open_book #walker` (any chapter tag: `compound`, `pocket`, a survivor's id) |
| Call a fire mission by hand | `/gscraft strike mortar ~ ~ ~` (or `artillery`, `air`); `/gscraft strike status`; `/gscraft strike reset` clears the cooldown and any run. The grenades: `/give @s gscraft:strike_mortar` (also `strike_artillery`, `strike_air`) |

## 2. The survivors and the first join

| Command | What it does |
|---|---|
| `/gscraft survivors` | the six survivors: profession, tag, chapter file present, hello line present, seen advancement present; the title, the join lines, the kit |
| `/gscraft say <npc> <key>` | prints the radio line as the server renders it (a check of the lang key) |
| `/gscraft say <npc> <key> <players>` | queues the line for those players: the click, `♪ [TUNE]  text`, one per player per 20 s |
| `/gscraft kit` / `/gscraft kit <player>` | lists the first-join kit as resolved stacks / gives it |
| `/gscraft join <player>` | the first join again: `joined` and `seen_*` cleared, the title, the kit, Tune's lines, the book on The compound |
| `/gscraft reset quests|players|all` | §1 |

Lines live in `assets/gscraft/lang/en_us.json` as `gscraft.say.<npc>.<key>`; the six summons are the datapack's
`function gscraft:camp_npc_<npc>` (all six: `function gscraft:camp_npcs`).

## 3. The station and the orders

| Command | What it does |
|---|---|
| `/gscraft station show <x y z> [viewer]` | the readout the block would give (the owner's, or a named viewer's: a stranger is refused), the order, the ticks left, lit, every slot |
| `/gscraft station bind <x y z> <name>` | makes the station that player's |
| `/gscraft station load <x y z> <slot> <item> [count]` | puts a stack in a slot (0 card, 1 tool, 2 output, 3-11 inputs) |
| `/gscraft station take <x y z>` | empties the output |
| `/gscraft station clear <x y z>` | empties every slot |
| `/gscraft station list` | the bound stations; the orders and cards loaded |
| `/gscraft items` / `/gscraft item <id>` | the mod's items against items.json / is an id registered |
| `/gscraft drops roll <entity> <n>` | rolls an entity's drop table n times and counts what fell |

Orders are `data/gscraft/gscraft_recipes/recipes.json`; the time classes quick 20 s, intermediate 2:00, equipment 5:00,
trip 20:00, scaled by the setting `station.speed`.

## 4. The sites, the stages and the board

| Command | What it does |
|---|---|
| `/gscraft sites` | every site's state, phase, clock, guard, contested |
| `/gscraft site <id>` | one site described |
| `/gscraft site <id> set unknown|scouted|looted|held` | the next rung (`held` starts the assault from the console, no marker: it always holds at the end); `unknown` resets the site; `defended` is only won at the gate |
| `/gscraft site <id> marker` | the claim marker's claim without the item: the assault, the banner at the anchor, the lamp; at the end the banner must stand and a player be inside, else lost back to looted |
| `/gscraft site <id> clock <seconds>` | sets the running assault's or fortify clock |
| `/gscraft site <id> guard` | tops up and counts the site guard |
| `/gscraft board` | one line per strongpoint: state, clock, garrison. The board's blocks were removed 2026-09-18; this is what it said, as text |
| `/gscraft clock free` / `online` | the site clocks tick with nobody online (tests) / only with players (the default) |
| `/gscraft stages` | every stage set |
| `/gscraft stage add <name>` / `remove <name>` | sets or clears a stage: the tag on every player, the advancement `gscraft:stage/<name>`, the functions a take runs |
| `/gscraft stage check [name]` | is the stage's advancement known to the server (the registry, tools/stages.py) |
| `/gscraft settings [filter]` | every setting in force (`data/gscraft/gscraft_settings/*.json`; `/reload` applies a change) |

The board was removed (owner, 2026-09-18: too much space for too little information). `function gscraft:board_remove` clears its blocks -
only board-coloured blocks, over each board's footprint. The mod runs without `gscraft_board/board.json`; a new display is to be designed.

## 4a. The fire missions

| Command | What it does |
|---|---|
| `/gscraft strike <mortar|artillery|air> <x y z>` | the call a landed grenade would make, from the console (no owner on the rounds): the spotting round, the barrage, or the Cobra's run; refused while the tube is hot |
| `/gscraft strike status` | each grenade ready or hot, the last call, rounds scheduled, runs in the air |
| `/gscraft strike reset` | every cooldown cleared, every scheduled round dropped, any Cobra unloaded |
| `/function gscraft:yard_mortar` | the tube stands in the yard. **The tube's reward only - never run it at a deploy** |
| `/function gscraft:yard_mortar_clear` | the tube taken down (`/gscraft reset quests` runs this) |
| `/gscraft npc place <id>` | **put a survivor where you stand, facing the way you face**, and save it with the world (ids: walker, michael, marshall, tony, tune, james). This is the compound (start) spot |
| `/gscraft npc place <id> building` | the same for where Marshall, Tony, Tune or James go once their building is taken (gatehouse, clinic, clinic, crossing); saved now, used when that stage is set |
| `/gscraft npc place <id> <start\|building> <x> <y> <z> <yaw>` | the same from the console, by coordinates |
| `/gscraft npc list` | every survivor: saved start and building spots, which is in force, where they stand now |
| `/gscraft npc respawn [id]` | put everyone (or one) up again: your saved spot if there is one, else the datapack's computed one |
| `/gscraft npc clear <id> [start\|building]` | forget a saved spot; the computed one stands again after a respawn |
| `/gscraft npc export` | the saved spots as lines, to bake into `tools/camp.py` once they are final |
| `/gscraft journal status <player>` | what the player can start now, the mod's HUD pins for them, their field notes |
| `/gscraft journal pins <player> on\|off` | the mod's pinning of the next quests for that player (the tag `gs_nopins`) |
| `/gscraft journal note <player> <death\|bulky\|vehicle\|infected\|warning>` | write a field note by hand |
| `/gscraft journal check` | whether FTB Quests' API is reachable for the pins |
| `/give @s patchouli:guide_book{"patchouli:book":"gscraft:notebook"}` | the survivor's notebook (the kit gives it at the first join) |

The numbers are settings under `strike.*` (`/gscraft settings strike`); the crews' turret sweep and its focus under fire are `armour.scan_arc`, `armour.scan_period_ticks`, `armour.scan_slew`, `armour.watch_arc`; the bail-out is stress: `armour.stress_hit`, `armour.stress_damage`, `armour.stress_decay`, `armour.stress_bail`. The design is `docs/gscraft-strikes-2026-09-13.md`.

## 5. The director and the zones

| Command | What it does |
|---|---|
| `/gscraft director pause` / `resume` / `stats` | stops or runs the ambient placement; passes, placed, refused, swept, ms per pass, creatures against the ceiling |
| `/gscraft director phantom set|add <x y z>` / `clear` | a stand-in for a player with nobody on (the tests): the director and the clocks treat it as presence |
| `/gscraft director ambient <x y z> <passes>` | director passes at that point (a squad from the zone's pool, out of sight, off the excluded margins) |
| `/gscraft director pass <x z> <passes>` / `passat <x y z> <passes>` | timed passes at the surface / at a stand |
| `/gscraft director census <x y z>` | what stands within the counting box, by kind |
| `/gscraft director survey <x y z> <samples>` | where placements would land from there: open, indoor, underground, visible, reachable |
| `/gscraft director room <x z> <radius>` | the nearest ground-floor room |
| `/gscraft director horrors <x y z>` | places the zone's horrors now |
| `/gscraft director bench <passes>` | full director passes for everyone present, timed |
| `/gscraft director armour <x y z> <vehicle> <riders>` | places a vehicle with its crew facing the way you look, riders 0-8; patrols if a road is under it |
| `/gscraft director armourpick <x z> <n>` | n picks from the zone's own armour compositions |
| `/gscraft director wave <x y z> <tx tz> <vehicle> <boss|none>` | a site-style armour wave from that stand towards the target |
| `/gscraft zones` / `/gscraft zone <x z>` | every zone / the zone at a point: box, cap, pools, garrison, lair, horrors, excluded |
| `/gscraft env <x y z>` | open, indoor or underground at that point |
| `/gscraft garrison <zone> fill|force` | the zone's garrison placed (force: even with nobody near) |
| `/gscraft sweep` / `sweep age <ticks>` | takes back placements further than the sweep range / older than the age |
| `/gscraft hold on|off|status` | freezes every fighter in place |
| `/gscraft locks` | the tower lock rectangles |

Placement rules in force: nothing where a player within `director.hidden_from` (64) can see it; nothing in an
excluded zone or within its `margin` (the compound: 32); the open ring 36-72 blocks, indoors 10-24, underground 8-24.
A vehicle patrols when the block under its stand is road: the road mod's surfaces anywhere, or a zone's listed surfaces
(`gscraft_armour/roads.json`; Skadowsky's streets for now). `/gscraft vehicle hit` with `superbwarfare:custom_explosion`
keeps the crew seated; a vanilla explosion type ejects it.

## 6. Fighters, squads and vehicles

| Command | What it does |
|---|---|
| `/gscraft fighter <entity>` | a fighter's state: rank, role, magazines, grenades, suppression, pose, target, cover, wounds, last hit |
| `/gscraft fighter <entity> hold <x y z> now` / `advance <x y z> now` / `free` | one fighter ordered to hold or advance to a point, or released |
| `/gscraft fighter <entity> squadhold <x y z> now` / `squadadvance <x y z> now` | the same for the whole squad |
| `/gscraft fighter <entity> goto <x y z> now` | walks there |
| `/gscraft squad <entity> form|disband|formation <f>|route <x z x z ...>|patrol` | squads by hand |
| `/gscraft zone <entity>` / `/gscraft armor <entity>` | the body zones and the armour a body wears |
| `/gscraft hit <entity> <zone> <pen>` / `/gscraft wound <entity> <kind>` | applies a hit or a wound (the combat model's test hooks) |
| `/gscraft monitor on <radius>|off|status` | the combat monitor's log around you |
| `/gscraft factions` / `/gscraft ranks` | the factions and their ranks as loaded |
| `/gscraft vehicle status <entity>` | a vehicle: type, health, weapon, crew, route, target |
| `/gscraft vehicle fuel <entity>` | energy |
| `/gscraft vehicle drive <entity> <ticks> [sprint]` | drives it forward that long |
| `/gscraft vehicle input <entity> <which> <on|off>` | a driver input by hand |
| `/gscraft vehicle target <entity> <target|none>` | the turret's target |
| `/gscraft vehicle spawn <type> <faction> [x y z]` | a bare vehicle of that faction (no crew) |
| `/gscraft vehicle crew <entity> <faction>` | mounts a crew of that faction |
| `/gscraft vehicle arm <entity>` | fills its ammunition |
| `/gscraft vehicle route <entity> add <x z>|clear|show` | its patrol route |
| `/gscraft vehicle hit <entity> <damage type> <amount> [attacker]` | applies damage through the vehicle's own rules |

## 7. Other mods' commands the slice uses

| Command | What it does |
|---|---|
| `/ftbquests open_book [#tag or hex id]` | opens the book on that object for the player running it (what a survivor's right-click does) |
| `/ftbquests change_progress <players> reset 1` | wipes a player's team progress (`1` is the whole file); `/gscraft reset quests` runs it for everyone online |
| `/ftbquests reload` | re-reads `config/ftbquests/quests` after `tools/chapters.py --install` |
| `/ftbteams party create` | the five players as one party so progress is shared |
| `/lootr clear <player>` | forgets which containers that player opened (they glow again) |
| `/reload` | datapacks and the mod's data (zones, sites, settings, recipes are read from the jar; functions from the world's datapack) |
| `/function gscraft:<name>` | a datapack function: `camp_npcs`, `camp_npc_<npc>`, `torch_<name>`, `board_remove`, `tower_stage_<n>` |

## 8. Tools that drive these from outside (this machine)

| Tool | What it does |
|---|---|
| `tools/war_phase<N>.py` | the headless tests over RCON (`localtest.Rcon("127.0.0.1", 25575, ...)`); phases 26-36 are the slice's |
| `tools/chapters.py --install` | writes and installs the quest book |
| `tools/board.py` | RETIRED 2026-09-18 with the board; kept for the record, do not run |
| `tools/itemflow.py [--json]` | the item economy audited from the data: what is asked for with no source, dead weight, and what one player expects from the start area's chests against the quests' needs |
| `tools/chests.py <world> --place --apply` | the Lootr chests: `--place` only writes placements into the record, `--apply` is what reaches the local server |
| `tools/camp.py <world>` | the survivors' summons and signs (then copy to the world's datapack) |
| `tools/chests.py <world> --place --apply` | the Lootr containers |
| `tools/stages.py` | the stage advancements from the registry and the recipe cards |
| `tools/items.py` | the items' models, placeholder textures and names |
| `tools/bisectpanel.py cmd "<command>"` | a console command on the live server (the reply is in `/logs/latest.log`) |

TRAP: `localtest.Rcon` loses sync on long multi-entity replies (`execute as @e[...] run data get`): in tests, count with
`execute if entity` instead.
