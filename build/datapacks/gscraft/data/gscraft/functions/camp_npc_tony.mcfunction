kill @e[type=minecraft:villager,tag=gscraft_npc_tony]
summon minecraft:villager -948 62 -1036 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:'{"text":"Tony the Medic"}',Tags:["gscraft_npc","gscraft_npc_tony"],VillagerData:{profession:"minecraft:cleric",level:2,type:"minecraft:plains"},Offers:{Recipes:[]}}
setblock -947 62 -1036 minecraft:oak_sign{front_text:{messages:['{"text":"TONY"}','{"text":"the clinic"}','{"text":"bandages"}','{"text":"right-click"}']}}
