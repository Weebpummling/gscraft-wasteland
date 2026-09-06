# GSCraft — changing what is on your screen

The pack ships a deliberate layout: one minimap, a readable HUD, and the noisier overlays turned off. This is how to
change any of it, and how to put it back.

Everything here is yours alone. None of it affects the server or anyone else.

---

## 1. What is on your screen, and who owns it

| What you see | Mod | How to change it |
|---|---|---|
| Minimap and the coordinates under it, top-left | Xaero's Minimap | **Alt+Y** for its settings |
| Full-screen map | Xaero's World Map | **M** |
| Waypoints | Xaero's Minimap | **N** to make one here, **U** to manage them |
| Recipe list beside your inventory | EMI | hover an item, **R** for recipes, **U** for uses |
| Food and saturation on the hunger bar | AppleSkin | on by default, nothing to configure |
| Quest book | FTB Quests | **J** |
| Backpack | Sophisticated Backpacks | **G** |
| Team marker you place for others | Ping Wheel | **middle mouse button** |
| Voice chat | Simple Voice Chat | **V** to talk, its own settings button in the pause menu |
| Party frame: portrait, name, health, armour | Sed's Parties | only appears when you are in a party. **F8** highlights party members |
| Weapon ammo and fire mode | TaCZ and Superb Warfare | **B** fire mode, **R** reload, **I** inspect |
| Stamina and movement | ParCool | **Alt+P** for its settings, **Ctrl+P** to switch it off |
| Third-person camera | Leawind's Third Person | **F5** as usual |

Two things are deliberately **off** because they were drawn on top of the minimap: Improved Mobs' purple "Difficulty"
readout, and FTB Chunks' second minimap. Section 4 says how to bring them back if you want them.

---

## 2. The quick wins

**Everything is too big or too small.** Options → Video Settings → **GUI Scale**. It ships on *Auto*, which picks a
size from your window. On a 1080p screen 2 is comfortable; on 1440p or 4K try 3.

**Hide the whole HUD for a screenshot.** **F1**. Press it again to bring it back. **F2** takes the screenshot, and
they land in the instance's `screenshots` folder (in Prism: right-click the instance → **Folder**).

**Turn off the debug overlay** if you opened it by accident: **F3**.

**Move the minimap.** Press **Alt+Y**, then use the minimap's own position and size options. If you would rather set
it exactly, section 5 has the file.

**Change any key.** Options → Controls. Type in the search box at the top to find a binding by name. If two things
share a key, Minecraft shows the clash in red.

---

## 3. Turning single elements off

Most of these live in the game, not in a file.

- **Minimap** — Alt+Y. You can shrink it, square it off, hide the coordinates, or switch it off entirely.
- **Party frame** — it only shows while you are in a party. Nothing to do unless you want it always on, see below.
- **Weapon HUD** — Alt+T opens TaCZ's settings, Alt+O opens Superb Warfare's.
- **Parkour stamina** — Alt+P, or Ctrl+P to disable ParCool altogether.
- **Voice chat icons** — the voice chat settings button in the pause menu, then *Show icons*.

---

## 4. The files, if you want exact control

Open the instance folder first: in Prism, right-click the GSCraft tile → **Folder**. Everything below is under
`.minecraft`. **Close the game before editing**, or your change will be overwritten when it exits.

| Setting | File | What to change |
|---|---|---|
| Minimap position | `config/xaerohud.txt` | the `minimap` line: `x=0;y=0;fromRight=false;fromBottom=false` puts it top-left; set `fromRight=true` for the right-hand side |
| Purple "Difficulty" text | `config/improvedmobs/client.toml` | `"Show Difficulty" = false` → `true` to bring it back; `"Difficulty location"` takes `TOPLEFT`, `TOPRIGHT`, `BOTTOMLEFT`, `BOTTOMRIGHT` |
| Party frame always on | `config/sedparties-client.toml` | `playerRender = "PARTY"` → `"ON"` for always, `"OFF"` for never |
| Second minimap (FTB Chunks) | `local/ftbchunks/client-config.snbt` | `minimap: { enabled: false }` → `true` |
| Parkour prompts | `config/parcool-client.toml` | its own on/off entries |
| Key binds and GUI scale | `options.txt` | one setting per line; easier to change in-game |

A file you edit yourself is never overwritten by a pack update. The pack only writes these once, on a fresh install.

---

## 5. Putting it back the way the pack ships it

Delete the file you changed and launch the game. The updater notices it is missing and downloads the pack's copy
again. That works for any file in the table above.

If you have changed a lot and want a clean slate, delete the instance and install again from the release. Your world
is on the server, so nothing of yours is lost.

---

## 6. If the screen looks wrong rather than badly arranged

**Blocks show as magenta and black squares.** That is a missing model, which means your mod list does not match the
server's. Quit the game fully and launch again so the pack updates. If it persists, see the install guide's section on
upgrading from an older install.

**Text is doubled or overlapping in a corner.** Two mods are drawing in the same place. Work out which by turning one
off in the table above, then move the other.

**The game is unreadably small on a high-resolution screen.** GUI Scale in Video Settings, and raise the font size in
Options → Chat if the chat is the problem.
