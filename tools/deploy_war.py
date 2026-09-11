"""Hand-run deployment of the GSCraft War mod to the hosted Bisect server (HANDOFF section 6: panel calls that change
the server are run by a person, from PowerShell in tools/, with ~/.bisect/config.json in place). Owner (2026-09-10):
"Push the current version on live. Essentially the spawn mechanics of the normal overworld is now complete." Backup
verified and no players online by the owner before the run.

usage (PowerShell, in tools/):
    python deploy_war.py plan          # print every panel command, run nothing
    python deploy_war.py upload        # while the server still runs: mods, config, properties (about 420 MB)
    python deploy_war.py swap          # stop, swap the folders, properties, start
    python deploy_war.py status        # resources + tail of the log

What goes up (no world files - the deploy guard rule is not in play; the world folder is not touched):
  /mods_20260910    <- G:/GSCraft/server/mods: 108 jars = live's 110 minus In Control, Improved Mobs and TenshiLib,
                       plus gscraft-0.1.0.jar (the War mod)
  /config_20260910  <- G:/GSCraft/scratch/deploy_war/config: the local config without the *.bak* files, with
                       hordes-common.toml pauseEventServer = true (live keeps it; only the local test server runs false).
                       Carries: Hordes infection_entities with the Bloater and the Matron, Zombie Awareness enhancedMobs,
                       Eyes in the Darkness EnableNaturalSpawn = false (the director places the Eyes), no incontrol/,
                       no improvedmobs/
  /server.properties.war <- build/phase03/server.properties.war: live's properties with difficulty=hard (the mod's
                       bodies are Monsters; peaceful removes them) and the MOTD; spawn-monsters stays false (nothing
                       spawns naturally - the director places, and the hold refuses everything else)
The swap: stop; /mods -> /mods_old_20260910, /mods_20260910 -> /mods (same for config); properties swapped; start.
/kubejs (gscraft_recipes.js) and /defaultconfigs are not touched. The world's gscraft datapack keeps its old
spawns_on/spawns_off functions; they are inert without In Control.
Rollback: the reverse renames and /server.properties.v8-live back to /server.properties.
After the start the log should show the four [gscraft] load lines (factions, ranks, zones, sites/locks/drops) and Done.
"""
import subprocess, sys, os, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRV = Path("G:/GSCraft/server"); STAGE = Path("G:/GSCraft/scratch/deploy_war"); B = HERE.parent / "build"
STAMP = "20260910"


def panel(*args, run=True):
    cmd = [sys.executable, str(HERE / "bisectpanel.py"), *args]
    print(">", " ".join(a if " " not in a else f'"{a}"' for a in cmd[2:]), flush=True)
    if not run: return ""
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "MSYS_NO_PATHCONV": "1"})
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0: print("  !!", out.strip()[-400:], flush=True)
    return out


def tree_dirs(local, remote):
    out = [(remote, local)]
    for p in sorted(x for x in local.rglob("*") if x.is_dir()):
        out.append((remote + "/" + p.relative_to(local).as_posix(), p))
    return out


def upload(run):
    panel("mkdir", f"/mods_{STAMP}", run=run); panel("putdir", str(SRV / "mods"), f"/mods_{STAMP}", run=run)
    for rd, ld in tree_dirs(STAGE / "config", f"/config_{STAMP}"):
        panel("mkdir", rd, run=run); panel("putdir", str(ld), rd, run=run)
    panel("put", str(B / "phase03" / "server.properties.war"), "/", run=run)


def swap(run):
    panel("power", "stop", run=run)
    if run:
        for _ in range(30):
            time.sleep(10)
            if "offline" in panel("resources", run=True).lower(): break
    for name in ("mods", "config"):
        panel("mv", f"/{name}", f"/{name}_old_{STAMP}", run=run); panel("mv", f"/{name}_{STAMP}", f"/{name}", run=run)
    panel("mv", "/server.properties", "/server.properties.v8-live", run=run)
    panel("mv", "/server.properties.war", "/server.properties", run=run)
    panel("power", "start", run=run)
    print("then, after two minutes: python deploy_war.py status  (expect Done and the [gscraft] load lines)")


def status():
    print(panel("resources")); print(panel("cat", "/logs/latest.log")[-3000:])


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if a == "plan": upload(False); swap(False)
    elif a == "upload": upload(True)
    elif a == "swap": swap(True)
    elif a == "status": status()
    else: sys.exit(__doc__)
