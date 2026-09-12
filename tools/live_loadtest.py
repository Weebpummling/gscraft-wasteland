"""A load test on the HOSTED server, through the panel console (no RCON there): what a fighter costs on Bisect's
cores, so the ceilings can be set to what the host carries with a five-player margin (owner, 2026-09-11; the
server confirmed empty and the players warned off).

Everything is staged on a stone platform at y 200 over the farm (-2000, -600), forceloaded for the run and removed
after, with the director paused; nothing of the world below is touched. Command replies are read back from
/logs/latest.log.

    live_loadtest.py            run it
    live_loadtest.py clean      only the cleanup (after an interrupted run)
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bisectpanel as B  # noqa: E402

cfg = B.load_config()
X, Y, Z = -2000, 200, -600
AREA = f"x={X - 70},y={Y - 10},z={Z - 70},dx=140,dy=40,dz=140"
TYPES = ("gscraft:nato_soldier", "gscraft:ruaf_soldier", "superbwarfare:hand_grenade")
HP = 'Health:4000f,Attributes:[{Name:"minecraft:generic.max_health",Base:4000}]'
report = []


def say(line):
    print(line)
    report.append(line)


def cmd(command):
    B.request(cfg, "POST", f"/api/client/servers/{cfg['server']}/command", body={"command": command})


def log():
    path = f"/api/client/servers/{cfg['server']}/files/contents"
    try:
        body = B.request(cfg, "POST", path, params={"file": "/logs/latest.log"}, raw=True)
    except SystemExit:
        data = B.request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/download", params={"file": "/logs/latest.log"})
        body = B.fetch_signed(data["attributes"]["url"])
    return body.decode("utf-8", "replace")


def tps():
    """the overworld's mean tick time in ms, fresh: the reply to a forge tps sent now"""
    before = log().count("Mean tick time")
    cmd("forge tps")
    for _ in range(10):
        time.sleep(2)
        text = log()
        if text.count("Mean tick time") > before:
            m = re.findall(r"overworld \(minecraft:overworld\): Mean tick time: ([\d.]+) ms", text)
            return float(m[-1]) if m else None
    return None


def count(sel):
    """execute if entity replies 'Test passed, count: N' on the console"""
    before = log().count("Test passed, count:") + log().count("Test failed")
    cmd(f"execute if entity {sel}")
    for _ in range(8):
        time.sleep(1.5)
        text = log()
        if text.count("Test passed, count:") + text.count("Test failed") > before:
            lines = [l for l in text.splitlines() if "Test passed, count:" in l or "Test failed" in l]
            m = re.search(r"count: (\d+)", lines[-1])
            return int(m.group(1)) if m else 0
    return -1


def settle(seconds):
    time.sleep(seconds)


def clear():
    for t in TYPES:
        cmd(f"kill @e[type={t},{AREA}]")
        time.sleep(0.3)


def platform():
    cmd(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
    cmd(f"fill {X - 40} {Y - 1} {Z - 20} {X + 40} {Y - 1} {Z + 20} minecraft:stone")
    cmd(f"fill {X - 41} {Y} {Z - 21} {X + 41} {Y + 1} {Z + 21} minecraft:stone hollow")
    cmd(f"fill {X - 40} {Y} {Z - 20} {X + 40} {Y + 3} {Z + 20} minecraft:air")
    for i in range(6):   # some walls to fight around, so cover and leaning are in the numbers
        cmd(f"fill {X - 20 + i * 8} {Y} {Z - 12} {X - 20 + i * 8} {Y + 2} {Z - 9} minecraft:stone")
        cmd(f"fill {X - 16 + i * 8} {Y} {Z + 9} {X - 16 + i * 8} {Y + 2} {Z + 12} minecraft:stone")


def cleanup():
    clear()
    time.sleep(1)
    cmd(f"fill {X - 41} {Y - 1} {Z - 21} {X + 41} {Y + 4} {Z + 21} minecraft:air")
    cmd("gscraft director phantom clear")
    cmd(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")
    cmd("gscraft director resume")
    time.sleep(2)
    left = count(f"@e[type=gscraft:nato_soldier,{AREA}]") + count(f"@e[type=gscraft:ruaf_soldier,{AREA}]")
    say(f"cleanup: fighters left in the area {left}; platform removed; forceload removed; director running")


def stage(label, per_side, seconds=45, both=True):
    clear()
    time.sleep(2)
    for i in range(per_side):
        # durable, so the fight lasts the whole measurement instead of ending in twenty seconds
        cmd(f'summon gscraft:nato_soldier {X - 35 + (i % 12) * 2} {Y} {Z - 15 + (i // 12) * 3} {{GscraftRank:"NATO Rifleman",{HP}}}')
        if both:
            cmd(f'summon gscraft:ruaf_soldier {X + 35 - (i % 12) * 2} {Y} {Z - 15 + (i // 12) * 3} {{GscraftRank:"RUAF Rifleman",{HP}}}')
        time.sleep(0.15)
    total = per_side * (2 if both else 1)
    samples = []
    t0 = time.time()
    while time.time() - t0 < seconds:
        time.sleep(5)
        t = tps()
        alive = count(f"@e[type=gscraft:nato_soldier,{AREA}]") + (count(f"@e[type=gscraft:ruaf_soldier,{AREA}]") if both else 0)
        if t is not None:
            samples.append((round(time.time() - t0), t, alive))
    worst = max(s[1] for s in samples) if samples else None
    say(f"{label}: {total} fighters placed; samples (s, ms per tick, alive) {samples}; worst {worst} ms")
    return samples


if len(sys.argv) > 1 and sys.argv[1] == "clean":
    cleanup()
    sys.exit(0)

say(f"live load test {time.strftime('%Y-%m-%d %H:%M')}")
cmd("gscraft director pause")
cmd(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
settle(12)
clear()
platform()
settle(20)
idle = tps()
say(f"idle with the platform loaded: {idle} ms per tick")

# what the director itself costs on the host: passes for one phantom on the platform
cmd(f"gscraft director phantom set {X} {Y} {Z}")
cmd("gscraft director bench 20")
time.sleep(3)
bench = [l for l in log().splitlines() if "bench:" in l]
say("director bench: " + (bench[-1].split("]: ", 1)[-1] if bench else "no reply"))
cmd("gscraft director phantom clear")
clear()
time.sleep(2)

stage("24 idle fighters (no enemy)", 24, seconds=30, both=False)
a = stage("24 v 24 firefight", 24)
b = stage("48 v 48 firefight", 48)
cleanup()
after = tps()
say(f"after cleanup: {after} ms per tick")
Path("G:/GSCraft/repo/docs/notes").mkdir(parents=True, exist_ok=True)
out = Path("G:/GSCraft/repo/docs/notes/live-loadtest-2026-09-11.md")
out.write_text("# Live load test, 2026-09-11\n\n" + "\n".join("- " + l for l in report) + "\n", encoding="utf-8")
print("written", out)
