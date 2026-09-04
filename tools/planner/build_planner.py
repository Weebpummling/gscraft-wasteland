"""Build the Wasteland Road Plan page (tools/planner/planner_template.html + plan_defaults.json + a JPEG of the
world render) into one HTML file, ready to publish as a Claude artifact with the `db` capability.
usage: build_planner.py <overview render png> <out.html>
The page draws the road network, moveable site boxes, city/wilderness zones and the map border over the render
(1 px = 8 blocks, origin x -3104 z -3760 for the v6/v7 box) and saves the plan to the artifact database at
plans/current; the assistant reads it back with the Artifact tool (read_db) and feeds roads.json / pads / zones.
Published 2026-09-04: https://claude.ai/code/artifact/5e91332d-e204-4c97-8905-64ebfb9de8f3
"""
import base64, io, json, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
png, out = Path(sys.argv[1]), Path(sys.argv[2])
buf = io.BytesIO(); Image.open(png).convert("RGB").save(buf, "JPEG", quality=78, optimize=True)
bg = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
data = json.load(open(HERE / "plan_defaults.json", encoding="utf-8"))
html = (HERE / "planner_template.html").read_text(encoding="utf-8").replace('"__BG__"', json.dumps(bg)).replace("__DATA__", json.dumps(data))
out.write_text(html, encoding="utf-8"); print(out, len(html) // 1024, "KB")
