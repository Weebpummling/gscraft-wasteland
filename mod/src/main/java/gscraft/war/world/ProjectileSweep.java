package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * Gun-mod projectiles never freeze at the edge of the simulated area. The server ticks entities only inside the
 * simulation distance around players; a rocket that flies past that ring stops dead in a chunk that is still
 * visible, then wakes when a player comes near and seems to follow them. Neither Superb Warfare nor TACZ has a
 * lifetime or range setting, so any gun-mod projectile that is about to leave the ring around every player, or is
 * older than {@link #MAX_AGE}, is retired. Mines, placed charges, vehicles and drones are not touched.
 * Replaces gscraft_projectiles.js, which never ran (fold-in review F17).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class ProjectileSweep {
    public static int DEFAULT_MAX_AGE = 20 * 30;
    private static volatile int maxAge = DEFAULT_MAX_AGE;

    public static void setDefaultMaxAge(int ticks) {
        DEFAULT_MAX_AGE = Math.max(1, ticks);
        maxAge = DEFAULT_MAX_AGE;
    }
    private static final int EDGE_MARGIN = 40;
    private static final int EVERY = 5;
    private static final Set<String> SUPERBWARFARE = Set.of(
            "projectile", "rpg_rocket_standard", "rpg_rocket_tbg", "small_rocket", "medium_rocket", "mortar_shell",
            "cannon_shell", "small_cannon_shell", "gun_grenade", "hand_grenade", "rgo_grenade", "javelin_missile",
            "igla_9k38_missile", "ru_9m336_missile", "wire_guide_missile", "agm_65", "kh_39", "tow", "mk_82",
            "blu_43", "bl_132", "grapeshot", "taser_bullet", "ptkm_projectile", "melon_bomb", "flare_decoy", "smoke_decoy");

    private static int ticks;
    private static long retired;

    private ProjectileSweep() {}

    static boolean isProjectile(Entity entity) {
        ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        if (key == null) return false;
        return switch (key.getNamespace()) {
            case "superbwarfare" -> SUPERBWARFARE.contains(key.getPath());
            case "tacz" -> !"target_minecart".equals(key.getPath());
            default -> false;
        };
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || ++ticks % EVERY != 0) return;
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;
        int simBlocks = Math.max(64, server.getPlayerList().getSimulationDistance() * 16 - EDGE_MARGIN);
        double limitSq = (double) simBlocks * simBlocks;
        for (ServerLevel level : server.getAllLevels()) {
            List<Entity> doomed = new ArrayList<>();
            for (Entity e : level.getAllEntities()) {
                if (!isProjectile(e)) continue;
                if (e.tickCount > maxAge) {
                    doomed.add(e);
                    continue;
                }
                // the ring exists only around players; a level with none keeps its projectiles to the age rule
                boolean near = level.players().isEmpty();
                for (ServerPlayer p : level.players()) {
                    if (e.distanceToSqr(p) <= limitSq) {
                        near = true;
                        break;
                    }
                }
                if (!near) doomed.add(e);
            }
            for (Entity e : doomed) e.discard();
            retired += doomed.size();
        }
    }

    /** the age past which a projectile is retired; the command sets it for a test and restores the default */
    public static void setMaxAge(int ticks) {
        maxAge = Math.max(1, ticks);
    }

    public static String status() {
        return "projectile sweep: " + retired + " retired since boot, max age " + maxAge + " ticks";
    }
}
