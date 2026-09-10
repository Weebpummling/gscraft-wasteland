package gscraft.war.entity;

import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Walk toward a heard shot until something to fight comes into view, the spot is reached, or twelve seconds pass.
 * Sits above wandering and below every fight, so a target always wins.
 */
public class InvestigateGoal extends Goal {
    private static final int GIVE_UP_TICKS = 240;

    private final PathfinderMob mob;
    private Vec3 pos;
    private int ticks;

    public InvestigateGoal(PathfinderMob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    public void hear(Vec3 heard) {
        this.pos = heard;
        this.ticks = 0;
    }

    @Override
    public boolean canUse() {
        return pos != null && mob.getTarget() == null;
    }

    @Override
    public void start() {
        mob.getNavigation().moveTo(pos.x, pos.y, pos.z, 1.0D);
    }

    @Override
    public boolean canContinueToUse() {
        return pos != null && mob.getTarget() == null && ticks < GIVE_UP_TICKS && !mob.getNavigation().isDone();
    }

    @Override
    public void tick() {
        ticks++;
    }

    @Override
    public void stop() {
        pos = null;
    }
}
