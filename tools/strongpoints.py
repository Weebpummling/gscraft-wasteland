"""Place the five strongpoint pads inside the pre-generated district, clear of every player build.
Writes strongpoints.json: name, size, block rect, purpose."""
import json, sys
sites = json.load(open(sys.argv[1]))          # site_rects_live.json
big = [10, -20, 250, 175]                     # search area, chunks (the wasteland ring around the district)
MARGIN = 40                                   # blocks kept clear around any player build
SPAWN = [-176, -176, 207, 207]
PADS = [  # name, width x, depth z, purpose - sized as compounds to hold, not single buildings
    ("radio_tower", 128, 128, "Endgame objective: the mast, its transmitter hall and a walled compound"),
    ("substation", 160, 160, "Power: transformer yard, switch house, perimeter and approach"),
    ("water_treatment", 192, 160, "Water and biodiesel: settling basins, pump house, tank farm"),
    ("hospital", 192, 192, "Medical: main block, wings, car park and a defensible perimeter"),
    ("airfield", 512, 192, "Aircraft and heavy vehicles: 400-block runway, apron, hangars, tower"),
]
def blocked(r):
    x1, z1, x2, z2 = r
    for s in sites + [{"blocks": SPAWN}]:
        a, b, c, d = s["blocks"]
        if x1 <= c + MARGIN and a - MARGIN <= x2 and z1 <= d + MARGIN and b - MARGIN <= z2: return True
    return False
X1, Z1, X2, Z2 = big[0]*16 + 48, big[1]*16 + 48, big[2]*16 + 15 - 48, big[3]*16 + 15 - 48
placed = []
# candidate anchors: spread the five over the district quadrants + centre, scanning outward for a free spot
anchors = {"radio_tower": (0.5, 0.05), "substation": (0.1, 0.35), "water_treatment": (0.92, 0.35), "hospital": (0.15, 0.9), "airfield": (0.8, 0.95)}
for name, w, d, purpose in PADS:
    fx, fz = anchors[name]
    ax, az = int(X1 + (X2 - X1) * fx), int(Z1 + (Z2 - Z1) * fz)
    best = None
    for ring in range(0, 1200, 16):
        cands = []
        for dx in range(-ring, ring + 1, 16):
            for dz in (-ring, ring):
                cands.append((ax + dx, az + dz)); cands.append((ax + dz, az + dx))
        for (cx, cz) in cands:
            r = [cx - w // 2, cz - d // 2, cx - w // 2 + w - 1, cz - d // 2 + d - 1]
            if r[0] < X1 or r[1] < Z1 or r[2] > X2 or r[3] > Z2: continue
            if blocked(r) or any(r[0] <= p["blocks"][2] + MARGIN and p["blocks"][0] - MARGIN <= r[2] and r[1] <= p["blocks"][3] + MARGIN and p["blocks"][1] - MARGIN <= r[3] for p in placed): continue
            best = r; break
        if best: break
    if not best: print("NO SPOT for", name); continue
    placed.append({"name": name, "size": [w, d], "blocks": best, "purpose": purpose, "chunks": [best[0] >> 4, best[1] >> 4, best[2] >> 4, best[3] >> 4]})
    print(f"{name:16s} {w}x{d}  x {best[0]}..{best[2]}  z {best[1]}..{best[3]}  chunks {placed[-1]['chunks']}")
json.dump(placed, open("strongpoints.json", "w"), indent=1)
