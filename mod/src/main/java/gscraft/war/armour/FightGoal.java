package gscraft.war.armour;

import gscraft.war.GscraftWar;
import gscraft.war.faction.Factions;
import net.minecraft.server.level.ServerLevel;
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
 * The crew fights (armour design §2, V3). It picks the nearest hostile in range with a line from the turret, gives
 * it to the mod as the turret's (or the commander's station's) target and as its own mob target: the mod lays the
 * turret and fires the seat's weapon once it is within four degrees. The driver halts the hull to shoot and picks
 * the weapon - a missile for armour where the seat has one, the cannon for everything else. Fire is held while an
 * ally stands in the line. Below the retreat share of health, or with the turret and the engine both gone, the
 * driver withdraws (the retreat goal); an engine that is gone means it sits and fights as a pillbox.
 */
public class FightGoal extends Goal {
    public static double ENGAGE = 64.0D;
    public static int LOST_TICKS = 100;
    public static double FRIENDLY_RADIUS = 2.5D;
    public static float RETREAT_SHARE = 0.33F;
    public static int RETREAT_TICKS = 200;
    public static int CALM_TICKS = 600;
    private static final String NONE = "undefined";

    private final Crew crew;
    private LivingEntity target;
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
        if (v == null) return false;
        long now = crew.level().getGameTime();
        if (!crew.gunner() && (crew.retreating(now) || crew.calm(now))) return false;
        target = pick(v);
        return target != null;
    }

    @Override
    public boolean canContinueToUse() {
        Entity v = crew.vehicle();
        return v != null && target != null && target.isAlive() && lost < LOST_TICKS && v.distanceTo(target) < ENGAGE * 1.25D
                && !(crew.gunner() ? false : crew.retreating(crew.level().getGameTime()));
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
        if (!crew.gunner()) {
            Vehicles.allStop(v);   // halt to shoot
            chooseWeapon(v);
        }
        aim(v);
        GscraftWar.LOG.info("[gscraft] {} ({}) engages {} at {} blocks", v.getName().getString(), crew.gunner() ? "gunner" : "driver", target.getName().getString(), Math.round(v.distanceTo(target)));
    }

    @Override
    public void stop() {
        Entity v = crew.vehicle();
        crew.setTarget(null);
        if (v != null) {
            if (crew.gunner()) Vehicles.setData(v, "AI_PASSENGER_WEAPON_TARGET_UUID", NONE);
            else Vehicles.setData(v, "AI_TURRET_TARGET_UUID", NONE);
        }
        target = null;
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
                GscraftWar.LOG.info("[gscraft] {} ({}) {}: an ally {} the line to {}", v.getName().getString(), crew.gunner() ? "gunner" : "driver", hold ? "holds fire" : "resumes fire", hold ? "in" : "out of", target.getName().getString());
            }
            if (gscraft.war.combat.Damage.DEBUG > 0 && ticks % 20 == 0) {
                GscraftWar.LOG.info("[gscraft] {} ({}) fight tick {}: hold {}, mob target {}, aim '{}'", v.getName().getString(), crew.gunner() ? "gunner" : "driver", ticks, hold,
                        crew.getTarget() == null ? "none" : crew.getTarget().getName().getString(), crew.gunner() ? Vehicles.data(v, "AI_PASSENGER_WEAPON_TARGET_UUID", "?") : Vehicles.turretTarget(v));
            }
            // the mod fires at the mob's target, and the laid turret fires at the aim target by itself: a hold clears both
            if (hold) clearAim(v);
            else aim(v);
        }
        if (ticks % 20 == 0 && !holding) aim(v);
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

    /** the weapon for the target: a missile for armour where the seat has one, else the first (the cannon) */
    private void chooseWeapon(Entity v) {
        int seat = Vehicles.seatIndex(v, crew);
        if (seat < 0) return;
        List<String> weapons = Vehicles.seatWeapons(v, seat);
        if (weapons == null || weapons.isEmpty()) return;
        boolean armour = target instanceof Crew;
        int want = 0;
        if (armour) {
            for (int i = 0; i < weapons.size(); i++) if (weapons.get(i).toLowerCase().contains("missile")) want = i;
        }
        if (Vehicles.selectedWeapon(v, seat) != want) Vehicles.changeWeapon(v, seat, want);
    }

    /** the nearest hostile in range with a line from the turret */
    private LivingEntity pick(Entity v) {
        if (!(crew.level() instanceof ServerLevel level)) return null;
        LivingEntity best = null;
        double bestD = Double.MAX_VALUE;
        List<LivingEntity> near = level.getEntitiesOfClass(LivingEntity.class, v.getBoundingBox().inflate(ENGAGE), e -> e != crew);
        int ok = 0;
        int seen = 0;
        for (LivingEntity e : near) {
            if (!valid(v, e)) continue;
            ok++;
            double d = e.distanceToSqr(v);
            if (!sees(v, e)) continue;
            seen++;
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        if (gscraft.war.combat.Damage.DEBUG > 0 && crew.tickCount % 40 == 0) {
            GscraftWar.LOG.info("[gscraft] {} ({}) pick: {} living within {}, {} hostile, {} in sight, faction {}, best {}", v.getName().getString(), crew.gunner() ? "gunner" : "driver",
                    near.size(), ENGAGE, ok, seen, crew.factionId(), best == null ? "none" : best.getName().getString());
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

    private static Vec3 turret(Entity v) {
        return v.position().add(0.0D, 2.2D, 0.0D);
    }

    private boolean sees(Entity v, LivingEntity e) {
        Vec3 from = turret(v);
        Vec3 to = e instanceof Crew c && c.vehicle() != null ? c.vehicle().position().add(0.0D, 1.5D, 0.0D) : e.getEyePosition();
        HitResult hit = v.level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, v));
        boolean clear = hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(to) < 1.5D;
        if (!clear && gscraft.war.combat.Damage.DEBUG > 0 && crew.tickCount % 40 == 0) {
            GscraftWar.LOG.info("[gscraft] {} sight to {} blocked at {} (from {} to {}): {}", v.getName().getString(), e.getName().getString(), hit.getLocation(), from, to,
                    hit instanceof net.minecraft.world.phys.BlockHitResult b ? v.level().getBlockState(b.getBlockPos()).getBlock().getName().getString() + " " + b.getBlockPos().toShortString() : hit.getType());
        }
        return clear;
    }

    /** a faction ally, or a vehicle of ours, standing within the radius of the line between the turret and the target and short of it */
    private boolean allyInLine(Entity v, LivingEntity t) {
        Vec3 from = turret(v);
        Vec3 to = t.getEyePosition();
        Vec3 line = to.subtract(from);
        double len = line.length();
        if (len < 1.0D) return false;
        Vec3 dir = line.scale(1.0D / len);
        for (Entity e : v.level().getEntities(v, v.getBoundingBox().inflate(len), e -> e != t && e.isAlive() && (e instanceof Mob m && Factions.allied(crew, m) && !(m instanceof Crew)) )) {
            Vec3 p = e.position().add(0.0D, e.getBbHeight() * 0.5D, 0.0D).subtract(from);
            double along = p.dot(dir);
            if (along < 0.0D || along > len) continue;
            double off = p.subtract(dir.scale(along)).length();
            if (off < FRIENDLY_RADIUS + e.getBbWidth() * 0.5D) return true;
        }
        return false;
    }
}
