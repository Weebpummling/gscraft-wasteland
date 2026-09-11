package gscraft.war.entity;

import gscraft.war.world.Director;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Cover (feasibility B1): a standing spot near the fighter where a line from the target's eyes to chest height is
 * blocked, and a line from a lean beside the spot is clear at the crouched eye, so the fighter can fire from the
 * lean and step back.
 * Sixteen candidates, three to ten blocks out, biased toward the fighter's side of the target; the nearest that
 * works wins. About fifty raycasts per search, every second per fighter in a fight.
 */
public final class Cover {
    public static int SAMPLES = 16;
    public static double MIN_R = 3.0D;
    public static double MAX_R = 10.0D;
    private static final double CHEST = 1.2D;
    public static double LEAN = 0.8D;
    public static double TOO_CLOSE = 5.0D;

    /**
     * @param spot the block to stand on (feet)
     * @param lean the point to step to when firing
     */
    public record Spot(BlockPos spot, Vec3 lean) {
        public Vec3 stand() {
            return Vec3.atBottomCenterOf(spot);
        }
    }

    private Cover() {}

    /** true when the target's eyes cannot see a chest at this standing spot */
    public static boolean covered(ServerLevel level, Mob mob, LivingEntity target, Vec3 stand) {
        return clipBlocked(level, mob, target.getEyePosition(), stand.add(0.0D, CHEST, 0.0D));
    }

    private static boolean clipBlocked(ServerLevel level, Mob mob, Vec3 from, Vec3 to) {
        return level.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, mob)).getType() != HitResult.Type.MISS;
    }

    public static Spot find(ServerLevel level, Mob mob, LivingEntity target, double maxFromTarget) {
        RandomSource random = mob.getRandom();
        Vec3 eyes = target.getEyePosition();
        // the fighter fires from the lean crouched, so the lean must see out from the crouched eye
        double eye = mob.getEyeHeight(net.minecraft.world.entity.Pose.CROUCHING);
        Vec3 toTarget = target.position().subtract(mob.position());
        double heading = Math.atan2(toTarget.z, toTarget.x);
        Spot best = null;
        double bestScore = Double.MAX_VALUE;
        for (int i = 0; i < SAMPLES; i++) {
            // most candidates on the fighter's own side: away from the target and to its flanks
            double angle = heading + Math.PI + (random.nextDouble() - 0.5D) * Math.PI * 1.4D;
            double r = MIN_R + random.nextDouble() * (MAX_R - MIN_R);
            BlockPos raw = BlockPos.containing(mob.getX() + Math.cos(angle) * r, mob.getY(), mob.getZ() + Math.sin(angle) * r);
            BlockPos spot = Director.nearestStand(level, raw);
            if (spot == null) continue;
            Vec3 stand = Vec3.atBottomCenterOf(spot);
            double toT = stand.distanceTo(target.position());
            if (toT < TOO_CLOSE || toT > maxFromTarget) continue;
            if (!clipBlocked(level, mob, eyes, stand.add(0.0D, CHEST, 0.0D))) continue;
            // a lean to either side, perpendicular to the line to the target, with a clear line from head height
            Vec3 dir = target.position().subtract(stand);
            Vec3 side = new Vec3(-dir.z, 0.0D, dir.x).normalize().scale(LEAN);
            Vec3 lean = null;
            for (Vec3 candidate : new Vec3[] {stand.add(side), stand.subtract(side)}) {
                // the body has to fit at the lean itself: a spot beside a bush whose lean sits in the bush is no cover
                if (!level.noCollision(mob, mob.getBoundingBox().move(candidate.subtract(mob.position())))) continue;
                if (!clipBlocked(level, mob, candidate.add(0.0D, eye, 0.0D), eyes)) {
                    lean = candidate;
                    break;
                }
            }
            if (lean == null) continue;
            double score = stand.distanceTo(mob.position()) + Math.abs(toT - Math.min(maxFromTarget, 20.0D)) * 0.25D;
            if (score < bestScore) {
                bestScore = score;
                best = new Spot(spot, lean);
            }
        }
        return best;
    }
}
