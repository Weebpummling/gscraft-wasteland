"""Phase B world build, v6 layout (docs/gscraft-map-layout-v6.md), offline on a copy of the world.

usage: buildv6.py <pregenerated world dir> <build world dir> [--pads pads_v6.json] [--plan transplant_plan_v6.json]
                  [--pristine <pristine region dir>] [--only step,step] [--dry-run]

Steps, in order (each can be selected with --only):
  copy       copy region/, entities/, level.dat and data/ of the pregenerated world into the build dir (poi/ left out)
  restore    put the old substation and hospital pads (and their ramps) back from the pristine v2 region set
  pads       terrain.py pad for every entry of pads_v6.json at its level (tower, Novo, plaza, settlement, airfield, hub)
  transplant runplan.py over transplant_plan_v6.json into the build dir (dy and section stacking included)
  smooth     terrain.py smooth: ramp the generated terrain to every transplant edge
  clearring  clear generated buildings within 24 blocks outside each site pad (no cut facades)
  ramps      terrain.py ramp around every pad at its level
  campads    small pads + ramps for the six NPC building sites (pads_camp.json), crater and tower protected
  gaps       terrain.py gaps report over the plan (edges of every transplant)
Roads and the camp buildings are not here: roads wait for the Phase A visual-pass list, the camp
buildings for camp.py. Tower stage 0 is placed in-game afterwards (localconsole.py "function
gscraft:tower_stage_0").
"""
import json, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
RESTORE_RECTS = [(7, 82, 29, 104),      # old substation pad + its ramp margin
                 (36, 141, 60, 166)]    # old hospital pad + margin (the plaza moved to dry land; the lake comes back)


def run(*args):
    print("$", " ".join(str(a) for a in args), flush=True)
    r = subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, text=True, capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out: print(out[-3000:], flush=True)
    if r.returncode: sys.exit(f"step failed: {args[0]}")
    return out


def step_copy(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("region", "entities"):
        if (dst / name).exists(): shutil.rmtree(dst / name)
        if (src / name).exists(): shutil.copytree(src / name, dst / name)
    for name in ("level.dat", "level.dat_old"):
        if (src / name).exists(): shutil.copy2(src / name, dst / name)
    if (src / "data").exists():
        if (dst / "data").exists(): shutil.rmtree(dst / "data")
        shutil.copytree(src / "data", dst / "data")
    if (dst / "poi").exists(): shutil.rmtree(dst / "poi")
    print(f"copied {len(list((dst / 'region').glob('*.mca')))} region files to {dst}")


def step_restore(dst: Path, pristine: Path):
    plan = [{"source": "pristine", "source_dir": str(pristine.parent), "chunks": list(r), "offset": [0, 0],
             "what": "old pad + ramps back to pre-edit terrain"} for r in RESTORE_RECTS]
    pf = dst / "restore_plan.json"; json.dump(plan, open(pf, "w"), indent=1)
    run(HERE / "runplan.py", "--plan", pf, "--dst", dst, "--remap", HERE / "remap_full.json")


def step_pads(dst: Path, pads, dry):
    for p in pads:
        x1, z1, x2, z2 = p["blocks"]
        args = [HERE / "terrain.py", "pad", dst, x1, z1, x2, z2, "--y", p["y"], "--label", p["name"]]
        for pr in p.get("protect", []): args += ["--protect", *pr]
        if not p.get("outline", True): args.append("--no-outline")     # a transplant's foundation is not a marked lot
        if dry: args.append("--dry-run")
        run(*args)


def step_transplant(dst: Path, plan: Path, dry):
    args = [HERE / "runplan.py", "--plan", plan, "--dst", dst, "--remap", HERE / "remap_full.json"]
    if dry: args.append("--dry-run")
    run(*args)


CRATER = ["-16", "-16", "47", "47"]
TOWER = ["64", "-144", "191", "-17"]


def step_campads(dst: Path, dry):
    """Small pads for the six NPC building sites on the camp rim (pads_camp.json), then their ramps."""
    pads = json.load(open(HERE / "pads_camp.json"))
    for p in pads:
        x1, z1, x2, z2 = p["blocks"]
        args = [HERE / "terrain.py", "pad", dst, x1, z1, x2, z2, "--y", p["y"], "--protect", *CRATER, *TOWER, "--label", p["name"]]
        if dry: args.append("--dry-run")
        run(*args)
    for p in pads:
        x1, z1, x2, z2 = p["blocks"]
        args = [HERE / "terrain.py", "ramp", dst, x1, z1, x2, z2, "--y", p["y"], "--label", p["name"]]
        if dry: args.append("--dry-run")
        run(*args)


def step_clearring(dst: Path, pads, dry, margin=24):
    """Clear generated buildings in a ring outside each site pad (cut facades at the pad edge), before ramps."""
    for p in pads:
        if p["name"] in ("radio_tower", "airfield"): continue
        x1, z1, x2, z2 = p["blocks"]
        args = [HERE / "terrain.py", "pad", dst, x1 - margin, z1 - margin, x2 + margin, z2 + margin,
                "--protect", x1, z1, x2, z2, "--label", p["name"] + "_ring", "--clear-only"]
        if dry: args.append("--dry-run")
        run(*args)


def step_smooth(dst: Path, plan: Path, dry):
    args = [HERE / "terrain.py", "smooth", dst, plan]
    if dry: args.append("--dry-run")
    run(*args)


def step_ramps(dst: Path, pads, dry):
    for p in pads:
        x1, z1, x2, z2 = p["blocks"]
        args = [HERE / "terrain.py", "ramp", dst, x1, z1, x2, z2, "--y", p["y"], "--label", p["name"]]
        if dry: args.append("--dry-run")
        run(*args)


def step_gaps(dst: Path, plan: Path):
    run(HERE / "terrain.py", "gaps", dst, plan)


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    src, dst = Path(a[1]), Path(a[2])
    pads = json.load(open(a[a.index("--pads") + 1] if "--pads" in a else HERE / "pads_v6.json"))
    plan = Path(a[a.index("--plan") + 1]) if "--plan" in a else HERE.parent / "buildmap" / "transplant_plan_v6.json"
    pristine = Path(a[a.index("--pristine") + 1]) if "--pristine" in a else Path(r"G:/GSCraft/scratch/worlds/wasteland/region")
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else {"copy", "restore", "pads", "transplant", "smooth", "clearring", "ramps", "campads", "gaps"}
    dry = "--dry-run" in a
    t0 = time.time()
    if "copy" in only: step_copy(src, dst)
    if "restore" in only: step_restore(dst, pristine)
    if "pads" in only: step_pads(dst, pads, dry)
    if "transplant" in only: step_transplant(dst, plan, dry)
    if "smooth" in only: step_smooth(dst, plan, dry)
    if "clearring" in only: step_clearring(dst, pads, dry)
    if "ramps" in only: step_ramps(dst, pads, dry)
    if "campads" in only: step_campads(dst, dry)
    if "gaps" in only: step_gaps(dst, plan)
    print(f"build v6 done in {int(time.time() - t0)} s -> {dst}")


if __name__ == "__main__":
    main(sys.argv)
