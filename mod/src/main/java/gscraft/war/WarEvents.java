package gscraft.war;

import gscraft.war.entity.Scavenger;
import gscraft.war.entity.Soldier;
import gscraft.war.faction.FactionDef;
import gscraft.war.faction.FactionMember;
import gscraft.war.faction.Factions;
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
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Game-bus hooks for the faction layer. */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class WarEvents {
    /** Mod-placed Dead carry this tag; In Control's hold lets it through and refuses everything else hostile. */
    public static final String PLACED_TAG = "gs_placed";

    private WarEvents() {}

    @SubscribeEvent
    public static void reloadListeners(AddReloadListenerEvent event) {
        event.addListener(new Factions());
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
                })));
    }
}
