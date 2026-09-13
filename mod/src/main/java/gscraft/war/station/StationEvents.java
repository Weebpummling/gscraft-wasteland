package gscraft.war.station;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import gscraft.war.GscraftWar;
import gscraft.war.world.SiteData;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.ResourceLocationArgument;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Map;
import java.util.UUID;

/**
 * The station's readout on the action bar while a player looks at one within five blocks (interface §3.3), and
 * {@code /gscraft station} for the console: show, bind, load, take, clear, list - what a headless test drives.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class StationEvents {
    private StationEvents() {}

    @SubscribeEvent
    public static void look(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer p) || p.tickCount % 10 != 0) return;
        net.minecraft.world.phys.Vec3 eye = p.getEyePosition();
        net.minecraft.world.phys.Vec3 look = p.getViewVector(1f);
        for (net.minecraft.world.entity.Entity e : p.level().getEntities(p, p.getBoundingBox().inflate(6), en -> en.getTags().contains("gscraft_npc"))) {
            net.minecraft.world.phys.Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
            double d = to.length();
            if (d <= 6 && to.normalize().dot(look) > 0.985) {
                gscraft.war.survivor.Survivors.Def def = gscraft.war.survivor.Survivors.byTag(e);
                String who = def != null ? def.name().toUpperCase(java.util.Locale.ROOT) : e.getName().getString().toUpperCase(java.util.Locale.ROOT);
                p.displayClientMessage(Component.literal(who + " — ").append(Component.translatable("gscraft.survivor.talk")), true);
                return;
            }
        }
        HitResult hit = p.pick(5.0, 0f, false);
        if (hit.getType() != HitResult.Type.BLOCK) return;
        BlockPos at = ((BlockHitResult) hit).getBlockPos();
        if (p.level().getBlockEntity(at) instanceof StationBlockEntity st) {
            p.displayClientMessage(Component.literal(st.readout(p)), true);
            return;
        }
        String column = gscraft.war.world.Board.column(at);
        if (column != null && p.level() instanceof ServerLevel sl) p.displayClientMessage(Component.literal(gscraft.war.world.Board.readout(sl, column)), true);
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("station")
                        .then(Commands.literal("show").then(Commands.argument("pos", BlockPosArgument.blockPos())
                                .executes(ctx -> show(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"), null))
                                .then(Commands.argument("viewer", StringArgumentType.word())
                                        .executes(ctx -> show(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"), StringArgumentType.getString(ctx, "viewer"))))))
                        .then(Commands.literal("bind").then(Commands.argument("pos", BlockPosArgument.blockPos()).then(Commands.argument("name", StringArgumentType.word())
                                .executes(ctx -> {
                                    StationBlockEntity st = at(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"));
                                    if (st == null) return 0;
                                    String name = StringArgumentType.getString(ctx, "name");
                                    ServerPlayer online = ctx.getSource().getServer().getPlayerList().getPlayerByName(name);
                                    st.bind(online != null ? online.getUUID() : UUID.nameUUIDFromBytes(("OfflinePlayer:" + name).getBytes(java.nio.charset.StandardCharsets.UTF_8)), name);
                                    ctx.getSource().sendSuccess(() -> Component.literal("station at " + st.getBlockPos().toShortString() + " is " + name + "'s"), false);
                                    return 1;
                                }))))
                        .then(Commands.literal("load").then(Commands.argument("pos", BlockPosArgument.blockPos()).then(Commands.argument("slot", IntegerArgumentType.integer(0, StationBlockEntity.SLOTS - 1))
                                .then(Commands.argument("item", ResourceLocationArgument.id())
                                        .executes(ctx -> load(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"), IntegerArgumentType.getInteger(ctx, "slot"), ResourceLocationArgument.getId(ctx, "item").toString(), 1))
                                        .then(Commands.argument("count", IntegerArgumentType.integer(1, 64))
                                                .executes(ctx -> load(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"), IntegerArgumentType.getInteger(ctx, "slot"), ResourceLocationArgument.getId(ctx, "item").toString(), IntegerArgumentType.getInteger(ctx, "count"))))))))
                        .then(Commands.literal("take").then(Commands.argument("pos", BlockPosArgument.blockPos()).executes(ctx -> {
                            StationBlockEntity st = at(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"));
                            if (st == null) return 0;
                            ItemStack out = st.items.getStackInSlot(StationBlockEntity.OUT);
                            String line = out.isEmpty() ? "nothing in the output" : "took " + out.getCount() + " " + ForgeRegistries.ITEMS.getKey(out.getItem());
                            st.items.setStackInSlot(StationBlockEntity.OUT, ItemStack.EMPTY);
                            ctx.getSource().sendSuccess(() -> Component.literal(line), false);
                            return out.getCount();
                        })))
                        .then(Commands.literal("clear").then(Commands.argument("pos", BlockPosArgument.blockPos()).executes(ctx -> {
                            StationBlockEntity st = at(ctx.getSource(), BlockPosArgument.getLoadedBlockPos(ctx, "pos"));
                            if (st == null) return 0;
                            for (int i = 0; i < StationBlockEntity.SLOTS; i++) st.items.setStackInSlot(i, ItemStack.EMPTY);
                            ctx.getSource().sendSuccess(() -> Component.literal("station cleared"), false);
                            return 1;
                        })))
                        .then(Commands.literal("list").executes(ctx -> {
                            Map<UUID, BlockPos> all = SiteData.get(ctx.getSource().getLevel()).stations();
                            all.forEach((id, pos) -> ctx.getSource().sendSuccess(() -> Component.literal(id + " -> " + pos.toShortString()), false));
                            ctx.getSource().sendSuccess(() -> Component.literal(all.size() + " bound stations; " + Orders.ALL.size() + " orders, " + Orders.cards().size() + " cards"), false);
                            return all.size();
                        }))));
    }

    private static StationBlockEntity at(CommandSourceStack src, BlockPos pos) {
        ServerLevel level = src.getLevel();
        if (level.getBlockEntity(pos) instanceof StationBlockEntity st) return st;
        src.sendFailure(Component.literal("no station at " + pos.toShortString()));
        return null;
    }

    private static int show(CommandSourceStack src, BlockPos pos, String viewer) {
        StationBlockEntity st = at(src, pos);
        if (st == null) return 0;
        Player p = viewer == null ? null : src.getServer().getPlayerList().getPlayerByName(viewer);
        String line;
        if (viewer != null && p == null) {
            // a name nobody online has: the readout a stranger would see
            UUID id = UUID.nameUUIDFromBytes(("OfflinePlayer:" + viewer).getBytes(java.nio.charset.StandardCharsets.UTF_8));
            line = st.owner != null && !st.owner.equals(id) ? st.title() + " — this one is " + st.ownerName + "'s" : st.readout(null);
        } else line = st.readout(p);
        StringBuilder slots = new StringBuilder();
        for (int i = 0; i < StationBlockEntity.SLOTS; i++) {
            ItemStack s = st.items.getStackInSlot(i);
            if (!s.isEmpty()) slots.append(' ').append(i).append('=').append(ForgeRegistries.ITEMS.getKey(s.getItem())).append('x').append(s.getCount());
        }
        String out = line + " | order " + st.orderId() + " remaining " + st.remaining() + " | lit " + st.getBlockState().getValue(StationBlock.LIT) + " |" + slots;
        src.sendSuccess(() -> Component.literal(out), false);
        return 1;
    }

    private static int load(CommandSourceStack src, BlockPos pos, int slot, String item, int count) {
        StationBlockEntity st = at(src, pos);
        if (st == null) return 0;
        Item it = ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.tryParse(item));
        if (it == null || it == net.minecraft.world.item.Items.AIR) {
            src.sendFailure(Component.literal("no such item " + item));
            return 0;
        }
        st.items.setStackInSlot(slot, new ItemStack(it, count));
        src.sendSuccess(() -> Component.literal("slot " + slot + " = " + item + " x" + count), false);
        return count;
    }
}
