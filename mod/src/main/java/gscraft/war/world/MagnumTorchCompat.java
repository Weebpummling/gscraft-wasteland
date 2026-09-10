package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraftforge.fml.ModList;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.reflect.Method;

/**
 * The Magnum Torches refuse a spawn when the entity joins the world (Puzzles Lib's entity-load hook, keyed to the
 * spawn type), not through Forge's spawn events, so posting a PositionCheck never reaches them. The director asks
 * their handler directly, as a NATURAL spawn - the type the diamond torch blocks for monsters. The handler answers
 * INTERRUPT when a torch is in range. Reflection keeps the mod optional.
 */
final class MagnumTorchCompat {
    private static final MethodHandle HANDLER = find();
    private static boolean warned;

    private MagnumTorchCompat() {}

    private static MethodHandle find() {
        if (!ModList.get().isLoaded("magnumtorch")) return null;
        try {
            Class<?> handler = Class.forName("fuzs.magnumtorch.handler.MobSpawningHandler");
            Method method = handler.getMethod("onLivingSpawn", Entity.class, ServerLevel.class, MobSpawnType.class);
            return MethodHandles.lookup().unreflect(method);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] Magnum Torch is loaded but its spawn handler was not found ({}); "
                    + "torches will not stop the director", ex.toString());
            return null;
        }
    }

    static boolean refuses(Mob mob, ServerLevel level) {
        if (HANDLER == null) return false;
        try {
            Object result = HANDLER.invoke((Entity) mob, level, MobSpawnType.NATURAL);
            return result != null && "INTERRUPT".equals(result.toString());
        } catch (Throwable t) {
            if (!warned) {
                warned = true;
                GscraftWar.LOG.warn("[gscraft] Magnum Torch spawn check failed ({}); placing without it", t.toString());
            }
            return false;
        }
    }
}
