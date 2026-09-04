// GSCraft - radio tower lock, the Forge-event half. KubeJS 2001 exposes ForgeEvents.onEvent to
// STARTUP scripts only, so these live here; the player-facing half (BlockEvents) is in
// server_scripts/gscraft_tower_lock.js. Same rect, same rules.
//
// explosions lose every affected block in the rect; mob griefing is denied for entities standing
// inside; fluids cannot flow in; pistons near the edge do nothing; non-player placements are cancelled.

const TOWER = { x0: 64, z0: -144, x1: 191, z1: -17 };   // tools/strongpoints.json radio_tower, tools/tower.py PAD
const DIM = 'minecraft:overworld';
const Result = Java.loadClass('net.minecraftforge.eventbus.api.Event$Result');

function inRect(x, z) {
  return x >= TOWER.x0 && x <= TOWER.x1 && z >= TOWER.z0 && z <= TOWER.z1;
}
function isOverworld(level) {
  try { return level && String(level.dimension().location()) === DIM; } catch (e) { return true; }
}
function bypassEntity(e) {
  try { return e && e.isPlayer && e.isPlayer() && e.hasPermissions(2) && e.isCreative(); } catch (x) { return false; }
}

ForgeEvents.onEvent('net.minecraftforge.event.level.ExplosionEvent$Detonate', event => {
  if (!isOverworld(event.getLevel())) return;
  event.getAffectedBlocks().removeIf(p => inRect(p.getX(), p.getZ()));
});

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityMobGriefingEvent', event => {
  const e = event.getEntity();
  if (!e || !isOverworld(e.level())) return;
  if (inRect(Math.floor(e.getX()), Math.floor(e.getZ()))) event.setResult(Result.DENY);
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
