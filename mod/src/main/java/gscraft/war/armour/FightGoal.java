package gscraft.war.armour;

import gscraft.war.GscraftWar;
import gscraft.war.entity.GunUser;
import gscraft.war.entity.Role;
import gscraft.war.faction.Factions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;

/**
 * The crew fights (armour design §2, V3; owner 2026-09-12: slower to acquire, sight rechecked, a limited cone, a
 * target priority). The mod's own tick lays the turret on the aim target and fires the seat's weapon at the mob's
 * target once the barrel is within four degrees, so the crew only chooses.
 *
 * Detection: a threat must lie inside the crew's cone about the hull's heading - the driver's is narrow, the
 * gunner's (the commander's station) wider - and be seen from the turret for the acquire time before it is
 * engaged; a hit on the vehicle alerts the crew and opens the cone all round for a while, and a target one crew
 * engages is known to the other. The cone is why armour needs infantry with it. Priority: enemy armour, then
 * players, then fighters with heavy weapons, then the rest, nearer first within a class. Sight is rechecked while
 * engaged and a target out of sight too long is dropped; a better target that comes into view replaces the current
 * one. The driver halts to shoot and picks the weapon (a missile for armour where the seat has one, else the
 * cannon); fire is held while an ally stands in the line; below the retreat share of health, or with the turret
 * gone, the driver withdraws (the retreat goal), and with the engine gone it sits and fights.
 */
public class FightGoal extends Goal {
    public static double ENGAGE = 96.0D;
    public static int ACQUIRE_TICKS = 40;
    public static int LOST_TICKS = 100;
    public static int RETARGET_TICKS = 60;
    public static double VIEW_CONE_DRIVER = 120.0D;
    public static double VIEW_CONE_GUNNER = 200.0D;
    public static int ALERT_TICKS = 400;
    public static double FRIENDLY_RADIUS = 2.5D;
    public static float RETREAT_SHARE = 0.33F;
    public static int RETREAT_TICKS = 200;
    public static int CALM_TICKS = 600;
    private static final String NONE = "undefined";

    private final Crew crew;
    private LivingEntity target;
    private LivingEntity candidate;
    private int candidateTicks;
    private int lost;
    private int ticks;
    private boolean holding;

    public FightGoal(Crew crew) {
        this.crew = crew;
        setFlags(crew.gunner() ? EnumSet.of(Flag.TARGET) : EnumSet.of(Flag.MOVE, Flag.TARGET));
    }

    @Override
    public boolean canUse() {
        Entity v = crew.vehicle();
        if (v == null || crew.bailed) return false;
        long now = crew.level().getGameTime();
        if (!crew.gunner() && (crew.retreating(now) || crew.calm(now))) return false;
        if (crew.tickCount % 5 != 0) return false;
        LivingEntity best = pick(v);
        if (best == null) {
            candidate = null;
            candidateTicks = 0;
            return false;
        }
        if (best != candidate) {
            candidate = best;
            candidateTicks = 0;
        }
        candidateTicks += 5;
        // a target the other crew already engages is known at once
        if (candidateTicks < ACQUIRE_TICKS && !Armour.engagedBy(v, best)) return false;
        target = candidate;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        Entity v = crew.vehicle();
        return v != null && !crew.bailed && target != null && target.isAlive() && lost < LOST_TICKS && v.distanceTo(target) < ENGAGE * 1.25D
                && (crew.gunner() || !crew.retreating(crew.level().getGameTime()));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        Entity v = crew.vehicle();
        lost = 0;
        ticks = 0;
        holding = false;
        if (v == null) return;
        crew.engaged = target;
        if (!crew.gunner()) {
            Vehicles.allStop(v);   // halt to shoot
            chooseWeapon(v);
            crew.dismount(v);
        }
        aim(v);
        GscraftWar.LOG.info("[gscraft] {} ({}) engages {} at {} blocks", v.getName().getString(), crew.gunner() ? "gunner" : "driver", target.getName().getString(), Math.round(v.distanceTo(target)));
    }

    @Override
    public void stop() {
        Entity v = crew.vehicle();
        crew.setTarget(null);
        crew.engaged = null;
        if (v != null) {
            if (crew.gunner()) Vehicles.setData(v, "AI_PASSENGER_WEAPON_TARGET_UUID", NONE);
            else Vehicles.setData(v, "AI_TURRET_TARGET_UUID", NONE);
        }
        target = null;
        candidate = null;
        candidateTicks = 0;
    }

    @Override
    public void tick() {
        Entity v = crew.vehicle();
        if (v == null || target == null) return;
        ticks++;
        if (ticks % 10 == 0) {
            if (sees(v, target)) lost = 0;
            else lost += 10;
        }
        if (ticks % 5 == 0) {
            boolean hold = allyInLine(v, target);
            if (hold != holding) {
                holding = hold;
                if (hold) GscraftWar.LOG.info("[gscraft] {} holds fire: an ally in the line to {}", v.getName().getString(), target.getName().getString());
            }
            // the mod fires at the mob's target, and the laid turret fires at the aim target by itself: a hold clears both
            if (hold) clearAim(v);
            else aim(v);
        }
        if (ticks % RETARGET_TICKS == 0) {
            LivingEntity better = pick(v);
            if (better != null && better != target && score(v, better) > score(v, target) + 0.5D) {
                target = better;
                crew.engaged = target;
                lost = 0;
                if (!crew.gunner()) chooseWeapon(v);
                if (!holding) aim(v);
            }
        }
        if (!crew.gunner() && ticks % 20 == 0 && shouldRetreat(v)) {
            crew.startRetreat(crew.level().getGameTime(), target.position());
        }
    }

    private void clearAim(Entity v) {
        crew.setTarget(null);
        if (crew.gunner()) Vehicles.setPassengerWeaponTarget(v, null);
        else Vehicles.setTurretTarget(v, null);
    }

    private void aim(Entity v) {
        if (crew.gunner()) Vehicles.setPassengerWeaponTarget(v, target.getUUID());
        else Vehicles.setTurretTarget(v, target.getUUID());
        if (!holding) crew.setTarget(target);
    }

    private boolean shouldRetreat(Entity v) {
        float health = Vehicles.health(v);
        float max = Vehicles.maxHealth(v);
        boolean engine = Vehicles.data(v, "MAIN_ENGINE_DAMAGED", false);
        boolean turret = Vehicles.data(v, "TURRET_DAMAGED", false);
        if (engine) return false;   // cannot move: a pillbox
        return (!Float.isNaN(health) && !Float.isNaN(max) && health < max * RETREAT_SHARE) || turret;
    }

    /** the weapon: always the seat's first (the cannon). The APC's missile has a magazine of one and the mod only
     *  reloads a magazine for a player, so a crew that chose it fired once and then sat laid on its target for good
     *  (owner 2026-09-12: "the APCs seem not to engage each other"). The cannon feeds from the container. */
    private void chooseWeapon(Entity v) {
        int seat = Vehicles.seatIndex(v, crew);
        if (seat < 0) return;
        List<String> weapons = Vehicles.seatWeapons(v, seat);
        if (weapons == null || weapons.isEmpty()) return;
        if (Vehicles.selectedWeapon(v, seat) != 0) Vehicles.changeWeapon(v, seat, 0);
    }

    // ---- choosing

    /** armour 3, players 2, fighters with heavy weapons 1.5, the rest 1; nearer first within a class */
    private double score(Entity v, LivingEntity e) {
        double base;
        if (e instanceof Crew) base = 3.0D;
        else if (e instanceof Player) base = 2.0D;
        else if (e instanceof GunUser g && (g.role() == Role.GUNNER || g.role() == Role.MARKSMAN)) base = 1.5D;
        else base = 1.0D;
        return base + Math.max(0.0D, 1.0D - v.distanceTo(e) / ENGAGE) * 0.4D;
    }

    /** the best-scored hostile in range, in the cone (or known), with a line from the turret */
    private LivingEntity pick(Entity v) {
        if (!(crew.level() instanceof ServerLevel level)) return null;
        long now = level.getGameTime();
        boolean allRound = crew.alertUntil > now;
        double half = (crew.gunner() ? VIEW_CONE_GUNNER : VIEW_CONE_DRIVER) * 0.5D;
        LivingEntity best = null;
        double bestScore = -1.0D;
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, v.getBoundingBox().inflate(ENGAGE), e -> e != crew && valid(v, e))) {
            if (v.distanceTo(e) > ENGAGE) continue;
            if (!allRound && !Armour.engagedBy(v, e) && !inCone(v, e, half)) continue;
            if (!sees(v, e)) continue;
            double s = score(v, e);
            if (s > bestScore) {
                bestScore = s;
                best = e;
            }
        }
        return best;
    }

    private boolean valid(Entity v, LivingEntity e) {
        if (!e.isAlive() || e == crew || e.getVehicle() == v) return false;
        if (e instanceof Player p) {
            if (p.isSpectator() || p.isCreative()) return false;
            return Factions.hostileToPlayer(crew, p);
        }
        if (e instanceof Crew c && c.vehicle() == null) return false;
        return e instanceof Mob && Factions.hostile(crew, e);
    }

    /** the threat's bearing against the hull's heading */
    private static boolean inCone(Entity v, LivingEntity e, double halfDegrees) {
        double dx = e.getX() - v.getX();
        double dz = e.getZ() - v.getZ();
        if (dx * dx + dz * dz < 4.0D) return true;
        float bearing = (float) Math.toDegrees(Math.atan2(-dx, dz));
        return Math.abs(Mth.wrapDegrees(bearing - v.getYRot())) <= halfDegrees;
    }

    private static Vec3 turret(Entity v) {
        return v.position().add(0.0D, 2.2D, 0.0D);
    }

    private boolean sees(Entity v, LivingEntity e) {
        Vec3 from = turret(v);
        Vec3 to = e instanceof Crew c && c.vehicle() != null ? c.vehicle().position().add(0.0D, 1.5D, 0.0D) : e.getEyePosition();
        HitResult hit = v.level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, v));
        return hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(to) < 1.5D;
    }

    /** a faction ally standing within the radius of the line between the turret and the target and short of it */
    private boolean allyInLine(Entity v, LivingEntity t) {
        Vec3 from = turret(v);
        Vec3 to = t.getEyePosition();
        Vec3 line = to.subtract(from);
        double len = line.length();
        if (len < 1.0D) return false;
        Vec3 dir = line.scale(1.0D / len);
        for (Entity e : v.level().getEntities(v, v.getBoundingBox().inflate(len), e -> e != t && e.isAlive() && e instanceof Mob m && Factions.allied(crew, m) && !(m instanceof Crew))) {
            Vec3 p = e.position().add(0.0D, e.getBbHeight() * 0.5D, 0.0D).subtract(from);
            double along = p.dot(dir);
            if (along < 0.0D || along > len) continue;
            double off = p.subtract(dir.scale(along)).length();
            if (off < FRIENDLY_RADIUS + e.getBbWidth() * 0.5D) return true;
        }
        return false;
    }
}
