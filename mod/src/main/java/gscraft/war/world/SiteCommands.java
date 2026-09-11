package gscraft.war.world;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import gscraft.war.GscraftWar;
import gscraft.war.world.SiteData.State;
import gscraft.war.world.Sites.SiteDef;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Locale;

/**
 * /gscraft sites|site|clock|stages|stage - the operator's side of the loop (interface §5). Brigadier merges these
 * into the /gscraft root with the director's.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class SiteCommands {
    private SiteCommands() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft")
                .requires(s -> s.hasPermission(2))
                .then(Commands.literal("sites").executes(ctx -> {
                    ServerLevel level = ctx.getSource().getLevel();
                    if (Sites.all().isEmpty()) {
                        say(ctx, "no sites loaded");
                        return 0;
                    }
                    for (SiteDef site : Sites.all().values()) say(ctx, Loop.describe(level, site));
                    say(ctx, "online clock " + Loop.mmss(SiteData.get(level).online) + (Loop.freeClock() ? " (free)" : " (players only)")
                            + "; contested: " + (SiteData.get(level).contested.isEmpty() ? "none" : SiteData.get(level).contested));
                    return Sites.all().size();
                }))
                .then(Commands.literal("site").then(Commands.argument("id", StringArgumentType.word())
                        .executes(ctx -> withSite(ctx, (level, site) -> Loop.describe(level, site)))
                        .then(Commands.literal("set").then(Commands.argument("state", StringArgumentType.word()).executes(ctx ->
                                withSite(ctx, (level, site) -> {
                                    State to;
                                    try {
                                        to = State.valueOf(StringArgumentType.getString(ctx, "state").toUpperCase(Locale.ROOT));
                                    } catch (IllegalArgumentException ex) {
                                        return "states: unknown, scouted, looted, held";
                                    }
                                    return Loop.advance(level, site, to);
                                }))))
                        .then(Commands.literal("clock").then(Commands.argument("seconds", IntegerArgumentType.integer(0, 36000)).executes(ctx ->
                                withSite(ctx, (level, site) -> Loop.clock(level, site, IntegerArgumentType.getInteger(ctx, "seconds"))))))
                        .then(Commands.literal("guard").executes(ctx -> withSite(ctx, (level, site) ->
                                site.id() + " site guard: " + Loop.keepGuard(level, site, SiteData.get(level).progress(site.id())) + " summoned, "
                                        + Loop.guardCount(level, site) + " standing")))))
                .then(Commands.literal("clock")
                        .then(Commands.literal("free").executes(ctx -> {
                            Loop.setFreeClock(true);
                            say(ctx, "clocks run with nobody online (tests)");
                            return 1;
                        }))
                        .then(Commands.literal("online").executes(ctx -> {
                            Loop.setFreeClock(false);
                            say(ctx, "clocks run only with a player online");
                            return 1;
                        })))
                .then(Commands.literal("stages").executes(ctx -> {
                    var stages = SiteData.get(ctx.getSource().getLevel()).stages();
                    say(ctx, stages.isEmpty() ? "no stages set" : String.join(", ", stages));
                    return stages.size();
                }))
                .then(Commands.literal("stage")
                        .then(Commands.literal("add").then(Commands.argument("name", StringArgumentType.word()).executes(ctx -> {
                            String name = StringArgumentType.getString(ctx, "name");
                            say(ctx, (Stages.add(ctx.getSource().getServer(), name) ? "stage set: " : "stage already set: ") + name);
                            return 1;
                        })))
                        .then(Commands.literal("remove").then(Commands.argument("name", StringArgumentType.word()).executes(ctx -> {
                            String name = StringArgumentType.getString(ctx, "name");
                            say(ctx, (Stages.remove(ctx.getSource().getServer(), name) ? "stage removed: " : "stage was not set: ") + name);
                            return 1;
                        })))));
    }

    private interface SiteAction {
        String run(ServerLevel level, SiteDef site);
    }

    private static int withSite(CommandContext<CommandSourceStack> ctx, SiteAction action) {
        String id = StringArgumentType.getString(ctx, "id");
        SiteDef site = Sites.get(id);
        if (site == null) {
            say(ctx, "no site " + id + "; sites: " + String.join(", ", Sites.all().keySet()));
            return 0;
        }
        say(ctx, action.run(ctx.getSource().getLevel(), site));
        return 1;
    }

    private static void say(CommandContext<CommandSourceStack> ctx, String text) {
        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
    }
}
