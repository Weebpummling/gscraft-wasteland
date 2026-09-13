package gscraft.war.station;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import gscraft.war.GscraftWar;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * The station's orders, from {@code /data/gscraft/gscraft_recipes/recipes.json} (crafting §3-§4, interface §4.3):
 * the card is the order, an order lists its inputs (item ids or #tags), the tool it wants in the tool slot, its
 * result and its class, and the class sets the time. Orders without a card are the quick recipes anyone may run.
 */
public final class Orders {
    private Orders() {}

    /** multiplies every order's time; the yard's tiers set it (crafting §4: 0.85, 0.7, 0.5) */
    public static double SPEED = 1.0;

    public record Order(String id, String card, String out, int count, String clazz, Map<String, Integer> in, String tool) {
        public int seconds() {
            return CLASSES.getOrDefault(clazz, 120);
        }

        public int ticks() {
            return (int) Math.max(20, Math.round(seconds() * 20 * SPEED));
        }

        public ItemStack result() {
            Item it = item(out);
            return it == null ? ItemStack.EMPTY : new ItemStack(it, count);
        }

        /** the result's name, lower case: "fastener kit" */
        public String name() {
            return needName(out);
        }

        /** "4 bolt, 4 nut, 4 screw, 4 nail; welding torch in the tool slot" */
        public String needs() {
            List<String> parts = new ArrayList<>();
            in.forEach((k, v) -> parts.add(v + " " + needName(k)));
            String s = String.join(", ", parts);
            return tool == null ? s : s + "; " + needName(tool) + " in the tool slot";
        }
    }

    public static final Map<String, Integer> CLASSES = new LinkedHashMap<>();
    public static final List<Order> ALL = load();

    private static List<Order> load() {
        List<Order> out = new ArrayList<>();
        try (var in = Orders.class.getResourceAsStream("/data/gscraft/gscraft_recipes/recipes.json")) {
            if (in == null) {
                GscraftWar.LOG.warn("[gscraft] no recipes.json: the station takes no orders");
                return out;
            }
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            if (root.has("classes")) for (var e : root.getAsJsonObject("classes").entrySet()) CLASSES.put(e.getKey(), e.getValue().getAsInt());
            for (JsonElement el : root.getAsJsonArray("orders")) {
                JsonObject o = el.getAsJsonObject();
                Map<String, Integer> needs = new LinkedHashMap<>();
                for (var e : o.getAsJsonObject("in").entrySet()) needs.put(e.getKey(), e.getValue().getAsInt());
                out.add(new Order(o.get("id").getAsString(), o.has("card") ? o.get("card").getAsString() : null, o.get("out").getAsString(),
                        o.has("count") ? o.get("count").getAsInt() : 1, o.has("class") ? o.get("class").getAsString() : "intermediate", needs,
                        o.has("tool") ? o.get("tool").getAsString() : null));
            }
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] recipes.json is invalid: {}", ex.toString());
        }
        GscraftWar.LOG.info("[gscraft] station: {} orders, {} cards", out.size(), cards(out).size());
        return out;
    }

    public static Order byId(String id) {
        for (Order o : ALL) if (o.id().equals(id)) return o;
        return null;
    }

    /** the orders a card item (its id under gscraft) is good for */
    public static List<Order> forCard(String cardId) {
        List<Order> out = new ArrayList<>();
        for (Order o : ALL) if (cardId.equals(o.card())) out.add(o);
        return out;
    }

    /** the quick recipes that need no card */
    public static List<Order> quick() {
        List<Order> out = new ArrayList<>();
        for (Order o : ALL) if (o.card() == null) out.add(o);
        return out;
    }

    public static Set<String> cards() {
        return cards(ALL);
    }

    private static Set<String> cards(List<Order> orders) {
        Set<String> out = new LinkedHashSet<>();
        for (Order o : orders) if (o.card() != null) out.add(o.card());
        return out;
    }

    static Item item(String id) {
        ResourceLocation rl = ResourceLocation.tryParse(id);
        return rl == null ? null : ForgeRegistries.ITEMS.getValue(rl);
    }

    /** does the stack satisfy a need ("gscraft:bolt" or "#minecraft:wool")? */
    public static boolean matches(ItemStack s, String need) {
        if (s.isEmpty()) return false;
        if (need.startsWith("#")) {
            ResourceLocation rl = ResourceLocation.tryParse(need.substring(1));
            return rl != null && s.is(TagKey.create(Registries.ITEM, rl));
        }
        Item it = item(need);
        return it != null && s.is(it);
    }

    /** a need's name for the readouts: an item's name lower case, a tag's path with spaces */
    public static String needName(String need) {
        if (need.startsWith("#")) {
            String p = need.substring(need.indexOf(':') + 1);
            return p.replace('_', ' ');
        }
        Item it = item(need);
        return it == null ? need : new ItemStack(it).getHoverName().getString().toLowerCase(Locale.ROOT);
    }

    public static String mmss(int ticks) {
        int s = (ticks + 19) / 20;
        return String.format("%d:%02d", s / 60, s % 60);
    }
}
