package gscraft.war.combat;

import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.event.common.EntityHurtByGunEvent;
import com.tacz.guns.api.event.common.GunDamageSourcePart;
import com.tacz.guns.entity.EntityKineticBullet;
import gscraft.war.GscraftWar;
import gscraft.war.entity.GunUser;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Where the model meets the mods' damage. TACZ: its pre-hurt event, the amount replaced with the model's and,
 * for a modelled body, both damage sources set to the armour-piercing one so vanilla armour does not judge the
 * hit a second time. Superb Warfare bullets and every blast: the hurt event (before vanilla armour) computes the
 * model's number and the damage event (after it) applies it - the one way to overrule vanilla armour for a
 * source we do not own. Melee and everything else pass untouched.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class DamageEvents {
    private static final Map<UUID, Float> pending = new HashMap<>();
    private static final String SW_PROJECTILES = "com.atsuishio.superbwarfare.entity.projectile.";
    public static boolean enabled = true;

    private DamageEvents() {}

    @SubscribeEvent
    public static void gun(EntityHurtByGunEvent.Pre event) {
        if (!enabled || !event.getLogicalSide().isServer()) return;
        if (!(event.getHurtEntity() instanceof LivingEntity target) || !(target.level() instanceof ServerLevel)) return;
        Entity bullet = event.getBullet();
        if (bullet == null) return;
        Vec3 hit = Ballistics.impact(target, bullet);
        Zone zone = Ballistics.zone(target, hit, bullet.getDeltaMovement());
        int pen = ArmorData.penetration(ammoOf(event.getGunId()));
        Damage.Result r = Damage.bullet(target, zone, event.getBaseAmount(), pen);
        event.setHeadshot(false);
        event.setHeadshotMultiplier(1.0F);
        event.setBaseAmount(r.damage());
        if (r.modelled()) event.setDamageSource(GunDamageSourcePart.NON_ARMOR_PIERCING, event.getDamageSource(GunDamageSourcePart.ARMOR_PIERCING));
        Damage.record(target, r, "bullet");
        Damage.wound(target, zone);
        if (Damage.DEBUG > 0) GscraftWar.LOG.info("[gscraft] gun hit: {} -> {} by {} side {} zone {} base {} -> {}", event.getAttacker() == null ? "?" : event.getAttacker().getName().getString(), target.getName().getString(), event.getGunId(), event.getLogicalSide(), zone, event.getBaseAmount(), r.damage());
    }

    private static ResourceLocation ammoOf(ResourceLocation gunId) {
        if (gunId == null) return null;
        try {
            return TimelessAPI.getCommonGunIndex(gunId).map(i -> i.getGunData().getAmmoId()).orElse(null);
        } catch (RuntimeException ex) {
            return null;
        }
    }

    @SubscribeEvent
    public static void hurt(LivingHurtEvent event) {
        if (!enabled) return;
        LivingEntity target = event.getEntity();
        if (!(target.level() instanceof ServerLevel)) return;
        DamageSource source = event.getSource();
        Entity direct = source.getDirectEntity();
        if (direct instanceof EntityKineticBullet) return;   // judged in the TACZ event
        Damage.Result r = null;
        Zone zone = null;
        if (direct instanceof Projectile && direct.getClass().getName().startsWith(SW_PROJECTILES)) {
            zone = Ballistics.zone(target, Ballistics.impact(target, direct), direct.getDeltaMovement());
            int pen = source.getEntity() instanceof LivingEntity shooter ? ArmorData.gunPenetration(shooter.getMainHandItem()) : ArmorData.penetration(null);
            r = Damage.bullet(target, zone, event.getAmount(), pen);
            Damage.record(target, r, "sw bullet");
        } else if (source.is(DamageTypeTags.IS_EXPLOSION)) {
            r = Damage.blast(target, event.getAmount());
            Damage.record(target, r, "blast");
            if (target instanceof GunUser user) user.fighterState().suppress(1.0F);
        }
        if (r == null) return;
        if (r.modelled()) {
            pending.put(target.getUUID(), r.damage());   // applied after vanilla armour, in its place
        } else {
            event.setAmount(r.damage());                 // the zone counts; vanilla armour still does its part
        }
        if (zone != null) Damage.wound(target, zone);
    }

    @SubscribeEvent
    public static void damage(LivingDamageEvent event) {
        Float ours = pending.remove(event.getEntity().getUUID());
        if (ours != null) event.setAmount(ours);
    }
}
