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
 * The body readout, bottom left (owner, 2026-09-11): a small figure - head, torso, arms, legs - each part coloured by
 * its state, the helmet and the vest drawn as a fill that drains with the plate and an outline that says the armour
 * class, and beside it the two plate counts and any wound's seconds. Fed by {@link Net.HudPacket} once a second.
 * Superb Warfare's own plate bar is hidden: it only knows its two vests and its own plate scale.
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

    @Mod.EventBusSubscriber(modid = GscraftWar.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class Register {
        private Register() {}

        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent event) {
            event.registerAboveAll("body", (gui, graphics, partialTick, width, height) -> draw(graphics, width, height));
        }
    }

    @Mod.EventBusSubscriber(modid = GscraftWar.MODID, value = Dist.CLIENT)
    public static final class Hide {
        private Hide() {}

        @SubscribeEvent
        public static void pre(RenderGuiOverlayEvent.Pre event) {
            if (SW_PLATE_OVERLAY.equals(event.getOverlay().id())) event.setCanceled(true);
        }
    }

    // the palette: flesh, armour by class, the wound
    private static final int SKIN = 0xFFD8C4A0;
    private static final int SKIN_DIM = 0xFF6E6252;
    private static final int WOUND = 0xFFD9453A;
    private static final int WOUND_DIM = 0xFF5A2A26;
    private static final int PLATE = 0xFF8FB1C9;
    private static final int PLATE_GONE = 0xFF3A4652;
    private static final int TEXT = 0xFFE6E6E6;
    private static final int DIM = 0xFF9C9C9C;
    private static final int BACK = 0x70000000;

    private static void draw(GuiGraphics g, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        Net.HudPacket p = latest;
        if (p == null || mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
        if (System.currentTimeMillis() - receivedAt > 5000L) return;
        Font font = mc.font;
        long t = System.currentTimeMillis();
        boolean blink = (t / 400L) % 2 == 0;

        // the panel: 92 wide, 46 high, in the corner above the bottom edge
        int panelW = 94;
        int panelH = 46;
        int x0 = 6;
        int y0 = height - 6 - panelH;
        g.fill(x0, y0, x0 + panelW, y0 + panelH, BACK);

        // the figure, 22 wide and 40 high, centred in the left 30
        int fx = x0 + 4;
        int fy = y0 + 3;
        boolean legs = p.legTicks() > 0;
        boolean arms = p.armTicks() > 0;
        boolean bleed = p.bleedTicks() > 0;
        // head 8x8 at the top centre: the helmet fills it from the bottom by plate share, the outline is the class
        part(g, fx + 7, fy, 8, 8, p.headClass(), p.headPlate(), p.headMax(), false, blink);
        // torso 12x16: the vest the same way; bleeding blinks the torso red
        part(g, fx + 5, fy + 9, 12, 16, p.chestClass(), p.chestPlate(), p.chestMax(), bleed, blink);
        // arms 4x14 either side of the torso
        limb(g, fx, fy + 9, 4, 14, arms, blink);
        limb(g, fx + 18, fy + 9, 4, 14, arms, blink);
        // legs 5x14 below the torso
        limb(g, fx + 5, fy + 26, 5, 14, legs, blink);
        limb(g, fx + 12, fy + 26, 5, 14, legs, blink);

        // the numbers beside it: helmet and vest plate, then the wounds' seconds
        int tx = x0 + 32;
        int ty = y0 + 4;
        plateLine(g, font, tx, ty, "H", p.headClass(), p.headPlate(), p.headMax());
        plateLine(g, font, tx, ty + 10, "C", p.chestClass(), p.chestPlate(), p.chestMax());
        int wy = ty + 22;
        String w = "";
        if (legs) w += "leg " + secs(p.legTicks()) + " ";
        if (arms) w += "arm " + secs(p.armTicks()) + " ";
        if (bleed) w += "bleed " + secs(p.bleedTicks());
        if (w.isEmpty()) {
            g.drawString(font, "unhurt", tx, wy, DIM, false);
        } else {
            g.drawString(font, w.trim(), tx, wy, blink ? WOUND : TEXT, false);
        }
    }

    private static String secs(int ticks) {
        return Math.max(1, ticks / 20) + "s";
    }

    /** a body part with armour over it: the flesh, the plate's fill from the bottom, and a one-pixel outline by class */
    private static void part(GuiGraphics g, int x, int y, int w, int h, int cls, int plate, int max, boolean wounded, boolean blink) {
        int flesh = wounded && blink ? WOUND : wounded ? WOUND_DIM : SKIN;
        g.fill(x, y, x + w, y + h, flesh);
        if (cls >= 0 && max > 0) {
            int fill = Math.round(h * Math.max(0, Math.min(max, plate)) / (float) max);
            g.fill(x, y + h - fill, x + w, y + h, PLATE);
            if (fill < h) g.fill(x, y, x + w, y + h - fill, plate <= 0 ? PLATE_GONE : flesh);
        }
        int outline = classColour(cls);
        g.fill(x - 1, y - 1, x + w + 1, y, outline);
        g.fill(x - 1, y + h, x + w + 1, y + h + 1, outline);
        g.fill(x - 1, y, x, y + h, outline);
        g.fill(x + w, y, x + w + 1, y + h, outline);
    }

    private static void limb(GuiGraphics g, int x, int y, int w, int h, boolean wounded, boolean blink) {
        g.fill(x, y, x + w, y + h, wounded ? (blink ? WOUND : WOUND_DIM) : SKIN);
    }

    private static int classColour(int cls) {
        if (cls < 0) return 0x00000000;          // nothing worn, or nothing the model knows: no outline
        if (cls == 0) return 0xFF7A7A7A;          // cloth
        if (cls <= 2) return 0xFFD8D8D8;          // soft armour
        if (cls == 3) return 0xFF6FC3E8;          // a helmet's class, a light plate
        return 0xFFE8C160;                        // a plate carrier
    }

    private static void plateLine(GuiGraphics g, Font font, int x, int y, String label, int cls, int plate, int max) {
        g.drawString(font, label, x, y, DIM, false);
        if (cls < 0 || max <= 0) {
            g.drawString(font, cls < 0 ? "-" : "cloth", x + 8, y, DIM, false);
            return;
        }
        int colour = plate <= 0 ? WOUND : plate * 3 < max ? 0xFFE0B040 : TEXT;
        g.drawString(font, plate + "/" + max, x + 8, y, colour, false);
        String c = "c" + cls;
        g.drawString(font, c, x + 8 + font.width("40/40") + 4, y, classColour(cls), false);
    }
}
