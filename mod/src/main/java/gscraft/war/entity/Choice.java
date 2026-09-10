package gscraft.war.entity;

import net.minecraft.util.RandomSource;

import java.util.List;

/**
 * What goes in one equipment slot: a single item, or a weighted list to roll from, where an option with no item
 * leaves the slot empty. The armies use it lightly - a rank keeps its uniform and varies its rifle - and the
 * Scavengers use it for everything, because looted gear is never twice the same (enemies §3.2).
 */
public record Choice(List<Option> options) {
    public static final Choice NONE = new Choice(List.of());

    /** one entry; {@code item} is null for "nothing in this slot" */
    public record Option(String item, int weight) {
    }

    public String pick(RandomSource random) {
        if (options.isEmpty()) return null;
        if (options.size() == 1) return options.get(0).item();
        int total = 0;
        for (Option o : options) total += Math.max(0, o.weight());
        if (total <= 0) return options.get(0).item();
        int roll = random.nextInt(total);
        for (Option o : options) {
            roll -= Math.max(0, o.weight());
            if (roll < 0) return o.item();
        }
        return options.get(options.size() - 1).item();
    }
}
