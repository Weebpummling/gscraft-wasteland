package gscraft.war;

/** Who stands with whom. Phase 2 moves the relations into datapack JSON; for now, two armies at war. */
public enum Faction {
    NATO,
    RUAF;

    public boolean hostileTo(Faction other) {
        return other != this;
    }
}
