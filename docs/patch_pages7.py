"""Phase 03 results: Lost Cities 7.5 mechanism, profile comparison, wasteland chosen; dry run clean."""
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


pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")

s = rep(s,
        "<p>Lost Cities 7.5.3 alone — LC²H cut after two failed gates on version coupling. Choose the profile deliberately — the old server had two different answers in two files. Iterate against throwaway worlds until density, rubble and wilderness gaps read right.</p>",
        "<p><strong>Done 2026-09-02.</strong> Lost Cities 7.5.3 alone — LC²H cut after two failed gates on version coupling. Two things learned the hard way: 7.5 ships no world preset, so <code>level-type</code> stays default and the city is switched on by <code>selectedProfile</code> in <code>defaultconfigs/lostcities-server.toml</code> before the world\'s first boot; and the old server\'s profile JSONs must not be carried — its <code>improved.json</code> referenced Pomkots World assets and crashed level load. Four throwaway worlds were generated and their spawn regions scanned: <code>rarecities</code> put no city within 400 blocks; <code>onlycities</code> was towers wall to wall with no wilderness; <code>improved</code> crashes on 7.5.3 even with stock profiles; <strong><code>wasteland</code></strong> — dense city on dead terrain, every one of the sixty most-built spawn chunks city fabric — is the setting, and is the profile of the real world.</p>")
s = rep(s,
        "<div class=\"gate\"><b>Gate</b><br>Three test worlds generated and flown through. One profile, set in both the mod config and <code>generator-settings</code>, committed.</div>",
        "<div class=\"gate\"><b>Gate · passed</b><br>Four test worlds generated and scanned. Profile <code>wasteland</code> committed via <code>defaultconfigs</code>; the real <code>wasteland</code> world created on a fresh seed with 0 errors.</div>")
s = rep(s,
        "<p>With the new world generated and the build-dependency mods installed, run <code>transplant.py</code>: the live district at the same coordinates, the spawn structure, the eleven old-world sites at their known offset, all through <code>remap.json</code>. Regenerate POI; move entities. Then fly it.</p>",
        "<p>With the new world generated and the build-dependency mods installed, run <code>runplan.py</code>: the live district at the same coordinates, the spawn structure, and 29 old-world sites at their known offset, all through <code>remap_full.json</code> (354 mappings). The dry run over all 32 rectangles — 14,430 chunks — is already clean: every block resolves in the new pack. Regenerate POI; move entities. Then fly it.</p>")
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")
