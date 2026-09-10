package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

/**
 * One creature a zone may place, weighted against the zone's other entries.
 *
 * @param night only placed at night (the Riders)
 */
public record SpawnEntry(ResourceLocation entity, int weight, boolean night) {
}
