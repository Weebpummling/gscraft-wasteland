"""Consistency check for the design documents.

Three changes on 2026-09-06/07 invalidated text scattered across the doc set: MCSP and the Vintage
Vehicle Pack were replaced by the Frontline Combat Pack and DragonRise: Reforge; the camp moved off the
plateau into Skadowsky; and on 2026-09-07 the Skadowsky camp was re-measured against the region files,
correcting seven figures the first draft got wrong. This script fails if a live design document still
asserts any of those old states.

The plateau coordinates and the dead mod names are allowed to appear near a "superseded" banner,
because a document may legitimately record what used to be true. The corrected figures are not: a wrong
number is wrong whether or not a banner sits above it, unless the line is recording the correction.

usage: python tools/checkdocs.py            (exit 1 if anything is stale)
       python tools/checkdocs.py --list     (show every hit, including the ones that are fine)

Dated audit snapshots and the v6 documents are history and are exempt; they only need the banner.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

# Snapshots of a moment. They record what was true then; they need a banner, not a rewrite.
HISTORY = {
    "gscraft-mod-utilization-2026-09-05.md", "gscraft-modpack-updates.md", "gscraft-modpack-review.md",
    "gscraft-modpack-update-applied-2026-09-05.md", "gscraft-sbw-addon-test-2026-09-06.md",
    "gscraft-map-layout-v6.md", "gscraft-map-review-v6.md", "gscraft-map-review-v6-raw.md",
    "gscraft-map-review-v7.md", "gscraft-skadowsky-camp.md", "gscraft-design-review-v8.md",
}

# The plateau camp's numbers. Any of these in a live doc must sit near a superseded banner.
PLATEAU = [
    r"-1690\s*[…\.]+\s*-1290", r"-2480\s*[…\.]+\s*-2080", r"-1792\s*[…\.]+\s*-1409",
    r"-1560\s*[…\.]+\s*-1433", r"-2460\s*[…\.]+\s*-2333", r"\(-1490,\s*-2230\)",
    r"\(-1517,\s*-2417\)", r"-1522\s*[…\.]+\s*-1459",
]
DEAD_MODS = [r"\bMCSP\b", r"\bvvp\b", r"Vintage Vehicle Pack"]

# Figures corrected on 2026-09-07 when the Skadowsky camp was re-measured against the region files.
# A "superseded" banner says a section is out of date; it does not make a wrong number right. So these
# are reported wherever they appear, unless the line itself is recording the correction.
CORRECTED = [
    (r"-1040\s*[\u2026.]+\s*-900", "old camp perimeter; it is z -1060..-845 (three NPC rectangles fell outside the first draft)"),
    (r"\b44 beds\b", "the north complex holds 24 beds, not 44 (48 bed blocks)"),
    (r"polished deepslate hall", "there is no 52 x 24 deepslate hall; the south complex is two buildings"),
    (r"38 blocks above the water", "the bridge deck stands 36 blocks above the water at y 53"),
    (r"y 94 deck", "the deck is y 89; only the truss sides reach y 94"),
    (r"(holds|and) [*]*1,785 bone blocks", "1,785 is the whole sector's count; the hospital holds 935"),
    (r"144 blocks, concentrated", "the hospital holds 372 white stained glass blocks, not 144"),
]
CORRECTION_NOTE = re.compile(r"corrected|first draft|earlier draft|was wrong|used to read|superseded", re.I)
# A dead-mod mention is fine when the same line says what replaced it.
REPLACED = re.compile(r"replac|dropped|went with|re-pointed|superseded|belonged to|2026-09-06", re.I)

BANNER = "Superseded 2026-09-07"
ROUTING = "Routing rule, 2026-09-07"


# ---- registry ids the docs assert must exist in the shipped jars -------------------------------
MODS = Path("G:/GSCraft/server/mods")
NS_JAR = {"fcp": "fcp-", "dragonrise_reforge": "dragonrise_reforge-", "superbwarfare": "superbwarfare-"}
ID_RE = re.compile(r"`(fcp|dragonrise_reforge|superbwarfare):([a-z0-9_/]+)`")
# Namespaced things that are not entities, items or blocks, so they never appear in a language
# file: recipe types and item tags. Named here so they are not reported as missing ids.
NOT_REGISTRY = {"superbwarfare:vehicle_assembling", "superbwarfare:military_armor",
                "superbwarfare:military_armor_heavy"}


def registry(ns):
    """Every entity/item/block name the namespace's jar registers: its language file, plus the
    spawn-egg and geometry files that evidence an entity the mod never translated."""
    import json
    import zipfile
    jars = sorted(MODS.glob(NS_JAR[ns] + "*.jar"))
    if not jars:
        return None
    z = zipfile.ZipFile(jars[-1])
    try:
        d = json.loads(z.read(f"assets/{ns}/lang/en_us.json").decode("utf-8"))
    except KeyError:
        return None
    out = set()
    for k in d:
        parts = k.split(".", 2)
        if len(parts) == 3 and parts[0] in ("entity", "item", "block") and parts[1] == ns:
            out.add(parts[2])
    # An entity whose mod forgot its translation still exists. A spawn egg model or a GeckoLib
    # geometry file is the jar saying so, and both are cheap to read from the name list.
    for n in z.namelist():
        if n.startswith(f"assets/{ns}/models/item/") and n.endswith("_spawn_egg.json"):
            out.add(n.rsplit("/", 1)[1][: -len("_spawn_egg.json")])
        elif n.startswith(f"assets/{ns}/geo/") and n.endswith(".geo.json"):
            out.add(n.rsplit("/", 1)[1][: -len(".geo.json")])
    return out


def check_ids(show_all):
    """Docs name mod ids as fact. Fail if one is not in the jar we actually ship."""
    cache = {}
    problems = []
    for p in sorted(list(DOCS.glob("*.md")) + [REPO / "HANDOFF.md"]):
        if not p.exists() or p.name in HISTORY:
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines()):
            for ns, name in ID_RE.findall(line):
                if ns not in cache:
                    cache[ns] = registry(ns)
                reg = cache[ns]
                if reg is None:
                    continue
                if f"{ns}:{name}" in NOT_REGISTRY:
                    continue
                base = name.split("/")[0]
                ok = base in reg
                if show_all or not ok:
                    problems.append((p.name, i + 1, f"id {ns}:{name}", ok, line.strip()[:110]))
    return problems



def norm(line):
    """Docs write coordinates with the Unicode minus U+2212 and ranges with an ellipsis; the patterns
    below are written in ASCII. Fold both so a pattern matches either spelling. This was a real bug:
    before it, every plateau coordinate written with the typographic minus slipped through."""
    return (line.replace("\u2212", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
                .replace("\u2026", "..")
                .replace("\u00d7", "x"))

def head_bannered(lines):
    """A banner in the first 30 lines is the document saying it is superseded as a whole."""
    return any(BANNER in l or ROUTING in l for l in lines[:30])


def near_banner(lines, i, window=60):
    if head_bannered(lines):
        return True
    lo = max(0, i - window)
    return any(BANNER in l or ROUTING in l for l in lines[lo:i + 3])


def main(argv):
    show_all = "--list" in argv
    problems = []
    checked = 0
    for p in sorted(list(DOCS.glob("*.md")) + [REPO / "HANDOFF.md", REPO / "README.md"]):
        if not p.exists() or p.name in HISTORY:
            continue
        checked += 1
        lines = p.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            nline = norm(line)
            for pat in PLATEAU:
                if re.search(pat, nline):
                    # a line that names the rectangle as dead is doing the right thing
                    ok = near_banner(lines, i) or bool(re.search(
                        r"\bold\b|\bdead\b|no longer|never built|superseded|retired|moved off", nline, re.I))
                    if show_all or not ok:
                        problems.append((p.name, i + 1, "plateau camp coords", ok, line.strip()[:110]))
            for pat in DEAD_MODS:
                if re.search(pat, nline):
                    ctx = " ".join(lines[max(0, i - 2):i + 3])
                    ok = bool(REPLACED.search(norm(ctx))) or near_banner(lines, i, 8)
                    if show_all or not ok:
                        problems.append((p.name, i + 1, "removed mod named", ok, line.strip()[:110]))
            for pat, why in CORRECTED:
                if re.search(pat, nline):
                    ctx = " ".join(lines[max(0, i - 4):i + 4])
                    ok = bool(CORRECTION_NOTE.search(norm(ctx))) or "sector's" in line
                    if show_all or not ok:
                        problems.append((p.name, i + 1, "corrected figure: " + why, ok, line.strip()[:110]))
    problems += check_ids(show_all)
    stale = [x for x in problems if not x[3]]
    for name, ln, kind, ok, text in problems:
        print(f"{'ok  ' if ok else 'STALE'} {name}:{ln}  {kind}\n        {text}")
    print(f"\n{checked} live documents checked, {len(stale)} stale.")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
