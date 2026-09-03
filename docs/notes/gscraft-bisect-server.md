
**GSCraft** — the user's Minecraft server on BisectHosting (games panel = customised Pterodactyl
"Starbase"), node `la308`, API identifier `493d6256` (the billing number 513806 is NOT the API id).
Forge 1.20.1-47.4.10, Java 17, 8 GB. 

**Decisions taken 2026-09-02** (see the two artifacts — Wasteland Server Blueprint
`98c0d7b4-dd8c-418e-a528-e509d1890917`, GSCraft Server Audit `7c1b7a04-810c-4502-97e3-986a01f1f2c4`):
- Version lock **1.20.1 Forge** (TaCZ is Forge-only, capped at 1.20.1). No NeoForge, no Fabric jars.
- **Bottom-up rebuild on the existing instance**, fresh world. Keep-jars are copied off the current
  server, not re-downloaded; only a short list of configs carries (In Control! rules, MobFactions,
  dynamicview, weapon configs). No player has joined since 2026-01-16, so no migration.
- The Hordes is the horde-night engine (not Enhanced Celestials); Immersive Engineering is the one
  tech tree kept; Create and everything fantasy/magic is cut. Full per-jar disposition is in the audit.
- The wipe (mods/, config/, world, etc.) is done by hand in the panel's file manager, after a
  panel backup; Aikar's flags via the Startup tab.

**LOCATION MOVED 2026-09-02 (user: non-legal work must leave the shared/synced folders; `Documents`
on this box is under OneDrive Known Folder Move, MyDocuments resolves into the OneDrive tree):**
everything now lives in **`C:\GSCraft\`** — `tools\` (the scripts, `build\`, `pull\`),
`server-backup\<date>\` (full server root: every directory as a verified zip + every root file,
made by `backup.py`, manifest `backup-manifest.json`). The old `Documents\Minecraft Server Tools`
copy is deleted once nothing runs from it; run scripts from `C:\GSCraft\tools` (`pull\` is
relative to the cwd). The client pack is `C:\GSCraft\tools\build\client\GSCraft-Client.zip`.

**Tool:** `C:\GSCraft\tools\bisectpanel.py` (was `Documents\Minecraft Server Tools\`) — verbs
`servers resources info startup ls cat get put rm mkdir power cmd audit pullmods`. Config with the
token lives at `~\.bisect\config.json`; the script reads it, I never do. Pulled server data sits in
`...\Minecraft Server Tools\pull\` (config.zip 513 files, crash-reports.zip 34, logs.zip 965). The
file is NOT named `bisect.py` — that shadows Python's stdlib `bisect` and breaks `random`.

**THE trap — Git Bash rewrites remote paths (found 2026-09-02, cost half a session):** in the Bash
tool, any argument that looks like a POSIX path (`/mods`, `/`, `/eula.txt`) is converted by MSYS to
`C:/Program Files/Git/mods` before Python runs. The panel then answers `DaemonConnectionException
500` for the nonexistent path — which reads exactly like a node outage. It was never the daemon.
**Always `export MSYS_NO_PATHCONV=1` before calling the tool from Bash**, or use PowerShell. The
script now refuses a drive-letter path on `ls/cat/get/rm/mkdir` with a message naming this.
A real "does not exist" (e.g. `/kubejs`, absent) returns the same 500, so a 500 on a path means
"check the path", never "the node is down" — `resources` and internal calls keep working either way.

**Panel API quirks, all verified:**
- Cloudflare returns error 1010 for Python's default User-Agent — send a browser-style UA.
- `files/contents` is **POST** here (stock Pterodactyl is GET); the tool falls back to the signed
  download route, which works.
- `files/compress` produces a **ZIP** regardless of the name it returns (`.tar.gz`); verify with
  `zipfile`, not gzip. Git Bash `tar` also reads `C:/...` as a remote host — use `/c/...`.

**Harness quoting trap:** in the Bash tool, an unbalanced apostrophe (`Farmer's`) or a backslash
escape (`\\n`) inside a heredoc breaks or mangles the command. Put code and HTML in files with the
Write tool and splice; keep Bash heredocs to plain ASCII without quotes or backslashes.

**Credential rule, applied here:** the user pasted an API key into chat on 2026-09-02; it was
treated as burned, not used, and they rotated it. Never accept a key in chat, never read
`config.json`, never echo the token. `python` on this box IS the firm's document toolchain —
do not install another Python for this project ([[ml-tooling-cpu-only-box]]).

Related: [[link-produced-file-folder]] (folder link + explorer block on every file-touching turn).
