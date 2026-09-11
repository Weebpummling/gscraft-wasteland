package gscraft.war.entity;

import com.tacz.guns.api.item.IGun;
import gscraft.war.faction.FactionMember;
import gscraft.war.faction.Factions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
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
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;

/**
 * A soldier on a player-shaped body. HumanoidModel plus HumanoidArmorLayer is the reason this class exists: the
 * illagers the factions stood up as before carry no armour layer, so every kit was invisible. A Monster on
 * purpose: turrets, guards and recruits already treat monsters as the enemy, and the armies are.
 */
public class Soldier extends Monster implements FactionMember, Skinned, GunUser, Hearing, Homed {
    private static final EntityDataAccessor<Integer> SKIN =
            SynchedEntityData.defineId(Soldier.class, EntityDataSerializers.INT);

    private final String faction;
    private final FighterState state = new FighterState(Role.RIFLEMAN);
    private InvestigateGoal investigate;

    public Soldier(EntityType<? extends Soldier> type, Level level, String faction) {
        super(type, level);
        setMaxUpStep(1.0F);
        if (getNavigation() instanceof GroundPathNavigation ground) {
            ground.setCanOpenDoors(true);
            ground.setCanPassDoors(true);
        }
        this.faction = faction;
        this.xpReward = 5;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 24.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FOLLOW_RANGE, 48.0D)
                .add(Attributes.ATTACK_DAMAGE, 3.0D);
    }

    @Override
    public String factionId() {
        return faction;
    }

    @Override
    public int skin() {
        return entityData.get(SKIN);
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
        goalSelector.addGoal(2, new GunAttackGoal(this, 1.0D));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.1D, false) {
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
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 16.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));

        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                p -> Factions.hostileToPlayer(this, (Player) p)));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
                e -> Factions.hostile(this, e)));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        state.decaySuppression();
        if (state.role == Role.SERGEANT && tickCount % 20 == 0) Fighters.callTarget(this);
    }

    /** Never turn on your own side, even after a stray round. */
    @Override
    public boolean canAttack(LivingEntity target) {
        if (Factions.allied(this, target)) return false;
        return super.canAttack(target);
    }

    /** Friendly fire does nothing: rounds from your own faction pass without harm. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getEntity() != null && Factions.allied(this, source.getEntity())) return false;
        return super.hurt(source, amount);
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
        // /summon with any NBT skips finalizeSpawn, so a soldier that arrived that way dresses on its first tick
        if (!level().isClientSide && !state.kitIssued) issueKit();
    }

    @Override
    public FighterState fighterState() {
        return state;
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
        RankDef rank = Kit.issue(this, faction, random, state.rank);
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
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        state.load(tag);
        state.applyHome(this);
        entityData.set(SKIN, tag.getInt("GscraftSkin"));
    }
}
