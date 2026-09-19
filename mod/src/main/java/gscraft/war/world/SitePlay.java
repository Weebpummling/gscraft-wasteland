package gscraft.war.world;

import gscraft.war.GscraftWar;
import gscraft.war.world.SiteData.Progress;
import gscraft.war.world.SiteData.State;
import gscraft.war.world.Sites.SiteDef;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.Map;

/**
 * Play moves a strongpoint (slice review 2026-09-19, finding 1: the hospital could not be reached by play). The ladder
 * unknown -> scouted -> looted -> held was climbed by the operator's {@code /gscraft site <id> set} and by nothing else,
 * and the claim marker is refused until a site is looted - so a player who built a marker was turned away at the door.
 * <ul>
 * <li><b>Scouted</b>: players on foot inside the site's box for {@link #SCOUT_SECONDS} seconds in all. Creative and
 * spectator do not count: an operator flying over must not move the game.</li>
 * <li><b>Looted</b>: {@link #LOOT_GOAL} different Lootr containers inside the box opened (a right-click; Lootr's loot is
 * per player, so searching costs nobody anything). A search on unscouted ground scouts it first.</li>
 * </ul>
 * Only strongpoints climb this way (a site with no alias); the building takes are stages set by their quests. The
 * console stand-ins {@code /gscraft site <id> presence <s>} and {@code ... search <pos>} run the same two methods the
 * events call, so the chain can be played headless with nothing standing in for the rules.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class SitePlay {
    private SitePlay() {}

    public static int SCOUT_SECONDS = 5, LOOT_GOAL = 6;
    private static final Map<String, Integer> presence = new HashMap<>();

    public static boolean strongpoint(SiteDef site) {
        return site.alias() == null;
    }

    private static SiteDef strongpointAt(int x, int z) {
        for (SiteDef s : Sites.all().values()) if (strongpoint(s) && s.contains(x, z)) return s;
        return null;
    }

    private static void tellAll(ServerLevel level, String key, Object... args) {
        level.getServer().getPlayerList().broadcastSystemMessage(Component.translatable(key, args).withStyle(ChatFormatting.GOLD), false);
    }

    /** seconds of players' presence inside the box; at SCOUT_SECONDS the site is scouted */
    public static String presence(ServerLevel level, SiteDef site, int seconds) {
        if (!strongpoint(site)) return site.id() + " is a building take, not a strongpoint: its quest sets its stage";
        Progress p = SiteData.get(level).progress(site.id());
        if (p.state != State.UNKNOWN) return site.id() + " is already " + p.state.name().toLowerCase();
        int total = presence.merge(site.id(), seconds, Integer::sum);
        if (total < SCOUT_SECONDS) return site.id() + ": " + total + " of " + SCOUT_SECONDS + " s inside";
        presence.remove(site.id());
        String msg = Loop.advance(level, site, State.SCOUTED);
        if (p.state == State.SCOUTED) {
            tellAll(level, "gscraft.site.scouted", site.name());
            GscraftWar.LOG.info("[gscraft] {}: scouted by presence", site.id());
        }
        return msg;
    }

    /** a Lootr container inside a strongpoint's box searched; the LOOT_GOAL'th different one loots the site */
    public static String searched(ServerLevel level, BlockPos pos, ServerPlayer who) {
        SiteDef site = strongpointAt(pos.getX(), pos.getZ());
        if (site == null) return "no strongpoint at " + pos.toShortString();
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(level.getBlockState(pos).getBlock());
        if (key == null || !key.getNamespace().equals("lootr")) return "nothing to search at " + pos.toShortString() + " (" + key + ")";
        SiteData data = SiteData.get(level);
        Progress p = data.progress(site.id());
        if (p.state == State.UNKNOWN) presence(level, site, SCOUT_SECONDS);   // searching a room is seeing the place
        if (p.state != State.SCOUTED) return site.id() + " is " + p.state.name().toLowerCase() + ": nothing left to find out";
        if (!p.searched.add(pos.asLong())) return site.id() + ": that one was searched already (" + p.searched.size() + " of " + LOOT_GOAL + ")";
        data.setDirty();
        int n = p.searched.size();
        if (who != null) who.displayClientMessage(Component.translatable("gscraft.site.searching", site.name(), n, LOOT_GOAL), true);
        if (n < LOOT_GOAL) return site.id() + ": " + n + " of " + LOOT_GOAL + " searched";
        String msg = Loop.advance(level, site, State.LOOTED);
        if (p.state == State.LOOTED) {
            tellAll(level, "gscraft.site.looted", site.name());
            GscraftWar.LOG.info("[gscraft] {}: looted after {} searches", site.id(), n);
        }
        return msg;
    }

    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer p) || p.tickCount % 20 != 0) return;
        if (p.isCreative() || p.isSpectator() || !p.isAlive() || p.level().dimension() != Level.OVERWORLD) return;
        SiteDef site = strongpointAt(p.getBlockX(), p.getBlockZ());
        if (site == null) return;
        if (SiteData.get(p.serverLevel()).progress(site.id()).state == State.UNKNOWN) presence(p.serverLevel(), site, 1);
    }

    @SubscribeEvent
    public static void opened(PlayerInteractEvent.RightClickBlock event) {
        if (event.getHand() != InteractionHand.MAIN_HAND || !(event.getEntity() instanceof ServerPlayer p)) return;
        if (p.isSpectator() || p.level().dimension() != Level.OVERWORLD) return;
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(p.level().getBlockState(event.getPos()).getBlock());
        if (key != null && key.getNamespace().equals("lootr")) searched(p.serverLevel(), event.getPos(), p);
    }
}
