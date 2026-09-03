"""Fold the player-build findings into the audit and the blueprint."""
import pathlib
import re
from html.parser import HTMLParser

SP = pathlib.Path(__file__).parent


def balanced(s):
    class P(HTMLParser):
        VOID = {"br", "img", "meta", "link", "hr", "input"}

        def __init__(self):
            super().__init__(); self.st, self.err = [], []

        def handle_starttag(self, t, a):
            if t not in self.VOID: self.st.append(t)

        def handle_endtag(self, t):
            if t in self.VOID: return
            if self.st and self.st[-1] == t: self.st.pop()
            else: self.err.append(t)
    q = P(); q.feed(s); return not q.err and not q.st


def rep(s, old, new):
    assert s.count(old) == 1, old[:80]
    return s.replace(old, new, 1)


# =============================================================================== AUDIT
bp = SP / "gscraft-audit-body.html"
b = bp.read_text(encoding="utf-8")

b = rep(b,
        "<p>There is nothing to migrate and nobody to displace. The world reset the blueprint requires is free.</p>",
        "<p>Nobody to displace — but the world holds player-made sceneries that survive the reset by transplant, not by keeping the map. See <em>Player builds</em> below.</p>")

b = rep(b,
        '<tr><td class="mod">ParCool · bettercombat · sedparties · MagnumTorch · Pillagers Gun</td><td>Optional</td><td>Urban traversal, melee, parties, base spawn-suppression, armed illagers. Each fine on its own; none load-bearing.</td></tr>',
        '<tr><td class="mod">ParCool · bettercombat · sedparties · MagnumTorch · Pillagers Gun</td><td>Optional</td><td>Urban traversal, melee, parties, base spawn-suppression, armed illagers. Each fine on its own; none load-bearing.</td></tr>\n'
        '        <tr><td class="mod">factory_blocks · chisel · antiblocksrechiseled</td><td>Build dependency</td><td>The players\' sceneries are made of these: 511 k Factory Blocks, 96 k Chisel variants, 14 k AntiBlocks. Kept for the blocks; add Chipped so Factory Blocks stays craftable.</td></tr>')

b = rep(b,
        "<li><b>chisel · antiblocksrechiseled · factory_blocks · reddens_stone_lanterns · waterframes</b><span>Decoration that doesn't serve the setting; Factory Blocks' recipes are broken without Chipped anyway.</span></li>",
        "<li><b>reddens_stone_lanterns · waterframes</b><span>Decoration that doesn't serve the setting; the few placed blocks are remapped during the transplant.</span></li>")

b = rep(b,
        '<tr><td class="mod">athena · cryonicconfig</td><td>Chisel, Factory Blocks</td><td>Cut</td></tr>',
        '<tr><td class="mod">athena · cryonicconfig</td><td>Chisel, Factory Blocks</td><td>Keep — their dependents are build dependencies</td></tr>')

builds = """<section>
  <h2>Player builds</h2>
  <div class="h2rule"></div>
  <p>Four worlds were pulled off the server and every region file was read: the July 2025 original (near-empty), the Oct–Dec 2025 world plus a September zip of it that sat in the root, the orphaned root <code>region/</code>, and the live world. Every chunk was decoded to its block palette; chunks were classified as built or generated, clustered into sites, and the two big worlds were matched against each other by content signature.</p>

  <div class="decision">
    <span class="tag">Finding</span>
    <p class="verdict">The live world already holds every old build. Someone transplanted them once before.</p>
    <p>479 old-world chunks reappear in the live world byte-for-byte at chunk offset (+140, +89) — blocks (+2240, +1424) — and another 891 reappear edited. The block the previous admin moved spans old chunks x −84…53, z −64…40; in the live world it is x 56…193, z 25…129. The old world is therefore not a second source of builds, with eleven small exceptions outside that block that never made the trip — among them the beacon and hopper array at old blocks (336…367, −1056…−1025): 253 beacons, 325 hoppers.</p>
  </div>

  <h3>The live player district</h3>
  <div class="tablewrap">
    <table>
      <thead><tr><th>Site</th><th>Blocks (x, z)</th><th>Size</th><th>What it is</th></tr></thead>
      <tbody>
        <tr><td class="mod">Mega-base</td><td class="ver">2192…2575, 400…927</td><td class="ver">436 chunks · 1.03 M placed · 6,425 BEs</td><td>A 17-layer <code>factory_blocks:factory</code> platform (432 k blocks) carrying concrete structures, 964 chiseled bookshelves, 885 sculk sensors, 728 dispensers, a gray-concrete tower and command blocks.</td></tr>
        <tr><td class="mod">Industrial district</td><td class="ver">1904…2367, 864…1135</td><td class="ver">182 chunks · 248 k · 4,071 BEs</td><td>Chisel concrete variants, IE machinery — 1,209 fluid pipes, 636 structural arms, 222 tank blocks — Factory Blocks wireframe and AntiBlocks lighting.</td></tr>
        <tr><td class="mod">Hempcrete compound</td><td class="ver">1568…1887, 1152…1471</td><td class="ver">139 chunks · 101 k · 1,474 BEs</td><td>IE hempcrete brick and concrete with Chisel tiling, 405 ceiling lights, 311 razor wire, furnished interiors.</td></tr>
        <tr><td class="mod">Acacia hall</td><td class="ver">1488…1599, 432…511</td><td class="ver">31 chunks · 78 k</td><td>43 k acacia wood on mossy stone brick.</td></tr>
        <tr><td class="mod">Library</td><td class="ver">2032…2127, 1392…1487</td><td class="ver">21 chunks · 2,010 BEs</td><td>615 signs, 356 barrels, 306 beehives, 302 chiseled bookshelves.</td></tr>
        <tr><td class="mod">Spawn structure</td><td class="ver">0…31, 0…31</td><td class="ver">4 chunks · 8 k</td><td>Warium concrete and armour blocks — the one site whose material is being cut; it is remapped to IE concrete.</td></tr>
        <tr><td class="mod">Village, farms, houses</td><td class="ver">inside the district</td><td class="ver">~20 small sites</td><td>Vanilla builds with Farmer\'s Delight and Refurbished Furniture interiors.</td></tr>
      </tbody>
    </table>
  </div>

  <h3>What the builds depend on</h3>
  <p>Counting only placed blocks — ores, Lost Cities filler (in this pack the city ground is IE hempcrete, millions of blocks of it) and the Backrooms dimension excluded — and only sites that do not repeat elsewhere (the apocalypse packs\' chest-spawner-blast-furnace buildings recur twenty-six times; a player build is one of a kind):</p>
  <ul>
    <li><strong>Kept anyway:</strong> Immersive Engineering 79 k, Superb Warfare 1.1 k, Refurbished Furniture, Farmer\'s Delight, Doomsday Decoration.</li>
    <li><strong>Moved from cut to keep as build dependencies:</strong> <code>factory_blocks</code> 511 k blocks (41 kinds), <code>chisel</code> 96 k (62 kinds), <code>antiblocksrechiseled</code> 14 k (47 kinds).</li>
    <li><strong>Remapped rather than kept</strong> — 9.1 k blocks across Warium (56 kinds, mostly structural concrete and coloured armour), Create Deco catwalks, Create track and cut deepslate, Survival Instinct props, stone lanterns, Moving Elevators, Waterframes, Doggy Talents, Waystones — each mapped to a vanilla or IE block of the same role in <code>remap.json</code>.</li>
    <li><strong>Already missing today:</strong> Spore, DimDoors and Modern Structures blocks in the old world are worldgen from mods removed long ago, not builds.</li>
  </ul>

  <h3>How they move</h3>
  <p>Chunk-level transplant between region files (<code>transplant.py</code>): the live district rectangle — chunks x 56…193, z 24…129, blocks 896…3103 × 384…2079 — is copied into the new world at the same coordinates, plus the spawn structure and one outlier, plus the eleven never-transplanted old sites at the known offset. Block entities, ticks and heightmaps shift with the chunk; structure references are dropped; entities move from the <code>entities/</code> region set; POI files are regenerated. The tool\'s typed NBT round-trips all 29,273 live chunks byte-for-byte, and a four-chunk trial transplant re-scanned with identical signatures.</p>
  <p>The panel offers no backups on this plan (<code>TooManyBackupsException: limit of 0</code>), so the rollback is the complete local snapshot: every world, <code>mods/</code>, <code>libraries/</code>, <code>tacz/</code>, configs, logs and crash reports — about 2.5 GB under <code>Minecraft Server Tools\\pull\\</code>.</p>
</section>

"""
b = rep(b, "<section>\n  <h2>Gaps against the blueprint</h2>", builds + "<section>\n  <h2>Gaps against the blueprint</h2>")

b = rep(b,
        "The only remaining unattributed item is which jar ships the seven Botania recipes.</p>",
        "The only remaining unattributed item is which jar ships the seven Botania recipes.</p>\n  <p><strong>Builds:</strong> all four worlds\' overworld region files read in full — 63 + 16 + 6 + 49 files, 29,273 live chunks — plus the old world\'s nether, Twilight Forest, Backrooms and DimDoors dimensions for the dependency tally. The four <code>[1.21]</code> datapacks were deleted from the live world after it was copied; SBW uniforms and No More Phantoms remain.</p>")

b = rep(b,
        "and one correction pass after the root listing succeeded. No independent review.</p>",
        "one correction pass after the root listing succeeded, and one build-analysis pass whose site classifier was revised three times against the data. No independent review.</p>")

bp.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full), "audit not balanced"
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched:", len(full), "chars")

# =============================================================================== BLUEPRINT
pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")

s = rep(s,
        '<tr><td class="mod">Xaero\'s Minimap + Worldmap</td><td><span class="chip sup">Supporting</span></td><td class="ver">1.20.1</td><td>A city map is unreadable without one. Waypoints are what make district-by-district exploration legible.</td></tr>',
        '<tr><td class="mod">Xaero\'s Minimap + Worldmap</td><td><span class="chip sup">Supporting</span></td><td class="ver">1.20.1</td><td>A city map is unreadable without one. Waypoints are what make district-by-district exploration legible.</td></tr>\n'
        '        <tr><td class="mod">Factory Blocks · Chisel · AntiBlocks Rechiseled · Chipped</td><td><span class="chip sup">Supporting</span></td><td class="ver">1.20.1</td><td>Build dependencies — the blocks the players\' existing sceneries are made of (511 k, 96 k and 14 k placed blocks). Chipped makes Factory Blocks craftable again.</td></tr>')

s = rep(s,
        "<li><strong>Backups → full backup</strong> before anything is wiped. This archive is the rollback.</li>",
        "<li><strong>No panel backup exists or can:</strong> this plan allows zero backup slots. The rollback is the complete local snapshot already taken — every world, mods, libraries, tacz, configs, logs — under <code>Minecraft Server Tools\\pull\\</code>. Nothing on the server is wiped until that folder is confirmed intact.</li>")

s = rep(s,
        "KubeJS with Rhino, Simple Voice Chat, Apotheosis. Each resolved",
        "KubeJS with Rhino, Simple Voice Chat, Apotheosis, Chipped. Each resolved")

s = rep(s,
        '<li><strong>Nothing else moves.</strong> Not the world, not <code>config/</code> wholesale, not <code>defaultconfigs/</code>, <code>logs/</code> or <code>crash-reports/</code>. The orphan configs end here.</li>',
        '<li><strong>The player builds move by transplant, not by keeping the world.</strong> The live player district (chunks x 56…193, z 24…129), the spawn structure, and eleven never-transplanted old-world sites are copied chunk-by-chunk into the new world after it generates, with cut-mod blocks remapped. Details in the audit\'s <em>Player builds</em> section.</li>\n'
        '    <li><strong>Nothing else moves.</strong> Not the world wholesale, not <code>config/</code>, not <code>defaultconfigs/</code>, <code>logs/</code> or <code>crash-reports/</code>. The orphan configs end here.</li>')

s = rep(s,
        "<p>Panel backup. Pull every Keep jar and each carry-over config into a local <code>build/</code>. Resolve the additions. Write <code>manifest.json</code> — filename, version, SHA-256, pillar — and build the client <code>.mrpack</code> from it.</p>",
        "<p><strong>Done:</strong> full local snapshot (all four worlds, mods, libraries, tacz, configs, logs, crash reports); every world scanned; build sites, dependencies, transplant plan and remap table produced; the four 1.21 datapacks removed from the live world. <strong>Remaining:</strong> pull every Keep jar into <code>build/</code> with hashes, resolve the additions, write <code>manifest.json</code>, build the client <code>.mrpack</code>.</p>")

new_phase = """  <div class="phase">
    <div class="num">04</div>
    <div>
      <h3>Transplant the player district</h3>
      <p>With the new world generated and the build-dependency mods installed, run <code>transplant.py</code>: the live district at the same coordinates, the spawn structure, the eleven old-world sites at their known offset, all through <code>remap.json</code>. Regenerate POI; move entities. Then fly it.</p>
      <div class="gate"><b>Gate</b><br>Every planned chunk present in the new region files. Boot log shows no unknown-block warnings except those the remap table deliberately maps to air. The library, the mega-base and the industrial district are walked in game and match the scan inventory.</div>
    </div>
  </div>

"""
anchor = "One profile, set in both the mod config and <code>generator-settings</code>, committed.</div>\n    </div>\n  </div>\n\n"
s = rep(s, anchor, anchor + new_phase)

# renumber phases sequentially in document order
n = [0]
def _renum(m):
    n[0] += 1
    return f'<div class="num">{n[0]:02d}</div>'
s = re.sub(r'<div class="num">\d\d</div>', _renum, s)
assert n[0] == 10, n[0]
assert balanced(s), "blueprint not balanced"
pp.write_text(s, encoding="utf-8")
print("blueprint patched:", len(s), "chars, phases:", n[0])
