// GSCraft - the terrorist stops handing out the infection cure.
//
// dragonrise_reforge:terrorist drops enchanted_golden_apple at 1 %, golden_apple at 20 %, apple
// otherwise. Golden apples are in the hordes:infection_cures tag, so an enemy that drops one in five
// quietly dismantles the infection economy the Dead are built on. Measured over 40 kills with this
// script off: 11 golden and 2 enchanted, so 13 of 40 corpses handed over a cure - worse than the 20 %
// the design assumed, because the roll is per corpse and both tiers are cures.
//
// The design (enemy pass 2026-09-08, E8) asked for a DeathLootTable override. That cannot work here:
// TerroristEntity overrides dropCustomDeathLoot (m_7472_) and calls spawnAtLocation with hardcoded
// ItemStacks - read out of the bytecode - so there is no loot table to point anywhere. DeathLootTable
// only replaces the loot-table path, which this mob never uses.
//
// Forge captures those stacks during die() and offers them to LivingDropsEvent before they spawn, so
// the event is the place to act. Cancelling it suppresses every drop this mob makes, which for the
// terrorist is exactly right: all three of its drops are food and two of them are the cure. When
// gscraft:mobs/scavenger exists, give it drops from there instead of leaving the corpse empty.
//
// Verified: 20 kills, 20 cancellations, "kill @e[type=item]" finds nothing.
//
// Startup script because ForgeEvents.onEvent exists only there in KubeJS 2001 - same as
// gscraft_mech_griefing.js.
//
// Three things here cost an afternoon and are worth writing down, because every one of them fails
// silently and two of them are in the neighbouring scripts already:
//
//   1. Rhino re-enters a handler's scope on every call, so `const` and `let` declared inside one throw
//      "redeclaration of var <name>" from the second invocation onwards. The name is irrelevant. Use
//      `var` inside an event handler here. gscraft_mech_griefing.js and gscraft_tower_lock.js both use
//      `const` inside their handlers behind a silent catch - they should be checked.
//   2. Never write `catch (x) {}`. That is what turned this into a handler that appeared never to be
//      called at all, through several rounds of looking in the wrong place.
//   3. Rhino cannot walk the event's drops collection: size() reads 1, but the iterator's hasNext() is
//      falsy and toArray().length is 0, so neither removal path is reachable from a script. Cancel the
//      event, or act on the entity before it dies.
//
// An EntityType does stringify as its registry id here ("dragonrise_reforge:terrorist"), not as a
// translation key - checked, after guessing otherwise.

function prop(obj, name) {
  try { var v = obj[name]; return (typeof v === 'function') ? v.call(obj) : v; } catch (err) { return null; }
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingDropsEvent', event => {
  try {
    var who = prop(event, 'entity');
    if (!who) return;
    var kind = String(prop(who, 'type') || '');
    if (kind.indexOf('dragonrise_reforge') < 0 || kind.indexOf('terrorist') < 0) return;
    event.setCanceled(true);
  } catch (err) {
    console.error('[gscraft] terrorist drop filter failed: ' + err);
  }
});

console.info('[gscraft] terrorist cure-drop filter armed (drops cancelled)');
