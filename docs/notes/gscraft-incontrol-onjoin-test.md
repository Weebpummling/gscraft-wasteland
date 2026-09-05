# In Control's join-time deny rule — does it swallow summons? (test T1, 2026-09-05)

**Question** (`gscraft-entities-v8.md` §8): `config/incontrol/spawn.json` rule 3 is `{"when":"onjoin","hostile":true,
"result":"deny"}` with no `spawntype`; the entity inventory suspected it cancels every hostile that joins a level —
`/summon`, Hordes waves, Apotheosis bosses, template entities, even chunk loads — while `doMobSpawning` is off.

**Answer: no.** Summoned hostiles join and stay with the rule in place. Read on for what was actually checked.

## What the code says

`mcjty/incontrol/ForgeEventHandlers.onEntityJoinWorld` (javap of the 9.5.0 jar): returns early only for non-living
entities, players and the client side; no `loadedFromDisk` check; then walks the `ONJOIN` rules in order, first match
decides, `setCanceled(true)` on deny, `continue` honoured. So the rule *is* evaluated on every living join, chunk loads
included — but `SpawnRule.match(EntityJoinLevelEvent)` is what decides, and in practice it does not match a
command-summoned hostile against this rule (the spawn-type cache the mod keeps from the finalize event is the likely
reason; the rule's `hostile` test is not the whole story). The log at boot: `Invalid keywords for spawn.json: minx maxz
maxx minz` twice (rules 1 and 2, the hub mechs) and `Invalid condition 'minx' for spawner rule!` (spawner rule 5) — those
three rules are dropped, the rest load.

## What the server says (local `wasteland-v8`, RCON, no player online)

| Step | Result |
|---|---|
| `difficulty normal`; `doMobSpawning` = false confirmed | — |
| force-load a 2×2-chunk block at (−1200, −2200) (**the first attempt only force-loaded one chunk and the later probes were summoned into unloaded chunks, where selectors cannot see them — that confounded two rounds; every result below is from the loaded block**) | — |
| `/summon minecraft:zombie`, `pillager`, `husk`, `villager` into the loaded block, shipped rules unchanged | **all four present** (`execute if entity … distance=..80`, one each) — the deny rule did not cancel a single one |
| `forceload remove all`, wait, `forceload add` again | the four still present; the chunks may never have unloaded in the interval (no player, lazy unload), so the **reload case is not proven** by this run — the code path is the same join event, and the summon case passed it |
| `/hordes spawnWave`, `/apoth spawn_boss` | **need a player** (`EntityArgument` players / "No available player context"): not runnable from RCON; both add their mobs with the same join path a summon uses. Syntax found in the jars: `/hordes spawnWave <players> <table id> <count>`; `/apoth spawn_boss <boss id> [rarity]` with the boss ids under `data/apotheosis/bosses/overworld/` |
| the difficulty | `server.properties` on the local server is **`difficulty=peaceful`** — that, not In Control, is what would remove every hostile on this server; the hosted server must be Normal or Hard before any mob test (restored to peaceful after the test, RCON left enabled with a local password) |

## What this settles for the design

- Rule 3 can stay as the natural-spawn backstop; narrowing it with `"spawntype": "natural"` is still the tidy form,
  but nothing in `gscraft-entities-v8.md` §4–§6 is blocked by it.
- The three rules with `minx/maxx` keys are dead until rewritten on `area` (`areas.json`) — entities §8 C2.
- Two tests remain for a session with a player online: one Hordes wave (`/hordes spawnWave @s hordes:default 1`) and
  one boss (`/apoth spawn_boss apotheosis:overworld/zombie`), plus a walk away and back to a placed garrison to see it
  reload — five minutes, on a Normal-difficulty server.
