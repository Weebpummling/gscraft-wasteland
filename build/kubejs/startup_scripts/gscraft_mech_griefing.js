// GSCraft - Pomkot's Mechs never break blocks. PMB01 (the hub's Custodian) destroys terrain on Hard when
// mob griefing is on, and the pack keeps mobGriefing on (zombies need doors), so the mod's entities get
// a per-entity denial through Forge's EntityMobGriefingEvent - the same mechanism the tower lock uses.
// Startup script: ForgeEvents.onEvent exists only here in KubeJS 2001. Design: docs/notes/gscraft-pomkots-mechs.md.

const Result = Java.loadClass('net.minecraftforge.eventbus.api.Event$Result');

function prop(o, name) {
  try { const v = o[name]; return (typeof v === 'function') ? v.call(o) : v; } catch (x) { return null; }
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityMobGriefingEvent', event => {
  try {
    const entity = prop(event, 'entity');
    if (!entity) return;
    const type = String(prop(entity, 'type') || '');
    if (type.indexOf('pomkotsmechs') >= 0) event.setResult(Result.DENY);
  } catch (x) { /* never let a handler fault reach the tick */ }
});

console.info('[gscraft] mech griefing denial armed (pomkotsmechs:*)');
