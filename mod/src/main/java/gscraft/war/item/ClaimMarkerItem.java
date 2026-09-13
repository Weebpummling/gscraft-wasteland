package gscraft.war.item;

import gscraft.war.survivor.Say;
import gscraft.war.world.Loop;
import gscraft.war.world.Sites;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Marshall's claim marker (map-design §6.1, interface §3 site ladder): used on the ground inside a strongpoint it
 * starts the assault - the banner stands at the site's anchor and must survive, with a player inside at the end.
 * Refused, in Marshall's words, on a site that is not looted or while another is contested; the marker stays in the hand.
 */
public class ClaimMarkerItem extends SliceItems.SliceItem {
    public ClaimMarkerItem(SliceItems.Def def) {
        super(def);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        Level level = ctx.getLevel();
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (!(ctx.getPlayer() instanceof ServerPlayer p) || !(level instanceof ServerLevel sl)) return InteractionResult.PASS;
        BlockPos at = ctx.getClickedPos();
        Sites.SiteDef site = null;
        for (Sites.SiteDef s : Sites.all().values()) {
            if (!s.building() && s.contains(at.getX(), at.getZ())) {
                site = s;
                break;
            }
        }
        if (site == null) {
            Say.queue(p, "marshall", "nobody", true);
            return InteractionResult.FAIL;
        }
        String msg = Loop.claim(sl, site);
        if (msg.contains("the assault begins")) {
            ctx.getItemInHand().shrink(1);
            Say.queue(p, "marshall", "marker_set", true);
            return InteractionResult.CONSUME;
        }
        Say.queue(p, "marshall", "marker_refused", true);
        p.displayClientMessage(Component.literal(msg), true);
        return InteractionResult.FAIL;
    }
}
