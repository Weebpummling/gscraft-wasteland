// GSCraft - the Scavengers fight the dead, not you. Unless you start it.
//
// They are scavengers, not raiders: their quarrel is with what the town became, and a player walking
// past is competition rather than prey. So a Scavenger will hunt zombies on sight and leave a player
// alone until the player draws first - at which point it stays angry for good.
//
// Two halves:
//   1. LivingChangeTargetEvent - if a Scavenger picks a player as its target and has not been hit by
//      one, refuse the target. Everything else it wants to fight, it may.
//   2. LivingHurtEvent - a player hitting a Scavenger tags it, and the tag is what unlocks the target.
//      A tag rather than getLastHurtByMob because that field expires after about a hundred ticks, and
//      a grudge should outlast a missed swing.
//
// var, not const, inside handlers: Rhino re-enters the scope and const throws from the first call.
// Never swallow the exception unlogged - that is how three of these scripts stayed broken for weeks.

var SCAV_TYPES = ['pillager', 'vindicator', 'terrorist'];
var PROVOKED = 'gs_provoked';

function isScav(e) {
  try {
    var t = String(e.type);
    for (var i = 0; i < SCAV_TYPES.length; i++) {
      if (t.indexOf(SCAV_TYPES[i]) >= 0) return true;
    }
  } catch (err) { /* an entity with no type is not one of ours */ }
  return false;
}

function hasTag(e, tag) {
  try { return e.tags.contains(tag); } catch (err) { return false; }
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingChangeTargetEvent', event => {
  try {
    var who = event.getEntity();
    if (!who || !isScav(who)) return;
    var target = event.getNewTarget();
    if (!target) return;
    if (String(target.type).indexOf('player') < 0) return;   // mobs are fair game
    if (hasTag(who, PROVOKED)) return;                       // it has been hit; let it answer
    event.setCanceled(true);
  } catch (err) {
    console.error('[gscraft] scavenger target filter failed: ' + err);
  }
});

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingHurtEvent', event => {
  try {
    var who = event.getEntity();
    if (!who || !isScav(who)) return;
    var src = event.getSource();
    if (!src) return;
    // DamageSource here has no getEntity(); KubeJS wraps it and the attacker hangs off a different
    // accessor depending on the source. Try each, and treat "none of them" as "not a player".
    var by = null;
    try { by = src.getEntity(); } catch (err) { by = null; }
    if (!by) { try { by = src.actual; } catch (err) { by = null; } }
    if (!by) { try { by = src.player; } catch (err) { by = null; } }
    if (!by) { try { by = src.getDirectEntity(); } catch (err) { by = null; } }
    if (!by || String(by.type).indexOf('player') < 0) return;
    if (!hasTag(who, PROVOKED)) who.addTag(PROVOKED);
  } catch (err) {
    console.error('[gscraft] scavenger provoke tag failed: ' + err);
  }
});

console.info('[gscraft] scavengers are neutral to players until struck');
