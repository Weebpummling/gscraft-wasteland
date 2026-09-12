package gscraft.war.client;

import dev.kosmx.playerAnim.api.layered.IAnimation;
import dev.kosmx.playerAnim.api.layered.KeyframeAnimationPlayer;
import dev.kosmx.playerAnim.api.layered.ModifierLayer;
import dev.kosmx.playerAnim.api.layered.modifier.AbstractFadeModifier;
import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import dev.kosmx.playerAnim.core.util.Ease;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationFactory;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;
import gscraft.war.GscraftWar;
import gscraft.war.entity.Anim;
import gscraft.war.entity.Animated;
import net.minecraft.resources.ResourceLocation;

import java.util.HashMap;
import java.util.Map;

/**
 * Our own clips on a fighter's stand-in (animation research §4, A2): one PlayerAnimator layer above TACZ's four,
 * fed from the fighter's synced {@link Anim} byte. A clip moves only the bones it names, so TACZ's gun handling
 * stays on the rest; a one-shot blends back into whatever pose is under it over six ticks.
 */
public final class FighterAnims {
    public static final ResourceLocation LAYER = new ResourceLocation(GscraftWar.MODID, "tactical");
    /** TACZ registers 93-96 (lower, loop upper, once upper, rotation); a higher number is applied after them */
    private static final int PRIORITY = 97;
    private static final int BLEND_OUT_TICKS = 6;
    private static final Map<Anim, KeyframeAnimation> CLIPS = new HashMap<>();

    private FighterAnims() {}

    /** at client setup, before any stand-in exists: every player-shaped entity gets the layer, empty until used */
    public static void register() {
        PlayerAnimationFactory.ANIMATION_DATA_FACTORY.registerFactory(LAYER, PRIORITY, player -> player instanceof FighterProxy ? new ModifierLayer<>() : null);
    }

    /** once a client tick per stand-in: the fighter's byte, played when it changes */
    public static void tick(FighterProxy p) {
        if (!(p.link instanceof Animated a)) return;
        int packed = a.animByte();
        if (packed == p.lastAnim) return;
        boolean first = p.lastAnim < 0;
        p.lastAnim = packed;
        Anim anim = Anim.unpack(packed);
        if (first && !anim.loop) return;   // seen for the first time: a one-shot from before is not replayed
        IAnimation raw = PlayerAnimationAccess.getPlayerAssociatedData(p).get(LAYER);
        if (!(raw instanceof ModifierLayer<?> found)) return;
        @SuppressWarnings("unchecked")
        ModifierLayer<IAnimation> layer = (ModifierLayer<IAnimation>) found;
        if (anim == Anim.NONE) {
            if (layer.isActive()) layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(BLEND_OUT_TICKS, Ease.INOUTSINE), null);
            return;
        }
        KeyframeAnimation clip = clip(anim);
        if (clip == null) return;
        layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(anim.loop ? 6 : 3, Ease.INOUTSINE), new KeyframeAnimationPlayer(clip));
    }

    /** the registered clip, its stop a few ticks past its end so a one-shot eases back instead of snapping */
    private static KeyframeAnimation clip(Anim anim) {
        KeyframeAnimation cached = CLIPS.get(anim);
        if (cached != null) return cached;
        KeyframeAnimation base = PlayerAnimationRegistry.getAnimation(new ResourceLocation(GscraftWar.MODID, anim.clip()));
        if (base == null) {
            GscraftWar.LOG.warn("[gscraft] no clip for {} (assets/gscraft/player_animation)", anim);
            return null;
        }
        KeyframeAnimation clip = base;
        if (!anim.loop) {
            KeyframeAnimation.AnimationBuilder b = base.mutableCopy();
            b.stopTick = b.endTick + BLEND_OUT_TICKS;
            clip = b.build();
        }
        CLIPS.put(anim, clip);
        return clip;
    }

    /** on a resource reload the clips are read again */
    public static void clear() {
        CLIPS.clear();
    }
}
