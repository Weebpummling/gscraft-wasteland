package gscraft.war;

import gscraft.war.item.SliceItems;
import gscraft.war.station.ModStation;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** the mod's own creative tab (owner, 2026-09-13): the station, the bandage, every slice item, the strikes, the spawn eggs */
public final class ModTab {
    private ModTab() {}

    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, GscraftWar.MODID);

    public static final RegistryObject<CreativeModeTab> GSCRAFT = TABS.register("gscraft", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.gscraft"))
            .icon(() -> new ItemStack(ModStation.STATION_ITEM.get()))
            .displayItems((params, out) -> {
                out.accept(ModStation.STATION_ITEM.get());
                out.accept(ModItems.BANDAGE.get());
                for (RegistryObject<Item> it : SliceItems.REGISTERED) out.accept(it.get());
                out.accept(ModItems.NATO_SOLDIER_EGG.get());
                out.accept(ModItems.RUAF_SOLDIER_EGG.get());
                out.accept(ModItems.SCAVENGER_EGG.get());
                out.accept(ModItems.BLOATER_EGG.get());
                out.accept(ModItems.MATRON_EGG.get());
            })
            .build());
}
