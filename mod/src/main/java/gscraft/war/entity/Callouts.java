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
 * fighter every five seconds, to the players within earshot. The text is a lang key, {@code gscraft.callout.<key>},
 * with the fighter's name as its argument.
 */
public final class Callouts {
    private static final double EARSHOT = 24.0D;
    private static final int THROTTLE = 100;
    private static final Map<String, Long> last = new HashMap<>();

    private Callouts() {}

    public static void say(Mob mob, String key) {
        if (!(mob.level() instanceof ServerLevel level)) return;
        long now = level.getGameTime();
        String id = mob.getUUID() + ":" + key;
        Long prev = last.get(id);
        if (prev != null && now - prev < THROTTLE) return;
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
