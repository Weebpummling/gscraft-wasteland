#!/bin/sh
cd "$(dirname "$0")"; W=G:/GSCraft/scratch/worlds/v8-build; F=G:/GSCraft/scratch/worlds/fresh_sectors
python integrate.py "$W" "$F" skad 2>&1 | grep -E "written|Traceback"
python river.py build "$W" ../buildmap/plan_v8/rivers_v8.json 2>&1 | tail -1
python river.py build "$W" ../buildmap/plan_v8/rivers_arm_v8.json 2>&1 | tail -1
python bridge.py "$W" ../buildmap/plan_v8/bridge_v8.json 2>&1 | grep bridge
python bridge.py "$W" ../buildmap/plan_v8/viaducts_v8.json 2>&1 | grep viaduct
python bridge.py "$W" ../buildmap/plan_v8/viaduct_lake_v8.json 2>&1 | grep viaduct
python shoreline.py "$W" ../buildmap/plan_v8/shoreline_v8.json G:/GSCraft/incoming/census/v8_cell_pass6_inspect.npz 2>&1 | tail -6
python regrade.py "$W" -300 -3115 -210 -3040 2>&1 | tail -1
python lakefill.py "$W" ../buildmap/plan_v8/lakefill_canopy_v8.json 2>&1 | tail -1
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
python smoothcliffs.py "$W" G:/GSCraft/incoming/census/v8_cell_pass6_inspect.npz --protect integrate_skad_mask.npz,bridge_skadowsky_highway_west_mask.npz,bridge_pripyat_highway_river_mask.npz,bridge_pripyat_road_river_mask.npz,bridge_lake_tracks_mask.npz 2>&1 | tail -2
python render_inspect.py "$W" v8_cell_pass6 -3900 -3900 1200 700 1 2>&1 | sed -n 2,2p
rm -rf G:/GSCraft/server/wasteland-v8/region G:/GSCraft/server/wasteland-v8/entities G:/GSCraft/server/wasteland-v8/poi; cp -r "$W/region" "$W/entities" G:/GSCraft/server/wasteland-v8/ && cp "$W/level.dat" G:/GSCraft/server/wasteland-v8/ && echo staged
echo WATER2 DONE
