package gscraft.war.faction;

import java.util.UUID;

/** A member of a {@link PlayerStance#PROVOKED} faction that remembers which players struck its band. */
public interface Grudging {
    boolean holdsGrudge(UUID player);
}
