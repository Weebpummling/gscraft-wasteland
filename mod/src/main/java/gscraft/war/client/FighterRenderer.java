package gscraft.war.client;

import gscraft.war.entity.Skinned;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** HumanoidMobRenderer plus the armour layer the illager renderers never had. Soldiers and Scavengers alike. */
public class FighterRenderer<T extends Mob & Skinned> extends HumanoidMobRenderer<T, FighterModel<T>> {
    // vanilla's default player skins, referenced where they already are; nothing is copied into the mod
    private static final String[] NAMES = {"steve", "alex", "ari", "efe", "kai", "makena", "noor", "sunny", "zuri"};
    private static final ResourceLocation[] SKINS = new ResourceLocation[NAMES.length];

    static {
        for (int i = 0; i < NAMES.length; i++) {
            SKINS[i] = new ResourceLocation("minecraft", "textures/entity/player/wide/" + NAMES[i] + ".png");
        }
    }

    public FighterRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new FighterModel<>(ctx.bakeLayer(ModelLayers.PLAYER)), 0.5F);
        addLayer(new HumanoidArmorLayer<>(this,
                new HumanoidModel<T>(ctx.bakeLayer(ModelLayers.PLAYER_INNER_ARMOR)),
                new HumanoidModel<T>(ctx.bakeLayer(ModelLayers.PLAYER_OUTER_ARMOR)),
                ctx.getModelManager()));
    }

    /** a body in the flat pose lies down: the player renderer does this, the mob renderer never did */
    @Override
    protected void setupRotations(T entity, com.mojang.blaze3d.vertex.PoseStack pose, float ageInTicks, float yaw, float partialTick) {
        super.setupRotations(entity, pose, ageInTicks, yaw, partialTick);
        float swim = entity.getSwimAmount(partialTick);
        if (swim > 0.0F) {
            float xRot = entity.isInWater() ? -90.0F - entity.getXRot() : -90.0F;
            pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(net.minecraft.util.Mth.lerp(swim, 0.0F, xRot)));
            if (entity.isVisuallySwimming()) pose.translate(0.0F, -1.0F, 0.3F);
        }
    }

    public static ResourceLocation skin(int index) {
        return SKINS[Math.floorMod(index, SKINS.length)];
    }

    /** the faction's uniform (assets/gscraft/textures/entity/skin/<faction>_<n>.png, made by tools/make_skins.py); vanilla's for a faction without one */
    public static ResourceLocation skin(Mob mob, int index) {
        String faction = mob instanceof gscraft.war.faction.FactionMember m ? m.factionId() : null;
        ResourceLocation own = faction == null ? null : UNIFORMS.get(faction);
        if (own == null) return skin(index);
        return new ResourceLocation(own.getNamespace(), own.getPath() + "_" + Math.floorMod(index, Skinned.SKIN_COUNT) + ".png");
    }

    private static final java.util.Map<String, ResourceLocation> UNIFORMS = java.util.Map.of(
            "nato", new ResourceLocation(gscraft.war.GscraftWar.MODID, "textures/entity/skin/nato"),
            "ruaf", new ResourceLocation(gscraft.war.GscraftWar.MODID, "textures/entity/skin/ruaf"),
            "scavengers", new ResourceLocation(gscraft.war.GscraftWar.MODID, "textures/entity/skin/scav"));

    @Override
    public ResourceLocation getTextureLocation(T e) {
        return skin(e, e.skin());
    }
}
