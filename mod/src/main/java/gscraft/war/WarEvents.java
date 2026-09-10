package gscraft.war;

import com.tacz.guns.api.GunProperties;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.event.common.GunShootEvent;
import com.tacz.guns.resource.modifier.AttachmentCacheProperty;
import gscraft.war.entity.Hearing;
import gscraft.war.entity.RankDef;
import gscraft.war.entity.Ranks;
import gscraft.war.entity.Scavenger;
import gscraft.war.entity.Soldier;
import gscraft.war.faction.FactionDef;
import gscraft.war.faction.FactionMember;
import gscraft.war.faction.Factions;
import it.unimi.dsi.fastutil.Pair;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Game-bus hooks for the faction layer. */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class WarEvents {
    /** Mod-placed Dead carry this tag; In Control's hold lets it through and refuses everything else hostile. */
    public static final String PLACED_TAG = "gs_placed";

    /** how far an unsuppressed shot carries, and a suppressed one */
    private static final double LOUD = 64.0D;
    private static final double SILENCED = 12.0D;
    private static final Map<UUID, Long> LAST_SHOT_HEARD = new HashMap<>();
    private static long lastHearingLog;

    private WarEvents() {}

    @SubscribeEvent
    public static void reloadListeners(AddReloadListenerEvent event) {
        event.addListener(new Factions());
        event.addListener(new Ranks());
    }

    /**
     * Mobs the mod does not own get a faction target goal when their faction asks for one - how the Dead come to
     * hunt soldiers and Scavengers. The predicate reads the faction data live, so a /reload changes who they hunt.
     */
    @SubscribeEvent
    public static void injectTargeting(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide()) return;
        if (!(event.getEntity() instanceof Mob mob) || mob instanceof FactionMember) return;
        FactionDef def = Factions.def(Factions.factionOf(mob));
        if (def == null || !def.injectTargeting() || def.hostile().isEmpty()) return;
        mob.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(mob, LivingEntity.class, 10, true, false,
                e -> Factions.hostile(mob, e)));
    }

    /**
     * The Converted (review W7): a fighter the Dead kill rises as one of them, still wearing its kit. Zombies
     * render armour, so the war leaves a visible residue - dead RUAF in the town, dead NATO at the plant. The
     * weapon stays behind; the Dead never carry guns.
     */
    @SubscribeEvent
    public static void converted(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (victim.level().isClientSide) return;
        if (!(victim instanceof Soldier) && !(victim instanceof Scavenger)) return;
        Entity killer = event.getSource().getEntity();
        if (killer == null || !"dead".equals(Factions.factionOf(killer))) return;
        ServerLevel level = (ServerLevel) victim.level();
        Zombie risen = EntityType.ZOMBIE.create(level);
        if (risen == null) return;
        risen.moveTo(victim.getX(), victim.getY(), victim.getZ(), victim.getYRot(), 0.0F);
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (slot.getType() == EquipmentSlot.Type.ARMOR) {
                risen.setItemSlot(slot, victim.getItemBySlot(slot).copy());
            }
            risen.setDropChance(slot, 0.0F);
        }
        risen.addTag(PLACED_TAG);
        risen.addTag("gs_converted");
        level.addFreshEntity(risen);
    }

    /**
     * Gunfire is heard (review §4.5). An enemy of the shooter with nothing to fight walks toward the shot; an idle
     * ally of a shooting fighter joins its fight. A suppressed gun carries twelve blocks instead of sixty-four.
     * One alert a second per shooter, however fast the gun cycles.
     */
    @SubscribeEvent
    public static void gunfireHeard(GunShootEvent event) {
        if (!event.getLogicalSide().isServer()) return;
        LivingEntity shooter = event.getShooter();
        if (shooter == null || !(shooter.level() instanceof ServerLevel level)) return;
        long now = level.getGameTime();
        Long last = LAST_SHOT_HEARD.get(shooter.getUUID());
        if (last != null && now - last < 20) return;
        LAST_SHOT_HEARD.put(shooter.getUUID(), now);
        if (LAST_SHOT_HEARD.size() > 512) LAST_SHOT_HEARD.entrySet().removeIf(e -> now - e.getValue() > 200);

        double radius = hearingRadius(shooter);
        Vec3 at = shooter.position();
        LivingEntity shooterTarget = shooter instanceof Mob m ? m.getTarget() : null;
        int heard = 0;
        List<Mob> listeners = level.getEntitiesOfClass(Mob.class, shooter.getBoundingBox().inflate(radius),
                m -> m != shooter && m.getTarget() == null && Factions.factionOf(m) != null);
        for (Mob mob : listeners) {
            if (mob.distanceToSqr(shooter) > radius * radius) continue;
            boolean hostile = shooter instanceof Player p ? Factions.hostileToPlayer(mob, p) : Factions.hostile(mob, shooter);
            if (hostile) {
                if (mob instanceof Hearing h) h.hear(at);
                else mob.getNavigation().moveTo(at.x, at.y, at.z, 1.0D);
                heard++;
            } else if (shooterTarget != null && shooterTarget.isAlive() && Factions.allied(mob, shooter)) {
                mob.setTarget(shooterTarget);
                heard++;
            }
        }
        if (heard > 0 && now - lastHearingLog > 200) {
            lastHearingLog = now;
            GscraftWar.LOG.info("[gscraft] shot by {} heard by {} within {} blocks",
                    shooter.getType().getDescriptionId(), heard, (int) radius);
        }
    }

    private static double hearingRadius(LivingEntity shooter) {
        try {
            AttachmentCacheProperty cache = IGunOperator.fromLivingEntity(shooter).getCacheProperty();
            if (cache != null) {
                Pair<Integer, Boolean> silence = cache.getCache(GunProperties.SILENCE);
                if (silence != null && Boolean.TRUE.equals(silence.right())) return SILENCED;
            }
        } catch (RuntimeException ex) {
            // a gun whose attachment cache is not built yet is heard at full range
        }
        return LOUD;
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft")
                .requires(s -> s.hasPermission(2))
                .then(Commands.literal("factions").executes(ctx -> {
                    for (FactionDef d : Factions.all().values()) {
                        String line = d.id() + ": players " + d.players().name().toLowerCase()
                                + ", hostile " + d.hostile() + ", members " + d.members().size()
                                + (d.injectTargeting() ? ", injected" : "");
                        ctx.getSource().sendSuccess(() -> Component.literal(line), false);
                    }
                    return Factions.all().size();
                }))
                .then(Commands.literal("ranks").executes(ctx -> {
                    Ranks.all().forEach((faction, ranks) -> {
                        StringBuilder line = new StringBuilder(faction).append(':');
                        for (RankDef r : ranks) {
                            line.append(' ').append(r.name()).append(" (").append(r.role().name().toLowerCase())
                                    .append(", ").append(r.weight()).append(')');
                        }
                        String text = line.toString();
                        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
                    });
                    return Ranks.all().size();
                })));
    }
}
