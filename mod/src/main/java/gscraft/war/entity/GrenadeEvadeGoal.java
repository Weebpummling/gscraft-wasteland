package gscraft.war.entity;

import gscraft.war.faction.Factions;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;

/**
 * A grenade on the ground nearby: run (owner, 2026-09-12). A fighter that is pinned or crawling cannot - it stays
 * where it is and takes it. Grenades are Superb Warfare's thrown projectiles (hand and RGO), and the players' too.
 */
public class GrenadeEvadeGoal extends Goal {
    private static final String SW_PROJECTILES = "com.atsuishio.superbwarfare.entity.projectile.";
    /** a grenade this close is run from, this far, for at most this long */
    public static double RADIUS = 6.0D;
    public static double RUN = 8.0D;
    public static int MAX_TICKS = 60;
    public static double SPEED = 1.4D;

    private final PathfinderMob mob;
    private Entity grenade;
    private int ticks;

    public <T extends PathfinderMob & GunUser> GrenadeEvadeGoal(T mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private FighterState state() {
        return ((GunUser) mob).fighterState();
    }

    public static boolean isGrenade(Entity e) {
        if (!(e instanceof Projectile)) return false;
        String name = e.getClass().getName();
        return name.startsWith(SW_PROJECTILES) && name.contains("Grenade") && !name.contains("Smoke");   // smoke is not a thing to run from
    }

    private Entity nearest() {
        List<Entity> found = mob.level().getEntities(mob, mob.getBoundingBox().inflate(RADIUS), e -> isGrenade(e) && !(e instanceof Projectile p && p.getOwner() != null && Factions.allied(mob, p.getOwner())));
        Entity best = null;
        double bestD = Double.MAX_VALUE;
        for (Entity e : found) {
            double d = e.distanceToSqr(mob);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }

    @Override
    public boolean canUse() {
        FighterState s = state();
        long now = mob.level().getGameTime();
        if (s.pinned(now) || s.crawlUntil > now) return false;
        grenade = nearest();
        return grenade != null;
    }

    @Override
    public boolean canContinueToUse() {
        return grenade != null && grenade.isAlive() && ticks < MAX_TICKS && !mob.getNavigation().isDone();
    }

    @Override
    public void start() {
        ticks = 0;
        Vec3 away = DefaultRandomPos.getPosAway(mob, (int) RUN, 4, grenade.position());
        if (away == null) away = mob.position().add(mob.position().subtract(grenade.position()).normalize().scale(RUN));
        mob.getNavigation().moveTo(away.x, away.y, away.z, SPEED);
        mob.setSprinting(true);
        Callouts.say(mob, "grenade");
    }

    @Override
    public void tick() {
        ticks++;
    }

    @Override
    public void stop() {
        mob.setSprinting(false);
        grenade = null;
    }
}
