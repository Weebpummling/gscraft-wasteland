package gscraft.war.entity;

import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.entity.ShootResult;
import com.tacz.guns.api.item.IGun;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Fire the issued TACZ gun, the way the fighter's {@link Role} fights. TACZ mixes IGunOperator into every
 * LivingEntity, so a soldier draws, aims and shoots through the same code a player does.
 *
 * Ammunition is finite (review W10): an empty magazine is replaced from the fighter's spare magazines after a
 * reload delay, and when the last one is gone the goal stops for good and the melee goal takes over.
 *
 * Under fire (feasibility A4) the fighter's suppression, 0 to 1, widens its spread, slows its aim and lowers its
 * stance: a crouch from 0.4, flat on the ground and not firing from 0.8. It crouches to fire from a standstill
 * beyond 16 blocks anyway, sidesteps after a burst in the open (A2), and sprints when it has ground to cover (A1).
 */
public class GunAttackGoal extends Goal {
    private static final int RELOAD_TICKS = 50;
    private static final int SUPPRESS_TICKS = 40;
    private static final double RAD_TO_DEG = 180.0D / Math.PI;
    private static final double MARKSMAN_MIN_DIST = 16.0D;
    private static final double SHIELD_LOWER_DIST = 12.0D;
    private static final double CROUCH_FIRE_DIST = 16.0D;
    private static final float CROUCH_AT = 0.4F;
    private static final float PINNED_AT = 0.8F;
    private static final int STRAFE_TICKS = 12;

    private final PathfinderMob mob;
    private final GunUser user;
    private final double speed;

    private int seeTime;
    private int sinceSeen = Integer.MAX_VALUE;
    private Vec3 lastSeen;
    private int reloadTicks;
    private int burstLeft;
    private int burstPause;
    private int strafeTicks;
    private float strafeDir;
    private boolean pinnedSaid;
    private ShootResult lastLogged;

    public <T extends PathfinderMob & GunUser> GunAttackGoal(T mob, double speed) {
        this.mob = mob;
        this.user = mob;
        this.speed = speed;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = mob.getTarget();
        return target != null && target.isAlive() && IGun.mainHandHoldGun(mob) && !user.outOfAmmo();
    }

    @Override
    public void start() {
        mob.setAggressive(true);
        IGunOperator.fromLivingEntity(mob).draw(mob::getMainHandItem);
        seeTime = 0;
        sinceSeen = Integer.MAX_VALUE;
        lastSeen = null;
        burstLeft = 0;
        burstPause = 0;
        strafeTicks = 0;
        pinnedSaid = false;
        Callouts.say(mob, "contact");
    }

    @Override
    public void stop() {
        mob.setAggressive(false);
        IGunOperator.fromLivingEntity(mob).aim(false);
        mob.getNavigation().stop();
        mob.setSprinting(false);
        stance(Pose.STANDING);
        lowerShield();
        seeTime = 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity target = mob.getTarget();
        if (target == null) return;
        Role role = user.role();
        float s = user.fighterState().suppression;

        double distSqr = mob.distanceToSqr(target);
        boolean canSee = mob.getSensing().hasLineOfSight(target);
        if (canSee) {
            seeTime++;
            sinceSeen = 0;
            lastSeen = new Vec3(target.getX(), target.getY() + target.getBbHeight() * 0.6D, target.getZ());
        } else {
            seeTime = 0;
            if (sinceSeen < Integer.MAX_VALUE) sinceSeen++;
        }

        if (s >= PINNED_AT) {
            // head down: nothing is fired and nothing moves until the fire lifts
            mob.getNavigation().stop();
            mob.setSprinting(false);
            stance(Pose.SWIMMING);
            IGunOperator.fromLivingEntity(mob).aim(false);
            if (!pinnedSaid) {
                pinnedSaid = true;
                Callouts.say(mob, "pinned");
            }
            return;
        }
        pinnedSaid = false;

        move(role, target, distSqr, canSee);

        if (role == Role.SHIELD) {
            // the shield is up while closing in and while reloading; it comes down only to fire at close range
            if (reloadTicks > 0 || !canSee || distSqr > SHIELD_LOWER_DIST * SHIELD_LOWER_DIST) raiseShield();
            else lowerShield();
        }

        IGunOperator op = IGunOperator.fromLivingEntity(mob);
        if (reloadTicks > 0) {
            if (--reloadTicks == 0) refill(mob.getMainHandItem());
            return;
        }

        Vec3 aim = null;
        int aimTicks = Math.round(role.aimTicks * (1.0F + s));
        if (canSee && seeTime >= aimTicks && distSqr <= role.range * role.range) {
            aim = lastSeen;
        } else if (!canSee && role == Role.GUNNER && sinceSeen < SUPPRESS_TICKS && lastSeen != null) {
            aim = lastSeen;   // suppression: keep the last known position under fire
        }
        if (aim == null) {
            op.aim(false);
            return;
        }
        op.aim(true);

        if (burstPause > 0) {
            burstPause--;
            return;
        }
        if (burstLeft <= 0) burstLeft = role.burstMin + mob.getRandom().nextInt(role.burstMax - role.burstMin + 1);

        float spread = role.spread * (1.0F + 2.0F * s);
        double dx = aim.x - mob.getX();
        double dy = aim.y - mob.getEyeY();
        double dz = aim.z - mob.getZ();
        double flat = Math.sqrt(dx * dx + dz * dz);
        final float yaw = (float) (Mth.atan2(dz, dx) * RAD_TO_DEG) - 90.0F + (mob.getRandom().nextFloat() - 0.5F) * spread;
        final float pitch = (float) -(Mth.atan2(dy, flat) * RAD_TO_DEG) + (mob.getRandom().nextFloat() - 0.5F) * spread;

        ShootResult result = op.shoot(() -> pitch, () -> yaw);
        if (result != lastLogged) {
            GscraftWar.LOG.debug("[gscraft] {} shoot -> {}", mob.getType().getDescriptionId(), result);
            lastLogged = result;
        }
        switch (result) {
            case SUCCESS -> {
                if (--burstLeft <= 0) {
                    burstPause = role.pauseMin + mob.getRandom().nextInt(role.pauseMax - role.pauseMin + 1);
                    // a sidestep after the burst, standing in the open, so the next burst comes from somewhere else
                    if (mob.getPose() == Pose.STANDING && mob.getNavigation().isDone() && role != Role.MARKSMAN && role != Role.SHIELD) {
                        strafeTicks = STRAFE_TICKS;
                        strafeDir = mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
                    }
                }
            }
            case NO_AMMO -> {
                if (user.takeMagazine()) {
                    reloadTicks = RELOAD_TICKS;
                    Callouts.say(mob, "reloading");
                } else {
                    user.markOutOfAmmo();
                    GscraftWar.LOG.info("[gscraft] {} out of ammo, closing to melee", mob.getType().getDescriptionId());
                }
            }
            case NOT_DRAW -> op.draw(mob::getMainHandItem);
            case NEED_BOLT -> op.bolt();
            default -> { }
        }
    }

    private void move(Role role, LivingEntity target, double distSqr, boolean canSee) {
        boolean moving;
        if (role == Role.MARKSMAN && canSee && distSqr < MARKSMAN_MIN_DIST * MARKSMAN_MIN_DIST) {
            Vec3 away = DefaultRandomPos.getPosAway(mob, 16, 7, target.position());
            if (away != null) mob.getNavigation().moveTo(away.x, away.y, away.z, speed * 1.15D);
            moving = true;
        } else {
            double hold = role.range * role.holdAt;
            moving = !canSee || distSqr > hold * hold;
            if (moving) {
                mob.getNavigation().moveTo(target, speed);
                // ground to cover: sprint when the target is well beyond the holding distance
                mob.setSprinting(distSqr > hold * hold * 2.25D);
            } else {
                mob.getNavigation().stop();
                mob.setSprinting(false);
            }
        }
        if (canSee) {
            mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
        } else if (lastSeen != null) {
            mob.getLookControl().setLookAt(lastSeen.x, lastSeen.y, lastSeen.z, 30.0F, 30.0F);
        }

        // the stance: flat is decided above; crouched under fire or firing at long range; standing when moving
        float s = user.fighterState().suppression;
        if (moving) {
            stance(Pose.STANDING);
            strafeTicks = 0;
        } else if (s >= CROUCH_AT || (canSee && distSqr > CROUCH_FIRE_DIST * CROUCH_FIRE_DIST && role != Role.SHIELD)) {
            stance(Pose.CROUCHING);
            strafeTicks = 0;
        } else {
            stance(Pose.STANDING);
        }
        if (strafeTicks > 0 && reloadTicks == 0) {
            strafeTicks--;
            mob.getMoveControl().strafe(0.0F, 0.6F * strafeDir);
        }
    }

    private void stance(Pose pose) {
        if (mob.getPose() != pose) {
            mob.setPose(pose);
            mob.refreshDimensions();
        }
    }

    private void raiseShield() {
        if (mob.getOffhandItem().is(Items.SHIELD) && !mob.isUsingItem()) mob.startUsingItem(InteractionHand.OFF_HAND);
    }

    private void lowerShield() {
        if (mob.isUsingItem() && mob.getUsedItemHand() == InteractionHand.OFF_HAND) mob.stopUsingItem();
    }

    /** Fill the magazine to the gun's own capacity, from TACZ's gun index. */
    static void refill(ItemStack stack) {
        IGun gun = IGun.getIGunOrNull(stack);
        if (gun == null) return;
        ResourceLocation id = gun.getGunId(stack);
        int magazine = TimelessAPI.getCommonGunIndex(id).map(i -> i.getGunData().getAmmoAmount()).orElse(30);
        gun.setCurrentAmmoCount(stack, magazine);
        gun.setBulletInBarrel(stack, true);
    }
}
