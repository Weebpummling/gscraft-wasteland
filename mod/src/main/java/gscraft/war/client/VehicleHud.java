package gscraft.war.client;

import gscraft.war.GscraftWar;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** In a vehicle the player's own health and armour bars are hidden (owner, 2026-09-13): the hull's state is the vehicle's. A horse keeps them. */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID, value = Dist.CLIENT)
public final class VehicleHud {
    private VehicleHud() {}

    public static boolean inVehicle() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return false;
        Entity v = mc.player.getVehicle();
        return v != null && !(v instanceof LivingEntity);
    }

    @SubscribeEvent
    public static void pre(RenderGuiOverlayEvent.Pre event) {
        if (!inVehicle()) return;
        ResourceLocation id = event.getOverlay().id();
        if (id.equals(VanillaGuiOverlay.PLAYER_HEALTH.id()) || id.equals(VanillaGuiOverlay.ARMOR_LEVEL.id())) event.setCanceled(true);
    }
}
