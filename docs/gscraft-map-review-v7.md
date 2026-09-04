# GSCraft Wasteland — world build v7, review

Built and reviewed 2026-09-04 on the local test server (`server\wasteland-v7`; release master
`scratch\worlds\wasteland-v7-final`). v7 is the v6 layout (`gscraft-map-layout-v6.md`) regenerated with the
structure-set pruning (`gscraft-structure-plan.md`, 67 kept sites), the Lost Cities palette fix, the Woods
wilderness rectangle (`gscraft-woods-plan.md`) and the Novo→Woods spur road. Audited by `tools/reviewv6.py`
(every chunk parsed), `tools/roads.py check`, `tools/place_kept.py --verify` and a rectangle scan of the two
pre-existing failure categories. Review passes: reviewv6 1, roads check 1, placement verify 2 (67 + 5), rectangle
scan 1, Woods city scan 2 (the first used a loose fingerprint - see §4).

## 1. How v7 was made

| Step | What | Result |
|---|---|---|
| Pre-generation | 10 km box regenerated from the same seed with `gscraft_worldgen` (16 structure sets at frequency 0) and `gscraft_lcfix` active; the pre-fix inner ring (108,411 chunks) regenerated again after the palette fix | 421,775 chunks, DataVersion 3465 everywhere, 0 Lost Cities `state is null` errors from the fixed lives on |
| Woods | chunks inside x 400…2400, z −3500…−1500 dropped and regenerated under the `woods` profile (cityChance 0, scattered 0, railways off) | 15,876 chunks in 6 min; **0.5 %** of sampled chunks carry a city fingerprint vs **48 %** at the same latitude east - the hits are mineshaft cobwebs and vanilla structures |
| Build | `buildv6.py`: substation/hospital restore, six site pads (Novo, plaza, settlement, hub without outlines), transplants with dy and stacking, smoothing, 24-block clear rings, ramps, six camp pads, gaps | 826 s; edge gap histogram: all 2,256 compared columns at +0, **0 columns** with a gap ≥ 3 |
| Roads | spur routed (search box fix, §4), all five roads laid | 52,134 road columns in 1,109 chunks |
| Structures | `place_kept.py` over the 67 kept sites, then the five Woods sites (two bunkers, outpost, two fog-man houses) | 67/67 and 5/5 verified by block probe |
| In-game | tower stage 0, camp ruins, camp torches, dossiers, Novo and financial furnishing, world spawn 19 94 26 | all executed; 5/5 server + 2/2 startup KubeJS scripts, 0 errors; 63 strip rules, 174 recipes removed |

## 2. Review results

| Check | Result | Reading |
|---|---|---|
| chunks | FAIL (strict rule), pre-existing | 443 region files, 421,775 chunks parse; 43 sections with Y outside −4…19 (23 in v6) - **0 inside any built rectangle or pad**; 5,019 chunks without light and 5,038 without heightmaps = the edited chunks, recomputed on first load |
| palette | PASS | 14 namespaces, nothing outside the pack, no 1.12 legacy names |
| entities | FAIL (strict rule), pre-existing | 1,251 `DUMMY` block entities (Forge's placeholder for a block-entity type it could not load), **0 inside any built rectangle or pad** (539 in v6; the count rose because more chunks were regenerated) |
| sites | PASS | ship boxes empty; every transplant present |
| pads | WARN, decided | Novo, plaza, settlement and hub carry no outline by decision (pads are plain foundations, layout §1); hub 85 % terrain at y 82 - the transplanted city is the rest |
| tower | WARN, intended | the one block above the pad is the camp's diamond magnum torch (`camp_torches`) |
| camp | WARN, small | built columns on the six NPC sites: Marshall 10, Walker 2, Michael 2, Tony 1, Tune 1, James 1 (the v6 rim fix took them from dozens to these; `camp.py` clears what its templates cover) |
| water | WARN, accepted | spur: 4 m of water in one crossing (a causeway); the other four roads dry |
| distances | WARN, decided | plant ↔ FR-06 418 m (owner: "Fine") |
| border | PASS | |

Roads check: buildings on the line spine 94, west 175, runway 201, settlement 48, spur 338 (the spur crosses the
Lost Cities belt north of Novo; the builder never touches built columns, so these are the same pass-throughs as v6);
max step spine 47, west 29, runway 44, settlement 28, spur 39.

## 3. Renders

`scratch\renders_v7\`: the 10 km overview (1 px per 8 blocks) and the site crops (Novo, plaza, sewers, settlement,
airfield, hub, biogen, radio tower). The Woods reads as unbroken forest and lakes with no city colour inside the
rectangle; the spur is the black line from Novo's north gate up through the Lost Cities belt to the Woods' south edge.

## 4. Traps met this build (fixed)

- **Geodes look like streets.** The first Woods scan counted smooth basalt and stone bricks anywhere in the column and
  reported 9 % "city"; amethyst geodes at y −64…30 are smooth basalt. A city scan must skip sections below y 32.
- **Lost Cities persists more than the profile.** `<world>\data\LostCityWorldGenData.dat` holds the street and highway
  modes and `LostCityHighwayData.dat` the highway hubs; a profile switch on an existing world changes city, scatter and
  railway settings only. With no cities inside the rectangle no route runs through it, so the Woods came out clean.
- **The road router had no search box.** A* over the hilly forest wandered across the world, decoding every chunk it
  touched (23 GB, the machine swapping). `roads.py route` now bounds each segment to its bounding box plus 512 blocks
  and stops at the target: the spur routed in seconds (2,352 m, one water cell, three built cells).
- **`Start-Process` on a `.bat` does not spawn java.** The play server is started with `cmd /k start.bat`.

## 5. Client crash found during the flight (fixed, pack-wide)

Parties 2.0-beta-p.7.1 crashes every client at mod setup with Xaero's Minimap 26.4.2
(`NoClassDefFoundError xaero/common/gui/IScreenBase`; Xaero moved the package in 25.3.2; the 2 September rebuild
introduced 26.4.2). Fix: `parties_xaerominimap_fix-1.0.0.jar` (CurseForge project 1589418, one mixin over Parties'
`XMCompatManager`, client-side only, owner-approved 2026-09-04) in the Prism instance, `release-v7\GSCraft-Client.zip`,
the packwiz pack (`build/packwiz/mods/parties-xaerominimap-fix-1-0-0.pw.toml`, side client, hosted on the
`pack-files-2026-09-04` release) and the manifests. Not on the server.

## 6. Open items (design, not defects)

- Phase A visual pass by the owner on this build (the server is up in the visual profile on port 9150).
- Woods custom sites (sawmill, ranger cabin, downed aircraft, hunters' hide) come with `camp.py`.
- Hosted deployment = the owner, HANDOFF §6.

Related: `gscraft-map-review-v6.md`, `gscraft-map-layout-v6.md`, `gscraft-woods-plan.md`, `gscraft-structure-plan.md`.
