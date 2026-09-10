package gscraft.war.faction;

import com.google.gson.Gson;
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
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Who stands with whom, as datapack JSON. It replaces Mob Factions for everything the mod owns: loyalty is read
 * per entity, so two armies built from the same kind of body can still be at war. The files reload with
 * {@code /reload}, unlike the In Control rules this layer retires.
 */
public final class Factions extends SimpleJsonResourceReloadListener {
    public static final String FOLDER = "gscraft_factions";
    private static final Gson GSON = new GsonBuilder().create();

    private static volatile Map<String, FactionDef> byId = Map.of();
    private static volatile Map<ResourceLocation, String> byType = Map.of();

    public Factions() {
        super(GSON, FOLDER);
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        Map<String, FactionDef> ids = new LinkedHashMap<>();
        Map<ResourceLocation, String> types = new HashMap<>();
        files.forEach((file, json) -> {
            try {
                JsonObject o = GsonHelper.convertToJsonObject(json, "faction");
                Set<ResourceLocation> members = new LinkedHashSet<>();
                for (JsonElement e : GsonHelper.getAsJsonArray(o, "members", new JsonArray())) {
                    members.add(new ResourceLocation(e.getAsString()));
                }
                Set<String> hostile = new LinkedHashSet<>();
                for (JsonElement e : GsonHelper.getAsJsonArray(o, "hostile", new JsonArray())) {
                    hostile.add(e.getAsString());
                }
                PlayerStance players = PlayerStance.valueOf(
                        GsonHelper.getAsString(o, "players", "neutral").toUpperCase(Locale.ROOT));
                boolean inject = GsonHelper.getAsBoolean(o, "inject_targeting", false);
                String id = file.getPath();
                ids.put(id, new FactionDef(id, Collections.unmodifiableSet(members),
                        Collections.unmodifiableSet(hostile), players, inject));
                for (ResourceLocation m : members) types.put(m, id);
            } catch (Exception ex) {
                // a bad file is skipped and named, never swallowed
                GscraftWar.LOG.error("[gscraft] faction file {} is invalid: {}", file, ex.toString());
            }
        });
        byId = Collections.unmodifiableMap(ids);
        byType = Collections.unmodifiableMap(types);
        GscraftWar.LOG.info("[gscraft] factions loaded: {}", ids.keySet());
    }

    public static Map<String, FactionDef> all() {
        return byId;
    }

    public static FactionDef def(String id) {
        return id == null ? null : byId.get(id);
    }

    public static String factionOf(Entity e) {
        if (e instanceof FactionMember m) return m.factionId();
        ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(e.getType());
        return key == null ? null : byType.get(key);
    }

    /** a attacks b on sight. One-way: the Dead can hunt a faction that only defends itself. */
    public static boolean hostile(Entity a, Entity b) {
        if (a == b) return false;
        String fa = factionOf(a);
        String fb = factionOf(b);
        if (fa == null || fb == null || fa.equals(fb)) return false;
        FactionDef d = byId.get(fa);
        return d != null && d.hostile().contains(fb);
    }

    /** same faction: no targeting, no friendly fire */
    public static boolean allied(Entity a, Entity b) {
        String fa = factionOf(a);
        return fa != null && fa.equals(factionOf(b));
    }

    public static boolean hostileToPlayer(Mob mob, Player player) {
        FactionDef d = def(factionOf(mob));
        if (d == null) return false;
        return switch (d.players()) {
            case HOSTILE -> true;
            case NEUTRAL -> false;
            case PROVOKED -> mob instanceof Grudging g && g.holdsGrudge(player.getUUID());
        };
    }
}
