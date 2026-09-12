package gscraft.war.client;

import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

/** Nothing to draw: the crew is inside the vehicle. */
public class NoopRenderer<T extends Entity> extends EntityRenderer<T> {
    private static final ResourceLocation NOTHING = new ResourceLocation("minecraft", "textures/misc/white.png");

    public NoopRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public boolean shouldRender(T entity, net.minecraft.client.renderer.culling.Frustum frustum, double x, double y, double z) {
        return false;
    }

    @Override
    public ResourceLocation getTextureLocation(T entity) {
        return NOTHING;
    }
}
