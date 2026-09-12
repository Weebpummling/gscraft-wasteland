package gscraft.war.armour;

import gscraft.war.GscraftWar;
import gscraft.war.WarEvents;
import gscraft.war.entity.Squad;
import gscraft.war.world.ArmourDef;
import gscraft.war.world.Director;
import gscraft.war.world.Env;
import gscraft.war.world.Loop;
import gscraft.war.world.Zone;
import gscraft.war.world.Zones;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;

/**
 * The rare armour patrol (armour design §3, V5): on a director pass, a player in open ground in a zone with an
 * armour entry rolls its chance; a road stand is found in a ring around the player - a column of road with room
 * for a hull, not inside the placement minimum of anyone - and never within the spacing of another armour group.
 * The vehicle goes down whole, fuelled, armed and crewed, its route the zone's patrol if it has one and else the
 * road it stands on both ways; its infantry is a squad placed beside it that its driver orders along behind it
 * (the escort). A vehicle counts as four against the ceilings; the sweep takes it back like anything else.
 */
public final class Patrols {
    public static double PLACE_MIN = 96.0D;
    public static double PLACE_MAX = 140.0D;
    public static double SPACING = 400.0D;
    public static int WEIGHT = 4;
    public static double ROAD_REACH = 60.0D;
    private static final int TRIES = 24;

    private Patrols() {}

    /** the director's roll for one player; the vehicle placed, or null */
    public static Entity roll(ServerLevel level, BlockPos player) {
        if (!Vehicles.available()) return null;
        Zone zone = Zones.at(player.getX(), player.getZ());
        if (zone == null || zone.exclude() || zone.armour() == null) return null;
        if (Env.at(level, player) != Env.OPEN) return null;
        RandomSource random = level.getRandom();
        if (random.nextFloat() >= zone.armour().chance()) return null;
        ArmourDef.Composition composition = zone.armour().pick(random);
        if (composition == null || composition.vehicles().isEmpty()) return null;
        if (armourNear(level, player, SPACING)) return null;
        int cost = WEIGHT * composition.vehicles().size() + composition.infantry();
        if (Director.countDirector(level) + cost > Director.SERVER_CEILING) return null;
        if (Director.countAround(level, player) + cost > Director.PLAYER_CEILING) return null;
        return place(level, player, composition, PLACE_MIN, PLACE_MAX);
    }

    /** a group on a road stand in the ring around a point (the forced command uses a ring of its own) */
    public static Entity place(ServerLevel level, BlockPos around, ArmourDef.Composition composition, double minR, double maxR) {
        RandomSource random = level.getRandom();
        Entity first = null;
        for (int i = 0; i < composition.vehicles().size(); i++) {
            ResourceLocation id = composition.vehicles().get(i);
            BlockPos stand = first == null ? roadStand(level, around, minR, maxR, random) : roadStandNear(level, first.blockPosition(), random);
            if (stand == null) {
                if (first == null) return null;
                break;
            }
            Zone here = Zones.at(stand.getX(), stand.getZ());
            List<BlockPos> route = here != null && !here.patrols().isEmpty() ? new ArrayList<>(here.patrols().get(0)) : roadRoute(level, stand);
            float yaw = route.isEmpty() ? random.nextFloat() * 360.0F : bearing(stand, route.get(0));
            Entity v = Armour.spawn(level, id, Vec3.atBottomCenterOf(stand), yaw, factionOf(id), route);
            if (v == null) continue;
            v.addTag("gs_armour");
            for (Entity p : v.getPassengers()) {
                if (p instanceof Crew c) {
                    c.addTag("gs_director");
                    c.addTag(WarEvents.PLACED_TAG);
                }
            }
            if (first == null) first = v;
        }
        if (first == null) return null;
        infantry(level, first, composition.infantry());
        return first;
    }

    /** a group at a point, road or not (the command): the lead vehicle stands on the point itself - the road stand
     *  there if the point is on a road, else the nearest open ground with a hull's room - and patrols the road under
     *  it or, off the roads, holds where it is; the others within a dozen blocks; the infantry beside the lead. */
    public static Entity placeAt(ServerLevel level, BlockPos at, ArmourDef.Composition composition, float yaw) {
        RandomSource random = level.getRandom();
        Entity first = null;
        for (int i = 0; i < composition.vehicles().size(); i++) {
            ResourceLocation id = composition.vehicles().get(i);
            BlockPos want = first == null ? at : at.offset(random.nextInt(25) - 12, 0, random.nextInt(25) - 12);
            BlockPos stand = roadStandAround(level, want.getX(), want.getY(), want.getZ());
            if (stand == null) stand = openStand(level, want);
            if (stand == null) {
                if (first == null) return null;
                break;
            }
            List<BlockPos> route = roadUnder(level, stand) ? roadRoute(level, stand) : new ArrayList<>();
            Entity v = Armour.spawn(level, id, Vec3.atBottomCenterOf(stand), route.isEmpty() ? yaw : bearing(stand, route.get(0)), factionOf(id), route);
            if (v == null) continue;
            v.addTag("gs_armour");
            for (Entity p : v.getPassengers()) {
                if (p instanceof Crew c) {
                    c.addTag("gs_director");
                    c.addTag(WarEvents.PLACED_TAG);
                }
            }
            if (first == null) first = v;
        }
        if (first == null) return null;
        infantry(level, first, composition.infantry());
        return first;
    }

    /** open ground within a few blocks of a column, up or down six: something solid under, a hull's room over */
    private static BlockPos openStand(ServerLevel level, BlockPos at) {
        for (int r = 0; r <= 4; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
                    for (int d = 0; d <= 6; d++) {
                        for (int sign = -1; sign <= 1; sign += 2) {
                            if (d == 0 && sign == 1) continue;
                            BlockPos stand = at.offset(dx, d * sign, dz);
                            if (!level.hasChunkAt(stand)) return null;
                            BlockPos below = stand.below();
                            if (level.getBlockState(below).getCollisionShape(level, below).isEmpty()) continue;
                            if (hullRoom(level, stand)) return stand;
                        }
                    }
                }
            }
        }
        return null;
    }

    /** the infantry: a squad beside the lead vehicle, ordered along behind it by the driver */
    private static void infantry(ServerLevel level, Entity vehicle, int count) {
        if (count <= 0) return;
        String faction = factionOf(ForgeRegistries.ENTITY_TYPES.getKey(vehicle.getType()));
        ResourceLocation soldier = new ResourceLocation(GscraftWar.MODID, faction + "_soldier");
        List<Mob> group = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            Mob m = Director.placeBeside(level, vehicle.blockPosition(), Env.OPEN, soldier, false);
            if (m == null) break;
            group.add(m);
        }
        if (group.isEmpty()) return;
        Squad.form(group);
        Crew driver = Armour.crewOf(vehicle);
        // the riders board on the crew's boarding tick, once the vehicle's seats are set up (a mount in the vehicle's first tick displaces the crew)
        if (driver != null) for (Mob m : group) driver.escorts.add(m.getUUID());
        GscraftWar.LOG.info("[gscraft] armour patrol: {} with {} infantry at {}", vehicle.getName().getString(), group.size(), vehicle.blockPosition().toShortString());
    }

    // ---- roads

    /** a road block: the road mod's surfaces, by name */
    public static boolean isRoad(BlockState state) {
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        if (key == null || !key.getNamespace().equals("furenikusroads")) return false;
        String p = key.getPath();
        return p.contains("road") || p.contains("street");
    }

    private static boolean roadUnder(ServerLevel level, BlockPos stand) {
        return isRoad(level.getBlockState(stand.below()));
    }

    /** a hull's worth of room: a 5 x 4 x 5 box of air over the stand, road under the middle */
    public static boolean hullRoom(ServerLevel level, BlockPos stand) {
        for (int dx = -2; dx <= 2; dx++) {
            for (int dz = -2; dz <= 2; dz++) {
                for (int dy = 0; dy < 4; dy++) {
                    if (!level.getBlockState(stand.offset(dx, dy, dz)).getCollisionShape(level, stand.offset(dx, dy, dz)).isEmpty()) return false;
                }
            }
        }
        return true;
    }

    private static BlockPos roadStand(ServerLevel level, BlockPos around, double minR, double maxR, RandomSource random) {
        for (int t = 0; t < TRIES; t++) {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double dist = minR + random.nextDouble() * Math.max(0.0D, maxR - minR);
            int x = Mth.floor(around.getX() + Math.cos(angle) * dist);
            int z = Mth.floor(around.getZ() + Math.sin(angle) * dist);
            BlockPos stand = roadStandAround(level, x, around.getY(), z);
            if (stand != null && !Director.anyoneWithin(level, stand.getX(), stand.getZ(), PLACE_MIN)) return stand;
        }
        return null;
    }

    private static BlockPos roadStandNear(ServerLevel level, BlockPos beside, RandomSource random) {
        for (int t = 0; t < TRIES; t++) {
            int x = beside.getX() + random.nextInt(25) - 12;
            int z = beside.getZ() + random.nextInt(25) - 12;
            if (Math.abs(x - beside.getX()) < 7 && Math.abs(z - beside.getZ()) < 7) continue;
            BlockPos stand = roadStandAround(level, x, beside.getY(), z);
            if (stand != null) return stand;
        }
        return null;
    }

    /** a road stand within a few blocks of a point, nearest first: a random point seldom lands on a road itself */
    public static BlockPos roadStandAround(ServerLevel level, int x, int y0, int z) {
        for (int r = 0; r <= 5; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
                    BlockPos stand = roadStandAt(level, x + dx, y0, z + dz);
                    if (stand != null) return stand;
                }
            }
        }
        return null;
    }

    /** the road stand at a column, or null: standing room on open ground, road under it, room for a hull, not suppressed */
    public static BlockPos roadStandAt(ServerLevel level, int x, int y0, int z) {
        Zone here = Zones.at(x, z);
        if (here == null || here.exclude() || Loop.suppressedAt(level, x, z)) return null;
        // the road mod's surfaces are not full cubes, so the general standing test refuses them: road under, air over
        for (int d = 0; d <= 6; d++) {
            for (int sign = -1; sign <= 1; sign += 2) {
                if (d == 0 && sign == 1) continue;
                BlockPos stand = new BlockPos(x, y0 + d * sign, z);
                if (!level.hasChunkAt(stand)) return null;
                boolean road = roadUnder(level, stand);
                boolean room = road && hullRoom(level, stand);
                Env env = room ? Env.at(level, stand) : null;
                if (gscraft.war.combat.Damage.DEBUG > 0 && road) GscraftWar.LOG.info("[gscraft] road stand {}: road {}, room {}, env {}, below {}", stand.toShortString(), road, room, env, ForgeRegistries.BLOCKS.getKey(level.getBlockState(stand.below()).getBlock()));
                if (!room || env != Env.OPEN) continue;
                return stand;
            }
        }
        return null;
    }

    /** the road both ways from the stand: the longer axis, its two ends as the route; empty when the road is a stub */
    public static List<BlockPos> roadRoute(ServerLevel level, BlockPos stand) {
        int bestLen = 0;
        List<BlockPos> best = new ArrayList<>();
        for (int axis = 0; axis < 2; axis++) {
            BlockPos a = follow(level, stand, axis == 0 ? 1 : 0, axis == 0 ? 0 : 1);
            BlockPos b = follow(level, stand, axis == 0 ? -1 : 0, axis == 0 ? 0 : -1);
            int len = a.distManhattan(b);
            if (len > bestLen) {
                bestLen = len;
                best = new ArrayList<>(List.of(a, b));
            }
        }
        return bestLen >= 24 ? best : new ArrayList<>();
    }

    private static BlockPos follow(ServerLevel level, BlockPos from, int dx, int dz) {
        BlockPos last = from;
        for (int step = 4; step <= ROAD_REACH; step += 4) {
            BlockPos p = from.offset(dx * step, 0, dz * step);
            BlockPos stand = null;
            for (int dy = 2; dy >= -2 && stand == null; dy--) {
                BlockPos q = p.above(dy);
                if (level.hasChunkAt(q) && roadUnder(level, q) && level.getBlockState(q).getCollisionShape(level, q).isEmpty()) stand = q;
            }
            if (stand == null) break;
            last = stand;
            from = new BlockPos(from.getX(), stand.getY(), from.getZ());
        }
        return last;
    }

    private static float bearing(BlockPos from, BlockPos to) {
        return (float) Math.toDegrees(Math.atan2(-(to.getX() - from.getX()), to.getZ() - from.getZ()));
    }

    // ---- the rest

    public static boolean armourNear(ServerLevel level, BlockPos at, double blocks) {
        return !level.getEntitiesOfClass(Crew.class, new net.minecraft.world.phys.AABB(at).inflate(blocks, 64.0D, blocks), c -> !c.gunner() && c.vehicle() != null).isEmpty();
    }

    /** the faction a vehicle fights for, from its make: the Russian pair for RUAF, the American for NATO */
    public static String factionOf(ResourceLocation vehicle) {
        if (vehicle == null) return "ruaf";
        String p = vehicle.getPath();
        return p.equals("bmp_2") || p.equals("t_90a") ? "ruaf" : "nato";
    }

    /** what a director creature weighs against the ceilings: a vehicle's driver stands for the vehicle */
    public static int weight(Mob mob) {
        if (mob instanceof Crew c) return c.gunner() ? 0 : WEIGHT;
        return 1;
    }
}
