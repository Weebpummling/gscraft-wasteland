"""The armour override datapack (design 2026-09-11 §1, §5): Superb Warfare's own vehicle files for the four vehicles,
copied out of the jar with our damage-modifier changes, as a world datapack that overrides the jar's data.

    python tools/armour_override.py            -> build/local-datapack/gscraft_armour/ (the repo copy)
    python tools/armour_override.py --install  -> also copied into the local world's datapacks (then /reload)

Changes made to each vehicle's DamageModifiers, in front of the mod's own list (an immunity holds wherever it sits):
  "#tacz:bullets 0"    every TACZ bullet type does nothing (small-arms immunity)
The explosive multipliers stay the mod's until the V1 numbers are settled; add them to CHANGES when they are.
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
CHANGES = {
    "prepend": ["#tacz:bullets 0"],
}


def main():
    jar = next(MODS.glob("superbwarfare-*.jar"))
    zf = zipfile.ZipFile(jar)
    target = OUT / "data" / "superbwarfare" / "sbw" / "vehicles"
    target.mkdir(parents=True, exist_ok=True)
    (OUT / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "GSCraft armour: the four vehicles' damage lists"}}, indent=2) + "\n", encoding="utf-8")
    for v in VEHICLES:
        raw = zf.read(f"data/superbwarfare/sbw/vehicles/{v}.json").decode("utf-8-sig")
        data = json.loads(re.sub(r"//[^\r\n]*", "", raw))
        mods = list(data["DamageModifiers"])
        for m in reversed(CHANGES["prepend"]):
            if m not in mods:
                mods.insert(0, m)
        data["DamageModifiers"] = mods
        (target / f"{v}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{v}: {len(mods)} modifiers, first {mods[:2]}")
    print(f"written to {OUT} from {jar.name}")
    if "--install" in sys.argv:
        if WORLD.exists():
            shutil.rmtree(WORLD)
        shutil.copytree(OUT, WORLD)
        print(f"installed to {WORLD}; /reload applies it")


if __name__ == "__main__":
    main()
