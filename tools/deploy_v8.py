"""Hand-run deployment of the v8 world to the hosted Bisect server (HANDOFF §6: panel calls that change the server are run
by a person, from PowerShell in tools/, with ~/.bisect/config.json in place). Owner (2026-09-05): "upload the current map
onto the server, and restart the server with enemies turned off; gameplay is worked on locally, scripting on the server
only when finalised".

usage (PowerShell, in tools/):
    python deploy_v8.py plan          # print every panel command, run nothing
    python deploy_v8.py upload        # while the old server still runs: world, mods, configs, properties (about 1.3 GB)
    python deploy_v8.py swap          # stop, swap folders, scripts off, start, then check the log
    python deploy_v8.py status        # resources + tail of the log

What goes up:
  /wasteland-v8           <- G:/GSCraft/server/wasteland-v8: level.dat, region (189 files, 616 MB), entities, data (without the
                             1,282 local map_*.dat items and DistantHorizons.sqlite), serverconfig, datapacks (gscraft_worldgen,
                             gscraft_lcfix - not the gameplay datapack)
  /mods_20260905          <- G:/GSCraft/server/mods (103 jars, 414 MB: the 2026-09-05 update set, Superb Warfare 0.8.8)
  /config_20260905        <- G:/GSCraft/server/config (the configs the new versions wrote on the local boot)
  /defaultconfigs_20260905<- G:/GSCraft/server/defaultconfigs
  /server.properties.v8   <- build/phase03/server.properties.v8 (difficulty=peaceful, spawn-monsters=false, level-name=wasteland-v8)
The swap: stop; /mods -> /mods_old_20260905, /mods_20260905 -> /mods (same for config, defaultconfigs); /kubejs ->
/kubejs_off_20260905 (no scripts); properties swapped; start. Forge stays 47.4.10 on the host (every mod's range accepts it;
the 47.4.23 move is a separate hand-run step). Rollback: the reverse renames and the old properties.
"""
import subprocess, sys, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path("G:/GSCraft/server/wasteland-v8"); SRV = Path("G:/GSCraft/server"); B = HERE.parent / "build"
STAMP = "20260905"
SKIP_DATA = lambda p: p.name.startswith("map_") or p.name == "DistantHorizons.sqlite"


def panel(*args, run=True):
    cmd = [sys.executable, str(HERE / "bisectpanel.py"), *args]
    print(">", " ".join(a if " " not in a else f'"{a}"' for a in cmd[2:]), flush=True)
    if not run: return ""
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "MSYS_NO_PATHCONV": "1"})
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0: print("  !!", out.strip()[-400:], flush=True)
    return out


def tree_dirs(local, remote):
    """(remote dir, local dir) pairs for every directory under local, parents first."""
    out = [(remote, local)]
    for p in sorted(x for x in local.rglob("*") if x.is_dir()):
        out.append((remote + "/" + p.relative_to(local).as_posix(), p))
    return out


def upload(run):
    upload_world(run); upload_pack(run)


def upload_world(run):
    panel("mkdir", "/wasteland-v8", run=run)
    for sub in ("region", "entities", "serverconfig"):
        for rd, ld in tree_dirs(W / sub, f"/wasteland-v8/{sub}"):
            panel("mkdir", rd, run=run); panel("putdir", str(ld), rd, run=run)
    panel("mkdir", "/wasteland-v8/data", run=run)
    for f in sorted(W.glob("data/*")):
        if f.is_file() and not SKIP_DATA(f): panel("put", str(f), "/wasteland-v8/data", run=run)
    for dp in ("gscraft_worldgen", "gscraft_lcfix"):
        for rd, ld in tree_dirs(W / "datapacks" / dp, f"/wasteland-v8/datapacks/{dp}"):
            panel("mkdir", rd, run=run); panel("putdir", str(ld), rd, run=run)
    panel("put", str(W / "level.dat"), "/wasteland-v8", run=run)


def upload_pack(run):
    panel("mkdir", f"/mods_{STAMP}", run=run); panel("putdir", str(SRV / "mods"), f"/mods_{STAMP}", run=run)
    for rd, ld in tree_dirs(SRV / "config", f"/config_{STAMP}"):
        panel("mkdir", rd, run=run); panel("putdir", str(ld), rd, run=run)
    for rd, ld in tree_dirs(SRV / "defaultconfigs", f"/defaultconfigs_{STAMP}"):
        panel("mkdir", rd, run=run); panel("putdir", str(ld), rd, run=run)
    panel("put", str(B / "phase03" / "server.properties.v8"), "/", run=run)


def swap(run):
    panel("power", "stop", run=run)
    if run:
        import time
        for _ in range(30):
            time.sleep(10)
            if "offline" in panel("resources", run=True).lower(): break
    for name in ("mods", "config", "defaultconfigs"):
        panel("mv", f"/{name}", f"/{name}_old_{STAMP}", run=run); panel("mv", f"/{name}_{STAMP}", f"/{name}", run=run)
    panel("mv", "/kubejs", f"/kubejs_off_{STAMP}", run=run)                       # scripting off until the gameplay side is final
    panel("mv", "/server.properties", "/server.properties.v7", run=run)
    panel("mv", "/server.properties.v8", "/server.properties", run=run)
    panel("power", "start", run=run)
    print("then, after two minutes: python deploy_v8.py status  (expect Done, the benign error set, no [gscraft] lines - scripts are off)")


def status():
    print(panel("resources")); print(panel("cat", "/logs/latest.log")[-3000:])


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if a == "plan": upload(False); swap(False)
    elif a == "upload": upload(True)
    elif a == "upload-pack": upload_pack(True)
    elif a == "upload-world": upload_world(True)
    elif a == "swap": swap(True)
    elif a == "status": status()
    else: sys.exit(__doc__)
