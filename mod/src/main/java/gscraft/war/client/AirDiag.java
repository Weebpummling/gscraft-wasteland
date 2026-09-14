package gscraft.war.client;

import gscraft.war.GscraftWar;
import gscraft.war.strike.AirRun;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.lang.reflect.Method;

/**
 * The Cobra's rotor on this client (owner, 2026-09-13: the rotor did not turn): once a second, for each airframe of a
 * run this client can see, the mod's rotor angle and its synched rate, the power and the client tick count go to the
 * client log, so a run can be read after the fact without a screen. Nothing else; a few lines per run.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID, value = Dist.CLIENT)
public final class AirDiag {
    private AirDiag() {}

    private static int t;

    private static Object call(Entity e, String name) {
        try {
            Method m = e.getClass().getMethod(name);
            return m.invoke(e);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return "?";
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || ++t % 20 != 0) return;
        for (Entity e : mc.level.entitiesForRendering()) {
            ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(e.getType());
            if (key == null || !key.toString().equals(AirRun.HELI)) continue;   // entity tags never reach the client: by type
            GscraftWar.LOG.info("[gscraft] airdiag {} tick {} rot {} rotO {} synched {} power {} pos {} dist {}", e.getType().toShortString(), e.tickCount,
                    call(e, "getPropellerRot"), call(e, "getPropellerRotO"), call(e, "getSynchedPropellerRot"), call(e, "getPower"),
                    e.blockPosition().toShortString(), mc.player == null ? "?" : String.format("%.0f", mc.player.distanceTo(e)));
        }
    }
}
