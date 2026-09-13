#!/usr/bin/env python3
"""The stage registry as advancements (system doc 2026-09-13 §5, ruling R2, slice build 1).

    python stages.py     -> mod/src/main/resources/data/gscraft/advancements/stage/<name>.json, one per stage

The mod sets a stage as a player tag and, since build 1, also grants the advancement `gscraft:stage/<name>` to every
player (and to a player on join), and revokes it when the stage is removed. FTB Quests' native advancement task reads
it; no compat mod, no script. Every advancement here is hidden (no display) with one impossible criterion, so only the
mod grants it. A stage the mod sets that has no file here is still a tag (the mod logs it once) - add it and rerun.

The registry: the five strongpoints' rungs, the five building takes and their aliases, the sector's, the bosses', the
gates on enemies, the per-player ones. The recipe stages `bp_<recipe>` are added by the crafting build from its recipe
file (RECIPES below is the list to extend).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mod/src/main/resources/data/gscraft/advancements/stage"

STRONGPOINTS = ("hospital", "switchyard", "intake", "turbine", "krot")
RUNGS = ("scouted", "looted", "held", "defended", "lost")
TAKES = {"square": "square_taken", "gatehouse": "gatehouse_taken", "north": "clinic_taken", "crossing": "crossing_taken", "mast": "mast_taken"}
SECTOR = ("compound_closed", "skadowsky_scouted", "skadowsky_held", "skadowsky_defended")
BOSSES = ("switchyard_gatekeeper",)
GATES = ("line_depot",)
PER_PLAYER = ("joined", "marshall_speaks", "revives_3", "seen_walker", "seen_tony", "seen_michael", "seen_tune", "seen_james", "seen_marshall")
RECIPES_FILE = ROOT / "mod/src/main/resources/data/gscraft/gscraft_recipes/recipes.json"
# bp_<card>: one per blueprint card in the station's recipe file (slice build 5); the card's id without its card_ prefix
RECIPES = tuple(dict.fromkeys(o["card"].removeprefix("card_") for o in json.loads(RECIPES_FILE.read_text(encoding="utf-8"))["orders"] if o.get("card")))


def registry():
    names = []
    for s in STRONGPOINTS:
        names += [f"{s}_{r}" for r in RUNGS]
    for site, alias in TAKES.items():
        names += [f"{site}_held", alias]
    names += list(SECTOR) + list(BOSSES) + list(GATES) + list(PER_PLAYER)
    names += [f"bp_{r}" for r in RECIPES]
    return names


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    names = registry()
    for name in names:
        (OUT / f"{name}.json").write_text(json.dumps({
            "criteria": {"set": {"trigger": "minecraft:impossible"}},
            "requirements": [["set"]],
            "__comment": f"the stage {name}; granted and revoked by the gscraft mod with the stage (tools/stages.py)",
        }, indent=2) + "\n", encoding="utf-8")
    print(f"{len(names)} stage advancements written to {OUT}")


if __name__ == "__main__":
    main()
