package gscraft.war.client;

import com.tacz.guns.api.item.IGun;
import gscraft.war.entity.Soldier;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;

/** The player model, with a two-handed rifle hold while the soldier is fighting. */
public class SoldierModel extends PlayerModel<Soldier> {
    public SoldierModel(ModelPart root) {
        super(root, false);
    }

    @Override
    public void setupAnim(Soldier e, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
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
