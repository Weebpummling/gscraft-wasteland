package gscraft.war.strike;

import gscraft.war.GscraftWar;
import gscraft.war.armour.Vehicles;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/**
 * The Cobra's run (owner, 2026-09-13): the AH-1F appears 300 blocks out along a random heading, crosses the marker
 * at 35 blocks up and 24 a second, fires its rockets from 120 blocks out in pairs converging on the smoke, works the
 * guns over anything hostile within twelve of it for the five seconds of the pass, then flies out 300 blocks and is
 * unloaded. A hit on the helicopter breaks the run off at once. The hull is the other mod's entity moved as a prop;
 * the rockets and rounds are Superb Warfare's own projectiles.
 */
public final class AirRun {
    public static String HELI = "dragonrise_reforge:ah1f";
    public static int RANGE = 300, HEIGHT = 55, ROCKET_FROM = 120, ROCKET_TO = 60, GUN_RANGE = 60, ROCKETS = 8;
    public static double SPEED = 1.2;
    public static float ROCKET_DAMAGE = 90f, ROCKET_EXPLOSION = 120f, ROCKET_RADIUS = 6f, GUN_DAMAGE = 14f;
    public static int GUN_EVERY = 2, GUN_TARGETS = 12;

    private final ServerLevel level;
    private final BlockPos target;
    private final ServerPlayer caller;
    private final Vec3 start, end, dir;
    private final float heading;
    private Entity heli;
    private float health0 = Float.NaN;
    private int t, rocketsFired, gunTicks;
    private boolean out, done;
    private int forcedX = Integer.MIN_VALUE, forcedZ;

    /** the chunk under the helicopter is kept loaded as it flies (the run starts 300 blocks out); the last one released */
    private void forceUnder(Vec3 pos) {
        int cx = Mth.floor(pos.x) >> 4, cz = Mth.floor(pos.z) >> 4;
        if (cx == forcedX && cz == forcedZ) return;
        if (forcedX != Integer.MIN_VALUE) level.setChunkForced(forcedX, forcedZ, false);
        level.setChunkForced(cx, cz, true);
        forcedX = cx;
        forcedZ = cz;
    }

    /** the engine on: power held at full every tick, so the rotor spins (the mod lerps its rotor to the power) and the engine sound plays on every client */
    private void engine() {
        Sw.set(heli, "setEngineStart", true);
        Sw.set(heli, "setEngineStartOver", true);
        Sw.set(heli, "setPower", 1.0f);
    }

    private void release() {
        if (forcedX != Integer.MIN_VALUE) level.setChunkForced(forcedX, forcedZ, false);
        forcedX = Integer.MIN_VALUE;
    }

    AirRun(ServerLevel level, BlockPos target, ServerPlayer caller) {
        this.level = level;
        this.target = target;
        this.caller = caller;
        double a = level.getRandom().nextDouble() * Math.PI * 2;
        Vec3 c = Strikes.centre(target);
        dir = new Vec3(Math.cos(a), 0, Math.sin(a));
        start = c.subtract(dir.scale(RANGE)).add(0, HEIGHT, 0);
        end = c.add(dir.scale(RANGE)).add(0, HEIGHT, 0);
        heading = (float) Math.toDegrees(Math.atan2(-dir.x, dir.z));
    }

    /** @return false when the run is over and the helicopter unloaded */
    boolean tick() {
        if (done) return false;
        if (heli == null) {
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(HELI));
            heli = type == null ? null : type.create(level);
            if (heli == null) {
                GscraftWar.LOG.warn("[gscraft] strike: no helicopter entity {}", HELI);
                done = true;
                return false;
            }
            forceUnder(start);
            heli.setPos(start);
            heli.setYRot(heading);
            heli.setNoGravity(true);
            heli.setInvulnerable(false);
            heli.addTag("gscraft_air_run");
            level.addFreshEntity(heli);
            health0 = Vehicles.health(heli);
            GscraftWar.LOG.info("[gscraft] strike: {} inbound from {} to {}", HELI, start, target.toShortString());
        }
        if (!heli.isAlive()) {
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is down");
            Strikes.tell("tune", "air_down", level.getServer());
            release();
            done = true;
            return false;
        }
        t++;
        // a hit breaks the run off: straight out from here
        float h = Vehicles.health(heli);
        if (!out && !Float.isNaN(health0) && !Float.isNaN(h) && h < health0 - 0.5f) {
            out = true;
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is hit, breaking off");
            Strikes.tell("tune", "air_hit", level.getServer());
        }
        Vec3 pos = heli.position().add(dir.scale(SPEED));
        forceUnder(pos);
        heli.setPos(pos);
        engine();
        heli.setYRot(heading);
        heli.setDeltaMovement(Vec3.ZERO);
        heli.hurtMarked = true;
        if (t % 20 == 1) Strikes.sound(level, heli.blockPosition(), "ah_6_engine", 4f, 0.8f);
        double along = pos.subtract(Strikes.centre(target).add(0, HEIGHT, 0)).dot(dir);   // negative inbound, positive past
        double dist = -along;
        if (!out) {
            if (dist <= ROCKET_FROM && dist >= ROCKET_TO && rocketsFired < ROCKETS && t % 5 == 0) {
                rocket(pos);
                rocket(pos);
                rocketsFired += 2;
            }
            if (Math.abs(along) <= GUN_RANGE && t % GUN_EVERY == 0) {
                gun(pos);
                gunTicks++;
                if (gunTicks % 4 == 0) Strikes.sound(level, heli.blockPosition(), "ah_6_cannon_fire_3p", 3f, 1f);
            }
        }
        if (along > RANGE - 5 || (out && along > GUN_RANGE + 40) || t > 20 * 60) {
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is off station ({} rockets, {} gun ticks)", rocketsFired, gunTicks);
            Strikes.tell("tune", "air_off", level.getServer());
            heli.discard();
            release();
            done = true;
            return false;
        }
        return true;
    }

    private void rocket(Vec3 from) {
        Entity e = Sw.create(level, "medium_rocket");
        if (!(e instanceof net.minecraft.world.entity.projectile.Projectile r)) return;
        Sw.set(r, "setDamage", ROCKET_DAMAGE);
        Sw.set(r, "setExplosionDamage", ROCKET_EXPLOSION);
        Sw.set(r, "setExplosionRadius", ROCKET_RADIUS);
        Sw.type(r, "HE");
        if (caller != null) r.setOwner(caller);
        Vec3 aim = Strikes.centre(target).add((level.getRandom().nextDouble() * 2 - 1) * 4, 0, (level.getRandom().nextDouble() * 2 - 1) * 4);
        Vec3 d = aim.subtract(from).normalize();
        r.setPos(from.add(dir.scale(3)).add(0, -1.5, 0));
        r.shoot(d.x, d.y, d.z, 4f, 0.3f);
        level.addFreshEntity(r);
        Strikes.sound(level, heli.blockPosition(), "medium_rocket_fire", 3f, 1f);
    }

    private void gun(Vec3 from) {
        Vec3 aim = null;
        AABB box = new AABB(target).inflate(GUN_TARGETS, 8, GUN_TARGETS);
        List<Mob> hostile = level.getEntitiesOfClass(Mob.class, box, m -> m.isAlive() && !m.getTags().contains("gscraft_npc") && !m.getTags().contains("gscraft_air_run"));
        if (!hostile.isEmpty()) aim = hostile.get(level.getRandom().nextInt(hostile.size())).position().add(0, 0.8, 0);
        if (aim == null) aim = Strikes.centre(target).add((level.getRandom().nextDouble() * 2 - 1) * 3, 0, (level.getRandom().nextDouble() * 2 - 1) * 3);
        Entity e = Sw.create(level, "projectile");
        if (!(e instanceof net.minecraft.world.entity.projectile.Projectile b)) return;
        Sw.shooter(b, caller != null ? caller : heli);
        Sw.set(b, "setDamage", GUN_DAMAGE);
        b.setPos(from.add(0, -1, 0));
        Vec3 d = aim.subtract(from).normalize();
        b.shoot(d.x, d.y, d.z, 6f, 1.5f);
        level.addFreshEntity(b);
    }

    void abort() {
        if (heli != null && heli.isAlive()) heli.discard();
        release();
        done = true;
    }

    static float yawTo(Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        return (float) Mth.wrapDegrees(Math.toDegrees(Math.atan2(-d.x, d.z)));
    }

    static boolean living(Entity e) {
        return e instanceof LivingEntity;
    }
}
