package gscraft.war.client;

import com.tacz.guns.api.item.IGun;
import gscraft.war.entity.Skinned;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.world.entity.Mob;

/** The player model, with a two-handed rifle hold while the fighter is in a fight. */
public class FighterModel<T extends Mob & Skinned> extends PlayerModel<T> {
    public FighterModel(ModelPart root) {
        super(root, false);
    }

    @Override
    public void setupAnim(T e, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        if (IGun.mainHandHoldGun(e) && e.isAggressive()) {
            rightArmPose = ArmPose.CROSSBOW_HOLD;
            leftArmPose = ArmPose.CROSSBOW_HOLD;
        } else {
            rightArmPose = e.getMainHandItem().isEmpty() ? ArmPose.EMPTY : ArmPose.ITEM;
            leftArmPose = e.getOffhandItem().isEmpty() ? ArmPose.EMPTY : ArmPose.ITEM;
        }
        super.setupAnim(e, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
    }
}
