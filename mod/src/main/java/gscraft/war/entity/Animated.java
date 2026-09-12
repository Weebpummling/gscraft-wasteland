package gscraft.war.entity;

/** A body whose tactical moves ({@link Anim}) are synced to the clients as one byte. */
public interface Animated {
    /** the packed byte: {@link Anim#unpack} for the move, {@link Anim#seq} for the sequence */
    int animByte();

    /** server side: play a move - a loop until the next play, a one-shot to its end */
    void play(Anim anim);
}
