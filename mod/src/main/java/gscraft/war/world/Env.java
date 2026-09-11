package gscraft.war.world;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.common.Tags;

/**
 * Where a creature stands, read from what is over its head, and how thickly the director fills that kind of ground
 * (owner, 2026-09-10: thinner and further out in the open, denser inside buildings and underground).
 *
 * Rock or earth overhead is underground, and so is a built ceiling with three or more blocks of rock or earth
 * over it (a bunker, a tunnel, a cellar dug into a hill); anything else solid is a building; nothing solid for 24 blocks is open
 * ground. Leaves and logs are looked through, so the Woods' canopy does not read as a roof.
 *
 * @param capScale  multiplies a zone's cap
 * @param minR,maxR how far from the player a placement lands
 * @param countBox,countY the box the cap is counted in; only creatures on the same kind of ground count, so a
 *                  bunker under a street no longer starves the street and the street no longer starves the bunker
 * @param dyUp,dyDown how far above and below the player's feet standing room is looked for, nearest first
 */
public enum Env {
    OPEN(1.0D, 36, 72, 80, 12, 6, 16),
    INDOOR(1.5D, 6, 24, 28, 6, 4, 4),
    UNDERGROUND(1.5D, 6, 24, 28, 8, 6, 8);

    private static final int LOOK_UP = 24;
    private static final int DEEP_OPEN_BELOW = 48;
    /** how far over a built ceiling earth is looked for, and how much of it makes the room buried */
    private static final int LOOK_BURIED = 48;
    private static final int BURIED = 3;

    public final double capScale;
    public final int minR;
    public final int maxR;
    public final int countBox;
    public final int countY;
    public final int dyUp;
    public final int dyDown;

    Env(double capScale, int minR, int maxR, int countBox, int countY, int dyUp, int dyDown) {
        this.capScale = capScale;
        this.minR = minR;
        this.maxR = maxR;
        this.countBox = countBox;
        this.countY = countY;
        this.dyUp = dyUp;
        this.dyDown = dyDown;
    }

    public static Env at(ServerLevel level, BlockPos feet) {
        BlockPos.MutableBlockPos p = feet.above(2).mutable();
        for (int i = 0; i < LOOK_UP; i++, p.move(Direction.UP)) {
            if (!level.isInWorldBounds(p)) break;
            BlockState s = level.getBlockState(p);
            if (s.isAir() || s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS) || s.getCollisionShape(level, p).isEmpty()) {
                continue;
            }
            if (natural(s)) return UNDERGROUND;
            // a built ceiling with earth or rock over it is a bunker or a tunnel, not a building
            return buried(level, p.immutable()) ? UNDERGROUND : INDOOR;
        }
        // nothing overhead for 24 blocks: open sky, unless this is a tall cavity well below the ground surface
        int surface = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, feet.getX(), feet.getZ());
        if (surface - feet.getY() > LOOK_UP) return feet.getY() < DEEP_OPEN_BELOW ? UNDERGROUND : INDOOR;
        return OPEN;
    }

    /** at least BURIED natural blocks between a built ceiling and the ground surface above it */
    private static boolean buried(ServerLevel level, BlockPos ceiling) {
        int surface = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ceiling.getX(), ceiling.getZ());
        int top = Math.min(surface, ceiling.getY() + LOOK_BURIED);
        int n = 0;
        BlockPos.MutableBlockPos p = ceiling.mutable();
        for (int y = ceiling.getY() + 1; y < top; y++) {
            p.setY(y);
            if (natural(level.getBlockState(p)) && ++n >= BURIED) return true;
        }
        return false;
    }

    private static boolean natural(BlockState s) {
        return s.is(BlockTags.BASE_STONE_OVERWORLD) || s.is(BlockTags.DIRT) || s.is(BlockTags.SAND)
                || s.is(Blocks.GRAVEL) || s.is(Blocks.CLAY) || s.is(Tags.Blocks.ORES) || s.is(Blocks.BEDROCK);
    }
}
