# GSCraft Wasteland — the documents

*Index, 2026-09-13. Start with the system document; everything else is a layer's specification, a record of a decision, or an archive.*

## Start here

- **`gscraft-system-2026-09-13.md`** — THE living description of the game as one system: the loop, every mechanic, the rulings, the stage registry, the reassessment, the vertical slice.
- `../HANDOFF.md` — where things stand on both servers, session by session, and the tools.
- `gscraft-strikes-2026-09-13.md` — the fire missions: the three strike grenades, the rounds the pack has, the quests that earn them, the items pass.
- `gscraft-commands.md` — every `/gscraft` command, the FTB Quests, Lootr and datapack commands the slice uses, and the play-test recipes (reset, armour, the hospital by hand).

## The rules

1. The system document is the living description of the game and is kept current with every build. New design goes into it or into a dated note; not into a new document.
2. The data is the truth of the enemy layer (`mod/src/main/resources/data/gscraft/*`): a document describes intent and is corrected to the data by a dated note, never the other way round.
3. The stage vocabulary is the registry in the system document §5. A document using another name is wrong.
4. A superseded file is moved to `archive/` with a banner, never deleted; a study that was acted on goes to `research/`.

## Living documents, by layer

**The game and the map**

- `gscraft-design-review-2026-09-13.md` — the review that produced the rulings (its §2 order is superseded by the system document).
- `gscraft-map-design.md` — the master intent (draft 6, reconciled by dated notes): the game, the map, the item ladder, the loop, the tower.
- `gscraft-skadowsky-camp.md` — the camp in Skadowsky: the site as measured, the survivors' rectangles, the mast, the routing rule.
- `gscraft-start-compound-2026-09-12.md` — the start in the south compound: the spawn, the gap, Act I building by building.
- `gscraft-objectives-v8.md` — where things live on the map: the three lands, objectives by act, the strongpoints, the tower's parts.
- `gscraft-design-gaps.md` — the gap ledger: open decisions and their answers, carried findings.

**The player layer (designed, not yet built)**

- `gscraft-quests.md` — the 173 quests in seven chapters (stages per the registry).
- `gscraft-onboarding.md` — how the game teaches itself: the first session, the book, the notebook.
- `gscraft-crafting.md` — stations, blueprint cards, timers, the vehicle roster.
- `gscraft-loot-tables.md` — loot tables by building type and by site.
- `gscraft-vendors.md` — the survivors' and keepers' offers, loyalty by tier.
- `gscraft-player-interface.md` — what the player sees and hears: the book, the readout, `gscraft:say`, titles, the board.
- `gscraft-camp-spec.md` — the camp's functions, blocks and readouts for the tools.
- `gscraft-create-and-artillery.md` — Create in the building tiers, the keeper chains, the gun (rehomed 2026-09-13).
- `gscraft-finale.md` — the finale: the Sleeper, the Captains, win and fail.

**The enemy layer (built; the mod and its data are the truth)**

- `gscraft-entities-v8.md` — everyone and everything that moves: factions by land, named enemies, the Machines.
- `gscraft-enemy-review-2026-09-10.md` — the enemy design as accepted under the mod (W1-W15, X1-X7).
- `gscraft-war-mod-design.md` — the enemy system as one mod: what the mod owns and why.
- `gscraft-armour-vehicles-design-2026-09-11.md` — armour as enemies: the crews, patrols, waves, bosses, the damage pass, results §9-§23.
- `gscraft-system-design-pass-2026-09-12.md` — the layers with squads and armour, the threat ladder by act, rulings S1-S10.

**References**

- `gscraft-equipment-inventory.md` — what equipment the pack actually has, from the registry.
- `gscraft-mod-capabilities.md` — what each mod supplies (reconciled: what the mod replaced).

## Notes (tools and operations)

- `notes/gscraft-kubejs-traps.md` — KubeJS traps on this server - read before any script ships; run tools/kubejs_trapscan.py.
- `notes/gscraft-one-click-install.md` — the one-click client install and tools/packwiz_build.py.
- `notes/gscraft-bisect-server.md` — the hosted server and tools/bisectpanel.py.
- `notes/gscraft-entity-inventory.md` — the entity inventory: what the pack can field.
- `notes/gscraft-phase-log.md` — the phase log.
- `notes/live-loadtest-2026-09-11.md` — the live load test (the budget without armour).

## Research records (`research/`)

Studies that were acted on; what came of each is in the system document.

- `research/gscraft-damage-model-feasibility-2026-09-11.md` — built as the mod's damage model (combat/*).
- `research/gscraft-humanoid-ai-feasibility-2026-09-10.md` — built as the fighters' AI (entity/*).
- `research/gscraft-fighter-animation-research-2026-09-12.md` — built in part (A1/A2 animation clips).
- `research/gscraft-fold-in-review-2026-09-10.md` — the KubeJS-to-mod fold-in; done.
- `research/gscraft-enemy-design-2026-09-08.md` — the first enemy design pass; superseded by the enemy review of 2026-09-10 and the mod.
- `research/gscraft-design-review-2026-09-08.md` — the design review of 2026-09-08; its decisions are in the gaps ledger.
- `research/gscraft-sbw-addon-test-2026-09-06.md` — the Frontline/DragonRise compatibility test; the packs shipped.
- `research/gscraft-desert-city-conversion.md` — the 1.12 block conversion of the desert city (the hub, deferred).
- `research/gscraft-road-review-v8.md` — the road rework of v8 (tools roadpatch/roadrelay/roadmask); done in the world.
- `research/gscraft-pomkots-mechs.md` — the Machines' mod; the faction exists, the set pieces are Act IV.
- `research/gscraft-flashlight-and-nvg.md` — acted on: Dynamic Flashlight added 2026-09-04.
- `research/gscraft-underground-network.md` — the sewers and tunnels as a connective layer; not built.
- `research/gscraft-designer-tools.md` — in-game tooling for the map designers.
- `research/gscraft-scale-and-travel.md` — why 10 km; the border ruling.

## Archive (`archive/`)

Superseded. Kept as the record; nothing in them is current.

- `archive/gscraft-design-review-v8.md` — the plateau-era review; its economy findings are carried in the gaps ledger.
- `archive/gscraft-enemies.md` — the first enemy document; superseded by gscraft-entities-v8.md, the enemy review and the mod's data (gscraft_ranks, gscraft_factions).
- `archive/gscraft-map-layout-v6.md` — the v6 placement sheet; the world is v8.
- `archive/gscraft-map-plan-v8.md` — the v8 terrain and road plan; built, the world is the record.
- `archive/gscraft-map-review-v6-raw.md` — the raw v6 review.
- `archive/gscraft-map-review-v6.md` — the v6 review.
- `archive/gscraft-map-review-v7.md` — the v7 review (v7 was rejected).
- `archive/gscraft-map-review-v8-pass4.md` — the v8 issue review and pass 4; done.
- `archive/gscraft-mod-utilization-2026-09-05.md` — the mod utilization audit; superseded by gscraft-mod-capabilities.md.
- `archive/gscraft-mod-utilization-plan.md` — the mod utilization plan; superseded by gscraft-mod-capabilities.md.
- `archive/gscraft-modpack-review.md` — the mod pack review of 2026-09-04; the pack has moved on (packwiz is the record).
- `archive/gscraft-modpack-update-applied-2026-09-05.md` — an update record.
- `archive/gscraft-modpack-updates.md` — an update record.
- `archive/gscraft-structure-plan.md` — the generated-structure prune behind v7/v8; done.
- `archive/gscraft-woods-plan.md` — the Woods plan; superseded by v8.
- `archive/gscraft-poi-coordinates.md` — point-of-interest coordinates of an earlier world build; verify against the v8 world before any use.
- `archive/gscraft-next-steps-plan-2026-09-12.md` — the plan of 2026-09-12; steps 1-3 built, the rest withdrawn by the reassessment (gscraft-system-2026-09-13.md §6).
- `archive/gscraft-server-audit.html` — the server as found (2026-09-01).
- `archive/wasteland-server-blueprint.html` — the original design record.
- `archive/wasteland-district-map.html` — the district map page of the first build.
- `archive/gscraft-foreign-builds-plan.md` — superseded 2026-09-03 by the placement sheet.
- `archive/gscraft-foreign-worlds.md` — the 1.12.2 saves brought across; done.
- `archive/gscraft-incontrol-onjoin-test.md` — In Control is retired.
- `archive/gscraft-rebuild-manifest.md` — the rebuild manifest of the first weeks.
- `archive/gscraft-player-builds.md` — the player builds census; the zones carry the exclusions now.

## Moved files

Older documents and HANDOFF entries refer to these by their old paths.

| Was | Is |
|---|---|
| `docs/gscraft-damage-model-feasibility-2026-09-11.md` | `docs/research/gscraft-damage-model-feasibility-2026-09-11.md` |
| `docs/gscraft-humanoid-ai-feasibility-2026-09-10.md` | `docs/research/gscraft-humanoid-ai-feasibility-2026-09-10.md` |
| `docs/gscraft-fighter-animation-research-2026-09-12.md` | `docs/research/gscraft-fighter-animation-research-2026-09-12.md` |
| `docs/gscraft-fold-in-review-2026-09-10.md` | `docs/research/gscraft-fold-in-review-2026-09-10.md` |
| `docs/gscraft-enemy-design-2026-09-08.md` | `docs/research/gscraft-enemy-design-2026-09-08.md` |
| `docs/gscraft-design-review-2026-09-08.md` | `docs/research/gscraft-design-review-2026-09-08.md` |
| `docs/gscraft-sbw-addon-test-2026-09-06.md` | `docs/research/gscraft-sbw-addon-test-2026-09-06.md` |
| `docs/gscraft-desert-city-conversion.md` | `docs/research/gscraft-desert-city-conversion.md` |
| `docs/gscraft-road-review-v8.md` | `docs/research/gscraft-road-review-v8.md` |
| `docs/notes/gscraft-pomkots-mechs.md` | `docs/research/gscraft-pomkots-mechs.md` |
| `docs/notes/gscraft-flashlight-and-nvg.md` | `docs/research/gscraft-flashlight-and-nvg.md` |
| `docs/notes/gscraft-underground-network.md` | `docs/research/gscraft-underground-network.md` |
| `docs/notes/gscraft-designer-tools.md` | `docs/research/gscraft-designer-tools.md` |
| `docs/notes/gscraft-scale-and-travel.md` | `docs/research/gscraft-scale-and-travel.md` |
| `docs/gscraft-design-review-v8.md` | `docs/archive/gscraft-design-review-v8.md` |
| `docs/gscraft-enemies.md` | `docs/archive/gscraft-enemies.md` |
| `docs/gscraft-map-layout-v6.md` | `docs/archive/gscraft-map-layout-v6.md` |
| `docs/gscraft-map-plan-v8.md` | `docs/archive/gscraft-map-plan-v8.md` |
| `docs/gscraft-map-review-v6-raw.md` | `docs/archive/gscraft-map-review-v6-raw.md` |
| `docs/gscraft-map-review-v6.md` | `docs/archive/gscraft-map-review-v6.md` |
| `docs/gscraft-map-review-v7.md` | `docs/archive/gscraft-map-review-v7.md` |
| `docs/gscraft-map-review-v8-pass4.md` | `docs/archive/gscraft-map-review-v8-pass4.md` |
| `docs/gscraft-mod-utilization-2026-09-05.md` | `docs/archive/gscraft-mod-utilization-2026-09-05.md` |
| `docs/gscraft-mod-utilization-plan.md` | `docs/archive/gscraft-mod-utilization-plan.md` |
| `docs/gscraft-modpack-review.md` | `docs/archive/gscraft-modpack-review.md` |
| `docs/gscraft-modpack-update-applied-2026-09-05.md` | `docs/archive/gscraft-modpack-update-applied-2026-09-05.md` |
| `docs/gscraft-modpack-updates.md` | `docs/archive/gscraft-modpack-updates.md` |
| `docs/gscraft-structure-plan.md` | `docs/archive/gscraft-structure-plan.md` |
| `docs/gscraft-woods-plan.md` | `docs/archive/gscraft-woods-plan.md` |
| `docs/gscraft-poi-coordinates.md` | `docs/archive/gscraft-poi-coordinates.md` |
| `docs/gscraft-next-steps-plan-2026-09-12.md` | `docs/archive/gscraft-next-steps-plan-2026-09-12.md` |
| `docs/gscraft-server-audit.html` | `docs/archive/gscraft-server-audit.html` |
| `docs/wasteland-server-blueprint.html` | `docs/archive/wasteland-server-blueprint.html` |
| `docs/wasteland-district-map.html` | `docs/archive/wasteland-district-map.html` |
| `docs/notes/gscraft-foreign-builds-plan.md` | `docs/archive/gscraft-foreign-builds-plan.md` |
| `docs/notes/gscraft-foreign-worlds.md` | `docs/archive/gscraft-foreign-worlds.md` |
| `docs/notes/gscraft-incontrol-onjoin-test.md` | `docs/archive/gscraft-incontrol-onjoin-test.md` |
| `docs/notes/gscraft-rebuild-manifest.md` | `docs/archive/gscraft-rebuild-manifest.md` |
| `docs/notes/gscraft-player-builds.md` | `docs/archive/gscraft-player-builds.md` |

`docs/maps/` (the world maps and renders) and `docs/renders/` are unchanged; the v8 geography render still draws the plateau camp and is dead until redrawn.
