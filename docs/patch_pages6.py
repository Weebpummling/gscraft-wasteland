"""LC2H cut after two failed gates; Lost Cities pinned 7.5.3; JVM flag facts."""
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


bp = SP / "gscraft-audit-body.html"
b = bp.read_text(encoding="utf-8")
b = rep(b,
        '<tr><td class="mod">lc2h 2.1.1</td><td>Replaced by LC²H 3.5.0 (April 2026), built against Lost Cities 7.4.x. Set debug off.</td></tr>',
        '<tr><td class="mod">lc2h 2.1.1</td><td><strong>Cut.</strong> LC²H 3.5.0 needs Lost Cities ≥ 7.4.11 and its spawn mixin breaks on 7.5.x — a pin window too narrow to maintain. Two phase-03 gates failed on it in sequence; Chunky pre-generation covers what it optimizes.</td></tr>')
b = rep(b,
        '<tr><td class="mod">lostcities 7.4.6</td><td>Setting</td><td>Newer than the blueprint\'s cited build.</td></tr>',
        '<tr><td class="mod">lostcities 7.4.6</td><td>Setting</td><td>Updated to 7.5.3 (August 2026) during phase 03.</td></tr>')
b = rep(b,
        '<tr><td class="mod">Heap</td><td class="ver">-Xms128M -Xmx8192M</td><td>Xms should equal Xmx. The JVM resizes the heap upward through play instead of starting where it will end up.</td></tr>',
        '<tr><td class="mod">Heap</td><td class="ver">-Xms128M -Xmx8192M</td><td>Xms should equal Xmx, but the Bisect egg hard-codes both and rejects <code>-Xms</code>/<code>-Xmx</code> in <code>CUSTOM_ARGS</code>. Not fixable from the panel; the JVM grows the heap on demand.</td></tr>')
b = rep(b,
        '<tr><td class="mod">Aikar\'s flags</td><td class="ver">disabled</td><td>Bisect exposes this as a one-click toggle (<code>AIKARS_ENABLED</code>). Turn it on.</td></tr>',
        '<tr><td class="mod">Aikar\'s flags</td><td class="ver">disabled</td><td>Now on: the G1 flag set is in <code>CUSTOM_ARGS</code> and shows in the rendered invocation; <code>AIKARS_ENABLED=1</code> as well.</td></tr>')
bp.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full)
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched")

pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")
s = rep(s,
        '<tr><td class="mod">The Lost Cities</td><td><span class="chip core">Load-bearing</span></td><td class="ver">1.20-7.4.6+</td>',
        '<tr><td class="mod">The Lost Cities</td><td><span class="chip core">Load-bearing</span></td><td class="ver">1.20-7.5.3</td>')
s = rep(s,
        "Simple Voice Chat 2.6.22, Apotheosis 7.4.8 (+ Apothic Attributes), Chipped 3.0.7 (+ Resourceful Lib), TaCZ 1.1.8-hotfix, LC²H 3.5.0.</li>",
        "Simple Voice Chat 2.6.22, Apotheosis 7.4.8 (+ Apothic Attributes), Chipped 3.0.7 (+ Resourceful Lib), TaCZ 1.1.8-hotfix, Lost Cities 7.5.3. LC²H was tried and cut: its 3.5.0 build pins Lost Cities to a window narrower than one minor version.</li>")
s = rep(s,
        "<p>Lost Cities 7.4.6 with LC²H pinned to match, plus terrain mods. Choose the profile deliberately — the current server has two different answers in two files. Iterate against throwaway worlds until density, rubble and wilderness gaps read right.</p>",
        "<p>Lost Cities 7.5.3 alone — LC²H cut after two failed gates on version coupling. Choose the profile deliberately — the old server had two different answers in two files. Iterate against throwaway worlds until density, rubble and wilderness gaps read right.</p>")
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")
