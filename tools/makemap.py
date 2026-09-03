"""Generate wasteland-district-map.html from the site inventory, transplant plan and strongpoints."""
import json, html as H, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # repo root
SP = ROOT / "buildmap"
DOCS = ROOT / "docs"
TOOLS = ROOT / "tools"
rows = json.load(open(SP / "site_inventory.json"))
sps = json.load(open(TOOLS / "strongpoints.json"))
plan = json.load(open(SP / "transplant_plan.json"))
start = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [-176, -176, 207, 207]
crater = [-16, -16, 47, 47]

for r in rows:  # second fingerprint: apocalypse-pack camps
    if {"campfire", "sign", "decorated_pot"} <= {k for k, v in r["bes"]}:
        r["generated"] = True

NAMES = {
    (2192, 400): ("FR-06 complex", "the custom cyberpunk cityscape: starship hangar FR-06 on its island, walled reactor plaza with the stadium, factory-block decks; 964 bookshelves, 885 sculk sensors, 728 dispensers"),
    (2528, 1344): ("Stone complex", "smooth stone and terracotta, sculk traps and 99 spawners"),
    (1904, 864): ("Industrial plant", "west wing of the cityscape: cyan and magenta refinery, 1,209 fluid pipes, tanks, razor wire"),
    (1568, 1152): ("Hempcrete compound", "walled compound, 405 ceiling lights, razor wire, IE wiring"),
    (1328, 1376): ("Residential block", "stone brick and white concrete housing, 168 chests, 92 beds"),
    (1488, 432): ("Acacia hall", "43k acacia wood, redstone connectors"),
    (2576, 368): ("Hopper array", "old world: 325 hoppers under terracotta; moved with the +140/+89 offset"),
    (2016, 768): ("Prismarine hall", "prismarine with sculk sensors"),
    (1920, 1024): ("Copper tower", "waxed copper, 38 decorated pots"),
    (2032, 1392): ("Library", "615 signs, 356 barrels, 306 beehives; 2,010 block entities in 96x96"),
    (2368, 1552): ("Mud village", "packed mud and spruce, 52 beds"),
    (2144, 704): ("Factory annex", "factory blocks and basalt, sculk sensors"),
    (0, 0): ("Spawn structure", "Warium refinery build on the lake island; world spawn on its plaza"),
    (1184, 464): ("Glass tower", "white glass and quartz pillars"),
    (1824, 1568): ("Stone-brick houses", "stone brick, oak, campfires and cabinets"),
}
major = []
for r in rows:
    key = (r["blocks"][0], r["blocks"][1])
    if key in NAMES and not r["generated"]:
        r["name"], r["what"] = NAMES[key]; major.append(r)
major.sort(key=lambda r: -r["placed"])

rects = []
for r in plan:
    x1, z1, x2, z2 = r["chunks"]; dx, dz = r["offset"]
    rects.append((r["source"], [(x1 + dx) * 16, (z1 + dz) * 16, (x2 + dx) * 16 + 15, (z2 + dz) * 16 + 15]))

X1, Z1, X2, Z2 = -300, -300, 6600, 3400
W, HGT = 1380, 740
sx = W / (X2 - X1); sz = HGT / (Z2 - Z1)
px = lambda x: (x - X1) * sx
pz = lambda z: (z - Z1) * sz


def rect(r, cls):
    x1, z1, x2, z2 = r
    return (f'<rect class="{cls}" x="{px(x1):.1f}" y="{pz(z1):.1f}" '
            f'width="{max(1.5, (x2 - x1 + 1) * sx):.1f}" height="{max(1.5, (z2 - z1 + 1) * sz):.1f}"/>')


parts = [f'<rect class="ground" x="0" y="0" width="{W}" height="{HGT}"/>']
grid = []
for gx in range(0, X2, 500):
    grid.append(f'<line class="grid" x1="{px(gx):.1f}" y1="0" x2="{px(gx):.1f}" y2="{HGT}"/>'
                f'<text class="tick" x="{px(gx) + 2:.1f}" y="{HGT - 4}">x {gx}</text>')
for gz in range(0, Z2, 500):
    grid.append(f'<line class="grid" x1="0" y1="{pz(gz):.1f}" x2="{W}" y2="{pz(gz):.1f}"/>'
                f'<text class="tick" x="3" y="{pz(gz) - 3:.1f}">z {gz}</text>')
for src, r in rects:
    parts.append(rect(r, "tr-live" if src == "live" else "tr-old"))
d = rects[0][1]
parts.append(f'<text class="prov" x="{px(d[0]) + 6:.1f}" y="{pz(d[1]) - 6:.1f}">'
             f'TRANSPLANTED DISTRICT (live world, same coordinates) chunks 56-193 / 24-129</text>')
parts.append(f'<text class="prov" x="{px(1000):.1f}" y="{pz(2400):.1f}">'
             f'OLD-WORLD SITES, moved +2240 / +1424 blocks (dashed)</text>')
for r in rows:
    if r["generated"]: parts.append(rect(r["blocks"], "ruin"))
for r in rows:
    if not r["generated"] and r not in major: parts.append(rect(r["blocks"], "small"))
for i, r in enumerate(major, 1):
    parts.append(rect(r["blocks"], "site"))
    x1, z1, x2, z2 = r["blocks"]
    parts.append(f'<text class="num" x="{px((x1 + x2) / 2):.1f}" y="{pz((z1 + z2) / 2) + 4:.1f}" text-anchor="middle">{i}</text>')
parts.append(rect(start, "start"))
parts.append(f'<text class="lbl" x="{px(start[0]) + 3:.1f}" y="{pz(start[3]) + 13:.1f}">'
             f'STARTING AREA {start[2] - start[0] + 1}x{start[3] - start[1] + 1}</text>')
parts.append(rect(crater, "crater"))
NAMESP = {"radio_tower": "RADIO TOWER", "substation": "SUBSTATION", "water_treatment": "WATER TREATMENT",
          "hospital": "HOSPITAL", "airfield": "AIRFIELD"}
for p in sps:
    x1, z1, x2, z2 = p["blocks"]
    parts.append(rect(p["blocks"], "pad"))
    parts.append(f'<text class="lbl" x="{px(x1) + 3:.1f}" y="{pz(z1) - 5:.1f}">{NAMESP[p["name"]]} {p["size"][0]}x{p["size"][1]}</text>')
# --- v6 layout layer (docs/gscraft-map-layout-v6.md): planned transplants, pads, the tower in the camp
plan6 = json.load(open(SP / "transplant_plan_v6.json")) if (SP / "transplant_plan_v6.json").exists() else []
pads6 = json.load(open(TOOLS / "pads_v6.json")) if (TOOLS / "pads_v6.json").exists() else []
for p6 in pads6:
    parts.append(rect(p6["blocks"], "pad6"))
    parts.append(f'<text class="lbl6" x="{px(p6["blocks"][0]) + 3:.1f}" y="{pz(p6["blocks"][1]) - 3:.1f}">pad {H.escape(p6["name"])} y{p6["y"]}</text>')
V6NAMES = {"settlement": "the settlement", "novo": "Novo Industrial Zone (SP1)", "plaza": "Financial Plaza (SP5)", "biogen_s": "Bio Gen",
           "biogen_n": "", "sewers": "sewers (below)", "hub": "NOVO EXPOGRAD - the hub (air ring)"}
for r6 in plan6:
    parts.append(rect(r6["dest_blocks"], "v6"))
    nm6 = V6NAMES.get(r6["source"], r6["source"])
    if nm6: parts.append(f'<text class="lbl6" x="{px(r6["dest_blocks"][0]) + 3:.1f}" y="{pz(r6["dest_blocks"][3]) + 11:.1f}">{H.escape(nm6)} dy{r6.get("dy", 0)}</text>')
parts.append(f'<text class="prov" x="{px(4700):.1f}" y="{pz(-150):.1f}">V6 LAYOUT (magenta): planned transplants and pads; tower in the camp; border 10 km centred 1900,1250</text>')
svg = "\n".join(grid + parts)

mrows = "\n".join(
    f'<tr><td class="num">{i}</td><td><b>{H.escape(r["name"])}</b></td><td class="mono">{r["size"][0]} x {r["size"][1]}</td>'
    f'<td class="mono">x {r["blocks"][0]}..{r["blocks"][2]}<br>z {r["blocks"][1]}..{r["blocks"][3]}</td>'
    f'<td class="mono">{r["placed"]:,}</td><td>{"old world" if r["world"] == "old-only" else "live world"}</td>'
    f'<td>{H.escape(r["what"])}</td></tr>' for i, r in enumerate(major, 1))
prow = "\n".join(
    f'<tr><td><b>{NAMESP[p["name"]]}</b></td><td class="mono">{p["size"][0]} x {p["size"][1]}</td>'
    f'<td class="mono">x {p["blocks"][0]}..{p["blocks"][2]}<br>z {p["blocks"][1]}..{p["blocks"][3]}</td>'
    f'<td>{H.escape(p["purpose"])}</td></tr>' for p in sps)
nsmall = sum(1 for r in rows if not r["generated"] and r not in major)
nruin = sum(1 for r in rows if r["generated"])
sw, sh = start[2] - start[0] + 1, start[3] - start[1] + 1

CSS = """
:root{--ground:#E4E3DC;--surface:#F2F1EB;--ink:#1D201C;--ink-soft:#585C53;--ink-faint:#83877D;--rule:#C6C5BB;--accent:#7C7211;--warn:#8C3928;--verify:#3F6560;--site:#7A5C2E;--ruin:#A9A398;--water:#4C7A96}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#15171A;--surface:#1D2024;--ink:#E6E4DB;--ink-soft:#A2A69C;--ink-faint:#767B72;--rule:#333840;--accent:#D4C24A;--warn:#D0705C;--verify:#7FAAA4;--site:#C69A5B;--ruin:#4E545C;--water:#6FA3C4}}
:root[data-theme="dark"]{--ground:#15171A;--surface:#1D2024;--ink:#E6E4DB;--ink-soft:#A2A69C;--ink-faint:#767B72;--rule:#333840;--accent:#D4C24A;--warn:#D0705C;--verify:#7FAAA4;--site:#C69A5B;--ruin:#4E545C;--water:#6FA3C4}
body{margin:0;background:var(--ground);color:var(--ink);font-family:"Archivo","Segoe UI",Helvetica,Arial,sans-serif;font-size:15px;line-height:1.55}
.wrap{max-width:1240px;margin:0 auto;padding:28px 24px 80px}
h1{font-family:"Oswald","Arial Narrow",sans-serif;text-transform:uppercase;font-weight:600;font-size:38px;line-height:1.05;margin:0 0 6px}
.sub{color:var(--ink-soft);margin:0 0 18px;max-width:78ch}
.mapwrap{overflow-x:auto;border:1px solid var(--rule);background:var(--surface)}
svg{display:block;min-width:900px}
.v6{fill:rgba(220,40,200,.18);stroke:#d028c8;stroke-width:1.4}
.pad6{fill:none;stroke:#d028c8;stroke-width:1;stroke-dasharray:4 3}
.lbl6{font:600 10px system-ui,sans-serif;fill:#a0109a}
.ground{fill:var(--surface)} .grid{stroke:var(--rule);stroke-width:1}
.tick{font:11px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink-faint)}
.tr-live{fill:var(--ink-faint);fill-opacity:.10;stroke:var(--ink-faint);stroke-width:1.2}
.tr-old{fill:var(--ink-faint);fill-opacity:.10;stroke:var(--ink-faint);stroke-width:1;stroke-dasharray:4 3}
.prov{font:600 10.5px "JetBrains Mono",ui-monospace,monospace;letter-spacing:.08em;fill:var(--ink-soft)}
.ruin{fill:var(--ruin);fill-opacity:.45;stroke:none}
.small{fill:var(--site);fill-opacity:.45;stroke:none}
.site{fill:var(--site);fill-opacity:.75;stroke:var(--ink);stroke-width:.8}
.num{font:700 11px "Oswald","Arial Narrow",sans-serif;fill:#fff;paint-order:stroke;stroke:#1D201C;stroke-width:2.5px}
.pad{fill:var(--accent);fill-opacity:.35;stroke:var(--accent);stroke-width:2}
.start{fill:var(--verify);fill-opacity:.22;stroke:var(--verify);stroke-width:2}
.crater{fill:var(--water);fill-opacity:.7;stroke:none}
.lbl{font:600 11px "Oswald","Arial Narrow",sans-serif;letter-spacing:.06em;fill:var(--ink)}
.legend{display:flex;flex-wrap:wrap;gap:10px 24px;margin:12px 0 26px;font-size:13px;color:var(--ink-soft)}
.legend span::before{content:"";display:inline-block;width:14px;height:10px;margin-right:7px;vertical-align:-1px;border:1px solid}
.l-site::before{background:var(--site);border-color:var(--ink)} .l-small::before{background:color-mix(in srgb,var(--site) 45%,transparent);border-color:transparent}
.l-ruin::before{background:color-mix(in srgb,var(--ruin) 45%,transparent);border-color:transparent}
.l-pad::before{background:color-mix(in srgb,var(--accent) 35%,transparent);border-color:var(--accent)}
.l-start::before{background:color-mix(in srgb,var(--verify) 22%,transparent);border-color:var(--verify)}
.l-live::before{background:color-mix(in srgb,var(--ink-faint) 10%,transparent);border-color:var(--ink-faint)}
.l-old::before{background:color-mix(in srgb,var(--ink-faint) 10%,transparent);border-color:var(--ink-faint);border-style:dashed}
.l-water::before{background:var(--water);border-color:var(--water)}
h2{font-family:"Oswald","Arial Narrow",sans-serif;text-transform:uppercase;font-weight:600;font-size:22px;margin:30px 0 8px;border-bottom:2px solid var(--ink);padding-bottom:4px}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;font:11px "JetBrains Mono",ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);padding:8px 10px;border-bottom:1px solid var(--rule)}
td{padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
td.mono{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;white-space:nowrap} td.num{font-weight:700}
.tablewrap{overflow-x:auto} p{max-width:78ch}
"""

page = f"""<title>Wasteland District Map</title>
<style>{CSS}</style>
<div class="wrap">
<h1>Wasteland District Map</h1>
<p class="sub">Top-down, north up, block coordinates. What was transplanted from the prior builds and where it sits, the player builds that matter by name, the generated ruin clusters that came along inside the district rectangle, the five strongpoint compounds in the wasteland ring around the district, and the starting area around the spawn lake.</p>
<div class="mapwrap"><svg viewBox="0 0 {W} {HGT}" width="{W}" height="{HGT}" xmlns="http://www.w3.org/2000/svg">{svg}</svg></div>
<div class="legend"><span class="l-site">numbered player builds (table below)</span><span class="l-small">{nsmall} small player scatters</span><span class="l-ruin">{nruin} generated ruin clusters carried with the district</span><span class="l-live">transplanted from the live world, same coordinates</span><span class="l-old">transplanted from the old world, moved +2240 / +1424</span><span class="l-pad">strongpoint compounds</span><span class="l-start">starting area</span><span class="l-water">spawn lake and structure</span></div>
<h2>Transplanted areas</h2>
<p>Two sources. The <b>live world</b> (the last world the server ran) already held the player district at chunks 56 to 193 by 24 to 129 plus the spawn structure and one outlier; those 14,644 chunks were copied at the same coordinates. The <b>old world</b> (the 2025 world) had 29 sites the previous admin never moved; they were copied with the same offset the admin had used for everything else, +140 / +89 chunks, so old and live content keep their relative positions. Everything inside those rectangles came across, ruins included: the grey clusters are Lost Cities apocalypse-pack buildings (cracked stone brick, spawner, chest, blast furnace, or the campfire, sign and decorated-pot camps), not player work.</p>
<h2>Player builds</h2>
<div class="tablewrap"><table><tr><th>#</th><th>Build</th><th>Size</th><th>Blocks</th><th>Placed</th><th>Source</th><th>What it is</th></tr>{mrows}</table></div>
<h2>Location pool</h2>
<p>The endgame does not ask five players to hold every site. Taking a location starts a clock to fortify it; on each cycle the game draws one held location, warns the players, and attacks that one. The pool is every location taken so far. It opens with the custom structures already in the district and the five compounds around it:</p>
<div class="tablewrap"><table><tr><th>Location</th><th>Kind</th><th>Blocks</th><th>Why it works as a location</th></tr>
<tr><td><b>FR-06 complex</b></td><td>custom, transplanted</td><td class="mono">x 2192..2575<br>z 400..927</td><td>Hangar, plaza and stadium: the natural airfield and the showpiece</td></tr>
<tr><td><b>Industrial plant</b></td><td>custom, transplanted</td><td class="mono">x 1904..2367<br>z 864..1135</td><td>Refinery and tank farm: water and fuel</td></tr>
<tr><td><b>Hempcrete compound</b></td><td>custom, transplanted</td><td class="mono">x 1568..1887<br>z 1152..1471</td><td>Walled, lit, wired: a ready garrison</td></tr>
<tr><td><b>Stone complex</b></td><td>custom, transplanted</td><td class="mono">x 2528..2751<br>z 1344..1631</td><td>Trapped interior, 99 spawners: a clear-and-hold dungeon</td></tr>
<tr><td><b>Residential block</b></td><td>custom, transplanted</td><td class="mono">x 1328..1551<br>z 1376..1775</td><td>Housing to defend street by street</td></tr>
<tr><td><b>Library</b></td><td>custom, transplanted</td><td class="mono">x 2032..2127<br>z 1392..1487</td><td>Dense interior, the intel site</td></tr>
</table></div>
<h2>Strongpoint compounds</h2>
<div class="tablewrap"><table><tr><th>Site</th><th>Footprint</th><th>Blocks</th><th>What the footprint has to hold</th></tr>{prow}</table></div>
<p>Sized as compounds to hold on a horde night, not as single buildings: the mega-base is 384 x 528 and the industrial district 464 x 272, so anything smaller than a city block reads as a shed next to them. They sit in the wasteland ring around the district because nothing that size fits between the builds; each is levelled to the median ground (above any water it touches), cleared, ramped into the surrounding terrain, and outlined in yellow concrete with corner posts as the cut line for a paste or a hand build.</p>
<h2>Starting area</h2>
<p>Blocks {start[0]} to {start[2]} on both axes, {sw} x {sh}, centred on the spawn structure. The structure stands in the old lake at level 62 at the bottom of a basin whose walls are ramped up to the plateau over 96 blocks; the whole square is cleared of city ruins down to natural ground and a yellow concrete line follows the ground along its border. World spawn is the structure plaza at 19, 94, 26.</p>
</div>"""
(DOCS / "wasteland-district-map.html").write_text(page, encoding="utf-8")
print("map written", len(page), "major:", [r["name"] for r in major], "small:", nsmall, "ruins:", nruin)
