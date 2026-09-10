package gscraft.war.entity;

import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.entity.ShootResult;
import com.tacz.guns.api.item.IGun;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.item.ItemStack;

import java.util.EnumSet;

/**
 * Fire the issued TACZ gun. TACZ mixes IGunOperator into every LivingEntity, so a soldier draws, aims and
 * shoots through the same code a player does. Fire comes in bursts with a pause between. An empty magazine
 * is refilled after a reload delay: TACZ checks ammo for non-players but gives them no inventory to reload
 * from, so without the refill a soldier would empty one magazine and stand there (design F4).
 */
public class GunAttackGoal extends Goal {
    private static final int AIM_TICKS = 12;
    private static final int RELOAD_TICKS = 50;
    private static final double RAD_TO_DEG = 180.0D / Math.PI;

    private final PathfinderMob mob;
    private final double speed;
    private final float rangeSqr;

    private int seeTime;
    private int reloadTicks;
    private int burstLeft;
    private int burstPause;
    private ShootResult lastLogged;

    public GunAttackGoal(PathfinderMob mob, double speed, float range) {
        this.mob = mob;
        this.speed = speed;
        this.rangeSqr = range * range;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = mob.getTarget();
        return target != null && target.isAlive() && IGun.mainHandHoldGun(mob);
    }

    @Override
    public void start() {
        mob.setAggressive(true);
        IGunOperator.fromLivingEntity(mob).draw(mob::getMainHandItem);
        seeTime = 0;
        burstLeft = 0;
        burstPause = 0;
    }

    @Override
    public void stop() {
        mob.setAggressive(false);
        IGunOperator.fromLivingEntity(mob).aim(false);
        mob.getNavigation().stop();
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

        double distSqr = mob.distanceToSqr(target);
        boolean canSee = mob.getSensing().hasLineOfSight(target);
        seeTime = canSee ? seeTime + 1 : 0;

        // close in until there is a line of sight and the range is comfortable, then hold ground
        if (!canSee || distSqr > rangeSqr * 0.6F) {
            mob.getNavigation().moveTo(target, speed);
        } else {
            mob.getNavigation().stop();
        }
        mob.getLookControl().setLookAt(target, 30.0F, 30.0F);

        IGunOperator op = IGunOperator.fromLivingEntity(mob);
        if (reloadTicks > 0) {
            if (--reloadTicks == 0) refill(mob.getMainHandItem());
            return;
        }
        if (!canSee || seeTime < AIM_TICKS || distSqr > rangeSqr) {
            op.aim(false);
            return;
        }
        op.aim(true);

        if (burstPause > 0) {
            burstPause--;
            return;
        }
        if (burstLeft <= 0) burstLeft = 3 + mob.getRandom().nextInt(4);

        double dx = target.getX() - mob.getX();
        double dy = target.getY() + target.getBbHeight() * 0.6D - mob.getEyeY();
        double dz = target.getZ() - mob.getZ();
        double flat = Math.sqrt(dx * dx + dz * dz);
        float spread = 2.5F;
        final float yaw = (float) (Mth.atan2(dz, dx) * RAD_TO_DEG) - 90.0F
                + (mob.getRandom().nextFloat() - 0.5F) * spread;
        final float pitch = (float) -(Mth.atan2(dy, flat) * RAD_TO_DEG)
                + (mob.getRandom().nextFloat() - 0.5F) * spread;

        ShootResult result = op.shoot(() -> pitch, () -> yaw);
        if (result != lastLogged) {
            // one line per change of outcome, so the log proves the gun path without flooding it
            GscraftWar.LOG.info("[gscraft] {} shoot -> {}", mob.getType().getDescriptionId(), result);
            lastLogged = result;
        }
        switch (result) {
            case SUCCESS -> {
                if (--burstLeft <= 0) burstPause = 20 + mob.getRandom().nextInt(25);
            }
            case NO_AMMO -> reloadTicks = RELOAD_TICKS;
            case NOT_DRAW -> op.draw(mob::getMainHandItem);
            case NEED_BOLT -> op.bolt();
            default -> { }
        }
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
