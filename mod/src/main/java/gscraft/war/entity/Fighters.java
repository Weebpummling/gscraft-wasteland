package gscraft.war.entity;

import gscraft.war.faction.Factions;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/** Behaviour shared by every fighter body. */
public final class Fighters {
    private static final double CALL_RADIUS = 20.0D;

    private Fighters() {}

    /** A Sergeant's target becomes the target of every idle ally within earshot. */
    public static void callTarget(Mob leader) {
        LivingEntity target = leader.getTarget();
        if (target == null || !target.isAlive()) return;
        for (Mob ally : leader.level().getEntitiesOfClass(Mob.class, leader.getBoundingBox().inflate(CALL_RADIUS),
                m -> m != leader && m.getTarget() == null && Factions.allied(leader, m))) {
            ally.setTarget(target);
        }
    }
}
