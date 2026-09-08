"""Safe world deploys: pull the live world first, apply the queued changes, then push.

Written after 2026-09-07, when a world upload overwrote a player's five-hour session. The staged copy
on this machine had no knowledge of that session, and the check that was supposed to catch it - "has
anyone been on?" - read the server's *current* log, which had rotated at the last restart and so did
not contain the session at all. The lesson is that no amount of log reading is a substitute for
comparing bytes: the only safe question is whether the live file still matches the one our edit was
built on.

So the guard is a rule, not a heuristic: **a region file may only be uploaded if this run pulled that
exact file from the live server first, and the live copy has not changed since.** There is no flag to
skip it. If the live file moved under us, the push stops and says which regions drifted.

    deployguard.py queue <tool> [args...]      add a world change to the pending queue
    deployguard.py queue --list                show what is pending
    deployguard.py queue --clear               drop the queue
    deployguard.py run [--dry-run] [--now]     the whole sequence, below
    deployguard.py status                      backup, server state, queue depth

`run` does, in order:
  1. refuse to start if the queue is empty
  2. take a backup through the panel and wait for it to finish; if the panel refuses (the plan's
     backup limit is zero) the run stops here unless --allow-no-backup is given
  3. stop the server
  4. pull every region, entity and poi file of the live world into the staging directory, recording
     the sha256 of each as pulled
  5. run each queued tool against the staging world
  6. upload only the files the tools changed, checking first that the live copy still hashes to what
     step 4 pulled
  7. start the server, and archive the queue

Step 4 is a full pull, about 900 MB. That is the price of never having to guess again.

**Run this by hand, at 04:00, after the host's own backup has finished** (owner, 2026-09-07). It is
deliberately not scheduled on the build machine: the PC is not always awake, and a deploy that fires
unattended into a world someone is playing is the failure this tool exists to prevent. 04:00 is when
the server is reliably empty, and going after the backup means there is always something to roll back
to. Check `deployguard.py status` first: it prints the server state, the age of the last backup and
what is queued.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bisectpanel as bp  # noqa: E402

STAGE = Path(r"G:/GSCraft/scratch/deploy_stage")
QUEUE = HERE / "deploy_queue.json"
HISTORY = HERE / "deploy_history"
REMOTE_WORLD = "/wasteland-v8"
LOCAL_WORLD_NAME = "wasteland-v8"
SUBDIRS = ("region", "entities", "poi")
BACKUP_MAX_AGE_H = 6


def sha(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- queue

def load_queue():
    return json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.exists() else []


def save_queue(q):
    QUEUE.write_text(json.dumps(q, indent=1), encoding="utf-8", newline="")


def cmd_queue(argv):
    if "--list" in argv:
        q = load_queue()
        if not q:
            print("queue is empty")
            return 0
        for i, e in enumerate(q, 1):
            print(f"{i}. {e['tool']} {' '.join(e['args'])}\n     added {e['added']}  {e.get('note','')}")
        return 0
    if "--clear" in argv:
        save_queue([])
        print("queue cleared")
        return 0
    if not argv:
        sys.exit("usage: deployguard.py queue <tool.py> [args...] | --list | --clear")
    tool = argv[0]
    if not (HERE / tool).exists():
        sys.exit(f"no such tool: {tool}")
    q = load_queue()
    q.append({"tool": tool, "args": list(argv[1:]),
              "added": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    save_queue(q)
    print(f"queued: {tool} {' '.join(argv[1:])}  ({len(q)} pending)")
    return 0


# ---------------------------------------------------------------- panel

def server_state(cfg):
    d = bp.request(cfg, "GET", f"/api/client/servers/{cfg['server']}/resources")
    return (d or {}).get("attributes", {}).get("current_state", "?")


def wait_state(cfg, want, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = server_state(cfg)
        if s == want:
            return True
        time.sleep(5)
    return False


def latest_backup(cfg):
    d = bp.request(cfg, "GET", f"/api/client/servers/{cfg['server']}/backups")
    rows = [r["attributes"] for r in (d or {}).get("data", [])]
    done = [a for a in rows if a.get("completed_at") and a.get("is_successful", True)]
    if not done:
        return None
    done.sort(key=lambda a: a["completed_at"], reverse=True)
    return done[0]


def take_backup(cfg, allow_none):
    name = "deployguard " + datetime.now().strftime("%Y-%m-%d %H%M")
    try:
        d = bp.request(cfg, "POST", f"/api/client/servers/{cfg['server']}/backups",
                       body={"name": name, "is_locked": False})
    except SystemExit as e:
        log(f"the panel refused a backup: {str(e)[:160]}")
        if allow_none:
            log("--allow-no-backup given, going on without one")
            return None
        sys.exit("stopping: no backup could be taken. Enable backups on the plan, or pass "
                 "--allow-no-backup if you accept the risk.")
    uid = (d or {}).get("attributes", {}).get("uuid")
    log(f"backup started: {uid}")
    t0 = time.time()
    while time.time() - t0 < 3600:
        time.sleep(15)
        a = latest_backup(cfg)
        if a and a["uuid"] == uid:
            log(f"backup finished: {bp.human(a.get('bytes', 0))}")
            return a
    sys.exit("stopping: the backup did not finish within the hour")


# ---------------------------------------------------------------- pull / push

def assert_offline(cfg, why):
    """A running server rewrites region files under us - r.-7.-3 hashed differently on three pulls
    two seconds apart while the server was up, and a quiet region hashed the same. So both the pull
    and the verify are only meaningful with the server stopped, and we check rather than assume."""
    s = server_state(cfg)
    if s != "offline":
        sys.exit(f"stopping: the server is {s} and {why} is only safe while it is offline")


def pull_world(cfg):
    """Every world file, live -> staging, with the hash of each as pulled."""
    assert_offline(cfg, "pulling the world")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    manifest = {}
    n = 0
    for sub in SUBDIRS:
        (STAGE / LOCAL_WORLD_NAME / sub).mkdir(parents=True, exist_ok=True)
        d = bp.request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/list",
                       params={"directory": f"{REMOTE_WORLD}/{sub}"})
        for row in (d or {}).get("data", []):
            a = row["attributes"]
            if not a.get("is_file") or not a["name"].endswith(".mca"):
                continue
            dest = STAGE / LOCAL_WORLD_NAME / sub / a["name"]
            bp.download(cfg, f"{REMOTE_WORLD}/{sub}/{a['name']}", dest)
            manifest[f"{sub}/{a['name']}"] = sha(dest)
            n += 1
            if n % 25 == 0:
                log(f"  pulled {n} files")
    (STAGE / "pulled.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    log(f"pulled {n} world files into the staging copy")
    return manifest


def push(cfg, manifest, dry):
    """Upload what the tools changed, but only where live still matches what we pulled."""
    world = STAGE / LOCAL_WORLD_NAME
    changed, drifted = [], []
    for rel, want in manifest.items():
        p = world / rel
        if not p.exists():
            continue
        if sha(p) != want:
            changed.append(rel)
    log(f"{len(changed)} files changed by the queued tools")
    if not changed:
        return 0
    # the guard: re-read each live file and check it is still the one we based the edit on
    assert_offline(cfg, "verifying against live")
    tmp = STAGE / "_verify"
    tmp.mkdir(exist_ok=True)
    for rel in changed:
        dest = tmp / rel.replace("/", "_")
        bp.download(cfg, f"{REMOTE_WORLD}/{rel}", dest)
        if sha(dest) != manifest[rel]:
            drifted.append(rel)
        dest.unlink(missing_ok=True)
    if drifted:
        print("\nGUARD STOPPED THE PUSH. These files changed on the server after we pulled them:")
        for r in drifted:
            print("   ", r)
        print("Nothing was uploaded. Someone was on, or the server saved over them. Re-run the whole\n"
              "sequence so the changes are rebuilt on the current world.")
        return 1
    log("guard passed: every file still matches what we pulled")
    if dry:
        log("dry run, nothing uploaded")
        return 0
    for i, rel in enumerate(changed, 1):
        sub = rel.split("/")[0]
        bp.cmd_put(str(world / rel), f"{REMOTE_WORLD}/{sub}")
        if i % 20 == 0:
            log(f"  uploaded {i}/{len(changed)}")
    log(f"uploaded {len(changed)} files")
    return 0


# ---------------------------------------------------------------- run

def cmd_run(argv):
    dry = "--dry-run" in argv
    allow_none = "--allow-no-backup" in argv
    q = load_queue()
    if not q:
        log("queue is empty, nothing to deploy")
        return 0
    log(f"{len(q)} queued change(s)")
    cfg = bp.load_config()

    a = latest_backup(cfg)
    age = None
    if a:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(a["completed_at"].replace("Z", "+00:00"))).total_seconds() / 3600
    if a and age is not None and age < BACKUP_MAX_AGE_H:
        log(f"using the existing backup from {age:.1f} h ago")
    else:
        take_backup(cfg, allow_none)

    if server_state(cfg) != "offline":
        log("stopping the server")
        bp.request(cfg, "POST", f"/api/client/servers/{cfg['server']}/power", body={"signal": "stop"})
        if not wait_state(cfg, "offline"):
            sys.exit("stopping: the server would not go offline")
    log("server is offline")

    manifest = pull_world(cfg)

    for e in q:
        cmd = [sys.executable, str(HERE / e["tool"]), str(STAGE / LOCAL_WORLD_NAME)] + e["args"]
        log(f"applying {e['tool']} {' '.join(e['args'])}")
        r = subprocess.run(cmd, cwd=str(HERE))
        if r.returncode != 0:
            sys.exit(f"stopping: {e['tool']} exited {r.returncode}; nothing has been uploaded")

    rc = push(cfg, manifest, dry)

    log("starting the server")
    bp.request(cfg, "POST", f"/api/client/servers/{cfg['server']}/power", body={"signal": "start"})
    wait_state(cfg, "running", timeout=600)
    log(f"server state: {server_state(cfg)}")

    if rc == 0 and not dry:
        HISTORY.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        (HISTORY / f"{stamp}.json").write_text(json.dumps(q, indent=1), encoding="utf-8")
        save_queue([])
        log(f"queue archived to deploy_history/{stamp}.json and cleared")
    return rc


def cmd_status(argv):
    cfg = bp.load_config()
    print("server state :", server_state(cfg))
    a = latest_backup(cfg)
    if a:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(a["completed_at"].replace("Z", "+00:00"))).total_seconds() / 3600
        print(f"last backup  : {a['name']}  {bp.human(a.get('bytes',0))}  {age:.1f} h ago")
    else:
        print("last backup  : NONE - the panel reports no completed backup")
    q = load_queue()
    print(f"queue        : {len(q)} pending")
    for e in q:
        print(f"   {e['tool']} {' '.join(e['args'])}")
    return 0


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    sub = argv[1]
    if sub == "queue":
        return cmd_queue(argv[2:])
    if sub == "run":
        return cmd_run(argv[2:])
    if sub == "status":
        return cmd_status(argv[2:])
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
