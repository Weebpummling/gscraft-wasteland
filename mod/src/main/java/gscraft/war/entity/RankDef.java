package gscraft.war.entity;

/**
 * One rank, read from {@code data/<ns>/gscraft_ranks/<faction>.json}. Item fields are registry ids; {@code gun} is a
 * TACZ gun definition such as {@code tacz:m4a1}. At most one of gun and melee is set.
 *
 * @param magazines spare magazines beyond the loaded one
 */
public record RankDef(String name, int weight, Role role, String head, String chest, String legs, String feet,
                      String gun, String melee, String offhand, int magazines) {
}
