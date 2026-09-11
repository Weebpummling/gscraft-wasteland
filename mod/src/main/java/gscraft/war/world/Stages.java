package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Quest stages (quests §9). FTB Quests without FTB XMod Compat reads a stage as a tag on the player, and KubeJS's own
 * store wraps the same tags, so the mod writes the tag itself. {@link SiteData} is the record; the tags are re-applied
 * to every player on join, so a stage set while someone was offline is never missed. The team is everyone on the
 * server (the five players are one party); FTB Teams scoping is a later cut.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Stages {
    private Stages() {}

    public static boolean add(MinecraftServer server, String stage) {
        SiteData data = SiteData.get(server.overworld());
        boolean fresh = data.addStage(stage);
        for (ServerPlayer p : server.getPlayerList().getPlayers()) p.addTag(stage);
        if (fresh) GscraftWar.LOG.info("[gscraft] stage {} set", stage);
        return fresh;
    }

    public static boolean remove(MinecraftServer server, String stage) {
        SiteData data = SiteData.get(server.overworld());
        boolean had = data.removeStage(stage);
        for (ServerPlayer p : server.getPlayerList().getPlayers()) p.removeTag(stage);
        return had;
    }

    @SubscribeEvent
    public static void joined(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        SiteData data = SiteData.get(player.serverLevel());
        for (String stage : data.stages()) player.addTag(stage);
    }
}
