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
                            str(o, "head"), str(o, "chest"), str(o, "legs"), str(o, "feet"),
                            str(o, "gun"), str(o, "melee"), str(o, "offhand"),
                            GsonHelper.getAsInt(o, "magazines", 3)));
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

    private static String str(JsonObject o, String key) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsString() : null;
    }

    public static List<RankDef> forFaction(String faction) {
        return byFaction.getOrDefault(faction, List.of());
    }

    public static Map<String, List<RankDef>> all() {
        return byFaction;
    }
}
