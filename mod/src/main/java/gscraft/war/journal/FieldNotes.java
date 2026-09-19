package gscraft.war.journal;

import com.mojang.brigadier.arguments.StringArgumentType;
import gscraft.war.GscraftWar;
import gscraft.war.armour.Vehicles;
import gscraft.war.world.Stages;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.EntityMountEvent;
import net.minecraftforge.event.entity.living.MobEffectEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Field notes (onboarding §4.5, interface §3.8): the journal's one chapter that writes itself. The first time a thing
 * happens to a player - a death, a bulky item in the pack, a seat in a vehicle, an infection, the warning before a
 * counterattack - the per-player stage {@code note_<key>} is granted (tag + advancement, like {@code seen_<npc>}), and
 * the chapter's entry for it, invisible until its one advancement task is done, appears with two lines. The rule gets
 * its name after the fact; nothing here announces one. A quiet action-bar line says the journal grew.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class FieldNotes {
    private FieldNotes() {}

    public static final List<String> KEYS = List.of("death", "bulky", "vehicle", "infected", "warning");

    /** the note granted once per player; true when it was new */
    public static boolean note(ServerPlayer player, String key) {
        if (!KEYS.contains(key) || !player.addTag("note_" + key)) return false;
        Stages.grant(player.server, player, "note_" + key, true);
        player.displayClientMessage(Component.translatable("gscraft.journal.note").withStyle(ChatFormatting.GRAY), true);
        GscraftWar.LOG.info("[gscraft] journal: field note {} for {}", key, player.getGameProfile().getName());
        return true;
    }

    /** the same note for everyone online (the loop's warning) */
    public static void noteAll(MinecraftServer server, String key) {
        for (ServerPlayer p : server.getPlayerList().getPlayers()) note(p, key);
    }

    /** the reset's side: the tags and advancements off, so a fresh run earns them again */
    public static void clear(ServerPlayer player) {
        for (String key : KEYS) {
            if (player.removeTag("note_" + key)) Stages.grant(player.server, player, "note_" + key, false);
        }
        player.getPersistentData().remove(Pins.OWNED);
    }

    @SubscribeEvent
    public static void respawned(PlayerEvent.PlayerRespawnEvent event) {
        if (!event.isEndConquered() && event.getEntity() instanceof ServerPlayer p) note(p, "death");
    }

    @SubscribeEvent
    public static void mounted(EntityMountEvent event) {
        if (event.isMounting() && event.getEntityMounting() instanceof ServerPlayer p && Vehicles.isVehicle(event.getEntityBeingMounted())) note(p, "vehicle");
    }

    @SubscribeEvent
    public static void effect(MobEffectEvent.Added event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || event.getEffectInstance() == null) return;
        ResourceLocation key = ForgeRegistries.MOB_EFFECTS.getKey(event.getEffectInstance().getEffect());
        if (key != null && key.getNamespace().equals("hordes") && key.getPath().contains("infect")) note(p, "infected");
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("journal")
                        .then(Commands.literal("check").executes(ctx -> {
                            ctx.getSource().sendSuccess(() -> Component.literal("journal: FTB Quests " + (Pins.api() ? "reachable" : "NOT reachable") + "; notes " + KEYS), false);
                            return Pins.api() ? 1 : 0;
                        }))
                        .then(Commands.literal("status").then(Commands.argument("player", EntityArgument.player()).executes(ctx -> {
                            ServerPlayer p = EntityArgument.getPlayer(ctx, "player");
                            Pins.update(p);
                            List<Pins.Next> next = Pins.available(p);
                            String names = next.stream().limit(8).map(n -> n.chapter() + "/" + n.title()).collect(Collectors.joining(", "));
                            String notes = KEYS.stream().filter(k -> p.getTags().contains("note_" + k)).collect(Collectors.joining(", "));
                            ctx.getSource().sendSuccess(() -> Component.literal("journal " + p.getGameProfile().getName() + ": available " + next.size() + " [" + names + "]; pinned by the mod "
                                    + Pins.owned(p).size() + (p.getTags().contains(Pins.OFF_TAG) ? " (pins off)" : "") + "; notes [" + notes + "]"), false);
                            return next.size();
                        })))
                        .then(Commands.literal("pins").then(Commands.argument("player", EntityArgument.player())
                                .then(Commands.literal("on").executes(ctx -> pins(EntityArgument.getPlayer(ctx, "player"), true, ctx.getSource())))
                                .then(Commands.literal("off").executes(ctx -> pins(EntityArgument.getPlayer(ctx, "player"), false, ctx.getSource())))))
                        .then(Commands.literal("note").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("key", StringArgumentType.word()).executes(ctx -> {
                            ServerPlayer p = EntityArgument.getPlayer(ctx, "player");
                            String key = StringArgumentType.getString(ctx, "key");
                            boolean fresh = note(p, key);
                            ctx.getSource().sendSuccess(() -> Component.literal("note " + key + (KEYS.contains(key) ? (fresh ? ": written" : ": already written") : ": unknown, one of " + KEYS)), false);
                            return fresh ? 1 : 0;
                        }))))));
    }

    private static int pins(ServerPlayer p, boolean on, net.minecraft.commands.CommandSourceStack source) {
        if (on) p.removeTag(Pins.OFF_TAG);
        else p.addTag(Pins.OFF_TAG);
        Pins.update(p);
        source.sendSuccess(() -> Component.literal("journal pins " + (on ? "on" : "off") + " for " + p.getGameProfile().getName()), false);
        return 1;
    }
}
