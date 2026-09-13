package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Quest stages (quests §9; system doc 2026-09-13 §5, ruling R2). A stage is a string in the world's record ({@link SiteData}),
 * a tag on every player, and - since slice build 1 - the advancement {@code gscraft:stage/<name>} granted to every player,
 * which FTB Quests' own advancement task reads; the advancement files come from tools/stages.py (the registry). Both the
 * tag and the advancement are re-applied on join, so a stage set while someone was offline is never missed, and both are
 * taken back when the stage is removed. The team is everyone on the server (the five players are one party); FTB Teams
 * scoping is a later cut. A stage with no advancement file is still a tag; it is logged once.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Stages {
    private Stages() {}

    /** the set as last read from the world's record: for the zones, which have no server in hand (refreshed every
     *  second by the loop and at once by add/remove) */
    private static volatile java.util.Set<String> live = java.util.Set.of();

    public static boolean isSet(String stage) {
        return live.contains(stage);
    }

    public static void refresh(MinecraftServer server) {
        live = java.util.Set.copyOf(SiteData.get(server.overworld()).stages());
    }

    public static boolean add(MinecraftServer server, String stage) {
        SiteData data = SiteData.get(server.overworld());
        boolean fresh = data.addStage(stage);
        live = java.util.Set.copyOf(data.stages());
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            p.addTag(stage);
            grant(server, p, stage, true);
        }
        if (fresh) GscraftWar.LOG.info("[gscraft] stage {} set", stage);
        return fresh;
    }

    private static final java.util.Set<String> noAdvancement = java.util.concurrent.ConcurrentHashMap.newKeySet();

    /** the stage's advancement granted (or revoked) on a player; a stage without one is logged once */
    public static void grant(MinecraftServer server, ServerPlayer player, String stage, boolean on) {
        net.minecraft.advancements.Advancement adv = server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation(GscraftWar.MODID, "stage/" + stage));
        if (adv == null) {
            if (noAdvancement.add(stage)) GscraftWar.LOG.warn("[gscraft] stage {} has no advancement (tools/stages.py); the tag alone carries it", stage);
            return;
        }
        if (on) player.getAdvancements().award(adv, "set");
        else player.getAdvancements().revoke(adv, "set");
    }

    public static boolean remove(MinecraftServer server, String stage) {
        SiteData data = SiteData.get(server.overworld());
        boolean had = data.removeStage(stage);
        live = java.util.Set.copyOf(data.stages());
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            p.removeTag(stage);
            grant(server, p, stage, false);
        }
        return had;
    }

    @SubscribeEvent
    public static void joined(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        SiteData data = SiteData.get(player.serverLevel());
        for (String stage : data.stages()) {
            player.addTag(stage);
            grant(player.server, player, stage, true);
        }
    }
}
