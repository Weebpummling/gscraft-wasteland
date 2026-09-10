package gscraft.war.entity;

import com.tacz.guns.api.item.IGun;
import gscraft.war.Faction;
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
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

import javax.annotation.Nullable;

/**
 * A soldier on a player-shaped body. HumanoidModel plus HumanoidArmorLayer is the reason this class exists:
 * the illagers the factions stood up as before carry no armour layer, so every kit was invisible.
 */
public class Soldier extends Monster {
    private static final EntityDataAccessor<Integer> SKIN =
            SynchedEntityData.defineId(Soldier.class, EntityDataSerializers.INT);
    public static final int SKIN_COUNT = 9;

    private final Faction faction;
    private boolean kitIssued;

    public Soldier(EntityType<? extends Soldier> type, Level level, Faction faction) {
        super(type, level);
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

    public Faction faction() {
        return faction;
    }

    public int skin() {
        return entityData.get(SKIN);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(SKIN, 0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new GunAttackGoal(this, 1.0D, 40.0F));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.1D, false) {
            @Override
            public boolean canUse() {
                return !IGun.mainHandHoldGun(mob) && super.canUse();
            }
        });
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 16.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));

        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Soldier.class, 10, true, false,
                e -> e instanceof Soldier s && faction.hostileTo(s.faction())));
        targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Zombie.class, true));
    }

    /** Never turn on your own side, even after a stray round. */
    @Override
    public boolean canAttack(LivingEntity target) {
        if (target instanceof Soldier s && !faction.hostileTo(s.faction())) return false;
        return super.canAttack(target);
    }

    /** Friendly fire does nothing: rounds from your own faction pass without harm. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getEntity() instanceof Soldier s && !faction.hostileTo(s.faction())) return false;
        return super.hurt(source, amount);
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data, @Nullable CompoundTag tag) {
        SpawnGroupData result = super.finalizeSpawn(level, difficulty, reason, data, tag);
        issueKit();
        return result;
    }

    @Override
    public void tick() {
        super.tick();
        // /summon with any NBT skips finalizeSpawn, so a soldier that arrived that way dresses on its first tick
        if (!level().isClientSide && !kitIssued) issueKit();
    }

    private void issueKit() {
        entityData.set(SKIN, random.nextInt(SKIN_COUNT));
        setCustomName(Component.literal(Kit.issue(this, faction, random)));
        for (EquipmentSlot slot : EquipmentSlot.values()) setDropChance(slot, 0.0F);
        kitIssued = true;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("GscraftKitIssued", kitIssued);
        tag.putInt("GscraftSkin", skin());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        kitIssued = tag.getBoolean("GscraftKitIssued");
        entityData.set(SKIN, tag.getInt("GscraftSkin"));
    }
}
