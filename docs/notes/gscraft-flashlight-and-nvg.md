# Flashlight and night vision — what the pack has and what to add

*Research note, 2026-09-04 (owner: "find a dynamic flashlight to give to players; is night vision /
thermal part of the pack?"). Sources: the mod jars and gun packs in `G:\GSCraft\server`, the
Modrinth API (project pages and version lists, read 2026-09-04).*

## 1. In the pack today

| Looked for | Found |
|---|---|
| Flashlight / weapon light item | **none.** Lang files across all jars: only lanterns (Chipped), Doomsday Decoration floodlights and streetlamps, IE's flare cartridge. TaCZ default pack: laser sights (`laser_compact`, `laser_lopro`, `laser_peq6`, `laser_peq15`, `nightstick`) and two "white light" sights (illuminated reticles), no weapon light. |
| Night vision for players | **none** as an item. Vanilla Night Vision (potion effect) exists; vvp has `key.vvp.toggle_nvg` — a vehicle-view feature. |
| Thermal | **vehicles only:** vvp's `ThermalVisionHandler` / `ThermalEntityGlowHandler` (`key.vvp.thermal_vision`). No player thermal, no thermal scope in the gun packs. |
| Dynamic-light engine | **none.** The client instance has no Embeddium/Rubidium/Oculus/Sodium and no dynamic-lights mod, so a held torch lights nothing. |

## 2. Candidates (Forge 1.20.1, Modrinth)

| Mod | Version / date | Needs | How it lights | Fit |
|---|---|---|---|---|
| **Dynamic Flashlight** (`dynamic-flashlight`) | 2.1.0-forge, 2026-08-02, `flashlight-2.1.0-forge-1.20.1.jar`, 93 KB | nothing | client-rendered beam that **other players see**; **optional server-side temporary light blocks** along the beam (range, spacing, refresh configurable) so the world is really lit; batteries drain and are consumed, sneak-right-click to reload; no GeckoLib, no shaders | **recommended** — no dependency, both halves of the problem (visible beam, real light), a battery loop that maps onto ours |
| TCT Flashlight (`tctflashlight`) | 5.0, 2025-12-07, 799 KB | **TCTCore** (required) | directional beam, headlamp, lantern, **night-vision goggles** item | second choice: the goggles are a plus, the core dependency and size are minuses; the goggles are a Night Vision effect, which a KubeJS item gives for free |
| Powered Flashlight (`powered-flashlight`) | 1.0.0, 2024-08-09, 78 KB | none (optional Embeddium DL / Lucent) | vanilla mode = light blocks; Forge Energy charging (IE could charge it) | older; vanilla-mode light only, no beam other players see |
| Flashables (`flashables`) | Forge 1.20.1 | none; "NOT compatible with Embeddium" (not in our pack) | a whole dynamic-lights engine (torches, lanterns, froglights emit light when held) + 17-colour flashlights | no: makes every held torch a light and softens the dark the design relies on |
| Flashier Flashlights | Forge 1.20.1 | shaders (shadow mapping) | real shadows | no: shader pack dependency, heavy |
| Another Flashlight Mod, Andy's, MrFEG's, Handheld Moon | Forge 1.20.1 | — | plain light items | no beam, or too bright ("mini moons") |

## 3. Recommendation

1. **Add Dynamic Flashlight 2.1.0** to the pack (both sides: `server/mods` and the client instance,
   `build/manifest.json`, the install guide — every player updates once). Replace the KubeJS
   Night-Vision flashlight of the camp spec with this item in the Custom Starting Gear kit; make its
   battery our **flashlight battery** (crafting §5.6: 1 car battery recharges; Michael and Tune sell
   them for 2). Turn the server-side light blocks **on** with a short range (8–12 blocks) and a slow
   refresh so five beams do not flood the server with light updates; verify the cost on the local
   server with five players (Phase C test).
2. **Night vision = a KubeJS goggles item** (`gscraft:nvg`, Night Vision while worn, battery bar),
   sold only by Tune at loyalty level 2 (vendors doc §6). No mod needed.
3. **Thermal stays vehicle-only** (vvp). Player thermal would delete the dark, and the dark is where
   Eyes in the Darkness, the fog man and the Warden's Darkness pulse live.

Adding a mod changes the pinned set; it is the owner's call and needs the client pack re-issued
(the same step as EMI on 2026-09-03).
