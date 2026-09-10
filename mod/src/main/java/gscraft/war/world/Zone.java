package gscraft.war.world;

import java.util.List;

/**
 * A piece of ground and what the director does on it. Zones are matched in file order and the first that contains
 * a point wins, so builds come first, then the small places, then the big ones, then the open ground (no box).
 *
 * @param exclude    nothing is ever placed here (the camp, KROT, every player build)
 * @param cap        most director-placed fighters and Dead standing near a player here
 * @param deadRanks  which Dead ranks a zombie placed here is dressed as, weighted by the ranks file
 */
public record Zone(String name, boolean hasBox, int x0, int x1, int z0, int z1, boolean exclude, int cap,
                   List<SpawnEntry> spawns, List<String> deadRanks, GarrisonDef garrison, List<HorrorDef> horrors) {

    public boolean contains(double x, double z) {
        return !hasBox || (x >= x0 && x <= x1 + 1 && z >= z0 && z <= z1 + 1);
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
