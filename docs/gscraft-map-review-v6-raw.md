# Map review: G:\GSCraft\server\wasteland-v6  (2026-09-03 07:49)

## chunks: **FAIL**
```
{
 "region_files": 441,
 "chunks": 421201,
 "unparseable": {
  "section Y out of range": 23
 },
 "data_versions": {
  "3465": 421201
 },
 "light_off": 6373,
 "no_heightmap": 6392,
 "seconds": 1229
}
```

## palette: **PASS**
```
{
 "namespaces": {
  "minecraft": 52180662,
  "superbwarfare": 6113403,
  "immersiveengineering": 2331693,
  "immersive_weathering": 1585757,
  "apotheosis": 13299,
  "farmersdelight": 4607,
  "factory_blocks": 3690,
  "chisel": 1191,
  "refurbished_furniture": 1014,
  "antiblocksrechiseled": 866,
  "doomsday_decoration": 529,
  "lootr": 45,
  "magnumtorch": 15,
  "sophisticatedbackpacks": 1
 },
 "outside_pack": {},
 "legacy_112_names": {}
}
```

## entities: **FAIL**
```
{
 "block_entities_outside_pack": {
  "DUMMY": 539
 }
}
```

## sites: **PASS**
```
{
 "ship_boxes_solid_blocks": [
  0,
  0
 ]
}
```
- {'site': 'settlement', 'dest': [3520, 640, 3791, 927], 'chunks': 306, 'missing_chunks': 0, 'placed_blocks': 84644}
- {'site': 'novo', 'dest': [992, 96, 1135, 255], 'chunks': 90, 'missing_chunks': 0, 'placed_blocks': 14655}
- {'site': 'plaza', 'dest': [-1952, 848, -1793, 991], 'chunks': 90, 'missing_chunks': 0, 'placed_blocks': 260452}
- {'site': 'biogen_s', 'dest': [2976, 2528, 3039, 2591], 'chunks': 16, 'missing_chunks': 0, 'placed_blocks': 6008}
- {'site': 'biogen_n', 'dest': [2976, 2608, 2991, 2639], 'chunks': 2, 'missing_chunks': 0, 'placed_blocks': 4256}
- {'site': 'sewers', 'dest': [-1920, 880, -1825, 975], 'chunks': 36, 'missing_chunks': 0, 'placed_blocks': 161345}
- {'site': 'hub', 'dest': [5600, 1184, 6431, 1823], 'chunks': 2080, 'missing_chunks': 0, 'placed_blocks': 693968}

## pads: **WARN**
- WARN: pad hub: 89% of terrain columns at y 82 (builds inside count as not-terrain)
```
{}
```
- {'name': 'radio_tower', 'y': 99, 'terrain_columns': 1015, 'at_level': 996, 'share_at_level': 0.981, 'min': 91, 'max': 102, 'border_share': 1.0}
- {'name': 'novo_site', 'y': 70, 'terrain_columns': 298, 'at_level': 292, 'share_at_level': 0.98, 'min': 62, 'max': 73, 'border_share': 0.85}
- {'name': 'plaza', 'y': 70, 'terrain_columns': 517, 'at_level': 502, 'share_at_level': 0.971, 'min': 70, 'max': 82, 'border_share': 1.0}
- {'name': 'settlement', 'y': 80, 'terrain_columns': 571, 'at_level': 564, 'share_at_level': 0.988, 'min': 75, 'max': 83, 'border_share': 1.0}
- {'name': 'airfield', 'y': 67, 'terrain_columns': 6030, 'at_level': 6009, 'share_at_level': 0.997, 'min': 63, 'max': 70, 'border_share': 0.98}
- {'name': 'hub', 'y': 82, 'terrain_columns': 1488, 'at_level': 1323, 'share_at_level': 0.889, 'min': 71, 'max': 102, 'border_share': 1.0}

## tower: **PASS**
```
{
 "blocks_above_pad": 414,
 "by_name": {
  "immersiveengineering:concrete_tile": 158,
  "immersiveengineering:concrete": 107,
  "immersiveengineering:steel_fence": 60,
  "immersiveengineering:sheetmetal_steel": 32,
  "minecraft:cobblestone": 21,
  "immersiveengineering:steel_scaffolding_standard": 15,
  "minecraft:yellow_concrete": 12,
  "minecraft:gravel": 9
 }
}
```

## camp: **WARN**
- WARN: Marshall gatehouse: 9 built columns on the site
```
{
 "crater_diff_columns": 0,
 "crater_sampled": 1024,
 "npc_sites": {
  "Marshall gatehouse": {
   "built_columns": 9,
   "surface_min": 110,
   "surface_max": 111
  },
  "Walker yard": {
   "built_columns": 0,
   "surface_min": 94,
   "surface_max": 94
  },
  "Tony clinic": {
   "built_columns": 0,
   "surface_min": 84,
   "surface_max": 84
  },
  "Michael plant": {
   "built_columns": 0,
   "surface_min": 108,
   "surface_max": 108
  },
  "Tune shack": {
   "built_columns": 0,
   "surface_min": 85,
   "surface_max": 85
  },
  "James lookout": {
   "built_columns": 0,
   "surface_min": 88,
   "surface_max": 88
  }
 }
}
```

## water: **PASS**
```
{
 "sites": [
  {
   "site": "radio_tower",
   "water_share_around": 0.068
  },
  {
   "site": "novo_site",
   "water_share_around": 0.06
  },
  {
   "site": "plaza",
   "water_share_around": 0.066
  },
  {
   "site": "settlement",
   "water_share_around": 0.061
  },
  {
   "site": "airfield",
   "water_share_around": 0.072
  },
  {
   "site": "hub",
   "water_share_around": 0.064
  },
  {
   "site": "settlement",
   "water_share_around": 0.044
  },
  {
   "site": "novo",
   "water_share_around": 0.045
  },
  {
   "site": "plaza",
   "water_share_around": 0.052
  },
  {
   "site": "biogen_s",
   "water_share_around": 0.0
  },
  {
   "site": "biogen_n",
   "water_share_around": 0.0
  },
  {
   "site": "sewers",
   "water_share_around": 0.0
  },
  {
   "site": "hub",
   "water_share_around": 0.043
  }
 ],
 "roads": {
  "spine_camp_novo_district": {
   "samples": 524,
   "water_samples": 0,
   "water_metres": 0,
   "crossings": 0
  },
  "west_road_camp_plaza": {
   "samples": 820,
   "water_samples": 0,
   "water_metres": 0,
   "crossings": 0
  },
  "district_runway": {
   "samples": 520,
   "water_samples": 0,
   "water_metres": 0,
   "crossings": 0
  },
  "district_settlement": {
   "samples": 191,
   "water_samples": 0,
   "water_metres": 0,
   "crossings": 0
  }
 }
}
```

## distances: **WARN**
- WARN: strongpoints plant and fr06 are 418 m apart (< 500 m)
```
{
 "from_camp_m": {
  "settlement": 3720,
  "novo": 1060,
  "plaza": 2094,
  "biogen_s": 3927,
  "biogen_n": 3950,
  "sewers": 2097,
  "hub": 6181,
  "residential": 2031,
  "plant": 2336,
  "fr06": 2454,
  "tower": 147
 }
}
```

## border: **PASS**
```
{
 "border": {
  "BorderCenterX": 1900.5,
  "BorderCenterZ": 1250.5,
  "BorderSize": 10000.0
 },
 "spawn": [
  19,
  94,
  26
 ]
}
```
