# GSCraft — how to join

Minecraft **1.20.1**, Forge **47.4.10**, about 100 mods. Everything you need is in one zip.
Two ways in. The first is one file; the second is for people who insist on the official launcher.

Server address: **199.115.76.82:9150** (also `gamesla308.bisecthosting.com:9150`). It is already in your server list after either install.

---

## Way 1 — one file (Windows, ~2 minutes of clicking)

1. Download the zip from the release page
   https://github.com/Weebpummling/gscraft-wasteland/releases/tag/client-installer-2026-09-04, unzip it, and double-click **`GSCraft-Setup.cmd`**.
   Windows may show "unknown publisher" — choose *Run anyway*. It installs Prism Launcher (portable, into
   `%LOCALAPPDATA%\GSCraft`) and imports the GSCraft instance.
2. Prism opens and asks you to **sign in** with your Microsoft account (your normal Minecraft account). Java 17 is
   downloaded by Prism itself.
3. Press **Play** on the GSCraft tile. The first launch downloads the pack (about 450 MB) and then starts the game;
   every later launch checks for pack updates in a few seconds and starts. **Multiplayer → GSCraft → Join Server.**

Already have Prism, or on macOS / Linux: install Prism, sign in, **Add Instance → Import → Browse**, and pick
`GSCraft-Instance.zip` from the unzipped download (self-updating) — or `GSCraft.mrpack` for a one-shot import (also
works in Modrinth App / ATLauncher).

**Memory:** the instance is preset to 6 GB. On an 8 GB PC: right-click the tile → **Edit → Settings → Java → Maximum
memory allocation** and set **4096 MB**.

Voice chat (Simple Voice Chat, push-to-talk **V**) works out of the box on the same address.

Flashlight (Dynamic Flashlight): right-click to switch it on; sneak + right-click while holding a battery to reload it.

Third person (Leawind's Third Person, needed by the mechs in the city): F5 now gives an over-the-shoulder camera; first person is unchanged.

---

## Way 2 — official Minecraft launcher (Windows, one file, but updates are manual)

1. Run the official Minecraft launcher once with plain **1.20.1** selected, so the game files exist, then close it.
2. From the release zip, double-click **`GSCraft-VanillaLauncher.cmd`**. It installs a private Java 17, Forge 47.4.10,
   and the GSCraft pack into `%APPDATA%\.minecraft`, and sets the Forge profile to 6 GB. If a `mods` folder with other
   mods is already there, empty it first — foreign mods will get you rejected by the server.
3. **Play** with the **GSCraft (forge)** profile, then **Multiplayer → GSCraft → Join Server**.
4. **Updates:** the official launcher cannot update the pack by itself. When the pack changes (we will say so),
   double-click the same file again; it only downloads what changed.

---

## If something goes wrong

| Symptom | Fix |
|---|---|
| “Incompatible FML modded server” / missing or extra mods listed | Your `mods` folder is not exactly the one in the zip. Delete it and copy it again from the zip. |
| Game closes at once with a Java error | Wrong Java. It must be Java **17** (Prism: Settings → Java; official launcher: the Forge profile's Java executable). |
| Very low FPS or out-of-memory crash | Raise memory to 6 GB if the PC has 16 GB; lower render distance to 8 in Video Settings. |
| Cannot hear anyone | Voice chat key is **V** (push to talk). Settings → Controls → Simple Voice Chat lets you switch to voice activation. |
| Want to point at something | Ping Wheel: **mouse button 5** by default places a marker everyone in the team sees for a few seconds; rebind under Controls → Ping Wheel. |
| What does this item do | EMI: hover it and press **R** for recipes, **U** for uses. Note: most recipes are made at the camp's stations, not a crafting table. |
| Server shows “Can't connect” | The server restarts a few times a day for maintenance; wait a minute and retry. If it stays down, message the admin. |

## What is in the pack (short version)

Lost Cities ruined-city world, TaCZ and Superb Warfare guns and vehicles, Immersive Engineering tech, The Hordes blood-moon nights, Lootr instanced loot, FTB Quests progression, Xaero maps (press **M**), EMI as the recipe viewer (hover an item and press **R**), Ping Wheel to mark a spot for the team (default **mouse button 5**, rebind it under Controls if your mouse has none), and a light dose of horror. The rules of the server are in the quest book (press the quest-book key or open it from the inventory).
