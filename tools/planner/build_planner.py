"""Build the Wasteland Road Plan page: tools/planner/planner_template.html + plan_defaults.json -> one HTML file,
published as a Claude artifact with the `db` capability (https://claude.ai/code/artifact/5e91332d-e204-4c97-8905-64ebfb9de8f3).
usage: build_planner.py <out.html>
A blank canvas: the world border, every element with its real footprint (camp, the Skadowsky sector, each preserved
player build, pads) at a default position, city/wilderness zones, and a road generator (spanning tree from the camp's
gates plus optional rings, bends that swing around other elements). The owner repositions everything and saves;
Save writes plans/current in the artifact database, read back with the Artifact tool's read_db; the build tools
generate the world to fit it (terrain plan, Lost Cities inside city zones, transplants, roads graded in one pass).
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = Path(sys.argv[1])
data = json.load(open(HERE / "plan_defaults.json", encoding="utf-8"))
html = (HERE / "planner_template.html").read_text(encoding="utf-8").replace("__DATA__", json.dumps(data))
out.write_text(html, encoding="utf-8"); print(out, len(html) // 1024, "KB")
