kill @e[type=minecraft:villager,tag=gscraft_npc_marshall]
summon minecraft:villager -967 69 -948 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:'{"text":"Marshall"}',Tags:["gscraft_npc","gscraft_npc_marshall"],VillagerData:{profession:"minecraft:armorer",level:2,type:"minecraft:plains"},Offers:{Recipes:[]}}
setblock -966 69 -948 minecraft:oak_sign{front_text:{messages:['{"text":"MARSHALL"}','{"text":"the gatehouse"}','{"text":"the strongpoints"}','{"text":"right-click"}']}}
