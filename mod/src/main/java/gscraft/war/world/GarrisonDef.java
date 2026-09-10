package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

/**
 * A standing garrison: {@code count} persistent members of {@code entity} held inside the zone, topped back up
 * {@code refillTicks} after the last refill once any have died.
 */
public record GarrisonDef(ResourceLocation entity, int count, int refillTicks) {
}
