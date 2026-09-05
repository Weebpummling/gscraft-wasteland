#!/bin/sh
# v8 pass 4: every transplanted sector onto the landscape (hub + Skadowsky included; the river is re-carved after Skadowsky
# because its margin restore erases the channel), then the settlement's removal, the edge audit and a full-cell render.
cd "$(dirname "$0")"
W=G:/GSCraft/scratch/worlds/v8-build
F=G:/GSCraft/scratch/worlds/fresh_sectors
run() { echo "== $1"; python integrate.py "$W" "$F" "$1" 2>&1 | grep -E "pass 1|lift|nothing|mask:|targets|written|Error|Traceback"; }
run hub; run skad
python river.py build "$W" ../buildmap/plan_v8/rivers_v8.json 2>&1 | tail -1
python bridge.py "$W" ../buildmap/plan_v8/bridge_v8.json 2>&1 | head -1
for s in novo plaza biogen settle mega indu hemp lib \
         old01 old02 old03 old04 old05 old06 old07 old08 old09 old10 old11 old12 old13 old14 old15 \
         old16 old17 old18 old19 old20 old21 old22 old23 old24 old25 old26 old27 old28 old29; do run $s; done
python edgeaudit.py "$W" ../buildmap/plan_v8/sectors_v8.json ../buildmap/plan_v8/edge_features_v8.json 2>&1 | tail -1
python render_inspect.py "$W" v8_cell_pass4 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
echo BATCH DONE
