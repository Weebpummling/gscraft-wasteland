package gscraft.war.strike;

import gscraft.war.GscraftWar;
import gscraft.war.ModEntities;
import gscraft.war.armour.Armour;
import gscraft.war.armour.Crew;
import gscraft.war.armour.Vehicles;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;
import java.util.Locale;

/**
 * The Cobra's run (owner, 2026-09-13): the AH-1F appears 300 blocks out along a random heading and crosses the
 * marker at 55 blocks up and 24 a second, flown along that line by this class. It is **crewed like the other
 * vehicles** (owner: fired from inside): a crew of the camp's faction sits in the seat, the crew logic lays the
 * mod's own turret and fires the airframe's own weapons at what it sees - the rockets on the run-in, the gun over
 * the smoke - with the mod's aiming, rate and damage. An invisible dummy at the smoke gives it something to fire at
 * when nothing hostile stands there; anything hostile that does outranks it. A hit on the helicopter breaks the run
 * off; 300 blocks past the smoke it is unloaded.
 */
public final class AirRun {
    public static String HELI = "dragonrise_reforge:ah1f";
    public static String FACTION = "camp";
    public static int RANGE = 300, HEIGHT = 55, HEIGHT_LOW = 25, DIVE_FROM = 150, DIVE_TO = 30, ROCKET_FROM = 150, ROCKET_TO = 45, GUN_RANGE = 60;
    public static double SPEED = 1.2;
    public static float POWER = 0.12f;   // the mod's own flying power (a pilot's collective tops out here); 1.0 spun the rotor so fast it strobed
    public static float PITCH_SIGN = 1f;
    public static int ROCKET_EVERY = 3;   // the mod fires one rocket a trigger at its own 450 rpm (2.7 ticks): every three ticks is the pods' full rate
    private int rocketsFired, rocketsOut;

    private final ServerLevel level;
    private final BlockPos target;
    private final ServerPlayer caller;
    private final Vec3 start, dir;
    private final float heading;
    private Entity heli;
    private Crew crew, gunner;
    private Mob dummy;
    private float health0 = Float.NaN;
    private int t, rockets = -1, gun = -1, weapon = -2;
    private boolean out, done;
    private int forcedX = Integer.MIN_VALUE, forcedZ;

    AirRun(ServerLevel level, BlockPos target, ServerPlayer caller) {
        this.level = level;
        this.target = target;
        this.caller = caller;
        double a = level.getRandom().nextDouble() * Math.PI * 2;
        Vec3 c = Strikes.centre(target);
        dir = new Vec3(Math.cos(a), 0, Math.sin(a));
        start = c.subtract(dir.scale(RANGE)).add(0, HEIGHT, 0);
        heading = (float) Math.toDegrees(Math.atan2(-dir.x, dir.z));
    }

    /** the chunk under the helicopter is kept loaded as it flies (the run starts 300 blocks out); the last one released */
    private void forceUnder(Vec3 pos) {
        int cx = Mth.floor(pos.x) >> 4, cz = Mth.floor(pos.z) >> 4;
        if (cx == forcedX && cz == forcedZ) return;
        if (forcedX != Integer.MIN_VALUE) level.setChunkForced(forcedX, forcedZ, false);
        level.setChunkForced(cx, cz, true);
        forcedX = cx;
        forcedZ = cz;
    }

    private void release() {
        if (forcedX != Integer.MIN_VALUE) level.setChunkForced(forcedX, forcedZ, false);
        forcedX = Integer.MIN_VALUE;
    }

    /** the engine on at the mod's flying power: the airframe is fuelled at spawn, so the mod's own engine holds the power and the rotor
     *  turns at a pilot's rate (the mod advances the blade by 30 x power a tick on every client; owner: it strobed at full power) */
    private void engine() {
        Sw.set(heli, "setEngineStart", true);
        Sw.set(heli, "setEngineStartOver", true);
        if (Vehicles.power(heli) < POWER) Sw.set(heli, "setPower", POWER);
    }

    /** the seat's weapons by name: the rockets and the gun; logged once so the names can be checked */
    private void weapons() {
        List<String> names = Vehicles.seatWeapons(heli, 0);
        if (names == null) {
            GscraftWar.LOG.warn("[gscraft] strike: {} lists no seat weapons", HELI);
            return;
        }
        for (int i = 0; i < names.size(); i++) {
            String n = names.get(i).toLowerCase(Locale.ROOT);
            if (rockets < 0 && (n.contains("rocket") || n.contains("hydra") || n.contains("pod"))) rockets = i;
            else if (gun < 0 && (n.contains("gun") || n.contains("cannon") || n.contains("mg") || n.contains("m197"))) gun = i;
        }
        if (gun < 0) gun = 0;
        if (rockets < 0) rockets = names.size() > 1 ? 1 : 0;
        GscraftWar.LOG.info("[gscraft] strike: {} seat weapons {}: rockets {}, gun {}", HELI, names, rockets, gun);
    }

    private void select(int index) {
        if (index == weapon || index < 0) return;
        weapon = index;
        if (crew != null) crew.weaponLock = index;
        Vehicles.changeWeapon(heli, 0, index);
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
            heli.addTag("gscraft_air_run");
            level.addFreshEntity(heli);
            Vehicles.whole(heli);
            Armour.arm(heli);   // the seat's ammunition, as the placed hulls get it
            Vehicles.refuel(heli);   // and its fuel: the mod's engine drains the power every tick without it
            crew = Armour.crew(level, heli, FACTION, null);
            if (crew != null) {
                crew.air = true;
                crew.addTag("gscraft_air_run");
            } else GscraftWar.LOG.warn("[gscraft] strike: no crew could mount the {}", HELI);
            // the turret is the second seat's (TurretControllerIndex 1): a second crew lays and fires the chin gun
            if (heli.getPassengers().size() < 2) {
                gunner = Armour.extraCrew(level, heli, FACTION);
                if (gunner != null) {
                    gunner.air = true;
                    gunner.addTag("gscraft_air_run");
                }
            }
            weapons();
            // the aim point: an invisible, invulnerable hostile at the smoke, outranked by anything real
            dummy = ModEntities.NATO_SOLDIER.get().create(level);
            if (dummy != null) {
                dummy.setPos(target.getX() + 0.5, target.getY() + 0.1, target.getZ() + 0.5);
                dummy.setNoAi(true);
                dummy.setInvisible(true);
                dummy.setInvulnerable(true);
                dummy.setSilent(true);
                dummy.setPersistenceRequired();
                dummy.addTag("gscraft_strike_dummy");
                level.addFreshEntity(dummy);
            }
            health0 = Vehicles.health(heli);
            GscraftWar.LOG.info("[gscraft] strike: {} inbound from {} to {}", HELI, start, target.toShortString());
        }
        if (!heli.isAlive()) {
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is down");
            Strikes.tell("tune", "air_down", level.getServer());
            finish();
            return false;
        }
        t++;
        float h = Vehicles.health(heli);
        if (!out && !Float.isNaN(health0) && !Float.isNaN(h) && h < health0 - 0.5f) {
            out = true;
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is hit, breaking off");
            Strikes.tell("tune", "air_hit", level.getServer());
        }
        // the position is the line's, from the start by the tick count: the powered hull's own lift never compounds into it;
        // the height dives from HEIGHT at DIVE_FROM out to HEIGHT_LOW over the smoke and climbs out the same way (the chin
        // gun's arc reaches the ground only from low; the rockets go where the nose points)
        Vec3 flat = start.add(dir.scale(SPEED * t));
        double alongNow = flat.subtract(Strikes.centre(target).add(0, HEIGHT, 0)).dot(dir);
        double a = Math.abs(alongNow);
        double y = a >= DIVE_FROM ? HEIGHT : a <= DIVE_TO ? HEIGHT_LOW : HEIGHT_LOW + (HEIGHT - HEIGHT_LOW) * (a - DIVE_TO) / (DIVE_FROM - DIVE_TO);
        Vec3 pos = new Vec3(flat.x, target.getY() + y, flat.z);
        forceUnder(pos);
        heli.setPos(pos);
        engine();
        heli.setYRot(heading);
        double toSmoke = -alongNow;
        // the nose on the smoke for the pods: the mod's aim vector reads the hull's pitch with nose-down negative (PITCH_SIGN), unlike vanilla
        float pitch = toSmoke <= ROCKET_FROM && toSmoke >= ROCKET_TO ? PITCH_SIGN * (float) Math.toDegrees(Math.atan2(y - 1.5, toSmoke)) : 0f;
        heli.setXRot(pitch);
        Sw.set(heli, "setZRot", 0f);
        heli.setDeltaMovement(Vec3.ZERO);
        heli.hurtMarked = true;
        if (t % 20 == 1) Strikes.sound(level, heli.blockPosition(), "ah_6_engine", 4f, 0.8f);
        double along = pos.subtract(Strikes.centre(target).add(0, HEIGHT, 0)).dot(dir);   // negative inbound, positive past
        double dist = -along;
        if (crew != null) crew.alertUntil = level.getGameTime() + 100;   // all round, always: a gunship looks everywhere
        if (gunner != null) gunner.alertUntil = level.getGameTime() + 100;
        if (crew != null) select(out ? gun : dist <= ROCKET_FROM && dist >= ROCKET_TO ? rockets : gun);
        // the pods are fixed and the mod's four-degree rule never lets an AI pilot fire them: the run pulls the trigger on the
        // airframe's own weapon system (vehicleShoot) while the nose is on the smoke - the rockets, sound and damage are the mod's
        if (crew != null && !out && dist <= ROCKET_FROM && dist >= ROCKET_TO && t % ROCKET_EVERY == 0) {
            if (Sw.invoke(heli, "vehicleShoot", new Class<?>[] {net.minecraft.world.entity.LivingEntity.class, String.class}, crew, "Rocket")) rocketsFired++;
        }
        if (dist <= ROCKET_FROM + 20 && dist >= ROCKET_TO - 20) {
            // the rockets that left the rails (the magazine, its reload and the ammunition are the mod's; the count is the proof):
            // each is caught in its first tick, within a tick's flight of the airframe
            EntityType<?> rocket = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("superbwarfare", "small_rocket"));
            for (Entity r : level.getEntities(heli, heli.getBoundingBox().inflate(24), e -> e.getType() == rocket && !e.getTags().contains("gscraft_counted"))) {
                r.addTag("gscraft_counted");
                rocketsOut++;
            }
        }
        if (along > RANGE - 5 || (out && along > GUN_RANGE + 40) || t > 20 * 60) {
            GscraftWar.LOG.info("[gscraft] strike: the helicopter is off station ({} rocket triggers, {} rockets out)", rocketsFired, rocketsOut);
            Strikes.tell("tune", "air_off", level.getServer());
            finish();
            return false;
        }
        return true;
    }

    private void finish() {
        if (crew != null && crew.isAlive()) crew.discard();   // before the hull: a crew left without one reports a wreck
        if (gunner != null && gunner.isAlive()) gunner.discard();
        if (dummy != null && dummy.isAlive()) dummy.discard();
        if (heli != null && heli.isAlive()) heli.discard();
        release();
        done = true;
    }

    void abort() {
        finish();
    }
}
