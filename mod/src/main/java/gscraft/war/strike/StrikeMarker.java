package gscraft.war.strike;

import gscraft.war.GscraftWar;
import gscraft.war.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Vector3f;

import java.util.Locale;

/**
 * The strike grenade in flight and, landed, the smoke that marks the target until the rounds come. Landing makes
 * the call ({@link Strikes#call}); a refused call drops the grenade back on the ground.
 */
public class StrikeMarker extends ThrowableItemProjectile {
    private Strikes.Kind kind = Strikes.Kind.MORTAR;
    private boolean landed;
    private int smoke;

    public StrikeMarker(EntityType<? extends ThrowableItemProjectile> type, Level level) {
        super(type, level);
    }

    public StrikeMarker(Level level, LivingEntity shooter) {
        super(ModEntities.STRIKE_MARKER.get(), shooter, level);
    }

    public void setKind(Strikes.Kind k) {
        kind = k;
    }

    @Override
    protected Item getDefaultItem() {
        Item it = ForgeRegistries.ITEMS.getValue(new ResourceLocation(GscraftWar.MODID, "strike_" + kind.name().toLowerCase(Locale.ROOT)));
        return it == null ? Items.SNOWBALL : it;
    }

    @Override
    protected void onHitBlock(BlockHitResult hit) {
        land(hit.getBlockPos().relative(hit.getDirection()));
    }

    @Override
    protected void onHitEntity(EntityHitResult hit) {
        land(hit.getEntity().blockPosition());
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
    }

    private void land(BlockPos at) {
        if (level().isClientSide || landed) return;
        landed = true;
        setDeltaMovement(0, 0, 0);
        setNoGravity(true);
        setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
        ServerPlayer owner = getOwner() instanceof ServerPlayer p ? p : null;
        String refused = Strikes.call((ServerLevel) level(), kind, at, owner);
        if (refused != null) {
            if (owner != null) owner.displayClientMessage(Component.literal(refused), true);
            level().addFreshEntity(new ItemEntity(level(), getX(), getY() + 0.5, getZ(), getItem().copy()));
            discard();
            return;
        }
        smoke = switch (kind) {
            case MORTAR -> Strikes.MORTAR_DELAY + 80 + Strikes.MORTAR_BARRAGE * Strikes.MORTAR_GAP;
            case ARTILLERY -> Strikes.ARTY_DELAY + 100 + Strikes.ARTY_BARRAGE * Strikes.ARTY_GAP;
            case AIR -> Strikes.AIR_DELAY + 300;
        };
    }

    @Override
    public void tick() {
        if (!landed) {
            super.tick();
            return;
        }
        if (!(level() instanceof ServerLevel sl)) return;
        if (tickCount % 2 == 0) {
            Vector3f colour = switch (kind) {
                case MORTAR -> new Vector3f(1.0f, 0.45f, 0.1f);
                case ARTILLERY -> new Vector3f(1.0f, 0.1f, 0.1f);
                case AIR -> new Vector3f(0.7f, 0.2f, 0.9f);
            };
            sl.sendParticles(new DustParticleOptions(colour, 2.0f), getX(), getY() + 0.6, getZ(), 4, 0.35, 0.9, 0.35, 0.02);
            if (tickCount % 6 == 0) sl.sendParticles(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, getX(), getY() + 0.4, getZ(), 1, 0.15, 0.1, 0.15, 0.01);
        }
        if (--smoke <= 0) discard();
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putString("Kind", kind.name());
        tag.putBoolean("Landed", landed);
        tag.putInt("Smoke", smoke);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        try {
            kind = Strikes.Kind.valueOf(tag.getString("Kind"));
        } catch (IllegalArgumentException ignored) {
            kind = Strikes.Kind.MORTAR;
        }
        landed = tag.getBoolean("Landed");
        smoke = tag.getInt("Smoke");
    }
}
