package gscraft.war.faction;

/** How a faction treats players. */
public enum PlayerStance {
    /** attacks players on sight (the armies, the Dead) */
    HOSTILE,
    /** never targets players (the camp) */
    NEUTRAL,
    /** ignores players until one of them strikes a member of the band (the Scavengers) */
    PROVOKED
}
