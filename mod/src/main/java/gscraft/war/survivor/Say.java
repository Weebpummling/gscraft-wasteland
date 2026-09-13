package gscraft.war.survivor;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * The radio line (interface §3.4): a click, then {@code ♪ [TUNE]  the text} - the name in the survivor's colour,
 * the text from the lang file ({@code gscraft.say.<npc>.<key>}). One line per player per 20 s; later lines queue;
 * a queue longer than three collapses to the newest per speaker. A hello line jumps the queue.
 */
public final class Say {
    private Say() {}

    public static int SPACING = 400;
    public static int COLLAPSE = 3;

    private record Line(String npc, String key) {}

    private static final Map<UUID, Deque<Line>> QUEUE = new HashMap<>();
    private static final Map<UUID, Long> LAST = new HashMap<>();

    public static MutableComponent render(Survivors.Def d, String key) {
        return Component.literal("♪ ").withStyle(ChatFormatting.DARK_GRAY)
                .append(Component.literal("[" + d.call() + "]").withStyle(d.format()))
                .append(Component.literal("  "))
                .append(Component.translatable("gscraft.say." + d.id() + "." + key).withStyle(ChatFormatting.WHITE));
    }

    /** the line as the server would print it (the console's view; the client renders its own lang) */
    public static String rendered(String npc, String key) {
        Survivors.Def d = Survivors.byId(npc);
        return d == null ? "no survivor " + npc : render(d, key).getString();
    }

    public static boolean queue(ServerPlayer p, String npc, String key, boolean now) {
        Survivors.Def d = Survivors.byId(npc);
        if (d == null) return false;
        long tick = p.server.getTickCount();
        if (now) {
            send(p, d, key, tick);
            return true;
        }
        Deque<Line> q = QUEUE.computeIfAbsent(p.getUUID(), k -> new ArrayDeque<>());
        q.add(new Line(npc, key));
        if (q.size() > COLLAPSE) {
            Map<String, Line> newest = new LinkedHashMap<>();
            for (Line l : q) {
                newest.remove(l.npc());
                newest.put(l.npc(), l);
            }
            q.clear();
            q.addAll(newest.values());
        }
        return true;
    }

    /** the next line comes no sooner than this many ticks from now (after a title, say) */
    public static void hold(ServerPlayer p, int ticks) {
        LAST.put(p.getUUID(), (long) p.server.getTickCount() - SPACING + ticks);
    }

    public static void tick(MinecraftServer server) {
        if (QUEUE.isEmpty()) return;
        long tick = server.getTickCount();
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            Deque<Line> q = QUEUE.get(p.getUUID());
            if (q == null || q.isEmpty()) continue;
            if (tick - LAST.getOrDefault(p.getUUID(), (long) -SPACING) < SPACING) continue;
            Line l = q.poll();
            Survivors.Def d = Survivors.byId(l.npc());
            if (d != null) send(p, d, l.key(), tick);
        }
    }

    public static int pending(ServerPlayer p) {
        Deque<Line> q = QUEUE.get(p.getUUID());
        return q == null ? 0 : q.size();
    }

    private static void send(ServerPlayer p, Survivors.Def d, String key, long tick) {
        p.playNotifySound(SoundEvents.NOTE_BLOCK_HAT.get(), SoundSource.PLAYERS, 0.4f, 0.5f);
        p.sendSystemMessage(render(d, key));
        LAST.put(p.getUUID(), tick);
    }
}
