package gscraft.war.armour;

import gscraft.war.GscraftWar;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The crew drives its vehicle round its route (armour design §2): the heading error to the next waypoint becomes
 * the steer inputs (the left input turns the hull left, about two degrees a tick, driving or standing - V1), forward
 * while the waypoint is ahead, a sprint when it is far and the hull is lined up. A hull that has not moved in two
 * seconds while driving reverses with the opposite steer for a moment; a waypoint that still is not reached after
 * three of those is skipped. Nothing here pathfinds: the routes are roads, and V5 lays them on roads.
 */
public class DriveGoal extends Goal {
    public static double ARRIVE = 5.0D;
    public static float STEER_DEAD = 6.0F;
    public static float SPRINT_WITHIN = 20.0F;
    public static double SPRINT_BEYOND = 16.0D;
    public static int STUCK_CHECK = 40;
    public static double STUCK_MOVE = 1.0D;
    public static int REVERSE_TICKS = 30;
    public static int STUCK_SKIP = 3;

    private final Crew crew;
    private Vec3 lastPos;
    private int sinceCheck;
    private int reversing;
    private boolean reverseLeft;
    private int stuckOnThis;

    public DriveGoal(Crew crew) {
        this.crew = crew;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return crew.vehicle() != null && !crew.route.isEmpty();
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        lastPos = null;
        sinceCheck = 0;
        reversing = 0;
        stuckOnThis = 0;
    }

    @Override
    public void stop() {
        Entity v = crew.vehicle();
        if (v != null) Vehicles.allStop(v);
    }

    @Override
    public void tick() {
        Entity v = crew.vehicle();
        if (v == null) return;
        if (crew.routeIndex >= crew.route.size()) crew.routeIndex = 0;
        BlockPos wp = crew.route.get(crew.routeIndex);
        double dx = wp.getX() + 0.5D - v.getX();
        double dz = wp.getZ() + 0.5D - v.getZ();
        double dist = Math.sqrt(dx * dx + dz * dz);
        if (dist < ARRIVE) {
            GscraftWar.LOG.info("[gscraft] crew of {} reached waypoint {} of {} at {}", v.getName().getString(), crew.routeIndex + 1, crew.route.size(), wp.toShortString());
            crew.routeIndex = (crew.routeIndex + 1) % crew.route.size();
            stuckOnThis = 0;
            return;
        }
        if (reversing > 0) {
            reversing--;
            set(v, false, true, reverseLeft, !reverseLeft, false);
            return;
        }
        float bearing = (float) Math.toDegrees(Math.atan2(-dx, dz));
        float err = Mth.wrapDegrees(bearing - v.getYRot());
        boolean left = err < -STEER_DEAD;
        boolean right = err > STEER_DEAD;
        boolean forward = Math.abs(err) < 90.0F;
        boolean sprint = forward && Math.abs(err) < SPRINT_WITHIN && dist > SPRINT_BEYOND;
        set(v, forward, false, left, right, sprint);
        // stuck: driving and not moving
        if (++sinceCheck >= STUCK_CHECK) {
            sinceCheck = 0;
            Vec3 now = v.position();
            if (forward && lastPos != null && now.distanceTo(lastPos) < STUCK_MOVE) {
                if (++stuckOnThis > STUCK_SKIP) {
                    GscraftWar.LOG.info("[gscraft] crew of {} gives up on waypoint {} at {} ({} blocks off)", v.getName().getString(), crew.routeIndex + 1, wp.toShortString(), Math.round(dist));
                    crew.routeIndex = (crew.routeIndex + 1) % crew.route.size();
                    stuckOnThis = 0;
                } else {
                    reversing = REVERSE_TICKS;
                    reverseLeft = !left;   // back out the other way
                }
            }
            lastPos = now;
        }
    }

    private static void set(Entity v, boolean forward, boolean back, boolean left, boolean right, boolean sprint) {
        Vehicles.input(v, "forward", forward);
        Vehicles.input(v, "back", back);
        Vehicles.input(v, "left", left);
        Vehicles.input(v, "right", right);
        Vehicles.input(v, "sprint", sprint);
    }
}
