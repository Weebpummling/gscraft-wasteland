package gscraft.war.client;

import gscraft.war.entity.Soldier;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.resources.ResourceLocation;

/** HumanoidMobRenderer plus the armour layer the illager renderers never had. */
public class SoldierRenderer extends HumanoidMobRenderer<Soldier, SoldierModel> {
    // vanilla's default player skins, referenced where they already are; nothing is copied into the mod
    private static final String[] NAMES = {"steve", "alex", "ari", "efe", "kai", "makena", "noor", "sunny", "zuri"};
    private static final ResourceLocation[] SKINS = new ResourceLocation[NAMES.length];

    static {
        for (int i = 0; i < NAMES.length; i++) {
            SKINS[i] = new ResourceLocation("minecraft", "textures/entity/player/wide/" + NAMES[i] + ".png");
        }
    }

    public SoldierRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new SoldierModel(ctx.bakeLayer(ModelLayers.PLAYER)), 0.5F);
        addLayer(new HumanoidArmorLayer<>(this,
                new HumanoidModel<Soldier>(ctx.bakeLayer(ModelLayers.PLAYER_INNER_ARMOR)),
                new HumanoidModel<Soldier>(ctx.bakeLayer(ModelLayers.PLAYER_OUTER_ARMOR)),
                ctx.getModelManager()));
    }

    @Override
    public ResourceLocation getTextureLocation(Soldier e) {
        return SKINS[Math.floorMod(e.skin(), SKINS.length)];
    }
}
