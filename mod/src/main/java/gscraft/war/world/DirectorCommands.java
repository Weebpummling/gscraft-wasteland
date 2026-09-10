package gscraft.war.world;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import gscraft.war.GscraftWar;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * /gscraft zone|zones|director|garrison - how the director is inspected and exercised without a player standing
 * in the zone. Brigadier merges this with the other /gscraft subcommands.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class DirectorCommands {
    private DirectorCommands() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft")
                .requires(s -> s.hasPermission(2))
                .then(Commands.literal("zones").executes(ctx -> {
                    say(ctx, Zones.all().size() + " zones");
                    return Zones.all().size();
                }))
                .then(Commands.literal("zone")
                        .then(Commands.argument("x", IntegerArgumentType.integer())
                                .then(Commands.argument("z", IntegerArgumentType.integer())
                                        .executes(ctx -> {
                                            int x = IntegerArgumentType.getInteger(ctx, "x");
                                            int z = IntegerArgumentType.getInteger(ctx, "z");
                                            Zone zone = Zones.at(x, z);
                                            if (zone == null) {
                                                say(ctx, "no zone at " + x + " " + z);
                                                return 0;
                                            }
                                            say(ctx, "zone " + zone.name() + (zone.exclude() ? " (excluded)" : "")
                                                    + " cap " + zone.cap() + " spawns " + zone.spawns().size()
                                                    + " dead " + zone.deadRanks()
                                                    + (zone.garrison() != null ? " garrison " + zone.garrison().count() : "")
                                                    + " horrors " + zone.horrors().size());
                                            return 1;
                                        }))))
                .then(Commands.literal("director")
                        .then(Commands.literal("pause").executes(ctx -> {
                            Director.setPaused(true);
                            say(ctx, "director paused");
                            return 1;
                        }))
                        .then(Commands.literal("resume").executes(ctx -> {
                            Director.setPaused(false);
                            say(ctx, "director running");
                            return 1;
                        }))
                        .then(Commands.literal("stats").executes(ctx -> {
                            say(ctx, Director.stats());
                            return 1;
                        }))
                        .then(Commands.literal("pass")
                                .then(Commands.argument("x", IntegerArgumentType.integer())
                                        .then(Commands.argument("z", IntegerArgumentType.integer())
                                                .then(Commands.argument("passes", IntegerArgumentType.integer(1, 500))
                                                        .executes(DirectorCommands::pass)))))
                        .then(Commands.literal("horrors")
                                .then(Commands.argument("x", IntegerArgumentType.integer())
                                        .then(Commands.argument("z", IntegerArgumentType.integer())
                                                .executes(ctx -> {
                                                    BlockPos at = surface(ctx);
                                                    int n = Director.horrors(ctx.getSource().getLevel(), at, true);
                                                    say(ctx, "horrors placed " + n);
                                                    return n;
                                                })))))
                .then(Commands.literal("garrison")
                        .then(Commands.argument("zone", StringArgumentType.word())
                                .then(Commands.literal("fill").executes(ctx -> garrison(ctx, false)))
                                .then(Commands.literal("force").executes(ctx -> garrison(ctx, true))))));
    }

    /** placement passes at a point, ignoring the cap - the director's own test, the way /gscraftspawn was the KubeJS one */
    private static int pass(CommandContext<CommandSourceStack> ctx) {
        ServerLevel level = ctx.getSource().getLevel();
        BlockPos at = surface(ctx);
        int passes = IntegerArgumentType.getInteger(ctx, "passes");
        long t0 = System.nanoTime();
        int n = 0;
        for (int i = 0; i < passes; i++) {
            if (Director.placeNear(level, at, 20, 44, null) != null) n++;
        }
        double ms = (System.nanoTime() - t0) / 1e6;
        Zone zone = Zones.at(at.getX(), at.getZ());
        say(ctx, String.format("zone %s: placed %d of %d in %.1f ms (%.2f ms per pass)",
                zone == null ? "none" : zone.name(), n, passes, ms, ms / passes));
        return n;
    }

    private static int garrison(CommandContext<CommandSourceStack> ctx, boolean force) {
        String name = StringArgumentType.getString(ctx, "zone");
        if (Zones.named(name) == null) {
            say(ctx, "no zone named " + name);
            return 0;
        }
        int n = Director.garrisons(ctx.getSource().getLevel(), name, force);
        say(ctx, "garrison " + name + ": spawned " + n);
        return n;
    }

    private static BlockPos surface(CommandContext<CommandSourceStack> ctx) {
        int x = IntegerArgumentType.getInteger(ctx, "x");
        int z = IntegerArgumentType.getInteger(ctx, "z");
        int y = ctx.getSource().getLevel().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        return new BlockPos(x, y, z);
    }

    private static void say(CommandContext<CommandSourceStack> ctx, String text) {
        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
    }
}
