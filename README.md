# GSCraft Wasteland

The rebuild of a modded Minecraft server (1.20.1 Forge 47.4.10, ~100 mods) into a post-apocalyptic
Lost Cities wasteland: looter survival, modern weapons and vehicles, blood-moon defence nights, a
light horror layer, and an endgame built around defending named locations rather than holding
everything at once. Five players.

This repository holds the tooling, the configuration, and the documentation. It does not hold the
mod jars, the client pack zip, or any world data; those are pinned by hash and download URL in
`build/manifest.json` and `build/additions.json`.

## Layout

| Path | What |
|---|---|
| `tools/` | The Python tools. `bisectpanel.py` drives the Bisect Hosting (Pterodactyl) panel API; `transplant.py`, `runplan.py`, `fixspawners.py` move player builds between worlds through a block remap; `anvil.py`, `terrain.py`, `runpass.py`, `strongpoints.py` edit terrain (ramps, pads, outlines); `worldscan.py`, `topdown.py`, `scanregion.py`, `buildmap.py` read and render worlds; `pregen.py` drives Chunky; `backup.py` pulls the whole server; `mcping.py` pings the server. |
| `build/` | The pinned mod set (`manifest.json`, `additions.json`), server properties, the Lost Cities profile config, carried mod configs, the server datapack, and the KubeJS scripts. |
| `client/` | The Prism Launcher instance files and the install guide players receive. |
| `buildmap/` | The transplant plan (32 rectangles), the site inventory, and the gap survey. |
| `docs/` | The design blueprint, the audit of the server as found, the district map, and top-down renders of the old and new worlds. |

## Tool notes

- `bisectpanel.py` reads its API token from `~/.bisect/config.json`, never from this repository.
- Run everything with `MSYS_NO_PATHCONV=1` under Git Bash, or from PowerShell: MSYS rewrites
  `/mods`-style panel paths into Windows paths otherwise.
- Terrain edits run on a local copy of the region files with the server stopped, then upload.

## Endgame loop

Take a location and a clock starts: a set time to fortify it before the first attack. Each cycle the
game draws one held location, warns the players, and attacks it; lose it or die and it must be
retaken, win and it stays held with more time to explore. Every location drops the loot that repairs
the radio tower. Repairing the tower starts a countdown; when it ends, waves come to the players'
own base, and the last wave carries the boss. Then the season increments.

The full design is `docs/wasteland-server-blueprint.html`.
