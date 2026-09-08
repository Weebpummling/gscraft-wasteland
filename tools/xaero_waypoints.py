"""Ship every place on the map to players as Xaero waypoints, so nobody has to explore to find things.

The obvious thing to ship would be Xaero's explored map tiles, and that is not something this can
safely fabricate: a region file carries its own palette of BlockStates written as NBT, per-pixel
palette indices, 12-bit signed packed heights and biome ids, behind a major/minor save version the mod
refuses to read if it is newer than itself. Writing that blind, with no way to check the result short
of launching the game, is a good way to ship a map that either fails to load or is quietly wrong.
Waypoints cost nothing and solve most of the same problem: from the first join, every build, landmark
and strongpoint is already named on the minimap and the world map.

    xaero_waypoints.py [--out DIR]

Writes one tree per server address the pack ships, because Xaero keys its folders on the address the
player actually connected with and the pack's servers.dat carries both:

    XaeroWaypoints/Multiplayer_gamesla308.bisecthosting.com/dim%0/mw$default_1.txt
    XaeroWaypoints/Multiplayer_199.115.76.82/dim%0/mw$default_1.txt

Sources: buildmap/plan_v8/sectors_v8.json for the placed builds, and the measured base-map landmarks
from docs/gscraft-skadowsky-camp.md section 11 and docs/gscraft-poi-coordinates.md. Sectors in group
`removed` are skipped - nothing stands there.

Line format, as WaypointIO reads it:
    waypoint:name:initials:x:y:z:colour:disabled:type:set:rotation:yaw:visibility:destination
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTORS = HERE.parent / "buildmap" / "plan_v8" / "sectors_v8.json"
ADDRESSES = ["gamesla308.bisecthosting.com", "199.115.76.82"]
DIM = "dim%0"
SET = "gui.xaero_default"

# Xaero colour indices 0-15
C_CAMP, C_STRONG, C_BUILD, C_FARM, C_TOWN, C_PLANT = 10, 14, 3, 8, 6, 4

# the base map's own landmarks, measured 2026-09-07 (skadowsky-camp section 11, poi-coordinates)
LANDMARKS = [
    ("Camp",                  -940, 65, -979,  C_CAMP,   "CP"),
    ("Bridge (west gate)",   -1043, 89, -946,  C_CAMP,   "BR"),
    ("The mast",              -808, 137, -1008, C_CAMP,  "MA"),
    ("Hospital",              -782, 64, -1277, C_STRONG, "HO"),
    ("Switchyard",            -815, 63, 105,   C_STRONG, "SW"),
    ("Turbine hall",           400, 64, 590,   C_STRONG, "TH"),
    ("Intake works",           895, 63, 155,   C_STRONG, "IW"),
    ("Confinement hall",      -642, 64, 518,   C_PLANT,  "CH"),
    ("Storage halls",         -888, 65, 167,   C_PLANT,  "SH"),
    ("Stadium",              -2395, 65, -3482, C_TOWN,   "ST"),
    ("Central square",       -2380, 65, -2975, C_TOWN,   "CS"),
    ("Palace of culture",    -2650, 65, -2889, C_TOWN,   "PC"),
    ("Collective farm",      -2112, 62, -896,  C_TOWN,   "CF"),
]


def initials(name):
    parts = [p for p in name.replace("-", " ").split() if p and p[0].isalnum()]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()


def line(name, ini, x, y, z, colour):
    name = name.replace(":", " ")
    return (f"waypoint:{name}:{ini}:{int(x)}:{int(y)}:{int(z)}:{colour}"
            f":false:0:{SET}:false:0:0:false")


def build():
    S = json.load(open(SECTORS, encoding="utf-8"))
    out = ["sets:" + SET, "#" + SET]
    seen = set()
    for w in LANDMARKS:
        n, x, y, z, c, ini = w
        out.append(line(n, ini, x, y, z, c))
        seen.add(n)
    for s in S["sectors"]:
        if s.get("group") == "removed":
            continue
        n = s.get("name", s["id"])
        if n in seen or s["id"] == "camp":
            continue
        cx, cz = (s["x0"] + s["x1"]) // 2, (s["z0"] + s["z1"]) // 2
        colour = C_FARM if s.get("group") == "farmstead" else C_BUILD
        out.append(line(n, initials(n), cx, 65, cz, colour))
    return out


def main(argv):
    out_root = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE.parent / "build" / "xaero"
    lines = build()
    n = sum(1 for l in lines if l.startswith("waypoint:"))
    for addr in ADDRESSES:
        d = out_root / "XaeroWaypoints" / f"Multiplayer_{addr}" / DIM
        d.mkdir(parents=True, exist_ok=True)
        (d / "mw$default_1.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{n} waypoints written for {len(ADDRESSES)} server addresses -> {out_root / 'XaeroWaypoints'}")
    for l in lines[2:8]:
        print("   ", l)
    print("    ...")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
