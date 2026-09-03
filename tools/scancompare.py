"""Compare two worldscan JSON outputs (same dimension, e.g. the September root zip vs the October
world): chunks only in A, only in B, and chunks whose placed-block count differs a lot.

usage: scancompare.py <a.json> <b.json> [--min-placed 500]
"""
import json, sys


def load(p):
    d = json.load(open(p)); return {tuple(map(int, k.split(","))): v for k, v in d["chunks"].items()}


def main(argv):
    a, b = load(argv[1]), load(argv[2])
    mn = int(argv[argv.index("--min-placed") + 1]) if "--min-placed" in argv else 500
    only_a = [k for k in a if k not in b and a[k][0] >= mn]
    only_b = [k for k in b if k not in a and b[k][0] >= mn]
    diff = [(k, a[k][0], b[k][0]) for k in a if k in b and abs(a[k][0] - b[k][0]) >= mn]
    print(f"A chunks {len(a)}, B chunks {len(b)}; built chunks only in A: {len(only_a)}, only in B: {len(only_b)}, both but differing >= {mn}: {len(diff)}")
    def bbox(keys):
        if not keys: return None
        xs = [k[0] for k in keys]; zs = [k[1] for k in keys]; return [min(xs), min(zs), max(xs), max(zs)]
    print("only-in-A bbox (chunks):", bbox(only_a), " placed total:", sum(a[k][0] for k in only_a))
    print("only-in-B bbox (chunks):", bbox(only_b), " placed total:", sum(b[k][0] for k in only_b))
    more_a = [d for d in diff if d[1] > d[2]]; more_b = [d for d in diff if d[2] > d[1]]
    print(f"A has more in {len(more_a)} chunks (sum {sum(d[1]-d[2] for d in more_a)}), B has more in {len(more_b)} chunks (sum {sum(d[2]-d[1] for d in more_b)})")
    for k, va, vb in sorted(more_a, key=lambda d: -(d[1] - d[2]))[:15]: print("  A>B", k, va, vb)
    for k, va, vb in sorted(more_b, key=lambda d: -(d[2] - d[1]))[:15]: print("  B>A", k, va, vb)
    json.dump({"only_a": only_a, "only_b": only_b, "more_a": more_a, "more_b": more_b}, open("scancompare.json", "w"))


if __name__ == "__main__":
    main(sys.argv)
