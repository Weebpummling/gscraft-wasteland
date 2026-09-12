package gscraft.war.armour;

import gscraft.war.GscraftWar;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.Entity;

import java.util.HashMap;
import java.util.Map;

/**
 * What the players are told about armour (design §4; owner 2026-09-12: no hit numbers, only a module that breaks).
 * From the driver's tick: a module lost (turret, engine, a track), the withdrawal, the destruction with the
 * killer's name, and the first contact - "engine noise to the north" - when a player comes inside the contact
 * range of a crewed vehicle. Under it a bar for the vehicle the crew is engaged with, health as the bar and the
 * modules as letters, dimmed when gone. Every line goes to the players within earshot and to the log.
 */
public final class Reports {
    public static double EARSHOT = 64.0D;
    public static double CONTACT = 96.0D;
    private static final int CONTACT_AGAIN = 6000;
    private static final Map<String, Long> contacts = new HashMap<>();
    private static final Map<Integer, ServerBossEvent> bars = new HashMap<>();

    private Reports() {}

    /** the driver's tick */
    public static void tick(Crew crew, Entity v, boolean[] partsBefore, boolean[] partsNow, boolean wreckBefore, boolean wreckNow) {
        ServerLevel level = (ServerLevel) crew.level();
        String[] keys = {"turret", "engine", "track_left", "track_right"};
        for (int i = 0; i < 4; i++) {
            if (partsNow[i] && !partsBefore[i]) say(level, v, "gscraft.armour." + keys[i]);
        }
        if (wreckNow && !wreckBefore) {
            Entity killer = lastAttacker(v);
            say(level, v, killer == null ? "gscraft.armour.destroyed" : "gscraft.armour.destroyed_by", killer == null ? Component.empty() : killer.getDisplayName());
            dropBar(v);
        }
        if (crew.tickCount % 20 == 0) {
            contact(level, v);
            bar(level, crew, v, partsNow, wreckNow);
        }
    }

    public static void withdrawing(Entity v) {
        if (v.level() instanceof ServerLevel level) say(level, v, "gscraft.armour.withdrawing");
    }

    private static void contact(ServerLevel level, Entity v) {
        long now = level.getGameTime();
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || p.distanceToSqr(v) > CONTACT * CONTACT) continue;
            String id = p.getUUID() + ":" + v.getUUID();
            Long prev = contacts.get(id);
            if (prev != null && now - prev < CONTACT_AGAIN) continue;
            contacts.put(id, now);
            p.sendSystemMessage(Component.translatable("gscraft.armour.contact", v.getDisplayName(), Component.translatable("gscraft.dir." + compass(p, v))));
        }
        if (contacts.size() > 1024) contacts.entrySet().removeIf(e -> now - e.getValue() > CONTACT_AGAIN);
    }

    /** eight points, from the player to the vehicle */
    private static String compass(Entity from, Entity to) {
        double dx = to.getX() - from.getX();
        double dz = to.getZ() - from.getZ();
        double deg = Math.toDegrees(Math.atan2(dx, -dz));   // 0 = north (-z), 90 = east (+x)
        int i = (int) Math.floor(((deg + 360.0D + 22.5D) % 360.0D) / 45.0D);
        return new String[] {"n", "ne", "e", "se", "s", "sw", "w", "nw"}[i];
    }

    private static void bar(ServerLevel level, Crew crew, Entity v, boolean[] parts, boolean wreck) {
        boolean show = (crew.engaged != null || crew.bossStage != null) && !wreck;
        if (!show) {
            dropBar(v);
            return;
        }
        float max = Vehicles.maxHealth(v);
        float health = Vehicles.health(v);
        String letters = (parts[0] ? "§8T§r" : "T") + " " + (parts[1] ? "§8E§r" : "E") + " " + (parts[2] ? "§8L§r" : "L") + " " + (parts[3] ? "§8R§r" : "R");
        ServerBossEvent bar = bars.computeIfAbsent(v.getId(), k -> new ServerBossEvent(Component.empty(), BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10));
        bar.setName(Component.literal(v.getName().getString() + "   " + letters));
        bar.setProgress(Float.isNaN(max) || max <= 0.0F ? 1.0F : Math.max(0.0F, Math.min(1.0F, health / max)));
        for (ServerPlayer p : level.players()) {
            boolean near = !p.isSpectator() && p.distanceToSqr(v) <= EARSHOT * EARSHOT;
            if (near && !bar.getPlayers().contains(p)) bar.addPlayer(p);
            else if (!near && bar.getPlayers().contains(p)) bar.removePlayer(p);
        }
    }

    public static void dropBar(Entity v) {
        ServerBossEvent bar = bars.remove(v.getId());
        if (bar != null) bar.removeAllPlayers();
    }

    /** the vehicle is gone without a wreck (an overkill removes it at once): reported from what the crew last saw */
    public static void destroyed(ServerLevel level, net.minecraft.world.phys.Vec3 at, Component vehicle, Component killer) {
        Component line = killer == null ? Component.translatable("gscraft.armour.destroyed", vehicle) : Component.translatable("gscraft.armour.destroyed_by", vehicle, killer);
        for (ServerPlayer p : level.players()) {
            if (p.position().distanceToSqr(at) <= EARSHOT * EARSHOT) p.sendSystemMessage(line);
        }
        GscraftWar.LOG.info("[gscraft] armour: {} {}", vehicle.getString(), killer == null ? "destroyed" : "destroyed_by");
    }

    public static Entity lastAttacker(Entity v) {
        try {
            Object r = v.getClass().getMethod("getLastAttacker").invoke(v);
            return r instanceof Entity e ? e : null;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return null;
        }
    }

    private static void say(ServerLevel level, Entity v, String key, Component... extra) {
        Component[] args = new Component[extra.length + 1];
        args[0] = v.getDisplayName();
        System.arraycopy(extra, 0, args, 1, extra.length);
        Component line = Component.translatable(key, (Object[]) args);
        for (ServerPlayer p : level.players()) {
            if (p.distanceToSqr(v) <= EARSHOT * EARSHOT) p.sendSystemMessage(line);
        }
        GscraftWar.LOG.info("[gscraft] armour: {} {}", v.getName().getString(), key.substring("gscraft.armour.".length()));
    }
}
