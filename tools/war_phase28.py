"""Phase 28, the advancement per stage (system doc 2026-09-13 §5, ruling R2, slice build 1) on the LOCAL server. Needs a
ticking world and no player. What a headless test can prove: every stage in the registry has an advancement the server
knows (`/gscraft stage check <name>`, and the count), a made-up id is unknown, and setting or removing a stage with nobody
online raises no error. The award to a player and FTB Quests' task reading it
are the owner's in-game check (a task on gscraft:stage/square_taken completing on `/gscraft stage add square_taken`).

1. Every registry stage's advancement is known to the server.
2. A made-up id is refused as unknown (the check has teeth).
3. Stage add and remove run clean with nobody online.
4. No gscraft errors.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402
import stages  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size


def c(cmd, t=60):
    return (r.cmd(cmd, timeout=t) or "").strip()


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def log_since(mark):
    with LOG.open("rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")


names = stages.registry()
unknown = [n for n in names if "known" not in c(f"gscraft stage check {n}") or "UNKNOWN" in c(f"gscraft stage check {n}")]
total = c("gscraft stage check")
check("every registry stage's advancement is known to the server", not unknown and str(len(names)) in total, f"{len(names)} stages; unknown {unknown[:6]}; [{total}]")

bogus = c("gscraft stage check no_such_stage_xyz")
check("a made-up id is refused as unknown", "UNKNOWN" in bogus, f"[{bogus[:60]}]")

mark = LOG.stat().st_size
c("gscraft stage add square_taken")
c("gscraft stage remove square_taken")
c("gscraft stage add hospital_scouted")
c("gscraft stage remove hospital_scouted")
new = log_since(mark)
check("stage add and remove run clean with nobody online", "stage square_taken set" in new and "Exception" not in new, f"log lines {len(new.splitlines())}")

r.close()
new = log_since(log_start)
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
check("no gscraft errors", not bad, f"error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
