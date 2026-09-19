# GSCraft Wasteland — the first session, and the deploy that has to come before it

*2026-09-19. The slice review's work order is done on the LOCAL server (steps 1–8; rulings R43–R52). Step 9 is the
session. Live is three builds behind and nothing below has been done there: every line of part 1 waits for the owner to
name live.*

## 1. The deploy (not started; needs the owner's word, an empty server, and `list` first)

In this order. Nothing here uploads a region file, so the 04:00 hash rule is not in play; every world change is a console
command.

| # | What | How | Why the order |
|---|---|---|---|
| 1 | the quest book | `build/ftbquests/quests` → `/config/ftbquests/quests` (data, chapter_groups, chapters) | can go while running; read at the restart |
| 2 | the datapack functions | `gate_close`, `gate_open`, `old_compound_chests_clear`, `yard_mortar_clear`, `board_remove` → the world's `datapacks/gscraft/data/gscraft/functions` | before the restart so they load with it |
| 3 | stop; the mod jar (`mod/build/libs/gscraft-0.1.0.jar`) → `/mods`; start | as `live_journal.py` did | the jar carries SitePlay, the kit, the respawn, the muzzle line, the director's fix, `camp.json`'s gate |
| 4 | the client pack | `build/packwiz`: the same jar for the clients (the notebook's pages and the lang lines are in it), version bumped, pushed | **a client on the old jar will not see the Guns and Armour pages and will show raw keys for the new messages** |
| 5 | the release jar | `pack-files` | with 4 |
| 6 | live's leftovers, by console, after Done + 60 s | `function gscraft:board_remove`; `function gscraft:yard_mortar_clear`; `forceload add -982 -899 -918 -816`, `function gscraft:old_compound_chests_clear`, `forceload remove …` | the board, the mortar I placed, the south compound's 19 chests. **A player may have stored things in one of those chests: ask first** |
| 7 | the containers | `python tools/chests.py <a pulled copy of live's world> --place`, then the record's commands by console | the record must be computed from LIVE's world, not the local one: live's hospital and road have never been scanned, and two barrels there may hold somebody's book as they do locally |
| 8 | checks | `gscraft journal check`, `gscraft survivors`, `gscraft kit`, `gscraft kit respawn`, `gscraft site hospital`, `gscraft zone -830 -880` | |

**Not part of a deploy, ever:** `yard_mortar`, `gate_close` (quest rewards), `site <id> set`, `stage add`.

Step 7 is the only one with real work in it: it needs live's region files pulled (read-only) for the three rectangles.

## 2. What only a player can prove (none of it could be tested headless)

| # | Do this | It should | If it does not |
|---|---|---|---|
| 1 | join fresh (or `/gscraft kit @s`) and hold the Glock | show 17 in the magazine | the gun is empty: `GunData.Ammo` is not how 0.8.9 shows a loaded gun. The 34 rounds still load it - pocket them, press R |
| 2 | right-click the pistol rounds, sneak-right-click the rest, press R | rounds leave the inventory; the gun reloads | the notebook's Guns page is wrong and must be rewritten from what happened |
| 3 | die | wake in the yard with the pistol (17) and the notebook, nothing else; the old kit lies where you fell | `SurvivorEvents.respawn` did not fire: `/gscraft kit respawn @s` gives the same stacks meanwhile |
| 4 | walk into the hospital's grounds (-865…-698, -1312…-1242) in survival | within about five seconds: a gold line, "scouted", and Eyes on it completes | `SitePlay.tick`. `/gscraft site hospital presence 5` is the stand-in |
| 5 | open six different containers in the hospital | the action bar counts "1 of 6" … then a gold line, "looted", What they left completes | `SitePlay.opened` |
| 6 | plant the marker, and lose the assault on purpose | the marker lies on the ground at the anchor (-782, -1277) | |
| 7 | hand in R0's eight sandbags | the north gate fills with sandbags and a fence gate; a Marlin and 32 rounds in the inventory | |
| 8 | hand in the junction | a 6B43 vest and two plates; hold a plate to use it with the vest on and damaged | the refill is Superb Warfare's own; it caps at 30 of the vest's 40 |
| 9 | eat canned goods when hungry | three drumsticks | |
| 10 | two players in one party | see whether one's quest progress shows for the other | unknown: the party mod's FTB Teams bridge was never seen working |

## 3. What to watch, because it changed

- **Enemy fire is more accurate over broken ground than in any session so far** (R51): fighters no longer shoot the rise
  in front of them. If the junction is now unplayable with a pistol and a Marlin, that is where it came from.
- **Nothing should appear in the open in front of you any more** (every member of a placed group is checked now, not only the first:
  the review's suite table, phase 36). If something does, note where you stood and where it appeared.
- **A counterattack on a held hospital now comes to the walled compound** - to the north gate, or round the open
  north-west corner if the gate is barred.
- The ammunition economy is a guess: about 2 pistol rounds a chest in flats and offices, 1.1 a soldier, none from the
  Dead, who cost about four each. Count what you have at the junction.
- Spark's tick numbers with a counterattack and an APC on the front.

## 4. Decisions still the owner's

Water as a need or not. Whether the north-west corner of the compound gets a wall. Whether bodies should drop their
vests more often than 5% now that a vest is a quest reward. `casings` and `concrete`: orders nobody can run.
