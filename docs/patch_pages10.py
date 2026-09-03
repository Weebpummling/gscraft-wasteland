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
pat = re.compile(r'<div class="gate"><b>Gate</b><br>Pre-gen complete, restore verified, manifest and configs committed, players on the whitelist can join with the pack\.</div>')
assert len(pat.findall(s)) == 1
s = pat.sub('<div class="gate"><b>Gate &middot; in progress</b><br>Pre-gen complete (14 rectangles, 19,369 chunks, 2026-09-02 17:10). Whitelist off by decision: five players, open door. Client pack built: GSCraft-Client.zip, 452 MB, a Prism Launcher instance with the install guide inside. Old-world housekeeping still pending.</div>', s)
s = rep(s, "<li><strong>Every mod is version-pinned.</strong>",
        "<li><strong>The district map lives at <a href=\"https://claude.ai/code/artifact/c76b1bb4-c845-4252-9ab8-17ee4fc10c3f\">Wasteland District Map</a>:</strong> every player build, the five strongpoint pads with sizes and coordinates, and the starting area.</li>\n<li><strong>Every mod is version-pinned.</strong>")
assert balanced(s)
pp.write_text(s, encoding="utf-8"); print("blueprint patched")
