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
import java.util.List;
import java.util.Map;

/**
 * Locked rectangles, from {@code data/<ns>/gscraft_locks/*.json}: nothing changes a block inside one except a
 * server-run command (the quest's stage functions) or an op in creative. All heights, overworld only. Replaces the
 * two KubeJS tower-lock scripts (fold-in review F16).
 *
 * @param x0,x1,z0,z1 inclusive block bounds
 */
public final class Locks extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_locks";
    /** pistons this close to a lock's edge do nothing, so nothing can be pushed across it */
    public static final int PISTON_MARGIN = 13;

    public record Lock(String name, int x0, int x1, int z0, int z1) {
        boolean contains(int x, int z) {
            return x >= x0 && x <= x1 && z >= z0 && z <= z1;
        }

        boolean near(int x, int z, int margin) {
            return x >= x0 - margin && x <= x1 + margin && z >= z0 - margin && z <= z1 + margin;
        }
    }

    private static volatile List<Lock> locks = List.of();

    public Locks() {
        super(new GsonBuilder().create(), FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        List<Lock> list = new ArrayList<>();
        files.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(file -> {
            try {
                for (JsonElement el : GsonHelper.getAsJsonArray(GsonHelper.convertToJsonObject(file.getValue(), "locks"), "locks")) {
                    JsonObject o = GsonHelper.convertToJsonObject(el, "lock");
                    JsonArray b = GsonHelper.getAsJsonArray(o, "box");
                    list.add(new Lock(GsonHelper.getAsString(o, "name"), Math.min(b.get(0).getAsInt(), b.get(1).getAsInt()),
                            Math.max(b.get(0).getAsInt(), b.get(1).getAsInt()), Math.min(b.get(2).getAsInt(), b.get(3).getAsInt()),
                            Math.max(b.get(2).getAsInt(), b.get(3).getAsInt())));
                }
            } catch (Exception ex) {
                GscraftWar.LOG.error("[gscraft] lock file {} is invalid: {}", file.getKey(), ex.toString());
            }
        });
        locks = List.copyOf(list);
        GscraftWar.LOG.info("[gscraft] locks loaded: {}", list.stream().map(Lock::name).toList());
    }

    public static List<Lock> all() {
        return locks;
    }

    public static boolean locked(int x, int z) {
        for (Lock lock : locks) {
            if (lock.contains(x, z)) return true;
        }
        return false;
    }

    public static boolean nearLock(int x, int z, int margin) {
        for (Lock lock : locks) {
            if (lock.near(x, z, margin)) return true;
        }
        return false;
    }
}
