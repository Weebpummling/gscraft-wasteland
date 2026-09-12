package gscraft.war.entity;

import gscraft.war.GscraftWar;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.lang.reflect.Constructor;
import java.util.EnumSet;

/**
 * Throw a Superb Warfare hand grenade at the target (feasibility D2, owner: "grenades are definitely going in").
 * The grenade is reached by reflection so the mod does not need Superb Warfare to compile or load; the fighter's
 * rank says how many it carries. Thrown at a target that has gone behind cover, or now and then at one in the
 * open, from 8 to 28 blocks, one every thirty seconds at most. The owner is the thrower, so the allied-damage rule
 * on the bodies keeps its squad safe. Block damage is Superb Warfare's {@code explosion_destroy}, off on our servers.
 */
public class GrenadeGoal extends Goal {
    public static double MIN_DIST = 8.0D;
    public static double MAX_DIST = 28.0D;
    public static int COOLDOWN = 600;
    private static final int WINDUP = 15;
    private static final int FOLLOW_THROUGH = 25;
    public static float CHANCE_IN_THE_OPEN = 0.25F;
    private static final Constructor<?> GRENADE = find();
    /** the fuse: the item calls this with 100 ticks after constructing the grenade; without it the grenade never detonates */
    private static final java.lang.reflect.Method SET_LIFE = findSetLife();
    private static final int FUSE = 100;

    private final PathfinderMob mob;
    private int ticks;
    private boolean thrown;

    /** read on use: Mob registers its goals before the body's fields exist */
    private FighterState state() {
        return ((GunUser) mob).fighterState();
    }

    public <T extends PathfinderMob & GunUser> GrenadeGoal(T mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private static Constructor<?> find() {
        try {
            return Class.forName("com.atsuishio.superbwarfare.entity.projectile.HandGrenadeEntity")
                    .getConstructor(LivingEntity.class, Level.class);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.info("[gscraft] Superb Warfare's hand grenade is not available; fighters throw nothing");
            return null;
        }
    }

    private static java.lang.reflect.Method findSetLife() {
        if (GRENADE == null) return null;
        try {
            return GRENADE.getDeclaringClass().getMethod("setLife", int.class);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] the hand grenade has no setLife(int); throws will not detonate: {}", ex.toString());
            return null;
        }
    }

    public static boolean available() {
        return GRENADE != null;
    }

    @Override
    public boolean canUse() {
        if (GRENADE == null || state().grenades <= 0 || state().suppression >= 0.8F) return false;
        if (state().armUntil > mob.level().getGameTime()) return false;
        LivingEntity target = mob.getTarget();
        if (target == null || !target.isAlive()) return false;
        if (mob.level().getGameTime() < state().nextGrenade) return false;
        double d = mob.distanceTo(target);
        if (d < MIN_DIST || d > MAX_DIST) return false;
        boolean sees = mob.getSensing().hasLineOfSight(target);
        if (sees) return mob.getRandom().nextFloat() < CHANCE_IN_THE_OPEN;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return ticks < WINDUP + FOLLOW_THROUGH && mob.getTarget() != null;
    }

    @Override
    public void start() {
        ticks = 0;
        thrown = false;
        mob.getNavigation().stop();
        mob.setSprinting(false);
        // the throw is never tried twice in a row: a miss still spends the cooldown
        state().nextGrenade = mob.level().getGameTime() + COOLDOWN;
        Fighters.play(mob, Anim.THROW);
        Callouts.say(mob, "grenade");
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity target = mob.getTarget();
        if (target == null) return;
        mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
        ticks++;
        if (ticks == WINDUP && !thrown) {
            thrown = true;
            throwAt(target);
        }
    }

    private void throwAt(LivingEntity target) {
        try {
            Object made = GRENADE.newInstance(mob, mob.level());
            if (!(made instanceof Projectile grenade)) return;
            if (SET_LIFE != null) SET_LIFE.invoke(grenade, FUSE);
            Vec3 eye = mob.getEyePosition();
            grenade.setPos(eye.x, eye.y - 0.1D, eye.z);
            Vec3 to = target.position().add(0.0D, 0.5D, 0.0D).subtract(eye);
            double flat = Math.sqrt(to.x * to.x + to.z * to.z);
            // a lob: the further the target, the more arc and the more speed
            Vec3 dir = new Vec3(to.x, to.y + flat * 0.22D, to.z).normalize();
            float speed = (float) Math.min(1.6D, 0.9D + flat / 50.0D);
            grenade.shoot(dir.x, dir.y, dir.z, speed, 3.0F);
            mob.level().addFreshEntity(grenade);
            state().grenades--;
            mob.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            GscraftWar.LOG.info("[gscraft] {} threw a grenade at {} blocks ({} left)", mob.getName().getString(), Math.round(flat), state().grenades);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] grenade throw failed: {}", ex.toString());
        }
    }
}
