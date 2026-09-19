package gscraft.war.world;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import gscraft.war.GscraftWar;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceLocationArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.LootTableReference;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import com.mojang.brigadier.arguments.IntegerArgumentType;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Pattern;

/**
 * Every chest in the world is part of ONE loot system (loot design 2026-09-19). The map's containers carry other mods'
 * tables - vanilla dungeons and villages, Underground Bunkers, Lost Cities, the Keerdm gun and ammo chests, Apotheosis -
 * and those hand out diamonds, enchanted armour and working TACZ guns: everything the design's first rule forbids and
 * nothing the economy uses. A world scan counted them (2026-09-19: 255 simple_dungeon, 113 bunker, 91 Keerdm, 29 Lost
 * Cities in the sixty largest region files). So any table whose path begins {@code chests/} and is not ours is REPLACED,
 * as it loads, by a reference to one of the design's building tables, by the first rule in
 * {@code data/gscraft/gscraft_loot/remap.json} whose pattern matches its id. The rules are read from the jar, not the
 * datapack: tables load before any reload listener of ours could have run. Lootr then rolls the replaced table per player
 * like any other. Block drops, entity drops and gameplay tables are never touched (their paths do not begin chests/).
 * {@code /gscraft loot remap <id>} says where an id goes; {@code /gscraft loot roll <table> <n>} rolls any table n times
 * and totals what came out, which is how tools/war_phase46.py proves the whole system headless.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class LootRemap {
    private LootRemap() {}

    private record Rule(Pattern match, ResourceLocation table) {}

    private static List<Rule> rules;
    private static int replaced;

    private static synchronized List<Rule> rules() {
        if (rules != null) return rules;
        List<Rule> out = new ArrayList<>();
        try (var in = LootRemap.class.getResourceAsStream("/data/gscraft/gscraft_loot/remap.json")) {
            if (in != null) {
                JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
                JsonArray arr = root.getAsJsonArray("rules");
                for (JsonElement el : arr) {
                    JsonObject o = el.getAsJsonObject();
                    out.add(new Rule(Pattern.compile(o.get("match").getAsString()), new ResourceLocation(o.get("table").getAsString())));
                }
            }
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] loot remap rules are invalid: {}", ex.toString());
        }
        rules = out;
        return out;
    }

    /** the design's table a foreign chest table becomes, or null when it is left alone */
    public static ResourceLocation target(ResourceLocation id) {
        if (id.getNamespace().equals(GscraftWar.MODID) || !id.getPath().startsWith("chests/")) return null;
        String s = id.toString();
        for (Rule r : rules()) if (r.match().matcher(s).matches()) return r.table().equals(id) ? null : r.table();   // a rule naming the id itself leaves it alone
        return null;
    }

    /** LOWEST: after every other mod's listener. Immersive Weathering (through Moonlight) ADDS a pool to vanilla chest tables in
     * this same event; at the default priority it ran after us and its moss clumps came out of a shipwreck's 'store' (phase 46) */
    @SubscribeEvent(priority = net.minecraftforge.eventbus.api.EventPriority.LOWEST)
    public static void load(LootTableLoadEvent event) {
        ResourceLocation to = target(event.getName());
        if (to == null) return;
        LootTable table = LootTable.lootTable().withPool(LootPool.lootPool().name("gscraft_remap").add(LootTableReference.lootTableReference(to))).build();
        table.setLootTableId(event.getName());
        event.setTable(table);
        if (replaced++ == 0) GscraftWar.LOG.info("[gscraft] loot remap: foreign chest tables are being replaced ({} rules); the first is {} -> {}", rules().size(), event.getName(), to);
    }

    /** a table rolled n times with a chest's context at the world spawn: item id -> total count */
    public static Map<String, Integer> roll(ServerLevel level, ResourceLocation id, int n) {
        Map<String, Integer> out = new TreeMap<>();
        LootTable table = level.getServer().getLootData().getLootTable(id);
        BlockPos at = level.getSharedSpawnPos();
        for (int i = 0; i < n; i++) {
            LootParams params = new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN, Vec3.atCenterOf(at)).create(LootContextParamSets.CHEST);
            for (ItemStack s : table.getRandomItems(params)) {
                if (s.isEmpty()) continue;
                out.merge(String.valueOf(ForgeRegistries.ITEMS.getKey(s.getItem())), s.getCount(), Integer::sum);
            }
        }
        return out;
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("loot")
                        .then(Commands.literal("roll").then(Commands.argument("table", ResourceLocationArgument.id())
                                .then(Commands.argument("n", IntegerArgumentType.integer(1, 20000)).executes(ctx -> {
                                    ResourceLocation id = ResourceLocationArgument.getId(ctx, "table");
                                    int n = IntegerArgumentType.getInteger(ctx, "n");
                                    boolean known = ctx.getSource().getServer().getLootData().getKeys(net.minecraft.world.level.storage.loot.LootDataType.TABLE).contains(id);
                                    Map<String, Integer> got = roll(ctx.getSource().getLevel(), id, n);
                                    StringBuilder sb = new StringBuilder(id + (known ? "" : " (NO SUCH TABLE)") + " x" + n + ":");
                                    got.forEach((k, v) -> sb.append(' ').append(k).append('=').append(v));
                                    ctx.getSource().sendSuccess(() -> Component.literal(sb.toString()), false);
                                    return got.size();
                                }))))
                        .then(Commands.literal("remap").then(Commands.argument("table", ResourceLocationArgument.id()).executes(ctx -> {
                            ResourceLocation id = ResourceLocationArgument.getId(ctx, "table");
                            ResourceLocation to = target(id);
                            ctx.getSource().sendSuccess(() -> Component.literal(id + " -> " + (to == null ? "left alone" : to.toString())), false);
                            return to == null ? 0 : 1;
                        })))
                        .then(Commands.literal("tables").executes(ctx -> {
                            List<String> ours = new ArrayList<>();
                            for (ResourceLocation id : ctx.getSource().getServer().getLootData().getKeys(net.minecraft.world.level.storage.loot.LootDataType.TABLE)) {
                                if (id.getNamespace().equals(GscraftWar.MODID) && (id.getPath().startsWith("building/") || id.getPath().startsWith("sites/"))) ours.add(id.getPath());
                            }
                            java.util.Collections.sort(ours);
                            ctx.getSource().sendSuccess(() -> Component.literal(ours.size() + " tables: " + String.join(" ", ours) + "; foreign chest tables replaced " + replaced), false);
                            return ours.size();
                        }))));
    }
}
