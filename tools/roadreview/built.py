"""The connectors standing in the world after the v8 road rework (2026-09-06)."""
import json
from pathlib import Path
PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8")
GONE = {"old12_S","old16_S","old20_W","old23_W","old24_S","old27_W",   # replaced by farm_belt
        "mega_S","indu_N","indu_E","old29_S"}                          # replaced by east_trunk
def built():
    out = []
    for f in ("routes_v8_short.json", "routes_v8_long.json", "routes_v8_stubs.json", "routes_v8_lake.json",
              "routes_v8_belt.json", "routes_v8_east.json", "routes_v8_ring.json"):
        for r in json.load(open(PLAN / f)):
            if r["name"] in GONE or not r["polyline"]: continue
            out.append(dict(r, file=f.replace("routes_v8_", "").replace(".json", "")))
    return out
if __name__ == "__main__":
    b = built()
    print(f"{len(b)} connectors standing, {sum(r['metres'] for r in b):,.0f} m")
