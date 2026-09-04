# One-click install for the GSCraft client — research and recommendation

*Research note, 2026-09-04 (owner: "how to create a one-click install for the mod pack, or at least a very
simple installer"). Sources: Prism Launcher wiki and command-line reference, the Modrinth .mrpack format
article, packwiz documentation, a Modrinth hash lookup of our 97 client jars (`scratch/modrinth_hash_lookup.json`).*

## 1. What "one click" can and cannot be

Three things no installer can remove: the player signs in with their **Microsoft account** once; the game
needs **Java 17** (Prism Launcher 9+ downloads it itself on Windows, so this one is solved by picking Prism);
and about **450 MB** of mods has to come down once. Everything else — installing a launcher, creating the
instance, putting 97 jars, configs, the TaCZ gun packs and KubeJS scripts in place, adding the server —
can be one action. Today's guide is three clicks plus a Drive download; the routes below get to one.

## 2. The routes, checked

| Route | What the player does | Size | Updates | Verdict |
|---|---|---|---|---|
| **A. Today** — Prism instance zip on a link, Add Instance → Import → Browse | install Prism, sign in, download 453 MB, import | 453 MB | a new zip each time, re-import by hand | works; every pack change (EMI, the flashlight) means a re-download |
| **B. `.mrpack` on the GitHub release** — the Modrinth pack format; Prism, Modrinth App and ATLauncher import it directly; Prism also takes `prismlauncher --import <url>` | install Prism, sign in, one import (file or URL) | ~3–5 MB (configs, scripts, gun packs; the jars are downloaded from their hosts) | a new mrpack per release, re-import | **good for the install**; the format allows download URLs only from `cdn.modrinth.com`, `github.com`, `raw.githubusercontent.com`, `gitlab.com` — 69 of our 97 jars are on Modrinth by exact hash; the other 28 (§4) come from our own GitHub release URLs, which the format permits |
| **C. packwiz** — a pack manifest (`pack.toml` + one `.pw.toml` per mod, hosted on GitHub Pages or raw.githubusercontent) and `packwiz-installer-bootstrap.jar` run as the instance's **pre-launch command**; on every launch it downloads only what changed | nothing after the first install | the first launch pulls ~450 MB; later launches pull the diff | **automatic, on every launch** | **the answer to our real problem**: the pack changes weekly, and players should never re-import. Any mod can be a direct URL with a hash, so the 28 non-Modrinth jars are fine. packwiz also **exports an .mrpack** from the same manifest (`packwiz modrinth export`), so B comes free |
| **D. A Windows one-file setup** — a `.cmd` (or signed installer) that downloads Prism's portable zip, writes `portable.txt`, and runs `prismlauncher.exe --import "<GitHub release URL of the instance zip or mrpack>"` | **double-click one file, sign in, press Play** | the cmd is 2 KB; Prism 40 MB; then the pack | via C | **the one click**, for Windows; macOS/Linux keep a three-line manual (install Prism, sign in, import the URL) |
| E. A custom launcher | — | — | — | no: weeks of work, code-signing, updates of the launcher itself; Prism already is the launcher |

Two facts make C+D work together: a **Prism instance export zip carries `instance.cfg`, including the
pre-launch command**, so an instance zip that contains only `packwiz-installer-bootstrap.jar`, the pack URL
in its pre-launch command and `servers.dat` is a few hundred kilobytes and self-installs the whole pack on
first launch; and Prism's `--import` accepts a URL, so the setup file never ships the pack at all.

## 3. Recommendation

1. **Make packwiz the pack's source of truth** (`build/packwiz/` in the repo): `packwiz init` for 1.20.1 /
   Forge 47.4.10, `packwiz modrinth add` for the 69 Modrinth-hosted jars, `packwiz url add` with the GitHub
   release asset URL for the 28 others, `config/`, `kubejs/`, `tacz/`, `defaultconfigs/`, `servers.dat` as
   pack files; `packwiz refresh`; publish the folder on **GitHub Pages** from the repo (the repo is public,
   so `raw.githubusercontent.com` works too). The server side uses the same manifest with `-s server`.
2. **Ship two artefacts per release** on the GitHub release: `GSCraft.mrpack` (exported by packwiz, for
   anyone who prefers Modrinth App / ATLauncher / a manual Prism import) and `GSCraft-Instance.zip` (the
   tiny Prism instance with the bootstrap pre-launch command, 6 GB memory preset, the server entry).
3. **`GSCraft-Setup.cmd`** (Windows) on the same release: downloads `PrismLauncher-Windows-MSVC-Portable-<ver>.zip`
   from Prism's GitHub, unpacks it to `%LOCALAPPDATA%\GSCraft\Prism`, writes `portable.txt`, and runs
   `prismlauncher.exe --import "<release URL>/GSCraft-Instance.zip"`. Prism opens on the import, asks for
   the Microsoft sign-in once, auto-downloads Java 17, and the first Play pulls the pack. A plain `.cmd`
   avoids the ps2exe problem (converted PowerShell exes are routinely flagged by Defender); if an `.exe`
   is wanted later, Inno Setup with a code-signing certificate is the path.
4. Keep the current install guide's Way 2 (official launcher) as the manual fallback; drop the Drive link.

**Player experience after this:** download one small file, double-click, sign in, Play. Every later pack
change reaches them the next time they press Play, with no announcement needed.

## 4. The 28 jars not on Modrinth (they go on our GitHub release as direct URLs)

BHStats, Custom Starting Gear, Eyes in the Darkness, FastSuite, Keerdm Zombie Apocalypse Essentials (TACZ),
LongNbtKiller, Pillagers Gun, The Hordes, Bandits, chunksending, cupboard, Doomsday Decoration, Dynamic View,
Framework, FTB Chunks, FTB Library, FTB Quests, FTB Teams, Hostile Villages, In Control!, Item Filters,
Recipe Essentials, Refurbished Furniture, sedparties, Sophisticated Backpacks, Sophisticated Core, TaCZ fire
control extension, vvp. Most are on CurseForge, but the mrpack format does not allow CurseForge's CDN, and
packwiz's CurseForge route needs an API key and hands the player a browser download for "no-redistribution"
mods — so our own release URLs are simpler and are what the current client zip already does.

## 5. Effort and order

| Step | Effort | Owner |
|---|---|---|
| packwiz manifest for the 109-entry manifest (script it from `build/manifest.json` + the hash lookup) | half a day | this session |
| GitHub Pages for `build/packwiz/` (or raw URLs), release assets for the 28 jars + the TaCZ packs | an hour | this session (release upload is `tools/release_upload.py`) |
| Instance zip with the bootstrap and `GSCraft-Setup.cmd` | two hours | this session |
| Test: a clean Windows user profile, run the cmd, sign in, join the hosted server | one evening | owner |
| Server side: `packwiz-installer-bootstrap.jar -g -s server <pack.toml>` replaces the hand-run `/mods` uploads | later, HANDOFF §6 | owner (panel) |

## 6. Risks

- **Licences.** The mrpack/packwiz route *references* Modrinth files (no redistribution) and hosts only the
  28 jars we already redistribute in the client zip today — no change of posture, but those 28 stay our
  responsibility.
- **Prism version drift.** The setup cmd should pin a Prism release URL and be updated with the pack.
- **Defender.** `.cmd` files show the "unknown publisher" prompt once; an unsigned `.exe` is worse. Say so
  in the guide.
- **Corporate/Mac/Linux players** run the three-line manual route with the same mrpack/instance zip.
- **First launch is slow** (450 MB through the bootstrap); the guide should say "the first Play takes a few
  minutes".

Sources: [Prism Launcher — Import](https://prismlauncher.org/wiki/help-pages/zip-import/),
[Prism Launcher — command-line arguments](https://prismlauncher-prismlauncher.mintlify.app/advanced/command-line),
[Prism Launcher — installing Java](https://prismlauncher.org/wiki/getting-started/installing-java/),
[Modrinth Modpack Format (.mrpack)](https://support.modrinth.com/en/articles/8802351-modrinth-modpack-format-mrpack),
[packwiz — installing with packwiz-installer](https://packwiz.infra.link/tutorials/installing/packwiz-installer/),
[packwiz issue #214 (pre-launch command in the pack)](https://github.com/packwiz/packwiz/issues/214),
[Prism issue #591 (built-in packwiz support)](https://github.com/PrismLauncher/PrismLauncher/issues/591),
[Prism Launcher — custom commands](https://prismlauncher.org/wiki/help-pages/custom-commands/),
[ps2exe false positives (Microsoft Q&A)](https://learn.microsoft.com/en-us/answers/questions/674093/powershell-script-to-exe).
