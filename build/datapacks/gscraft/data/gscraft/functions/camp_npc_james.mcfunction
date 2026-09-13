kill @e[type=minecraft:villager,tag=gscraft_npc_james]
summon minecraft:villager -893 66 -971 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:'{"text":"James the Scout"}',Tags:["gscraft_npc","gscraft_npc_james"],VillagerData:{profession:"minecraft:cartographer",level:2,type:"minecraft:plains"},Offers:{Recipes:[]}}
setblock -892 66 -971 minecraft:oak_sign{front_text:{messages:['{"text":"JAMES"}','{"text":"the signal box"}','{"text":"the map"}','{"text":"right-click"}']}}
