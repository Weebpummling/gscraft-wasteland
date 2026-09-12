package gscraft.war.world;

import net.minecraft.resources.ResourceLocation;

import java.util.List;

/**
 * A zone's armour roll (armour design §3): the chance per director pass that a player in open ground here gets an
 * armour group placed on a road, and what that group is - the vehicles and the infantry that walks with them.
 */
public record ArmourDef(float chance, List<Composition> compositions) {
    public record Composition(int weight, List<ResourceLocation> vehicles, int infantry) {}

    public Composition pick(net.minecraft.util.RandomSource random) {
        int total = 0;
        for (Composition c : compositions) total += Math.max(0, c.weight());
        if (total <= 0) return null;
        int roll = random.nextInt(total);
        for (Composition c : compositions) {
            roll -= Math.max(0, c.weight());
            if (roll < 0) return c;
        }
        return compositions.get(compositions.size() - 1);
    }
}
