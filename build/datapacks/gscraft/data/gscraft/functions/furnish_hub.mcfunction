# GSCraft - the hub's street furniture: two dormant Pomkot's Mechs on the rail spine (NoAI, invulnerable, silent),
# placed like the dead vehicles. Run once after the hub is staged. Coordinates are the hub's centre line at the
# pad level (docs/gscraft-map-layout-v6.md: x 5600..6431, z 1184..1823, pad y 82) - the visual pass moves them to the
# exact street spots (gaps C16). Design: docs/notes/gscraft-pomkots-mechs.md section 2.
kill @e[type=pomkotsmechs:pms02,tag=gscraft_dressing]
kill @e[type=pomkotsmechs:pms05,tag=gscraft_dressing]
summon pomkotsmechs:pms02 5990 83 1480 {NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Tags:["gscraft_dressing"]}
summon pomkotsmechs:pms05 6040 83 1530 {NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Tags:["gscraft_dressing"]}
