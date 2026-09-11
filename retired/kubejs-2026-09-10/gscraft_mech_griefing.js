// GSCraft - Pomkot's Mechs never break blocks. PMB01 (the hub's Custodian) destroys terrain on Hard when
// mob griefing is on, and the pack keeps mobGriefing on (zombies need doors), so the mod's entities get
// a per-entity denial through Forge's EntityMobGriefingEvent - the same mechanism the tower lock uses.
// Startup script: ForgeEvents.onEvent exists only here in KubeJS 2001. Design: docs/notes/gscraft-pomkots-mechs.md.

const Result = Java.loadClass('net.minecraftforge.eventbus.api.Event$Result');

function prop(o, name) {
  try { var v = o[name]; return (typeof v === 'function') ? v.call(o) : v; } catch (err) { return null; }
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityMobGriefingEvent', event => {
  try {
    // var, not const: Rhino re-enters this scope on every call and throws "redeclaration of var" from
    // the second invocation onwards. With the silent catch below that made this handler look like it
    // worked while denying nothing after the first mech. Proven in gscraft_terrorist_drops.js.
    var entity = prop(event, 'entity');
    if (!entity) return;
    var type = String(prop(entity, 'type') || '');
    if (type.indexOf('pomkotsmechs') >= 0) event.setResult(Result.DENY);
  } catch (err) { console.error('[gscraft] mech griefing denial failed: ' + err); }
});

console.info('[gscraft] mech griefing denial armed (pomkotsmechs:*)');
