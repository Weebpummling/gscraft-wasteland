"""The armour override datapack (design 2026-09-11 §1, §5): Superb Warfare's own vehicle files for the four vehicles,
copied out of the jar with our damage list in place of the mod's, as a world datapack that overrides the jar's data.

    python tools/armour_override.py            -> build/local-datapack/gscraft_armour/ (the repo copy)
    python tools/armour_override.py --install  -> also copied into the local world's datapacks (then /reload)

The damage pass (owner 2026-09-12: a BMP dies to two rockets at most). The mod's list took 13 off everything, then
a fifth, then its multipliers, so a rocket left a BMP at two thirds. Ours replaces it whole, by weight - LIGHT for the
BMP-2 and Bradley (300 health), HEAVY for the T-90A and M1A2 (500) - with immunities first and a plain multiplier
per source; the rules apply in order, so the numbers below are the final share of the raw damage. Roughly, on light
armour: a Superb Warfare RPG round 160 (two), a Javelin one, a tank shell 280 (one or two), an ATGM 230 (two), a
40 mm grenade 65, a hand grenade 50, C4 180, a 30 mm AP round 11 (a burst of thirty); on heavy: an RPG 125 (four),
a Javelin 300 with the top attack (two), a tank shell 215 (three), an ATGM 165 (three or four), a grenade 30,
C4 300 (two), 30 mm AP 4. TACZ explosive rounds are a vanilla explosion and get a flat amount from the mod
(armour/ArmourDamage.java: rocket 160 light, 130 heavy) - their type is left alone here on purpose.
The explosive pass (owner 2026-09-12: "way off base, fun but off base", then "visually very strong"): every blast in the mod's data - the four
vehicles' weapons and wreck blasts, and every gun file's rounds (RPG, Javelin, M79, grenades) - has its radius and
damage tamed by tame(): a radius over 3 keeps 40% of the excess (10 -> 5.8, 16 -> 8.2; TNT is 4), a blast damage over
60 keeps 60% of the excess (160 -> 120). The same formulas go over the [explosion] section of the server's
superbwarfare-server.toml (grenades, mortar, C4, the drone's RPG, the bombs), which the mod reads at start. The
vehicles' direct-hit damage (the numbers above) is untouched: only the blast shrinks. The blast's look follows its
radius in the mod (under 2 mini, 2-4 small, 4-10 medium, over 10 large/huge), so the smaller radii also mean smaller
fireballs; the wrecks' own "Huge"/"Giant" blasts (a 200-400 block screen shake) become "Large". The screen shake
itself is the client's superbwarfare-client.toml (explosion_screen_shake, shipped in the pack at 40).
Rerun after a Superb Warfare update: the rest of each file is the jar's, so the mod's own changes come through.
"""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

MODS = Path("G:/GSCraft/server/mods")
OUT = Path(__file__).resolve().parents[1] / "build" / "local-datapack" / "gscraft_armour"
WORLD = Path("G:/GSCraft/server/wasteland-v8/datapacks/gscraft_armour")
VEHICLES = ["bmp_2", "bradley", "t_90a", "m_1a_2"]
IMMUNE = [
    "#tacz:bullets 0", "superbwarfare:gunfire 0", "superbwarfare:gunfire_headshot 0",
    "superbwarfare:gunfire_absolute 0", "superbwarfare:gunfire_headshot_absolute 0",
    "#superbwarfare:projectile 0", "#superbwarfare:projectile_absolute 0",
    "minecraft:mob_attack 0", "minecraft:mob_attack_no_aggro 0", "minecraft:mob_projectile 0", "minecraft:player_attack 0",
    "minecraft:in_fire 0", "minecraft:on_fire 0", "minecraft:hot_floor 0", "minecraft:cactus 0", "minecraft:fall 0",
    "minecraft:fly_into_wall 0", "minecraft:drown 0", "minecraft:freeze 0", "minecraft:sweet_berry_bush 0",
]
LIGHT = IMMUNE + [
    "superbwarfare:projectile_hit * 0.35",
    "superbwarfare:custom_explosion * 0.4", "superbwarfare:projectile_explosion * 0.4",
    "@superbwarfare:small_cannon_shell * 0.5",
    "@superbwarfare:mortar_shell * 1.5", "@superbwarfare:c4 * 1.5",
    "minecraft:explosion * 2", "minecraft:lava * 2",
    "#superbwarfare:vehicle_strike * 2.5",
    "@#superbwarfare:aerial_bomb * 3", "@#superbwarfare:aa_missile * 0.5",
    "superbwarfare:laser * 0.5", "superbwarfare:burn * 0.5", "superbwarfare:phosphorus_fire * 0.5", "superbwarfare:shock * 0.2",
]
HEAVY = IMMUNE + [
    "superbwarfare:projectile_hit * 0.28",
    "superbwarfare:custom_explosion * 0.25", "superbwarfare:projectile_explosion * 0.25",
    "@superbwarfare:small_cannon_shell * 0.2",
    "@superbwarfare:javelin_missile * 1.3",
    "@superbwarfare:mortar_shell * 1.5", "@superbwarfare:c4 * 4",
    "minecraft:explosion * 1.2", "minecraft:lava * 1",
    "#superbwarfare:vehicle_strike * 2.5",
    "@#superbwarfare:aerial_bomb * 6", "@#superbwarfare:aa_missile * 0.3",
    "superbwarfare:laser * 0.3", "superbwarfare:burn * 0.3", "superbwarfare:phosphorus_fire * 0.3", "superbwarfare:shock * 0.1",
]
WEIGHT = {"bmp_2": LIGHT, "bradley": LIGHT, "t_90a": HEAVY, "m_1a_2": HEAVY}
CONFIG = Path("G:/GSCraft/server/config/superbwarfare-server.toml")


def tame_radius(r):
    return r if r <= 3 else round(3 + (r - 3) * 0.4, 1)


def tame_damage(d):
    return d if d <= 60 else round(60 + (d - 60) * 0.6)


PARTICLE = {"Giant": "Large", "Huge": "Large"}   # the wreck's blast: Large is the biggest without the 200-400 block screen shake


def tame(obj):
    """every ExplosionRadius / ExplosionDamage / ParticleType in a data tree, in place"""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k == "ExplosionRadius" and isinstance(v, (int, float)):
                obj[k] = tame_radius(v)
            elif k == "ExplosionDamage" and isinstance(v, (int, float)):
                obj[k] = tame_damage(v)
            elif k == "ParticleType" and isinstance(v, str) and v in PARTICLE:
                obj[k] = PARTICLE[v]
            else:
                tame(v)
    elif isinstance(obj, list):
        for v in obj:
            tame(v)
    return obj


def tame_config():
    """the [explosion] section of the server config: the same formulas on every *_explosion_radius / _explosion_damage,
    computed from the pack's pre-pass value (the .bak-explosion backup) or else the '# Default: N' comment the mod
    writes above each value, so a rerun lands on the same numbers"""
    if not CONFIG.exists():
        print(f"no {CONFIG}: config untouched")
        return
    lines = CONFIG.read_text(encoding="utf-8").splitlines()
    # the pack's own values before the pass (the backup an earlier session left) win over the mod's defaults
    base = {}
    backup = CONFIG.with_name(CONFIG.name + ".bak-explosion")
    if backup.exists():
        for line in backup.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(\w+_explosion_(?:radius|damage)) = ([\d.]+)\s*$", line)
            if m:
                base[m.group(1)] = float(m.group(2))
    changed = 0
    default = None
    for i, line in enumerate(lines):
        m = re.match(r"\s*#\s*Default:\s*([\d.]+)\s*$", line)
        if m:
            default = float(m.group(1))
            continue
        m = re.match(r"(\s*)(\w+_explosion_(?:radius|damage)) = ([\d.]+)\s*$", line)
        if not m:
            if line.strip() and not line.strip().startswith("#"):
                default = None
            continue
        indent, key, cur = m.group(1), m.group(2), m.group(3)
        if key in base:
            default = base[key]
        if default is None:
            print(f"  {key}: no default comment, left at {cur}")
            continue
        new = tame_radius(default) if key.endswith("_radius") else tame_damage(default)
        out = f"{int(new)}" if float(new).is_integer() and "." not in str(default).rstrip("0").rstrip(".") else f"{new}"
        if "." in m.group(3) and "." not in out:
            out = f"{float(out)}"
        if out != cur:
            changed += 1
        lines[i] = f"{indent}{key} = {out}"
        default = None
    CONFIG.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    print(f"{CONFIG.name}: {changed} blast values set from the defaults")


def main():
    jar = next(MODS.glob("superbwarfare-*.jar"))
    zf = zipfile.ZipFile(jar)
    target = OUT / "data" / "superbwarfare" / "sbw" / "vehicles"
    target.mkdir(parents=True, exist_ok=True)
    (OUT / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "GSCraft armour: the four vehicles' damage lists"}}, indent=2) + "\n", encoding="utf-8")
    for v in VEHICLES:
        raw = zf.read(f"data/superbwarfare/sbw/vehicles/{v}.json").decode("utf-8-sig")
        data = json.loads(re.sub(r"//[^\r\n]*", "", raw))
        mods = list(WEIGHT[v])
        data["DamageModifiers"] = mods
        tame(data)
        (target / f"{v}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{v}: {len(mods)} modifiers, first {mods[:2]}")
    guns = OUT / "data" / "superbwarfare" / "sbw" / "guns"
    guns.mkdir(parents=True, exist_ok=True)
    tamed = 0
    for name in zf.namelist():
        if not name.startswith("data/superbwarfare/sbw/guns/") or not name.endswith(".json"):
            continue
        raw = zf.read(name).decode("utf-8-sig")
        data = json.loads(re.sub(r"//[^\r\n]*", "", raw))
        before = json.dumps(data)
        tame(data)
        if json.dumps(data) != before:
            (guns / name.rsplit("/", 1)[1]).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            tamed += 1
    print(f"{tamed} gun files with blasts tamed")
    tame_config()
    print(f"written to {OUT} from {jar.name}")
    if "--install" in sys.argv:
        if WORLD.exists():
            shutil.rmtree(WORLD)
        shutil.copytree(OUT, WORLD)
        print(f"installed to {WORLD}; /reload applies it")


if __name__ == "__main__":
    main()
