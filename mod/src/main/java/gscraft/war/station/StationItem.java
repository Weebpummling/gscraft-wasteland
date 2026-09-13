package gscraft.war.station;

import gscraft.war.world.SiteData;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.Block;

import java.util.UUID;

/** the station as an item: one per player - a second cannot be placed while the first stands (crafting §4) */
public class StationItem extends BlockItem {
    public StationItem(Block block, Properties props) {
        super(block, props);
    }

    @Override
    public InteractionResult place(BlockPlaceContext ctx) {
        Player p = ctx.getPlayer();
        if (p != null && ctx.getLevel() instanceof ServerLevel sl) {
            BlockPos have = standing(sl, p.getUUID());
            if (have != null) {
                p.displayClientMessage(Component.literal("your station stands at " + have.getX() + " " + have.getY() + " " + have.getZ()), true);
                return InteractionResult.FAIL;
            }
        }
        return super.place(ctx);
    }

    /** where the player's station stands, or null; a record whose block is gone is dropped */
    public static BlockPos standing(ServerLevel level, UUID owner) {
        SiteData data = SiteData.get(level);
        BlockPos pos = data.station(owner);
        if (pos == null) return null;
        if (!level.hasChunkAt(pos)) return pos;   // unloaded: trusted
        if (level.getBlockEntity(pos) instanceof StationBlockEntity st && owner.equals(st.owner)) return pos;
        data.unbindStation(owner, pos);
        return null;
    }
}
