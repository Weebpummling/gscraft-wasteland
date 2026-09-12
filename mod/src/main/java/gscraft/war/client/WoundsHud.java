package gscraft.war.client;

import gscraft.war.GscraftWar;
import gscraft.war.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * The body readout, bottom left (owner, 2026-09-11): the helmet and the vest with their class and plate, and the
 * three wounds. Fed by {@link Net.HudPacket} once a second. Superb Warfare's own plate bar is hidden: it only
 * knows its two vests and its own plate scale, and two bars that disagree are worse than one.
 */
public final class WoundsHud {
    private static final ResourceLocation SW_PLATE_OVERLAY = new ResourceLocation("superbwarfare", "armor_plate");
    private static volatile Net.HudPacket latest;
    private static long receivedAt;

    private WoundsHud() {}

    public static void accept(Net.HudPacket packet) {
        latest = packet;
        receivedAt = System.currentTimeMillis();
    }

    /** registered on the mod bus, client only */
    @Mod.EventBusSubscriber(modid = GscraftWar.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class Register {
        private Register() {}

        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent event) {
            event.registerAboveAll("body", (gui, graphics, partialTick, width, height) -> draw(graphics, width, height));
        }
    }

    /** on the forge bus, client only: the SW bar goes */
    @Mod.EventBusSubscriber(modid = GscraftWar.MODID, value = Dist.CLIENT)
    public static final class Hide {
        private Hide() {}

        @SubscribeEvent
        public static void pre(RenderGuiOverlayEvent.Pre event) {
            if (SW_PLATE_OVERLAY.equals(event.getOverlay().id())) event.setCanceled(true);
        }
    }

    private static final int OK = 0xFFB9D89A;
    private static final int HURT = 0xFFE86A5A;
    private static final int DIM = 0xFF9A9A9A;
    private static final int TEXT = 0xFFE8E8E8;

    private static void draw(GuiGraphics g, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        Net.HudPacket p = latest;
        if (p == null || mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
        if (System.currentTimeMillis() - receivedAt > 5000L) return;   // the server stopped talking: nothing to claim
        Font font = mc.font;
        int x = 6;
        int lineH = 10;
        int lines = 3;
        int w = 132;
        int top = height - 6 - lines * lineH - 4;
        g.fill(x - 3, top - 3, x + w, top + lines * lineH + 3, 0x66000000);
        int y = top;
        piece(g, font, x, y, "HEAD", p.headName(), p.headClass(), p.headPlate(), p.headMax());
        y += lineH;
        piece(g, font, x, y, "CHEST", p.chestName(), p.chestClass(), p.chestPlate(), p.chestMax());
        y += lineH;
        int cx = x;
        cx = wound(g, font, cx, y, "LEGS", p.legTicks());
        cx = wound(g, font, cx, y, "ARMS", p.armTicks());
        wound(g, font, cx, y, "BLEED", p.bleedTicks());
    }

    private static void piece(GuiGraphics g, Font font, int x, int y, String label, String name, int cls, int plate, int max) {
        g.drawString(font, label, x, y, DIM, true);
        if (cls < 0) {
            g.drawString(font, name.isEmpty() ? "none" : name + " (no rating)", x + 34, y, DIM, true);
            return;
        }
        String shown = name.length() > 14 ? name.substring(0, 13) + "." : name;
        g.drawString(font, shown, x + 34, y, TEXT, true);
        int bx = x + 34 + font.width(shown) + 4;
        g.drawString(font, "c" + cls, bx, y, DIM, true);
        bx += 12;
        int bw = 30;
        g.fill(bx, y + 2, bx + bw, y + 7, 0xFF333333);
        if (max > 0) {
            int fill = Math.round(bw * Math.max(0, Math.min(max, plate)) / (float) max);
            int color = plate <= 0 ? HURT : plate * 3 < max ? 0xFFE0B040 : OK;
            g.fill(bx, y + 2, bx + fill, y + 7, color);
        }
        g.drawString(font, plate + "/" + max, bx + bw + 3, y, plate <= 0 ? HURT : TEXT, true);
    }

    private static int wound(GuiGraphics g, Font font, int x, int y, String label, int ticks) {
        boolean hurt = ticks > 0;
        String s = label + (hurt ? " " + Math.max(1, ticks / 20) + "s" : " ok");
        g.drawString(font, s, x, y, hurt ? HURT : OK, true);
        return x + font.width(s) + 8;
    }
}
