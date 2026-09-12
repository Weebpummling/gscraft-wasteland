package gscraft.war.entity;

import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.entity.ShootResult;
import com.tacz.guns.api.item.IGun;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
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
 *
 * Cover (B1): once it has a target in reach and is not the Shield, it looks for a spot nearby that the target
 * cannot see into, with a lean beside it that can see out; it walks there, crouches, steps to the lean to fire a
 * burst and steps back for the pause. Cover is dropped when the target can see into it again. Orders (B2): a
 * holding fighter never chases and only takes cover within six blocks of its point; an advancing one walks to its
 * point and fires when it can. The Marksman goes flat to fire beyond 32 blocks (A3).
 */
public class GunAttackGoal extends Goal {
    public static int RELOAD_TICKS = 50;
    /** cover is taken, and the squad stops bounding, inside range x hold_at x this */
    public static double HOLD_FACTOR = 1.2D;
    public static int SUPPRESS_TICKS = 40;
    private static final double RAD_TO_DEG = 180.0D / Math.PI;
    public static double MARKSMAN_MIN_DIST = 16.0D;
    public static double MARKSMAN_PRONE_DIST = 32.0D;
    private static final double SHIELD_LOWER_DIST = 12.0D;
    public static double CROUCH_FIRE_DIST = 16.0D;
    public static float CROUCH_AT = 0.4F;
    public static float PINNED_AT = 0.8F;
    private static final int STRAFE_TICKS = 12;
    private static final int COVER_SEARCH_EVERY = 20;
    public static int COVER_LOST_TICKS = 40;
    private static final double COVER_ARRIVE = 1.6D;
    private static final int COVER_PATH_EVERY = 10;
    public static int COVER_TRAVEL_TICKS = 100;   // a spot not reached in five seconds is given up
    private static final int LOW_BLOCKED_TICKS = 100;
    private static final double HOLD_COVER_REACH = 6.0D;

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
    private long lastFightEnd = Long.MIN_VALUE;
    private ShootResult lastLogged;

    // cover
    private Cover.Spot cover;
    private boolean leaning;
    private int coverSearch;
    private int coverLost;
    private int coverPath;
    private int coverTravel;
    private int leanStuck;
    /** a lowered stance that lost the line of sight stands back up and stays up for a while */
    private long lowBlockedUntil;

    public <T extends PathfinderMob & GunUser> GunAttackGoal(T mob, double speed) {
        this.mob = mob;
        this.user = mob;
        this.speed = speed;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    public Cover.Spot cover() {
        return cover;
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
        cover = null;
        leaning = false;
        coverSearch = 0;
        coverLost = 0;
        if (mob.level().getGameTime() - lastFightEnd > 200) Callouts.say(mob, "contact");
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
        cover = null;
        lastFightEnd = mob.level().getGameTime();
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
        FighterState state = user.fighterState();
        float s = state.suppression;

        double distSqr = mob.distanceToSqr(target);
        boolean canSee = mob.getSensing().hasLineOfSight(target);
        if (canSee) {
            seeTime++;
            sinceSeen = 0;
            lastSeen = new Vec3(target.getX(), target.getY() + target.getBbHeight() * 0.6D, target.getZ());
        } else {
            // a blink of lost sight costs part of the aim, not all of it: a lowered eye over rough ground blinks
            if (seeTime > 0) seeTime = Math.max(0, seeTime - 4);
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

        // lowered and blind: terrain in the way at the lower eye - stand, and stay standing for a while (out of cover)
        if (!canSee && cover == null && mob.getPose() != Pose.STANDING && lastSeen != null) {
            stance(Pose.STANDING);
            lowBlockedUntil = mob.level().getGameTime() + LOW_BLOCKED_TICKS;
        }

        updateCover(role, state, target, distSqr);
        move(role, state, target, distSqr, canSee);

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

        // the pause between bursts is time, not time in sight: counted down behind cover too, or a fighter whose
        // pause outlasted its step back behind the cover never leaned out again (the Marksman, every time)
        if (burstPause > 0) burstPause--;
        Vec3 aim = null;
        int aimTicks = Math.round(role.aimTicks * (1.0F + s) * (state.armUntil > mob.level().getGameTime() ? 2.0F : 1.0F));
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

        if (burstPause > 0) return;
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
                    if (cover != null) {
                        leaning = false;   // the burst is done: back behind the cover for the pause
                    } else if (mob.getPose() == Pose.STANDING && mob.getNavigation().isDone() && role != Role.MARKSMAN && role != Role.SHIELD) {
                        // a sidestep after the burst, standing in the open, so the next burst comes from somewhere else
                        strafeTicks = STRAFE_TICKS;
                        strafeDir = mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
                    }
                }
            }
            case NO_AMMO -> {
                if (user.takeMagazine()) {
                    reloadTicks = RELOAD_TICKS;
                    leaning = false;
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

    /** look for cover once a second while none is held; drop it once the target can see into it */
    private void updateCover(Role role, FighterState state, LivingEntity target, double distSqr) {
        if (!(mob.level() instanceof ServerLevel level) || role == Role.SHIELD || state.order == FighterState.Order.ADVANCE) {
            cover = null;
            return;
        }
        if (cover != null) {
            boolean there = mob.position().distanceTo(cover.stand()) <= COVER_ARRIVE;
            if (!there && !leaning && ++coverTravel > COVER_TRAVEL_TICKS) {
                cover = null;   // the path never got there: a spot the fighter cannot actually stand in
                return;
            }
            // judged where the fighter really stands once it is there (a spot the body settles beside, not on, is no
            // cover), at the marked stand while walking in or leaning out
            Vec3 judge = there && !leaning ? mob.position() : cover.stand();
            if (Cover.covered(level, mob, target, judge)) {
                coverLost = 0;
            } else if (++coverLost > COVER_LOST_TICKS) {
                cover = null;
                leaning = false;
            }
            return;
        }
        // cover only once the fighter has closed to its holding distance (the squad bounds beyond it); a fighter that
        // dug in at forty blocks never advanced - the Marksman's hold is its full range, so it digs in where it stands
        double hold = role.range * role.holdAt * HOLD_FACTOR;
        if (distSqr > hold * hold) return;
        if (--coverSearch > 0) return;
        coverSearch = COVER_SEARCH_EVERY;
        Cover.Spot found = Cover.find(level, mob, target, role.range);
        if (found == null) return;
        if (state.order == FighterState.Order.HOLD && found.stand().distanceTo(Vec3.atBottomCenterOf(state.orderPos)) > HOLD_COVER_REACH) return;
        cover = found;
        leaning = false;
        coverLost = 0;
        coverTravel = 0;
    }

    private void move(Role role, FighterState state, LivingEntity target, double distSqr, boolean canSee) {
        boolean moving;
        if (state.order == FighterState.Order.ADVANCE) {
            // the order stands: walk to the point, fire on the way when the line is there
            Vec3 to = Vec3.atBottomCenterOf(state.orderPos);
            moving = mob.position().distanceTo(to) > 2.5D;
            if (moving) mob.getNavigation().moveTo(to.x, to.y, to.z, speed * 1.15D);
            else state.order = FighterState.Order.HOLD;
            mob.setSprinting(false);
        } else if (cover != null) {
            Vec3 stand = cover.stand();
            Vec3 want = leaning ? cover.lean() : stand;
            double away = mob.position().distanceTo(want);
            if (away > COVER_ARRIVE && !leaning) {
                if (--coverPath <= 0) {
                    coverPath = COVER_PATH_EVERY;
                    mob.getNavigation().moveTo(want.x, want.y, want.z, speed);
                }
                moving = away > 3.0D;
            } else {
                mob.getNavigation().stop();
                // at the cover: step to the lean to fire, back behind it to pause or reload
                boolean wantLean = burstPause == 0 && reloadTicks == 0 && distSqr <= role.range * role.range;
                if (wantLean != leaning) {
                    leaning = wantLean;
                    leanStuck = 0;
                }
                Vec3 step = leaning ? cover.lean() : stand;
                if (mob.position().distanceTo(step) > 0.35D) {
                    mob.getMoveControl().setWantedPosition(step.x, step.y, step.z, 0.7D);
                    // a lean the body cannot reach in two seconds (something in the way the search did not see): the spot is no good
                    if (leaning && ++leanStuck > 40) {
                        cover = null;
                        leaning = false;
                    }
                } else {
                    leanStuck = 0;
                }
                moving = false;
            }
            mob.setSprinting(false);
        } else if (state.order == FighterState.Order.HOLD) {
            // held: fire from here, never chase
            mob.getNavigation().stop();
            mob.setSprinting(false);
            moving = false;
        } else if (role == Role.MARKSMAN && canSee && distSqr < MARKSMAN_MIN_DIST * MARKSMAN_MIN_DIST) {
            Vec3 away = DefaultRandomPos.getPosAway(mob, 16, 7, target.position());
            if (away != null) mob.getNavigation().moveTo(away.x, away.y, away.z, speed * 1.15D);
            moving = true;
        } else {
            double hold = role.range * role.holdAt;
            moving = !canSee || distSqr > hold * hold;
            if (moving) {
                mob.getNavigation().moveTo(target, speed);
                // ground to cover: sprint when the target is well beyond the holding distance
                mob.setSprinting(distSqr > hold * hold * 2.25D && state.crawlUntil <= mob.level().getGameTime());
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

        // the stance: flat is decided above; crouched in cover, under fire or firing at long range; the Marksman
        // flat beyond 32; standing when moving
        float s = state.suppression;
        boolean mayLower = cover != null || mob.level().getGameTime() >= lowBlockedUntil;
        if (state.crawlUntil > mob.level().getGameTime()) {
            stance(Pose.SWIMMING);   // a leg wound: flat and slow until it passes
            mob.setSprinting(false);
            strafeTicks = 0;
        } else if (moving || !mayLower) {
            stance(Pose.STANDING);
            strafeTicks = 0;
        } else if (role == Role.MARKSMAN && cover == null && canSee && seeTime >= role.aimTicks && distSqr > MARKSMAN_PRONE_DIST * MARKSMAN_PRONE_DIST) {
            // flat in the open only: a cover's lean is judged from the crouched eye, and a prone eye behind it sees nothing
            stance(Pose.SWIMMING);
            strafeTicks = 0;
        } else if (cover != null || s >= CROUCH_AT
                || (canSee && distSqr > CROUCH_FIRE_DIST * CROUCH_FIRE_DIST && role != Role.SHIELD && (role != Role.MARKSMAN || seeTime >= role.aimTicks))) {
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
