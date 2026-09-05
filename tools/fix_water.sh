#!/bin/sh
cd "$(dirname "$0")"; W=G:/GSCraft/scratch/worlds/v8-build
for n in old12_S old16_S old20_W old23_W old24_S old27_W; do python unroad.py "$W" ../buildmap/plan_v8/routes_v8_long.json $n 2>&1 | tail -1; done
python lakefill.py "$W" ../buildmap/plan_v8/lakefill_v8.json 2>&1 | tail -8
python river.py build "$W" ../buildmap/plan_v8/rivers_arm_v8.json 2>&1 | tail -1
python bridge.py "$W" ../buildmap/plan_v8/viaduct_lake_v8.json 2>&1 | tail -1
python roads.py route "$W" ../buildmap/plan_v8/roads_v8_lake.json ../buildmap/plan_v8/routes_v8_lake.json 2>&1 | tail -8
python roads.py build "$W" ../buildmap/plan_v8/routes_v8_lake.json --style skadowsky 2>&1 | tail -8
python river.py build "$W" ../buildmap/plan_v8/rivers_v8.json 2>&1 | tail -1
python bridge.py "$W" ../buildmap/plan_v8/bridge_v8.json 2>&1 | head -1
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
python smoothcliffs.py "$W" G:/GSCraft/incoming/census/v8_cell_pass6_inspect.npz --protect integrate_skad_mask.npz 2>&1 | tail -1
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
echo WATER DONE
