package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

import java.util.Set;

/**
 * A horror a zone admits: at most one near a player, only at night when {@code night}, at {@code chance} per pass,
 * and only on the kinds of ground listed in {@code envs} (empty: any) - the Knocker belongs in cellars.
 */
public record HorrorDef(ResourceLocation entity, boolean night, double chance, Set<Env> envs) {
}
