package gscraft.war.world;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.ArgumentBuilder;
import com.mojang.brigadier.builder.RequiredArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import gscraft.war.GscraftWar;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.function.Function;

/**
 * /gscraft zone|zones|env|director|garrison|hold|locks|drops|sweep - how the director is inspected and exercised without a player standing
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
                .then(Commands.literal("zone").then(xz(ctx -> {
                    int x = IntegerArgumentType.getInteger(ctx, "x");
                    int z = IntegerArgumentType.getInteger(ctx, "z");
                    Zone zone = Zones.at(x, z);
                    if (zone == null) {
                        say(ctx, "no zone at " + x + " " + z);
                        return 0;
                    }
                    say(ctx, "zone " + zone.name() + (zone.exclude() ? " (excluded)" : "")
                            + " cap " + zone.cap() + " spawns " + zone.spawns().size()
                            + " indoor " + zone.indoorSpawns().size() + " underground " + zone.undergroundSpawns().size()
                            + " dead " + zone.deadRanks()
                            + (zone.garrison() != null ? " garrison " + zone.garrison().count() : "")
                            + (zone.lair() != null ? " lair " + zone.lair().entity() : "")
                            + " horrors " + zone.horrors().size());
                    return 1;
                })))
                .then(Commands.literal("env").then(xyz(ctx -> {
                    BlockPos at = pos(ctx);
                    say(ctx, "ground at " + at.toShortString() + ": " + Env.at(ctx.getSource().getLevel(), at));
                    return 1;
                })))
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
                        .then(Commands.literal("pass").then(xzThen(passes(ctx -> pass(ctx, surface(ctx))))))
                        .then(Commands.literal("passat").then(xyzThen(passes(ctx -> pass(ctx, standAt(ctx))))))
                        .then(Commands.literal("survey").then(xyzThen(Commands.argument("samples",
                                IntegerArgumentType.integer(10, 1000)).executes(DirectorCommands::survey))))
                        .then(Commands.literal("ambient").then(xyzThen(passes(DirectorCommands::ambient))))
                        .then(Commands.literal("room").then(xzThen(Commands.argument("radius",
                                IntegerArgumentType.integer(2, 128)).executes(ctx -> {
                            int x = IntegerArgumentType.getInteger(ctx, "x");
                            int z = IntegerArgumentType.getInteger(ctx, "z");
                            int radius = IntegerArgumentType.getInteger(ctx, "radius");
                            BlockPos room = Director.groundRoom(ctx.getSource().getLevel(), x, z, radius);
                            say(ctx, room == null ? "no ground-floor room within " + radius
                                    : "room at " + room.getX() + " " + room.getY() + " " + room.getZ());
                            return room == null ? 0 : 1;
                        }))))
                        .then(Commands.literal("horrors").then(xyz(ctx -> {
                            int n = Director.horrors(ctx.getSource().getLevel(), pos(ctx), true);
                            say(ctx, "horrors placed " + n);
                            return n;
                        }))))
                .then(Commands.literal("hold")
                        .then(Commands.literal("on").executes(ctx -> {
                            Hold.setEnabled(true);
                            say(ctx, Hold.status());
                            return 1;
                        }))
                        .then(Commands.literal("off").executes(ctx -> {
                            Hold.setEnabled(false);
                            say(ctx, Hold.status());
                            return 1;
                        }))
                        .then(Commands.literal("status").executes(ctx -> {
                            say(ctx, Hold.status());
                            return 1;
                        })))
                .then(Commands.literal("locks").executes(ctx -> {
                    say(ctx, Locks.all().isEmpty() ? "no locks" : Locks.all().stream()
                            .map(l -> l.name() + " x " + l.x0() + ".." + l.x1() + " z " + l.z0() + ".." + l.z1())
                            .reduce((a, b) -> a + "; " + b).orElse(""));
                    return Locks.all().size();
                }))
                .then(Commands.literal("drops").then(Commands.argument("entity", StringArgumentType.greedyString()).executes(ctx -> {
                    var rules = Drops.rulesFor(new net.minecraft.resources.ResourceLocation(StringArgumentType.getString(ctx, "entity")));
                    say(ctx, rules.size() + " drop rules (" + Drops.types() + " entity types loaded): " + rules.stream()
                            .map(d -> d.item().getPath() + " " + Math.round(d.chance() * 100) + "%")
                            .reduce((a, b) -> a + ", " + b).orElse(""));
                    return rules.size();
                })))
                .then(Commands.literal("sweep").executes(ctx -> {
                    say(ctx, ProjectileSweep.status());
                    return 1;
                }).then(Commands.literal("age").then(Commands.argument("ticks", IntegerArgumentType.integer(1, 72000)).executes(ctx -> {
                    ProjectileSweep.setMaxAge(IntegerArgumentType.getInteger(ctx, "ticks"));
                    say(ctx, ProjectileSweep.status());
                    return 1;
                }))))
                .then(Commands.literal("garrison")
                        .then(Commands.argument("zone", StringArgumentType.word())
                                .then(Commands.literal("fill").executes(ctx -> garrison(ctx, false)))
                                .then(Commands.literal("force").executes(ctx -> garrison(ctx, true))))));
    }

    private static RequiredArgumentBuilder<CommandSourceStack, Integer> xz(Function<CommandContext<CommandSourceStack>, Integer> run) {
        var z = Commands.argument("z", IntegerArgumentType.integer());
        if (run != null) z.executes(run::apply);
        return Commands.argument("x", IntegerArgumentType.integer()).then(z);
    }

    private static RequiredArgumentBuilder<CommandSourceStack, Integer> xyz(Function<CommandContext<CommandSourceStack>, Integer> run) {
        var z = Commands.argument("z", IntegerArgumentType.integer());
        if (run != null) z.executes(run::apply);
        return Commands.argument("x", IntegerArgumentType.integer())
                .then(Commands.argument("y", IntegerArgumentType.integer()).then(z));
    }

    /** x z, then more arguments; Brigadier builds a child when it is attached, so the tail goes on z first */
    private static RequiredArgumentBuilder<CommandSourceStack, Integer> xzThen(ArgumentBuilder<CommandSourceStack, ?> tail) {
        return Commands.argument("x", IntegerArgumentType.integer())
                .then(Commands.argument("z", IntegerArgumentType.integer()).then(tail));
    }

    private static RequiredArgumentBuilder<CommandSourceStack, Integer> xyzThen(ArgumentBuilder<CommandSourceStack, ?> tail) {
        return Commands.argument("x", IntegerArgumentType.integer())
                .then(Commands.argument("y", IntegerArgumentType.integer())
                        .then(Commands.argument("z", IntegerArgumentType.integer()).then(tail)));
    }

    private static RequiredArgumentBuilder<CommandSourceStack, Integer> passes(Function<CommandContext<CommandSourceStack>, Integer> run) {
        return Commands.argument("passes", IntegerArgumentType.integer(1, 500)).executes(run::apply);
    }

    /** placement passes at a point, ignoring the cap, on the kind of ground the point stands on */
    private static int pass(CommandContext<CommandSourceStack> ctx, BlockPos at) {
        ServerLevel level = ctx.getSource().getLevel();
        int passes = IntegerArgumentType.getInteger(ctx, "passes");
        Env env = Env.at(level, at);
        long t0 = System.nanoTime();
        int n = 0;
        int sealed = 0;
        for (int i = 0; i < passes; i++) {
            Mob mob = Director.placeNear(level, at, env, null, Director.rollSealed(level, env));
            if (mob == null) continue;
            n++;
            if (mob.getTags().contains(Director.SEALED_TAG)) sealed++;
        }
        double ms = (System.nanoTime() - t0) / 1e6;
        Zone zone = Zones.at(at.getX(), at.getZ());
        say(ctx, String.format("zone %s, %s ground: placed %d of %d in %.1f ms (%.2f ms per pass), behind shut doors %d",
                zone == null ? "none" : zone.name(), env, n, passes, ms, ms / passes, sealed));
        return n;
    }

    /** the director's own ambient step at a point, cap and all, as if a player stood there for this many passes */
    private static int ambient(CommandContext<CommandSourceStack> ctx) {
        ServerLevel level = ctx.getSource().getLevel();
        BlockPos at = standAt(ctx);
        int passes = IntegerArgumentType.getInteger(ctx, "passes");
        int n = 0;
        for (int i = 0; i < passes; i++) {
            if (Director.ambient(level, at)) n++;
        }
        Env env = Env.at(level, at);
        Zone zone = Zones.at(at.getX(), at.getZ());
        int cap = zone == null ? 0 : Director.capFor(zone, env);
        say(ctx, String.format("ambient at %s, %s ground: placed %d in %d passes; counted here %d of cap %d, "
                        + "behind shut doors %d of %d", at.toShortString(), env, n, passes,
                Director.countOurs(level, at, env), cap, Director.countSealed(level, at, env), Director.sealedCap(cap)));
        return n;
    }

    private static int survey(CommandContext<CommandSourceStack> ctx) {
        ServerLevel level = ctx.getSource().getLevel();
        BlockPos at = standAt(ctx);
        int samples = IntegerArgumentType.getInteger(ctx, "samples");
        Zone zone = Zones.at(at.getX(), at.getZ());
        Env env = Env.at(level, at);
        say(ctx, "survey at " + at.toShortString() + ", zone " + (zone == null ? "none" : zone.name()) + ", ground " + env
                + (zone == null ? "" : ", cap here " + Director.capFor(zone, env) + " (zone " + zone.cap() + ")")
                + ", director creatures counted here now " + Director.countOurs(level, at, env));
        say(ctx, Director.survey(level, at, samples, true).describe("first version"));
        say(ctx, Director.survey(level, at, samples, false).describe("layered"));
        return 1;
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

    /** the point given, moved to the nearest standing room when it is inside a block */
    private static BlockPos standAt(CommandContext<CommandSourceStack> ctx) {
        BlockPos raw = pos(ctx);
        BlockPos stand = Director.nearestStand(ctx.getSource().getLevel(), raw);
        return stand != null ? stand : raw;
    }

    private static BlockPos pos(CommandContext<CommandSourceStack> ctx) {
        return new BlockPos(IntegerArgumentType.getInteger(ctx, "x"), IntegerArgumentType.getInteger(ctx, "y"),
                IntegerArgumentType.getInteger(ctx, "z"));
    }

    private static void say(CommandContext<CommandSourceStack> ctx, String text) {
        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
    }
}
