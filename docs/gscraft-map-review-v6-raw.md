# Map review: G:\GSCraft\server\wasteland-v6  (2026-09-03 04:28)

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
 "light_off": 5763,
 "no_heightmap": 5782,
 "seconds": 1887
}
```

## palette: **PASS**
```
{
 "namespaces": {
  "minecraft": 52183519,
  "superbwarfare": 6113392,
  "immersiveengineering": 2331721,
  "immersive_weathering": 1587070,
  "apotheosis": 13302,
  "farmersdelight": 4611,
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
- {'site': 'novo', 'dest': [992, 96, 1135, 255], 'chunks': 90, 'missing_chunks': 0, 'placed_blocks': 14390}
- {'site': 'plaza', 'dest': [688, 2368, 847, 2511], 'chunks': 90, 'missing_chunks': 0, 'placed_blocks': 260452}
- {'site': 'biogen_s', 'dest': [2976, 2528, 3039, 2591], 'chunks': 16, 'missing_chunks': 0, 'placed_blocks': 5777}
- {'site': 'biogen_n', 'dest': [2976, 2608, 2991, 2639], 'chunks': 2, 'missing_chunks': 0, 'placed_blocks': 4256}
- {'site': 'sewers', 'dest': [720, 2400, 815, 2495], 'chunks': 36, 'missing_chunks': 0, 'placed_blocks': 161345}
- {'site': 'hub', 'dest': [5600, 1184, 6431, 1823], 'chunks': 2080, 'missing_chunks': 0, 'placed_blocks': 693968}

## pads: **WARN**
- WARN: pad hub: 89% of terrain columns at y 82 (builds inside count as not-terrain)
```
{}
```
- {'name': 'radio_tower', 'y': 99, 'terrain_columns': 1015, 'at_level': 1014, 'share_at_level': 0.999, 'min': 99, 'max': 102, 'border_share': 1.0}
- {'name': 'novo_site', 'y': 70, 'terrain_columns': 320, 'at_level': 319, 'share_at_level': 0.997, 'min': 70, 'max': 73, 'border_share': 1.0}
- {'name': 'plaza', 'y': 70, 'terrain_columns': 320, 'at_level': 319, 'share_at_level': 0.997, 'min': 70, 'max': 73, 'border_share': 1.0}
- {'name': 'settlement', 'y': 80, 'terrain_columns': 576, 'at_level': 575, 'share_at_level': 0.998, 'min': 80, 'max': 83, 'border_share': 1.0}
- {'name': 'airfield', 'y': 67, 'terrain_columns': 6064, 'at_level': 6044, 'share_at_level': 0.997, 'min': 63, 'max': 70, 'border_share': 1.0}
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
- WARN: Walker yard: surface spread 22 blocks
- WARN: Michael plant: surface spread 28 blocks
```
{
 "crater_diff_columns": 0,
 "crater_sampled": 1024,
 "npc_sites": {
  "Marshall gatehouse": {
   "built_columns": 0,
   "surface_min": 109,
   "surface_max": 116
  },
  "Walker yard": {
   "built_columns": 0,
   "surface_min": 87,
   "surface_max": 109
  },
  "Tony clinic": {
   "built_columns": 0,
   "surface_min": 84,
   "surface_max": 89
  },
  "Michael plant": {
   "built_columns": 0,
   "surface_min": 84,
   "surface_max": 112
  },
  "Tune shack": {
   "built_columns": 0,
   "surface_min": 84,
   "surface_max": 94
  },
  "James lookout": {
   "built_columns": 0,
   "surface_min": 88,
   "surface_max": 89
  }
 }
}
```

## water: **WARN**
- WARN: plaza: 43% water around the site (causeway needed)
- WARN: plaza: 35% water around the site (causeway needed)
- WARN: road spine camp->Novo->district: 56 m of water in 6 crossing(s)
- WARN: road district->plaza: 440 m of water in 6 crossing(s)
- WARN: road district->runway: 236 m of water in 6 crossing(s)
```
{
 "sites": [
  {
   "site": "radio_tower",
   "water_share_around": 0.068
  },
  {
   "site": "novo_site",
   "water_share_around": 0.062
  },
  {
   "site": "plaza",
   "water_share_around": 0.431
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
   "water_share_around": 0.047
  },
  {
   "site": "plaza",
   "water_share_around": 0.352
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
   "water_share_around": 0.002
  },
  {
   "site": "hub",
   "water_share_around": 0.044
  }
 ],
 "roads": {
  "spine camp->Novo->district": {
   "samples": 258,
   "water_samples": 14,
   "water_metres": 56,
   "crossings": 6
  },
  "district->plaza": {
   "samples": 267,
   "water_samples": 110,
   "water_metres": 440,
   "crossings": 6
  },
  "district->runway": {
   "samples": 263,
   "water_samples": 59,
   "water_metres": 236,
   "crossings": 6
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
  "plaza": 2537,
  "biogen_s": 3927,
  "biogen_n": 3950,
  "sewers": 2545,
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
