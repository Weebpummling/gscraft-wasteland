package gscraft.war.station;

import gscraft.war.GscraftWar;
import gscraft.war.ModItems;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** the station's registries: the block, its item, its block entity and its menu */
public final class ModStation {
    private ModStation() {}

    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, GscraftWar.MODID);
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, GscraftWar.MODID);
    public static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(ForgeRegistries.MENU_TYPES, GscraftWar.MODID);

    public static final RegistryObject<StationBlock> STATION = BLOCKS.register("station", StationBlock::new);
    public static final RegistryObject<Item> STATION_ITEM = ModItems.ITEMS.register("station", () -> new StationItem(STATION.get(), new Item.Properties().stacksTo(1)));
    public static final RegistryObject<BlockEntityType<StationBlockEntity>> STATION_BE = BLOCK_ENTITIES.register("station",
            () -> BlockEntityType.Builder.of(StationBlockEntity::new, STATION.get()).build(null));
    public static final RegistryObject<MenuType<StationMenu>> STATION_MENU = MENUS.register("station", () -> IForgeMenuType.create(StationMenu::new));

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        BLOCK_ENTITIES.register(bus);
        MENUS.register(bus);
    }
}
