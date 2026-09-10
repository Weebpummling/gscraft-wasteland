package gscraft.war.entity;

import gscraft.war.WarEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Husk;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

import javax.annotation.Nullable;

/**
 * The Matron (enemies §5, entities-v8 §6, review W6): the Skadowsky hospital's named horror, the first named enemy a
 * team meets. Half again the size of the Dead around her, slow and hard to put down; she calls her brood to her in a
 * fight, and the air near her drags at the legs. She keeps the hospital as a lair until the site's take is built
 * (review phase 6), when she moves to its fifth wave.
 *
 * Rendered at 1.5 times a husk's size; her hitbox stays within a two-block doorway so the hospital's corridors are
 * still hers.
 */
public class Matron extends Husk {
    public static final float RENDER_SCALE = 1.5F;
    private static final String BROOD_TAG = "gs_brood";
    private static final int BROOD_CAP = 6;
    private static final double BAR_RANGE = 32.0D;

    private final ServerBossEvent bar = new ServerBossEvent(Component.literal("The Matron"),
            BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.PROGRESS);

    public Matron(EntityType<? extends Husk> type, Level level) {
        super(type, level);
        this.xpReward = 40;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Zombie.createAttributes()
                .add(Attributes.MAX_HEALTH, 90.0D)
                .add(Attributes.ATTACK_DAMAGE, 7.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.21D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8D)
                .add(Attributes.FOLLOW_RANGE, 40.0D);
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
        setCustomName(Component.literal("The Matron"));
        return result;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (tickCount % 20 == 0) updateBar();
        if (tickCount % 40 == 0) {
            for (Player p : level().getEntitiesOfClass(Player.class, getBoundingBox().inflate(6.0D))) {
                if (!p.isCreative() && !p.isSpectator()) p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
            }
        }
        LivingEntity target = getTarget();
        if (target != null && target.isAlive() && tickCount % 300 == 0) callBrood(target);
    }

    /** two of the Dead rise beside her, up to six at a time */
    private void callBrood(LivingEntity target) {
        ServerLevel level = (ServerLevel) level();
        int brood = level.getEntitiesOfClass(Zombie.class, getBoundingBox().inflate(24.0D),
                z -> z.getTags().contains(BROOD_TAG)).size();
        for (int i = brood; i < Math.min(BROOD_CAP, brood + 2); i++) {
            Zombie z = EntityType.ZOMBIE.create(level);
            if (z == null) continue;
            z.moveTo(getX() + (random.nextDouble() - 0.5D) * 4.0D, getY(), getZ() + (random.nextDouble() - 0.5D) * 4.0D,
                    random.nextFloat() * 360.0F, 0.0F);
            z.addTag(WarEvents.PLACED_TAG);
            z.addTag(BROOD_TAG);
            for (EquipmentSlot slot : EquipmentSlot.values()) z.setDropChance(slot, 0.0F);
            z.setTarget(target);
            level.addFreshEntity(z);
        }
        playSound(SoundEvents.ZOMBIE_VILLAGER_CURE, 2.0F, 0.5F);
    }

    private void updateBar() {
        bar.setProgress(Math.max(0.0F, getHealth() / getMaxHealth()));
        for (ServerPlayer p : java.util.List.copyOf(bar.getPlayers())) {
            if (!p.isAlive() || p.distanceToSqr(this) > BAR_RANGE * BAR_RANGE) bar.removePlayer(p);
        }
        for (ServerPlayer p : ((ServerLevel) level()).getPlayers(p -> p.distanceToSqr(this) <= BAR_RANGE * BAR_RANGE)) {
            bar.addPlayer(p);
        }
    }

    @Override
    public void remove(RemovalReason reason) {
        bar.removeAllPlayers();
        super.remove(reason);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        bar.removePlayer(player);
    }
}
