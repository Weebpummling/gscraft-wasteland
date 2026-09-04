# GSCraft - FR-06's reactor plaza: one dormant PMS04 missile platform beside the BMPT and the Strykers of the site
# dressing pass (design section 2.3). NoAI, invulnerable: it never activates; it is the visual link between the reactor's
# technology and the hub's mechs. Coordinates are the plaza's centre at the district's street level - the visual pass
# sets the exact spot and height (gaps C16). Design: docs/notes/gscraft-pomkots-mechs.md section 2.
kill @e[type=pomkotsmechs:pms04,tag=gscraft_dressing]
summon pomkotsmechs:pms04 2383 100 663 {NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Tags:["gscraft_dressing"]}
