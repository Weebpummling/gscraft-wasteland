#!/bin/sh
cd "$(dirname "$0")"; W=G:/GSCraft/scratch/worlds/v8-build
cp ../buildmap/plan_v8/roads_v8_stubs_new.json ../buildmap/plan_v8/roads_v8_stubs.json
python roads.py route "$W" ../buildmap/plan_v8/roads_v8_stubs.json ../buildmap/plan_v8/routes_v8_stubs.json 2>&1 | tail -20
python roads.py build "$W" ../buildmap/plan_v8/routes_v8_stubs.json --style skadowsky 2>&1 | tail -20
python edgeaudit.py "$W" ../buildmap/plan_v8/sectors_v8.json ../buildmap/plan_v8/edge_features_v8.json 2>&1 | tail -1
python render_inspect.py "$W" v8_cell_pass4 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
rm -rf G:/GSCraft/server/wasteland-v8/region G:/GSCraft/server/wasteland-v8/entities G:/GSCraft/server/wasteland-v8/poi
cp -r "$W/region" "$W/entities" G:/GSCraft/server/wasteland-v8/ && cp "$W/level.dat" G:/GSCraft/server/wasteland-v8/level.dat && echo "staged to server/wasteland-v8"
echo FINISH2 DONE
