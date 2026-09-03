"""Corrections from the manifest resolution: txnilib's real dependent, chaoszpack's hard deps, LC2H 3.5.0,
Immersive Vehicles on Modrinth, the additions' own dependencies."""
import pathlib
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


# ------------------------------------------------------------------ audit
bp = SP / "gscraft-audit-body.html"
b = bp.read_text(encoding="utf-8")

b = rep(b,
        "Nothing in the loaded registry names itself as txnilib\'s dependent — the likely one is <strong>From The Fog</strong>, whose jar is a Forge-and-Fabric universal build and whose <code>watching:check</code> datapack function also fails to load. That is inferred from the jar type, not read from its manifest.</p>",
        "Reading every kept jar\'s <code>mods.toml</code> settled who needs it: <strong>Chunk Activity Tracker</strong>, a minor performance mod, is the only dependent. It is cut, and txnilib leaves with it. (An earlier version of this page guessed From The Fog; the manifest says otherwise. From The Fog\'s failing <code>watching:check</code> function is a separate defect.)</p>")

b = rep(b,
        '<tr><td class="mod">chaoszpack 1.3.7</td><td>Weapons · loot</td><td>The curated TaCZ pack with Lost Cities loot.</td></tr>\n',
        "")
b = rep(b,
        '<tr><td class="mod">AI-Improvements · letmedespawn · LongNbtKiller · chunksending · dynview · chunkactivitytracker · FastFurnace · FastSuite · FastWorkbench · recipeessentials · LeavesBeGone · getittogetherdrops</td><td>Infrastructure</td><td>Performance set, all healthy.</td></tr>',
        '<tr><td class="mod">AI-Improvements · letmedespawn · LongNbtKiller · chunksending · dynview · FastFurnace · FastSuite · FastWorkbench · recipeessentials · LeavesBeGone · getittogetherdrops</td><td>Infrastructure</td><td>Performance set, all healthy. Chunk Activity Tracker is dropped — it is the one jar that requires txnilib.</td></tr>')

b = rep(b,
        '<tr><td class="mod">lc2h 2.1.1</td><td>Pin to the release built against Lost Cities 7.4.x; three of its mixins currently find no target. Set debug off.</td></tr>',
        '<tr><td class="mod">lc2h 2.1.1</td><td>Replaced by LC²H 3.5.0 (April 2026), built against Lost Cities 7.4.x. Set debug off.</td></tr>')

b = rep(b,
        '<tr><td class="mod">From-The-Fog (watching) 1.9.2</td><td>The Man From The Fog (Forge-native)</td><td>Universal Forge/Fabric jar; its datapack function fails; likely the reason txnilib and Fabric API are here.</td></tr>',
        '<tr><td class="mod">From-The-Fog (watching) 1.9.2</td><td>The Man From The Fog 1.4 (Forge-native)</td><td>Universal Forge/Fabric jar whose datapack function fails at load.</td></tr>\n'
        '        <tr><td class="mod">chaoszpack 1.3.7</td><td>TaCZ\'s default gun pack + Keerdm</td><td>Its manifest declares <em>mandatory</em> dependencies on Create, Create Deco, Horror Element Mod, MineTraps and Survival Instinct — five cut mods. Keerdm already carries the Lost Cities loot and structures. Fallback if the pack\'s guns are wanted back: edit its <code>mods.toml</code> to make those optional.</td></tr>\n'
        '        <tr><td class="mod">chunkactivitytracker</td><td>Nothing</td><td>The only mod that requires txnilib (the Fabric API bundle).</td></tr>')

b = rep(b,
        '<tr><td class="mod">cloth-config · architectury · kotlinforforge · fzzy_config · uilib · Atlas Lib · almanac · collective · placebo</td><td>Check each survivor\'s manifest at pin time</td><td>Keep only on a confirmed dependent; otherwise cut</td></tr>',
        '<tr><td class="mod">cloth-config · architectury · Atlas Lib · almanac · placebo</td><td>bettercombat · Factory Blocks, Chisel, KubeJS · The Hordes · Let Me Despawn · the Fast* trio and Apotheosis</td><td>Keep — each confirmed from a kept jar\'s manifest</td></tr>\n'
        '        <tr><td class="mod">kotlinforforge · fzzy_config · uilib · collective</td><td>No kept mod declares them</td><td>Cut</td></tr>')

b = rep(b,
        '<tr><td class="mod">Immersive Vehicles</td><td><span class="chip sup">Absent</span></td><td>Only military vehicles exist (Superb Warfare, MCSP, vvp). No civilian cars, no fuel economy.</td></tr>',
        '<tr><td class="mod">Immersive Vehicles</td><td><span class="chip sup">Absent</span></td><td>Only military vehicles exist (Superb Warfare, MCSP, vvp). No civilian cars, no fuel economy. Resolved: 24.0.0 for 1.20.1 on Modrinth.</td></tr>')

bp.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full)
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched")

# ------------------------------------------------------------------ blueprint
pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")
s = rep(s,
        "<li><strong>Additions</strong>, from the pillar tables: Lootr, Improved Mobs, FTB Chunks, FTB Quests, Canary, Xaero\'s Minimap + World Map, The Man From The Fog, Immersive Vehicles plus one content pack, KubeJS with Rhino, Simple Voice Chat, Apotheosis, Chipped. Each resolved to an exact 1.20.1 Forge build and pinned by filename and hash.</li>",
        "<li><strong>Additions</strong>, resolved on Modrinth to exact 1.20.1 Forge builds and hash-verified into <code>build/mods</code>: Lootr 0.7.35.94, Improved Mobs 1.13.7 (+ TenshiLib), FTB Chunks / Quests / Library / Teams, Canary 0.3.3, Xaero\'s Minimap 26.4.2 + World Map 1.45.0, The Man From The Fog 1.4, Immersive Vehicles 24.0.0, KubeJS 2001.6.5 (+ Rhino, Architectury), Simple Voice Chat 2.6.22, Apotheosis 7.4.8 (+ Apothic Attributes), Chipped 3.0.7 (+ Resourceful Lib), TaCZ 1.1.8-hotfix, LC²H 3.5.0.</li>")
s = rep(s,
        '<tr><td class="mod">Curated TaCZ gun packs</td><td><span class="chip sup">Supporting</span></td><td class="ver">n/a</td><td>Pick two or three packs and stop. Loading every pack available is the fastest way to make loot tables meaningless.</td></tr>',
        '<tr><td class="mod">TaCZ default gun pack + Keerdm</td><td><span class="chip sup">Supporting</span></td><td class="ver">n/a</td><td>The stock pack for the arsenal; Keerdm for Lost Cities loot and apocalypse structures. The server\'s chaoszpack is dropped — its manifest hard-requires five cut mods.</td></tr>')
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")
