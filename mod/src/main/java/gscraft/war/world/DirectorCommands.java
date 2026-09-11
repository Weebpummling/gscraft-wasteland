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
                        .then(Commands.literal("phantom")
                                .then(Commands.literal("clear").executes(ctx -> {
                                    Director.setPhantoms(java.util.List.of());
                                    say(ctx, "no phantoms");
                                    return 1;
                                }))
                                .then(Commands.literal("add").then(xyz(ctx -> {
                                    java.util.List<BlockPos> all = new java.util.ArrayList<>(Director.phantoms());
                                    all.add(pos(ctx));
                                    Director.setPhantoms(all);
                                    say(ctx, all.size() + " phantoms");
                                    return all.size();
                                })))
                                .then(Commands.literal("set").then(xyz(ctx -> {
                                    Director.setPhantoms(java.util.List.of(pos(ctx)));
                                    say(ctx, "1 phantom at " + pos(ctx).toShortString());
                                    return 1;
                                }))))
                        .then(Commands.literal("bench").then(passes(DirectorCommands::bench)))
                        .then(Commands.literal("census").then(xyz(ctx -> {
                            ServerLevel level = ctx.getSource().getLevel();
                            say(ctx, Director.census(level, pos(ctx), Env.at(level, pos(ctx))));
                            return 1;
                        })))
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
                .then(Commands.literal("fighter").then(Commands.argument("who", net.minecraft.commands.arguments.EntityArgument.entity()).executes(ctx -> {
                    net.minecraft.world.entity.Entity e = net.minecraft.commands.arguments.EntityArgument.getEntity(ctx, "who");
                    if (!(e instanceof gscraft.war.entity.GunUser user) || !(e instanceof net.minecraft.world.entity.Mob mob)) {
                        say(ctx, "not a fighter");
                        return 0;
                    }
                    gscraft.war.entity.FighterState st = user.fighterState();
                    gscraft.war.entity.Cover.Spot cover = e instanceof gscraft.war.entity.Soldier sol ? sol.cover()
                            : e instanceof gscraft.war.entity.Scavenger sc ? sc.cover() : null;
                    boolean hidden = mob.getTarget() != null && gscraft.war.entity.Cover.covered(ctx.getSource().getLevel(), mob, mob.getTarget(), mob.position());
                    say(ctx, String.format("%s: rank %s, role %s, magazines %d, grenades %d, suppression %.2f, pose %s, sprinting %s, target %s, ammo %s, "
                                    + "order %s%s, cover %s, hidden from target %s",
                            mob.getName().getString(), st.rank, st.role, st.magazines, st.grenades, st.suppression, mob.getPose(),
                            mob.isSprinting(), mob.getTarget() == null ? "none" : mob.getTarget().getName().getString(),
                            st.outOfAmmo ? "out" : "yes", st.order, st.order == gscraft.war.entity.FighterState.Order.NONE ? "" : " at " + st.orderPos.toShortString(),
                            cover == null ? "none" : cover.spot().toShortString(), hidden));
                    return 1;
                }).then(Commands.literal("hold").then(xyzThen(Commands.literal("now").executes(ctx -> order(ctx, gscraft.war.entity.FighterState.Order.HOLD, false)))))
                .then(Commands.literal("advance").then(xyzThen(Commands.literal("now").executes(ctx -> order(ctx, gscraft.war.entity.FighterState.Order.ADVANCE, false)))))
                .then(Commands.literal("free").executes(ctx -> order(ctx, gscraft.war.entity.FighterState.Order.NONE, false)))
                .then(Commands.literal("squadhold").then(xyzThen(Commands.literal("now").executes(ctx -> order(ctx, gscraft.war.entity.FighterState.Order.HOLD, true)))))
                .then(Commands.literal("squadadvance").then(xyzThen(Commands.literal("now").executes(ctx -> order(ctx, gscraft.war.entity.FighterState.Order.ADVANCE, true)))))
                .then(Commands.literal("goto").then(xyzThen(Commands.literal("now").executes(ctx -> {
                    // an order to walk to a point (feasibility B2, first cut): the operator's, and the tests'
                    net.minecraft.world.entity.Entity e = net.minecraft.commands.arguments.EntityArgument.getEntity(ctx, "who");
                    BlockPos to = pos(ctx);
                    if (!(e instanceof net.minecraft.world.entity.Mob mob)) {
                        say(ctx, "not a mob");
                        return 0;
                    }
                    if (!(e instanceof gscraft.war.entity.GunUser user)) {
                        say(ctx, "not a fighter");
                        return 0;
                    }
                    user.fighterState().order = gscraft.war.entity.FighterState.Order.ADVANCE;
                    user.fighterState().orderPos = to;
                    say(ctx, mob.getName().getString() + " walks to " + to.toShortString());
                    return 1;
                }))))))
                .then(Commands.literal("squad").then(Commands.argument("who", net.minecraft.commands.arguments.EntityArgument.entity())
                        .executes(ctx -> squad(ctx, "info", ""))
                        .then(Commands.literal("form").executes(ctx -> squad(ctx, "form", "")))
                        .then(Commands.literal("disband").executes(ctx -> squad(ctx, "disband", "")))
                        .then(Commands.literal("formation").then(Commands.argument("f", StringArgumentType.word()).executes(ctx -> squad(ctx, "formation", StringArgumentType.getString(ctx, "f")))))
                        .then(Commands.literal("route").then(Commands.argument("points", StringArgumentType.greedyString()).executes(ctx -> squad(ctx, "route", StringArgumentType.getString(ctx, "points")))))
                        .then(Commands.literal("patrol").executes(ctx -> squad(ctx, "patrol", "")))))
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

    /** full director passes for the players (or phantoms) present, timed: what one tick of the director costs */
    private static int bench(CommandContext<CommandSourceStack> ctx) {
        ServerLevel level = ctx.getSource().getLevel();
        int passes = IntegerArgumentType.getInteger(ctx, "passes");
        java.util.List<BlockPos> at = Director.presence(level);
        if (at.isEmpty()) {
            say(ctx, "nobody present: no players and no phantoms");
            return 0;
        }
        long total = 0;
        long worst = 0;
        long best = Long.MAX_VALUE;
        int before = Director.countDirector(level);
        for (int i = 0; i < passes; i++) {
            Director.pass(level, at);
            long n = Director.lastPassNanos();
            total += n;
            worst = Math.max(worst, n);
            best = Math.min(best, n);
        }
        int after = Director.countDirector(level);
        say(ctx, String.format("bench: %d passes for %d present: %.3f ms mean, %.3f min, %.3f max per pass; creatures %d -> %d",
                passes, at.size(), total / 1e6 / passes, best / 1e6, worst / 1e6, before, after));
        return passes;
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

    /** an order to one fighter, or (squad) to it and every ally within twenty blocks - a Sergeant's call */
    private static int order(CommandContext<CommandSourceStack> ctx, gscraft.war.entity.FighterState.Order order, boolean squad) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        net.minecraft.world.entity.Entity e = net.minecraft.commands.arguments.EntityArgument.getEntity(ctx, "who");
        if (!(e instanceof net.minecraft.world.entity.Mob leader) || !(e instanceof gscraft.war.entity.GunUser)) {
            say(ctx, "not a fighter");
            return 0;
        }
        BlockPos at = order == gscraft.war.entity.FighterState.Order.NONE ? BlockPos.ZERO : pos(ctx);
        java.util.List<net.minecraft.world.entity.Mob> given = new java.util.ArrayList<>();
        given.add(leader);
        if (squad) {
            given.addAll(ctx.getSource().getLevel().getEntitiesOfClass(net.minecraft.world.entity.Mob.class, leader.getBoundingBox().inflate(20.0D),
                    m -> m != leader && m instanceof gscraft.war.entity.GunUser && gscraft.war.faction.Factions.allied(m, leader)));
        }
        for (net.minecraft.world.entity.Mob m : given) {
            gscraft.war.entity.FighterState st = ((gscraft.war.entity.GunUser) m).fighterState();
            st.order = order;
            st.orderPos = at;
        }
        say(ctx, given.size() + " ordered: " + order + (order == gscraft.war.entity.FighterState.Order.NONE ? "" : " at " + at.toShortString()));
        return given.size();
    }

    private static int squad(CommandContext<CommandSourceStack> ctx, String what, String arg) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        net.minecraft.world.entity.Entity e = net.minecraft.commands.arguments.EntityArgument.getEntity(ctx, "who");
        ServerLevel level = ctx.getSource().getLevel();
        if (!(e instanceof net.minecraft.world.entity.Mob mob) || !(e instanceof gscraft.war.entity.GunUser user)) {
            say(ctx, "not a fighter");
            return 0;
        }
        gscraft.war.entity.FighterState st = user.fighterState();
        switch (what) {
            case "form" -> {
                java.util.UUID id = gscraft.war.entity.Squad.formAround(level, mob);
                say(ctx, id == null ? "nobody to form with" : "squad formed: " + gscraft.war.entity.Squad.members(level, mob).size() + " fighters");
                return id == null ? 0 : 1;
            }
            case "disband" -> {
                for (net.minecraft.world.entity.Mob m : gscraft.war.entity.Squad.members(level, mob)) {
                    gscraft.war.entity.FighterState s = ((gscraft.war.entity.GunUser) m).fighterState();
                    s.squadId = null;
                    s.route = new java.util.ArrayList<>();
                    if (s.orderBySquad) {
                        s.order = gscraft.war.entity.FighterState.Order.NONE;
                        s.orderBySquad = false;
                    }
                }
                say(ctx, "squad disbanded");
                return 1;
            }
            case "formation" -> {
                gscraft.war.entity.Squad.Formation f;
                try {
                    f = gscraft.war.entity.Squad.Formation.valueOf(arg.toUpperCase(java.util.Locale.ROOT));
                } catch (IllegalArgumentException ex) {
                    say(ctx, "formations: wedge, line, column");
                    return 0;
                }
                for (net.minecraft.world.entity.Mob m : gscraft.war.entity.Squad.members(level, mob)) ((gscraft.war.entity.GunUser) m).fighterState().formation = f;
                say(ctx, "formation " + f);
                return 1;
            }
            case "route" -> {
                java.util.List<BlockPos> route = new java.util.ArrayList<>();
                String[] n = arg.replace("\"", " ").trim().split("\\s+");
                for (int i = 0; i + 1 < n.length; i += 2) {
                    try {
                        route.add(new BlockPos(Integer.parseInt(n[i]), Integer.MIN_VALUE, Integer.parseInt(n[i + 1])));
                    } catch (NumberFormatException ex) {
                        say(ctx, "route: x z x z ...");
                        return 0;
                    }
                }
                net.minecraft.world.entity.Mob leader = gscraft.war.entity.Squad.leader(level, mob);
                gscraft.war.entity.FighterState ls = ((gscraft.war.entity.GunUser) leader).fighterState();
                ls.route = route;
                ls.routeIndex = 0;
                say(ctx, leader.getName().getString() + " patrols " + route.size() + " points");
                return route.size();
            }
            case "patrol" -> {
                net.minecraft.world.entity.Mob leader = gscraft.war.entity.Squad.leader(level, mob);
                gscraft.war.entity.FighterState ls = ((gscraft.war.entity.GunUser) leader).fighterState();
                ls.nextPatrolPickup = 0;
                say(ctx, ls.route.isEmpty() ? "the leader picks up its zone's route on its next second, if the zone has one" : "already on a route of " + ls.route.size());
                return 1;
            }
            default -> {
                java.util.List<net.minecraft.world.entity.Mob> members = gscraft.war.entity.Squad.members(level, mob);
                net.minecraft.world.entity.Mob leader = members.isEmpty() ? mob : members.get(0);
                StringBuilder sb = new StringBuilder(mob.getName().getString()).append(": ");
                if (st.squadId == null) {
                    sb.append("no squad");
                } else {
                    sb.append("squad ").append(st.squadId.toString(), 0, 8).append(", slot ").append(st.slot).append(" of ").append(st.squadSize)
                            .append(", leader ").append(leader.getName().getString()).append(leader == mob ? " (self)" : "")
                            .append(", alive ").append(members.size()).append(", formation ").append(((gscraft.war.entity.GunUser) leader).fighterState().formation);
                    gscraft.war.entity.FighterState ls = ((gscraft.war.entity.GunUser) leader).fighterState();
                    if (!ls.route.isEmpty()) sb.append(", route ").append(ls.route.size()).append(" points at ").append(ls.routeIndex);
                }
                sb.append("; order ").append(st.order).append(st.orderBySquad ? " (squad)" : "");
                say(ctx, sb.toString());
                return 1;
            }
        }
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
