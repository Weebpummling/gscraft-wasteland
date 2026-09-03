"""Transplant landed on the server; cleanup pass (spawners, legacy entities, loot tables); mason table fix."""
import pathlib, re
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
pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")
s = rep(s,
    "<p>With the new world generated and the build-dependency mods installed, run <code>runplan.py</code>: the live district at the same coordinates, the spawn structure, and 29 old-world sites at their known offset, all through <code>remap_full.json</code> (354 mappings). The dry run over all 32 rectangles — 14,430 chunks — is already clean: every block resolves in the new pack. Regenerate POI; move entities. Then fly it.</p>",
    "<p><strong>Done 2026-09-02 16:40.</strong> <code>runplan.py</code> wrote all 32 rectangles — 14,430 chunks — through <code>remap_full.json</code> (354 mappings), every block resolving in the new pack. The region and entity files were uploaded into <code>/wasteland/</code> with the POI cache cleared, and the library&#8217;s region pulled back byte-identical: chunk (131, 90) scans at 1,603 placed blocks and 402 block entities. A second pass then cleaned what the old world carried inside the chunks: 47 spawners pointing at mobs from cut mods now spawn zombies, 35 stray entity records from cut mods are gone, and 1,168 unopened chests whose loot tables no longer exist were retargeted — the cut pack&#8217;s city loot to Lost Cities&#8217; own city chest, ammo to Keerdm&#8217;s TaCZ ammo chest, dungeon-flavoured tables to the vanilla dungeon, village professions to their vanilla counterparts, and the 1.21-only trial-chamber tables to the dungeon. Boot after: no unknown-block or skipped-entity lines. Still to do: fly it.</p>")
pat = re.compile(r'<div class="gate"><b>Gate</b><br>Every planned chunk present in the new region files\..*?</div>', re.S)
assert len(pat.findall(s)) == 1
s = pat.sub('<div class="gate"><b>Gate &middot; passed on scan, flight pending</b><br>Library region byte-identical on the server; expected block-entity counts present; boot clean of chunk, block and entity warnings. In-game flight through each site still to do.</div>', s)
s = rep(s, "Full set boots clean: 19 error lines, every one in a known-benign set.", "Full set boots clean: 12 error lines, every one in a known-benign set (eleven Immersive Vehicles pack model quirks and one Forge dist probe).")
s = rep(s,
    "Factory Blocks\' mason table was uncraftable (its recipe used a Chipped 2.x type) and is restored by a KubeJS recipe.",
    "Factory Blocks ships its mason table recipe twice, once in the Chipped 2.x format that fails on 3.x and once in the 3.x format that works; the server datapack overrides the broken copy and KubeJS removes the duplicate, so the bench works and the boot is clean.")
assert balanced(s)
pp.write_text(s, encoding="utf-8"); print("blueprint patched")
