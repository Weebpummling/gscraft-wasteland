#!/bin/sh
cd "$(dirname "$0")"; W=G:/GSCraft/scratch/worlds/v8-build
python river.py build "$W" ../buildmap/plan_v8/rivers_edges2_v8.json 2>&1 | tail -10
python roads.py route "$W" ../buildmap/plan_v8/roads_v8_stubs.json ../buildmap/plan_v8/routes_v8_stubs.json 2>&1 | tail -30
python roads.py build "$W" ../buildmap/plan_v8/routes_v8_stubs.json --style skadowsky 2>&1 | tail -30
python edgeaudit.py "$W" ../buildmap/plan_v8/sectors_v8.json ../buildmap/plan_v8/edge_features_v8.json 2>&1 | tail -1
python render_inspect.py "$W" v8_cell_pass4 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
echo FINISH DONE
