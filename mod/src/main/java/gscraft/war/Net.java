package gscraft.war;

import gscraft.war.client.WoundsHud;   // resolved on the client only, see handle
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.function.Supplier;

/** The mod's one channel: the player's body readout for the HUD, server to client, once a second. */
public final class Net {
    private static final String VERSION = "1";
    // any client version, and none at all, is accepted: the HUD is a convenience, and a client on an older jar or the
    // vanilla launcher must still be able to join (the first cut rejected the owner's own main instance)
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(new ResourceLocation(GscraftWar.MODID, "main"),
            () -> VERSION, v -> true, v -> true);

    private Net() {}

    public static void register() {
        CHANNEL.registerMessage(0, HudPacket.class, HudPacket::write, HudPacket::read, HudPacket::handle);
    }

    public static void sendHud(ServerPlayer player, HudPacket packet) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }

    /** what the HUD shows: the two pieces with class, plate and its full points, and the three wounds in ticks */
    public record HudPacket(String headName, int headClass, int headPlate, int headMax,
                            String chestName, int chestClass, int chestPlate, int chestMax,
                            int legTicks, int armTicks, int bleedTicks) {
        public void write(FriendlyByteBuf buf) {
            buf.writeUtf(headName, 64);
            buf.writeVarInt(headClass);
            buf.writeVarInt(headPlate);
            buf.writeVarInt(headMax);
            buf.writeUtf(chestName, 64);
            buf.writeVarInt(chestClass);
            buf.writeVarInt(chestPlate);
            buf.writeVarInt(chestMax);
            buf.writeVarInt(legTicks);
            buf.writeVarInt(armTicks);
            buf.writeVarInt(bleedTicks);
        }

        public static HudPacket read(FriendlyByteBuf buf) {
            return new HudPacket(buf.readUtf(64), buf.readVarInt(), buf.readVarInt(), buf.readVarInt(),
                    buf.readUtf(64), buf.readVarInt(), buf.readVarInt(), buf.readVarInt(),
                    buf.readVarInt(), buf.readVarInt(), buf.readVarInt());
        }

        public void handle(Supplier<NetworkEvent.Context> ctx) {
            if (ctx.get().getDirection() == NetworkDirection.PLAY_TO_CLIENT) {
                // the HUD class is client-only; a dedicated server must never resolve it
                ctx.get().enqueueWork(() -> net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT, () -> () -> WoundsHud.accept(this)));
            }
            ctx.get().setPacketHandled(true);
        }
    }
}
