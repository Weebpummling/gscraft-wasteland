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

    private static final java.util.UUID CRAWL_ID = java.util.UUID.fromString("7f1c2b3e-4d5a-4f60-9a71-0b2c3d4e5f60");

    /** the damage model's wounds on a body: bleeding hurts, a crawling fighter is slow and flat, the rest is read by the goals */
    public static void tickWounds(net.minecraft.world.entity.Mob mob, FighterState s) {
        long now = mob.level().getGameTime();
        if (s.bleedTicks > 0) {
            s.bleedTicks--;
            if (s.bleedTicks % gscraft.war.combat.Damage.BLEED_EVERY == 0) mob.hurt(mob.damageSources().generic(), gscraft.war.combat.Damage.BLEED_DAMAGE);
        }
        net.minecraft.world.entity.ai.attributes.AttributeInstance speed = mob.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED);
        if (speed == null) return;
        boolean crawling = s.crawlUntil > now;
        boolean has = speed.getModifier(CRAWL_ID) != null;
        if (crawling && !has) {
            speed.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(CRAWL_ID, "gscraft crawl", -0.6D,
                    net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_TOTAL));
        } else if (!crawling && has) {
            speed.removeModifier(CRAWL_ID);
            if (mob.getPose() == net.minecraft.world.entity.Pose.SWIMMING) {
                mob.setPose(net.minecraft.world.entity.Pose.STANDING);
                mob.refreshDimensions();
            }
        }
        // flat whether or not the gun goal is running: a crawl, or pinned under fire (the gun goal agrees when it runs);
        // only what this tick laid down does it stand up again, so the Marksman's own prone is left alone
        boolean flat = crawling || s.suppression >= GunAttackGoal.PINNED_AT;
        if (flat) {
            mob.setSprinting(false);
            if (mob.getPose() != net.minecraft.world.entity.Pose.SWIMMING) {
                mob.setPose(net.minecraft.world.entity.Pose.SWIMMING);
                mob.refreshDimensions();
            }
            s.flatByWounds = true;
        } else if (s.flatByWounds) {
            s.flatByWounds = false;
            if (mob.getPose() == net.minecraft.world.entity.Pose.SWIMMING && mob.getTarget() == null) {
                mob.setPose(net.minecraft.world.entity.Pose.STANDING);
                mob.refreshDimensions();
            }
        }
    }
}
