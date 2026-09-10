package gscraft.war.entity;

/** A fighter with a role and a finite supply of spare magazines (review W10). */
public interface GunUser {
    Role role();

    /** spend one spare magazine; false when none are left */
    boolean takeMagazine();

    boolean outOfAmmo();

    /** the last magazine is empty and none are left: the fighter closes to melee from here on */
    void markOutOfAmmo();
}
