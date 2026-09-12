package gscraft.war.client;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import gscraft.war.GscraftWar;
import gscraft.war.entity.Skinned;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Draws a fighter as its player stand-in ({@link FighterProxy}): every frame the stand-in is moved onto the
 * fighter - position, both rotations, pose, sprint, crouch, the hurt and death timers - and handed to a player
 * renderer. Falls back to the mob renderer if the stand-in cannot be made. The stand-ins are ticked once a client
 * tick for their walk cycle and their animation layers, and dropped when the fighter is gone.
 */
public class FighterProxyRenderer<T extends Mob & Skinned> extends FighterRenderer<T> {
    /** -Dgscraft.proxy=false draws the old mob renderer, for comparison */
    public static final boolean ENABLED = !"false".equals(System.getProperty("gscraft.proxy"));
    private static final Map<Integer, FighterProxy> PROXIES = new HashMap<>();
    private final ProxyPlayerRenderer player;

    public FighterProxyRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        player = new ProxyPlayerRenderer(ctx);
    }

    @Override
    public void render(T fighter, float yaw, float partialTick, PoseStack pose, MultiBufferSource buffer, int light) {
        FighterProxy proxy = ENABLED ? proxy(fighter) : null;
        if (proxy == null) {
            super.render(fighter, yaw, partialTick, pose, buffer, light);
            return;
        }
        follow(proxy, fighter);
        player.render(proxy, yaw, partialTick, pose, buffer, light);
    }

    private FighterProxy proxy(T fighter) {
        FighterProxy p = PROXIES.get(fighter.getId());
        if (p != null && p.link == fighter) return p;
        try {
            p = new FighterProxy(Minecraft.getInstance().level, fighter);
        } catch (RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] no stand-in for {}: {}", fighter.getName().getString(), ex.toString());
            return null;
        }
        PROXIES.put(fighter.getId(), p);
        return p;
    }

    /** the stand-in takes the fighter's place for this frame */
    private static void follow(FighterProxy p, Mob f) {
        p.xo = f.xo;
        p.yo = f.yo;
        p.zo = f.zo;
        p.setPos(f.getX(), f.getY(), f.getZ());
        p.xRotO = f.xRotO;
        p.yRotO = f.yRotO;
        p.setXRot(f.getXRot());
        p.setYRot(f.getYRot());
        p.yBodyRot = f.yBodyRot;
        p.yBodyRotO = f.yBodyRotO;
        p.yHeadRot = f.yHeadRot;
        p.yHeadRotO = f.yHeadRotO;
        p.tickCount = f.tickCount;
        p.hurtTime = f.hurtTime;
        p.hurtDuration = f.hurtDuration;
        p.deathTime = f.deathTime;
        p.setHealth(f.getHealth());
        p.setPose(f.getPose());
        p.setShiftKeyDown(f.isShiftKeyDown() || f.getPose() == net.minecraft.world.entity.Pose.CROUCHING);
        p.setSprinting(f.isSprinting());
        p.setOnGround(f.onGround());
        p.swinging = f.swinging;
        p.swingTime = f.swingTime;
        p.swingingArm = f.swingingArm;
        p.setDeltaMovement(f.getDeltaMovement());
    }

    /** once a client tick: the walk cycle from the fighter's own, the animation layers, the dead dropped */
    @Mod.EventBusSubscriber(modid = GscraftWar.MODID, value = Dist.CLIENT)
    public static final class Tick {
        private Tick() {}

        @SubscribeEvent
        public static void tick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END || PROXIES.isEmpty()) return;
            Iterator<Map.Entry<Integer, FighterProxy>> it = PROXIES.entrySet().iterator();
            while (it.hasNext()) {
                FighterProxy p = it.next().getValue();
                Mob f = p.link;
                if (f.isRemoved() || Minecraft.getInstance().level != f.level()) {
                    it.remove();
                    continue;
                }
                p.walkAnimation.update(f.walkAnimation.speed(), 0.4F);
                try {
                    FighterAnims.tick(p);
                    PlayerAnimationAccess.getPlayerAnimLayer(p).tick();
                } catch (RuntimeException ignored) {
                    // no animation data on this stand-in: the vanilla poses still draw
                }
            }
        }
    }

    /** the vanilla player renderer, with the fighter's skin and no name tag */
    private static final class ProxyPlayerRenderer extends PlayerRenderer {
        ProxyPlayerRenderer(EntityRendererProvider.Context ctx) {
            super(ctx, false);
        }

        @Override
        public ResourceLocation getTextureLocation(AbstractClientPlayer player) {
            return player instanceof FighterProxy p ? p.getSkinTextureLocation() : super.getTextureLocation(player);
        }

        @Override
        protected boolean shouldShowName(AbstractClientPlayer player) {
            return false;
        }

        @Override
        protected void renderNameTag(AbstractClientPlayer player, Component name, PoseStack pose, MultiBufferSource buffer, int light) {
        }
    }
}
