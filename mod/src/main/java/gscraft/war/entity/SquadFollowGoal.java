package gscraft.war.entity;

import gscraft.war.world.Director;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** Out of a fight, a squad member walks to its slot around the leader and keeps it (feasibility C1). */
public class SquadFollowGoal extends Goal {
    private static final double SLACK = 2.5D;
    private final PathfinderMob mob;
    private int repath;

    public <T extends PathfinderMob & GunUser> SquadFollowGoal(T mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private FighterState state() {
        return ((GunUser) mob).fighterState();
    }

    private Mob leader() {
        if (!(mob.level() instanceof ServerLevel level) || state().squadId == null) return null;
        Mob leader = Squad.leader(level, mob);
        return leader == mob ? null : leader;
    }

    @Override
    public boolean canUse() {
        if (state().order != FighterState.Order.NONE || mob.getTarget() != null) return false;
        Mob leader = leader();
        if (leader == null || !leader.isAlive()) return false;
        Vec3 slot = Squad.slotPosition(leader, ((GunUser) leader).fighterState().formation, state().slot);
        return mob.position().distanceTo(slot) > SLACK;
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
        repath = 10;
        Mob leader = leader();
        if (leader == null) return;
        Vec3 slot = Squad.slotPosition(leader, ((GunUser) leader).fighterState().formation, state().slot);
        BlockPos stand = Director.nearestStand((ServerLevel) mob.level(), BlockPos.containing(slot));
        if (stand == null) stand = BlockPos.containing(slot);
        double far = mob.position().distanceTo(slot);
        mob.getNavigation().moveTo(stand.getX() + 0.5D, stand.getY(), stand.getZ() + 0.5D, far > 8.0D ? 1.2D : 1.0D);
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }
}
