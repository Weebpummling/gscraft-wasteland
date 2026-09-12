package gscraft.war.armour;

import gscraft.war.GscraftWar;
import gscraft.war.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/** Placing armour: a Superb Warfare vehicle, fuelled and whole, with a crew of ours in the driver's seat. */
public final class Armour {
    private Armour() {}

    /** the vehicle, or null when the type is unknown or not a vehicle */
    public static Entity spawn(ServerLevel level, ResourceLocation vehicleType, Vec3 at, float yaw, String faction, List<BlockPos> route) {
        EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(vehicleType);
        if (type == null) {
            GscraftWar.LOG.warn("[gscraft] no entity type {}", vehicleType);
            return null;
        }
        Entity v = type.create(level);
        if (v == null || !Vehicles.isVehicle(v)) {
            GscraftWar.LOG.warn("[gscraft] {} is not a Superb Warfare vehicle", vehicleType);
            return null;
        }
        v.moveTo(at.x, at.y, at.z, yaw, 0.0F);
        v.setYRot(yaw);
        Vehicles.whole(v);
        Vehicles.refuel(v);
        level.addFreshEntity(v);
        crew(level, v, faction, route);
        GscraftWar.LOG.info("[gscraft] armour placed: {} ({}) at {} with {} waypoints", v.getName().getString(), faction, BlockPos.containing(at).toShortString(), route == null ? 0 : route.size());
        return v;
    }

    /** a crew for a vehicle already in the world; the old crew, if any, is replaced */
    public static Crew crew(ServerLevel level, Entity vehicle, String faction, List<BlockPos> route) {
        Crew old = crewOf(vehicle);
        if (old != null) old.discard();
        Crew crew = ModEntities.CREW.get().create(level);
        if (crew == null) return null;
        crew.setFaction(faction);
        if (route != null) crew.route.addAll(route);
        crew.moveTo(vehicle.getX(), vehicle.getY() + 1.0D, vehicle.getZ(), vehicle.getYRot(), 0.0F);
        level.addFreshEntity(crew);
        if (!crew.startRiding(vehicle, true)) {
            GscraftWar.LOG.warn("[gscraft] the crew could not mount {}", vehicle.getName().getString());
            crew.discard();
            return null;
        }
        return crew;
    }

    public static Crew crewOf(Entity vehicle) {
        for (Entity p : vehicle.getPassengers()) if (p instanceof Crew c) return c;
        return null;
    }
}
