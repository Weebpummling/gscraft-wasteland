# Tactical movement and animation for the fighters — research (2026-09-12)

Owner's brief: the fighters should do more with movement, and it should look like it. Look at Expressive Advanced
(https://www.curseforge.com/minecraft/mc-mods/expressive-advanced) and at anything else useful — the aim is
tactical movement on the AI, or a mod that already does it on the server.

Read from the mod pages, the open repositories, and the jars in the pack. Nothing here was tried in the game.

## 1. Where the fighters stand

The behaviour side is largely built: cover with a lean-out, crouch and prone poses, sprint and sidestep, orders,
squads with bounding and fall-back, grenade throws, and (today) a grenade to run from and near misses that count.
What is thin is the *look*: a fighter is a vanilla humanoid model with the two vanilla poses and a gun held in the
vanilla arm pose. It does not shoulder the rifle, does not reload visibly, does not dive to the ground, slide into
cover or lean out of it; the prone is the swim pose lying down. The movement reads on the server; it does not read
in the players' eyes.

## 2. The mods, one by one

**Expressive Advanced** is listed on CurseForge as *Tactical Movement Renewed (Point Blank and TACZ)*. It is a
**first-person player** mod: smooth leaning with rotation, point-aiming, and a crawl for prone, in three builds
(TACZ, Point Blank, generic leaning-only). Client and server, Forge 1.20.1. Its page says: "no third person
animations yet". No API, All Rights Reserved. **It has nothing for NPCs** and cannot run on the server for the AI:
it animates the local player's own view. For *players* it would be the leaning the pack lacks (TACZ already has
the crawl, `EnableCrawl = true`; ParCool in the pack already gives vault, roll, slide). A candidate for the player
side, not this brief.

**TACZ: Npcs** (https://www.curseforge.com/minecraft/mc-mods/tacz-npcs, MIT, source at
github.com/Corrinedev/tacznpcs_refactor) — "fully animated neutral and enemy NPCs with loot tables" that "use TACZ
guns from any addon pack just like a player would", with "full PlayerAnimator and player skin support". Forge and
NeoForge, 1.20.1. Its trick is the one that matters: the NPC is rendered through a **client-side fake player**
(`FakePlayer extends RemotePlayer implements IGunOperator`, linked to the NPC and delegating its gun state), so
TACZ's own third-person gun animations — shoulder, aim, reload, melee, sprint — and PlayerAnimator both treat it
as a player. The server tells clients what to play by entity id (`AnimationPacket`; `ClientAnimationManager`
picks the reload or melee clip, a prone variant included). Its AI is thinner than ours (fire at nearest, alert
allies, a seek-shelter goal, melee). Being MIT, its rendering approach can be adopted line by line.

**Mob Player Animator** (https://www.curseforge.com/minecraft/mc-mods/mob-player-animator, CC0, Forge 1.20.1,
4.4 M downloads) — "an add-on to Player Animator that allows it to work with humanoid mobs". It mixes
PlayerAnimator into `HumanoidModel`, `HumanoidMobRenderer`, `LivingEntityRenderer` and the zombie, piglin, skeleton
and illager models, with an API (`MobAnimationAccess`, `MobAnimationFactory`, `HumanoidModelAccess`, body-part
poses). Our fighters are exactly `HumanoidMobRenderer` + `HumanoidModel`, so with this mod in the pack a keyframe
animation plays on them with no renderer change. It does not know about TACZ's gun animations; those are keyed to
players. Public domain: it can be added to the pack, or its two hundred lines borrowed.

**PlayerAnimator** (already in the pack, `player-animation-lib-forge-1.0.2-rc1+1.20`, MIT) is the engine under
both: Blockbench keyframe animations in the Emotecraft JSON format, loaded from `assets/<mod>/player_animation/`,
played on a `ModifierLayer` with fades and speed modifiers. Its README is explicit that it animates players only
and points custom entities to GeckoLib — which is why the two mods above exist. TACZ ships its compat for it
(`PlayerAnimatorCompat`: lower, upper-loop, upper-once and rotation layers) and the default gun pack carries the
clips (`rifle_default`, `pistol_default`, `minigun` player animations). Those clips are the shouldered rifle, the
aim and the reload the players already see on each other — and they can be ours.

**Dochi's Warfare** (formerly CNPC TACZ Fire, https://www.curseforge.com/minecraft/mc-mods/dochis-warfare) is a
whole authoring toolkit: firearm NPC AI with stances, hearing, cover, ammunition, squad formations and postures, a
pose system, traps, and **passengerless Superb Warfare ground vehicles** with patrol routes, target rules, turret
management and crew seats, driven from an in-game editor. It needs CustomNPCs for the bodies, Superb Warfare at
exactly our build (`0.8.9-final 6effe4385`), and is All Rights Reserved with no API. It is not something to build
on — two enemy AIs in one world, and its bodies are not ours — but it is proof that a Superb Warfare vehicle can be
driven without a passenger, which is the open question of the armour design (`gscraft-armour-vehicles-design`
§7, V1).

**TACZ_MORE_LEVEL** (All Rights Reserved) is six tiers of GeckoLib soldiers with "state machine animations" and
"tactical maneuvering" at the top tiers. It shows the other road — own GeckoLib models with authored animation
sets — which we set aside when the bodies were built, because a GeckoLib body loses the vanilla armour layer that
makes every kit in the pack render. Nothing to take from it.

**Epic Fight** can animate any patched entity from a datapack, but it is a combat overhaul for the players too,
its custom-entity animations are reported broken on servers, and it would sit under TACZ's gun handling. No.

## 3. The way in

Two routes, both on the library the pack already has:

- **A. Mob Player Animator + our own clips.** Add the mod (CC0), author the clips, and play them on the fighters
  from a synced animation state. Small, keeps our renderer, and every clip is ours to make: dive to prone, crawl,
  slide into cover, lean-out, mantle, throw, a hit flinch. What it cannot give is TACZ's gun handling: the rifle
  stays in the vanilla arm pose unless we author shoulder, aim and reload clips ourselves, per weapon class.
- **B. The fake-player proxy, after TACZ: Npcs.** Render each fighter as a client-side player linked to it. TACZ
  then plays its own third-person clips for the fighter's gun — shoulder, aim down the sights, reload, melee, sprint
  — from the gun pack, per weapon, with no authoring; PlayerAnimator is on that fake player natively, so our own
  clips play on the same body. This is what makes a fighter look like it is *using* the rifle. The costs: a proxy
  entity per visible fighter on the client (TACZ: Npcs runs it in the hundreds of thousands of downloads), the
  skin and armour rendering to be carried over to the proxy (it is a player model: our skins and the armour layer
  come for free; the name tag and the hitbox stay on the real entity), and TACZ's own "who is aiming/reloading"
  state (`getSynIsAiming`, `getSynReloadState`) to be fed from our fighter — which is state we already have.

**Recommendation: B, and Mob Player Animator is not needed then.** The gun handling is the single biggest
difference between "a zombie with a gun" and a soldier, and it is already authored in every gun pack we ship,
including the CIBR pack's rifles. Our own tactical clips ride the same body.

## 4. What moves, and what it needs

| move | server side today | animation | new server work |
|---|---|---|---|
| shoulder, aim, fire, reload | done (the gun goal, magazines) | TACZ's clips via the proxy | feed aim/reload state |
| sprint | done | TACZ's sprint clip | none |
| crouch | done (pose) | vanilla crouch on the proxy | none |
| dive to prone, crawl | prone pose; crawl speed | our clip: a dive (0.5 s) then a crawl loop | a `DIVE` state on the way down |
| slide into cover | walks to the spot | our clip; a speed burst for the last three blocks | `SLIDE` state when within three blocks of cover |
| lean out and fire | sidestep to the lean | our clip: a lean of the upper body instead of the step | lean becomes a body tilt, not a position (the LOS check stays) |
| mantle a two-block wall | not possible (step height 1) | our clip | a `MANTLE` move: 0.6 s, the body lerped up and over when the path is blocked by a 2-high obstacle with room beyond |
| throw a grenade | done (reflection on SW) | our clip, upper body | `THROW` state at the windup |
| hit flinch | none | our clip, upper body, 0.3 s | on the model's hit event |
| surprised drop | done (the hold) | the dive clip | none |
| callouts | chat | none | none |

Animation state is one synced byte on the fighter (state id) plus the start tick; the client's proxy plays the
matching clip on a `ModifierLayer` with a fade. Loop clips (crawl) run while the state holds; one-shots (dive,
throw, flinch) play once and the byte clears. Upper-body clips layer over TACZ's lower-body gun stance the way
TACZ layers its own.

## 5. Authoring

Clips are Blockbench animations exported with the Emotecraft plugin as PlayerAnimator JSON, eight to start (dive,
crawl loop, slide, lean left, lean right, mantle, throw, flinch), in `assets/gscraft/player_animation/`. The
CC0 and MIT sources above are the reference for the file shape; TACZ's `rifle_default.player_animation.json` in
the default gun pack is the reference for the layered format. A day of animation work for a first pass; the
quality bar is "reads at fifty metres", not motion capture.

## 6. Order and cost

| step | work | proves |
|---|---|---|
| A1 | the fake-player proxy renderer for Soldier and Scavenger, fed from the fighter's gun state (aiming, reloading, sprinting, the gun in hand); skins and armour on it | a fighter shoulders and aims its rifle, reloads visibly, sprints like a player |
| A2 | the animation state byte and the client player of our clips; the first two clips (dive, crawl) | a pinned fighter dives and crawls |
| A3 | the remaining clips and their states: slide, lean, throw, flinch | the fight reads |
| A4 | the mantle move (server) with its clip | fighters cross two-block rubble |

A1 is the risk and the payoff, a day to a day and a half; A2–A4 a day each plus the authoring. Everything is
client-side rendering and one synced byte, so the server build stays what it is and a client on an older jar
still joins (it sees the vanilla poses).

## 8. Built (2026-09-12, local only)

**A1, the stand-in.** `client/FighterProxy` (a `RemotePlayer` that answers every gun question from the fighter it is
linked to - TACZ syncs a mob's gun state as it does a player's) and `client/FighterProxyRenderer` (every frame the
stand-in is moved onto the fighter: position, both rotations, pose, sprint, crouch, the hurt and death timers; a
player renderer draws it with the fighter's skin, no name tag; the stand-ins are ticked once a client tick for the
walk cycle and the animation layers and dropped with the fighter). `-Dgscraft.proxy=false` on the client draws the
old mob renderer. PlayerAnimator's jar sits in `mod/libs` next to TACZ's (compile only, ignored by git like it).

**A2, our own moves.** One synced byte on Soldier and Scavenger (`entity/Anim`, `entity/Animated`: the move in the
low four bits, a sequence in the high four so a repeat is seen), set on the server by the things that already
happen: `Fighters.stance` plays **dive** on any drop to flat (the gun goal, the wound tick); the gun goal plays
**slide** on the last three blocks into cover at 1.15x the walk (settings `fight.slide_dist`, `fight.slide_speed`; 1.35x overshot the stand spot and cost the cover - phase 8 caught it) and holds
**lean_left / lean_right** while it leans (the side from the lean step against the body's facing); the grenade goal
plays **throw** at its start (the release at its fifteenth tick); a hit that did not lay the body down plays
**flinch**. `/gscraft fighter` reads it as `anim MOVE#seq`; `tools/war_phase14.py` checks the five.

The client (`client/FighterAnims`) holds one PlayerAnimator layer per stand-in at priority 97, above TACZ's four
(93-96), and plays the clip of the move's name from `assets/gscraft/player_animation/tactical.json` when the byte
changes: loops until the byte changes, one-shots to their end with a six-tick blend back into whatever pose is
under them (the clip's stop tick pushed past its end). A clip moves only the bones it names, so the rifle stays
in TACZ's hands through a lean or a flinch. The file is Blockbench's GeckoLib format - the one TACZ's gun packs use -
degrees, bones `head torso right_arm left_arm right_leg left_leg body`, seconds, `catmullrom` for a smooth key.
The six clips are numeric first passes written by hand; the bar is "reads at fifty metres". The crawl needs no clip
of ours: the stand-in lies down through the vanilla swim tilt and TACZ plays its own `lie` / `lie_move` on a
lying player.

Left of the plan: the visual check of A1 and A2 on WarTest (a headless test cannot see a clip), the lean as a body
tilt instead of a sidestep, and A4 (the mantle: `Anim.MANTLE` is reserved).

## 7. For the players themselves

Out of this brief, noted for the owner: Expressive Advanced's leaning and point-aim are the two things a player
cannot do today (TACZ crawls, ParCool vaults, rolls and slides). It is client-and-server, TACZ-specific, and would
go into the pack as a jar like any other — but with All Rights Reserved it has to be served from CurseForge's own
CDN in the manifest, not from our release, and that is a packwiz question before it is a design one.

Sources: [Tactical Movement Renewed on CurseForge](https://www.curseforge.com/minecraft/mc-mods/expressive-advanced),
[TACZ: Npcs](https://www.curseforge.com/minecraft/mc-mods/tacz-npcs) and its
[repository](https://github.com/Corrinedev/tacznpcs_refactor),
[Mob Player Animator](https://www.curseforge.com/minecraft/mc-mods/mob-player-animator) and its
[repository](https://github.com/Thelnfamous1/Mob-Player-Animator),
[PlayerAnimator](https://github.com/KosmX/minecraftPlayerAnimator),
[Dochi's Warfare](https://www.curseforge.com/minecraft/mc-mods/dochis-warfare),
[TACZ_MORE_LEVEL](https://www.curseforge.com/minecraft/mc-mods/tacz-more-level),
[Epic Fight custom entity datapacks](https://epicfight-docs.readthedocs.io/Guides/Entities/page1/).
