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
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

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
public class Scavenger extends PathfinderMob implements FactionMember, Skinned, Grudging {
    public static final String FACTION = "scavengers";
    private static final double BAND_RADIUS = 24.0D;
    private static final EntityDataAccessor<Integer> SKIN =
            SynchedEntityData.defineId(Scavenger.class, EntityDataSerializers.INT);

    private final Set<UUID> grudges = new HashSet<>();
    private boolean kitIssued;

    public Scavenger(EntityType<? extends Scavenger> type, Level level) {
        super(type, level);
        this.xpReward = 3;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 20.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FOLLOW_RANGE, 32.0D)
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
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(SKIN, 0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new GunAttackGoal(this, 1.0D, 30.0F));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.15D, false) {
            @Override
            public boolean canUse() {
                return !IGun.mainHandHoldGun(mob) && super.canUse();
            }
        });
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 12.0F));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));

        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                p -> Factions.hostileToPlayer(this, (Player) p)));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
                e -> Factions.hostile(this, e)));
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
        issueKit();
        return result;
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide && !kitIssued) issueKit();
    }

    private void issueKit() {
        entityData.set(SKIN, random.nextInt(SKIN_COUNT));
        setCustomName(Component.literal(Kit.issue(this, FACTION, random)));
        for (EquipmentSlot slot : EquipmentSlot.values()) setDropChance(slot, 0.0F);
        kitIssued = true;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("GscraftKitIssued", kitIssued);
        tag.putInt("GscraftSkin", skin());
        ListTag list = new ListTag();
        for (UUID id : grudges) list.add(NbtUtils.createUUID(id));
        tag.put("GscraftGrudges", list);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        kitIssued = tag.getBoolean("GscraftKitIssued");
        entityData.set(SKIN, tag.getInt("GscraftSkin"));
        grudges.clear();
        for (Tag t : tag.getList("GscraftGrudges", Tag.TAG_INT_ARRAY)) grudges.add(NbtUtils.loadUUID(t));
    }
}
