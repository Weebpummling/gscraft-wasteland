"""Assemble buildmap/plan_v8/transplant_plan_v8.json from the art-pass placements (sectors_v8.json), the v6 transplant
entries (source rects and their vertical offsets to a pad level) and the measured source ground levels, all onto the
Pripyat cell's ground level (65). Farmsteads come from the 29 old-site rects of transplant_plan.json (live coords in
the v7 pristine world). usage: plan_v8.py"""
import json, glob, os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GROUND = 65
sec = {p["id"]: p for p in json.load(open(REPO / "buildmap/plan_v8/sectors_v8.json"))["sectors"]}
old = json.load(open(r"G:/GSCraft/incoming/census/old_sites_ground.json"))
v6 = {r["source"]: r for r in json.load(open(REPO / "buildmap/transplant_plan_v6.json"))}
LIVE = "G:/GSCraft/scratch/worlds/wasteland-v7-pregen"
SKAD = os.path.dirname(glob.glob("G:/GSCraft/incoming/skadowsky/unpacked12/*/level.dat")[0]).replace(os.sep, "/")
plan = []


def add(source, source_dir, schunks, dest_id, dy, what, extra=None, dest_xz=None):
    d = sec[dest_id]; dx0, dz0 = dest_xz or (d["x0"], d["z0"])
    off = [dx0 // 16 - schunks[0], dz0 // 16 - schunks[1]]
    e = dict(source=source, source_dir=source_dir, chunks=list(schunks), offset=off, dy=dy, what=what,
             dest_blocks=[dx0, dz0, dx0 + (schunks[2] - schunks[0] + 1) * 16 - 1, dz0 + (schunks[3] - schunks[1] + 1) * 16 - 1],
             chunk_count=(schunks[2] - schunks[0] + 1) * (schunks[3] - schunks[1] + 1))
    if extra: e.update(extra)
    plan.append(e)


add("hub", v6["hub"]["source_dir"], v6["hub"]["chunks"], "hub", v6["hub"]["dy"] + (GROUND - 82), "Novo Expograd hub -> cyberpunk district at the ridge foot")
add("novo", v6["novo"]["source_dir"], v6["novo"]["chunks"], "novo", v6["novo"]["dy"] + (GROUND - 70), "Novo Expograd Industrial Zone; superflat source ground 230")
add("plaza", v6["plaza"]["source_dir"], v6["plaza"]["chunks"], "plaza", v6["plaza"]["dy"] + (GROUND - 70), "Financial Plaza; source ground 54")
p = sec["plaza"]
add("sewers", v6["sewers"]["source_dir"], v6["sewers"]["chunks"], "plaza", v6["sewers"]["dy"] + (GROUND - 70), "sewers under the plaza, sections below y 43 only",
    extra=dict(sections_below_y=48 + (GROUND - 70)), dest_xz=(p["x0"] + 32, p["z0"] + 32))
b = sec["biogen"]
add("biogen_s", v6["biogen_s"]["source_dir"], v6["biogen_s"]["chunks"], "biogen", v6["biogen_s"]["dy"] + (GROUND - 67), "Bio Gen south group", dest_xz=(b["x0"], b["z0"]))
add("biogen_n", v6["biogen_n"]["source_dir"], v6["biogen_n"]["chunks"], "biogen", v6["biogen_n"]["dy"] + (GROUND - 67), "Bio Gen north group", dest_xz=(b["x0"], b["z0"] + 80))
if "settle" in sec:
    add("settle", v6["settlement"]["source_dir"], v6["settlement"]["chunks"], "settle", v6["settlement"]["dy"] + (GROUND - 80), "the settlement (1.12 east compound); source ground 64")
add("skad", SKAD, [-30, -77, -2, -31], "skad", 35, "Region Skadowsky 1.2 sector; highway level 30 -> 65, its river stays low")
for sid, rect, dy, what in (("mega", (137, 25, 160, 57), -25, "Mega-base (live world), ground median 90"),
                            ("indu", (119, 54, 147, 70), -5, "Industrial district (live), ground 70"),
                            ("hemp", (98, 72, 117, 91), 0, "Hempcrete compound (live), ground 65"),
                            ("lib", (127, 87, 132, 92), -52, "Library (live), hill top 117")):
    if sid in sec: add(sid, LIVE, rect, sid, dy, what)
for i, o in enumerate(old):
    sid = f"old{i + 1:02d}"
    if sid in sec: add(sid, LIVE, o["chunks"], sid, GROUND - (o["ground_median"] or GROUND), f"old site {i + 1} as a farmstead; ground {o['ground_median']}")
out = REPO / "buildmap/plan_v8/transplant_plan_v8.json"
json.dump(plan, open(out, "w"), indent=1)
print(len(plan), "entries;", sum(e["chunk_count"] for e in plan), "chunks ->", out)
for e in plan:
    if not e["source"].startswith("old"): print(f"  {e['source']:10s} dy {e['dy']:5d} -> {e['dest_blocks']}")
print("settlement placed:", "settle" in sec)
