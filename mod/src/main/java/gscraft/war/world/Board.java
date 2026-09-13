package gscraft.war.world;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import gscraft.war.GscraftWar;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * The strongpoint board on the hall's ground floor (camp spec §2, ruling R4): six columns of concrete, one per
 * strongpoint, coloured by state; a lamp lit while a site is contested. The blocks are the datapack's
 * {@code gscraft:board_<site>_<state>} and {@code board_lamp_on/off} functions (tools/board.py, which also finds the
 * wall and writes {@code gscraft_board/board.json}); the loop calls them on every state change. Looking at a column
 * reads its state on the action bar (interface §3.3).
 */
public final class Board {
    private Board() {}

    private static boolean loaded;
    private static int ox, oy, oz, dx, dz, width = 2, height = 3;
    private static final List<String> COLUMNS = new ArrayList<>();
    private static final Set<String> missing = new HashSet<>();

    static {
        load();
    }

    private static void load() {
        try (var in = Board.class.getResourceAsStream("/data/gscraft/gscraft_board/board.json")) {
            if (in == null) {
                GscraftWar.LOG.info("[gscraft] no board.json: no board");
                return;
            }
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonArray o = root.getAsJsonArray("origin");
            ox = o.get(0).getAsInt();
            oy = o.get(1).getAsInt();
            oz = o.get(2).getAsInt();
            JsonArray a = root.getAsJsonArray("along");
            dx = a.get(0).getAsInt();
            dz = a.get(1).getAsInt();
            if (root.has("width")) width = root.get("width").getAsInt();
            if (root.has("height")) height = root.get("height").getAsInt();
            for (JsonElement el : root.getAsJsonArray("columns")) COLUMNS.add(el.getAsString());
            loaded = true;
            GscraftWar.LOG.info("[gscraft] board at {} {} {}, {} columns", ox, oy, oz, COLUMNS.size());
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] board.json is invalid: {}", ex.toString());
        }
    }

    public static boolean loaded() {
        return loaded;
    }

    public static List<String> columns() {
        return COLUMNS;
    }

    /** the site whose column the block belongs to (the concrete, or the sign row above it), or null */
    public static String column(BlockPos pos) {
        if (!loaded) return null;
        if (dx != 0 ? pos.getZ() != oz && pos.getZ() != oz + 1 && pos.getZ() != oz - 1 : pos.getX() != ox && pos.getX() != ox + 1 && pos.getX() != ox - 1) return null;
        int along = (pos.getX() - ox) * dx + (pos.getZ() - oz) * dz;
        if (pos.getY() < oy || pos.getY() > oy + height || along < 0 || along >= COLUMNS.size() * width) return null;
        return COLUMNS.get(along / width);
    }

    /** the column recoloured for a state, if the datapack has the function */
    public static void apply(ServerLevel level, String site, String state) {
        if (!loaded || !COLUMNS.contains(site)) return;
        function(level, "gscraft:board_" + site + "_" + state.toLowerCase(Locale.ROOT));
    }

    public static void lamp(ServerLevel level, boolean on) {
        if (!loaded) return;
        function(level, on ? "gscraft:board_lamp_on" : "gscraft:board_lamp_off");
    }

    private static void function(ServerLevel level, String id) {
        ResourceLocation key = ResourceLocation.tryParse(id);
        if (key == null || level.getServer().getFunctions().get(key).isEmpty()) {
            if (missing.add(id)) GscraftWar.LOG.warn("[gscraft] board function {} is not loaded (tools/board.py)", id);
            return;
        }
        Loop.run(level, List.of(id));
    }

    /** the action bar while looking at a column: {@code THE HOSPITAL — held — garrison 6/6} */
    public static String readout(ServerLevel level, String site) {
        Sites.SiteDef def = Sites.get(site);
        String name = def == null ? site.toUpperCase(Locale.ROOT).replace('_', ' ') : def.name();
        if (def == null) return name + " — unknown";
        SiteData data = SiteData.get(level);
        SiteData.Progress p = data.progress(site);
        StringBuilder s = new StringBuilder(name).append(" — ").append(p.lost ? "lost" : p.state.name().toLowerCase(Locale.ROOT));
        long left = p.deadline - data.online;
        if (p.phase == SiteData.Phase.ASSAULT) s.append(" — hold ").append(mmss(left));
        else if (p.phase == SiteData.Phase.FORTIFY) s.append(" — clock ").append(mmss(left));
        else if (p.phase == SiteData.Phase.COUNTER) s.append(" — the gate");
        if (p.guardTarget > 0) s.append(" — garrison ").append(Loop.guardCount(level, def)).append("/").append(p.guardTarget);
        return s.toString();
    }

    private static String mmss(long ticks) {
        long sec = Math.max(0, ticks) / 20;
        return String.format("%d:%02d", sec / 60, sec % 60);
    }

    public static String describe() {
        return loaded ? "board at " + ox + " " + oy + " " + oz + " along " + dx + "," + dz + ", " + width + "x" + height + " per column: " + COLUMNS : "no board (gscraft_board/board.json)";
    }
}
