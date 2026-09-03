"""Keerdm's six failing tables are unused Point Blank variants; FTB suite comes from CurseForge."""
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
        """  <div class="flag">
    <span class="tag">Player-facing · looting</span>
    <p><strong>Six Keerdm Zombie Essentials loot tables fail to parse</strong> — <code>abandoned_car_basic</code>, <code>abandoned_car_advanced</code>, <code>abandoned_car_emergency</code>, <code>apartment_bathroom</code>, <code>vics_point_blank_ammochest</code>, <code>vics_point_blank_gunchest</code>. They reference items from Vic\'s Point Blank, which is not installed. Those containers generate <strong>empty</strong> throughout every Lost Cities structure that uses them. On a looter server this is the headline defect.</p>
  </div>""",
        """  <div class="flag">
    <span class="tag">Log noise, not a defect</span>
    <p><strong>Six Keerdm Zombie Essentials loot tables fail to parse</strong> — its <code>_vics</code> variants, which reference Vic\'s Point Blank items. The first version of this page called them empty chests. Keerdm\'s own Lost Cities conditions (<code>car_loot.json</code>, <code>chestloot.json</code>) reference only the <code>_tacz</code> twins, so nothing generates from the broken tables; they are dead files shipped for a Point Blank configuration. Seventy error lines a boot, zero player impact.</p>
  </div>""")

b = rep(b,
        '<tr><td class="mod">Keerdm Zombie Essentials 1.4</td><td>Override the six Point-Blank loot tables with a datapack so the cars, bathrooms and ammo chests generate loot.</td></tr>',
        '<tr><td class="mod">Keerdm Zombie Essentials 1.4</td><td>Nothing to fix — the failing <code>_vics</code> tables are unused. Keep as-is.</td></tr>')

b = rep(b,
        '<tr><td class="mod">Lootr</td><td><span class="chip core">Absent</span></td><td>Per-player loot instancing. The single most important mod for a looter server, and the one whose absence explains "first player empties the map."</td></tr>',
        '<tr><td class="mod">Lootr</td><td><span class="chip core">Absent</span></td><td>Per-player loot instancing. The single most important mod for a looter server, and the one whose absence explains "first player empties the map." Pinned: 0.7.35.94.</td></tr>')

b = rep(b,
        '<tr><td class="mod">FTB Quests</td><td><span class="chip sup">Absent</span></td><td>RealmRPG Quests is installed instead — a small alternative that cannot carry the strongpoint structure.</td></tr>',
        '<tr><td class="mod">FTB Quests</td><td><span class="chip sup">Absent</span></td><td>RealmRPG Quests is installed instead — a small alternative that cannot carry the strongpoint structure. FTB publishes on CurseForge only; Quests 2001.4.22, Library 2001.2.13, Teams 2001.3.2 and Item Filters were pulled from its CDN by file id.</td></tr>')

bp.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full)
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched")

pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")
s = rep(s,
        "<p>TaCZ 1.1.8 with chaoszpack, the fire-control extension, and Keerdm plus a datapack that overrides its six Point-Blank loot tables. Superb Warfare with MCSP and vvp, small arms disabled. Immersive Engineering trimmed. Immersive Vehicles with one pack.</p>",
        "<p>TaCZ 1.1.8 with its default gun pack, the fire-control extension, and Keerdm. Superb Warfare with MCSP and vvp, small arms disabled. Immersive Engineering trimmed. Immersive Vehicles with the two official packs (Content Pack V29, Automobile Pack V3).</p>")
s = rep(s,
        "<div class=\"gate\"><b>Gate</b><br>One ammo economy. Every weapon and vehicle craftable through a known route. The six loot tables generate loot.</div>",
        "<div class=\"gate\"><b>Gate</b><br>One ammo economy. Every weapon and vehicle craftable through a known route. Keerdm car and chest loot rolls TaCZ guns and ammo.</div>")
s = rep(s,
        "Lootr 0.7.35.94, Improved Mobs 1.13.7 (+ TenshiLib), FTB Chunks / Quests / Library / Teams, Canary 0.3.3,",
        "Lootr 0.7.35.94, Improved Mobs 1.13.7 (+ TenshiLib), FTB Chunks, Quests 2001.4.22, Library 2001.2.13, Teams 2001.3.2 and Item Filters (CurseForge CDN by file id — FTB does not publish on Modrinth), Canary 0.3.3,")
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")
