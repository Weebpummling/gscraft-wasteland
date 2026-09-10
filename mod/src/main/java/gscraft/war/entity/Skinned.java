package gscraft.war.entity;

/** A humanoid that wears one of the player skins, chosen when its kit is issued. */
public interface Skinned {
    int SKIN_COUNT = 9;

    int skin();
}
