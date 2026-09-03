"""Stage the public repo at C:\\GSCraft\\repo from C:\\GSCraft\\tools + the session pages.
Excludes mod jars, the client zip, world pulls, backups, and anything with a token.
"""
import shutil, sys, json, re
from pathlib import Path

TOOLS = Path(r"C:\GSCraft\tools")
SP = Path(r"C:\GSCraft\scratch")
REPO = Path(r"C:\GSCraft\repo")

SCRIPTS = ["bisectpanel.py", "scanregion.py", "buildmap.py", "planblocks.py", "makeremap.py", "transplant.py",
           "runplan.py", "fixspawners.py", "findid.py", "loottally.py", "anvil.py", "terrain.py", "runpass.py",
           "strongpoints.py", "pregen.py", "spawnmap.py", "spawnsurvey.py", "roofgrid.py", "topblocks.py",
           "worldscan.py", "scancompare.py", "topdown.py", "backup.py", "mcping.py", "stage_repo.py"]
DATA = ["remap.json", "remap_full.json", "remap_todo.json", "strongpoints.json", "pad_heights.json", "pregen_rects.json"]
BUILD_DIRS = ["datapacks", "kubejs", "phase02", "phase03", "phase05", "phase04"]
BUILD_FILES = ["manifest.json", "additions.json"]
CLIENT = ["GSCraft Install Guide.md", "GSCraft Install Guide.html", "GSCraft/mmc-pack.json", "GSCraft/instance.cfg"]
PAGES = ["wasteland-server-blueprint.html", "gscraft-server-audit.html", "wasteland-district-map.html", "makemap.py"]
BUILDMAP = ["transplant_plan.json", "site_inventory.json", "site_rects_live.json", "builds.json", "gaps.txt"]
SCANS = ["efm_overworld_topdown.png", "zip_overworld_topdown.png", "live_overworld_topdown.png", "live_complex.png",
         "new_complex.png", "new_overview.png"]


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir(): shutil.copytree(src, dst, dirs_exist_ok=True)
    else: shutil.copy2(src, dst)


def main():
    if REPO.exists() and not (REPO / ".git").exists(): shutil.rmtree(REPO)
    REPO.mkdir(parents=True, exist_ok=True)
    for f in SCRIPTS: copy(TOOLS / f, REPO / "tools" / f)
    for f in DATA: copy(TOOLS / f, REPO / "tools" / f)
    for d in BUILD_DIRS:
        if (TOOLS / "build" / d).exists(): copy(TOOLS / "build" / d, REPO / "build" / d)
    for f in BUILD_FILES: copy(TOOLS / "build" / f, REPO / "build" / f)
    for f in CLIENT: copy(TOOLS / "build" / "client" / f, REPO / "client" / Path(f).name)
    for f in PAGES: copy(SP / f, REPO / "docs" / f)
    for f in BUILDMAP:
        if (SP / "worlds" / "buildmap" / f).exists(): copy(SP / "worlds" / "buildmap" / f, REPO / "buildmap" / f)
    for f in SCANS:
        if (SP / "scan" / f).exists(): copy(SP / "scan" / f, REPO / "docs" / "renders" / f)
    # strip anything that could carry a secret: the tool reads its token from ~/.bisect, never here
    bad = [p for p in REPO.rglob("*") if p.is_file() and p.suffix in {".jar", ".zip", ".mca"}]
    for p in bad: p.unlink()
    for p in REPO.rglob("*"):
        if p.is_file() and p.suffix in {".py", ".json", ".md", ".toml", ".cfg", ".js", ".html", ".txt", ".properties"}:
            t = p.read_text(encoding="utf-8", errors="replace")
            assert not re.search(r"ptlc_[A-Za-z0-9]{20,}", t), f"token-like string in {p}"
    (REPO / ".gitignore").write_text("*.jar\n*.zip\n*.mca\npull/\nworlds/\n__pycache__/\n*.log\n", encoding="utf-8")
    n = sum(1 for p in REPO.rglob("*") if p.is_file())
    size = sum(p.stat().st_size for p in REPO.rglob("*") if p.is_file())
    print(f"staged {n} files, {size/1e6:.1f} MB at {REPO}")


if __name__ == "__main__":
    main()
