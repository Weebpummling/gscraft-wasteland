package gscraft.war.entity;

import com.tacz.guns.api.TimelessAPI;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

import javax.annotation.Nullable;
import java.util.List;
import java.util.UUID;

/**
 * Dresses a fighter as one rank of its faction. The ranks are data ({@link Ranks}); every slot is rolled from its
 * {@link Choice} as the fighter is issued, so two Scavengers of the same kind rarely match and two soldiers of the same
 * rank match in everything but the details the rank lets vary. The wardrobe was chosen from the live registry
 * (docs/gscraft-equipment-inventory.md).
 */
public final class Kit {
    private static final UUID SPEED_ID = UUID.fromString("5a0c7e1e-6b0e-4a35-9d7e-1f3c2a9b0a01");
    private static final UUID HEALTH_ID = UUID.fromString("5a0c7e1e-6b0e-4a35-9d7e-1f3c2a9b0a02");

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
        equipRank(mob, rank, random);
        return rank;
    }

    /** Dress the mob as one rank rolled from the given pool; null for an empty pool. */
    @Nullable
    public static RankDef issueFrom(Mob mob, List<RankDef> pool, RandomSource random) {
        if (pool.isEmpty()) return null;
        RankDef rank = pick(pool, random);
        equipRank(mob, rank, random);
        return rank;
    }

    private static void equipRank(Mob mob, RankDef rank, RandomSource random) {
        equip(mob, EquipmentSlot.HEAD, rank.head().pick(random));
        equip(mob, EquipmentSlot.CHEST, rank.chest().pick(random));
        equip(mob, EquipmentSlot.LEGS, rank.legs().pick(random));
        equip(mob, EquipmentSlot.FEET, rank.feet().pick(random));
        String gun = rank.gun().pick(random);
        if (gun != null) {
            mob.setItemSlot(EquipmentSlot.MAINHAND, gun(gun));
        } else {
            equip(mob, EquipmentSlot.MAINHAND, rank.melee().pick(random));
        }
        equip(mob, EquipmentSlot.OFFHAND, rank.offhand().pick(random));
        multiply(mob, Attributes.MOVEMENT_SPEED, rank.speed(), SPEED_ID);
        multiply(mob, Attributes.MAX_HEALTH, rank.health(), HEALTH_ID);
        if (rank.health() != 1.0D) mob.setHealth(mob.getMaxHealth());
    }

    private static void multiply(Mob mob, Attribute attribute, double factor, UUID id) {
        AttributeInstance instance = mob.getAttribute(attribute);
        if (instance == null) return;
        instance.removeModifier(id);
        if (factor != 1.0D) {
            instance.addPermanentModifier(new AttributeModifier(id, "gscraft rank", factor - 1.0D,
                    AttributeModifier.Operation.MULTIPLY_BASE));
        }
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
