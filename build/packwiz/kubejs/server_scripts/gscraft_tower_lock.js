// GSCraft - the radio tower compound is locked. Nothing changes a block inside it except the
// quest's stage functions (server-run `/place template`, which no event below can touch).
// Rect: the tower pad in the camp, all heights, overworld only. Ops in creative bypass the
// player rules so the world build can still be edited by hand.
//
// This file: player break / place / right-click cancelled (server script).
// startup_scripts/gscraft_tower_lock_native.js: explosions, mob griefing, fluids, pistons, non-player placements.

const TOWER = { x0: 64, z0: -144, x1: 191, z1: -17 };   // tools/strongpoints.json radio_tower, tools/tower.py PAD
const DIM = 'minecraft:overworld';

function inRect(x, z) {
  return x >= TOWER.x0 && x <= TOWER.x1 && z >= TOWER.z0 && z <= TOWER.z1;
}
function bypass(player) {
  return player && player.hasPermissions(2) && player.isCreative();
}
function overworld(level) {
  return level && String(level.dimension) === DIM;
}

BlockEvents.broken(event => {
  if (!overworld(event.level) || !inRect(event.block.x, event.block.z)) return;
  if (bypass(event.player)) return;
  event.cancel();
});

BlockEvents.placed(event => {
  if (!overworld(event.level) || !inRect(event.block.x, event.block.z)) return;
  if (bypass(event.player)) return;      // event.player is null for non-player placements: cancelled too
  event.cancel();
});

BlockEvents.rightClicked(event => {
  if (!overworld(event.level) || !inRect(event.block.x, event.block.z)) return;
  if (bypass(event.player)) return;
  event.cancel();
});

// The explosion / mob-griefing / fluid / piston / entity-place layers are Forge events, which KubeJS 2001
// only exposes to startup scripts: see startup_scripts/gscraft_tower_lock_native.js.

console.info('[gscraft] tower lock armed: x ' + TOWER.x0 + '..' + TOWER.x1 + ' z ' + TOWER.z0 + '..' + TOWER.z1);
