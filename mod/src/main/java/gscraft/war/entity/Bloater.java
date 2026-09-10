package gscraft.war.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

import javax.annotation.Nullable;

/**
 * The Bloater (enemies §3.1, review W6): one of the Dead gone to bloat - three times the health, slow, and it dies
 * loudly, bursting into a cloud that poisons and turns the stomach of whoever stood close. It is the Anchor of the
 * Dead's waves: it forces a team to commit. Act III ground (the plant).
 *
 * It renders 1.4 times the size of a zombie, as designed, but its hitbox stays within a two-block doorway so it can
 * still come through the plant's doors; In Control's sizemultiply could never do even the first half of this.
 */
public class Bloater extends Zombie {
    public static final float RENDER_SCALE = 1.4F;

    public Bloater(EntityType<? extends Zombie> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Zombie.createAttributes()
                .add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.17D)
                .add(Attributes.ATTACK_DAMAGE, 5.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D);
    }

    @Override
    protected boolean isSunSensitive() {
        return false;
    }

    @Override
    protected boolean convertsInWater() {
        return false;
    }

    @Override
    public boolean isBaby() {
        return false;
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data, @Nullable CompoundTag tag) {
        SpawnGroupData result = super.finalizeSpawn(level, difficulty, reason, new Zombie.ZombieGroupData(false, false), tag);
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            setItemSlot(slot, ItemStack.EMPTY);
            setDropChance(slot, 0.0F);
        }
        setCustomName(Component.literal("Bloater"));
        return result;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (!level().isClientSide) burst();
    }

    private void burst() {
        AreaEffectCloud cloud = new AreaEffectCloud(level(), getX(), getY() + 0.5D, getZ());
        cloud.setRadius(3.5F);
        cloud.setWaitTime(5);
        cloud.setDuration(120);
        cloud.setRadiusPerTick(-cloud.getRadius() / cloud.getDuration());
        cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0));
        cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 160, 0));
        level().addFreshEntity(cloud);
        level().playSound(null, getX(), getY(), getZ(), SoundEvents.SLIME_DEATH, getSoundSource(), 2.5F, 0.4F);
        for (LivingEntity near : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(3.0D), e -> e != this)) {
            near.knockback(0.8D, getX() - near.getX(), getZ() - near.getZ());
        }
    }
}
