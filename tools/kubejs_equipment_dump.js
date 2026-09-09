// TEMPORARY: dump every wearable and weapon in the pack, from the live registry.
//
// Asset scanning cannot answer this - it cannot tell an armour item from a block model and cannot tell
// which slot a piece goes in. The registry can. Output goes to the console because KubeJS's class
// filter blocks java.nio.file, and is read back out of logs/latest.log.
//
// var, not const, inside the handler: Rhino re-enters the scope and const throws.
// instanceof, not .class.isInstance: a Java class from Java.loadClass has no reachable `class` member.

ServerEvents.loaded(event => {
  try {
    var Registries = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
    var ArmorItem = Java.loadClass('net.minecraft.world.item.ArmorItem');
    var TieredItem = Java.loadClass('net.minecraft.world.item.TieredItem');
    var SwordItem = Java.loadClass('net.minecraft.world.item.SwordItem');
    var BowItem = Java.loadClass('net.minecraft.world.item.BowItem');
    var CrossbowItem = Java.loadClass('net.minecraft.world.item.CrossbowItem');
    var ShieldItem = Java.loadClass('net.minecraft.world.item.ShieldItem');

    var it = Registries.ITEM.iterator();
    var n = 0;
    while (it.hasNext()) {
      var item = it.next();
      var id = String(Registries.ITEM.getKey(item));
      var kind = null;
      var extra = '';
      if (item instanceof ArmorItem) {
        kind = 'ARMOR';
        try {
          extra = String(item.getEquipmentSlot()) + '|def=' + item.getDefense()
                  + '|tough=' + item.getToughness();
        } catch (err) {
          try { extra = String(item.getEquipmentSlot()); } catch (e2) { extra = '?'; }
        }
      } else if (item instanceof ShieldItem) {
        kind = 'SHIELD';
      } else if (item instanceof SwordItem) {
        kind = 'SWORD';
      } else if (item instanceof BowItem || item instanceof CrossbowItem) {
        kind = 'BOW';
      } else if (item instanceof TieredItem) {
        kind = 'TOOL';
      }
      if (kind) { console.info('EQUIPDUMP\t' + kind + '\t' + id + '\t' + extra); n++; }
      else if (id.indexOf('minecraft:') !== 0) {
        // everything else in a mod namespace, by its Java class, so gun items that are not vanilla
        // subclasses stay visible. TACZ and Superb Warfare weapons are custom Item classes.
        console.info('CLASSDUMP' + '	' + id + '	' + String(item.getClass().getSimpleName()));
      }
    }
    console.info('[gscraft] equipment dump: ' + n + ' items');
  } catch (err) {
    console.error('[gscraft] equipment dump failed: ' + err);
  }
});
