import sys, collections
from pathlib import Path
from transplant import R, read_region_raw, T_COMPOUND, T_LIST, T_STRING
c = collections.Counter()
for f in sorted(Path(sys.argv[1]).glob("*.mca")):
    for slot, (ts, comp, raw) in read_region_raw(f).items():
        if b"LootTable" not in raw: continue
        name, root = R(raw).root()
        for be in root.get("block_entities", (T_LIST, (T_COMPOUND, [])))[1][1]:
            lt = be.get("LootTable")
            if lt and lt[0] == T_STRING: c[lt[1]] += 1
ns = collections.Counter()
for k, v in c.items(): ns[k.split(":")[0]] += v
print("by namespace:", dict(ns.most_common()))
for k, v in c.most_common(): print(f"{v:5d}  {k}")
