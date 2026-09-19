package gscraft.war.item;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import gscraft.war.GscraftWar;
import gscraft.war.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegistryObject;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * The player layer's items (system doc 2026-09-13 §7 build 3; crafting §5, design §4.2), registered from one list -
 * {@code /data/gscraft/gscraft_items/items.json}, which tools/items.py also turns into the models, the placeholder
 * textures and the names - so an item is a line of data, not a class. Each carries a stack size, a tooltip line
 * ({@code item.gscraft.<id>.tip}) and may be bulky: a player carrying a bulky item walks slowly and cannot sprint
 * (design §4.2's rule; the pack's refusal is the backpack mod's config, Phase C).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class SliceItems {
    private SliceItems() {}

    /** @param heal health a use closes (0: not a medicine); @param healTicks how long the use is held */
    public record Def(String id, int stack, boolean bulky, String role, int nutrition, float saturation, float heal, int healTicks) {}

    public static final List<Def> DEFS = load();
    public static final List<RegistryObject<Item>> REGISTERED = new ArrayList<>();
    public static int TOOL_USES = 64;

    private static List<Def> load() {
        List<Def> out = new ArrayList<>();
        try (var in = SliceItems.class.getResourceAsStream("/data/gscraft/gscraft_items/items.json")) {
            if (in == null) {
                GscraftWar.LOG.warn("[gscraft] no items.json: no slice items");
                return out;
            }
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonArray items = root.getAsJsonArray("items");
            for (JsonElement el : items) {
                JsonObject o = el.getAsJsonObject();
                out.add(new Def(o.get("id").getAsString(), o.has("stack") ? o.get("stack").getAsInt() : 64,
                        o.has("bulky") && o.get("bulky").getAsBoolean(), o.has("role") ? o.get("role").getAsString() : "item",
                        o.has("food") ? o.getAsJsonArray("food").get(0).getAsInt() : 0, o.has("food") ? o.getAsJsonArray("food").get(1).getAsFloat() : 0f,
                        o.has("heal") ? o.getAsJsonArray("heal").get(0).getAsFloat() : 0f, o.has("heal") ? o.getAsJsonArray("heal").get(1).getAsInt() : 0));
            }
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] items.json is invalid: {}", ex.toString());
        }
        return out;
    }

    /** called from ModItems' static init: every listed item registered */
    public static void register() {
        for (Def d : DEFS) {
            REGISTERED.add(ModItems.ITEMS.register(d.id(), () -> d.id().equals("claim_marker") ? new ClaimMarkerItem(d)
                    : d.id().startsWith("strike_") ? new gscraft.war.strike.StrikeItem(d, gscraft.war.strike.Strikes.Kind.valueOf(d.id().substring(7).toUpperCase(java.util.Locale.ROOT)))
                    : d.heal() > 0 ? new MedicineItem(d)
                    : new SliceItem(d)));
        }
        GscraftWar.LOG.info("[gscraft] items: {} from items.json", DEFS.size());
    }

    /**
     * A medicine (items.json "heal": [points, ticks]): held to use like the bandage, it clears the wounds and closes that much
     * health. The med kit's tooltip had always said "Heals a wound" and three quests pay in med kits, and the item did
     * NOTHING (the completeness audit, 2026-09-19). Finishing the use fires Forge's use-finish event, which is where The
     * Hordes cures an infection with any item in its `hordes:infection_cures` tag - the med kit is in it
     * (data/hordes/tags/items), so the one item is the cure the notebook promised and the economy can make.
     */
    public static class MedicineItem extends SliceItem {
        public MedicineItem(Def def) {
            super(def);
        }

        @Override
        public int getUseDuration(ItemStack stack) {
            return def.healTicks();
        }

        @Override
        public net.minecraft.world.item.UseAnim getUseAnimation(ItemStack stack) {
            return net.minecraft.world.item.UseAnim.BOW;
        }

        @Override
        public net.minecraft.world.InteractionResultHolder<ItemStack> use(Level level, net.minecraft.world.entity.player.Player player, net.minecraft.world.InteractionHand hand) {
            player.startUsingItem(hand);
            return net.minecraft.world.InteractionResultHolder.consume(player.getItemInHand(hand));
        }

        @Override
        public ItemStack finishUsingItem(ItemStack stack, Level level, net.minecraft.world.entity.LivingEntity user) {
            if (!level.isClientSide && user instanceof net.minecraft.world.entity.player.Player player) {
                gscraft.war.combat.PlayerWounds.clear(player);
                player.heal(def.heal());
                if (!player.getAbilities().instabuild) stack.shrink(1);
            }
            return stack;
        }
    }

    public static class SliceItem extends Item {
        public final Def def;

        private static Item.Properties props(Def def) {
            Item.Properties p = new Item.Properties().stacksTo(def.bulky() ? 1 : def.stack());
            if (def.role().equals("tool")) p = p.durability(TOOL_USES);   // a tool loses one point per order in the station's tool slot
            // "food": [nutrition, saturation] in items.json: nothing the mod registered could be eaten, on Hard (slice review 2026-09-19)
            if (def.nutrition() > 0) p = p.food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(def.nutrition()).saturationMod(def.saturation()).build());
            return p;
        }

        public SliceItem(Def def) {
            super(props(def));
            this.def = def;
        }

        @Override
        public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
            String key = "item.gscraft." + def.id() + ".tip";
            Component tip = Component.translatable(key);
            if (!tip.getString().equals(key)) lines.add(tip.copy().withStyle(ChatFormatting.GRAY));
            if (def.bulky()) lines.add(Component.translatable("gscraft.item.bulky").withStyle(ChatFormatting.GOLD));
            if (def.role().equals("card")) for (gscraft.war.station.Orders.Order o : gscraft.war.station.Orders.forCard(def.id())) {
                // the card's tooltip is the recipe (interface §4.3)
                lines.add(Component.literal(o.name() + ": " + o.needs() + "; " + gscraft.war.station.Orders.mmss(o.ticks()) + " at a station").withStyle(ChatFormatting.YELLOW));
            }
        }
    }

    /** the bulky rule: a player carrying one walks slowly and cannot sprint (checked every second) */
    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide || event.player.tickCount % 20 != 0) return;
        Player p = event.player;
        boolean bulky = false;
        for (ItemStack s : p.getInventory().items) {
            if (s.getItem() instanceof SliceItem si && si.def.bulky()) {
                bulky = true;
                break;
            }
        }
        if (!bulky) return;
        if (p instanceof net.minecraft.server.level.ServerPlayer sp) gscraft.war.journal.FieldNotes.note(sp, "bulky");   // the first time: a field note
        p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1, false, false, true));
        if (p.isSprinting()) p.setSprinting(false);
    }
}
