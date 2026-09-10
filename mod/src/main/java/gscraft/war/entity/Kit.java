package gscraft.war.entity;

import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;
import java.util.Map;

/**
 * What each fighter is issued, by faction. The wardrobe is the one chosen from the live registry
 * (docs/gscraft-equipment-inventory.md). Phase 3 moves ranks into datapack JSON.
 *
 * NATO matches, the Scavengers do not: looted, never issued, and never twice the same.
 */
public final class Kit {
    /** gunId is a TACZ gun definition; melee is an item id. At most one is set. */
    private record Rank(String name, int weight, String head, String chest, String legs, String feet,
                        String gunId, String melee) {}

    private static final String SBW = "superbwarfare:";
    private static final String DR = "dragonrise_reforge:";
    private static final String PK = "pomkotsmechs:";
    private static final String CR = "create:";

    private static final List<Rank> NATO = List.of(
            new Rank("NATO Sergeant", 12, DR + "fast_helmet", DR + "kr06_chest", DR + "kr06_pants", null, "tacz:m4a1", null),
            new Rank("NATO Rifleman", 88, SBW + "us_helmet_pasgt", SBW + "us_chest_iotv", DR + "kr06_pants", null, "tacz:m4a1", null));

    private static final List<Rank> RUAF = List.of(
            new Rank("RUAF Sergeant", 12, DR + "fast_helmet", DR + "kr06_chest", DR + "msv_pants", null, "tacz:ak47", null),
            new Rank("RUAF Rifleman", 88, SBW + "ru_helmet_6b47", SBW + "ru_chest_6b43", DR + "msv_pants", null, "tacz:ak47", null));

    private static final List<Rank> SCAVENGERS = List.of(
            new Rank("Scavenger", 40, PK + "wandererarmorhelmet", PK + "wandererarmorchestplate",
                    PK + "wandererarmorleggings", PK + "wandererarmorboots", null, SBW + "steel_pipe"),
            // cardboard armour reads as scrap at fifty metres; Create's cardboard sword deals no damage (a Scrapper
            // carrying one lost to two zombies without landing a hit), so the Scrapper fights with a knife
            new Rank("Scrapper", 18, CR + "cardboard_helmet", CR + "cardboard_chestplate",
                    CR + "cardboard_leggings", CR + "cardboard_boots", null, SBW + "knife"),
            new Rank("Scavenger Raider", 16, SBW + "ge_helmet_m_35", DR + "gorka3",
                    DR + "gorka3_leggings", PK + "wandererarmorboots", null, SBW + "crowbar"),
            new Rank("Scavenger Digger", 12, null, DR + "army07hat",
                    DR + "pants21", PK + "wandererarmorboots", null, SBW + "military_shovel"),
            new Rank("Scavenger Gunman", 8, PK + "pomkotsarmorhelmet", DR + "gorka3",
                    PK + "wandererarmorleggings", PK + "wandererarmorboots", "tacz:kar98", null),
            new Rank("Scavenger Captain", 6, DR + "kr06_helmet", DR + "msv_chest",
                    DR + "gorka3_leggings", PK + "wandererarmorboots", "tacz:spas_12", null));

    private static final Map<String, List<Rank>> BY_FACTION = Map.of(
            "nato", NATO,
            "ruaf", RUAF,
            Scavenger.FACTION, SCAVENGERS);

    private Kit() {}

    /** Dress the mob as a rank of its faction and return the rank's name. */
    public static String issue(Mob mob, String faction, RandomSource random) {
        List<Rank> ranks = BY_FACTION.get(faction);
        if (ranks == null) {
            GscraftWar.LOG.warn("[gscraft] no kit for faction {}", faction);
            return "";
        }
        Rank rank = pick(ranks, random);
        equip(mob, EquipmentSlot.HEAD, rank.head());
        equip(mob, EquipmentSlot.CHEST, rank.chest());
        equip(mob, EquipmentSlot.LEGS, rank.legs());
        equip(mob, EquipmentSlot.FEET, rank.feet());
        if (rank.gunId() != null) {
            mob.setItemSlot(EquipmentSlot.MAINHAND, gun(rank.gunId()));
        } else {
            equip(mob, EquipmentSlot.MAINHAND, rank.melee());
        }
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
        GunAttackGoal.refill(stack);
        return stack;
    }
}
