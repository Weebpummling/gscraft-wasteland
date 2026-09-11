"""Phase 11 of the enemy work, on the LOCAL server: the settings file (owner, 2026-09-11: "check what other things
we can place into settings instead of a jar update"). Needs a ticking world and no player.

1. /gscraft settings lists the values in force, with the jar's defaults.json applied.
2. A world datapack override (zz_test.json with a few keys) changes them on /reload: the server ceiling, a role's
   range, an env radius; unknown keys are logged and ignored.
3. The changed ceiling bites: with server_ceiling 4 the director places nothing past four creatures.
4. Removing the override and reloading restores the defaults.
"""
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import localtest as L  # noqa: E402

LOG = Path("G:/GSCraft/server/logs/latest.log")
PACK = Path("G:/GSCraft/server/wasteland-v8/datapacks/gscraft_settings_test")
r = L.Rcon("127.0.0.1", 25575, "gscraft-local-test")
results = []
log_start = LOG.stat().st_size
X, Z = -2000, -600
AREA = f"x={X - 120},y=-64,z={Z - 120},dx=240,dy=400,dz=240"


def c(cmd, t=180):
    return (r.cmd(cmd, timeout=t) or "").strip()


def count(sel):
    m = re.search(r"count: (\d+)", c(f"execute if entity {sel}"))
    return int(m.group(1)) if m else 0


def check(name, ok, detail):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


def setting(path):
    out = c(f"gscraft settings {path}")
    m = re.search(re.escape(path) + r" = ([\d.]+)", out)
    return float(m.group(1)) if m else None


def write_pack(values):
    (PACK / "data/gscraft/gscraft_settings").mkdir(parents=True, exist_ok=True)
    (PACK / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "gscraft settings test"}}), encoding="utf-8")
    (PACK / "data/gscraft/gscraft_settings/zz_test.json").write_text(json.dumps(values), encoding="utf-8")


def surface_y(x, z):
    c(f'execute positioned {x} 0 {z} positioned over motion_blocking_no_leaves run summon minecraft:armor_stand ~ ~ ~ {{Tags:["ymark"],Invisible:1b}}')
    p = c("data get entity @e[tag=ymark,limit=1] Pos")
    c("kill @e[tag=ymark]")
    n = re.findall(r"-?[\d.]+(?=d)", p)
    return int(float(n[1])) if len(n) == 3 else 64


if PACK.exists():
    shutil.rmtree(PACK)
    c("reload")
    time.sleep(3)

# 1. the listing
head = c("gscraft settings director")
ceiling, rng, open_max = setting("director.server_ceiling"), setting("roles.rifleman.range"), setting("env.open.max_r")
check("the settings are listed with the jar's defaults in force", "defaults (" in head and ceiling == 48 and rng == 40 and open_max == 72,
      f"{head[:80]}; server_ceiling {ceiling}, rifleman range {rng}, open max_r {open_max}")

# 2. a datapack override
write_pack({"director": {"server_ceiling": 4}, "roles": {"rifleman": {"range": 25}}, "env": {"open": {"max_r": 60}}, "nonsense": {"key": 1}})
reload = c("reload")
time.sleep(4)
ceiling2, rng2, open2 = setting("director.server_ceiling"), setting("roles.rifleman.range"), setting("env.open.max_r")
head2 = c("gscraft settings director.server")
check("a world datapack override changes them on /reload", ceiling2 == 4 and rng2 == 25 and open2 == 60 and "(default 48)" in head2,
      f"server_ceiling {ceiling2}, rifleman range {rng2}, open max_r {open2}; {head2[:120]}")

# 3. the changed ceiling bites
c("gscraft director pause")
c(f"forceload add {X - 64} {Z - 64} {X + 64} {Z + 64}")
time.sleep(6)
c(f"kill @e[tag=gs_director,{AREA}]")
c(f"kill @e[tag=gs_placed,{AREA}]")
c(f"gscraft director phantom set {X} {surface_y(X, Z)} {Z}")
c("gscraft director bench 8")
placed = count(f"@e[tag=gs_director,{AREA}]")
stats = c("gscraft director stats")
check("with server_ceiling 4 the director places nothing past four creatures", 2 <= placed <= 4 and "(ceiling 4)" in stats, f"{placed} placed after eight passes; {stats[-60:]}")
c("gscraft director phantom clear")
c(f"kill @e[tag=gs_director,{AREA}]")
c(f"forceload remove {X - 64} {Z - 64} {X + 64} {Z + 64}")
c("gscraft director resume")

# 4. back to the defaults
shutil.rmtree(PACK)
c("reload")
time.sleep(4)
ceiling3, rng3 = setting("director.server_ceiling"), setting("roles.rifleman.range")
check("removing the override and reloading restores the defaults", ceiling3 == 48 and rng3 == 40, f"server_ceiling {ceiling3}, rifleman range {rng3}")

r.close()
with LOG.open("rb") as f:
    f.seek(log_start)
    new = f.read().decode("utf-8", "replace")
bad = [l for l in new.splitlines() if re.search(r"ERROR|Exception", l) and "gscraft" in l.lower()]
unknown = [l for l in new.splitlines() if "no setting named nonsense.key" in l]
loaded = [l for l in new.splitlines() if "settings:" in l and "values from" in l]
check("the unknown key was logged, the loads were logged, no gscraft errors", unknown and len(loaded) >= 2 and not bad,
      f"unknown-key lines {len(unknown)}, load lines {len(loaded)}, error lines {len(bad)}")
for l in bad[:8]:
    print("     ", l[:200])
print(f"\n{sum(results)} pass, {len(results) - sum(results)} fail")
sys.exit(0 if all(results) else 1)
