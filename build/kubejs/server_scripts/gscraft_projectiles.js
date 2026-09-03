// GSCraft - projectiles never freeze at the edge of the simulated area.
//
// Why: the server only ticks entities inside the simulation distance around players. A rocket that
// flies past that ring stops dead in a chunk that is still visible, then wakes up when a player
// comes near and seems to "follow" them. Neither Superb Warfare nor TaCZ has a lifetime or range
// setting, so this script retires any gun-mod projectile that is (a) about to leave the simulated
// ring around every player or (b) older than MAX_AGE ticks. Mines, placed charges, vehicles and
// drones are not touched.

const MAX_AGE = 20 * 30;          // 30 s of flight is farther than any weapon in the pack reaches
const EDGE_MARGIN = 40;           // blocks inside the simulation edge at which a projectile is retired
const EVERY = 5;                  // ticks between sweeps

const SW = new Set([
  'projectile', 'rpg_rocket_standard', 'rpg_rocket_tbg', 'small_rocket', 'medium_rocket', 'mortar_shell',
  'cannon_shell', 'small_cannon_shell', 'gun_grenade', 'hand_grenade', 'rgo_grenade', 'javelin_missile',
  'igla_9k38_missile', 'ru_9m336_missile', 'wire_guide_missile', 'agm_65', 'kh_39', 'tow', 'mk_82',
  'blu_43', 'bl_132', 'grapeshot', 'taser_bullet', 'ptkm_projectile', 'melon_bomb', 'flare_decoy', 'smoke_decoy'
]);

function isProjectile(type) {
  const i = type.indexOf(':');
  if (i < 0) return false;
  const ns = type.substring(0, i), path = type.substring(i + 1);
  if (ns === 'superbwarfare') return SW.has(path);
  if (ns === 'tacz') return path !== 'target_minecart';
  return false;
}

ServerEvents.tick(event => {
  const server = event.server;
  if (server.tickCount % EVERY !== 0) return;
  const players = server.players;
  if (players.length === 0) return;
  // simulation distance in blocks, less the margin; never below 64 so short ranges still work
  const simBlocks = Math.max(64, server.getPlayerList().getSimulationDistance() * 16 - EDGE_MARGIN);
  const limitSq = simBlocks * simBlocks;
  for (const level of server.levels) {
    const ents = level.getEntities();
    for (const e of ents) {
      const type = String(e.type);
      if (!isProjectile(type)) continue;
      if (e.age > MAX_AGE) { e.discard(); continue; }
      let near = false;
      for (const p of players) {
        if (p.level.dimension !== level.dimension) continue;
        if (e.distanceToSqr(p) <= limitSq) { near = true; break; }
      }
      if (!near) e.discard();
    }
  }
});

console.info('[gscraft] projectile sweep armed: retire gun-mod projectiles at the simulation edge or after ' + (MAX_AGE / 20) + ' s');
