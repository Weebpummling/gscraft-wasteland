"""Blend the land around every placed v8 build into its ground level with grade.py (falloff 48 blocks; every column
inside the footprint is left alone; buildings beyond the footprint are kept). usage: grade_v8.py <world dir> [--dry-run]"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
world = sys.argv[1]; dry = "--dry-run" in sys.argv
sec = json.load(open(HERE.parent / "buildmap/plan_v8/sectors_v8.json"))["sectors"]
for p in sec:
    if p["id"] == "camp": continue                    # the camp is graded with its own basin later (camp pass)
    args = [sys.executable, str(HERE / "grade.py"), world, str(p["x0"]), str(p["z0"]), str(p["x1"]), str(p["z1"]), "--y", "65", "--falloff", "48",
            "--protect", str(p["x0"]), str(p["z0"]), str(p["x1"]), str(p["z1"]), "--keep-built-beyond", "0", "--label", p["id"], "--fill", "minecraft:dirt", "--top", "minecraft:grass_block", "--repaint", "minecraft:terracotta"]
    if dry: args.append("--dry-run")
    r = subprocess.run(args, capture_output=True, text=True); print((r.stdout + r.stderr).strip().splitlines()[-2:])
