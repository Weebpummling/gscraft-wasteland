package gscraft.war;

import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, GscraftWar.MODID);

    public static final RegistryObject<Item> NATO_SOLDIER_EGG = ITEMS.register("nato_soldier_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.NATO_SOLDIER, 0x4B5320, 0x1F3A5F, new Item.Properties()));
    public static final RegistryObject<Item> RUAF_SOLDIER_EGG = ITEMS.register("ruaf_soldier_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.RUAF_SOLDIER, 0x5B6B3A, 0x8A1C1C, new Item.Properties()));
    public static final RegistryObject<Item> SCAVENGER_EGG = ITEMS.register("scavenger_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SCAVENGER, 0x6B5B3E, 0xA86C12, new Item.Properties()));

    public static final RegistryObject<Item> BLOATER_EGG = ITEMS.register("bloater_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.BLOATER, 0x5C6B3A, 0x8B9A46, new Item.Properties()));
    public static final RegistryObject<Item> MATRON_EGG = ITEMS.register("matron_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.MATRON, 0xC2B280, 0x6E2C2C, new Item.Properties()));

    private ModItems() {}

    static void creativeTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) {
            event.accept(NATO_SOLDIER_EGG);
            event.accept(RUAF_SOLDIER_EGG);
            event.accept(SCAVENGER_EGG);
            event.accept(BLOATER_EGG);
            event.accept(MATRON_EGG);
        }
    }
}
