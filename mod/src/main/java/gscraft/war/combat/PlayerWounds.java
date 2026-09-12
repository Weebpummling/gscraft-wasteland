package gscraft.war.combat;

import gscraft.war.GscraftWar;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * A player's wounds, kept in the player's persistent data until a bandage: a leg wound (slowness, no sprint),
 * an arm wound (weakness - the pack's guns have no sway hook), bleeding (a point of damage every two seconds and
 * hunger with it). Death clears them.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class PlayerWounds {
    private static final String TAG = "GscraftWounds";
    /** a player's wounds outlast a fighter's: these are how long they run untreated */
    public static int PLAYER_LEG_TICKS = 2400;
    public static int PLAYER_ARM_TICKS = 2400;
    public static int PLAYER_BLEED_TICKS = 600;

    private PlayerWounds() {}

    private static CompoundTag tag(Player player) {
        CompoundTag root = player.getPersistentData();
        if (!root.contains(TAG)) root.put(TAG, new CompoundTag());
        return root.getCompound(TAG);
    }

    public static void wound(Player player, Zone zone) {
        long now = player.level().getGameTime();
        CompoundTag t = tag(player);
        switch (zone) {
            case LEGS -> t.putLong("Leg", now + PLAYER_LEG_TICKS);
            case ARMS -> t.putLong("Arm", now + PLAYER_ARM_TICKS);
            case STOMACH -> t.putInt("Bleed", Math.max(t.getInt("Bleed"), PLAYER_BLEED_TICKS));
            default -> { }
        }
    }

    public static void clear(Player player) {
        player.getPersistentData().remove(TAG);
    }

    public static String describe(Player player) {
        CompoundTag t = tag(player);
        long now = player.level().getGameTime();
        StringBuilder sb = new StringBuilder();
        if (t.getLong("Leg") > now) sb.append("leg ").append((t.getLong("Leg") - now) / 20).append("s ");
        if (t.getLong("Arm") > now) sb.append("arm ").append((t.getLong("Arm") - now) / 20).append("s ");
        if (t.getInt("Bleed") > 0) sb.append("bleeding ").append(t.getInt("Bleed") / 20).append("s ");
        return sb.length() == 0 ? "none" : sb.toString().trim();
    }

    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide || !event.player.isAlive()) return;
        Player player = event.player;
        CompoundTag root = player.getPersistentData();
        long now = player.level().getGameTime();
        if (now % 20 == 5 && player instanceof net.minecraft.server.level.ServerPlayer sp) gscraft.war.Net.sendHud(sp, hud(player));
        if (!root.contains(TAG)) return;
        CompoundTag t = root.getCompound(TAG);
        boolean any = false;
        if (t.getLong("Leg") > now) {
            any = true;
            player.setSprinting(false);
            if (now % 20 == 0) player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 45, 2, true, false, true));
        }
        if (t.getLong("Arm") > now) {
            any = true;
            if (now % 20 == 0) player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 45, 0, true, false, true));
        }
        int bleed = t.getInt("Bleed");
        if (bleed > 0) {
            any = true;
            t.putInt("Bleed", bleed - 1);
            if (bleed % Damage.BLEED_EVERY == 0) {
                player.hurt(player.damageSources().generic(), Damage.BLEED_DAMAGE);
                player.causeFoodExhaustion(1.0F);
            }
        }
        if (!any) root.remove(TAG);
    }

    /** the packet's worth: each piece's name, class, plate and full points (a known piece is written on first sight) */
    public static gscraft.war.Net.HudPacket hud(Player player) {
        CompoundTag t = tag(player);
        long now = player.level().getGameTime();
        Object[] head = piece(player, net.minecraft.world.entity.EquipmentSlot.HEAD);
        Object[] chest = piece(player, net.minecraft.world.entity.EquipmentSlot.CHEST);
        return new gscraft.war.Net.HudPacket((String) head[0], (Integer) head[1], (Integer) head[2], (Integer) head[3],
                (String) chest[0], (Integer) chest[1], (Integer) chest[2], (Integer) chest[3],
                (int) Math.max(0L, t.getLong("Leg") - now), (int) Math.max(0L, t.getLong("Arm") - now), Math.max(0, t.getInt("Bleed")));
    }

    private static Object[] piece(Player player, net.minecraft.world.entity.EquipmentSlot slot) {
        net.minecraft.world.item.ItemStack stack = player.getItemBySlot(slot);
        if (stack.isEmpty()) return new Object[] {"", -1, 0, 0};
        String name = stack.getHoverName().getString();
        ArmorData.Piece data = ArmorData.of(stack);
        if (data == null) return new Object[] {name, -1, 0, 0};
        return new Object[] {name, data.armorClass(), Damage.plate(stack, slot, data), data.points()};
    }

    @SubscribeEvent
    public static void death(net.minecraftforge.event.entity.living.LivingDeathEvent event) {
        if (event.getEntity() instanceof Player player) clear(player);
    }
}
