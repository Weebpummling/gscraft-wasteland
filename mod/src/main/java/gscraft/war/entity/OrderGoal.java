package gscraft.war.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Out of a fight, an ordered fighter walks to its point and stays (feasibility B2). HOLD keeps it there; ADVANCE
 * walks it there and becomes HOLD on arrival. In a fight the gun goal reads the same order: a holding fighter does
 * not chase, an advancing one keeps walking and fires when it can.
 */
public class OrderGoal extends Goal {
    private static final double ARRIVE = 2.5D;
    private final PathfinderMob mob;
    private int repath;

    public <T extends PathfinderMob & GunUser> OrderGoal(T mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private FighterState state() {
        return ((GunUser) mob).fighterState();
    }

    @Override
    public boolean canUse() {
        FighterState s = state();
        if (s.order == FighterState.Order.NONE) return false;
        return mob.blockPosition().distSqr(s.orderPos) > ARRIVE * ARRIVE;
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public void start() {
        repath = 0;
    }

    @Override
    public void tick() {
        if (--repath > 0) return;
        repath = 20;
        BlockPos to = state().orderPos;
        mob.getNavigation().moveTo(to.getX() + 0.5D, to.getY(), to.getZ() + 0.5D, state().order == FighterState.Order.ADVANCE ? 1.15D : 1.0D);
    }

    @Override
    public void stop() {
        FighterState s = state();
        if (s.order == FighterState.Order.ADVANCE && mob.blockPosition().distSqr(s.orderPos) <= ARRIVE * ARRIVE) {
            s.order = FighterState.Order.HOLD;
        }
    }
}
