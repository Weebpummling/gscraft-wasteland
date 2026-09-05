# GSCraft — In-game tooling for the map designers (research, 2026-09-05)

The five players are also the map's designers and its repair crew (owner, 2026-09-05: "we do need to give the players
the convenience tools back, WorldEdit at least; needed for hand-passed repairs in game and for map designers"). This
note is what exists for Forge 1.20.1, what each costs, and a recommended kit. Availability, sides and versions were
read from the Modrinth API on 2026-09-05; CurseForge cannot be queried from a script, so CurseForge-only tools are
marked for a hand check.

## 1. What a designer does in game

Hand repairs after an art pass (a torn edge, a wrong block, a flooded cellar), dressing a site (props, signs, wrecks),
moving a build a few blocks, copying a structure to a second place, checking light levels where mobs must not spawn,
reading what a block or a block entity is, flying a camera to judge a skyline, and bringing a build made elsewhere
(single-player creative, WorldPainter, a .schem or .nbt) into the live world.

## 2. Already in the pack, at no cost

| Tool | What it gives the designer | Note |
|---|---|---|
| **WorldEdit 7.2.15** (both sides) | selections, `//set`, `//replace`, brushes, `//copy`/`//paste`, `//schem`, undo | op-gated on Forge (no permissions mod): every designer is opped at **level 2**; `op-permission-level=2` so `/op` grants 2, the owner alone at 4 in `ops.json`. WorldEdit writes blocks directly, so the tower and building locks do not stop it — the point of a hand repair |
| **Create 6.0.8** (both) | the **schematic table** and **schematicannon**: a .nbt made anywhere (single-player creative, WorldEdit `//schem save`) is uploaded from the client's `schematics/` folder and the cannon places it block by block from a supplied inventory; the **schematic and quill** captures a build in the live world | the survival-side route for bringing work in; needs gunpowder and blocks, or creative |
| **Xaero's World Map** (client) | the top-down check of an area; waypoints for a fix list | in |
| vanilla `/tp`, `/gamemode`, `/give`, `/setblock`, `/fill`, `/clone`, structure blocks | everything level 2 carries | structure blocks need level 2 too |
| **spark**, **Chunky** | server profiling and pre-generation | server tooling |

## 3. Candidates with a Forge 1.20.1 build

| Tool | Sides | Latest 1.20.1 Forge build | Deps | What it adds | Cost / risk | Verdict |
|---|---|---|---|---|---|---|
| **WorldEdit CUI** (`worldeditcui-forge`) | client only | 1.20+01, 2023-09 | — | the selection box, the brush outline, the polygon points drawn in the world | one client jar; nothing on the server | **add** — WorldEdit without it is blind |
| **Lighty** | client only | 2.1.3, 2024-07 | — | a light-level overlay (where mobs can spawn) | one client jar | **add** — the torch pass at every site and inside the camp outline |
| **Freecam** | client only | 1.2.1, 2025-03 | — | a detached camera to judge a skyline or a roofline | any player can use it to look through walls: a scouting cheat in play | add for the designers, **off by default** in the shipped options (unbound key); a friends-only server can live with it |
| **IBE Editor** | both, optional | 2.2.8, 2023-12 | — | in-game editor for block entities, items and entities (signs, chests, spawners, item NBT, villager data — the six survivors and the keepers can be adjusted in place) | server-side; gated to ops by its config (`permissionLevel`) — verify on install | **add** — the one tool for fixing an NPC or a sign without a datapack round-trip |
| **Jade** | both, optional | 11.13.3, 2026-07 | — | what block / entity is under the crosshair, with mod name | a permanent HUD element, against interface rule 3 | add as **client-optional with the overlay hidden by default** (Jade's own toggle key); designers turn it on |
| **BoccHUD** (MiniHUD port) | client only | 0.1.7, 2024-07 | MaFgLib | coordinates, light overlay, chunk borders, spawn spheres, shape renderers, structure bounding boxes | two client jars | optional — Lighty covers the light pass; take it only if the shape renderer is wanted for radius checks (the torch ellipsoids, the 6 m revive range) |
| **Forgematica** (Litematica port) | client only | 0.1.13, 2025-04 | MaFgLib | ghost-block schematic overlay to build against by hand; **ForgematicaPrinter** is a separate mod and would be a survival cheat | two client jars | optional — Create's schematicannon already places; the overlay helps a hand build match a plan |
| **Effortless Building** | both | 3.11, 2026-04 | — | build modes (line, wall, floor, cube), mirrors, arrays, a radial menu | every player gets it in survival unless its server config limits it; it changes how fast anyone can build inside the claim | **not in play**; a designer-only variant needs its config checked — hold |
| **Construction Wand** | both | 2.11, 2023-08 | — | a wand that extends a face of blocks | a survival item; would need to be op-given (the station-only rule strips its recipes) | hold — WorldEdit does this |
| **BetterF3** | client only | 7.0.2, 2023-11 | Cloth Config (in) | a tidier debug screen | cosmetic | optional |
| **kyoyu** | both, optional | 1.2.0 beta | — | share .litematic files between players on the server | beta | no |
| **WorldEdit Hang Fix** | server | 1.18.2 build only | — | — | not for 1.20.1 | no |

## 4. Not available for Forge 1.20.1 (Modrinth)

- **Axiom** — the strongest in-game editor (painting, blueprints, a real editor UI) has no Forge 1.20.1 build on
  Modrinth (its Forge line starts later; NeoForge/Fabric otherwise). **Hand check on CurseForge** before ruling it out.
- **FTB Ultimine** — area/vein mining, in the FTB family the pack already carries; CurseForge only. Worth the hand
  download: clearing a wrecked interior is the slowest part of a repair. `Create Ultimine` (Modrinth) is its Create addon.
- **Building Gadgets 2** — not on Modrinth under any slug tried; CurseForge only; overlaps WorldEdit.
- **Litematica** proper is Fabric; Forgematica is the port.

## 5. The recommended kit

| Tier | Tools | Where | Hand steps |
|---|---|---|---|
| **1 — now** | WorldEdit (in) + **WorldEdit CUI**; **Lighty**; **IBE Editor**; op level 2 for the designers | CUI and Lighty client-only in `CLIENT_EXTRA_JARS`; IBE Editor both sides (`server/mods`, the pack) | hosted server: `op-permission-level=2`, `/op <designer>`; IBE Editor's jar to the hosted server |
| **2 — on request** | Jade (overlay hidden by default), Freecam (key unbound by default), BoccHUD + MaFgLib | client | none |
| **3 — hand check** | FTB Ultimine (CurseForge), Axiom (CurseForge, if a Forge 1.20.1 build exists) | both | download by hand, hash, release assets |
| **never** | ForgematicaPrinter, Effortless Building in survival, Construction Wand as a survival item | — | they change play, not design |

Rules that go with the kit: a designer in creative or with a wand is a designer, and nothing about the counters,
stations, quests or locks changes; the tools' items never get recipes (the station-only rule stands); the notebook does
not mention them (they are not the players' game); a **Designer** page in `HANDOFF.md` lists the commands and the
schematic round-trip. Every mod added here is a client refresh for everyone (packwiz), so tier 1 is bundled with the
v8 release.
