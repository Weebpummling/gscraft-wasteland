package gscraft.war.entity;

import gscraft.war.Faction;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/**
 * What each soldier is issued. Phase 1 carries two ranks per faction, taken from tools/spawn_rules.py - the
 * same wardrobe the illager factions wore, invisibly. Phase 3 moves every rank into datapack JSON.
 */
public final class Kit {
    private record Rank(String name, int weight, String head, String chest, String legs, String feet, String gunId) {}

    private static final String SBW = "superbwarfare:";
    private static final String DR = "dragonrise_reforge:";

    private static final List<Rank> NATO = List.of(
            new Rank("NATO Sergeant", 12, DR + "fast_helmet", DR + "kr06_chest", DR + "kr06_pants", null, "tacz:m4a1"),
            new Rank("NATO Rifleman", 88, SBW + "us_helmet_pasgt", SBW + "us_chest_iotv", DR + "kr06_pants", null, "tacz:m4a1"));

    private static final List<Rank> RUAF = List.of(
            new Rank("RUAF Sergeant", 12, DR + "fast_helmet", DR + "kr06_chest", DR + "msv_pants", null, "tacz:ak47"),
            new Rank("RUAF Rifleman", 88, SBW + "ru_helmet_6b47", SBW + "ru_chest_6b43", DR + "msv_pants", null, "tacz:ak47"));

    private Kit() {}

    /** Dress the soldier as a rank of its faction and return the rank's name. */
    public static String issue(Soldier mob, Faction faction, RandomSource random) {
        Rank rank = pick(faction == Faction.NATO ? NATO : RUAF, random);
        equip(mob, EquipmentSlot.HEAD, rank.head());
        equip(mob, EquipmentSlot.CHEST, rank.chest());
        equip(mob, EquipmentSlot.LEGS, rank.legs());
        equip(mob, EquipmentSlot.FEET, rank.feet());
        mob.setItemSlot(EquipmentSlot.MAINHAND, gun(rank.gunId()));
        return rank.name();
    }

    private static Rank pick(List<Rank> ranks, RandomSource random) {
        int total = 0;
        for (Rank r : ranks) total += r.weight();
        int roll = random.nextInt(total);
        for (Rank r : ranks) {
            roll -= r.weight();
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

    private static void equip(Soldier mob, EquipmentSlot slot, String id) {
        if (id == null) return;
        Item item = item(id);
        if (item != null) mob.setItemSlot(slot, new ItemStack(item));
    }

    private static ItemStack gun(String gunId) {
        Item item = item("tacz:modern_kinetic_gun");
        if (item == null) return ItemStack.EMPTY;
        ItemStack stack = new ItemStack(item);
        stack.getOrCreateTag().putString("GunId", gunId);
        GunAttackGoal.refill(stack);
        return stack;
    }
}
