"""Phases 04-08 executed on the server; known-benign error set; berezka_api dropped."""
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
        "<p>TaCZ 1.1.8 with its default gun pack, the fire-control extension, and Keerdm. Superb Warfare with MCSP and vvp, small arms disabled. Immersive Engineering trimmed. Immersive Vehicles with the two official packs (Content Pack V29, Automobile Pack V3).</p>",
        "<p><strong>Installed 2026-09-02 15:40</strong> as part of the full pinned set (95 jars, 102 mod IDs). TaCZ 1.1.8 with its default gun pack, the fire-control extension, and Keerdm. Superb Warfare with MCSP and vvp. Immersive Engineering. Immersive Vehicles with the two official packs — their model files log eleven cosmetic warnings a boot, which is the packs\' business, not ours. Superb Warfare\'s small-arms toggle is still to be set.</p>")
s = rep(s,
        "<div class=\"gate\"><b>Gate</b><br>One ammo economy. Every weapon and vehicle craftable through a known route. Keerdm car and chest loot rolls TaCZ guns and ammo.</div>",
        "<div class=\"gate\"><b>Gate · boot passed, balance open</b><br>Full set boots clean: 19 error lines, every one in a known-benign set. Small-arms overlap and the in-game craft routes are checked in play.</div>")
s = rep(s,
        "<p>Lootr, Sophisticated Backpacks, PlayerRevive, Custom Starting Gear, Farmer\'s Delight, Apotheosis, FTB Chunks, FTB Quests. Loot tables written per district tier.</p>",
        "<p><strong>Installed.</strong> Lootr, Sophisticated Backpacks, PlayerRevive, Custom Starting Gear, Farmer\'s Delight, Apotheosis, FTB Chunks, FTB Quests. Factory Blocks\' mason table was uncraftable (its recipe used a Chipped 2.x type) and is restored by a KubeJS recipe. Loot tables per district tier are still to be written.</p>")
s = rep(s,
        "<p>The carried In Control! rules, Mob Factions, Zombie Awareness, The Hordes with a freshly generated 1.5.4c config, Improved Mobs constrained, Bandits, Hostile and Guard Villagers, Recruits. Per-district faction rules authored on top of the carried spawn layer.</p>",
        "<p><strong>Installed and configured.</strong> The carried In Control! rules with the mech entries removed, Mob Factions likewise, Zombie Awareness, The Hordes on a freshly generated 1.5.4c config, Improved Mobs, Bandits, Hostile and Guard Villagers, Recruits. Per-district faction rules and the Improved Mobs block-breaking constraints are still to be authored.</p>")
s = rep(s,
        "<p>The Man From The Fog, Eyes in the Darkness and The Knocker — added last, rates cut hard, plus sound and the client ambience set.</p>",
        "<p><strong>Installed with rates cut:</strong> Eyes in the Darkness at one eye per player on a 600-tick cycle (300 at midnight) instead of 2–3 every 150; The Knocker on <code>rare</code>; The Man From The Fog at defaults pending measurement.</p>")
s = rep(s,
        "<li><strong>Every mod is version-pinned.</strong> Keep a manifest of exact filenames and jar hashes. \"Latest\" is how a working server breaks overnight.</li>",
        "<li><strong>Every mod is version-pinned.</strong> <code>build/manifest.json</code> and <code>build/additions.json</code> hold exact filenames, hashes and declared dependencies for the whole set. \"Latest\" is how a working server breaks overnight.</li>")
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")

bp = SP / "gscraft-audit-body.html"
b = bp.read_text(encoding="utf-8")
b = rep(b,
        '<tr><td class="mod">berezka_api</td><td>chaoszpack</td><td>Keep</td></tr>',
        '<tr><td class="mod">berezka_api</td><td>chaoszpack</td><td>Cut — went with chaoszpack; nothing else declares it</td></tr>')
bp.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full)
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched")
