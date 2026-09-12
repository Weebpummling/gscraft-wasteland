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
        arm(v);
        crew(level, v, faction, route);
        GscraftWar.LOG.info("[gscraft] armour placed: {} ({}) at {} with {} waypoints", v.getName().getString(), faction, BlockPos.containing(at).toShortString(), route == null ? 0 : route.size());
        return v;
    }

    /** a crew for a vehicle already in the world - the driver in seat 0 and, where the vehicle has a commander's
     *  station, a gunner in its seat; an old crew is replaced. Returns the driver. */
    public static Crew crew(ServerLevel level, Entity vehicle, String faction, List<BlockPos> route) {
        for (Entity p : new java.util.ArrayList<>(vehicle.getPassengers())) if (p instanceof Crew c) c.discard();
        Crew driver = mount(level, vehicle, faction, false);
        if (driver == null) return null;
        if (route != null) driver.route.addAll(route);
        if (Vehicles.hasPassengerWeaponStation(vehicle)) {
            Crew gunner = mount(level, vehicle, faction, true);
            if (gunner == null) GscraftWar.LOG.warn("[gscraft] no gunner could mount {}", vehicle.getName().getString());
        }
        return driver;
    }

    private static Crew mount(ServerLevel level, Entity vehicle, String faction, boolean gunner) {
        Crew crew = ModEntities.CREW.get().create(level);
        if (crew == null) return null;
        crew.setFaction(faction);
        crew.setGunner(gunner);
        crew.moveTo(vehicle.getX(), vehicle.getY() + 1.0D, vehicle.getZ(), vehicle.getYRot(), 0.0F);
        level.addFreshEntity(crew);
        if (!crew.startRiding(vehicle, true)) {
            GscraftWar.LOG.warn("[gscraft] the {} could not mount {}", gunner ? "gunner" : "crew", vehicle.getName().getString());
            crew.discard();
            return null;
        }
        return crew;
    }

    /** the ammunition each of the four carries (the weapon files' AmmoType): shells HE first so the gun fires HE at
     *  infantry, AP behind, missiles for the IFVs, rifle and heavy rounds for the machine guns. Fills from slot 0. */
    public static int arm(Entity v) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(v.getType());
        String name = id == null ? "" : id.getPath();
        String[][] load;
        if (name.equals("t_90a") || name.equals("m_1a_2")) {
            load = new String[][] {{"superbwarfare:large_shell_he", "32"}, {"superbwarfare:large_shell_he", "32"}, {"superbwarfare:large_shell_ap", "16"},
                    {"superbwarfare:rifle_ammo", "64"}, {"superbwarfare:rifle_ammo", "64"}, {"superbwarfare:heavy_ammo", "64"}, {"superbwarfare:heavy_ammo", "64"}};
        } else if (name.equals("bmp_2") || name.equals("bradley")) {
            load = new String[][] {{"superbwarfare:small_shell_he", "64"}, {"superbwarfare:small_shell_he", "64"}, {"superbwarfare:small_shell_ap", "64"},
                    {"superbwarfare:medium_anti_ground_missile", "8"}, {"superbwarfare:rifle_ammo", "64"}, {"superbwarfare:rifle_ammo", "64"}};
        } else {
            return 0;
        }
        int slots = Vehicles.containerSize(v);
        int placed = 0;
        for (int i = 0; i < load.length && i < slots; i++) {
            net.minecraft.world.item.Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(load[i][0]));
            if (item == null || item == net.minecraft.world.item.Items.AIR) {
                GscraftWar.LOG.warn("[gscraft] no such ammunition item {}", load[i][0]);
                continue;
            }
            int count = Math.min(Integer.parseInt(load[i][1]), item.getMaxStackSize());
            if (Vehicles.setItem(v, i, new net.minecraft.world.item.ItemStack(item, count))) placed++;
        }
        return placed;
    }

    /** a vehicle in a site's wave (design §3, V6): on a road stand beside the wave point where there is one, else any
     *  stand with a hull's room; driving for the target, or holding where it is as a boss (named, its stage set on
     *  its death); tagged like the wave, so the sweep leaves it and the wave's end takes it. */
    public static boolean wave(ServerLevel level, String siteId, String faction, ResourceLocation vehicleType, BlockPos point, BlockPos target, String boss, String name) {
        // a wave point carries no height (the site's edges are x/z): the heightmap gives it; a given height is trusted
        int y = point.getY() > level.getMinBuildHeight() + 1 ? point.getY() : level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, point.getX(), point.getZ());
        BlockPos stand = Patrols.roadStandAround(level, point.getX(), y, point.getZ());
        for (int t = 0; t < 8 && stand == null; t++) {
            int x = point.getX() + level.getRandom().nextInt(13) - 6;
            int z = point.getZ() + level.getRandom().nextInt(13) - 6;
            BlockPos p = gscraft.war.world.Director.legacyStand(level, x, point.getY() > level.getMinBuildHeight() + 1 ? point.getY() : level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
            if (p != null && Patrols.hullRoom(level, p)) stand = p;
        }
        if (stand == null) {
            GscraftWar.LOG.warn("[gscraft] {} wave: no stand with a hull's room near {}", siteId, point.toShortString());
            return false;
        }
        boolean isBoss = boss != null && !boss.isEmpty();
        List<BlockPos> route = isBoss || target == null ? List.of() : List.of(target);
        float yaw = target == null ? 0.0F : (float) Math.toDegrees(Math.atan2(-(target.getX() - stand.getX()), target.getZ() - stand.getZ()));
        Entity v = spawn(level, vehicleType, Vec3.atBottomCenterOf(stand), yaw, faction == null || faction.isEmpty() ? Patrols.factionOf(vehicleType) : faction, route);
        if (v == null) return false;
        String tag = gscraft.war.world.Loop.WAVE_TAG + "_" + siteId;
        v.addTag(gscraft.war.world.Loop.WAVE_TAG);
        v.addTag(tag);
        v.addTag(gscraft.war.WarEvents.PLACED_TAG);
        for (Entity p : v.getPassengers()) {
            if (!(p instanceof Crew c)) continue;
            c.addTag(gscraft.war.world.Loop.WAVE_TAG);
            c.addTag(tag);
            c.addTag(gscraft.war.WarEvents.PLACED_TAG);
            if (isBoss && !c.gunner()) c.bossStage = siteId + "_" + boss;
        }
        if (isBoss) {
            v.setCustomName(net.minecraft.network.chat.Component.literal(name == null || name.isEmpty() ? v.getName().getString() : name));
            v.setCustomNameVisible(true);
        }
        GscraftWar.LOG.info("[gscraft] {} wave armour: {} at {}{}", siteId, v.getName().getString(), stand.toShortString(), isBoss ? " (boss " + boss + ")" : target == null ? "" : ", for " + target.toShortString());
        return true;
    }

    /** a target one of the vehicle's crews already engages */
    public static boolean engagedBy(Entity vehicle, Entity target) {
        for (Entity p : vehicle.getPassengers()) if (p instanceof Crew c && c.engaged == target) return true;
        return false;
    }

    /** the driver */
    public static Crew crewOf(Entity vehicle) {
        for (Entity p : vehicle.getPassengers()) if (p instanceof Crew c && !c.gunner()) return c;
        return null;
    }
}
