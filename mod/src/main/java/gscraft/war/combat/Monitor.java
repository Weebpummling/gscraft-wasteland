package gscraft.war.combat;

import gscraft.war.GscraftWar;
import gscraft.war.entity.Anim;
import gscraft.war.entity.Animated;
import gscraft.war.entity.FighterState;
import gscraft.war.entity.GunUser;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * The fire monitor (owner, 2026-09-12: "the NPCs are still not reacting to the shots that land near them from player
 * bullets"). {@code /gscraft monitor on [radius]} and every gun event the server sees within that radius of the
 * watcher is told to them in chat as it happens and written to the log: each shot the server registers, each bullet
 * into a block with the impact point and every fighter close enough to count (suppression before and after) or else
 * the nearest fighter and how far it was, each bullet into a fighter with the zone and what the suppression and the
 * hold did. Once a second the fighters within the radius are listed with their suppression, pose, hold and target,
 * so the decay and the thresholds can be watched against the numbers in {@code /gscraft settings fight}.
 * {@code status} gives the counts since it was switched on; {@code off} ends it.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Monitor {
    private static final class Watch {
        final int radius;
        final long since;
        int shots, impacts, near, hits;

        Watch(int radius, long since) {
            this.radius = radius;
            this.since = since;
        }
    }

    private static final Map<UUID, Watch> WATCHERS = new HashMap<>();
    private static final int LIST_EVERY = 20;
    private static final int LIST_MAX = 6;

    private Monitor() {}

    public static boolean on() {
        return !WATCHERS.isEmpty();
    }

    public static String start(ServerPlayer player, int radius) {
        WATCHERS.put(player.getUUID(), new Watch(radius, player.level().getGameTime()));
        return "monitor on within " + radius + " blocks: shots, impacts, hits and a fighter list once a second; /gscraft monitor off ends it";
    }

    public static String stop(ServerPlayer player) {
        Watch w = WATCHERS.remove(player.getUUID());
        return w == null ? "monitor was off" : "monitor off; " + counts(w, player.level().getGameTime());
    }

    public static String status(ServerPlayer player) {
        Watch w = WATCHERS.get(player.getUUID());
        return w == null ? "monitor off" : counts(w, player.level().getGameTime());
    }

    private static String counts(Watch w, long now) {
        return String.format("since %d s: shots seen %d, impacts %d (fighters suppressed by them %d), hits on fighters %d",
                (now - w.since) / 20, w.shots, w.impacts, w.near, w.hits);
    }

    /** a shot the server registered */
    public static void shot(LivingEntity shooter, String gun) {
        if (!on() || !(shooter.level() instanceof ServerLevel level)) return;
        tell(level, shooter.position(), w -> w.shots++,
                String.format("shot by %s (%s) at %s", shooter.getName().getString(), gun, pos(shooter.position())));
    }

    /** a bullet into a block: who counted and by how much, or how far the nearest fighter was */
    public static void impact(ServerLevel level, Entity shooter, Vec3 at, double radius, List<Mob> near, List<Float> before) {
        if (!on()) return;
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("impact at %s by %s: %d fighter(s) within %.1f", pos(at), shooter == null ? "no owner" : shooter.getName().getString(), near.size(), radius));
        for (int i = 0; i < near.size(); i++) {
            Mob m = near.get(i);
            FighterState st = ((GunUser) m).fighterState();
            sb.append(String.format("; %s %.1f away, suppression %.2f -> %.2f", m.getName().getString(), m.position().distanceTo(at), before.get(i), st.suppression));
        }
        if (near.isEmpty()) {
            Mob nearest = null;
            double best = Double.MAX_VALUE;
            for (Mob m : level.getEntitiesOfClass(Mob.class, new net.minecraft.world.phys.AABB(at, at).inflate(24.0D), m -> m instanceof GunUser)) {
                double d = m.position().distanceTo(at);
                if (d < best) {
                    best = d;
                    nearest = m;
                }
            }
            sb.append(nearest == null ? "; no fighter within 24" : String.format("; nearest %s at %.1f (outside near_radius)", nearest.getName().getString(), best));
        }
        int n = near.size();
        tell(level, at, w -> {
            w.impacts++;
            w.near += n;
        }, sb.toString());
    }

    /** a bullet into a fighter */
    public static void hit(ServerLevel level, Mob mob, LivingEntity attacker, String event, float before, boolean flatBefore) {
        if (!on()) return;
        FighterState st = ((GunUser) mob).fighterState();
        long now = level.getGameTime();
        tell(level, mob.position(), w -> w.hits++,
                String.format("hit on %s by %s (%s): suppression %.2f -> %.2f, pose %s, target %s, flat %s -> %s (hold %d ticks), last hit %s",
                        mob.getName().getString(), attacker == null ? "?" : attacker.getName().getString(), event, before, st.suppression, mob.getPose(),
                        mob.getTarget() == null ? "none" : mob.getTarget().getName().getString(), flatBefore, st.pinned(now), Math.max(0, st.flatUntil - now),
                        st.lastHit.isEmpty() ? "-" : st.lastHit));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || WATCHERS.isEmpty()) return;
        for (ServerLevel level : event.getServer().getAllLevels()) {
            if (level.getGameTime() % LIST_EVERY != 0) continue;
            for (ServerPlayer p : level.players()) {
                Watch w = WATCHERS.get(p.getUUID());
                if (w == null) continue;
                List<String> lines = new ArrayList<>();
                long now = level.getGameTime();
                for (Mob m : level.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(w.radius), m -> m instanceof GunUser && m.isAlive())) {
                    if (lines.size() >= LIST_MAX) break;
                    FighterState st = ((GunUser) m).fighterState();
                    lines.add(String.format("  %s %.0fm: suppression %.2f, pose %s, flat %s (%d), target %s, anim %s",
                            m.getName().getString(), m.distanceTo(p), st.suppression, mob(m), st.pinned(now), Math.max(0, st.flatUntil - now),
                            m.getTarget() == null ? "none" : m.getTarget().getName().getString(),
                            m instanceof Animated a ? Anim.unpack(a.animByte()) + "#" + Anim.seq(a.animByte()) : "-"));
                }
                if (lines.isEmpty()) continue;
                p.sendSystemMessage(Component.literal("§8[mon] fighters within " + w.radius + ":"));
                for (String l : lines) p.sendSystemMessage(Component.literal("§8" + l));
            }
        }
    }

    private static String mob(Mob m) {
        return m.getPose().name();
    }

    private interface Count {
        void add(Watch w);
    }

    private static void tell(ServerLevel level, Vec3 at, Count count, String text) {
        GscraftWar.LOG.info("[gscraft] [mon] {}", text);
        for (ServerPlayer p : level.players()) {
            Watch w = WATCHERS.get(p.getUUID());
            if (w == null || p.position().distanceTo(at) > w.radius) continue;
            count.add(w);
            p.sendSystemMessage(Component.literal("§7[mon] " + text));
        }
    }

    private static String pos(Vec3 v) {
        return String.format("%.1f %.1f %.1f", v.x, v.y, v.z);
    }
}
