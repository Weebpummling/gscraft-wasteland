# GSCraft Wasteland — the vertical slice reviewed for playability

*2026-09-19. Owner: "Review the entire vertical slice and review to see what we should work on to make it actually
playable." Method: the slice walked as a player would walk it, from the first join to holding the hospital, each step
checked against what the game actually loads — the quest book, the station's orders, the loot and drop tables, the site
and zone data, the mod's code, the local world's region files and a running local server. Nothing here is an opinion about
fun; every line is something the data or the server says. What only a session can tell is listed at the end.*

## The verdict

**The slice cannot be played to its end, and would not survive its first hour.** Builds 0–8 each pass their own phase,
and each phase tests its build in isolation with operator commands standing in for the player. Nobody — no test, and not
I — had walked the chain end to end as a player. Doing that finds four places where a player is stopped outright, and
four more where the hour does not work even if they are not.

## Tier 1 — a player is stopped

| # | Finding | Evidence |
|---|---|---|
| 1 | **The hospital, the slice's climax, cannot be reached by play.** A strongpoint climbs unknown → scouted → looted → held. The claim marker is refused unless the site is already looted ("hospital is unknown; the next rung is scouted"). Nothing a player does scouts or loots a site. | `Loop.advance` has two callers: the operator command `/gscraft site <id> set <state>` and the marker's own claim. No quest task, reward or text mentions the hospital. Phase 35 passes because it sets the rungs by command. |
| 2 | **The player's only gun cannot be reloaded, and there is no other gun.** The kit gives a TACZ Glock 17 with one spare magazine: 34 rounds. | No table, drop, quest reward or station order gives `tacz:ammo`. What bodies and the garage give is `superbwarfare:handgun_ammo` and `rifle_ammo`, another mod's ammunition. No quest rewards a weapon; bodies never drop one by design; `damaged_pistol` is an inert part. The 20 bunker chests in town hold vanilla ores and armour. |
| 3 | **There is nothing to eat**, on Hard, where starvation kills. | No gscraft item has food properties. `canned_goods` carries the tooltip "Food. Apartments are full of it." and cannot be eaten. World food: bread from 10% of scavengers, rotten flesh, kelp. |
| 4 | **A death disarms a player for good.** | `keepInventory` false; the kit is given at the first join only (`SurvivorEvents:119`) and by operator command. PlayerRevive helps a group; a solo death leaves the gun where it fell, and finding 2 applies. |

## Tier 2 — the hour does not work

| # | Finding | Evidence |
|---|---|---|
| 5 | **The town is empty.** The quests send players to "the town's rooms". In the 900-block square around the start there are **144** loot containers: 123 ours (the compound, the junction, the clinic, and about 19 still bound in the old south compound), 20 bunker chests, one mineshaft. Nothing between the compound and the hospital, and **none in the hospital** — the rung "looted" has nothing to loot. | Region files, tallied by loot table. |
| 6 | **One claim marker is forty minutes of station time and a third of the fasteners in the start area**, and a lost assault destroys it. | The order chain, one order at a time: 4 fastener kits, 4 steel frames, a circuit assembly, a wiring harness, then 20 minutes for the marker itself. Raw: 24 scrap, 16 each of bolts, nuts, screws and nails, plus electronics. `Loop.assaultLost`: "the marker is gone and re-crafted". The audit of 2026-09-18 did not count this: it is an item used, not handed in. |
| 7 | **The first objective is a military front.** Outside the north gate is the Dead (`sk_south`, cap 7). The junction, 100 blocks on, is `front_en`: NATO and RUAF squads, cap 5, APCs by design. It is walked into with a pistol, 34 rounds, no armour. The hospital holds the Infected and a Matron's lair, then six assault waves. | `/gscraft zone` at each point. Nothing in the slice improves a player's weapons or armour at any step. |
| 8 | **Closing the gate does nothing.** R0 takes eight sandbags and promises "the north gate is barred". | `compound_closed` is read by nothing: no function, no block, no code. It only unlocks the next quest. |

Also: T2 (Tony's second) opens after T1 alone, but its antiseptic and syringes exist only in the clinic's barrels, in the
north complex, which is enemy ground until `clinic_taken`. It reads as a compound errand and is a raid.

## Tier 3 — rough edges, known

- The director tests only a squad's anchor for line of sight; a squad-mate can be scattered into the open 21 blocks from
  a player (observed 2026-09-18). The owner's "spawning right in front of players", not yet gone.
- Whether a party shares quest progress is unproven: the party mod has an FTB Teams bridge, and it needs two players to see.
- The station can be placed anywhere; the survivors' signs stand at computed spots, not the owner's placed ones.
- 17 items drop or spawn that nothing uses: 13–30% of each building table's rolls. `casings` and `concrete` are orders
  nobody can run and nothing wants.
- Live and local have diverged: live still has the board and a jar that repaints it, the mortar I placed, and a pack one
  build behind its server.

## What the process missed, and why

Every build had a green phase. The slice still does not play, because a phase proves its own build with the operator's
hand on the scale: phase 35 sets `hospital looted` by command and then proves the marker works. That is a correct test of
the marker and says nothing about whether a player can get there. Three times this week a phase had been quietly wrong:
31 was red for five days; 31 and `chests.py` both force-loaded a rectangle the compound had left; and I reported chests
"placed" that were only written to a record. **The missing test is the one that plays the chain**: a fresh world state,
no operator commands except what stands in for a player's hands (give an item, walk to a place), from Wake up to a held
hospital. It would have failed at finding 1 on the day build 8 shipped.

## What to work on, in order

Sized in sessions of mine. The first four make the slice finishable; the rest make it an hour worth having.

1. **Let play move a strongpoint (one session).** Scouted: a player enters the site's box. Looted: a share of the site's
   bound chests opened, or a hand-in to Marshall of something only the site holds. Bind chests in the hospital itself
   (`chests.py`, the `hospital` table is written and unused there). Give the hospital a quest line in Marshall's chapter:
   go and look, bring back, then the marker. This is the slice's spine and it does not exist yet.
2. **Give the player a fight they can have (half a session, plus a decision).** The decision is the owner's: TACZ or
   Superb Warfare for the player's guns. Either the tables and bodies give `tacz:ammo` in the kit gun's calibre, or the kit
   gun becomes a Superb Warfare pistol whose ammunition already drops everywhere. Then one step of progression inside the
   slice: a long gun as a quest reward before the junction, and the armour plates that soldiers already drop made to do
   something.
3. **Food (an hour).** Make `canned_goods` edible — the table already stocks apartments with it and the tooltip already
   promises it. Decide whether water is a thing.
4. **Soften death (an hour, a decision).** Re-issue the pistol on respawn, or turn `keepInventory` on for the slice.
5. **Cut the marker's cost (an hour).** Forty minutes of waiting is not play. The `trip` class at 20 minutes was written
   for a journey, not a craft. Shorten it, and let a lost assault leave the marker standing, damaged, not gone.
6. **Make the gate a gate (an hour).** A function on `compound_closed` that bars the north gate's opening
   (x −835…−830, z −912), so the first thing a player builds is something they can see.
7. **Put loot where the quests send people (one session).** Bind the buildings along the road north: the junction's are
   done; the streets to the hospital have nothing. Unbind the old south compound's 19.
8. **The end-to-end phase (one session, and the one that keeps the rest honest).** Described above.
9. **Then build 9: the session**, the owner and players, an hour from the yard. Only that answers pacing, the pressure at
   the junction, whether the pinned list and the notebook carry a new player, and the tick cost.

## What only a session can tell

How the junction fight feels with whatever answer finding 2 gets; whether forty scavenger kills for the slice's
remaining fasteners is a pleasure or a chore; whether players read the notebook; whether a party shares the book;
spark's tick numbers with a counterattack and an APC on the front.

## Regression suite, run for this review

*Every headless phase run in sequence on the local server (phase 42 needs a client and was not run).*

RUNNING at the time of writing (about five minutes a phase, 42 phases). Results are appended here when it ends.
