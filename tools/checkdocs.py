"""Consistency check for the design documents.

Two changes on 2026-09-06/07 invalidated text scattered across the doc set: MCSP and the Vintage Vehicle
Pack were replaced by the Frontline Combat Pack and DragonRise: Reforge, and the camp moved off the
plateau into Skadowsky. This script fails if a live design document still asserts either old state
without a pointer to the doc that replaced it.

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
    "gscraft-map-review-v7.md", "gscraft-skadowsky-camp.md",
}

# The plateau camp's numbers. Any of these in a live doc must sit near a superseded banner.
PLATEAU = [
    r"-1690\s*[…\.]+\s*-1290", r"-2480\s*[…\.]+\s*-2080", r"-1792\s*[…\.]+\s*-1409",
    r"-1560\s*[…\.]+\s*-1433", r"-2460\s*[…\.]+\s*-2333", r"\(-1490,\s*-2230\)",
    r"\(-1517,\s*-2417\)", r"-1522\s*[…\.]+\s*-1459",
]
DEAD_MODS = [r"\bMCSP\b", r"\bvvp\b", r"Vintage Vehicle Pack"]
# A dead-mod mention is fine when the same line says what replaced it.
REPLACED = re.compile(r"replac|dropped|went with|re-pointed|superseded|belonged to|2026-09-06", re.I)

BANNER = "Superseded 2026-09-07"
ROUTING = "Routing rule, 2026-09-07"


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
            for pat in PLATEAU:
                if re.search(pat, line):
                    ok = near_banner(lines, i)
                    if show_all or not ok:
                        problems.append((p.name, i + 1, "plateau camp coords", ok, line.strip()[:110]))
            for pat in DEAD_MODS:
                if re.search(pat, line):
                    ctx = " ".join(lines[max(0, i - 2):i + 3])
                    ok = bool(REPLACED.search(ctx)) or near_banner(lines, i, 8)
                    if show_all or not ok:
                        problems.append((p.name, i + 1, "removed mod named", ok, line.strip()[:110]))
    stale = [x for x in problems if not x[3]]
    for name, ln, kind, ok, text in problems:
        print(f"{'ok  ' if ok else 'STALE'} {name}:{ln}  {kind}\n        {text}")
    print(f"\n{checked} live documents checked, {len(stale)} stale.")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
