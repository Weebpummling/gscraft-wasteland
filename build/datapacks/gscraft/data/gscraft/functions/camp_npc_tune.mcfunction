kill @e[type=minecraft:villager,tag=gscraft_npc_tune]
summon minecraft:villager -922 62 -1030 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:'{"text":"Tune the Technician"}',Tags:["gscraft_npc","gscraft_npc_tune"],VillagerData:{profession:"immersiveengineering:electrician",level:2,type:"minecraft:plains"},Offers:{Recipes:[]}}
setblock -923 62 -1030 minecraft:oak_sign{front_text:{messages:['{"text":"TUNE"}','{"text":"the shack"}','{"text":"boards, radios"}','{"text":"right-click"}']}}
