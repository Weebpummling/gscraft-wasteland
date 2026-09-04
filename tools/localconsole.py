"""Boot the LOCAL test server, run console commands, stop it. For the offline build's in-game steps
(placing tower stage 0, setting the world spawn, a boot check) without a player.

usage: localconsole.py <server dir> "<command>" ["<command>" ...] [--keep-running N] [--log-grep PATTERN]
  --keep-running N   wait N seconds after the last command before stopping (default 10)
  --log-grep PATTERN print console lines matching PATTERN (regex) at the end, e.g. "ERROR|gscraft"
Output: the console log is <server dir>/console-<timestamp>.log; the boot's error/warn counts are printed.
"""
import subprocess, sys, time, re
from pathlib import Path

JAVA = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot\bin\java.exe"


def main(a):
    if len(a) < 3: sys.exit(__doc__)
    sdir = Path(a[1]).resolve()
    keep = int(a[a.index("--keep-running") + 1]) if "--keep-running" in a else 10
    grep = a[a.index("--log-grep") + 1] if "--log-grep" in a else None
    pause = int(a[a.index("--pause") + 1]) if "--pause" in a else 2      # seconds between commands
    cmds = [c for c in a[2:] if not c.startswith("--") and c not in (str(keep), grep, str(pause))]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    logf = sdir / f"console-{stamp}.log"
    con = open(logf, "w", encoding="utf-8")
    argfile = "libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt"
    p = subprocess.Popen([JAVA, "@user_jvm_args.txt", f"@{argfile}", "nogui"], cwd=sdir,
                         stdin=subprocess.PIPE, stdout=con, stderr=subprocess.STDOUT, text=True)
    def tail(): return logf.read_text(encoding="utf-8", errors="replace")
    t0 = time.time()
    while "Done (" not in tail():
        if p.poll() is not None: print("server exited before Done; see", logf); return 1
        if time.time() - t0 > 1200: p.kill(); print("boot timeout"); return 1
        time.sleep(3)
    print(f"Done after {int(time.time() - t0)} s")
    for c in cmds:
        print(">", c)
        try:
            p.stdin.write(c + "\n"); p.stdin.flush()
        except OSError:
            print("server pipe closed (crashed?) - see", logf); break
        time.sleep(pause)
        if p.poll() is not None:
            print("server exited during commands; see", logf); break
    time.sleep(keep)
    for c in ("save-all flush", "stop"):
        try: p.stdin.write(c + "\n"); p.stdin.flush()
        except OSError: break
        time.sleep(2)
    try: p.wait(timeout=600)
    except subprocess.TimeoutExpired: p.kill(); print("stop timed out; killed")
    txt = tail()
    errs = [l for l in txt.splitlines() if "/ERROR]" in l]; warns = [l for l in txt.splitlines() if "/WARN]" in l]
    print(f"exit {p.returncode}; ERROR lines {len(errs)}, WARN lines {len(warns)}; log {logf}")
    if grep:
        for l in txt.splitlines():
            if re.search(grep, l): print("  " + l.strip()[:220])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
