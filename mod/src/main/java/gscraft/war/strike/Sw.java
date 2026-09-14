package gscraft.war.strike;

import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.ForgeRegistries;

import java.lang.reflect.Method;
import java.util.HashSet;
import java.util.Set;

/** Superb Warfare's projectiles by reflection (the mod is not a compile dependency, as with the vehicles): create, set a float, set a type */
final class Sw {
    private Sw() {}

    private static final Set<String> warned = new HashSet<>();

    static Entity create(Level level, String id) {
        EntityType<?> t = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("superbwarfare", id));
        Entity e = t == null ? null : t.create(level);
        if (e == null && warned.add(id)) GscraftWar.LOG.warn("[gscraft] strike: no entity superbwarfare:{}", id);
        return e;
    }

    /** calls a one-float setter such as setDamage(float) if the entity has it */
    static void set(Entity e, String method, float value) {
        try {
            Method m = e.getClass().getMethod(method, float.class);
            m.invoke(e, value);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            if (warned.add(e.getClass().getSimpleName() + "." + method)) GscraftWar.LOG.warn("[gscraft] strike: {} has no {}(float): {}", e.getClass().getSimpleName(), method, ex.toString());
        }
    }

    /** calls a one-boolean setter such as setEngineStart(boolean) if the entity has it */
    static void set(Entity e, String method, boolean value) {
        try {
            Method m = e.getClass().getMethod(method, boolean.class);
            m.invoke(e, value);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            if (warned.add(e.getClass().getSimpleName() + "." + method)) GscraftWar.LOG.warn("[gscraft] strike: {} has no {}(boolean): {}", e.getClass().getSimpleName(), method, ex.toString());
        }
    }

    /** calls setType(<enum>) with the constant of that name if the entity has such a setter */
    @SuppressWarnings({"unchecked", "rawtypes"})
    static void type(Entity e, String constant) {
        try {
            for (Method m : e.getClass().getMethods()) {
                if (!m.getName().equals("setType") || m.getParameterCount() != 1 || !m.getParameterTypes()[0].isEnum()) continue;
                m.invoke(e, Enum.valueOf((Class<Enum>) m.getParameterTypes()[0], constant));
                return;
            }
        } catch (ReflectiveOperationException | RuntimeException ex) {
            if (warned.add(e.getClass().getSimpleName() + ".setType")) GscraftWar.LOG.warn("[gscraft] strike: {} setType({}) failed: {}", e.getClass().getSimpleName(), constant, ex.toString());
        }
    }

    /** any public method by name and parameter types, for the vehicle's own weapon system (vehicleShoot(LivingEntity, String)) */
    static boolean invoke(Entity e, String method, Class<?>[] types, Object... args) {
        try {
            Method m = e.getClass().getMethod(method, types);
            m.invoke(e, args);
            return true;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            if (warned.add(e.getClass().getSimpleName() + "." + method)) GscraftWar.LOG.warn("[gscraft] strike: {}.{} failed: {}", e.getClass().getSimpleName(), method, ex.toString());
            return false;
        }
    }

    /** the bullet's fluent shooter(Entity) if it has one */
    static void shooter(Entity e, Entity shooter) {
        if (shooter == null) return;
        try {
            Method m = e.getClass().getMethod("shooter", Entity.class);
            m.invoke(e, shooter);
        } catch (ReflectiveOperationException | RuntimeException ignored) {
            // a projectile without it keeps the vanilla owner
        }
    }
}
