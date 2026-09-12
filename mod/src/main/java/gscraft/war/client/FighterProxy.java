package gscraft.war.client;

import com.mojang.authlib.GameProfile;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.entity.ReloadState;
import com.tacz.guns.api.entity.ShootResult;
import com.tacz.guns.entity.shooter.ShooterDataHolder;
import com.tacz.guns.resource.modifier.AttachmentCacheProperty;
import gscraft.war.entity.Skinned;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.RemotePlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.PlayerModelPart;
import net.minecraft.world.item.ItemStack;

import java.util.function.Supplier;

/**
 * A fighter's stand-in on the client: a player-shaped entity that is never in the world, only drawn in the
 * fighter's place (after TACZ: Npcs, MIT). TACZ animates guns in third person on a player - the shouldered
 * rifle, the aim, the reload and the sprint from every gun pack's PlayerAnimator clips - and PlayerAnimator itself
 * only animates players; a mob gets the vanilla arm pose. Drawn as a player, the fighter gets all of it, and our
 * own clips ride the same body. Every gun state TACZ asks a player for is answered from the linked fighter, which
 * TACZ already syncs (its living-entity tick covers every living entity, not only players).
 */
public class FighterProxy extends RemotePlayer implements IGunOperator {
    public final Mob link;
    /** the last animation byte played, -1 before the first look */
    public int lastAnim = -1;

    public <T extends Mob & Skinned> FighterProxy(ClientLevel level, T link) {
        super(level, new GameProfile(link.getUUID(), "fighter"));
        this.link = link;
    }

    private IGunOperator op() {
        return IGunOperator.fromLivingEntity(link);
    }

    // ---- what the renderer reads as a player

    @Override
    public boolean isModelPartShown(PlayerModelPart part) {
        return true;
    }

    @Override
    public ResourceLocation getSkinTextureLocation() {
        return FighterRenderer.skin(link, ((Skinned) link).skin());
    }

    @Override
    public String getModelName() {
        return "default";
    }

    @Override
    public boolean shouldShowName() {
        return false;
    }

    @Override
    public Component getDisplayName() {
        return link.getDisplayName();
    }

    @Override
    public Component getName() {
        return link.getName();
    }

    @Override
    public float getSwimAmount(float partialTick) {
        return link.getSwimAmount(partialTick);   // the fighter ticks its own; the stand-in is never ticked
    }

    @Override
    public float getAttackAnim(float partialTick) {
        return link.getAttackAnim(partialTick);
    }

    @Override
    public ItemStack getItemBySlot(EquipmentSlot slot) {
        return link.getItemBySlot(slot);
    }

    @Override
    public ItemStack getMainHandItem() {
        return link.getMainHandItem();
    }

    @Override
    public ItemStack getOffhandItem() {
        return link.getOffhandItem();
    }

    @Override
    public boolean isInvisible() {
        return link.isInvisible();
    }

    @Override
    public boolean isSpectator() {
        return false;
    }

    @Override
    public boolean isCreative() {
        return false;
    }

    // ---- what TACZ asks a player: answered from the fighter, whose state TACZ syncs itself

    @Override
    public long getSynShootCoolDown() {
        return op().getSynShootCoolDown();
    }

    @Override
    public long getSynMeleeCoolDown() {
        return op().getSynMeleeCoolDown();
    }

    @Override
    public long getSynDrawCoolDown() {
        return op().getSynDrawCoolDown();
    }

    @Override
    public boolean getSynIsBolting() {
        return op().getSynIsBolting();
    }

    @Override
    public ReloadState getSynReloadState() {
        return op().getSynReloadState();
    }

    @Override
    public float getSynAimingProgress() {
        return op().getSynAimingProgress();
    }

    @Override
    public boolean getSynIsAiming() {
        return op().getSynIsAiming();
    }

    @Override
    public float getSynSprintTime() {
        return op().getSynSprintTime();
    }

    @Override
    public boolean needCheckAmmo() {
        return op().needCheckAmmo();
    }

    @Override
    public boolean consumesAmmoOrNot() {
        return op().consumesAmmoOrNot();
    }

    @Override
    public boolean getProcessedSprintStatus(boolean sprinting) {
        return op().getProcessedSprintStatus(sprinting);
    }

    @Override
    public AttachmentCacheProperty getCacheProperty() {
        return op().getCacheProperty();
    }

    @Override
    public ShooterDataHolder getDataHolder() {
        return op().getDataHolder();
    }

    @Override
    public boolean nextBulletIsTracer(int interval) {
        return op().nextBulletIsTracer(interval);
    }

    // ---- a stand-in does nothing of its own

    @Override
    public void initialData() {
    }

    @Override
    public void draw(Supplier<ItemStack> gun) {
    }

    @Override
    public void bolt() {
    }

    @Override
    public void reload() {
    }

    @Override
    public void cancelReload() {
    }

    @Override
    public void fireSelect() {
    }

    @Override
    public void zoom() {
    }

    @Override
    public void melee() {
    }

    @Override
    public ShootResult shoot(Supplier<Float> pitch, Supplier<Float> yaw) {
        return ShootResult.UNKNOWN_FAIL;
    }

    @Override
    public ShootResult shoot(Supplier<Float> pitch, Supplier<Float> yaw, long timestamp) {
        return ShootResult.UNKNOWN_FAIL;
    }

    @Override
    public void aim(boolean aiming) {
    }

    @Override
    public void crawl(boolean crawling) {
    }

    @Override
    public void updateCacheProperty(AttachmentCacheProperty property) {
    }
}
