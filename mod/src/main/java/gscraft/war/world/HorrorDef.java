package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

/** A horror a zone admits: at most one near a player, only at night when {@code night}, at {@code chance} per pass. */
public record HorrorDef(ResourceLocation entity, boolean night, double chance) {
}
