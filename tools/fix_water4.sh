#!/bin/sh
cd "$(dirname "$0")"; W=G:/GSCraft/scratch/worlds/v8-build; C=G:/GSCraft/incoming/census
python shoreline.py "$W" ../buildmap/plan_v8/shoreline3_v8.json $C/v8_cell_pass6_inspect.npz 2>&1 | tail -1
python river.py build "$W" ../buildmap/plan_v8/rivers_v8.json 2>&1 | tail -1
python bridge.py "$W" ../buildmap/plan_v8/bridge_v8.json 2>&1 | grep bridge
python bridge.py "$W" ../buildmap/plan_v8/viaduct_lake_v8.json 2>&1 | grep viaduct
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
python smoothcliffs.py "$W" $C/v8_cell_pass6_inspect.npz --protect integrate_skad_mask.npz,bridge_skadowsky_highway_west_mask.npz,bridge_pripyat_highway_river_mask.npz,bridge_pripyat_road_river_mask.npz,bridge_lake_tracks_mask.npz 2>&1 | tail -2
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
rm -rf G:/GSCraft/server/wasteland-v8/region G:/GSCraft/server/wasteland-v8/entities G:/GSCraft/server/wasteland-v8/poi; cp -r "$W/region" "$W/entities" G:/GSCraft/server/wasteland-v8/ && cp "$W/level.dat" G:/GSCraft/server/wasteland-v8/ && echo staged
echo WATER4 DONE
