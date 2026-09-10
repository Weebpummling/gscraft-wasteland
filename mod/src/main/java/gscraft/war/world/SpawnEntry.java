package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

/** One entity a zone may place, weighted against the zone's other entries. */
public record SpawnEntry(ResourceLocation entity, int weight) {
}
