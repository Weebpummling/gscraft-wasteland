package gscraft.war.world;

import java.util.List;

/**
 * A piece of ground and what the director does on it. Zones are matched in file order and the first that contains
 * a point wins, so builds come first, then the small places, then the big ones, then the open ground (no box).
 *
 * @param exclude           nothing is ever placed here (the camp, KROT, every player build)
 * @param cap               most director-placed creatures near a player here, before the ground's scale
 * @param spawns            what open ground here draws, and every kind of ground that has no list of its own
 * @param indoorSpawns      what the insides of buildings draw
 * @param undergroundSpawns what bunkers, cellars and caves draw
 * @param deadRanks         which Dead ranks a zombie placed here is dressed as, weighted by the ranks file
 * @param garrison          a standing garrison of soldiers
 * @param lair              the zone's unique creature, kept at one while it lives and returned only after a long wait
 */
public record Zone(String name, boolean hasBox, int x0, int x1, int z0, int z1, boolean exclude, int cap,
                   List<SpawnEntry> spawns, List<SpawnEntry> indoorSpawns, List<SpawnEntry> undergroundSpawns,
                   List<String> deadRanks, GarrisonDef garrison, GarrisonDef lair, List<HorrorDef> horrors, int groupMin, int groupMax,
                   List<List<net.minecraft.core.BlockPos>> patrols) {

    /** how many arrive together: the zone's own range, or the ground's default (open 2-3, inside and below 2-4) */
    public int groupSize(Env env, net.minecraft.util.RandomSource random) {
        int lo = groupMin > 0 ? groupMin : 2;
        int hi = groupMax > 0 ? groupMax : (env == Env.OPEN ? 3 : 4);
        return lo + random.nextInt(Math.max(1, hi - lo + 1));
    }

    public boolean contains(double x, double z) {
        return !hasBox || (x >= x0 && x <= x1 + 1 && z >= z0 && z <= z1 + 1);
    }

    public List<SpawnEntry> spawnsFor(Env env) {
        return switch (env) {
            case INDOOR -> indoorSpawns.isEmpty() ? spawns : indoorSpawns;
            case UNDERGROUND -> undergroundSpawns.isEmpty() ? spawns : undergroundSpawns;
            case OPEN -> spawns;
        };
    }

    public int centerX() {
        return (x0 + x1) / 2;
    }

    public int centerZ() {
        return (z0 + z1) / 2;
    }

    public int halfExtent() {
        return Math.max(x1 - x0, z1 - z0) / 2;
    }
}
