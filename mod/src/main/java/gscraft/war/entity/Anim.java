package gscraft.war.entity;

import java.util.Locale;

/**
 * A fighter's tactical move, told to the clients as one synced byte (animation research §4, A2): the low four bits
 * are the move, the high four a sequence that steps on every play, so a move repeated back to back is seen twice.
 * The client plays the clip of the same name from {@code assets/gscraft/player_animation/} on the fighter's
 * stand-in; loops run until the byte changes, one-shots end by themselves. The gun handling itself (shoulder, aim,
 * reload, the crawl) is TACZ's own on the stand-in and needs nothing here.
 */
public enum Anim {
    NONE(0, false),
    /** dropping flat: the arms go out to catch the ground */
    DIVE(1, false),
    /** the last blocks into cover at a run, sliding in */
    SLIDE(2, false),
    /** the upper body out of cover to fire, held while the lean lasts */
    LEAN_LEFT(3, true),
    LEAN_RIGHT(4, true),
    /** a grenade: the wind-up, the release at the goal's fifteenth tick, the follow-through */
    THROW(5, false),
    /** a hit that did not lay the body down */
    FLINCH(6, false),
    /** reserved for A4 */
    MANTLE(7, false);

    public final int id;
    public final boolean loop;

    Anim(int id, boolean loop) {
        this.id = id;
        this.loop = loop;
    }

    /** the clip's name in the registry: {@code gscraft:<name>} */
    public String clip() {
        return name().toLowerCase(Locale.ROOT);
    }

    public static Anim of(int id) {
        for (Anim a : values()) if (a.id == id) return a;
        return NONE;
    }

    public static Anim unpack(int packed) {
        return of(packed & 15);
    }

    public static int seq(int packed) {
        return (packed >> 4) & 15;
    }

    public static byte pack(Anim a, int seq) {
        return (byte) (((seq & 15) << 4) | a.id);
    }
}
