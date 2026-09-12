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
        return !crew.gunner() && crew.vehicle() != null && crew.retreating(crew.level().getGameTime()) && crew.threat != null
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
        boolean forward = Math.abs(err) < 100.0F;
        Vehicles.input(v, "forward", forward);
        Vehicles.input(v, "back", false);
        Vehicles.input(v, "left", err < -DriveGoal.STEER_DEAD);
        Vehicles.input(v, "right", err > DriveGoal.STEER_DEAD);
        Vehicles.input(v, "sprint", forward && Math.abs(err) < 30.0F);
    }

    @Override
    public void stop() {
        Entity v = crew.vehicle();
        if (v != null) Vehicles.allStop(v);
    }
}
