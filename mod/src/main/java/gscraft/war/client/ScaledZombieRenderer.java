package gscraft.war.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.monster.Zombie;

/** A zombie or husk drawn larger than life: the Bloater at 1.4, the Matron at 1.5. */
public class ScaledZombieRenderer extends ZombieRenderer {
    private static final ResourceLocation HUSK = new ResourceLocation("minecraft", "textures/entity/zombie/husk.png");

    private final float scale;
    private final boolean husk;

    public ScaledZombieRenderer(EntityRendererProvider.Context ctx, float scale, boolean husk) {
        super(ctx);
        this.scale = scale;
        this.husk = husk;
        this.shadowRadius *= scale;
    }

    @Override
    protected void scale(Zombie entity, PoseStack pose, float partialTick) {
        pose.scale(scale, scale, scale);
    }

    @Override
    public ResourceLocation getTextureLocation(Zombie entity) {
        return husk ? HUSK : super.getTextureLocation(entity);
    }
}
