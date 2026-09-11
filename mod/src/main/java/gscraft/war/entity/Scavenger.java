package gscraft.war.entity;

import com.tacz.guns.api.item.IGun;
import gscraft.war.faction.FactionMember;
import gscraft.war.faction.Factions;
import gscraft.war.faction.Grudging;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.OpenDoorGoal;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * The Scavengers are people, not raiders (owner, 2026-09-09): they fight the Dead and leave a player alone until
 * that player strikes one of them. Deliberately not a Monster, so Superb Warfare's turrets and the camp's guards,
 * which hunt monsters, pass them by.
 *
 * A strike is remembered by the whole band, not only the one who was hit: every Scavenger within 24 blocks takes
 * the grudge, and keeps it through a save. Team standing (review W1) builds on this in a later phase.
 */
public class Scavenger extends PathfinderMob implements FactionMember, Skinned, Grudging, GunUser, Hearing, Homed {
    public static final String FACTION = "scavengers";
    private static final double BAND_RADIUS = 24.0D;
    private static final EntityDataAccessor<Integer> SKIN =
            SynchedEntityData.defineId(Scavenger.class, EntityDataSerializers.INT);

    private final Set<UUID> grudges = new HashSet<>();
    private GunAttackGoal gunGoal;
    private final FighterState state = new FighterState(Role.SCAVENGER);
    private InvestigateGoal investigate;

    public Scavenger(EntityType<? extends Scavenger> type, Level level) {
        super(type, level);
        setMaxUpStep(1.0F);
        if (getNavigation() instanceof GroundPathNavigation ground) {
            ground.setCanOpenDoors(true);
            ground.setCanPassDoors(true);
        }
        this.xpReward = 3;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FOLLOW_RANGE, 40.0D)
                .add(Attributes.ATTACK_DAMAGE, 2.0D);
    }

    @Override
    public String factionId() {
        return FACTION;
    }

    @Override
    public int skin() {
        return entityData.get(SKIN);
    }

    @Override
    public boolean holdsGrudge(UUID player) {
        return grudges.contains(player);
    }

    public void addGrudge(UUID player) {
        grudges.add(player);
    }

    @Override
    public Role role() {
        return state.role;
    }

    @Override
    public boolean takeMagazine() {
        if (state.magazines <= 0) return false;
        state.magazines--;
        return true;
    }

    @Override
    public boolean outOfAmmo() {
        return state.outOfAmmo;
    }

    @Override
    public void markOutOfAmmo() {
        state.outOfAmmo = true;
    }

    @Override
    public void setHome(BlockPos post, int radius) {
        state.home = post;
        state.homeRadius = radius;
        state.applyHome(this);
    }

    @Override
    public void hear(Vec3 pos) {
        if (investigate != null) investigate.hear(pos);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(SKIN, 0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new OpenDoorGoal(this, true));
        goalSelector.addGoal(1, new GrenadeGoal(this));
        gunGoal = new GunAttackGoal(this, 1.0D);
        goalSelector.addGoal(2, gunGoal);
        goalSelector.addGoal(4, new OrderGoal(this));
        goalSelector.addGoal(5, new PatrolGoal(this));
        goalSelector.addGoal(5, new SquadFollowGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.15D, false) {
            @Override
            public boolean canUse() {
                return (!IGun.mainHandHoldGun(mob) || state.outOfAmmo) && super.canUse();
            }
        });
        // assigned here, not at the field: Mob's constructor calls registerGoals before field initialisers run
        investigate = new InvestigateGoal(this);
        goalSelector.addGoal(5, investigate);
        goalSelector.addGoal(6, new MoveTowardsRestrictionGoal(this, 1.0D));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 12.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));

        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                p -> Factions.hostileToPlayer(this, (Player) p)));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
                e -> Factions.hostile(this, e)));
        // a target out of sight for fifteen seconds is still the target: cover means not seeing it (feasibility B1)
        targetSelector.getAvailableGoals().forEach(w -> {
            if (w.getGoal() instanceof NearestAttackableTargetGoal<?> g) g.setUnseenMemoryTicks(300);
        });
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (Factions.allied(this, target)) return false;
        return super.canAttack(target);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getEntity() != null && Factions.allied(this, source.getEntity())) return false;
        boolean hit = super.hurt(source, amount);
        if (hit && !level().isClientSide && source.getEntity() instanceof Player player) {
            for (Scavenger s : level().getEntitiesOfClass(Scavenger.class, getBoundingBox().inflate(BAND_RADIUS))) {
                s.addGrudge(player.getUUID());
            }
        }
        return hit;
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data, @Nullable CompoundTag tag) {
        SpawnGroupData result = super.finalizeSpawn(level, difficulty, reason, data, tag);
        if (!state.kitIssued) issueKit();
        return result;
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide) state.decaySuppression();
        if (!level().isClientSide && tickCount % 20 == 10) Squad.leaderTick(this);
        if (!level().isClientSide && !state.kitIssued) issueKit();
    }

    @Override
    public FighterState fighterState() {
        return state;
    }

    /** the cover the gun goal holds, for the readout */
    public Cover.Spot cover() {
        return gunGoal == null ? null : gunGoal.cover();
    }

    /** crouched and flat stances (feasibility A3): the box follows the pose the way a player's does */
    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return switch (pose) {
            case CROUCHING -> EntityDimensions.scalable(0.6F, 1.5F);
            case SWIMMING -> EntityDimensions.scalable(0.6F, 0.6F);
            default -> super.getDimensions(pose);
        };
    }

    /** the rank to issue on the first tick, for a wave or a test */
    public void pinRank(String rank) {
        state.rank = rank;
        state.kitIssued = false;
    }

    private void issueKit() {
        entityData.set(SKIN, random.nextInt(SKIN_COUNT));
        RankDef rank = Kit.issue(this, FACTION, random, state.rank);
        if (rank != null) {
            state.apply(rank);
            setCustomName(Component.literal(rank.name()));
        } else {
            state.kitIssued = true;
        }
        for (EquipmentSlot slot : EquipmentSlot.values()) setDropChance(slot, 0.0F);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        state.save(tag);
        tag.putInt("GscraftSkin", skin());
        ListTag list = new ListTag();
        for (UUID id : grudges) list.add(NbtUtils.createUUID(id));
        tag.put("GscraftGrudges", list);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        state.load(tag);
        state.applyHome(this);
        entityData.set(SKIN, tag.getInt("GscraftSkin"));
        grudges.clear();
        for (Tag t : tag.getList("GscraftGrudges", Tag.TAG_INT_ARRAY)) grudges.add(NbtUtils.loadUUID(t));
    }
}
