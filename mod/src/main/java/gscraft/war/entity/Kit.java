package gscraft.war.entity;

import com.tacz.guns.api.TimelessAPI;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

import javax.annotation.Nullable;
import java.util.List;

/**
 * Dresses a fighter as one rank of its faction. The ranks themselves are data ({@link Ranks}); the wardrobe was
 * chosen from the live registry (docs/gscraft-equipment-inventory.md).
 */
public final class Kit {
    private Kit() {}

    /**
     * Equip the mob and return the rank it was given, or null when its faction has no ranks.
     *
     * @param pinned a rank name to issue instead of rolling, or empty to roll by weight
     */
    @Nullable
    public static RankDef issue(Mob mob, String faction, RandomSource random, @Nullable String pinned) {
        List<RankDef> ranks = Ranks.forFaction(faction);
        if (ranks.isEmpty()) {
            GscraftWar.LOG.warn("[gscraft] no ranks for faction {}", faction);
            return null;
        }
        RankDef rank = null;
        if (pinned != null && !pinned.isEmpty()) {
            for (RankDef r : ranks) {
                if (r.name().equals(pinned)) rank = r;
            }
            if (rank == null) GscraftWar.LOG.warn("[gscraft] pinned rank '{}' is not a {} rank; rolling", pinned, faction);
        }
        if (rank == null) rank = pick(ranks, random);
        equipRank(mob, rank);
        return rank;
    }

    /** Dress the mob as one rank rolled from the given pool; null for an empty pool. */
    @Nullable
    public static RankDef issueFrom(Mob mob, List<RankDef> pool, RandomSource random) {
        if (pool.isEmpty()) return null;
        RankDef rank = pick(pool, random);
        equipRank(mob, rank);
        return rank;
    }

    private static void equipRank(Mob mob, RankDef rank) {
        equip(mob, EquipmentSlot.HEAD, rank.head());
        equip(mob, EquipmentSlot.CHEST, rank.chest());
        equip(mob, EquipmentSlot.LEGS, rank.legs());
        equip(mob, EquipmentSlot.FEET, rank.feet());
        if (rank.gun() != null) {
            mob.setItemSlot(EquipmentSlot.MAINHAND, gun(rank.gun()));
        } else {
            equip(mob, EquipmentSlot.MAINHAND, rank.melee());
        }
        equip(mob, EquipmentSlot.OFFHAND, rank.offhand());
    }

    private static RankDef pick(List<RankDef> ranks, RandomSource random) {
        int total = 0;
        for (RankDef r : ranks) total += Math.max(0, r.weight());
        if (total <= 0) return ranks.get(0);
        int roll = random.nextInt(total);
        for (RankDef r : ranks) {
            roll -= Math.max(0, r.weight());
            if (roll < 0) return r;
        }
        return ranks.get(ranks.size() - 1);
    }

    private static Item item(String id) {
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(id));
        if (item == null || item == Items.AIR) {
            GscraftWar.LOG.warn("[gscraft] kit item {} is not registered; slot left empty", id);
            return null;
        }
        return item;
    }

    private static void equip(Mob mob, EquipmentSlot slot, String id) {
        if (id == null) return;
        Item item = item(id);
        if (item != null) mob.setItemSlot(slot, new ItemStack(item));
    }

    private static ItemStack gun(String gunId) {
        Item item = item("tacz:modern_kinetic_gun");
        if (item == null) return ItemStack.EMPTY;
        ItemStack stack = new ItemStack(item);
        stack.getOrCreateTag().putString("GunId", gunId);
        if (TimelessAPI.getCommonGunIndex(new ResourceLocation(gunId)).isEmpty()) {
            GscraftWar.LOG.warn("[gscraft] kit gun {} is not a loaded TACZ gun", gunId);
        }
        GunAttackGoal.refill(stack);
        return stack;
    }
}
