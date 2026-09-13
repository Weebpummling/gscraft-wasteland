package gscraft.war.survivor;

import gscraft.war.GscraftWar;
import gscraft.war.world.SiteData;
import gscraft.war.world.Stages;
import net.minecraft.advancements.Advancement;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.GameType;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.List;

/**
 * The test resets (owner, 2026-09-13): {@code /gscraft reset quests} wipes the quest sequence - FTB Quests' progress
 * for everyone online, every stage in the world's record, the site ladder, and every player's stage tags and
 * advancements; {@code /gscraft reset players} puts everyone online back at the start - survival, an empty inventory,
 * full health, the world spawn as their spawn, and the first join again (the title, Tune's lines, the kit);
 * {@code /gscraft reset all} does both, then clears Lootr's opened-container memory. Players offline keep their
 * tags and inventory until they come back: run these with everyone on.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class ResetCommands {
    private ResetCommands() {}

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("reset")
                        .then(Commands.literal("quests").executes(ctx -> quests(ctx.getSource())))
                        .then(Commands.literal("players").executes(ctx -> players(ctx.getSource())))
                        .then(Commands.literal("all").executes(ctx -> {
                            int n = quests(ctx.getSource()) + players(ctx.getSource());
                            MinecraftServer server = ctx.getSource().getServer();
                            int cleared = 0;
                            if (server.getCommands().getDispatcher().getRoot().getChild("lootr") != null) {
                                for (ServerPlayer p : server.getPlayerList().getPlayers()) cleared += run(server, "lootr clear " + p.getGameProfile().getName()) ? 1 : 0;
                            }
                            int lootr = cleared;
                            ctx.getSource().sendSuccess(() -> Component.literal("reset all: lootr memory cleared for " + lootr + " players"), true);
                            return n;
                        }))));
    }

    private static boolean run(MinecraftServer server, String command) {
        return server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), command) > 0;
    }

    /** the quest sequence wiped: FTB Quests' progress, the stages, the ladder, every player's stage tags and advancements */
    static int quests(CommandSourceStack src) {
        MinecraftServer server = src.getServer();
        SiteData data = SiteData.get(server.overworld());
        List<String> stages = new ArrayList<>(data.stages());
        for (String s : stages) Stages.remove(server, s);
        data.all().clear();
        data.contested = "";
        data.setDirty();
        Stages.refresh(server);
        List<Advancement> stageAdvancements = new ArrayList<>();
        for (Advancement a : server.getAdvancements().getAllAdvancements()) {
            if (a.getId().getNamespace().equals(GscraftWar.MODID) && a.getId().getPath().startsWith("stage/")) stageAdvancements.add(a);
        }
        int players = 0, ftb = 0;
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            for (String tag : new ArrayList<>(p.getTags())) {
                if (stages.contains(tag) || tag.startsWith("seen_") || tag.startsWith("bp_") || tag.endsWith("_taken") || tag.endsWith("_held") || tag.endsWith("_scouted") || tag.endsWith("_looted") || tag.endsWith("_defended") || tag.endsWith("_lost") || tag.equals("joined") || tag.equals("marshall_speaks")) p.removeTag(tag);
            }
            for (Advancement a : stageAdvancements) {
                var progress = p.getAdvancements().getOrStartProgress(a);
                if (progress.hasProgress()) for (String c : progress.getCompletedCriteria()) p.getAdvancements().revoke(a, c);
            }
            if (run(server, "ftbquests change_progress " + p.getGameProfile().getName() + " reset 1")) ftb++;
            players++;
        }
        String line = "reset quests: " + stages.size() + " stages cleared, the ladder cleared, " + players + " players' tags and advancements revoked, FTB Quests progress reset for " + ftb;
        src.sendSuccess(() -> Component.literal(line), true);
        GscraftWar.LOG.info("[gscraft] {}", line);
        return stages.size();
    }

    /** everyone online back at the start: survival, empty, healed, the world spawn, the first join again */
    static int players(CommandSourceStack src) {
        MinecraftServer server = src.getServer();
        ServerLevel overworld = server.overworld();
        BlockPos spawn = overworld.getSharedSpawnPos();
        SiteData data = SiteData.get(overworld);
        int n = 0;
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            p.setGameMode(GameType.SURVIVAL);
            p.getInventory().clearContent();
            p.setHealth(p.getMaxHealth());
            p.getFoodData().setFoodLevel(20);
            p.getFoodData().setSaturation(5f);
            p.removeAllEffects();
            p.setRespawnPosition(overworld.dimension(), null, 0f, false, false);
            p.teleportTo(overworld, spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5, p.getYRot(), p.getXRot());
            data.stations().remove(p.getUUID());
            data.setDirty();
            p.removeTag("joined");
            for (Survivors.Def d : Survivors.ALL) p.removeTag("seen_" + d.id());
            SurvivorEvents.firstJoin(p);
            n++;
        }
        int count = n;
        String line = "reset players: " + count + " at " + spawn.toShortString() + " in survival with the starting kit";
        src.sendSuccess(() -> Component.literal(line), true);
        GscraftWar.LOG.info("[gscraft] {}", line);
        return n;
    }
}
