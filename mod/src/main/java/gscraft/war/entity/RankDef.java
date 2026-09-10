package gscraft.war.entity;

/**
 * One rank, read from {@code data/<ns>/gscraft_ranks/<faction>.json}. Each slot is a {@link Choice}: one registry id,
 * or a weighted list where "none" leaves the slot empty. {@code gun} is a TACZ gun definition such as
 * {@code tacz:m4a1}; when the gun roll comes up empty the melee slot is rolled instead.
 *
 * @param magazines spare magazines beyond the loaded one
 * @param speed     multiplies movement speed (the Runner is 1.3)
 * @param health    multiplies maximum health (the Runner is 0.8)
 */
public record RankDef(String name, int weight, Role role, Choice head, Choice chest, Choice legs, Choice feet,
                      Choice gun, Choice melee, Choice offhand, int magazines, double speed, double health) {
}
