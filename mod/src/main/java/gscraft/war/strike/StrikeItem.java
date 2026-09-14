package gscraft.war.strike;

import gscraft.war.item.SliceItems;
import gscraft.war.survivor.Say;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;
import java.util.Locale;

/** the strike grenade: thrown like a snowball, it lands as the smoke that marks the target and makes the call */
public class StrikeItem extends SliceItems.SliceItem {
    public final Strikes.Kind kind;

    public StrikeItem(SliceItems.Def def, Strikes.Kind kind) {
        super(def);
        this.kind = kind;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        if (Strikes.hot(sl.getServer())) {
            Say.queue(sp, "marshall", "tube_hot", true);
            sp.displayClientMessage(Component.literal("the tube is hot: " + Strikes.hotFor(sl.getServer())), true);
            return InteractionResultHolder.fail(stack);
        }
        StrikeMarker m = new StrikeMarker(level, player);
        m.setKind(kind);
        m.setItem(stack.copyWithCount(1));
        m.shootFromRotation(player, player.getXRot(), player.getYRot(), 0f, 1.3f, 1f);
        level.addFreshEntity(m);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SNOWBALL_THROW, SoundSource.PLAYERS, 0.6f, 0.6f);
        if (!player.getAbilities().instabuild) stack.shrink(1);
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
        super.appendHoverText(stack, level, lines, flag);
        lines.add(Component.translatable("gscraft.strike.tip." + kind.name().toLowerCase(Locale.ROOT)).withStyle(ChatFormatting.YELLOW));
        lines.add(Component.translatable("gscraft.strike.tip.cooldown").withStyle(ChatFormatting.GRAY));
    }
}
