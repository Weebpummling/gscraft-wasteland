package gscraft.war.faction;

import net.minecraft.resources.ResourceLocation;

import java.util.Set;

/**
 * One faction, read from {@code data/<ns>/gscraft_factions/<id>.json}.
 *
 * @param members          entity types that belong to it, for mobs that are not the mod's own
 * @param hostile          faction ids it attacks on sight
 * @param players          how it treats players
 * @param injectTargeting  add a faction target goal to member mobs from other mods and vanilla on join
 */
public record FactionDef(String id, Set<ResourceLocation> members, Set<String> hostile, PlayerStance players,
                         boolean injectTargeting) {
}
