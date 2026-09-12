package gscraft.war.combat;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.Optional;

/**
 * Where a bullet meets a body. A projectile's position at the moment its mod reports the hit is the start of
 * its step, not the impact - a TACZ round moves 12-28 blocks a tick - but its velocity is on it, so the impact
 * is the target's box clipped by the segment position -> position + velocity (or, if the mod already moved it,
 * the segment from its previous position). The zone is read from the impact's height as a fraction of the
 * body's height and its distance from the body's axis.
 */
public final class Ballistics {
    /** the head reaches this far below the eyes */
    public static double HEAD_BELOW_EYES = 0.2D;
    /** the thorax band, as fractions of the body's height; above it and below the head is still the thorax */
    public static double THORAX_BOTTOM = 0.55D;
    public static double STOMACH_BOTTOM = 0.4D;
    /** the outer share of the body's half-width, in the thorax band, that is an arm */
    public static double ARM_SHARE = 0.3D;
    private static final double GRACE = 0.1D;

    private Ballistics() {}

    /** the impact point on the target for this projectile, from its step; the target's centre if nothing clips */
    public static Vec3 impact(Entity target, Entity projectile) {
        AABB box = target.getBoundingBox().inflate(GRACE);
        Vec3 pos = projectile.position();
        Vec3 delta = projectile.getDeltaMovement();
        Vec3 hit = clip(box, pos, pos.add(delta));
        if (hit == null) hit = clip(box, new Vec3(projectile.xo, projectile.yo, projectile.zo), pos);
        if (hit == null) hit = clip(box, pos.subtract(delta), pos.add(delta.scale(2.0D)));
        if (hit == null) hit = box.contains(pos) ? pos : nearest(box, pos);
        return hit;
    }

    /** the impact of a segment on the target, for the tests and the command; null if it misses */
    public static Vec3 clipTarget(Entity target, Vec3 from, Vec3 to) {
        return clip(target.getBoundingBox().inflate(GRACE), from, to);
    }

    private static Vec3 clip(AABB box, Vec3 from, Vec3 to) {
        if (from.distanceToSqr(to) < 1.0E-6D) return box.contains(from) ? from : null;
        if (box.contains(from)) return from;
        Optional<Vec3> c = box.clip(from, to);
        return c.orElse(null);
    }

    private static Vec3 nearest(AABB box, Vec3 p) {
        return new Vec3(Math.max(box.minX, Math.min(box.maxX, p.x)), Math.max(box.minY, Math.min(box.maxY, p.y)), Math.max(box.minZ, Math.min(box.maxZ, p.z)));
    }

    /**
     * The zone an impact point falls in on this body, in its current pose. The arms are judged sideways to the
     * shot: how far the impact sits from the body's axis across the line of fire, since the impact is always on
     * the body's surface and its plain distance from the axis says nothing.
     */
    public static Zone zone(LivingEntity target, Vec3 hit, Vec3 direction) {
        double h = Math.max(0.1D, target.getBbHeight());
        double rel = (hit.y - target.getY()) / h;
        double eyes = target.getEyeHeight() / h;
        if (rel >= eyes - HEAD_BELOW_EYES / h) return Zone.HEAD;
        if (rel >= THORAX_BOTTOM) {
            double dx = hit.x - target.getX();
            double dz = hit.z - target.getZ();
            double half = Math.max(0.1D, target.getBbWidth() / 2.0D);
            double len = Math.sqrt(direction.x * direction.x + direction.z * direction.z);
            double out;
            if (len < 1.0E-6D) {
                out = Math.sqrt(dx * dx + dz * dz) / half;   // a shot from straight above or below: radial is all there is
            } else {
                out = Math.abs(dx * direction.z - dz * direction.x) / len / half;
            }
            return out >= 1.0D - ARM_SHARE ? Zone.ARMS : Zone.THORAX;
        }
        if (rel >= STOMACH_BOTTOM) return Zone.STOMACH;
        return Zone.LEGS;
    }
}
