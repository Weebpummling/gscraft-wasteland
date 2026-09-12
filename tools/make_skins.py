"""Uniform skins for the fighters (owner, 2026-09-12: "make their uniforms match their armor").

Nine 64x64 player skins (wide arms) per faction into mod/src/main/resources/assets/gscraft/textures/entity/skin/:
  nato_0..8   OCP: the tan/brown/olive of Superb Warfare's IOTV vest and PASGT helmet, tan gloves, brown boots
  ruaf_0..8   dark olive digital: the 6B43 vest and 6B47 helmet, black gloves, black boots
  scav_0..8   civilian: a drab shirt or hoodie and worn trousers, no two alike
Faces, skin tones and hair vary by index. Deterministic (seeded by faction and index), so a rerun changes nothing.
The armour draws over these; what shows is the face, the sleeves and hands, and whatever a missing piece leaves bare.
"""
import random
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parents[1] / "mod/src/main/resources/assets/gscraft/textures/entity/skin"
COUNT = 9

# vanilla layout: (x0, y0, x1, y1) per face of each part, wide model
HEAD = {"top": (8, 0, 16, 8), "bottom": (16, 0, 24, 8), "right": (0, 8, 8, 16), "front": (8, 8, 16, 16), "left": (16, 8, 24, 16), "back": (24, 8, 32, 16)}
BODY = {"top": (20, 16, 28, 20), "bottom": (28, 16, 36, 20), "right": (16, 20, 20, 32), "front": (20, 20, 28, 32), "left": (28, 20, 32, 32), "back": (32, 20, 40, 32)}
RARM = {"top": (44, 16, 48, 20), "bottom": (48, 16, 52, 20), "right": (40, 20, 44, 32), "front": (44, 20, 48, 32), "left": (48, 20, 52, 32), "back": (52, 20, 56, 32)}
RLEG = {"top": (4, 16, 8, 20), "bottom": (8, 16, 12, 20), "right": (0, 20, 4, 32), "front": (4, 20, 8, 32), "left": (8, 20, 12, 32), "back": (12, 20, 16, 32)}
LLEG = {"top": (20, 48, 24, 52), "bottom": (24, 48, 28, 52), "right": (16, 52, 20, 64), "front": (20, 52, 24, 64), "left": (24, 52, 28, 64), "back": (28, 52, 32, 64)}
LARM = {"top": (36, 48, 40, 52), "bottom": (40, 48, 44, 52), "right": (32, 52, 36, 64), "front": (36, 52, 40, 64), "left": (40, 52, 44, 64), "back": (44, 52, 48, 64)}

SKIN_TONES = [(232, 190, 160), (214, 170, 135), (190, 140, 100), (150, 105, 70), (110, 75, 50), (86, 58, 40)]
HAIR = [(40, 30, 25), (70, 45, 30), (120, 85, 50), (160, 130, 80), (30, 30, 30), (90, 90, 90)]
EYES = [(60, 40, 30), (40, 60, 90), (50, 70, 40)]

# camouflage palettes read off the armour textures (average and the top blocks)
OCP = [(150, 135, 105), (128, 112, 84), (108, 118, 84), (92, 78, 58), (70, 60, 45), (165, 150, 120)]
EMR = [(78, 86, 60), (60, 68, 44), (96, 104, 70), (44, 48, 34), (70, 78, 52), (52, 60, 40)]
SHIRTS = [(110, 40, 40), (60, 70, 90), (70, 70, 70), (95, 80, 55), (70, 85, 60), (40, 45, 60), (120, 100, 70), (90, 50, 60), (50, 50, 50)]
TROUSERS = [(60, 70, 95), (75, 70, 60), (55, 55, 55), (80, 75, 55), (50, 55, 70)]


def fill(im, rect, rgb):
    x0, y0, x1, y1 = rect
    for x in range(x0, x1):
        for y in range(y0, y1):
            im.putpixel((x, y), (*rgb, 255))


def camo(im, rect, palette, rng, grain=2):
    """blotches of the palette, blocky, a little darker at the bottom"""
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = palette[rng.randrange(len(palette))] if (x % grain == 0 and y % grain == 0) or rng.random() < 0.15 else None
            if c is None:
                left = im.getpixel((x - 1, y)) if x > x0 else None
                up = im.getpixel((x, y - 1)) if y > y0 else None
                c = (left or up or (*palette[0], 255))[:3]
            im.putpixel((x, y), (*c, 255))


def wear(im, rect, rng, amount=0.08):
    """dirt: a few pixels darkened"""
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        for x in range(x0, x1):
            if rng.random() < amount:
                r, g, b, a = im.getpixel((x, y))
                im.putpixel((x, y), (int(r * 0.8), int(g * 0.8), int(b * 0.78), a))


def rows(rect, y_from, y_to):
    x0, y0, x1, y1 = rect
    return (x0, y0 + y_from, x1, min(y1, y0 + y_to))


def head(im, rng, tone, hair, eyes, hair_style):
    for f, r in HEAD.items():
        fill(im, r, tone)
    # hair: the top, and a band down the sides and back; the front gets a hairline
    if hair_style != "shaved":
        fill(im, HEAD["top"], hair)
        depth = 2 if hair_style == "short" else 4
        for f in ("right", "left", "back"):
            fill(im, rows(HEAD[f], 0, depth), hair)
        fill(im, rows(HEAD["front"], 0, 1), hair)
        if hair_style == "long":
            fill(im, rows(HEAD["back"], 0, 7), hair)
    # face: brows, eyes (white + iris), nose shade, mouth
    fx, fy = HEAD["front"][0], HEAD["front"][1]
    brow = tuple(int(c * 0.6) for c in tone)
    for x in (1, 2, 5, 6):
        im.putpixel((fx + x, fy + 3), (*brow, 255))
    for ex in (1, 5):
        im.putpixel((fx + ex, fy + 4), (255, 255, 255, 255))
        im.putpixel((fx + ex + 1, fy + 4), (*eyes, 255))
    nose = tuple(int(c * 0.85) for c in tone)
    im.putpixel((fx + 3, fy + 5), (*nose, 255))
    im.putpixel((fx + 4, fy + 5), (*nose, 255))
    mouth = tuple(int(c * 0.7) for c in tone)
    for x in (3, 4):
        im.putpixel((fx + x, fy + 6), (*mouth, 255))
    # a little stubble on some
    if rng.random() < 0.4:
        stub = tuple(int(c * 0.8) for c in tone)
        for x in range(1, 7):
            if rng.random() < 0.5:
                im.putpixel((fx + x, fy + 7), (*stub, 255))


def limb_uniform(im, part, palette, rng, glove, boot, tone):
    for f, r in part.items():
        if f in ("top", "bottom"):
            fill(im, r, palette[0])
        else:
            camo(im, r, palette, rng)
    if glove is not None:
        for f in ("right", "front", "left", "back"):
            fill(im, rows(part[f], 9, 12), glove)
        fill(im, part["bottom"], glove)
    if boot is not None:
        for f in ("right", "front", "left", "back"):
            fill(im, rows(part[f], 9, 12), boot)
        fill(im, part["bottom"], boot)
    if glove is None and boot is None and tone is not None:
        for f in ("right", "front", "left", "back"):
            fill(im, rows(part[f], 9, 12), tone)
        fill(im, part["bottom"], tone)


def soldier(faction, i, palette, glove, boot):
    rng = random.Random(f"{faction}-{i}")
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    tone = SKIN_TONES[rng.randrange(len(SKIN_TONES))]
    head(im, rng, tone, HAIR[rng.randrange(len(HAIR))], EYES[rng.randrange(len(EYES))], rng.choice(["short", "short", "shaved"]))
    for f, r in BODY.items():
        if f in ("top", "bottom"):
            fill(im, r, palette[0])
        else:
            camo(im, r, palette, rng)
    # collar: a darker band at the neck
    fill(im, rows(BODY["front"], 0, 1), palette[3])
    fill(im, rows(BODY["back"], 0, 1), palette[3])
    limb_uniform(im, RARM, palette, rng, glove, None, tone)
    limb_uniform(im, LARM, palette, rng, glove, None, tone)
    limb_uniform(im, RLEG, palette, rng, None, boot, None)
    limb_uniform(im, LLEG, palette, rng, None, boot, None)
    for part in (BODY, RARM, LARM, RLEG, LLEG):
        for f in ("right", "front", "left", "back"):
            wear(im, part[f], rng, 0.05)
    return im


def scavenger(i):
    rng = random.Random(f"scav-{i}")
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    tone = SKIN_TONES[rng.randrange(len(SKIN_TONES))]
    head(im, rng, tone, HAIR[rng.randrange(len(HAIR))], EYES[rng.randrange(len(EYES))], rng.choice(["short", "long", "shaved", "short"]))
    shirt = SHIRTS[i % len(SHIRTS)]
    trousers = TROUSERS[rng.randrange(len(TROUSERS))]
    sleeves = rng.random() < 0.6   # long sleeves or bare arms
    for f, r in BODY.items():
        fill(im, r, shirt)
    # a stripe or a patch on some shirts
    if rng.random() < 0.5:
        stripe = tuple(min(255, int(c * 1.35)) for c in shirt)
        fill(im, rows(BODY["front"], 5, 7), stripe)
    for part in (RARM, LARM):
        for f, r in part.items():
            fill(im, r, shirt if sleeves else tone)
        if sleeves:
            for f in ("right", "front", "left", "back"):
                fill(im, rows(part[f], 9, 12), tone)
            fill(im, part["bottom"], tone)
    boot = (45, 38, 30) if rng.random() < 0.7 else (70, 70, 70)
    for part in (RLEG, LLEG):
        for f, r in part.items():
            fill(im, r, trousers)
        for f in ("right", "front", "left", "back"):
            fill(im, rows(part[f], 10, 12), boot)
        fill(im, part["bottom"], boot)
    for part in (BODY, RARM, LARM, RLEG, LLEG):
        for f in ("right", "front", "left", "back"):
            wear(im, part[f], rng, 0.12)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i in range(COUNT):
        soldier("nato", i, OCP, (120, 100, 70), (70, 55, 40)).save(OUT / f"nato_{i}.png")
        soldier("ruaf", i, EMR, (35, 35, 35), (30, 30, 30)).save(OUT / f"ruaf_{i}.png")
        scavenger(i).save(OUT / f"scav_{i}.png")
    # a contact sheet beside them for a look, not shipped (the resources folder is what the jar packs: keep it out)
    sheet = Image.new("RGBA", (64 * COUNT, 64 * 3), (30, 30, 30, 255))
    for i in range(COUNT):
        for row, name in enumerate(("nato", "ruaf", "scav")):
            sheet.paste(Image.open(OUT / f"{name}_{i}.png"), (i * 64, row * 64))
    sheet_path = Path(__file__).resolve().parents[1] / "build" / "skins-contact-sheet.png"
    sheet_path.parent.mkdir(exist_ok=True)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(sheet_path)
    print(f"{COUNT * 3} skins in {OUT}; contact sheet {sheet_path}")


if __name__ == "__main__":
    main()
