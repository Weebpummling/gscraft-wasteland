package gscraft.war.entity;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.profiling.ProfilerFiller;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Every rank of every faction, as datapack JSON, one file per faction. Reloads with /reload. */
public final class Ranks extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_ranks";

    private static volatile Map<String, List<RankDef>> byFaction = Map.of();

    public Ranks() {
        super(new GsonBuilder().create(), FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        Map<String, List<RankDef>> map = new LinkedHashMap<>();
        files.forEach((file, json) -> {
            try {
                List<RankDef> list = new ArrayList<>();
                for (JsonElement el : GsonHelper.getAsJsonArray(GsonHelper.convertToJsonObject(json, "ranks"), "ranks")) {
                    JsonObject o = GsonHelper.convertToJsonObject(el, "rank");
                    list.add(new RankDef(
                            GsonHelper.getAsString(o, "name"),
                            GsonHelper.getAsInt(o, "weight", 1),
                            Role.parse(GsonHelper.getAsString(o, "role", "rifleman")),
                            choice(o, "head"), choice(o, "chest"), choice(o, "legs"), choice(o, "feet"),
                            choice(o, "gun"), choice(o, "melee"), choice(o, "offhand"),
                            GsonHelper.getAsInt(o, "magazines", 3),
                            GsonHelper.getAsFloat(o, "speed", 1.0F),
                            GsonHelper.getAsFloat(o, "health", 1.0F)));
                }
                map.put(file.getPath(), List.copyOf(list));
            } catch (Exception ex) {
                GscraftWar.LOG.error("[gscraft] rank file {} is invalid: {}", file, ex.toString());
            }
        });
        byFaction = Collections.unmodifiableMap(map);
        StringBuilder summary = new StringBuilder();
        map.forEach((f, l) -> summary.append(f).append('=').append(l.size()).append(' '));
        GscraftWar.LOG.info("[gscraft] ranks loaded: {}", summary.toString().trim());
    }

    /** a slot: absent, one id, or a list of ids and {"item", "weight"} objects; "none" or a null item is an empty slot */
    private static Choice choice(JsonObject o, String key) {
        if (!o.has(key) || o.get(key).isJsonNull()) return Choice.NONE;
        JsonElement el = o.get(key);
        if (el.isJsonPrimitive()) return new Choice(List.of(new Choice.Option(item(el.getAsString()), 1)));
        List<Choice.Option> list = new ArrayList<>();
        for (JsonElement e : el.getAsJsonArray()) {
            if (e.isJsonPrimitive()) {
                list.add(new Choice.Option(item(e.getAsString()), 1));
            } else {
                JsonObject c = e.getAsJsonObject();
                String id = c.has("item") && !c.get("item").isJsonNull() ? item(c.get("item").getAsString()) : null;
                list.add(new Choice.Option(id, GsonHelper.getAsInt(c, "weight", 1)));
            }
        }
        return new Choice(List.copyOf(list));
    }

    private static String item(String id) {
        return "none".equals(id) ? null : id;
    }

    public static List<RankDef> forFaction(String faction) {
        return byFaction.getOrDefault(faction, List.of());
    }

    public static RankDef named(String faction, String name) {
        for (RankDef r : forFaction(faction)) {
            if (r.name().equals(name)) return r;
        }
        return null;
    }

    public static Map<String, List<RankDef>> all() {
        return byFaction;
    }
}
