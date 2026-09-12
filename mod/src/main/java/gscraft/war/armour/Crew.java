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
    /** a hit on the vehicle: the crew looks all round until this tick */
    public long alertUntil;
    /** what this crew engages, for the other crew of the same vehicle */
    public net.minecraft.world.entity.LivingEntity engaged;
    private float lastHealth = Float.NaN;
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
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;
        Entity v = vehicle();
        if (v == null || Vehicles.wreck(v)) {
            if (++unseated > GRACE || (v != null && Vehicles.wreck(v))) {
                GscraftWar.LOG.info("[gscraft] crew of {} gone: {}", v == null ? "nothing" : v.getName().getString(), v == null ? "no vehicle" : "wreck");
                discard();
            }
        } else {
            unseated = 0;
            float h = Vehicles.health(v);
            if (!Float.isNaN(lastHealth) && h < lastHealth - 0.01F) alertUntil = level().getGameTime() + FightGoal.ALERT_TICKS;
            lastHealth = h;
        }
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
