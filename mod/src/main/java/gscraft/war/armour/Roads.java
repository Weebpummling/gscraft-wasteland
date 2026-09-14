package gscraft.war.armour;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import gscraft.war.GscraftWar;
import gscraft.war.world.Zone;
import gscraft.war.world.Zones;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.registries.ForgeRegistries;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * What counts as road under a vehicle ({@code /data/gscraft/gscraft_armour/roads.json}): the road mod's surfaces by
 * name anywhere, and per zone a list of plain blocks - Skadowsky's streets are vanilla stone work as built, accepted
 * for now (owner, 2026-09-13) until the road network pass.
 */
public final class Roads {
    private Roads() {}

    private record Surface(String zone, Set<ResourceLocation> blocks) {}

    private static final Map<String, List<String>> NAMESPACES = new LinkedHashMap<>();
    private static final List<Surface> SURFACES = new ArrayList<>();

    static {
        try (var in = Roads.class.getResourceAsStream("/data/gscraft/gscraft_armour/roads.json")) {
            if (in == null) {
                NAMESPACES.put("furenikusroads", List.of("road", "street"));
                GscraftWar.LOG.warn("[gscraft] no roads.json: the road mod's surfaces only");
            } else {
                JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
                if (root.has("namespaces")) for (var e : root.getAsJsonObject("namespaces").entrySet()) {
                    List<String> words = new ArrayList<>();
                    for (JsonElement w : e.getValue().getAsJsonArray()) words.add(w.getAsString());
                    NAMESPACES.put(e.getKey(), words);
                }
                if (root.has("surfaces")) for (JsonElement el : root.getAsJsonArray("surfaces")) {
                    JsonObject o = el.getAsJsonObject();
                    Set<ResourceLocation> blocks = new HashSet<>();
                    for (JsonElement b : o.getAsJsonArray("blocks")) {
                        ResourceLocation rl = ResourceLocation.tryParse(b.getAsString());
                        if (rl != null) blocks.add(rl);
                    }
                    SURFACES.add(new Surface(o.has("zone") ? o.get("zone").getAsString() : null, blocks));
                }
            }
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] roads.json is invalid: {}", ex.toString());
        }
        GscraftWar.LOG.info("[gscraft] roads: {} road mods, {} zone surfaces", NAMESPACES.size(), SURFACES.size());
    }

    /** the road mod's surfaces, anywhere */
    public static boolean isRoadBlock(BlockState state) {
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        if (key == null) return false;
        List<String> words = NAMESPACES.get(key.getNamespace());
        if (words == null) return false;
        for (String w : words) if (key.getPath().contains(w)) return true;
        return false;
    }

    /** road at a block: the road mod's surfaces, or a zone's own listed surfaces inside its box */
    public static boolean isRoad(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (isRoadBlock(state)) return true;
        if (SURFACES.isEmpty()) return false;
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        if (key == null) return false;
        for (Surface s : SURFACES) {
            if (!s.blocks().contains(key)) continue;
            if (s.zone() == null) return true;
            Zone zone = Zones.named(s.zone());
            if (zone != null && zone.hasBox() && zone.contains(pos.getX(), pos.getZ())) return true;
        }
        return false;
    }
}
