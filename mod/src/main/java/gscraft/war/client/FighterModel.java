package gscraft.war.client;

import com.tacz.guns.api.item.IGun;
import gscraft.war.entity.Skinned;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Items;

/** The player model: a two-handed rifle hold in a fight, and a raised shield when the Shield rank blocks. */
public class FighterModel<T extends Mob & Skinned> extends PlayerModel<T> {
    public FighterModel(ModelPart root) {
        super(root, false);
    }

    @Override
    public void setupAnim(T e, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        boolean blocking = e.isUsingItem() && e.getUsedItemHand() == InteractionHand.OFF_HAND
                && e.getOffhandItem().is(Items.SHIELD);
        if (IGun.mainHandHoldGun(e) && e.isAggressive() && !blocking) {
            rightArmPose = ArmPose.CROSSBOW_HOLD;
            leftArmPose = ArmPose.CROSSBOW_HOLD;
        } else {
            rightArmPose = e.getMainHandItem().isEmpty() ? ArmPose.EMPTY : ArmPose.ITEM;
            leftArmPose = blocking ? ArmPose.BLOCK : (e.getOffhandItem().isEmpty() ? ArmPose.EMPTY : ArmPose.ITEM);
        }
        super.setupAnim(e, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
    }
}
