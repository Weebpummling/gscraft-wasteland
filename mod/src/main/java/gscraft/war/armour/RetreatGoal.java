package gscraft.war.armour;

import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** The driver withdraws: the hull turned away from the threat and driven off at a sprint for the retreat's length. */
public class RetreatGoal extends Goal {
    private final Crew crew;

    public RetreatGoal(Crew crew) {
        this.crew = crew;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        return !crew.gunner() && !crew.bailed && crew.vehicle() != null && crew.retreating(crew.level().getGameTime()) && crew.threat != null
                && !Vehicles.data(crew.vehicle(), "MAIN_ENGINE_DAMAGED", false);
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
    public void tick() {
        Entity v = crew.vehicle();
        if (v == null) return;
        Vec3 away = v.position().subtract(crew.threat);
        if (away.horizontalDistanceSqr() < 1.0E-4D) away = new Vec3(1.0D, 0.0D, 0.0D);
        float bearing = (float) Math.toDegrees(Math.atan2(-away.x, away.z));
        float err = Mth.wrapDegrees(bearing - v.getYRot());
        // the threat ahead: back straight out, front armour to it (a hull turning in place went nowhere - owner 2026-09-13);
        // the way clear behind or beside: drive off, steering away
        boolean forward = Math.abs(err) < 90.0F;
        // never off a drop or into water (owner 2026-09-13): the ground three and six blocks along the way must be there;
        // if it is not, the other way if that is safe, else the hull stays put
        if (!groundAlong(v, forward)) {
            if (groundAlong(v, !forward)) forward = !forward;
            else {
                Vehicles.allStop(v);
                return;
            }
        }
        Vehicles.input(v, "forward", forward);
        Vehicles.input(v, "back", !forward);
        Vehicles.input(v, "left", forward && err < -DriveGoal.STEER_DEAD);
        Vehicles.input(v, "right", forward && err > DriveGoal.STEER_DEAD);
        Vehicles.input(v, "sprint", forward && Math.abs(err) < 30.0F);
    }

    /** solid ground within five blocks under the points three and six blocks along the hull's heading (or behind it), and no fluid on the way */
    static boolean groundAlong(Entity v, boolean ahead) {
        Vec3 look = v.getLookAngle();
        Vec3 dir = new Vec3(look.x, 0, look.z);
        if (dir.lengthSqr() < 1.0E-4) dir = new Vec3(0, 0, 1);
        dir = dir.normalize().scale(ahead ? 1 : -1);
        for (int d = 3; d <= 6; d += 3) {
            Vec3 p = v.position().add(dir.scale(d));
            net.minecraft.core.BlockPos at = net.minecraft.core.BlockPos.containing(p.x, v.getY() + 1, p.z);
            boolean ground = false;
            for (int dy = 0; dy <= 6; dy++) {
                net.minecraft.core.BlockPos q = at.below(dy);
                if (!v.level().getFluidState(q).isEmpty()) return false;
                if (!v.level().getBlockState(q).getCollisionShape(v.level(), q).isEmpty()) {
                    ground = true;
                    break;
                }
            }
            if (!ground) return false;
        }
        return true;
    }

    @Override
    public void stop() {
        Entity v = crew.vehicle();
        if (v != null) Vehicles.allStop(v);
    }
}
