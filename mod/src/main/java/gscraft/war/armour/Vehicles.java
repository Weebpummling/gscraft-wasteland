package gscraft.war.armour;

import gscraft.war.GscraftWar;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;

import java.lang.reflect.Method;
import java.util.Locale;
import java.util.UUID;

/**
 * Superb Warfare's vehicles, reached by reflection the way the grenade is (armour design §2, §8): the crew touches
 * them only through public setters, synced data and one method, so a jar update breaks the crew, not the server.
 * Everything here answers null / false / NaN when the mod or a member is not there.
 */
public final class Vehicles {
    private static final String BASE = "com.atsuishio.superbwarfare.entity.vehicle.base.VehicleEntity";
    private static final Class<?> VEHICLE = find(BASE);

    private Vehicles() {}

    private static Class<?> find(String name) {
        try {
            return Class.forName(name);
        } catch (ClassNotFoundException ex) {
            return null;
        }
    }

    public static boolean available() {
        return VEHICLE != null;
    }

    public static boolean isVehicle(Entity e) {
        return VEHICLE != null && VEHICLE.isInstance(e);
    }

    public static boolean isVehicleType(net.minecraft.world.entity.EntityType<?> type) {
        return VEHICLE != null && VEHICLE.isAssignableFrom(type.getBaseClass());
    }

    private static Object call(Entity v, String name, Class<?>[] types, Object... args) {
        try {
            Method m = v.getClass().getMethod(name, types);
            return m.invoke(v, args);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] vehicle {} has no {}: {}", v.getType().getDescriptionId(), name, ex.toString());
            return null;
        }
    }

    /** a synced field by the name of its static accessor on the vehicle's class or a parent */
    @SuppressWarnings("unchecked")
    private static <T> EntityDataAccessor<T> accessor(Entity v, String field) {
        for (Class<?> c = v.getClass(); c != null; c = c.getSuperclass()) {
            try {
                return (EntityDataAccessor<T>) c.getField(field).get(null);
            } catch (NoSuchFieldException ignored) {
                // a parent may have it
            } catch (IllegalAccessException | RuntimeException ex) {
                return null;
            }
        }
        return null;
    }

    public static <T> T data(Entity v, String field, T fallback) {
        EntityDataAccessor<T> a = accessor(v, field);
        if (a == null) return fallback;
        try {
            return v.getEntityData().get(a);
        } catch (RuntimeException ex) {
            return fallback;
        }
    }

    public static <T> boolean setData(Entity v, String field, T value) {
        EntityDataAccessor<T> a = accessor(v, field);
        if (a == null) return false;
        try {
            v.getEntityData().set(a, value);
            return true;
        } catch (RuntimeException ex) {
            return false;
        }
    }

    // ---- the controls: forward back left right up down fire decoy sprint

    public static boolean input(Entity v, String which, boolean on) {
        String name = "set" + which.substring(0, 1).toUpperCase(Locale.ROOT) + which.substring(1).toLowerCase(Locale.ROOT) + "InputDown";
        return call(v, name, new Class<?>[] {boolean.class}, on) != null || hasMethod(v, name, boolean.class);
    }

    public static boolean inputState(Entity v, String which) {
        Object r = call(v, which.toLowerCase(Locale.ROOT) + "InputDown", new Class<?>[0]);
        return r instanceof Boolean b && b;
    }

    private static boolean hasMethod(Entity v, String name, Class<?>... types) {
        try {
            v.getClass().getMethod(name, types);
            return true;
        } catch (NoSuchMethodException ex) {
            return false;
        }
    }

    public static void allStop(Entity v) {
        for (String w : new String[] {"forward", "back", "left", "right", "up", "down", "fire", "sprint"}) input(v, w, false);
    }

    // ---- what it is

    public static float health(Entity v) {
        Object r = call(v, "getHealth", new Class<?>[0]);
        return r instanceof Float f ? f : Float.NaN;
    }

    public static float maxHealth(Entity v) {
        Object r = call(v, "getMaxHealth", new Class<?>[0]);
        return r instanceof Float f ? f : Float.NaN;
    }

    public static boolean wreck(Entity v) {
        return data(v, "IS_WRECK", false);
    }

    public static int energy(Entity v) {
        Object r = call(v, "getEnergy", new Class<?>[0]);
        return r instanceof Integer i ? i : -1;
    }

    public static int maxEnergy(Entity v) {
        Object r = call(v, "getMaxEnergy", new Class<?>[0]);
        return r instanceof Integer i ? i : -1;
    }

    public static void refuel(Entity v) {
        int max = maxEnergy(v);
        if (max > 0) call(v, "setEnergy", new Class<?>[] {int.class}, max);
    }

    /** every part at its maximum and no damaged flag: what a vehicle fresh from the factory has (a /summon with no NBT does not) */
    public static void whole(Entity v) {
        for (String[] pair : new String[][] {{"setTurretHealth", "getTurretMaxHealth"}, {"setMainEngineHealth", "getEngineMaxHealth"},
                {"setLeftWheelHealth", "getWheelMaxHealth"}, {"setRightWheelHealth", "getWheelMaxHealth"}}) {
            if (!hasMethod(v, pair[0], float.class) || !hasMethod(v, pair[1])) continue;
            Object max = call(v, pair[1], new Class<?>[0]);
            if (max instanceof Float f) call(v, pair[0], new Class<?>[] {float.class}, f);
        }
        for (String flag : new String[] {"setTurretDamaged", "setMainEngineDamaged", "setLeftWheelDamaged", "setRightWheelDamaged"}) {
            if (hasMethod(v, flag, boolean.class)) call(v, flag, new Class<?>[] {boolean.class}, false);
        }
        float max = maxHealth(v);
        if (!Float.isNaN(max) && hasMethod(v, "setHealth", float.class)) call(v, "setHealth", new Class<?>[] {float.class}, max);
    }

    public static float turretYaw(Entity v) {
        Object r = call(v, "getTurretYRot", new Class<?>[0]);
        return r instanceof Float f ? f : Float.NaN;
    }

    /** the AI turret: the target it lays on by itself; null clears it (the mod's own empty value is the word undefined) */
    public static boolean setTurretTarget(Entity v, UUID target) {
        return setData(v, "AI_TURRET_TARGET_UUID", target == null ? "undefined" : target.toString());
    }

    // ---- seats and weapons

    public static int seatIndex(Entity v, Entity passenger) {
        Object r = call(v, "getSeatIndex", new Class<?>[] {Entity.class}, passenger);
        return r instanceof Integer i ? i : -1;
    }

    public static boolean hasPassengerWeaponStation(Entity v) {
        Object r = call(v, "hasPassengerWeaponStation", new Class<?>[0]);
        return r instanceof Boolean b && b;
    }

    public static int passengerWeaponSeat(Entity v) {
        Object r = call(v, "getPassengerWeaponStationControllerIndex", new Class<?>[0]);
        return r instanceof Integer i ? i : -1;
    }

    public static int turretSeat(Entity v) {
        Object r = call(v, "getTurretControllerIndex", new Class<?>[0]);
        return r instanceof Integer i ? i : 0;
    }

    /** the names of a seat's weapons, from the vehicle's data (Cannon, MachineGun, Missile ...); null when unreadable */
    @SuppressWarnings("unchecked")
    public static java.util.List<String> seatWeapons(Entity v, int seat) {
        try {
            Object data = v.getClass().getMethod("computed").invoke(v);
            java.util.List<Object> seats = (java.util.List<Object>) data.getClass().getMethod("seats").invoke(data);
            if (seat < 0 || seat >= seats.size()) return null;
            Object info = seats.get(seat);
            Object weapons = info.getClass().getMethod("weapons").invoke(info);
            return weapons instanceof java.util.List<?> l ? (java.util.List<String>) l : null;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return null;
        }
    }

    public static int selectedWeapon(Entity v, int seat) {
        Object r = call(v, "getSelectedWeapon", new Class<?>[] {int.class}, seat);
        return r instanceof Integer i ? i : -1;
    }

    public static void changeWeapon(Entity v, int seat, int index) {
        call(v, "changeWeapon", new Class<?>[] {int.class, int.class, boolean.class}, seat, index, true);
    }

    // ---- the inventory (ammunition)

    public static int containerSize(Entity v) {
        Object r = call(v, "getContainerSize", new Class<?>[0]);
        return r instanceof Integer i ? i : 0;
    }

    public static boolean setItem(Entity v, int slot, net.minecraft.world.item.ItemStack stack) {
        return hasMethod(v, "setItem", int.class, net.minecraft.world.item.ItemStack.class) && call(v, "setItem", new Class<?>[] {int.class, net.minecraft.world.item.ItemStack.class}, slot, stack) == null && true;
    }

    public static net.minecraft.world.item.ItemStack getItem(Entity v, int slot) {
        Object r = call(v, "getItem", new Class<?>[] {int.class}, slot);
        return r instanceof net.minecraft.world.item.ItemStack st ? st : net.minecraft.world.item.ItemStack.EMPTY;
    }

    public static String vehicleType(Entity v) {
        Object r = call(v, "getVehicleType", new Class<?>[0]);
        return r == null ? "?" : r.toString();
    }

    public static String turretTarget(Entity v) {
        return data(v, "AI_TURRET_TARGET_UUID", "");
    }

    public static boolean setPassengerWeaponTarget(Entity v, UUID target) {
        return setData(v, "AI_PASSENGER_WEAPON_TARGET_UUID", target == null ? "undefined" : target.toString());
    }

    /** what the mod's modifier list would make of this source and amount, without applying it */
    public static float compute(Entity v, DamageSource source, float amount) {
        try {
            Object modifier = v.getClass().getMethod("getDamageModifier").invoke(v);
            Method compute = modifier.getClass().getMethod("compute", DamageSource.class, float.class);
            Object r = compute.invoke(modifier, source, amount);
            return r instanceof Float f ? f : Float.NaN;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return Float.NaN;
        }
    }

    /** the parts' health as synced, in order: turret, engine, left wheel, right wheel (NaN where the vehicle has none) */
    public static float[] parts(Entity v) {
        return new float[] {data(v, "TURRET_HEALTH", Float.NaN), data(v, "MAIN_ENGINE_HEALTH", Float.NaN), data(v, "L_WHEEL_HEALTH", Float.NaN), data(v, "R_WHEEL_HEALTH", Float.NaN)};
    }

    public static String describe(Entity v) {
        float[] p = parts(v);
        return String.format(Locale.ROOT, "%s (tracked %d chunks): health %.1f/%.1f, wreck %s, energy %d/%d, turret %.0f (damaged %s), engine %.0f, wheels %.0f/%.0f, turret target '%s', turret yaw %.1f, body yaw %.1f, at %.1f %.1f %.1f, inputs f%s b%s l%s r%s sprint%s fire%s",
                v.getName().getString(), v.getType().clientTrackingRange(), health(v), maxHealth(v), wreck(v), energy(v), maxEnergy(v), p[0], data(v, "TURRET_DAMAGED", false), p[1], p[2], p[3],
                turretTarget(v), turretYaw(v), v.getYRot(), v.getX(), v.getY(), v.getZ(),
                flag(inputState(v, "forward")), flag(inputState(v, "back")), flag(inputState(v, "left")), flag(inputState(v, "right")), flag(inputState(v, "sprint")), flag(inputState(v, "fire")));
    }

    private static String flag(boolean b) {
        return b ? "+" : "-";
    }
}
