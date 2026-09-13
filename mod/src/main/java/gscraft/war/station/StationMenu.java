package gscraft.war.station;

import gscraft.war.item.SliceItems;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.ItemStackHandler;
import net.minecraftforge.items.SlotItemHandler;

/**
 * The station's screen (interface §4.3): a plain container, row 1 the card, the tool and the output, rows 2-4 the
 * nine inputs. A player who is not the owner sees it and is refused: no slot takes or gives them anything.
 */
public class StationMenu extends AbstractContainerMenu {
    public static final int ROWS = 4;
    public final StationBlockEntity station;
    private final Player player;
    private final ContainerLevelAccess access;

    public StationMenu(int id, Inventory inv, FriendlyByteBuf buf) {
        this(id, inv, at(inv, buf.readBlockPos()));
    }

    private static StationBlockEntity at(Inventory inv, BlockPos pos) {
        BlockEntity be = inv.player.level().getBlockEntity(pos);
        return be instanceof StationBlockEntity st ? st : null;
    }

    public StationMenu(int id, Inventory inv, StationBlockEntity station) {
        super(ModStation.STATION_MENU.get(), id);
        this.station = station;
        this.player = inv.player;
        this.access = station == null ? ContainerLevelAccess.NULL : ContainerLevelAccess.create(station.getLevel(), station.getBlockPos());
        IItemHandler h = station == null ? new ItemStackHandler(StationBlockEntity.SLOTS) : station.items;
        addSlot(new StationSlot(h, StationBlockEntity.CARD, 8, 18) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return owns() && stack.getItem() instanceof SliceItems.SliceItem si && si.def.role().equals("card");
            }
        });
        addSlot(new StationSlot(h, StationBlockEntity.TOOL, 26, 18));
        addSlot(new StationSlot(h, StationBlockEntity.OUT, 44, 18) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return false;
            }
        });
        for (int r = 0; r < 3; r++) for (int c = 0; c < 9; c++) addSlot(new StationSlot(h, StationBlockEntity.IN0 + r * 9 + c, 8 + c * 18, 36 + r * 18));
        int base = (ROWS - 4) * 18;
        for (int r = 0; r < 3; r++) for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c + r * 9 + 9, 8 + c * 18, 103 + base + r * 18));
        for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, 8 + c * 18, 161 + base));
    }

    public boolean owns() {
        return station == null || station.owns(player);
    }

    private class StationSlot extends SlotItemHandler {
        StationSlot(IItemHandler h, int index, int x, int y) {
            super(h, index, x, y);
        }

        @Override
        public boolean mayPlace(ItemStack stack) {
            return owns() && super.mayPlace(stack);
        }

        @Override
        public boolean mayPickup(Player p) {
            return owns() && super.mayPickup(p);
        }
    }

    @Override
    public boolean stillValid(Player p) {
        return station == null || stillValid(access, p, ModStation.STATION.get());
    }

    @Override
    public ItemStack quickMoveStack(Player p, int index) {
        if (!owns()) return ItemStack.EMPTY;
        Slot slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;
        ItemStack stack = slot.getItem();
        ItemStack copy = stack.copy();
        int inv = StationBlockEntity.SLOTS;
        if (index < inv) {
            if (!moveItemStackTo(stack, inv, inv + 36, true)) return ItemStack.EMPTY;
        } else {
            boolean card = stack.getItem() instanceof SliceItems.SliceItem si && si.def.role().equals("card");
            if (card ? !moveItemStackTo(stack, StationBlockEntity.CARD, StationBlockEntity.CARD + 1, false)
                    : !moveItemStackTo(stack, StationBlockEntity.IN0, inv, false)) return ItemStack.EMPTY;
        }
        if (stack.isEmpty()) slot.set(ItemStack.EMPTY);
        else slot.setChanged();
        return copy;
    }
}
