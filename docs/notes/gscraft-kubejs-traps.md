# KubeJS traps on this server (KubeJS 2001.6.5-build.26, Rhino 2001.2.3-build.10)

2026-09-09. KubeJS on this pack fails **silently** far more often than it fails loudly, and several of the
explanations written into our scripts and docs so far were wrong even where their workaround happened to be
right. This note is the reference: what breaks, how it shows, and the safe pattern, each backed by evidence.

Build 26 is the newest 1.20.1 Forge build, and the Rhino 2001 branch has had no commits since build 10, so
none of this is fixed upstream for us.

**Evidence tags**
- **[G]** reproduced in game, on isolated minimal Forge servers carrying only KubeJS, Rhino and
  Architectury (four probe runs, ids like S01 / V10 / W4b / Q11 refer to those probes)
- **[B]** read in the jar bytecode
- **[R]** reproduced in a raw Rhino harness outside the game (weaker than [G])
- **[D]** KubeJS / Rhino source or issue tracker

Run `python tools/kubejs_trapscan.py` before any KubeJS script ships. It checks every rule below that can be
checked statically, across the server, repo-build, packwiz and client copies.

## 0. House rules

1. **Declare with `var` or `let`.** `const` only at the top level of a function body, or as a `for…of` loop
   variable. Never inside `try`, `if`, loop or any other block. (§2.1)
2. **Call KubeJS `event.cancel()` / `success()` / `exit()` outside every `try`.** Decide inside the try, act
   after it. Forge's own `event.setCanceled(true)` / `setResult(...)` are not affected. (§2.2)
3. **Every `ForgeEvents.onEvent` handler body is wrapped in `try`/`catch`.** An uncaught throw there crashes
   the server. (§1.2)
4. **In startup scripts, log with `console.warn`, never `console.error`,** at least for anything that can run
   before loading completes. (§1.1)
5. **Prefix every top-level name per file** (`gsTL_inRect`, not `inRect`), and give any file that depends on
   another's definitions a `// priority: N` header. All files of one script type share one scope and load
   order is not alphabetical. (§2.5, §2.6)
6. **Wrap Java values before comparing:** `Number(x)`, `String(s)`. (§2.8)
7. **Never write a `//` comment line whose text is `priority …`, `ignore …`, `ignored …`, `packmode …` or
   `requires …`.** It is parsed as a script property. (§2.7)
8. **Test in a harness before trusting any explanation**, including the ones in this repo. (§6)

## 1. Traps that stop or crash the server

### 1.1 Any startup-script error blocks a dedicated server's boot [G][B]

`KubeJS.loadComplete` throws `There were KubeJS startup script syntax errors!` if the startup console
captured **any** error, and on a dedicated server that is an FML crash. `startupErrorGUI` only matters on a
client. Verified triggers:

| Trigger | Result |
|---|---|
| a top-level `const` redeclared by a second startup file | `TypeError: redeclaration of const X`, boot never reaches Done |
| `console.error(...)` at startup load time | `Loaded 1/1 … with 1 errors` → FML crash report, exit 1 |
| `console.warn(...)` at startup load time | harmless |

Server-script errors are different: the failing file is logged and skipped, the rest load, boot continues.
A startup `console.error` inside a handler that only runs after boot (all of ours) was not reproduced as a
crash; use `console.warn` there anyway.

### 1.2 An uncaught throw in a `ForgeEvents` handler crashes the server [G][B]

`ForgeEvents` puts the JS function straight on Forge's event bus with no KubeJS guard, and the bus rethrows.
Probe: one uncaught `throw` in a startup `TickEvent$ServerTickEvent` handler → `Description: Exception in
server tick loop`, crash report, server down. The same throw in `ServerEvents.tick` was logged, the server
lived, and the handler kept being called every tick afterwards.

### 1.3 One throwing KubeJS handler skips the rest for that event [G][B]

When a `ServerEvents` / `EntityEvents` / … handler throws, the error is logged and **every later handler for
that same post is skipped** (Q11: handler B, registered after the throwing handler A, did not run that tick).
In `ServerEvents.recipes` this reads as "half the recipe edits are missing".

## 2. Silent traps

### 2.1 `const` inside any block is broken [G][B]

Rhino compiles a block-level `const` so that it either throws or goes stale, depending on the function it is
in. The name does not matter, and name collisions are **not** the cause.

| Where the `const` is | Result | Probe |
|---|---|---|
| top level of a function or handler body | works | W1 W4a W5a, `gscraft_recipes.js` |
| `for (const x of list)` loop variable | works | Q14 |
| inside `try { }` | **throws `redeclaration of var <name>` every run, first run included** | S01 S04 V01 V04 V17 W4b W5b |
| inside any block (`if`, loop, `{}`) of a function that has a `try`, a nested function or uses `arguments` | **throws** | f4LoopConstNested, W6 |
| inside a loop body of a function with none of those | **keeps its first value**: `0,0,0` instead of `0,10,20` | f4LoopConstPlain, f4WhileConst |
| inside an `if` of a function with none of those | works today; breaks the day anyone adds a `try` or closure | W2 W4c |
| `let` anywhere | works | S02 V02 W4d W8 |
| top-level `const` read from a handler, a function, or another file | works | S07 S08 S17 V06 V07 V15b |

Mechanism [B]: `Interpreter.doSetConstVar` skips the write once the slot is initialised (stale), and
`ScriptableObject.putConstImpl` throws `msg.var.redecl` on the activation path `IRFactory.initFunction`
selects for functions with nested functions (throws).

Behind a `catch (x) {}` this produces a handler that logs its "armed" line and then does nothing — which is
exactly how `gscraft_mech_griefing.js` and `gscraft_tower_lock_native.js` stayed dead for weeks.

### 2.2 `event.cancel()` inside `try`/`catch` is swallowed [G][B]

KubeJS `cancel()`, `success()` and `exit()` work by **throwing** `EventExit`. A JS `catch` around them
catches it (`JavaException: dev.latvian.mods.kubejs.event.EventExit: result`) and the handler returns
normally, so the event is **not** cancelled — the probe creeper survived; the spider cancelled after its try
was removed. Pattern:

```js
EntityEvents.spawned('minecraft:spider', event => {
  var deny = false;
  try { deny = decide(event.entity); } catch (err) { console.error('[gscraft] spider: ' + err); }
  if (deny) event.cancel();          // outside the try
});
```

### 2.3 `EntityEvents.checkSpawn` is inverted and misses scripted spawns [G][B]

It maps to Forge `MobSpawnEvent.FinalizeSpawn`, and on Forge the Architectury result mapping is backwards:

| Handler calls | Probe result |
|---|---|
| `event.cancel()` | **the mob spawns anyway** (zombie present) |
| `event.success()` | the mob is **blocked** (husk absent) |

And it only fires where vanilla finalises a spawn:

| Spawn path | `checkSpawn` fires? | `EntityEvents.spawned` fires? |
|---|---|---|
| `/summon minecraft:zombie x y z` (no NBT) | yes | yes |
| `/summon … {NBT}` | **no** — vanilla skips finalizeSpawn when NBT is given | yes |
| `level.createEntity(id)` + `entity.spawn()` (what `gscraft_area_spawner.js` does) | **no** | yes |

So `checkSpawn` cannot gate the loop's summons, the area spawner, or Hordes' NBT-dressed waves. Use
`EntityEvents.spawned` (or In Control `onjoin`) for "never let this exist", with `cancel()` outside any try.
Open: whether `spawned` also fires for entities loaded back from disk (it exposes no `loadedFromDisk`; the
probe was inconclusive), which would make a `spawned` deny delete persisted mobs on chunk load. Test before
relying on it.

### 2.4 `Math.PI`, `Math.E` and every Math constant are `undefined` [G][B]

`NativeMath.findPrototypeId` covers the 36 methods only; the constants are never found. `Math.random`,
`Math.cos`, `Math.floor` work. It is Rhino's `Math`, not `java.lang.Math` (which the class filter blocks).
Use `KMath.PI` or a literal (`6.283185307179586`). This, not `const`, is what made the area spawner's
positions `NaN`.

### 2.5 All files of one script type share one scope [G][B][D]

`ScriptManager.load` evaluates every file of a type into one scope object.

- a top-level `const`/`let` name declared in two files → the second file fails to load ("redeclaration of
  const"). In **startup** scripts that blocks boot (§1.1).
- a top-level `function` or `var` declared in two files → **silently the last-loaded definition wins for
  every file** (S10/S16: both files' handlers called the second file's `sharedFn`).
- `global` is one static map shared by startup, server and client scripts, never cleared by `/reload`
  [G][B]; it is lost on restart.

### 2.6 Load order is `// priority:` first, then raw directory order [G][B]

Higher `priority` first; ties keep filesystem walk order (a stable sort). On this machine's G: drive (not
NTFS) that is **file creation order** (run 1: `zz_order_first, tt_throw, mm_second, aa_scope`); on NTFS it
is alphabetical; on the host's Linux filesystem it is neither. Subfolders load too (walk depth 10); only
`.js` / `.ts` files load, so `*.js.bak` is ignored. Anything that depends on another file's definition needs
a priority header — and §2.5 means a duplicate helper name can change which copy runs when the host lists
files differently.

### 2.7 `//` comment lines can be script properties [G][B]

Every line whose trimmed text starts with `//` is matched against `key value`. For the keys `priority`,
`ignore`/`ignored`, `packmode` and `requires`, anywhere in the file:

| Comment | Probe |
|---|---|
| `// ignore true` | the file is skipped |
| `// priority high` | `NumberFormatException: "high"`, file fails |
| `// requires nonexistentmod` (mid-file) | the whole file is skipped |
| `// radio tower`, `// Two halves` | harmless |

(The jar research also claimed lines starting with `import` are blanked; that did **not** reproduce.)

### 2.8 Java values are not JS values [G][R]

- **Boxed numbers** (command arguments, `Map` values): `typeof` is `object`; `x === 400` is **false**,
  `x == 400` true, `switch (x)` **misses**; arithmetic works (`x + 12.3` = 412.3). Use `Number(x)` [G].
- **Overloads**: `Integer.valueOf(400)` picked `valueOf(String)` and threw `NumberFormatException: "400.0"`
  — a JS number stringifies as a double [G].
- **Java strings**: block ids and similar are `typeof object` but `=== 'minecraft:air'` is true [G];
  `.length` is the Java method (`s.length()`), and JS `Set.has` / `Map.get` miss them — use `String(s)` [R].
- **Accessors are properties**: `level.dimension` works; `level.dimension()` throws "not a function, it is
  object" [G]. `String(level.dimension) === 'minecraft:overworld'` is true [G]. `String(entity.type)` is the
  registry id [G].
- A missing property is `undefined`; a Java `null` is `null` (`== undefined` true, `=== undefined` false) [R].

### 2.9 Scoping and loops [G][D]

- `var` is **block-scoped**: `if (true) { var bs = 5; } bs` → ReferenceError (Q1, Q1b).
- `var` in a `for` header is rewritten to `let`: the index is undefined after the loop (Q2).
- No per-iteration binding: closures created in `for (var …)` **and** `for (let …)` all see the last value
  (`3,3,3`); `list.forEach(x => …)` gives `0,1,2` (Q3, Q3b, Q3c).
- Two declarations in one `for` header work (Q2b; issue #44 does not apply to build 10).

### 2.10 Reload [G][B]

| | `/reload` | `/kubejs reload startup_scripts` |
|---|---|---|
| server script handlers | cleared and re-registered — **no duplication** (DUP probe) | — |
| `ForgeEvents` listeners | untouched | **refused** ("can't be reloaded"): the *old* code keeps running until restart |
| `server.scheduleInTicks` callbacks | **survive, and run with the old script's closures** (Q12) | — |
| `global` | survives | survives |
| recipes/tags/loot events | re-fired | — |

`scheduleInTicks` from `ServerEvents.loaded` fired on time (Q13), so the "fires early" report did not apply.

## 3. Syntax [G]

| Works | Syntax error (the whole file fails) |
|---|---|
| arrow functions, template literals, `let`, destructuring, `?.`, `??`, `for…of` over arrays and Java lists, two declarations in one `for` header | spread `...`, default parameters `f(a = 1)`, `class` |

The jar research [R] adds, not re-run in game: rest parameters, shorthand/computed object keys, `async`/
`await`, `f?.()` / `a?.[i]`, `??=`, numeric separators, BigInt, optional-catch-binding, regex named groups and
lookbehind fail to parse; `Promise`, `globalThis`, `Array.prototype.flat/flatMap/at`, `Object.fromEntries`,
`String.prototype.replaceAll` are missing at runtime.

## 4. API facts verified for the calls our scripts use [G]

| Call | Fact |
|---|---|
| `server.levels` | **`undefined`**. `server.getAllLevels()` iterates with `for…of` and `forEach` (3 levels) |
| `level.getEntities()` | returns a list (`[]` when empty), iterable with `for…of` — never null |
| `level.getEntitiesWithin(AABB.of(...))` | works; `AABB` is bound in server scripts |
| `server.players`, `server.getPlayers()` | both work, `.length` works |
| `level.getBlock(x,y,z).id` | compares equal to a JS string |
| `level.createEntity(id)` + `setPosition` + `spawn()` | works; fires `spawned`, not `checkSpawn` |
| `EntityEvents.hurt` | is Forge `LivingAttackEvent` (raw pre-armour damage), not `LivingHurtEvent` [B] |
| `ForgeEvents` | startup scripts only; fixed priority NORMAL; never sees an event another listener cancelled [B][D] |
| `Java.loadClass` | allowed except `java.lang.*` (bar the boxed types, String, Object, Iterable…), `java.io`, `java.nio`, `java.net`, `sun`, `io.netty`, ASM/Mixin, FML/modlauncher [B] |

## 5. What this means for GSCraft's scripts today

Scanned with `tools/kubejs_trapscan.py` on 2026-09-09. Line numbers are the `server/kubejs` copy.

| Script | Finding | Effect |
|---|---|---|
| `startup_scripts/gscraft_tower_lock_native.js:19` | `prop()` still has `try { const v = … }` | that copy of `prop` **always returns `null`** |
| startup scope: `prop` in `gscraft_mech_griefing.js`, `gscraft_terrorist_drops.js`, `gscraft_tower_lock_native.js` | one shared function name (§2.5) | the last-loaded copy serves all three files. Locally a working copy loads last; if the host lists `gscraft_tower_lock_native.js` last, **the mech griefing denial and the terrorist cure-drop filter silently stop working** |
| `gscraft_tower_lock_native.js:49, 54, 61` | three `ForgeEvents` handlers with no `try` (fluid place, piston, entity place) | any throw in them crashes the server (§1.2) |
| `server_scripts/gscraft_projectiles.js:50` | iterates `server.levels` | the parked sweep's real fault is `server.levels` being undefined, **not** `getEntities()`; the fix is `server.getAllLevels()` |
| `server_scripts/gscraft_area_spawner.js` | places mobs with `createEntity` + `spawn()` | invisible to `checkSpawn` (§2.3); In Control `onjoin` and `EntityEvents.spawned` do see them |
| `server_scripts/gscraft_tower_lock.js` | `String(level.dimension) === DIM`, `cancel()` outside try | correct |
| `gscraft_recipes.js`, `gscraft_scavenger_neutral.js`, `gscraft_terrorist_drops.js`, `gscraft_mech_griefing.js` (server copy) | no rule hit | correct as written; the last three use Forge `setCanceled`/`setResult`, unaffected by §2.2 |
| `build/packwiz/kubejs` and the client instance | still ship the old `const`-in-`try` `gscraft_mech_griefing.js` and `gscraft_tower_lock_native.js`, and the pre-parking `gscraft_projectiles.js` | stale copies on every player's machine; harmless on a dedicated server (these events fire server-side) but they are the versions someone will copy from |
| hosted server `/kubejs` | carries only `gscraft_recipes.js` and the two `example.js` | none of the repaired scripts is live |

### Recorded explanations that are wrong

The workarounds in these places are mostly right; the stated causes are not, and a wrong cause produces a
wrong rule the next time.

| Claim | Where | What is true |
|---|---|---|
| "`const` **and `let`** inside a handler throw … the name is irrelevant" / "const throws from the first call" | `docs/gscraft-design-review-2026-09-08.md` §4b (lines ~313–330), `gscraft_terrorist_drops.js:27`, `gscraft_scavenger_neutral.js:14`, `gscraft_mech_griefing.js:14`, `gscraft_area_spawner.js:16`, `tools/area_spawner.py:111` | `let` is always safe; `const` fails only inside blocks (§2.1). The design review's CONST/VAR test put `const` inside a `try`, which is why it threw every time |
| "A const declared here reads as undefined from inside a function" | `gscraft_area_spawner.js:18`, `tools/area_spawner.py:113` | top-level `const` reads correctly everywhere (§2.1); the NaN was `Math.PI` |
| "`Math` here is java.lang.Math" | `gscraft_area_spawner.js:29`, `tools/area_spawner.py:124` | Rhino's own `Math` without its constants (§2.4) |
| "A Java Integer in a `+` with a JS double makes Rhino concatenate strings" | `gscraft_area_spawner.js:123`, `tools/area_spawner.py:184` | arithmetic works; `===` and `switch` are what break (§2.8). The `Number()` coercion is still right |
| "`level.getEntities()` returns null in KubeJS 2001" | `gscraft_projectiles.js:4, 37, 51` | it returns a list; `server.levels` is the null (§4) |

`tools/area_spawner.py` generates `gscraft_area_spawner.js`, so its three wrong comments must be fixed in
the generator or they return on the next run.

## 6. Open, not verified in game

- `EntityEvents.spawned` firing for entities loaded back from disk (§2.3) — the probe's entity did not reload
  inside the test window, so it proved nothing either way.
- `console.error` from a startup handler that runs *after* boot counting toward the startup error set.
- JS `Set`/`Map` lookups with Java strings, and long precision above 2^53 — raw Rhino only [R].
- Repeated `removeAllTagsFrom` throwing intermittently (issue #602, 1.19.2) — untested here.

## 7. Safe skeletons

```js
// startup_scripts/gsx_feature.js   ForgeEvents live only here; edits need a restart
// priority: 10
var gsX_Result = Java.loadClass('net.minecraftforge.eventbus.api.Event$Result');   // per-file prefix
function gsX_inRect(x, z) { return x >= 64 && x <= 191 && z >= -144 && z <= -17; }

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityMobGriefingEvent', event => {
  try {                                        // mandatory: an escaped throw crashes the server
    var e = event.getEntity();                 // var or let, never a block-level const
    if (e == null) return;
    if (gsX_inRect(Math.floor(e.getX()), Math.floor(e.getZ()))) event.setResult(gsX_Result.DENY);
  } catch (err) {
    console.warn('[gscraft] griefing: ' + err);   // warn in startup scripts
  }
});
```

```js
// server_scripts/gsy_feature.js   reruns on /reload; handlers do not stack
var gsY_EVERY = 20;
ServerEvents.tick(event => {
  var server = event.server;
  if (server.tickCount % gsY_EVERY !== 0) return;          // 20 calls a second: leave early
  try {
    server.getAllLevels().forEach(level => {               // not server.levels
      var ents = level.getEntities();
      for (var i = 0; i < ents.length; i++) {
        var type = String(ents[i].type);                   // String() before comparing or keying
      }
    });
  } catch (err) { console.error('[gscraft] tick: ' + err); }
});

EntityEvents.spawned('minecraft:spider', event => {
  var deny = false;
  try { deny = Number(event.entity.y) < 0; } catch (err) { console.error('[gscraft] spawned: ' + err); }
  if (deny) event.cancel();                                // outside the try
});
```

Related: `docs/gscraft-design-review-2026-09-08.md` §4b (the first, partly wrong, record of the `const`
fault), `docs/notes/gscraft-incontrol-onjoin-test.md`, `tools/kubejs_trapscan.py`.
