kill @e[type=minecraft:villager,tag=gscraft_npc_walker]
summon minecraft:villager -959 65 -863 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:'{"text":"Walker the Foreman"}',Tags:["gscraft_npc","gscraft_npc_walker"],VillagerData:{profession:"immersiveengineering:machinist",level:2,type:"minecraft:plains"},Offers:{Recipes:[]}}
setblock -960 65 -863 minecraft:oak_sign{front_text:{messages:['{"text":"WALKER"}','{"text":"the yard"}','{"text":"bolts and nuts"}','{"text":"right-click"}']}}
