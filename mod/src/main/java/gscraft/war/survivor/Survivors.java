package gscraft.war.survivor;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.item.IAmmo;
import gscraft.war.GscraftWar;
import gscraft.war.entity.GunAttackGoal;
import net.minecraft.ChatFormatting;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * The six survivors as data ({@code /data/gscraft/gscraft_survivors/survivors.json}): who they are, the villager
 * tag that is them, the chapter their right-click opens, and the first join's title, lines and kit.
 */
public final class Survivors {
    private Survivors() {}

    public record Def(String id, String name, String colour, String profession, String chapter) {
        public String tag() {
            return "gscraft_npc_" + id;
        }

        /** the name on the radio: the first word, upper case */
        public String call() {
            return name.split(" ")[0].toUpperCase(Locale.ROOT);
        }

        public ChatFormatting format() {
            ChatFormatting f = ChatFormatting.getByName(colour.toUpperCase(Locale.ROOT));
            return f == null ? ChatFormatting.WHITE : f;
        }
    }

    /** @param respawn given again after a death, if the player does not carry one (owner, 2026-09-19: re-issue the pistol) */
    /** @param slot head|chest|legs|feet: worn, not carried (if that slot is free); @param respawnCount the count a respawn gives (0: the kit's own) */
    public record KitEntry(String item, int count, String gun, int magazines, String nbt, boolean respawn, String slot, int respawnCount) {}

    public static final List<Def> ALL = new ArrayList<>();
    public static final List<String[]> JOIN_LINES = new ArrayList<>();
    public static final List<KitEntry> KIT = new ArrayList<>();
    public static String TITLE = "WASTELAND";
    public static String SUBTITLE = "";
    public static String OPEN_CHAPTER = "";

    static {
        load();
    }

    private static void load() {
        try (var in = Survivors.class.getResourceAsStream("/data/gscraft/gscraft_survivors/survivors.json")) {
            if (in == null) {
                GscraftWar.LOG.warn("[gscraft] no survivors.json: nobody speaks");
                return;
            }
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            for (JsonElement el : root.getAsJsonArray("survivors")) {
                JsonObject o = el.getAsJsonObject();
                ALL.add(new Def(o.get("id").getAsString(), o.get("name").getAsString(), o.has("colour") ? o.get("colour").getAsString() : "white",
                        o.has("profession") ? o.get("profession").getAsString() : "minecraft:nitwit", o.has("chapter") ? o.get("chapter").getAsString() : o.get("id").getAsString()));
            }
            if (root.has("first_join")) {
                JsonObject fj = root.getAsJsonObject("first_join");
                if (fj.has("title")) TITLE = fj.get("title").getAsString();
                if (fj.has("subtitle")) SUBTITLE = fj.get("subtitle").getAsString();
                if (fj.has("open_chapter")) OPEN_CHAPTER = fj.get("open_chapter").getAsString();
                if (fj.has("lines")) for (JsonElement el : fj.getAsJsonArray("lines")) {
                    JsonArray a = el.getAsJsonArray();
                    JOIN_LINES.add(new String[]{a.get(0).getAsString(), a.get(1).getAsString()});
                }
                if (fj.has("kit")) for (JsonElement el : fj.getAsJsonArray("kit")) {
                    JsonObject o = el.getAsJsonObject();
                    KIT.add(new KitEntry(o.has("item") ? o.get("item").getAsString() : null, o.has("count") ? o.get("count").getAsInt() : 1,
                            o.has("gun") ? o.get("gun").getAsString() : null, o.has("magazines") ? o.get("magazines").getAsInt() : 1,
                            o.has("nbt") ? o.get("nbt").getAsString() : null, o.has("respawn") && o.get("respawn").getAsBoolean(),
                            o.has("slot") ? o.get("slot").getAsString() : null, o.has("respawn_count") ? o.get("respawn_count").getAsInt() : 0));
                }
            }
        } catch (RuntimeException | java.io.IOException ex) {
            GscraftWar.LOG.error("[gscraft] survivors.json is invalid: {}", ex.toString());
        }
        GscraftWar.LOG.info("[gscraft] survivors: {}, {} join lines, {} kit entries", ALL.size(), JOIN_LINES.size(), KIT.size());
    }

    public static Def byId(String id) {
        for (Def d : ALL) if (d.id().equals(id)) return d;
        return null;
    }

    /** the survivor an entity is, by its tag, or null */
    public static Def byTag(Entity e) {
        for (Def d : ALL) if (e.getTags().contains(d.tag())) return d;
        return null;
    }

    private static Item item(String id) {
        ResourceLocation rl = ResourceLocation.tryParse(id);
        Item it = rl == null ? null : ForgeRegistries.ITEMS.getValue(rl);
        return it == null || it == Items.AIR ? null : it;
    }

    /** the first join's kit as stacks: a gun comes loaded with its spare magazines as TACZ ammo */
    public static List<ItemStack> kit() {
        return kit(false);
    }

    /** @param respawnOnly only the entries marked {@code "respawn": true}: what a player gets back after a death */
    public static List<ItemStack> kit(boolean respawnOnly) {
        List<ItemStack> out = new ArrayList<>();
        for (KitEntry k : KIT) {
            if (respawnOnly && !k.respawn()) continue;
            if (k.gun() != null) {
                Item gunItem = item("tacz:modern_kinetic_gun");
                Item ammoItem = item("tacz:ammo");
                var index = TimelessAPI.getCommonGunIndex(new ResourceLocation(k.gun()));
                if (gunItem == null || index.isEmpty()) {
                    GscraftWar.LOG.warn("[gscraft] kit gun {} is not a loaded TACZ gun", k.gun());
                    continue;
                }
                ItemStack gun = new ItemStack(gunItem);
                gun.getOrCreateTag().putString("GunId", k.gun());
                GunAttackGoal.refill(gun);
                out.add(gun);
                if (ammoItem != null && k.magazines() > 0) {
                    ItemStack ammo = new ItemStack(ammoItem);
                    IAmmo ia = IAmmo.getIAmmoOrNull(ammo);
                    if (ia != null) {
                        ia.setAmmoId(ammo, index.get().getGunData().getAmmoId());
                        ammo.setCount(index.get().getGunData().getAmmoAmount() * k.magazines());
                        out.add(ammo);
                    }
                }
                continue;
            }
            Item it = item(k.item());
            if (it == null) {
                GscraftWar.LOG.warn("[gscraft] kit item {} is not registered", k.item());
                continue;
            }
            // a respawn may give less than the first join did (`respawn_count`); more than a stack is several stacks (150 rifle rounds)
            int left = respawnOnly && k.respawnCount() > 0 ? k.respawnCount() : k.count();
            while (left > 0) {
                ItemStack stack = new ItemStack(it, Math.min(left, it.getMaxStackSize(new ItemStack(it))));
                left -= stack.getCount();
                if (k.nbt() != null) {   // the notebook: patchouli:guide_book with its book id; a gun: its loaded rounds
                    try {
                        stack.setTag(net.minecraft.nbt.TagParser.parseTag(k.nbt()));
                    } catch (com.mojang.brigadier.exceptions.CommandSyntaxException ex) {
                        GscraftWar.LOG.warn("[gscraft] kit item {} has bad nbt: {}", k.item(), ex.getMessage());
                    }
                }
                if (k.slot() != null) stack.getOrCreateTag().putString(WEAR, k.slot());   // read and removed by give()
                out.add(stack);
            }
        }
        return out;
    }

    private static final String WEAR = "GscraftKitSlot";

    /**
     * The kit into a player's hands - and onto their back: an entry with a `slot` is WORN if that slot is free, carried if it
     * is not. On a respawn, an item the player already carries or wears is not given again. Returns the stacks given.
     */
    public static int give(net.minecraft.server.level.ServerPlayer p, boolean respawnOnly) {
        int given = 0;
        java.util.Set<Item> had = new java.util.HashSet<>();
        if (respawnOnly) {
            for (int i = 0; i < p.getInventory().getContainerSize(); i++) had.add(p.getInventory().getItem(i).getItem());
        }
        for (ItemStack s : kit(respawnOnly)) {
            String wear = s.hasTag() && s.getTag().contains(WEAR) ? s.getTag().getString(WEAR) : null;
            if (wear != null) {
                s.getTag().remove(WEAR);
                if (s.getTag().isEmpty()) s.setTag(null);
            }
            if (respawnOnly && had.contains(s.getItem())) continue;
            net.minecraft.world.entity.EquipmentSlot slot = wear == null ? null : switch (wear) {
                case "head" -> net.minecraft.world.entity.EquipmentSlot.HEAD;
                case "chest" -> net.minecraft.world.entity.EquipmentSlot.CHEST;
                case "legs" -> net.minecraft.world.entity.EquipmentSlot.LEGS;
                case "feet" -> net.minecraft.world.entity.EquipmentSlot.FEET;
                default -> null;
            };
            if (slot != null && p.getItemBySlot(slot).isEmpty()) p.setItemSlot(slot, s);
            else if (!p.getInventory().add(s)) p.drop(s, false);
            given++;
        }
        return given;
    }
}
