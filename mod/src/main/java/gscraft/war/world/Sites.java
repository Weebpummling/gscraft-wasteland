package gscraft.war.world;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.profiling.ProfilerFiller;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The strongpoints and the camp, from {@code data/<ns>/gscraft_sites/*.json} (design §6; fold-in review F1–F3).
 * A site file: id, name, box, anchor, the faction that counterattacks, the camp approach its counterattack uses,
 * six assault waves and three defence waves. The camp file: perimeter, the camp square (the loss check) and the
 * four approaches, 48 blocks outside the perimeter.
 */
public final class Sites extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_sites";

    /** one line of a wave: this many of this body, dressed as this rank when one is named */
    public record WaveEntry(ResourceLocation entity, String rank, int count) {}

    public record SiteDef(String id, String name, int x0, int x1, int z0, int z1, int anchorX, int anchorZ, String faction,
                          String approach, List<List<WaveEntry>> assault, List<List<WaveEntry>> defence) {
        public boolean contains(int x, int z) {
            return x >= x0 && x <= x1 && z >= z0 && z <= z1;
        }
    }

    public record CampDef(int x0, int x1, int z0, int z1, int sx0, int sx1, int sz0, int sz1, Map<String, int[]> approaches) {
        public boolean inSquare(double x, double z) {
            return x >= sx0 && x <= sx1 + 1 && z >= sz0 && z <= sz1 + 1;
        }
    }

    private static volatile Map<String, SiteDef> sites = Map.of();
    private static volatile CampDef camp;

    public Sites() {
        super(new GsonBuilder().create(), FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        Map<String, SiteDef> map = new LinkedHashMap<>();
        CampDef campDef = null;
        for (Map.Entry<ResourceLocation, JsonElement> file : files.entrySet()) {
            try {
                JsonObject o = GsonHelper.convertToJsonObject(file.getValue(), "site");
                if (o.has("camp")) {
                    campDef = parseCamp(GsonHelper.getAsJsonObject(o, "camp"));
                } else {
                    SiteDef def = parseSite(o);
                    map.put(def.id(), def);
                }
            } catch (Exception ex) {
                GscraftWar.LOG.error("[gscraft] site file {} is invalid: {}", file.getKey(), ex.toString());
            }
        }
        sites = Map.copyOf(map);
        camp = campDef;
        GscraftWar.LOG.info("[gscraft] sites loaded: {} ({}), camp {}", map.size(), map.keySet(), campDef == null ? "MISSING" : "ok");
    }

    private static int[] box(JsonObject o, String key) {
        JsonArray b = GsonHelper.getAsJsonArray(o, key);
        int[] v = {b.get(0).getAsInt(), b.get(1).getAsInt(), b.get(2).getAsInt(), b.get(3).getAsInt()};
        return new int[] {Math.min(v[0], v[1]), Math.max(v[0], v[1]), Math.min(v[2], v[3]), Math.max(v[2], v[3])};
    }

    private static SiteDef parseSite(JsonObject o) {
        int[] b = box(o, "box");
        JsonArray a = GsonHelper.getAsJsonArray(o, "anchor");
        return new SiteDef(GsonHelper.getAsString(o, "id"), GsonHelper.getAsString(o, "name"), b[0], b[1], b[2], b[3],
                a.get(0).getAsInt(), a.get(1).getAsInt(), GsonHelper.getAsString(o, "faction"),
                GsonHelper.getAsString(o, "approach"), waves(o, "assault"), waves(o, "defence"));
    }

    private static List<List<WaveEntry>> waves(JsonObject o, String key) {
        List<List<WaveEntry>> waves = new ArrayList<>();
        for (JsonElement w : GsonHelper.getAsJsonArray(o, key)) {
            List<WaveEntry> wave = new ArrayList<>();
            for (JsonElement e : w.getAsJsonArray()) {
                JsonObject s = e.getAsJsonObject();
                wave.add(new WaveEntry(new ResourceLocation(GsonHelper.getAsString(s, "entity")),
                        GsonHelper.getAsString(s, "rank", ""), GsonHelper.getAsInt(s, "count", 1)));
            }
            waves.add(List.copyOf(wave));
        }
        return List.copyOf(waves);
    }

    private static CampDef parseCamp(JsonObject o) {
        int[] p = box(o, "perimeter");
        int[] s = box(o, "square");
        Map<String, int[]> approaches = new LinkedHashMap<>();
        JsonObject ap = GsonHelper.getAsJsonObject(o, "approaches");
        for (String name : ap.keySet()) {
            JsonArray xz = ap.getAsJsonArray(name);
            approaches.put(name, new int[] {xz.get(0).getAsInt(), xz.get(1).getAsInt()});
        }
        return new CampDef(p[0], p[1], p[2], p[3], s[0], s[1], s[2], s[3], Map.copyOf(approaches));
    }

    public static Map<String, SiteDef> all() {
        return sites;
    }

    public static SiteDef get(String id) {
        return sites.get(id);
    }

    public static CampDef camp() {
        return camp;
    }
}
