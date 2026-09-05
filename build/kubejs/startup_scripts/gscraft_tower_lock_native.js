// GSCraft - radio tower lock, the Forge-event half. KubeJS 2001 exposes ForgeEvents.onEvent to
// STARTUP scripts only, so these live here; the player-facing half (BlockEvents) is in
// server_scripts/gscraft_tower_lock.js. Same rect, same rules.
//
// explosions lose every affected block in the rect; mob griefing is denied for entities standing
// inside; fluids cannot flow in; pistons near the edge do nothing; non-player placements are cancelled.

const TOWER = { x0: 64, z0: -144, x1: 191, z1: -17 };   // tools/strongpoints.json radio_tower, tools/tower.py PAD
const DIM = 'minecraft:overworld';
// startup scripts share one scope: a plain `Result` collides with other scripts' consts (gscraft_mech_griefing.js), so the name is prefixed
const TL_Result = Java.loadClass('net.minecraftforge.eventbus.api.Event$Result');

function inRect(x, z) {
  return x >= TOWER.x0 && x <= TOWER.x1 && z >= TOWER.z0 && z <= TOWER.z1;
}
// Rhino exposes Java no-arg accessors as PROPERTIES (entity.level, level.dimension); calling them as
// functions throws a TypeError that crashes the server tick (a dolphin did, 2026-09-04). Read both ways.
function prop(o, name) {
  try { const v = o[name]; return (typeof v === 'function') ? v.call(o) : v; } catch (x) { return null; }
}
function isOverworld(level) {
  try {
    if (!level) return true;
    const d = prop(level, 'dimension');
    if (!d) return true;
    const loc = prop(d, 'location');
    return String(loc || d) === DIM;
  } catch (e) { return true; }
}
function bypassEntity(e) {
  try { return e && e.isPlayer && e.isPlayer() && e.hasPermissions(2) && e.isCreative(); } catch (x) { return false; }
}

ForgeEvents.onEvent('net.minecraftforge.event.level.ExplosionEvent$Detonate', event => {
  try {
    if (!isOverworld(prop(event, 'level'))) return;
    event.getAffectedBlocks().removeIf(p => inRect(p.getX(), p.getZ()));
  } catch (x) { console.warn('[gscraft] tower lock explosion handler: ' + x); }
});

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityMobGriefingEvent', event => {
  try {
    const e = event.getEntity();
    if (!e || !isOverworld(prop(e, 'level'))) return;
    if (inRect(Math.floor(e.getX()), Math.floor(e.getZ()))) event.setResult(TL_Result.DENY);
  } catch (x) { console.warn('[gscraft] tower lock griefing handler: ' + x); }
});

ForgeEvents.onEvent('net.minecraftforge.event.level.BlockEvent$FluidPlaceBlockEvent', event => {
  const p = event.getPos();
  if (inRect(p.getX(), p.getZ())) event.setCanceled(true);
});

ForgeEvents.onEvent('net.minecraftforge.event.level.PistonEvent$Pre', event => {
  const p = event.getPos();
  if (p.getX() >= TOWER.x0 - 13 && p.getX() <= TOWER.x1 + 13 && p.getZ() >= TOWER.z0 - 13 && p.getZ() <= TOWER.z1 + 13) {
    event.setCanceled(true);
  }
});

ForgeEvents.onEvent('net.minecraftforge.event.level.BlockEvent$EntityPlaceEvent', event => {
  const p = event.getPos();
  if (!inRect(p.getX(), p.getZ())) return;
  if (bypassEntity(event.getEntity())) return;
  event.setCanceled(true);
});

console.info('[gscraft] tower lock (native events) armed: x ' + TOWER.x0 + '..' + TOWER.x1 + ' z ' + TOWER.z0 + '..' + TOWER.z1);
