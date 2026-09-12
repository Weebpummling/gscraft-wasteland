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
import java.util.EnumSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * The director's map, as datapack JSON in {@code data/<ns>/gscraft_zones/}. Generated from the measured boxes by
 * tools/war_zones.py. Reloads with /reload - the reason In Control's areas are no longer the source.
 */
public final class Zones extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_zones";

    private static volatile List<Zone> zones = List.of();

    public Zones() {
        super(new GsonBuilder().create(), FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        List<Zone> list = new ArrayList<>();
        files.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(file -> {
            try {
                for (JsonElement el : GsonHelper.getAsJsonArray(GsonHelper.convertToJsonObject(file.getValue(), "zones"), "zones")) {
                    list.add(parse(GsonHelper.convertToJsonObject(el, "zone")));
                }
            } catch (Exception ex) {
                GscraftWar.LOG.error("[gscraft] zone file {} is invalid: {}", file.getKey(), ex.toString());
            }
        });
        zones = List.copyOf(list);
        long excluded = list.stream().filter(Zone::exclude).count();
        long garrisons = list.stream().filter(z -> z.garrison() != null).count();
        long lairs = list.stream().filter(z -> z.lair() != null).count();
        GscraftWar.LOG.info("[gscraft] zones loaded: {} ({} excluded, {} garrisons, {} lairs)", list.size(), excluded, garrisons, lairs);
    }

    private static Zone parse(JsonObject o) {
        String name = GsonHelper.getAsString(o, "name");
        boolean hasBox = o.has("box");
        int x0 = 0, x1 = 0, z0 = 0, z1 = 0;
        if (hasBox) {
            JsonArray b = GsonHelper.getAsJsonArray(o, "box");
            x0 = b.get(0).getAsInt();
            x1 = b.get(1).getAsInt();
            z0 = b.get(2).getAsInt();
            z1 = b.get(3).getAsInt();
        }
        List<String> deadRanks = new ArrayList<>();
        for (JsonElement el : GsonHelper.getAsJsonArray(o, "dead_ranks", new JsonArray())) deadRanks.add(el.getAsString());
        List<HorrorDef> horrors = new ArrayList<>();
        for (JsonElement el : GsonHelper.getAsJsonArray(o, "horrors", new JsonArray())) {
            JsonObject h = el.getAsJsonObject();
            Set<Env> envs = EnumSet.noneOf(Env.class);
            for (JsonElement e : GsonHelper.getAsJsonArray(h, "envs", new JsonArray())) {
                envs.add(Env.valueOf(e.getAsString().toUpperCase(Locale.ROOT)));
            }
            horrors.add(new HorrorDef(new ResourceLocation(GsonHelper.getAsString(h, "entity")),
                    GsonHelper.getAsBoolean(h, "night", true), GsonHelper.getAsFloat(h, "chance", 0.02F), Set.copyOf(envs)));
        }
        return new Zone(name, hasBox, x0, x1, z0, z1, GsonHelper.getAsBoolean(o, "exclude", false),
                GsonHelper.getAsInt(o, "cap", 0), entries(o, "spawns"), entries(o, "indoor_spawns"),
                entries(o, "underground_spawns"), List.copyOf(deadRanks), standing(o, "garrison", 4, 10),
                standing(o, "lair", 1, 120), List.copyOf(horrors), group(o, 0), group(o, 1), patrols(o), armour(o));
    }

    /** optional "armour": {"chance": 0.06, "compositions": [{"weight": 6, "vehicles": ["superbwarfare:bmp_2"], "infantry": 4}, ...]} */
    private static ArmourDef armour(JsonObject o) {
        if (!o.has("armour")) return null;
        JsonObject a = GsonHelper.getAsJsonObject(o, "armour");
        List<ArmourDef.Composition> comps = new ArrayList<>();
        for (JsonElement el : GsonHelper.getAsJsonArray(a, "compositions", new JsonArray())) {
            JsonObject c = el.getAsJsonObject();
            List<ResourceLocation> vehicles = new ArrayList<>();
            for (JsonElement v : GsonHelper.getAsJsonArray(c, "vehicles", new JsonArray())) vehicles.add(new ResourceLocation(v.getAsString()));
            comps.add(new ArmourDef.Composition(GsonHelper.getAsInt(c, "weight", 1), List.copyOf(vehicles), GsonHelper.getAsInt(c, "infantry", 0)));
        }
        return new ArmourDef(GsonHelper.getAsFloat(a, "chance", 0.0F), List.copyOf(comps));
    }

    /** optional "patrols": [[[x, z], ...], ...] - routes a squad leader walks (feasibility C2); y is found on arrival */
    private static List<List<net.minecraft.core.BlockPos>> patrols(JsonObject o) {
        List<List<net.minecraft.core.BlockPos>> routes = new ArrayList<>();
        for (JsonElement r : GsonHelper.getAsJsonArray(o, "patrols", new JsonArray())) {
            List<net.minecraft.core.BlockPos> route = new ArrayList<>();
            for (JsonElement pt : r.getAsJsonArray()) {
                JsonArray xz = pt.getAsJsonArray();
                route.add(new net.minecraft.core.BlockPos(xz.get(0).getAsInt(), Integer.MIN_VALUE, xz.get(1).getAsInt()));
            }
            if (route.size() >= 2) routes.add(List.copyOf(route));
        }
        return List.copyOf(routes);
    }

    /** optional "group": [min, max] - how many arrive together in this zone */
    private static int group(JsonObject o, int i) {
        if (!o.has("group")) return 0;
        JsonArray g = GsonHelper.getAsJsonArray(o, "group");
        return g.size() > i ? g.get(i).getAsInt() : 0;
    }

    private static List<SpawnEntry> entries(JsonObject o, String key) {
        List<SpawnEntry> list = new ArrayList<>();
        for (JsonElement el : GsonHelper.getAsJsonArray(o, key, new JsonArray())) {
            JsonObject s = el.getAsJsonObject();
            list.add(new SpawnEntry(new ResourceLocation(GsonHelper.getAsString(s, "entity")),
                    GsonHelper.getAsInt(s, "weight", 1), GsonHelper.getAsBoolean(s, "night", false)));
        }
        return List.copyOf(list);
    }

    private static GarrisonDef standing(JsonObject o, String key, int defaultCount, int defaultMinutes) {
        if (!o.has(key)) return null;
        JsonObject g = GsonHelper.getAsJsonObject(o, key);
        return new GarrisonDef(new ResourceLocation(GsonHelper.getAsString(g, "entity")),
                GsonHelper.getAsInt(g, "count", defaultCount), GsonHelper.getAsInt(g, "refill_minutes", defaultMinutes) * 1200);
    }

    /** the first zone containing the point, or null when not even open ground is defined */
    public static Zone at(double x, double z) {
        for (Zone zone : zones) {
            if (zone.contains(x, z)) return zone;
        }
        return null;
    }

    public static Zone named(String name) {
        for (Zone zone : zones) {
            if (zone.name().equals(name)) return zone;
        }
        return null;
    }

    public static List<Zone> all() {
        return zones;
    }
}
