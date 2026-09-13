#!/usr/bin/env python3
"""The player layer's items as data (system doc 2026-09-13 §7 build 3; crafting §5, design §4.2).

    python items.py    -> from mod/src/main/resources/data/gscraft/gscraft_items/items.json:
                          assets/gscraft/models/item/<id>.json (a flat item), textures/item/<id>.png (a placeholder: a
                          coloured tile by role with the id's initials, until art comes), lang entries item.gscraft.<id>
                          and .tip merged into en_us.json

items.json: {"items": [{"id", "name", "tip", "stack" (64), "bulky" (false), "role": small|intermediate|card|tool|part}]}.
The mod registers every entry at start (gscraft.war.item.SliceItems), so an item is a line here and nothing else.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "mod/src/main/resources"
LIST = RES / "data/gscraft/gscraft_items/items.json"
MODELS = RES / "assets/gscraft/models/item"
TEX = RES / "assets/gscraft/textures/item"
LANG = RES / "assets/gscraft/lang/en_us.json"
COLOUR = {"small": (140, 140, 150), "intermediate": (90, 120, 160), "card": (200, 190, 120), "tool": (150, 110, 70), "part": (170, 90, 90), "item": (120, 120, 120)}


def texture(path, role, initials):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = COLOUR.get(role, COLOUR["item"])
    d.rectangle([2, 2, 13, 13], fill=c + (255,), outline=tuple(max(0, x - 60) for x in c) + (255,))
    # the initials as 3x5 pixel glyphs (A-Z, 0-9 kept crude): two letters at most
    glyph = {"A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
             "G": "011100101101011", "H": "101101111101101", "I": "111010010010111", "J": "001001001101010", "K": "101110100110101", "L": "100100100100111",
             "M": "101111111101101", "N": "110101101101101", "O": "010101101101010", "P": "110101110100100", "Q": "010101101011001", "R": "110101110110101",
             "S": "011100010001110", "T": "111010010010010", "U": "101101101101011", "V": "101101101010010", "W": "101101111111101", "X": "101010010010101",
             "Y": "101101010010010", "Z": "111001010100111"}
    x0 = 3 if len(initials) > 1 else 6
    for i, ch in enumerate(initials[:2].upper()):
        g = glyph.get(ch)
        if not g:
            continue
        for yy in range(5):
            for xx in range(3):
                if g[yy * 3 + xx] == "1":
                    d.point((x0 + i * 5 + xx, 5 + yy), fill=(20, 20, 25, 255))
    img.save(path)


def main():
    data = json.loads(LIST.read_text(encoding="utf-8"))
    MODELS.mkdir(parents=True, exist_ok=True)
    TEX.mkdir(parents=True, exist_ok=True)
    lang = json.loads(LANG.read_text(encoding="utf-8"))
    n = 0
    for it in data["items"]:
        iid = it["id"]
        (MODELS / f"{iid}.json").write_text(json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": f"gscraft:item/{iid}"}}, indent=2) + "\n", encoding="utf-8")
        png = TEX / f"{iid}.png"
        if not png.exists() or it.get("placeholder", True):
            words = iid.split("_")
            texture(png, it.get("role", "item"), "".join(w[0] for w in words[:2]))
        lang[f"item.gscraft.{iid}"] = it["name"]
        if it.get("tip"):
            lang[f"item.gscraft.{iid}.tip"] = it["tip"]
        n += 1
    lang["gscraft.item.bulky"] = "Bulky: slow to carry, cannot sprint"
    LANG.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} items: models, placeholder textures and names written")


if __name__ == "__main__":
    main()
