package gscraft.war.station;

import gscraft.war.GscraftWar;
import gscraft.war.item.SliceItems;
import gscraft.war.world.SiteData;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.items.ItemStackHandler;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * The work station (interface §4.3, crafting §3-§4): slot 0 the card, slot 1 the tool, slot 2 the output (take
 * only), slots 3-11 the inputs. Every second it compares the card's orders (and the quick recipes) with the inputs;
 * the moment one matches it consumes the parts, ticks the countdown and delivers the result to the output with a
 * chime. It stays lit until the output is taken. The first player to place or open it owns it; anyone else sees
 * the screen and is refused. What it would say is {@link #readout(Player)}: the action bar while looked at.
 */
public class StationBlockEntity extends BlockEntity implements MenuProvider {
    public static final int CARD = 0, TOOL = 1, OUT = 2, IN0 = 3, SLOTS = 12;

    public final ItemStackHandler items = new ItemStackHandler(SLOTS) {
        @Override
        protected void onContentsChanged(int slot) {
            setChanged();
        }
    };
    public UUID owner;
    public String ownerName = "";
    private String orderId;
    private int remaining;
    private String why = "";

    public StationBlockEntity(BlockPos pos, BlockState state) {
        super(ModStation.STATION_BE.get(), pos, state);
    }

    // ---- owner

    public void bind(Player p) {
        bind(p.getUUID(), p.getGameProfile().getName());
    }

    public void bind(UUID id, String name) {
        owner = id;
        ownerName = name == null ? "" : name;
        if (level instanceof ServerLevel sl) SiteData.get(sl).bindStation(id, worldPosition);
        setChanged();
    }

    public boolean owns(Player p) {
        return owner == null || owner.equals(p.getUUID());
    }

    public String title() {
        return owner == null ? "STATION" : ownerName.toUpperCase(Locale.ROOT) + "'S STATION";
    }

    // ---- the order

    public String orderId() {
        return orderId;
    }

    public int remaining() {
        return remaining;
    }

    public void serverTick() {
        if (level == null) return;
        if (orderId != null) {
            if (remaining > 0) remaining--;
            if (remaining <= 0) deliver();
            if (level.getGameTime() % 20 == 0) lit();
            return;
        }
        if (level.getGameTime() % 20 != 0) return;
        ItemStack card = items.getStackInSlot(CARD);
        List<Orders.Order> byCard = card.getItem() instanceof SliceItems.SliceItem si && si.def.role().equals("card") ? Orders.forCard(si.def.id()) : List.of();
        List<Orders.Order> all = new ArrayList<>(byCard);
        all.addAll(Orders.quick());
        Orders.Order best = null;
        List<String> bestMissing = null;
        Orders.Order ready = null;   // of the orders that can start, the one that uses the most of what is loaded (sandbags over a bandage)
        for (Orders.Order o : all) {
            List<String> missing = missing(o);
            if (missing.isEmpty()) {
                if (ready == null || o.in().values().stream().mapToInt(Integer::intValue).sum() > ready.in().values().stream().mapToInt(Integer::intValue).sum()) ready = o;
                continue;
            }
            boolean loaded = missing.size() < o.in().size() + (o.tool() == null ? 0 : 1) || missing.stream().anyMatch(m -> m.contains(" more "));
            // the readout names the card's order (or the quick one the inputs are closest to); nothing loaded and no card is "no card"
            if (best == null || (byCard.contains(o) && !byCard.contains(best)) || (byCard.contains(o) == byCard.contains(best) && loaded && missing.size() < bestMissing.size())) {
                best = o;
                bestMissing = missing;
            }
        }
        if (ready != null) {
            start(ready);
            return;
        }
        if (best == null) why = "no card";
        else if (byCard.isEmpty() && !anyInput()) why = "no card";
        else why = best.name() + " — needs: " + String.join(", ", bestMissing);
        lit();
    }

    private boolean anyInput() {
        for (int i = IN0; i < SLOTS; i++) if (!items.getStackInSlot(i).isEmpty()) return true;
        return false;
    }

    /** what the order still lacks, in the readout's words; empty when it can start */
    public List<String> missing(Orders.Order o) {
        List<String> out = new ArrayList<>();
        for (var e : o.in().entrySet()) {
            int have = 0;
            for (int i = IN0; i < SLOTS; i++) {
                ItemStack s = items.getStackInSlot(i);
                if (Orders.matches(s, e.getKey())) have += s.getCount();
            }
            if (have < e.getValue()) out.add(have > 0 ? (e.getValue() - have) + " more " + Orders.needName(e.getKey()) : e.getValue() + " " + Orders.needName(e.getKey()));
        }
        if (o.tool() != null && !Orders.matches(items.getStackInSlot(TOOL), o.tool())) out.add(Orders.needName(o.tool()));
        return out;
    }

    private void start(Orders.Order o) {
        ItemStack out = items.getStackInSlot(OUT);
        ItemStack result = o.result();
        if (result.isEmpty()) {
            why = o.name() + " — no such item";
            return;
        }
        if (!out.isEmpty() && !(ItemStack.isSameItemSameTags(out, result) && out.getCount() + result.getCount() <= out.getMaxStackSize())) {
            why = o.name() + " — output full";
            return;
        }
        for (var e : o.in().entrySet()) {
            int left = e.getValue();
            for (int i = IN0; i < SLOTS && left > 0; i++) {
                ItemStack s = items.getStackInSlot(i);
                if (!Orders.matches(s, e.getKey())) continue;
                int take = Math.min(left, s.getCount());
                ItemStack remainder = s.getCraftingRemainingItem();
                s.shrink(take);
                left -= take;
                if (s.isEmpty() && !remainder.isEmpty()) items.setStackInSlot(i, remainder);
                else items.setStackInSlot(i, s);
            }
        }
        if (o.tool() != null) {
            ItemStack tool = items.getStackInSlot(TOOL);
            if (tool.isDamageableItem()) {
                tool.setDamageValue(tool.getDamageValue() + 1);
                if (tool.getDamageValue() >= tool.getMaxDamage()) tool.shrink(1);
                items.setStackInSlot(TOOL, tool);
            }
        }
        orderId = o.id();
        remaining = o.ticks();
        why = "";
        setChanged();
        lit();
    }

    private void deliver() {
        Orders.Order o = Orders.byId(orderId);
        if (o == null) {
            GscraftWar.LOG.warn("[gscraft] station at {} had an unknown order {}; dropped", worldPosition, orderId);
            orderId = null;
            setChanged();
            return;
        }
        ItemStack result = o.result();
        ItemStack out = items.getStackInSlot(OUT);
        if (out.isEmpty()) items.setStackInSlot(OUT, result);
        else if (ItemStack.isSameItemSameTags(out, result) && out.getCount() + result.getCount() <= out.getMaxStackSize()) {
            out.grow(result.getCount());
            items.setStackInSlot(OUT, out);
        } else {
            remaining = 0;   // output full: the order waits, the readout says so
            return;
        }
        orderId = null;
        remaining = 0;
        if (level != null) level.playSound(null, worldPosition, SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.BLOCKS, 0.8f, 1.2f);
        setChanged();
        lit();
    }

    private void lit() {
        boolean lit = orderId != null || !items.getStackInSlot(OUT).isEmpty();
        BlockState s = getBlockState();
        if (level != null && s.hasProperty(StationBlock.LIT) && s.getValue(StationBlock.LIT) != lit) level.setBlock(worldPosition, s.setValue(StationBlock.LIT, lit), 3);
    }

    /** the action bar while the player looks at the block (interface §3.3); null viewer is the console */
    public String readout(Player viewer) {
        if (owner != null && viewer != null && !owner.equals(viewer.getUUID())) return title() + " — this one is " + ownerName + "'s";
        if (orderId != null) {
            Orders.Order o = Orders.byId(orderId);
            String n = (o == null ? orderId : o.name()).toUpperCase(Locale.ROOT);
            return remaining > 0 ? n + " — " + Orders.mmss(remaining) : n + " — output full";
        }
        ItemStack out = items.getStackInSlot(OUT);
        if (!out.isEmpty()) return out.getHoverName().getString().toUpperCase(Locale.ROOT) + " — done";
        return why.isEmpty() || why.equals("no card") ? title() + " — " + Component.translatable("gscraft.station.no_card").getString() : why;
    }

    // ---- nbt, menu

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.put("Items", items.serializeNBT());
        if (owner != null) {
            tag.putUUID("Owner", owner);
            tag.putString("OwnerName", ownerName);
        }
        if (orderId != null) {
            tag.putString("Order", orderId);
            tag.putInt("Remaining", remaining);
        }
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        if (tag.contains("Items")) items.deserializeNBT(tag.getCompound("Items"));
        owner = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
        ownerName = tag.getString("OwnerName");
        orderId = tag.contains("Order") ? tag.getString("Order") : null;
        remaining = tag.getInt("Remaining");
    }

    @Override
    public Component getDisplayName() {
        return Component.literal(title());
    }

    @Override
    public AbstractContainerMenu createMenu(int id, Inventory inv, Player player) {
        return new StationMenu(id, inv, this);
    }
}
