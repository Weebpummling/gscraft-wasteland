package gscraft.war.armour;

import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.event.common.EntityHurtByGunEvent;
import com.tacz.guns.entity.EntityKineticBullet;
import com.tacz.guns.resource.pojo.data.gun.ExplosionData;
import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Explosion;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * TACZ explosives against armour (armour design §1; owner 2026-09-12: a BMP dies to two rockets at most). A TACZ
 * explosive round is a bullet whose blast is a vanilla explosion, and a vanilla explosion damages by the distance
 * from the blast to the entity's feet: a rocket into a hull's side, three blocks from its centre, did a fifth of
 * its damage. So a direct hit on a vehicle by an explosive round does a flat amount by the round's class - rocket
 * (a blast of 100 or more), grenade (a blast radius of four or more), other (HE rifle rounds) - and by the
 * vehicle's weight (light under the heavy-health threshold, heavy over); its blast then adds nothing, and a blast
 * that only lands beside a vehicle does the splash share of the flat amount. The flat damage goes in as a player
 * explosion by the shooter, so the vehicle's own list (which leaves that type alone) and its last-attacker record
 * see it. Superb Warfare's rockets, missiles and shells hit by their own damage types and are set by the vehicle's
 * list in tools/armour_override.py.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class ArmourDamage {
    public static double ROCKET_LIGHT = 160.0D;
    public static double ROCKET_HEAVY = 130.0D;
    public static double GRENADE_LIGHT = 60.0D;
    public static double GRENADE_HEAVY = 20.0D;
    public static double OTHER_LIGHT = 30.0D;
    public static double OTHER_HEAVY = 8.0D;
    public static double SPLASH = 0.5D;
    public static double HEAVY_HEALTH = 400.0D;
    /** vehicle id -> the bullet that hit it directly (its blast then adds nothing) */
    private static final Map<Integer, Integer> directHits = new HashMap<>();

    private ArmourDamage() {}

    @SubscribeEvent
    public static void hit(EntityHurtByGunEvent.Pre event) {
        if (!event.getLogicalSide().isServer()) return;
        Entity v = event.getHurtEntity();
        if (v == null || !Vehicles.isVehicle(v) || !(event.getBullet() instanceof EntityKineticBullet b)) return;
        ExplosionData x = explosion(b.getGunId());
        if (x == null || !x.isExplode()) return;   // a plain round: the vehicle's list makes it nothing
        boolean heavy = Vehicles.heavy(v);
        float dmg = flat(x, heavy);
        directHits.put(v.getId(), b.getId());
        v.hurt(v.level().damageSources().explosion(b, event.getAttacker()), dmg);
        GscraftWar.LOG.info("[gscraft] armour hit: {} by {} ({}, {}) for {}", v.getName().getString(), event.getAttacker() == null ? "?" : event.getAttacker().getName().getString(), b.getGunId(), kind(x), Math.round(dmg));
    }

    @SubscribeEvent
    public static void detonate(ExplosionEvent.Detonate event) {
        Explosion x = event.getExplosion();
        if (!(x.getExploder() instanceof EntityKineticBullet b)) return;
        ExplosionData data = explosion(b.getGunId());
        Iterator<Entity> it = event.getAffectedEntities().iterator();
        while (it.hasNext()) {
            Entity v = it.next();
            if (!Vehicles.isVehicle(v)) continue;
            it.remove();   // the mod's distance-based damage is not for armour
            Integer direct = directHits.remove(v.getId());
            if (direct != null && direct == b.getId()) continue;
            if (data == null || !data.isExplode()) continue;
            float dmg = (float) (flat(data, Vehicles.heavy(v)) * SPLASH);
            if (dmg > 0.0F) v.hurt(x.getDamageSource(), dmg);
        }
    }

    private static ExplosionData explosion(ResourceLocation gunId) {
        if (gunId == null) return null;
        try {
            return TimelessAPI.getCommonGunIndex(gunId).map(i -> i.getGunData().getBulletData().getExplosionData()).orElse(null);
        } catch (RuntimeException ex) {
            return null;
        }
    }

    private static String kind(ExplosionData x) {
        return x.getDamage() >= 100.0F ? "rocket" : x.getRadius() >= 4.0F ? "grenade" : "other";
    }

    private static float flat(ExplosionData x, boolean heavy) {
        return (float) switch (kind(x)) {
            case "rocket" -> heavy ? ROCKET_HEAVY : ROCKET_LIGHT;
            case "grenade" -> heavy ? GRENADE_HEAVY : GRENADE_LIGHT;
            default -> heavy ? OTHER_HEAVY : OTHER_LIGHT;
        };
    }
}
