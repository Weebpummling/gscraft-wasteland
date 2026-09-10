package gscraft.war.entity;

import gscraft.war.GscraftWar;

import java.util.Locale;

/**
 * How a rank fights with its gun. The numbers are the behaviour; the rank data only names the role.
 *
 * @param range     furthest a target is engaged, in blocks
 * @param aimTicks  line of sight needed before the first shot
 * @param holdAt    fraction of range at which the fighter stops closing in and holds ground
 */
public enum Role {
    RIFLEMAN(40.0F, 12, 3, 6, 20, 45, 2.5F, 0.6F),
    /** a rifleman who calls his target to every ally nearby */
    SERGEANT(40.0F, 12, 3, 6, 20, 45, 2.0F, 0.6F),
    /** long aim, one heavy shot, keeps distance and backs away from anything that closes */
    MARKSMAN(64.0F, 40, 1, 1, 30, 50, 0.6F, 1.0F),
    /** long bursts, and keeps firing at the last known position for two seconds after sight is lost */
    GUNNER(40.0F, 16, 8, 15, 30, 60, 4.0F, 0.7F),
    /** walks in behind a raised shield and lowers it only to fire at close range */
    SHIELD(24.0F, 10, 1, 3, 15, 30, 3.0F, 0.4F),
    /** looted guns, worse discipline */
    SCAVENGER(30.0F, 14, 2, 4, 25, 50, 4.0F, 0.6F);

    public final float range;
    public final int aimTicks;
    public final int burstMin;
    public final int burstMax;
    public final int pauseMin;
    public final int pauseMax;
    public final float spread;
    public final float holdAt;

    Role(float range, int aimTicks, int burstMin, int burstMax, int pauseMin, int pauseMax, float spread, float holdAt) {
        this.range = range;
        this.aimTicks = aimTicks;
        this.burstMin = burstMin;
        this.burstMax = burstMax;
        this.pauseMin = pauseMin;
        this.pauseMax = pauseMax;
        this.spread = spread;
        this.holdAt = holdAt;
    }

    public static Role parse(String name) {
        try {
            return valueOf(name.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException ex) {
            GscraftWar.LOG.warn("[gscraft] unknown role '{}', using rifleman", name);
            return RIFLEMAN;
        }
    }
}
