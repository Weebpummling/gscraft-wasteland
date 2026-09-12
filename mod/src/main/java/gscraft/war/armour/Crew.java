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

import java.util.ArrayList;
import java.util.List;

/**
 * The crew of a Superb Warfare vehicle (armour design §2, V2): an invisible, silent, unhittable mob that rides the
 * driver's seat and writes the vehicle's inputs. The vehicle only drives, aims and fires with a mob in that seat
 * (§9), so this is the passenger the mod wants. It is a faction member like a Soldier, so targeting, hearing, the
 * hold and the sweep already know it; it dies with the vehicle and never otherwise.
 */
public class Crew extends Mob implements FactionMember {
    private static final EntityDataAccessor<String> FACTION = SynchedEntityData.defineId(Crew.class, EntityDataSerializers.STRING);
    /** ticks without a vehicle under it before it is gone (a dismount by anything but us is a bug, not a state) */
    private static final int GRACE = 40;

    /** the route the drive goal follows, looped; empty = sit */
    public final List<BlockPos> route = new ArrayList<>();
    public int routeIndex;
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
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new DriveGoal(this));
    }

    public void setFaction(String faction) {
        entityData.set(FACTION, faction);
    }

    @Override
    public String factionId() {
        String f = entityData.get(FACTION);
        return f.isEmpty() ? null : f;
    }

    /** the vehicle under it, or null */
    public Entity vehicle() {
        Entity v = getVehicle();
        return v != null && Vehicles.isVehicle(v) ? v : null;
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
        ListTag list = new ListTag();
        for (BlockPos p : route) list.add(NbtUtils.writeBlockPos(p));
        tag.put("GscraftRoute", list);
        tag.putInt("GscraftRouteIndex", routeIndex);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(FACTION, tag.getString("GscraftFaction"));
        route.clear();
        for (Tag t : tag.getList("GscraftRoute", Tag.TAG_COMPOUND)) route.add(NbtUtils.readBlockPos((CompoundTag) t));
        routeIndex = tag.getInt("GscraftRouteIndex");
    }
}
