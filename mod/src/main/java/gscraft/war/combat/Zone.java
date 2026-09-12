package gscraft.war.combat;

/** Where a hit landed on a body (damage model, 2026-09-11). */
public enum Zone {
    HEAD, THORAX, STOMACH, ARMS, LEGS;

    public float multiplier() {
        return switch (this) {
            case HEAD -> Damage.HEAD;
            case THORAX -> Damage.THORAX;
            case STOMACH -> Damage.STOMACH;
            case ARMS -> Damage.ARMS;
            case LEGS -> Damage.LEGS;
        };
    }
}
