package gscraft.war.entity;

import gscraft.war.world.Director;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * A squad leader walks its route waypoint by waypoint and loops (feasibility C2); the members follow in
 * formation. A route is a list of x/z points; the standing height is found on arrival at each column.
 */
public class PatrolGoal extends Goal {
    private static final double ARRIVE = 3.0D;
    private final PathfinderMob mob;
    private int repath;
    private BlockPos waypoint;

    public <T extends PathfinderMob & GunUser> PatrolGoal(T mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private FighterState state() {
        return ((GunUser) mob).fighterState();
    }

    @Override
    public boolean canUse() {
        FighterState s = state();
        if (s.route.isEmpty() || s.order != FighterState.Order.NONE || mob.getTarget() != null) return false;
        if (!(mob.level() instanceof ServerLevel level)) return false;
        // a route is walked for someone to meet the squad: with nobody within reach it waits where it is
        if (!Squad.someoneNear(level, mob)) return false;
        return s.squadId == null || Squad.isLeader(level, mob);
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public void start() {
        repath = 0;
        waypoint = null;
    }

    @Override
    public void tick() {
        FighterState s = state();
        if (waypoint == null) waypoint = resolve(s.route.get(s.routeIndex % s.route.size()));
        if (mob.blockPosition().distSqr(waypoint) <= ARRIVE * ARRIVE || mob.position().distanceTo(net.minecraft.world.phys.Vec3.atBottomCenterOf(waypoint)) <= ARRIVE) {
            s.routeIndex = (s.routeIndex + 1) % s.route.size();
            waypoint = resolve(s.route.get(s.routeIndex));
            repath = 0;
        }
        if (--repath > 0) return;
        repath = 20;
        mob.getNavigation().moveTo(waypoint.getX() + 0.5D, waypoint.getY(), waypoint.getZ() + 0.5D, s.routeSpeed);
    }

    private BlockPos resolve(BlockPos xz) {
        ServerLevel level = (ServerLevel) mob.level();
        int y = xz.getY() > level.getMinBuildHeight() ? xz.getY() : level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, xz.getX(), xz.getZ());
        BlockPos stand = Director.nearestStand(level, new BlockPos(xz.getX(), y, xz.getZ()));
        return stand != null ? stand : new BlockPos(xz.getX(), y, xz.getZ());
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }
}
