package gscraft.war.entity;

import net.minecraft.world.phys.Vec3;

/** A fighter that goes to look when it hears a shot it has no target for. */
public interface Hearing {
    void hear(Vec3 pos);
}
