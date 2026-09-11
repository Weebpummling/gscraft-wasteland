package gscraft.war.world;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Extra drops from a kill by a player, from {@code data/<ns>/gscraft_drops/*.json}: In Control's loot.json carried
 * 65 such rules for the Dead (string, spider eyes, gunpowder, bones, ammunition boxes, food); they live here now,
 * unchanged in content, until the loot design re-cuts them into corpse tables (enemy review §7).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Drops extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_drops";

    public record Drop(ResourceLocation item, float chance, int min, int max) {}

    private static volatile Map<ResourceLocation, List<Drop>> drops = Map.of();

    public Drops() {
        super(new GsonBuilder().create(), FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        Map<ResourceLocation, List<Drop>> map = new HashMap<>();
        int n = 0;
        for (Map.Entry<ResourceLocation, JsonElement> file : files.entrySet()) {
            try {
                for (JsonElement el : GsonHelper.getAsJsonArray(GsonHelper.convertToJsonObject(file.getValue(), "drops"), "drops")) {
                    JsonObject o = GsonHelper.convertToJsonObject(el, "drop");
                    ResourceLocation entity = new ResourceLocation(GsonHelper.getAsString(o, "entity"));
                    ResourceLocation item = new ResourceLocation(GsonHelper.getAsString(o, "item"));
                    if (!ForgeRegistries.ITEMS.containsKey(item)) {
                        GscraftWar.LOG.warn("[gscraft] drop item {} is not registered; rule skipped", item);
                        continue;
                    }
                    int count = GsonHelper.getAsInt(o, "count", 1);
                    map.computeIfAbsent(entity, k -> new ArrayList<>()).add(new Drop(item, GsonHelper.getAsFloat(o, "chance", 1.0F),
                            GsonHelper.getAsInt(o, "min", count), GsonHelper.getAsInt(o, "max", count)));
                    n++;
                }
            } catch (Exception ex) {
                GscraftWar.LOG.error("[gscraft] drop file {} is invalid: {}", file.getKey(), ex.toString());
            }
        }
        map.replaceAll((k, v) -> List.copyOf(v));
        drops = Map.copyOf(map);
        GscraftWar.LOG.info("[gscraft] drops loaded: {} rules for {} entity types", n, map.size());
    }

    public static List<Drop> rulesFor(ResourceLocation entity) {
        return drops.getOrDefault(entity, List.of());
    }

    public static int types() {
        return drops.size();
    }

    @SubscribeEvent
    public static void dropped(LivingDropsEvent event) {
        LivingEntity victim = event.getEntity();
        if (victim.level().isClientSide || !(event.getSource().getEntity() instanceof Player)) return;
        List<Drop> rules = rulesFor(ForgeRegistries.ENTITY_TYPES.getKey(victim.getType()));
        if (rules.isEmpty()) return;
        RandomSource random = victim.getRandom();
        for (Drop drop : rules) {
            if (random.nextFloat() >= drop.chance) continue;
            Item item = ForgeRegistries.ITEMS.getValue(drop.item);
            if (item == null) continue;
            int count = drop.min + (drop.max > drop.min ? random.nextInt(drop.max - drop.min + 1) : 0);
            event.getDrops().add(new ItemEntity(victim.level(), victim.getX(), victim.getY(), victim.getZ(), new ItemStack(item, count)));
        }
    }
}
