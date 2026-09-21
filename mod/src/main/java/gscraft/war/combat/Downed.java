package gscraft.war.combat;

import com.tacz.guns.api.item.IGun;
import gscraft.war.GscraftWar;
import gscraft.war.world.Upgrades;
import net.minecraft.network.protocol.game.ClientboundSetCarriedItemPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * A downed player holds no gun (owner, 2026-09-20, two reports with one cause: "on death, you can still use your weapons" and
 * "the down screen does not advance past even with left click held, something is overlapping"). PlayerRevive counts its
 * give-up while the ATTACK KEY is held ({@code options.keyAttack.isDown()}, read in its client tick); Superb Warfare, with a
 * gun in the main hand, takes the left mouse button for its own fire key and cancels the click before the key mapping ever
 * sees it. So a bleeding player with a gun in hand went on shooting, and the give-up never counted. Superb Warfare's
 * ShootEvent.Pre cannot be cancelled (read in its jar), so the hand is what changes: every tick a bleeding player's main
 * hand is moved off any gun - to an empty hotbar slot, else any hotbar slot without a gun, else the gun goes to the pack.
 * With no gun in hand Superb Warfare leaves the click alone, PlayerRevive sees it, and nothing fires. Scrolling back to the
 * gun lasts one tick. It needs PlayerRevive; without it nobody is ever "bleeding" and this does nothing.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Downed {
    private Downed() {}

    private static Class<?> swGun;
    private static boolean looked;

    /** a Superb Warfare gun (by its class, reached by name: no compile dependency) or a TACZ one */
    public static boolean gun(ItemStack stack) {
        if (stack.isEmpty()) return false;
        if (!looked) {
            looked = true;
            try {
                swGun = Class.forName("com.atsuishio.superbwarfare.item.gun.GunItem");
            } catch (ClassNotFoundException | LinkageError ex) {
                GscraftWar.LOG.warn("[gscraft] downed: Superb Warfare's GunItem is not reachable ({}): only TACZ guns are taken out of a downed hand", ex.toString());
            }
        }
        return swGun != null && swGun.isInstance(stack.getItem()) || IGun.getIGunOrNull(stack) != null;
    }

    /** the hotbar slot a downed hand goes to: an empty one, else one without a gun, else -1 */
    static int restingSlot(Inventory inv) {
        int other = -1;
        for (int i = 0; i < Inventory.getSelectionSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.isEmpty()) return i;
            if (other < 0 && !gun(s)) other = i;
        }
        return other;
    }

    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer p)) return;
        if (!gun(p.getMainHandItem()) || !Upgrades.bleeding(p)) return;
        Inventory inv = p.getInventory();
        int slot = restingSlot(inv);
        if (slot < 0) {
            // nine guns on the hotbar: the one in hand goes to the pack (or the ground), and its slot is the empty one
            ItemStack held = inv.getItem(inv.selected).copy();
            inv.setItem(inv.selected, ItemStack.EMPTY);
            int free = -1;
            for (int i = Inventory.getSelectionSize(); i < inv.items.size(); i++) {   // the pack only: `add` would refill the slot just emptied
                if (inv.getItem(i).isEmpty()) {
                    free = i;
                    break;
                }
            }
            if (free >= 0) inv.setItem(free, held);
            else p.drop(held, false);
            slot = inv.selected;
        }
        if (slot != inv.selected) {
            inv.selected = slot;
            p.connection.send(new ClientboundSetCarriedItemPacket(slot));
        }
    }
}
