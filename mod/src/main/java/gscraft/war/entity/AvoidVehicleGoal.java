package gscraft.war.entity;

import gscraft.war.armour.Vehicles;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;

/**
 * A fighter never stands against a hull (owner 2026-09-13: they kept running into vehicles): inside a vehicle's box
 * grown by the clearance - friend's or foe's, still or driving at them - the fighter steps out of it, four blocks
 * off the hull's centre, before anything else. Riding is not standing against; and an escort within four of its own
 * hull's centre is boarding, which the clearance leaves room for.
 */
public class AvoidVehicleGoal extends Goal {
    public static double CLEARANCE = 1.5D;
    public static double STEP = 4.5D;

    private final Mob mob;
    private Entity hull;
    private int ticks;

    public AvoidVehicleGoal(Mob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private Entity near() {
        List<Entity> hulls = mob.level().getEntities(mob, mob.getBoundingBox().inflate(4.0D), e -> Vehicles.isVehicle(e) && e != mob.getVehicle() && e.isAlive());
        for (Entity e : hulls) {
            if (e.getBoundingBox().inflate(CLEARANCE, 0.5D, CLEARANCE).contains(mob.position())) return e;
        }
        return null;
    }

    @Override
    public boolean canUse() {
        if (mob.isPassenger() || mob.tickCount % 5 != 0) return false;
        hull = near();
        return hull != null;
    }

    @Override
    public void start() {
        ticks = 0;
        step();
    }

    private void step() {
        Vec3 away = mob.position().subtract(hull.position());
        away = new Vec3(away.x, 0, away.z);
        if (away.lengthSqr() < 1.0E-3) {
            // dead centre: sideways off the hull's heading
            double yaw = Math.toRadians(hull.getYRot());
            away = new Vec3(Math.cos(yaw), 0, Math.sin(yaw));
        }
        Vec3 to = hull.position().add(away.normalize().scale(STEP));
        mob.getNavigation().moveTo(to.x, mob.getY(), to.z, 1.2D);
    }

    @Override
    public boolean canContinueToUse() {
        return hull != null && hull.isAlive() && ++ticks < 40 && hull.getBoundingBox().inflate(CLEARANCE, 0.5D, CLEARANCE).contains(mob.position());
    }

    @Override
    public void tick() {
        if (ticks % 10 == 0) step();
    }

    @Override
    public void stop() {
        hull = null;
    }
}
