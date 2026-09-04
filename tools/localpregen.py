"""Pre-generate the wasteland world on the LOCAL test server with Chunky, driving the server console,
cycling the server every batch of chunks because Lost Cities' per-chunk caches only clear on a restart
(two 10 km attempts died of OutOfMemory at 8 GB and 20 GB heap, at 43k and 67k chunks).

usage: localpregen.py <server dir> [--center X Z] [--radius R] [--border] [--batch N] [--dry-run]
defaults: center 1900 1250, radius 5000 (a 10 km square), batch 12000 chunks per server life.

Cycle: start server -> wait Done -> (first life only: worldborder if --border, chunky world/shape/
center/radius/start; later lives: chunky continue) -> poll Chunky's progress -> after N chunks or
when the JVM working set passes 14 GB: chunky pause, save-all, stop -> next life. Ends on Chunky's
"Task finished". Progress lines go to <server dir>/pregen.log; each life's console to
pregen-console-<n>.log. Chunky keeps its own task file (config/chunky/tasks), so a killed run resumes.
"""
import subprocess, sys, time, re
from pathlib import Path

JAVA = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot\bin\java.exe"
WS_LIMIT_MB = 14000


def ws_mb(pid):
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
        m = re.search(r'"([\d,\.]+) K"', out)
        return int(m.group(1).replace(",", "").replace(".", "")) // 1024 if m else 0
    except Exception:
        return 0


def main(a):
    if len(a) < 2: sys.exit(__doc__)
    sdir = Path(a[1]).resolve()
    cx, cz = (int(a[a.index("--center") + 1]), int(a[a.index("--center") + 2])) if "--center" in a else (1900, 1250)
    radius = int(a[a.index("--radius") + 1]) if "--radius" in a else 5000
    batch = int(a[a.index("--batch") + 1]) if "--batch" in a else 12000
    level = next((l.split("=", 1)[1].strip() for l in (sdir / "server.properties").read_text().splitlines()
                  if l.startswith("level-name=")), "world")
    first = [f"chunky world {level}", "chunky shape square", f"chunky center {cx} {cz}", f"chunky radius {radius}", "chunky start"]
    if "--border" in a:
        first = [f"worldborder center {cx} {cz}", f"worldborder set {radius * 2}"] + first
    if "--dry-run" in a:
        print("\n".join(first)); return 0
    log = open(sdir / "pregen.log", "a", encoding="utf-8")
    def note(s):
        line = f"[{time.strftime('%H:%M:%S')}] {s}"; print(line, flush=True); log.write(line + "\n"); log.flush()
    argfile = "libraries/net/minecraftforge/forge/1.20.1-47.4.10/win_args.txt"
    life = 0; t_all = time.time(); finished = False; total_seen = 0
    while not finished and life < 60:
        life += 1
        (sdir / f"{level}/session.lock").unlink(missing_ok=True)
        conf = sdir / f"pregen-console-{life}.log"
        con = open(conf, "w", encoding="utf-8")
        p = subprocess.Popen([JAVA, "@user_jvm_args.txt", f"@{argfile}", "nogui"], cwd=sdir,
                             stdin=subprocess.PIPE, stdout=con, stderr=subprocess.STDOUT, text=True)
        note(f"life {life}: server pid {p.pid}")
        def tail(): return conf.read_text(encoding="utf-8", errors="replace")
        def send(c):
            p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(1.5)
        t0 = time.time()
        while "Done (" not in tail():
            if p.poll() is not None: note("server exited before Done"); return 1
            if time.time() - t0 > 1200: p.kill(); note("boot timeout"); return 1
            time.sleep(3)
        note(f"life {life}: Done after {int(time.time() - t0)} s")
        # a saved, not-cancelled Chunky task (config/chunky/tasks) means a previous run was interrupted: continue it
        task = sdir / "config/chunky/tasks/minecraft/overworld.properties"
        resume = life > 1 or (task.exists() and "cancelled=false" in task.read_text(errors="replace"))
        for c in (["chunky continue"] if resume else first):
            send(c)
        time.sleep(5)
        if life > 1 and re.search(r"No tasks to continue|no task", tail(), re.I):
            note("nothing to continue; starting the task again (Chunky skips generated chunks)")
            for c in first: send(c)
        start_count = None; last = None; t_life = time.time(); reason = None
        while True:
            txt = tail()
            if "Task finished" in txt:
                finished = True; break
            m = re.findall(r"Processed: (\d+) chunks \(([\d.]+)%\)", txt)
            if m:
                n = int(m[-1][0])
                if start_count is None: start_count = n
                if m[-1] != last:
                    last = m[-1]; note(f"chunky {n} chunks ({m[-1][1]}%) life {life}")
                if n - start_count >= batch: reason = f"batch {n - start_count}"; break
            ws = ws_mb(p.pid)
            if ws > WS_LIMIT_MB: reason = f"working set {ws} MB"; break
            if "OutOfMemoryError" in txt: reason = "OOM"; break
            if p.poll() is not None: reason = "server exited"; break
            if time.time() - t_life > 3 * 3600: reason = "life timeout"; break
            time.sleep(15)
        if not finished:
            note(f"life {life}: cycling ({reason})")
        if p.poll() is None:
            try:
                for c in ("chunky pause", "save-all flush", "stop"): send(c)
                p.wait(timeout=300)
            except Exception:
                p.kill(); note("stop timed out; killed")
        note(f"life {life}: server exit {p.returncode}")
        if reason == "server exited" and not finished:
            time.sleep(5)
    note(f"{'FINISHED' if finished else 'gave up'}; elapsed {int(time.time() - t_all)} s over {life} lives")
    log.write("server exit (all lives done)\n"); log.flush()
    return 0 if finished else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
