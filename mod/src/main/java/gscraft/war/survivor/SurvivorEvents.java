package gscraft.war.survivor;

import com.mojang.brigadier.arguments.StringArgumentType;
import gscraft.war.GscraftWar;
import gscraft.war.world.Stages;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraftforge.registries.ForgeRegistries;

import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;

/**
 * The survivors as the book (system doc 2026-09-13 §7 build 6): right-click on one opens the quest book at their
 * chapter ({@code /ftbquests open_book #<chapter>}, run as the player) and plays their hello line the first time;
 * a player's first join is the title, Tune's lines and the kit (onboarding §2/§8). {@code /gscraft say|survivors|kit|join}
 * for the console and the tests.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class SurvivorEvents {
    private SurvivorEvents() {}

    private record Later(UUID player, long at, java.util.function.Consumer<ServerPlayer> action) {}

    private static final List<Later> LATER = new ArrayList<>();

    /** something done to the player this many ticks from now, if they are still on */
    public static void later(ServerPlayer p, int ticks, java.util.function.Consumer<ServerPlayer> action) {
        LATER.add(new Later(p.getUUID(), p.server.getTickCount() + ticks, action));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Say.tick(event.getServer());
        if (LATER.isEmpty()) return;
        long now = event.getServer().getTickCount();
        for (Iterator<Later> it = LATER.iterator(); it.hasNext(); ) {
            Later l = it.next();
            if (l.at() > now) continue;
            it.remove();
            ServerPlayer p = event.getServer().getPlayerList().getPlayer(l.player());
            if (p != null) l.action().accept(p);
        }
    }

    /**
     * A survivor takes no damage from anything (owner 2026-09-13: Marshall died to the guns). The summons carry
     * Invulnerable, but a creative player's own rounds bypass that flag, and so does anything that skips the flag;
     * the attack is refused here at the source. Only what bypasses invulnerability outright (the console's kill,
     * which the summons use to re-issue a survivor) still lands.
     */
    @SubscribeEvent
    public static void attacked(net.minecraftforge.event.entity.living.LivingAttackEvent event) {
        if (!event.getEntity().getTags().contains("gscraft_npc")) return;
        if (event.getSource().is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return;
        event.setCanceled(true);
    }

    /** nothing hunts a survivor: the Dead would path into the compound after the villagers otherwise */
    @SubscribeEvent
    public static void target(net.minecraftforge.event.entity.living.LivingChangeTargetEvent event) {
        if (event.getNewTarget() != null && event.getNewTarget().getTags().contains("gscraft_npc")) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void interact(PlayerInteractEvent.EntityInteract event) {
        if (event.getHand() != InteractionHand.MAIN_HAND) return;
        Survivors.Def d = Survivors.byTag(event.getTarget());
        if (d == null) return;
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        if (event.getEntity() instanceof ServerPlayer p) open(p, d);
    }

    /** the survivor's right-click: the hello line once, then the book at their chapter */
    public static void open(ServerPlayer p, Survivors.Def d) {
        if (p.addTag("seen_" + d.id())) {
            Stages.grant(p.server, p, "seen_" + d.id(), true);
            Say.queue(p, d.id(), "hello", true);
        }
        p.server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withSuppressedOutput(), "ftbquests open_book #" + d.chapter());
    }

    @SubscribeEvent
    public static void login(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer p && !p.getTags().contains("joined")) firstJoin(p);
    }

    /**
     * A death no longer disarms a player for good (slice review 2026-09-19, finding 4; owner: re-issue, not keepInventory).
     * Whatever the kit marks {@code "respawn": true} is given again, unless the player already carries that item - so a
     * revive, or keepInventory one day, hands out nothing twice. What fell stays where it fell.
     */
    @SubscribeEvent
    public static void respawn(PlayerEvent.PlayerRespawnEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || event.isEndConquered()) return;
        int given = reissue(p) + gscraft.war.world.Upgrades.afterRespawn(p);   // Medical 2 adds rounds and bandages
        if (given > 0) GscraftWar.LOG.info("[gscraft] respawn: {} given {} kit stacks again", p.getGameProfile().getName(), given);
    }

    public static int reissue(ServerPlayer p) {
        return Survivors.give(p, true);
    }

    /** the first join: the title card, the kit, Tune's lines from five seconds on and twenty apart */
    public static void firstJoin(ServerPlayer p) {
        p.addTag("joined");
        Stages.grant(p.server, p, "joined", true);
        p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 70, 20));
        p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(Survivors.TITLE)));
        if (!Survivors.SUBTITLE.isEmpty()) p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket(Component.literal(Survivors.SUBTITLE)));
        // the book opens on its first chapter once the title has faded: the one page that says where you are
        if (!Survivors.OPEN_CHAPTER.isEmpty()) later(p, 110, pl -> pl.server.getCommands().performPrefixedCommand(pl.createCommandSourceStack().withSuppressedOutput(), "ftbquests open_book #" + Survivors.OPEN_CHAPTER));
        Survivors.give(p, false);
        Say.hold(p, 100);
        for (String[] l : Survivors.JOIN_LINES) Say.queue(p, l[0], l[1], false);
        GscraftWar.LOG.info("[gscraft] first join: {}", p.getGameProfile().getName());
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("say").then(Commands.argument("npc", StringArgumentType.word()).then(Commands.argument("key", StringArgumentType.word())
                        .executes(ctx -> {
                            String line = Say.rendered(StringArgumentType.getString(ctx, "npc"), StringArgumentType.getString(ctx, "key"));
                            ctx.getSource().sendSuccess(() -> Component.literal(line), false);
                            return 1;
                        })
                        .then(Commands.argument("targets", EntityArgument.players()).executes(ctx -> {
                            Collection<ServerPlayer> targets = EntityArgument.getPlayers(ctx, "targets");
                            int n = 0;
                            for (ServerPlayer p : targets) if (Say.queue(p, StringArgumentType.getString(ctx, "npc"), StringArgumentType.getString(ctx, "key"), false)) n++;
                            int count = n;
                            ctx.getSource().sendSuccess(() -> Component.literal("queued for " + count), false);
                            return n;
                        })))))
                .then(Commands.literal("survivors").executes(ctx -> survivors(ctx.getSource())))
                .then(Commands.literal("kit").executes(ctx -> {
                    for (ItemStack s : Survivors.kit()) ctx.getSource().sendSuccess(() -> Component.literal(s.getCount() + " " + ForgeRegistries.ITEMS.getKey(s.getItem()) + (s.hasTag() ? " " + s.getTag() : "")), false);
                    return Survivors.kit().size();
                }).then(Commands.literal("respawn").executes(ctx -> {   // what a death gives back, listed; with a player, given as the respawn gives it
                    for (ItemStack s : Survivors.kit(true)) ctx.getSource().sendSuccess(() -> Component.literal(s.getCount() + " " + ForgeRegistries.ITEMS.getKey(s.getItem()) + (s.hasTag() ? " " + s.getTag() : "")), false);
                    return Survivors.kit(true).size();
                }).then(Commands.argument("player", EntityArgument.player()).executes(ctx -> {
                    int given = reissue(EntityArgument.getPlayer(ctx, "player"));
                    ctx.getSource().sendSuccess(() -> Component.literal("given again: " + given + " stacks"), false);
                    return given;
                }))).then(Commands.argument("player", EntityArgument.player()).executes(ctx -> {
                    ServerPlayer p = EntityArgument.getPlayer(ctx, "player");
                    Survivors.give(p, false);
                    return 1;
                })))
                .then(Commands.literal("join").then(Commands.argument("player", EntityArgument.player()).executes(ctx -> {
                    // the first join again, for a look at it
                    ServerPlayer p = EntityArgument.getPlayer(ctx, "player");
                    p.removeTag("joined");
                    for (Survivors.Def d : Survivors.ALL) p.removeTag("seen_" + d.id());
                    gscraft.war.journal.FieldNotes.clear(p);
                    firstJoin(p);
                    return 1;
                }))));
    }

    private static int survivors(CommandSourceStack src) {
        MinecraftServer server = src.getServer();
        int ok = 0;
        for (Survivors.Def d : Survivors.ALL) {
            boolean hello = !Component.translatable("gscraft.say." + d.id() + ".hello").getString().startsWith("gscraft.say.");
            boolean chapter = Files.exists(FMLPaths.CONFIGDIR.get().resolve("ftbquests/quests/chapters/" + d.chapter() + ".snbt"));
            boolean adv = server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation(GscraftWar.MODID, "stage/seen_" + d.id())) != null;
            String line = d.id() + ": " + d.name() + ", " + d.profession() + ", tag " + d.tag() + ", chapter #" + d.chapter() + (chapter ? " (file present)" : " (NO FILE)")
                    + (hello ? ", hello line" : ", NO HELLO LINE") + (adv ? ", seen advancement" : ", NO SEEN ADVANCEMENT");
            src.sendSuccess(() -> Component.literal(line), false);
            if (hello && chapter && adv) ok++;
        }
        List<String> missing = new java.util.ArrayList<>();
        for (String[] l : Survivors.JOIN_LINES) if (Component.translatable("gscraft.say." + l[0] + "." + l[1]).getString().startsWith("gscraft.say.")) missing.add(l[0] + "." + l[1]);
        String summary = Survivors.ALL.size() + " survivors, " + ok + " complete; title " + Survivors.TITLE + "; join lines " + Survivors.JOIN_LINES.size() + ", missing " + missing
                + "; kit " + Survivors.kit().size() + " stacks of " + Survivors.KIT.size() + " entries";
        src.sendSuccess(() -> Component.literal(summary), false);
        return ok;
    }
}
