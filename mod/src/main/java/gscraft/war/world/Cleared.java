package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import com.mojang.brigadier.arguments.IntegerArgumentType;

import java.util.ArrayList;
import java.util.List;

/**
 * Ground the players have cleared STAYS cleared (owner, 2026-09-20: "make it so the soldiers don't respawn after clearing the
 * area out", then "make it a kill count to clear up an area in fact"). Every NATO or RUAF soldier a player kills is one on the
 * tally of the ground he fell on (kills within MERGE blocks of one another share a tally; a tally lapses COUNT_MINUTES
 * after its last kill). At KILLS the ground is CLEARED, everyone is told, and while that lasts the director places no
 * soldier - ambient, a group's other members, a garrison's refill, an armoured patrol - within RADIUS blocks of it. A kill
 * on cleared ground renews it. Marks are saved with the world (`gscraft_cleared`), so a restart does not bring the soldiers back;
 * they run on the world's game time, MINUTES long (0 = forever). The Dead and the scavengers are not held back: a cleared
 * street is quiet of rifles, not empty. What is placed outside a mark may still walk into it.
 * {@code /gscraft cleared} lists the marks; {@code /gscraft cleared mark <x> <z>} and {@code ... forget} are the console's.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Cleared extends SavedData {
    private static final String NAME = "gscraft_cleared";

    public static int RADIUS = 96;
    public static int MERGE = 48;
    public static int MINUTES = 120;
    /** soldiers players must kill within MERGE of one another, inside COUNT_MINUTES, before that ground counts as cleared */
    public static int KILLS = 8;
    public static int COUNT_MINUTES = 30;

    /** kills below KILLS: a tally that lapses at `until`; at KILLS: cleared ground until `until` */
    private record Mark(int x, int z, long until, int kills) {
        boolean cleared() {
            return kills >= KILLS;
        }
    }

    private final List<Mark> marks = new ArrayList<>();

    public static Cleared get(ServerLevel level) {
        return level.getServer().overworld().getDataStorage().computeIfAbsent(Cleared::load, Cleared::new, NAME);
    }

    private static Cleared load(CompoundTag tag) {
        Cleared data = new Cleared();
        ListTag list = tag.getList("Marks", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag m = list.getCompound(i);
            data.marks.add(new Mark(m.getInt("X"), m.getInt("Z"), m.getLong("Until"), m.contains("Kills") ? m.getInt("Kills") : KILLS));
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Mark m : marks) {
            CompoundTag t = new CompoundTag();
            t.putInt("X", m.x());
            t.putInt("Z", m.z());
            t.putLong("Until", m.until());
            t.putInt("Kills", m.kills());
            list.add(t);
        }
        tag.put("Marks", list);
        return tag;
    }

    private static long until(ServerLevel level) {
        return MINUTES <= 0 ? Long.MAX_VALUE : level.getGameTime() + MINUTES * 1200L;
    }

    /** a soldier fell here to a player: one more on the tally of the ground he fell on; at KILLS the ground is cleared. Returns the tally. */
    public static int mark(ServerLevel level, int x, int z) {
        return mark(level, x, z, 1);
    }

    public static int mark(ServerLevel level, int x, int z, int kills) {
        Cleared data = get(level);
        long now = level.getGameTime();
        data.marks.removeIf(m -> m.until() <= now);
        long tally = now + COUNT_MINUTES * 1200L;
        for (int i = 0; i < data.marks.size(); i++) {
            Mark m = data.marks.get(i);
            if (Math.abs(m.x() - x) > MERGE || Math.abs(m.z() - z) > MERGE) continue;
            int n = Math.min(KILLS, m.kills() + kills);
            boolean nowCleared = n >= KILLS;
            data.marks.set(i, new Mark(m.x(), m.z(), nowCleared ? until(level) : tally, n));   // a kill on cleared ground renews it
            data.setDirty();
            if (nowCleared && !m.cleared()) announce(level, m.x(), m.z());
            return n;
        }
        int n = Math.min(KILLS, kills);
        data.marks.add(new Mark(x, z, n >= KILLS ? until(level) : tally, n));
        data.setDirty();
        if (n >= KILLS) announce(level, x, z);
        return n;
    }

    private static void announce(ServerLevel level, int x, int z) {
        level.getServer().getPlayerList().broadcastSystemMessage(Component.translatable("gscraft.cleared", x, z).withStyle(net.minecraft.ChatFormatting.GOLD), false);
        GscraftWar.LOG.info("[gscraft] cleared: {} kills round {} {}; no soldier is placed within {} of it for {}", KILLS, x, z, RADIUS, MINUTES <= 0 ? "good" : MINUTES + " minutes");
    }

    /** may a soldier be placed here? not inside a live mark */
    public static boolean holds(ServerLevel level, double x, double z) {
        if (RADIUS <= 0) return false;
        long now = level.getGameTime();
        for (Mark m : get(level).marks) {
            if (m.cleared() && m.until() > now && (m.x() - x) * (m.x() - x) + (m.z() - z) * (m.z() - z) <= (double) RADIUS * RADIUS) return true;
        }
        return false;
    }

    @SubscribeEvent
    public static void death(LivingDeathEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(mob.level() instanceof ServerLevel level) || level.dimension() != Level.OVERWORLD) return;
        if (!Director.soldier(ForgeRegistries.ENTITY_TYPES.getKey(mob.getType()))) return;
        Entity killer = event.getSource().getEntity();
        if (killer != null && !(killer instanceof ServerPlayer) && killer.getControllingPassenger() instanceof ServerPlayer driver) killer = driver;   // a player's vehicle
        if (!(killer instanceof ServerPlayer) && !(mob.getKillCredit() instanceof ServerPlayer)) return;
        mark(level, mob.getBlockX(), mob.getBlockZ());
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("cleared").executes(ctx -> {
                    ServerLevel level = ctx.getSource().getServer().overworld();
                    long now = level.getGameTime();
                    StringBuilder sb = new StringBuilder("cleared ground (radius " + RADIUS + ", " + (MINUTES <= 0 ? "for good" : MINUTES + " min") + "):");
                    int live = 0;
                    for (Mark m : get(level).marks) {
                        if (m.until() <= now) continue;
                        live++;
                        sb.append("\n  ").append(m.x()).append(' ').append(m.z()).append(m.cleared() ? " CLEARED" : " " + m.kills() + " of " + KILLS + " kills")
                                .append(m.until() == Long.MAX_VALUE ? " for good" : " for " + (m.until() - now) / 1200 + " more min");
                    }
                    int n = live;
                    ctx.getSource().sendSuccess(() -> Component.literal(n == 0 ? "no ground is marked cleared" : sb.toString()), false);
                    return n;
                }).then(Commands.literal("mark").then(Commands.argument("x", IntegerArgumentType.integer()).then(Commands.argument("z", IntegerArgumentType.integer()).executes(ctx -> {
                    int n = mark(ctx.getSource().getServer().overworld(), IntegerArgumentType.getInteger(ctx, "x"), IntegerArgumentType.getInteger(ctx, "z"));
                    ctx.getSource().sendSuccess(() -> Component.literal("a kill counted there: " + n + " of " + KILLS + (n >= KILLS ? " - CLEARED" : "")), false);
                    return n;
                })))).then(Commands.literal("forget").executes(ctx -> {
                    Cleared data = get(ctx.getSource().getServer().overworld());
                    int n = data.marks.size();
                    data.marks.clear();
                    data.setDirty();
                    ctx.getSource().sendSuccess(() -> Component.literal("forgot " + n + " marks"), false);
                    return n;
                }))));
    }
}
