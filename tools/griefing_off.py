"""Switch off mob block destruction while the designers build by hand (owner, 2026-09-09).

Nothing hostile should be able to alter terrain or structures until construction and expansion of the
sites is finished. That is more than one switch, because four different systems can break blocks and
only one of them is the vanilla gamerule:

  1. `mobGriefing`               vanilla: creeper craters, enderman block pickup, zombies breaking doors,
                                 ravagers trampling. Also stops villager farming and sheep eating grass,
                                 which is an acceptable price while nobody is playing.
  2. Improved Mobs `BLOCKBREAK`  its own block-breaking AI, which does not consult the gamerule. Disabled
                                 through `Flag Blacklist`, which switches the feature off for every mob.
  3. Improved Mobs `LADDER`      it places scaffolding blocks to climb. That is placement, not
                                 destruction, but it is still a mob editing the world.
  3b. Improved Mobs `USEITEM`    it hands mobs usable items and uses them - flint and steel among them,
                                 which is arson, and ender pearls, which teleport them through walls.
                                 Measured: a dressed Militia Rifleman was given flint and steel in the
                                 offhand, and a Scavenger an ender pearl, after the ARMOR/HELDITEMS
                                 exemption had already taken. USEITEM is a separate slot writer.
  4. the fog man / Knocker       `break_blocks` in their own configs.

`gscraft_mech_griefing.js` stays as it is: it is a per-entity denial for pomkotsmechs and is unaffected
by any of the above being on or off.

    griefing_off.py [--on] [--dry-run]

`--on` puts all four back, for when the build is done. The gamerule is written into the local world's
level.dat, so it travels with the world; the rest are config.
"""
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transplant import R, W  # noqa: E402

SERVER = Path(r"G:/GSCraft/server")
LEVEL = SERVER / "wasteland-v8" / "level.dat"
IM = SERVER / "config" / "improvedmobs" / "common.toml"
FLAGS = ["BLOCKBREAK", "LADDER", "USEITEM"]
# the fog man ("man"); the only break_blocks key under server/config
BREAKERS = [SERVER / "config" / "man_config.toml"]


def set_gamerule(on, dry):
    raw = gzip.open(LEVEL, "rb").read()
    name, root = R(raw).root()
    rules = root["Data"][1]["GameRules"][1]
    was = rules.get("mobGriefing", (8, "?"))[1]
    want = "true" if on else "false"
    if was == want:
        print(f"  mobGriefing already {want}")
        return
    print(f"  mobGriefing {was} -> {want}")
    if dry:
        return
    rules["mobGriefing"] = (8, want)
    # serialise first, then replace. Opening the target with gzip.open(..., "wb") truncates it before
    # anything is written, so a failure between the two leaves level.dat empty - which is exactly what
    # happened here once, and a world with a zero-byte level.dat does not load at all.
    blob = W().root(name, root)
    tmp = LEVEL.with_suffix(".dat.tmp")
    with gzip.open(tmp, "wb") as fh:
        fh.write(blob)
    LEVEL.with_suffix(".dat.bak-griefing").write_bytes(LEVEL.read_bytes())
    tmp.replace(LEVEL)


def set_flags(on, dry):
    s = IM.read_text(encoding="utf-8")
    line = next(l for l in s.splitlines() if l.strip().startswith('"Flag Blacklist"'))
    current = json.loads(line.split("=", 1)[1].strip())
    want = [f for f in current if f not in FLAGS] + ([] if on else FLAGS)
    if sorted(want) == sorted(current):
        print(f"  Flag Blacklist already {current}")
        return
    print(f"  Flag Blacklist {current} -> {want}")
    if dry:
        return
    IM.write_text(s.replace(line, '\t"Flag Blacklist" = ' + json.dumps(want), 1),
                  encoding="utf-8", newline="")


def set_breakers(on, dry):
    want = "true" if on else "false"
    for p in BREAKERS:
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        m = re.search(r'^(\s*"?break_blocks"?\s*=\s*)(true|false)\s*$', s, re.M | re.I)
        if not m:
            continue
        if m.group(2) == want:
            print(f"  {p.name}: break_blocks already {want}")
            continue
        print(f"  {p.name}: break_blocks {m.group(2)} -> {want}")
        if not dry:
            p.write_text(re.sub(r'^(\s*"?break_blocks"?\s*=\s*)(true|false)\s*$',
                                lambda mm: mm.group(1) + want, s, count=1, flags=re.M | re.I),
                         encoding="utf-8", newline="")


def main(argv):
    on = "--on" in argv
    dry = "--dry-run" in argv
    print(f"mob block destruction: {'ON' if on else 'OFF'}{' (dry run)' if dry else ''}")
    set_gamerule(on, dry)
    set_flags(on, dry)
    set_breakers(on, dry)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
