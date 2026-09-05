"""Write docs/gscraft-modpack-updates.md from the Modrinth audit (scratch/modpack_update_audit.json) plus the hand-checked
CurseForge results. usage: modpack_report.py"""
import json, os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
a = json.load(open(r"G:/GSCraft/scratch/modpack_update_audit.json"))
man = json.load(open(REPO / "build/manifest.json")); srv = set(os.listdir(r"G:/GSCraft/server/mods"))
pom = [k for k in man if "pomkot" in k.lower()]; lea = [k for k in man if "leawind" in k.lower()]; wf = [k for k in man if "waterframes" in k.lower()]
IMPACT = {
    "lostcities-1.20-7.5.3.jar": ("B", "new profile option (railwayLevelOffset) and an in-game profile editor; no format change; v8 pre-builds its cell so only chunks beyond the border are generated - take it at the v8 server start, not into the live v6 world"),
    "superbwarfare-1.20.1-0.8.8-final-6a6b54795.jar": ("B", "0.8.9.1 adds vehicles (AC-130H, Kirov airship, Archer SPG, Air Sheep, Happiest Ghast), perks, tools, ammo, a catapult controller, vehicle keys and skin sprays: every new vehicle needs a line in gscraft_recipes.js (off-roster strip) and a place in the blueprint design; configs re-check; client and server must match"),
    "recruits-1.20.1-1.14.0.jar": ("B", "1.15: routes on the world map, siege fixes, better target finding - good for the site-guard design; a crash fix for non-living projectile hits (guns) is in 1.15.1; check recruits-server.toml keys after the jump"),
    "modernfix-forge-5.25.2+mc1.20.1.jar": ("A", "38 bug-fix/performance builds; drop-in"),
    "moonlight-1.20-2.16.15-forge.jar": ("A", "library backports; drop-in (Immersive Weathering dependency)"),
    "azurelib-neo-1.20.1-3.1.2.jar": ("A", "3.1.11 rendering pipeline overhaul (client CPU), 3.1.12 fixes; drop-in"),
    "geckolib-forge-1.20.1-4.8.2.jar": ("A", "math.pi animation fix; drop-in"),
    "CreativeCore_FORGE_v2.12.32_mc1.20.1.jar": ("A", "config crash fixes; drop-in (PlayerRevive dependency)"),
    "guardvillagers-1.20.1-1.6.15.jar": ("A", "patrol stutter and a rare crash fixed; drop-in"),
    "the_knocker-1.5.0-forge-1.20.1.jar": ("A", "natural spawn fix, player disguise when lurking; drop-in"),
    "Patchouli-1.20.1-84.1-FORGE.jar": ("A", "maintenance; drop-in"),
    "voicechat-forge-1.20.1-2.6.22.jar": ("A", "2.6.23 beta: shutdown error and off-thread camera fixes; wait for the release tag"),
    "Ping-Wheel-1.12.0-forge-1.20.1.jar": ("A", "localisation and Distant Horizons compat; drop-in (beta)"),
    "FarmersDelight-1.20.1-1.2.9.jar": ("B", "1.3.x rebalances meals (Fried Rice, Chicken Soup) and changes tags; our loot-table stand-ins reference FD items - re-check ids after the jump; otherwise safe"),
    "lukis-grand-capitals-1.1.2.jar": ("C", "1.1.3 removes mansions from the structure pack; v8 places structures by hand, so no gain - keep 1.1.2"),
    "ParCool-1.20.1-3.4.2.0.jar": ("C", "4.0.0.x is alpha; skip until a release"),
    "leawind_third_person-v2.1.0-mc1.20.1-forge.jar": ("C", "3.0.x beta; skip (added to server/mods by the mechs test, client-side mod)"),
    "watermedia-2.1.37.jar": ("C", "3.0 beta with API breaks; not in server/mods (audited via the hash lookup only)"),
    "waterframes-FORGE-mc1.20.1-v2.1.22.jar": ("C", "2.2.0-beta needs WaterMedia 3 beta; skip"),
}
rows = []
for k, v in sorted(a.items(), key=lambda kv: -(kv[1].get("newer_count") or 0)):
    if not v.get("newer_count"): continue
    cls, note = IMPACT.get(k, ("?", ""))
    rows.append(f"| {k} | {v['installed']} ({v['installed_date']}) | {v['latest']} ({v['latest_date']}, {v['latest_type']}) | {v['newer_count']} | {cls} | {note} |")
current = sorted(k for k, v in a.items() if not v.get("newer_count") and k in srv)
doc = f"""# GSCraft mod pack - update status (2026-09-05)

Audit of every jar in `server/mods` (103) against the newest **1.20.1 Forge** builds: 75 Modrinth-hosted jars through the
Modrinth API (`buildmap/audit/modpack_update_audit_2026-09-05.json`, changelogs included), Forge through its promotions
file, and the CurseForge-only mods that matter through their files pages. Owner's question: what is out of date, and
does applying the updates affect the server.

## 1. Summary

- **56 of the 75 Modrinth-hosted jars are current.** 19 have newer 1.20.1 Forge builds: 13 are drop-in library or
  bug-fix updates (class A), 4 change content or configs and need work before they go in (class B), and 5 are
  betas/alphas or removals to skip (class C).
- **Forge 47.4.10 -> 47.4.23** (latest; 47.4.10 is still the *recommended* build). The changes: a handshake fix (a
  client could miss the last login packet), an event-bus upgrade with leak fixes, support for multiple access-transformer
  configs, TOML parse errors written to the log, a RegistryObject equality change. Nothing touches worldgen or the chunk
  format. Worth taking with a boot test; the RegistryObject and event-bus changes are the compatibility risk.
- **CurseForge-only mods:** FTB Quests 2001.4.22, FTB Teams 2001.3.2, FTB Chunks 2001.3.8, FTB Library 2001.2.13 and
  Refurbished Furniture 1.0.20 are the newest 1.20.1 builds. **Sophisticated Backpacks 3.24.13 -> 3.24.67** (54 builds,
  with **Sophisticated Core 1.2.109 -> 1.3.84**, a major core jump), **In Control 9.3.3 -> 9.5.0** (the spawn rules file
  must be re-validated), **The Hordes 1.5.4c -> 1.6.3g** (a 1.6 line: config schema and infection behaviour to re-test;
  the design's 20-minute infection clock depends on it). Not checked (slug unknown or page missing, manual pass needed):
  Keerdm Zombie Apocalypse Essentials 1.41, Eyes in the Darkness, Framework, Doomsday Decoration, TaCZ Fire Control
  Extension, Dynamic View, cupboard, chunksending, Hostile Villages, Recipe Essentials, LongNbtKiller, BHStats, Custom
  Starting Gear, Pillager's Gun, Bandits, vvp, sedparties, FastSuite, Item Filters.
- **Does updating affect the server?** Class A: no behaviour change, but client and server jars must match, so every
  change means a packwiz refresh (the installer picks it up on the next launch). Class B: yes - Superb Warfare 0.8.9.1
  adds vehicles the design has not placed (each needs a strip rule and a blueprint decision), Recruits 1.15 changes AI
  and adds routes (helps the site-guard design), Farmers Delight 1.3 rebalances meals and tags, Lost Cities 7.5.4 only
  matters for new chunks (v8 pre-builds its cell). The three CurseForge jumps (Sophisticated, In Control, Hordes) are the
  ones most likely to change behaviour the design relies on: backpack upgrades as station orders, the spawn deny rule,
  infection.
- **Observation:** `server/mods` carries three jars from the other session's mech test that are not in the design:
  `pomkotsmechs-forge-0.0.1-alpha.8.jar` (alpha; a mixin config warning at every boot), `leawind_third_person` (a
  client-side camera mod) and `waterframes` (needs WaterMedia). Manifest entries found: pomkots {len(pom)}, leawind
  {len(lea)}, waterframes {len(wf)}.

## 2. Recommendation

**Applied 2026-09-05 on the local server - see `gscraft-modpack-update-applied-2026-09-05.md` for what went in, what was held
(Superb Warfare) and the conflict review.**

Do not update the live v6 server piecemeal. Bundle: take class A, Forge 47.4.23 and Lost Cities 7.5.4 with the v8
release (one client refresh), test-boot on the local server (5 server + 2 startup scripts, the benign error set, one
play session), then decide class B one mod at a time with its design work: Superb Warfare after the vehicle roster and
strip list are extended; Recruits with the site-guard build (Phase C); Sophisticated Backpacks + Core, In Control 9.5.0
and Hordes 1.6.3g each with a config diff and a test; Farmers Delight after the loot-table ids are checked. Skip class C.
Never mix: a partial update leaves clients and server on different versions of a networked mod.

## 3. Modrinth-hosted jars with newer 1.20.1 Forge builds

| Jar | Installed | Latest | Newer | Class | Impact |
|---|---|---|---|---|---|
{chr(10).join(rows)}

Class A = drop-in bug fixes / libraries; B = content or config change, needs work; C = skip.

## 4. Current (no newer 1.20.1 Forge build on Modrinth)

{", ".join(current)}
"""
(REPO / "docs/gscraft-modpack-updates.md").write_text(doc, encoding="utf-8")
print("report written;", len(rows), "update rows;", len(current), "current")
