# Pomkot's Mechs — can it live in the tech sites without taking over?

*Research note, 2026-09-04 (owner: "see if we can integrate this into the various tech locations, not too
much, but the cyberpunk city could definitely use this"). Sources: the CurseForge page, the Modrinth project
and version API (read 2026-09-04), the 2026-09-02 server audit (`gscraft-server-audit.html`), the jars on
this machine.*

## 1. What the mod is

| Fact | Value |
|---|---|
| Version for us | `pomkotsmechs-forge-0.0.1-alpha.8.jar`, 2026-07-19, **50.7 MB**, Forge 1.20.1 (Modrinth `2rcrhKI8`, CDN-hosted — packwiz can reference it, no redistribution needed) |
| Licence | All Rights Reserved (the author plans MIT/GPL later); referencing the Modrinth file is fine, bundling it is not |
| Dependencies | GeckoLib (we have 4.8.2; the mod was built against 4.4.9 — to test), Cloth Config (have), Architectury (have), **Leawind's Third Person 2.1.0** (a client camera mod every player gets; Mod Menu is Fabric-only) |
| Content | pilotable **PMV01 / PMV01B** (red / black: gatling, pile bunker, vertical missiles, grenade cannon; a construction mode with hammer and shovel); five enemy mechs **PMS01** charger, **PMS02** flier, **PMS03** shooter, **PMS04** missile platform, **PMS05** multi-legged grenadier; one boss **PMB01**, melee, with terrain destruction on Hard when mob griefing is on |
| Obtaining | **no recipes, no loot tables, no natural spawns** — Core Stone items summon (and left-click heal) the vehicles; spawn eggs for the mobs and the boss. Everything is ours to script, which is exactly what the design wants |
| Cost | the author calls it very resource-heavy (their rig: i7-14700F, RTX 4070 Ti Super); alpha builds |
| History here | the 2026-09-02 audit **removed** Pomkot's Mechs, its extension pack and Pomkots World from the inherited pack ("sci-fi drift; alpha; client mixin on the server") and stripped their rules from In Control! and Mob Factions. Coming back is a deliberate reversal, limited to the places below |

## 2. Where it fits, and where it must not

The design's rule of thumb: the wasteland is guns, wrecks and zombies; the **hub** (Novo Expograd, the
cyberpunk city, 6.2 km, Act IV) is the one place that was always "the future", and **FR-06** (the
reactor plaza, "Power and hangar") is the only strongpoint with a tech face. Mechs belong to those two
and nowhere else.

| Place | What appears | How | Why it does not overstay |
|---|---|---|---|
| **The hub — streets** | two **dormant PMS units** as dressing (NoAI, invulnerable, script-placed like the dead vehicles) on the rail spine and the platform | `gscraft:furnish_hub` summons them with `NoAI:1b,Invulnerable:1b` | statues; seen from the plane on the approach, never fought |
| **The hub — ambient** | **PMS01** chargers and **PMS03** shooters, two of each at most, inside the hub rectangle only, replacing a third of the hub's bandit count | In Control! rule keyed to the hub rect (`maxcount` 2 each); Improved Mobs scaling excluded for them | the hub is expedition ground, never held, never counterattacks; nothing mechanical ever walks to the camp |
| **The hub — the set piece** | **PMB01, "the Custodian"**, guarding the phased-array container — the last tower component | spawned once by the loop script when a player first enters the hub's core (the Pantsir plaza); a kill task; per-entity mob griefing **denied** for `pomkotsmechs:*` by a startup-script handler (Forge's `EntityMobGriefingEvent`, the tower lock's mechanism), so the boss wrecks nothing even on Hard | one fight, one place, Act IV; it makes the hub's prize cost something |
| **The team's mech** | **one PMV01B (black)** Core Stone, late: Walker rebuilds it from the Custodian's wreck | a new quest, **W-M2 The pilot** (Act IV): hand in 8 steel frames, 1 large battery pack, 1 reactor control module, after the Custodian is dead → the Core Stone; healed with the Stone (the mod's rule); no second one | it arrives for the finale and the Woods' last quests only; the SW military tier (Humvee, Black Hawk, Bradley) stays the roster's spine |
| **FR-06 — the reactor plaza** | one **dormant PMS04** beside the BMPT and the Strykers | the site dressing pass, NoAI | the visual link: the reactor's technology is the city's; nothing there ever activates |
| Everywhere else | nothing | — | Novo, the plant, the block, the plaza, the Woods, the counterattacks and the finale stay as designed (the Sleeper is the boss) |

Two quests, added on 2026-09-04 (the owner's yes; 138 quests): **J-H1 The custodian** (James, Act IV:
kill the Custodian; gate J7; reward the hub's core opened, `custodian_dead`) and **W-M2 The pilot** (Walker,
Act IV; gate J-H1, W-B3; reward the PMV01B Core Stone). Quest counts would become James 25, Walker 27, 138.

## 3. What has to be true before it goes in

1. **A local test first**: spawn PMB01 and four PMS units in the hub on the local server, measure server
   tick time and a client's frame rate on the weakest player machine we know of. The mod's own warning
   is the reason the audit cut it; the number decides.
2. **GeckoLib compatibility**: the mod pins 4.4.9, the pack runs 4.8.2 — confirmed only by the test.
3. **Leawind's Third Person** goes to every client (packwiz adds it). It changes the third-person camera;
   first person is untouched. Say so in the install guide.
4. **Terrain**: the griefing denial above, and `difficulty=hard` stays (the pack's baseline).
5. **Ammunition**: whether the PMV01's weapons need ammunition items is not documented; the test says.
   If they do, they become Teddy's orders (his chapter already owns explosives).
6. Server side: the audit noted the mod's client camera mixin logs a missing target on the dedicated
   server, harmless.

## 4. Test result and decision (2026-09-04)

The isolated server test (`scratch/mechtest_run.py`: a copy of the pack's server with the two jars, a flat world, PMB01 +
five PMS units + one PMV01B summoned, tick time sampled) got as far as **two clean boots with both mods loaded** — no
mod errors, GeckoLib 4.8.2 accepted, the expected client-camera mixin warning on the dedicated server — but the run was
cut before the summons could be measured: Simple Voice Chat could not bind its UDP port beside the owner's live test
server and shut the test server down, and the owner then stopped the retry because it was interfering with the real
test. **The owner chose to proceed without the tick-time and frame-rate numbers** ("assume it will be fine"); they are
measured on the owner's next play session in the hub instead. The integration went in as written in §2.

## 5. The recommendation as it stood before the test

Yes, at the scale above: the hub gets its guardian, its street furniture and two mechanical enemy
types; FR-06 gets one dormant machine; the team gets one mech, late. Nothing elsewhere changes, so the
wasteland stays a gun-and-zombie world with one city that is stranger than the rest. Adding the mod
(and Leawind) is a client-pack change and the owner's call; the local test in §3 comes before it.

Sources: [CurseForge — Pomkots Mechs](https://www.curseforge.com/minecraft/mc-mods/pomkots-mechs),
[Modrinth — Pomkots Mechs](https://modrinth.com/mod/pomkots-mechs),
[Modrinth — Pomkots Mechs versions](https://modrinth.com/mod/pomkots-mechs/versions),
[CurseForge — Pomkots Mechs Extension Pack](https://www.curseforge.com/minecraft/mc-mods/pomkots-mechs-extension-pack).
