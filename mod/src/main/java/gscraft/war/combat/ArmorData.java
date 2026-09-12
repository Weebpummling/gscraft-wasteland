package gscraft.war.combat;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.Map;

/**
 * Armour classes and plate points per item, penetration classes per calibre: {@code data/gscraft/gscraft_armor/*.json},
 * every file merged (later files by name override earlier ones):
 * <pre>
 * {"items": {"superbwarfare:us_chest_iotv": {"class": 4, "points": 40}},
 *  "calibres": {"tacz:556x45": 3},
 *  "guns": {"superbwarfare:ak_47": 3},
 *  "default_penetration": 3}
 * </pre>
 * A round of penetration class at or above the piece's class goes through; below it, the piece stops it. The
 * points are what a piece can take before it protects nothing; they live on the worn item's NBT.
 */
public final class ArmorData extends SimpleJsonResourceReloadListener {
    private static final Gson GSON = new Gson();
    private static Map<ResourceLocation, Piece> items = Map.of();
    private static Map<ResourceLocation, Integer> calibres = Map.of();
    private static Map<ResourceLocation, Integer> guns = Map.of();
    private static int defaultPenetration = 3;

    public record Piece(int armorClass, int points) {}

    public ArmorData() {
        super(GSON, "gscraft_armor");
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        Map<ResourceLocation, Piece> it = new HashMap<>();
        Map<ResourceLocation, Integer> cal = new HashMap<>();
        Map<ResourceLocation, Integer> gun = new HashMap<>();
        int def = 3;
        for (ResourceLocation id : files.keySet().stream().sorted((a, b) -> a.getPath().compareTo(b.getPath())).toList()) {
            JsonElement root = files.get(id);
            if (!root.isJsonObject()) continue;
            JsonObject o = root.getAsJsonObject();
            if (o.has("items")) {
                for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("items").entrySet()) {
                    JsonObject p = e.getValue().getAsJsonObject();
                    it.put(new ResourceLocation(e.getKey()), new Piece(p.get("class").getAsInt(), p.has("points") ? p.get("points").getAsInt() : 0));
                }
            }
            if (o.has("calibres")) {
                for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("calibres").entrySet()) cal.put(new ResourceLocation(e.getKey()), e.getValue().getAsInt());
            }
            if (o.has("guns")) {
                for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("guns").entrySet()) gun.put(new ResourceLocation(e.getKey()), e.getValue().getAsInt());
            }
            if (o.has("default_penetration")) def = o.get("default_penetration").getAsInt();
        }
        items = Map.copyOf(it);
        calibres = Map.copyOf(cal);
        guns = Map.copyOf(gun);
        defaultPenetration = def;
        GscraftWar.LOG.info("[gscraft] armour loaded: {} pieces, {} calibres, {} guns", items.size(), calibres.size(), guns.size());
    }

    /** the piece's class and points, or null for an item the model does not know (vanilla armour applies to it) */
    public static Piece of(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return null;
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id == null ? null : items.get(id);
    }

    public static int penetration(ResourceLocation ammo) {
        if (ammo == null) return defaultPenetration;
        return calibres.getOrDefault(ammo, defaultPenetration);
    }

    public static int gunPenetration(ItemStack gun) {
        if (gun == null || gun.isEmpty()) return defaultPenetration;
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(gun.getItem());
        return id == null ? defaultPenetration : guns.getOrDefault(id, defaultPenetration);
    }

    public static int pieces() {
        return items.size();
    }
}
