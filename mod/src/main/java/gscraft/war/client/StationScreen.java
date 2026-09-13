package gscraft.war.client;

import gscraft.war.station.StationMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

/** the station's screen: vanilla's chest background at four rows, the title the station's name (interface §4.3) */
public class StationScreen extends AbstractContainerScreen<StationMenu> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("textures/gui/container/generic_54.png");

    public StationScreen(StationMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        imageHeight = 114 + StationMenu.ROWS * 18;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        renderBackground(g);
        super.render(g, mouseX, mouseY, partial);
        renderTooltip(g, mouseX, mouseY);
    }

    @Override
    protected void renderBg(GuiGraphics g, float partial, int mouseX, int mouseY) {
        int top = StationMenu.ROWS * 18 + 17;
        g.blit(TEXTURE, leftPos, topPos, 0, 0, imageWidth, top);
        g.blit(TEXTURE, leftPos, topPos + top, 0, 126, imageWidth, 96);
    }
}
