#!/usr/bin/env python3
"""The quest book's chapters, one per survivor (system doc 2026-09-13 §7 build 6; onboarding §4).

    python chapters.py             -> build/ftbquests/quests/data.snbt and chapters/<id>.snbt from
                                      mod/src/main/resources/data/gscraft/gscraft_survivors/survivors.json
    python chapters.py --install   -> also copied to G:/GSCraft/server/config/ftbquests/quests (the local server;
                                      FTB Quests reads config/ftbquests/quests, file version 13); existing chapter
                                      files with the same name are overwritten, others left alone

Each chapter carries the tag the survivor's right-click opens it by (`/ftbquests open_book #<chapter>`, a tag
lookup over every quest object) and a stable id from the chapter name. The quests themselves are build 7's; a
chapter written by that build keeps its id and tag from here.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURVIVORS = ROOT / "mod/src/main/resources/data/gscraft/gscraft_survivors/survivors.json"
OUT = ROOT / "build/ftbquests/quests"
SERVER = Path("G:/GSCraft/server/config/ftbquests/quests")
VERSION = 13


def hex_id(name):
    return hashlib.sha1(("gscraft:" + name).encode()).hexdigest()[:16].upper()


def chapter(d, index):
    return (
        "{\n"
        f'\tid: "{hex_id(d["chapter"])}"\n'
        '\tgroup: ""\n'
        f"\torder_index: {index}\n"
        f'\tfilename: "{d["chapter"]}"\n'
        f'\ttitle: "{d["name"].split(" ")[0]}"\n'
        '\tdefault_quest_shape: ""\n'
        "\tdefault_hide_dependency_lines: false\n"
        "\ttags: [\n"
        f'\t\t"{d["chapter"]}"\n'
        "\t]\n"
        "\tquests: [ ]\n"
        "\tquest_links: [ ]\n"
        "}\n"
    )


DATA = (
    "{\n"
    f"\tversion: {VERSION}\n"
    '\tdefault_quest_shape: "circle"\n'
    "\tdefault_reward_team: false\n"
    "\tdisable_gui: false\n"
    "\tdrop_loot_crates: false\n"
    "}\n"
)


def main(argv):
    survivors = json.loads(SURVIVORS.read_text(encoding="utf-8"))["survivors"]
    (OUT / "chapters").mkdir(parents=True, exist_ok=True)
    (OUT / "data.snbt").write_text(DATA, encoding="utf-8")
    for i, d in enumerate(survivors):
        (OUT / "chapters" / f'{d["chapter"]}.snbt').write_text(chapter(d, i), encoding="utf-8")
    print(f"{len(survivors)} chapters and data.snbt written to {OUT}")
    if "--install" in argv:
        (SERVER / "chapters").mkdir(parents=True, exist_ok=True)
        if not (SERVER / "data.snbt").exists():
            shutil.copy(OUT / "data.snbt", SERVER / "data.snbt")
        for d in survivors:
            shutil.copy(OUT / "chapters" / f'{d["chapter"]}.snbt', SERVER / "chapters" / f'{d["chapter"]}.snbt')
        print(f"installed to {SERVER}")


if __name__ == "__main__":
    main(sys.argv[1:])
