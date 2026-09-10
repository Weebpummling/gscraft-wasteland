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
 */
public class GunAttackGoal extends Goal {
    private static final int RELOAD_TICKS = 50;
    private static final int SUPPRESS_TICKS = 40;
    private static final double RAD_TO_DEG = 180.0D / Math.PI;
    private static final double MARKSMAN_MIN_DIST = 16.0D;
    private static final double SHIELD_LOWER_DIST = 12.0D;

    private final PathfinderMob mob;
    private final GunUser user;
    private final double speed;

    private int seeTime;
    private int sinceSeen = Integer.MAX_VALUE;
    private Vec3 lastSeen;
    private int reloadTicks;
    private int burstLeft;
    private int burstPause;
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
    }

    @Override
    public void stop() {
        mob.setAggressive(false);
        IGunOperator.fromLivingEntity(mob).aim(false);
        mob.getNavigation().stop();
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
        if (canSee && seeTime >= role.aimTicks && distSqr <= role.range * role.range) {
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

        double dx = aim.x - mob.getX();
        double dy = aim.y - mob.getEyeY();
        double dz = aim.z - mob.getZ();
        double flat = Math.sqrt(dx * dx + dz * dz);
        final float yaw = (float) (Mth.atan2(dz, dx) * RAD_TO_DEG) - 90.0F
                + (mob.getRandom().nextFloat() - 0.5F) * role.spread;
        final float pitch = (float) -(Mth.atan2(dy, flat) * RAD_TO_DEG)
                + (mob.getRandom().nextFloat() - 0.5F) * role.spread;

        ShootResult result = op.shoot(() -> pitch, () -> yaw);
        if (result != lastLogged) {
            // one line per change of outcome, so the log proves the gun path without flooding it
            GscraftWar.LOG.info("[gscraft] {} shoot -> {}", mob.getType().getDescriptionId(), result);
            lastLogged = result;
        }
        switch (result) {
            case SUCCESS -> {
                if (--burstLeft <= 0) {
                    burstPause = role.pauseMin + mob.getRandom().nextInt(role.pauseMax - role.pauseMin + 1);
                }
            }
            case NO_AMMO -> {
                if (user.takeMagazine()) {
                    reloadTicks = RELOAD_TICKS;
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
        if (role == Role.MARKSMAN && canSee && distSqr < MARKSMAN_MIN_DIST * MARKSMAN_MIN_DIST) {
            Vec3 away = DefaultRandomPos.getPosAway(mob, 16, 7, target.position());
            if (away != null) mob.getNavigation().moveTo(away.x, away.y, away.z, speed * 1.15D);
        } else {
            double hold = role.range * role.holdAt;
            if (!canSee || distSqr > hold * hold) {
                mob.getNavigation().moveTo(target, speed);
            } else {
                mob.getNavigation().stop();
            }
        }
        if (canSee) {
            mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
        } else if (lastSeen != null) {
            mob.getLookControl().setLookAt(lastSeen.x, lastSeen.y, lastSeen.z, 30.0F, 30.0F);
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
