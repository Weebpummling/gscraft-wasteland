package gscraft.war;

import com.mojang.logging.LogUtils;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/**
 * GSCraft War: the enemy system as one mod. Bodies, loyalty, loadout, placement and memory live here instead
 * of across In Control, KubeJS, Improved Mobs and Mob Factions. See docs/gscraft-war-mod-design.md.
 */
@Mod(GscraftWar.MODID)
public class GscraftWar {
    public static final String MODID = "gscraft";
    public static final Logger LOG = LogUtils.getLogger();

    public GscraftWar() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModEntities.ENTITIES.register(modBus);
        ModItems.ITEMS.register(modBus);
        modBus.addListener(ModEntities::attributes);
        modBus.addListener(ModItems::creativeTabs);
    }
}
