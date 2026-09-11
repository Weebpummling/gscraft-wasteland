package gscraft.war.world;

import gscraft.war.GscraftWar;
import gscraft.war.WarEvents;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * The hold (owner's standing ruling: no hostile spawns until the designers finish building, and nothing at KROT or a
 * player build ever). In Control carried it as three rules - allow the mod's own types, allow anything tagged
 * {@code gs_placed}, deny every other hostile joining the overworld - and the mod carries the same three here, so
 * In Control could go (fold-in review R1). Everything the director places is tagged; a bare /summon of a hostile
 * is refused, as it was, unless it carries the tag.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Hold {
    private static volatile boolean enabled = true;
    private static long refused;

    private Hold() {}

    @SubscribeEvent
    public static void joined(EntityJoinLevelEvent event) {
        if (!enabled || event.getLevel().isClientSide() || event.getLevel().dimension() != Level.OVERWORLD) return;
        Entity entity = event.getEntity();
        if (!(entity instanceof Mob) || !(entity instanceof Enemy)) return;
        if (entity.getTags().contains(WarEvents.PLACED_TAG)) return;
        ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        if (key != null && GscraftWar.MODID.equals(key.getNamespace())) return;
        event.setCanceled(true);
        refused++;
    }

    public static void setEnabled(boolean value) {
        enabled = value;
    }

    public static String status() {
        return "hold " + (enabled ? "on" : "off") + ": " + refused + " hostiles refused since boot";
    }
}
