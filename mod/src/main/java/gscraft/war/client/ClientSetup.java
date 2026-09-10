package gscraft.war.client;

import gscraft.war.GscraftWar;
import gscraft.war.ModEntities;
import gscraft.war.entity.Bloater;
import gscraft.war.entity.Matron;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = GscraftWar.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientSetup {
    private ClientSetup() {}

    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.NATO_SOLDIER.get(), FighterRenderer::new);
        event.registerEntityRenderer(ModEntities.RUAF_SOLDIER.get(), FighterRenderer::new);
        event.registerEntityRenderer(ModEntities.SCAVENGER.get(), FighterRenderer::new);
        event.registerEntityRenderer(ModEntities.BLOATER.get(), ctx -> new ScaledZombieRenderer(ctx, Bloater.RENDER_SCALE, false));
        event.registerEntityRenderer(ModEntities.MATRON.get(), ctx -> new ScaledZombieRenderer(ctx, Matron.RENDER_SCALE, true));
    }
}
