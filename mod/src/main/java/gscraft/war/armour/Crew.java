package gscraft.war.armour;

import gscraft.war.GscraftWar;
import gscraft.war.faction.FactionMember;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * The crew of a Superb Warfare vehicle (armour design §2, V2/V3): an invisible, silent, unhittable mob that rides
 * a seat and works the vehicle. The vehicle only drives, aims and fires with a mob in the seat (§9), and the mod's
 * own tick fires a seat's weapon at the mob's target once the turret is laid, so the crew's goals choose targets,
 * halt, choose the weapon and withdraw; the mod does the rest. The driver sits in seat 0 and drives; a gunner (on
 * a tank with a commander's station) sits in that station's seat and only fights. It is a faction member like a
 * Soldier, so targeting, hearing, the hold and the sweep already know it; it dies with the vehicle and never
 * otherwise.
 */
public class Crew extends Mob implements FactionMember {
    private static final EntityDataAccessor<String> FACTION = SynchedEntityData.defineId(Crew.class, EntityDataSerializers.STRING);
    private static final EntityDataAccessor<Boolean> GUNNER = SynchedEntityData.defineId(Crew.class, EntityDataSerializers.BOOLEAN);
    /** ticks without a vehicle under it before it is gone (a dismount by anything but us is a bug, not a state) */
    private static final int GRACE = 40;

    /** the route the drive goal follows, looped; empty = sit */
    public final List<BlockPos> route = new ArrayList<>();
    public int routeIndex;
    /** the retreat: driving away from the threat until this tick, then no fighting until calmUntil */
    public long retreatUntil;
    public long calmUntil;
    public Vec3 threat;
    /** the infantry that walks with the vehicle (V5): ordered along behind it by the driver */
    public final List<java.util.UUID> escorts = new ArrayList<>();
    public static double ESCORT_BEHIND = 8.0D;
    /** a hit on the vehicle: the crew looks all round until this tick */
    public long alertUntil;
    /** what this crew engages, for the other crew of the same vehicle */
    public net.minecraft.world.entity.LivingEntity engaged;
    private float lastHealth = Float.NaN;
    private boolean[] partsSeen;
    private boolean wreckSeen;
    private net.minecraft.network.chat.Component vehicleName;
    private net.minecraft.network.chat.Component attackerName;
    private boolean goneReported;
    private int unseated;

    public Crew(EntityType<? extends Crew> type, Level level) {
        super(type, level);
        setInvisible(true);
        setInvulnerable(true);
        setSilent(true);
        setPersistenceRequired();
        noPhysics = true;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.0D)
                .add(Attributes.FOLLOW_RANGE, 64.0D);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(FACTION, "");
        entityData.define(GUNNER, false);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new RetreatGoal(this));
        goalSelector.addGoal(1, new FightGoal(this));
        goalSelector.addGoal(2, new DriveGoal(this));
    }

    public void setFaction(String faction) {
        entityData.set(FACTION, faction);
    }

    @Override
    public String factionId() {
        String f = entityData.get(FACTION);
        return f.isEmpty() ? null : f;
    }

    public boolean gunner() {
        return entityData.get(GUNNER);
    }

    public void setGunner(boolean gunner) {
        entityData.set(GUNNER, gunner);
        goalSelector.removeAllGoals(g -> true);
        registerGoals();
    }

    /** the vehicle under it, or null */
    public Entity vehicle() {
        Entity v = getVehicle();
        return v != null && Vehicles.isVehicle(v) ? v : null;
    }

    public boolean retreating(long now) {
        return now < retreatUntil;
    }

    public boolean calm(long now) {
        return now < calmUntil;
    }

    public void startRetreat(long now, Vec3 from) {
        retreatUntil = now + FightGoal.RETREAT_TICKS;
        calmUntil = retreatUntil + FightGoal.CALM_TICKS;
        threat = from;
        Entity v = vehicle();
        GscraftWar.LOG.info("[gscraft] {} withdraws ({} health)", v == null ? "crew" : v.getName().getString(), v == null ? "?" : String.format("%.0f", Vehicles.health(v)));
        if (v != null) Reports.withdrawing(v);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;
        Entity v = vehicle();
        if (v == null && !gunner() && vehicleName != null && !goneReported) {
            // an overkill removes the vehicle in the same tick, before any wreck flag: the loss is the report
            goneReported = true;
            Reports.destroyed((net.minecraft.server.level.ServerLevel) level(), position(), vehicleName, attackerName);
        }
        if (v == null || Vehicles.wreck(v)) {
            if (++unseated > GRACE || (v != null && Vehicles.wreck(v) && wreckSeen)) {
                GscraftWar.LOG.info("[gscraft] crew of {} gone: {}", v == null ? "nothing" : v.getName().getString(), v == null ? "no vehicle" : "wreck");
                discard();
            }
        } else {
            unseated = 0;
            float h = Vehicles.health(v);
            if (!Float.isNaN(lastHealth) && h < lastHealth - 0.01F) alertUntil = level().getGameTime() + FightGoal.ALERT_TICKS;
            lastHealth = h;
        }
        if (!gunner() && v != null && tickCount % 40 == 0) escortTick(v);
        if (!gunner() && v != null) {
            vehicleName = v.getDisplayName();
            Entity attacker = Reports.lastAttacker(v);
            if (attacker != null) attackerName = attacker.getDisplayName();
            if (Vehicles.wreck(v)) goneReported = true;   // the wreck report below covers it
            boolean[] parts = {Vehicles.data(v, "TURRET_DAMAGED", false), Vehicles.data(v, "MAIN_ENGINE_DAMAGED", false),
                    Vehicles.data(v, "L_WHEEL_DAMAGED", false), Vehicles.data(v, "R_WHEEL_DAMAGED", false)};
            boolean wreck = Vehicles.wreck(v);
            if (partsSeen != null) Reports.tick(this, v, partsSeen, parts, wreckSeen, wreck);
            partsSeen = parts;
            wreckSeen = wreck;
        }
    }

    /** how far the slowest living escort is behind the vehicle; 0 with no escort */
    public double escortLag(Entity v) {
        if (escorts.isEmpty() || !(level() instanceof net.minecraft.server.level.ServerLevel level)) return 0.0D;
        double worst = 0.0D;
        for (java.util.UUID id : escorts) {
            Entity e = level.getEntity(id);
            if (e != null && e.isAlive()) worst = Math.max(worst, e.distanceTo(v));
        }
        return worst;
    }

    /** the escort's order: along behind the moving vehicle; free to fight (and take cover) when it halts to fight */
    private void escortTick(Entity v) {
        if (escorts.isEmpty() || !(level() instanceof net.minecraft.server.level.ServerLevel level)) return;
        boolean moving = engaged == null && !route.isEmpty();
        double yaw = Math.toRadians(v.getYRot());
        BlockPos behind = BlockPos.containing(v.getX() + Math.sin(yaw) * ESCORT_BEHIND, v.getY(), v.getZ() - Math.cos(yaw) * ESCORT_BEHIND);
        java.util.Iterator<java.util.UUID> it = escorts.iterator();
        while (it.hasNext()) {
            Entity e = level.getEntity(it.next());
            if (!(e instanceof Mob m) || !m.isAlive() || !(m instanceof gscraft.war.entity.GunUser g)) {
                it.remove();
                continue;
            }
            gscraft.war.entity.FighterState s = g.fighterState();
            if (moving) {
                if (m.distanceToSqr(v) > 4.0D * 4.0D) {
                    s.order = gscraft.war.entity.FighterState.Order.ADVANCE;
                    s.orderPos = behind;
                    s.orderBySquad = true;
                }
            } else if (s.orderBySquad && s.order != gscraft.war.entity.FighterState.Order.NONE) {
                s.order = gscraft.war.entity.FighterState.Order.NONE;
            }
        }
    }

    /** swept by the director (a discard, not a death): the vehicle goes with its driver; a wreck stays as loot */
    @Override
    public void remove(RemovalReason reason) {
        if (reason == RemovalReason.DISCARDED && !gunner() && !level().isClientSide) {
            Entity v = vehicle();
            if (v != null && !Vehicles.wreck(v)) {
                Reports.dropBar(v);
                for (Entity p : new ArrayList<>(v.getPassengers())) if (p != this) p.discard();
                v.discard();
            }
        }
        super.remove(reason);
    }

    // ---- never hit, never seen, never pushed

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return false;
    }

    @Override
    public boolean isInvulnerableTo(DamageSource source) {
        return true;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean canBeCollidedWith() {
        return false;
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(0.2F, 0.2F);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putString("GscraftFaction", entityData.get(FACTION));
        tag.putBoolean("GscraftGunner", gunner());
        ListTag list = new ListTag();
        for (BlockPos p : route) list.add(NbtUtils.writeBlockPos(p));
        tag.put("GscraftRoute", list);
        tag.putInt("GscraftRouteIndex", routeIndex);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(FACTION, tag.getString("GscraftFaction"));
        setGunner(tag.getBoolean("GscraftGunner"));
        route.clear();
        for (Tag t : tag.getList("GscraftRoute", Tag.TAG_COMPOUND)) route.add(NbtUtils.readBlockPos((CompoundTag) t));
        routeIndex = tag.getInt("GscraftRouteIndex");
    }
}
