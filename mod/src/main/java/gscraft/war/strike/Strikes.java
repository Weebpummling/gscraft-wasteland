package gscraft.war.strike;

import com.mojang.brigadier.arguments.StringArgumentType;
import gscraft.war.GscraftWar;
import gscraft.war.survivor.Say;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;

/**
 * The fire missions (owner, 2026-09-13; docs/gscraft-strikes-2026-09-13.md): a strike grenade lands, the call goes
 * out on the radio, and after the delay the rounds come - the mortar's spotting round then a short barrage, the
 * guns' heavier and wider barrage, or the Cobra's rocket and gun run ({@link AirRun}). One global cooldown covers
 * all three; every player hears the call and the refusal. Rounds are Superb Warfare's own shells and rockets,
 * spawned in flight above the target, so their damage, blast and sound are the mod's.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Strikes {
    private Strikes() {}

    public enum Kind { MORTAR, ARTILLERY, AIR }

    // the settings (strike.*); a cooldown per grenade, not one for all (owner, 2026-09-13)
    public static int COOLDOWN_MORTAR = 3600, COOLDOWN_ARTILLERY = 6000, COOLDOWN_AIR = 9600;
    public static int MORTAR_DELAY = 300, MORTAR_BARRAGE = 6, MORTAR_GAP = 30, MORTAR_SCATTER = 6;
    public static float MORTAR_DAMAGE = 60f, MORTAR_EXPLOSION = 80f, MORTAR_RADIUS = 5f;
    public static int ARTY_DELAY = 400, ARTY_BARRAGE = 8, ARTY_GAP = 25, ARTY_SCATTER = 12;
    public static float ARTY_DAMAGE = 120f, ARTY_EXPLOSION = 160f, ARTY_RADIUS = 9f;
    public static int AIR_DELAY = 600;
    public static int DROP_HEIGHT = 70;

    private record Task(long at, Runnable run) {}

    private static final List<Task> TASKS = new ArrayList<>();
    private static final List<AirRun> RUNS = new ArrayList<>();
    private static final java.util.EnumMap<Kind, Long> COOLDOWN_UNTIL = new java.util.EnumMap<>(Kind.class);
    private static String lastCall = "";

    public static int cooldown(Kind kind) {
        return switch (kind) {
            case MORTAR -> COOLDOWN_MORTAR;
            case ARTILLERY -> COOLDOWN_ARTILLERY;
            case AIR -> COOLDOWN_AIR;
        };
    }

    public static boolean hot(MinecraftServer server, Kind kind) {
        return server.getTickCount() < COOLDOWN_UNTIL.getOrDefault(kind, 0L);
    }

    public static int hotTicks(MinecraftServer server, Kind kind) {
        return (int) Math.max(0, COOLDOWN_UNTIL.getOrDefault(kind, 0L) - server.getTickCount());
    }

    public static String hotFor(MinecraftServer server, Kind kind) {
        return mmss(COOLDOWN_UNTIL.getOrDefault(kind, 0L) - server.getTickCount());
    }

    /** the refusal in the caller's words: the tube, the guns, the Cobra */
    public static String refusal(MinecraftServer server, Kind kind) {
        return switch (kind) {
            case MORTAR -> "the tube is hot: " + hotFor(server, kind);
            case ARTILLERY -> "the guns are hot: " + hotFor(server, kind);
            case AIR -> "the Cobra is refuelling: " + hotFor(server, kind);
        };
    }

    /** the line the refusal comes with: Marshall for the tube and the guns, Tune for the Cobra */
    public static String[] refusalLine(Kind kind) {
        return switch (kind) {
            case MORTAR -> new String[]{"marshall", "tube_hot"};
            case ARTILLERY -> new String[]{"marshall", "guns_hot"};
            case AIR -> new String[]{"tune", "air_busy"};
        };
    }

    static String mmss(long ticks) {
        long s = Math.max(0, ticks) / 20;
        return String.format("%d:%02d", s / 60, s % 60);
    }

    static void later(MinecraftServer server, int ticks, Runnable run) {
        TASKS.add(new Task(server.getTickCount() + ticks, run));
    }

    /** the call: accepted (null) or the refusal; the cooldown starts, everyone hears it */
    public static String call(ServerLevel level, Kind kind, BlockPos target, ServerPlayer caller) {
        MinecraftServer server = level.getServer();
        if (hot(server, kind)) return refusal(server, kind) + " (" + lastCall + ")";
        COOLDOWN_UNTIL.put(kind, server.getTickCount() + (long) cooldown(kind));
        lastCall = kind.name().toLowerCase(Locale.ROOT) + " at " + target.toShortString();
        BlockPos ground = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, target);
        switch (kind) {
            case MORTAR -> {
                tell("marshall", "fire_mission", server);
                later(server, MORTAR_DELAY, () -> {
                    shell(level, caller, ground, 1, MORTAR_DAMAGE * 0.5f, MORTAR_EXPLOSION * 0.5f, MORTAR_RADIUS * 0.6f, "mortar_shell");
                    GscraftWar.LOG.info("[gscraft] strike: mortar spotting round at {}", ground.toShortString());
                    tell("tune", "splash", server);
                });
                for (int i = 0; i < MORTAR_BARRAGE; i++) {
                    int n = i + 1;
                    later(server, MORTAR_DELAY + 80 + i * MORTAR_GAP, () -> {
                        shell(level, caller, ground, MORTAR_SCATTER, MORTAR_DAMAGE, MORTAR_EXPLOSION, MORTAR_RADIUS, "mortar_shell");
                        if (n == MORTAR_BARRAGE) GscraftWar.LOG.info("[gscraft] strike: mortar barrage of {} complete at {}", MORTAR_BARRAGE, ground.toShortString());
                    });
                }
            }
            case ARTILLERY -> {
                tell("marshall", "fire_for_effect", server);
                later(server, ARTY_DELAY, () -> {
                    shell(level, caller, ground, 2, ARTY_DAMAGE * 0.5f, ARTY_EXPLOSION * 0.5f, ARTY_RADIUS * 0.6f, "cannon_shell");
                    GscraftWar.LOG.info("[gscraft] strike: artillery spotting round at {}", ground.toShortString());
                    tell("tune", "splash", server);
                });
                for (int i = 0; i < ARTY_BARRAGE; i++) {
                    int n = i + 1;
                    later(server, ARTY_DELAY + 100 + i * ARTY_GAP, () -> {
                        shell(level, caller, ground, ARTY_SCATTER, ARTY_DAMAGE, ARTY_EXPLOSION, ARTY_RADIUS, "cannon_shell");
                        if (n == ARTY_BARRAGE) GscraftWar.LOG.info("[gscraft] strike: artillery barrage of {} complete at {}", ARTY_BARRAGE, ground.toShortString());
                    });
                }
            }
            case AIR -> {
                tell("marshall", "air_support", server);
                later(server, AIR_DELAY, () -> RUNS.add(new AirRun(level, ground, caller)));
            }
        }
        GscraftWar.LOG.info("[gscraft] strike: {} called at {} by {}", kind, ground.toShortString(), caller == null ? "the console" : caller.getGameProfile().getName());
        return null;
    }

    static void tell(String npc, String key, MinecraftServer server) {
        for (ServerPlayer p : server.getPlayerList().getPlayers()) Say.queue(p, npc, key, true);
    }

    /** one round in flight above the target, falling: the mod's shell with our numbers; the whistle at the target */
    static void shell(ServerLevel level, ServerPlayer owner, BlockPos ground, int scatter, float damage, float explosion, float radius, String type) {
        RandomSource random = level.getRandom();
        double x = ground.getX() + 0.5 + (random.nextDouble() * 2 - 1) * scatter;
        double z = ground.getZ() + 0.5 + (random.nextDouble() * 2 - 1) * scatter;
        Entity e = Sw.create(level, type);
        if (!(e instanceof net.minecraft.world.entity.projectile.Projectile shell)) return;
        Sw.set(shell, "setDamage", damage);
        Sw.set(shell, "setExplosionDamage", explosion);
        Sw.set(shell, "setExplosionRadius", radius);
        Sw.type(shell, type.equals("mortar_shell") ? "NORMAL" : "HE");
        if (owner != null) shell.setOwner(owner);
        shell.setPos(x, ground.getY() + DROP_HEIGHT, z);
        shell.shoot(0, -1, 0, 2.5f, 0f);
        level.addFreshEntity(shell);
        sound(level, ground, "shell_fly", 3f, 1f);
    }

    static void sound(ServerLevel level, BlockPos at, String id, float volume, float pitch) {
        SoundEvent s = ForgeRegistries.SOUND_EVENTS.getValue(new ResourceLocation("superbwarfare", id));
        if (s != null) level.playSound(null, at, s, SoundSource.HOSTILE, volume, pitch);
    }

    static Vec3 centre(BlockPos p) {
        return new Vec3(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        long now = event.getServer().getTickCount();
        for (Iterator<Task> it = TASKS.iterator(); it.hasNext(); ) {
            Task t = it.next();
            if (t.at() > now) continue;
            it.remove();
            try {
                t.run().run();
            } catch (RuntimeException ex) {
                GscraftWar.LOG.error("[gscraft] strike task failed: {}", ex.toString());
            }
        }
        for (Iterator<AirRun> it = RUNS.iterator(); it.hasNext(); ) {
            AirRun r = it.next();
            if (!r.tick()) it.remove();
        }
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("strike")
                        .then(Commands.literal("status").executes(ctx -> {
                            MinecraftServer server = ctx.getSource().getServer();
                            StringBuilder sb = new StringBuilder();
                            for (Kind k : Kind.values()) sb.append(k.name().toLowerCase(Locale.ROOT)).append(' ').append(hot(server, k) ? "hot " + hotFor(server, k) : "ready").append("; ");
                            String line = sb + "last " + (lastCall.isEmpty() ? "none" : lastCall) + "; " + TASKS.size() + " rounds scheduled, " + RUNS.size() + " runs";
                            ctx.getSource().sendSuccess(() -> Component.literal(line), false);
                            return 1;
                        }))
                        .then(Commands.literal("reset").executes(ctx -> {
                            COOLDOWN_UNTIL.clear();
                            TASKS.clear();
                            for (AirRun r : RUNS) r.abort();
                            RUNS.clear();
                            ctx.getSource().sendSuccess(() -> Component.literal("strikes reset: the tube is cold"), false);
                            return 1;
                        }))
                        .then(Commands.argument("kind", StringArgumentType.word()).then(Commands.argument("at", BlockPosArgument.blockPos()).executes(ctx -> {
                            Kind kind;
                            try {
                                kind = Kind.valueOf(StringArgumentType.getString(ctx, "kind").toUpperCase(Locale.ROOT));
                            } catch (IllegalArgumentException ex) {
                                ctx.getSource().sendFailure(Component.literal("kinds: mortar, artillery, air"));
                                return 0;
                            }
                            ServerPlayer caller = ctx.getSource().getEntity() instanceof ServerPlayer p ? p : null;
                            String refused = call(ctx.getSource().getLevel(), kind, BlockPosArgument.getLoadedBlockPos(ctx, "at"), caller);
                            String line = refused == null ? kind.name().toLowerCase(Locale.ROOT) + " called" : refused;
                            ctx.getSource().sendSuccess(() -> Component.literal(line), false);
                            return refused == null ? 1 : 0;
                        })))));
    }
}
