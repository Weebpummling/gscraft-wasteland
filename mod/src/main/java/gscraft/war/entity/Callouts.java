package gscraft.war.entity;

import gscraft.war.GscraftWar;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Mob;

import java.util.HashMap;
import java.util.Map;

/**
 * What a fighter says (feasibility A5; interface E1: chat subtitles until there is voice). One line per key per
 * fighter every thirty seconds, one voice per twenty blocks every three seconds, to the players within earshot. The text is a lang key, {@code gscraft.callout.<key>},
 * with the fighter's name as its argument.
 */
public final class Callouts {
    private static final double EARSHOT = 24.0D;
    /** the same line from the same fighter: once in thirty seconds (owner, 2026-09-10: they were too common) */
    private static final int THROTTLE = 600;
    /** one voice per area: a callout within this of another in the last AREA_TICKS is dropped */
    private static final double AREA = 20.0D;
    private static final int AREA_TICKS = 60;
    private static final Map<String, Long> last = new HashMap<>();
    private static final java.util.List<Object[]> recent = new java.util.ArrayList<>();

    private Callouts() {}

    public static void say(Mob mob, String key) {
        if (!(mob.level() instanceof ServerLevel level)) return;
        long now = level.getGameTime();
        String id = mob.getUUID() + ":" + key;
        Long prev = last.get(id);
        if (prev != null && now - prev < THROTTLE) return;
        recent.removeIf(r -> now - (long) r[1] > AREA_TICKS);
        for (Object[] r : recent) {
            if (((net.minecraft.world.phys.Vec3) r[0]).distanceToSqr(mob.position()) <= AREA * AREA) return;
        }
        recent.add(new Object[] {mob.position(), now});
        last.put(id, now);
        if (last.size() > 2048) last.entrySet().removeIf(e -> now - e.getValue() > 1200);
        Component line = Component.translatable("gscraft.callout." + key, mob.getDisplayName());
        int heard = 0;
        for (ServerPlayer p : level.players()) {
            if (p.distanceToSqr(mob) <= EARSHOT * EARSHOT) {
                p.sendSystemMessage(line);
                heard++;
            }
        }
        GscraftWar.LOG.debug("[gscraft] callout {} by {} heard by {}", key, mob.getName().getString(), heard);
    }
}
