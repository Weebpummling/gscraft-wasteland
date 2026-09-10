package gscraft.war.entity;

import net.minecraft.core.BlockPos;

/** A fighter bound to a post: it stays within the radius of home, and the binding survives a save. */
public interface Homed {
    void setHome(BlockPos home, int radius);
}
