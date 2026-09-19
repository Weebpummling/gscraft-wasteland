package gscraft.war.survivor;

import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import gscraft.war.GscraftWar;
import gscraft.war.world.Stages;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.Vec3Argument;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.entity.npc.VillagerType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * The survivors where the owner puts them (owner, 2026-09-18: "provide a way for us to easily edit where the NPCs are
 * placed. I am just going to manually place them"). Stand where a survivor should stand, look where they should look,
 * and {@code /gscraft npc place <id>}: the spot is saved with the world and the survivor is put there now. Each survivor
 * has two slots - {@code start} (the compound) and {@code building} (where the site loop moves Marshall, Tony, Tune and
 * James when their building is taken); the one in force is the building's while its stage is set, else the start's.
 * <p>
 * Every other path still works and ends at the owner's spot: the datapack's {@code camp_npcs} / {@code camp_npc_<id>}
 * functions (the deploy, the resets, the site loop's held lists) summon at tools/camp.py's computed coordinates, and the
 * join hook here moves a survivor that arrives anywhere else to the saved spot in force. No record, no move: the
 * computed spot stands. The Java summon carries the one disabled placeholder trade - a survivor saved with an empty
 * offer list generates its trades on the autosave, and a cartographer's map search hangs the server (2026-09-13).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class NpcPlaces extends SavedData {
    public static final List<String> SLOTS = List.of("start", "building");
    /** the stage that puts a survivor's building slot in force; the two who live in the compound have none */
    public static final Map<String, String> BUILDING_STAGE = Map.of("marshall", "gatehouse_taken", "tony", "clinic_taken", "tune", "clinic_taken", "james", "crossing_taken");
    private static final String NAME = "gscraft_npc_places";

    public record Spot(double x, double y, double z, float yaw) {
        String text() {
            return String.format(Locale.ROOT, "%.1f %.1f %.1f facing %.0f", x, y, z, yaw);
        }
    }

    private final Map<String, Spot> spots = new LinkedHashMap<>();   // "<id>/<slot>" -> spot

    public static NpcPlaces get(ServerLevel anyLevel) {
        return anyLevel.getServer().overworld().getDataStorage().computeIfAbsent(NpcPlaces::load, NpcPlaces::new, NAME);
    }

    private static NpcPlaces load(CompoundTag tag) {
        NpcPlaces out = new NpcPlaces();
        for (String key : tag.getAllKeys()) {
            CompoundTag s = tag.getCompound(key);
            out.spots.put(key, new Spot(s.getDouble("x"), s.getDouble("y"), s.getDouble("z"), s.getFloat("yaw")));
        }
        return out;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        spots.forEach((key, s) -> {
            CompoundTag t = new CompoundTag();
            t.putDouble("x", s.x());
            t.putDouble("y", s.y());
            t.putDouble("z", s.z());
            t.putFloat("yaw", s.yaw());
            tag.put(key, t);
        });
        return tag;
    }

    public Spot spot(String id, String slot) {
        return spots.get(id + "/" + slot);
    }

    /** the owner's spot in force for this survivor, or null when none is saved (the datapack's computed spot stands) */
    public Spot inForce(String id) {
        String stage = BUILDING_STAGE.get(id);
        if (stage != null && Stages.isSet(stage) && spot(id, "building") != null) return spot(id, "building");
        if (stage != null && Stages.isSet(stage)) return null;   // moved out to a building the owner has not placed: the function's spot
        return spot(id, "start");
    }

    private static Survivors.Def def(String id) {
        for (Survivors.Def d : Survivors.ALL) if (d.id().equals(id)) return d;
        return null;
    }

    /** the survivor put up at the spot, any other copy of them removed; the same villager the datapack summons */
    public static Villager summon(ServerLevel level, Survivors.Def def, Spot spot) {
        for (Entity e : level.getAllEntities()) {
            if (e instanceof Villager && e.getTags().contains("gscraft_npc_" + def.id())) e.discard();
        }
        Villager v = EntityType.VILLAGER.create(level);
        if (v == null) return null;
        v.moveTo(spot.x(), spot.y(), spot.z(), spot.yaw(), 0f);
        v.setYHeadRot(spot.yaw());
        v.setYBodyRot(spot.yaw());
        v.setNoAi(true);
        v.setInvulnerable(true);
        v.setPersistenceRequired();
        v.setSilent(true);
        v.setCustomName(Component.literal(def.name()));
        v.setCustomNameVisible(true);
        v.addTag("gscraft_npc");
        v.addTag("gscraft_npc_" + def.id());
        VillagerProfession profession = ForgeRegistries.VILLAGER_PROFESSIONS.getValue(new ResourceLocation(def.profession()));
        v.setVillagerData(v.getVillagerData().setType(VillagerType.PLAINS).setLevel(2).setProfession(profession == null ? VillagerProfession.NITWIT : profession));
        MerchantOffers offers = new MerchantOffers();
        offers.add(new MerchantOffer(new ItemStack(Items.EMERALD), new ItemStack(Items.EMERALD), 0, 0, 0f));   // maxUses 0: the disabled placeholder
        v.setOffers(offers);
        level.addFreshEntity(v);
        return v;
    }

    /** a survivor arriving anywhere but the owner's spot in force (a datapack summon, a chunk load) is moved onto it */
    @SubscribeEvent
    public static void joined(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !(event.getEntity() instanceof Villager v)) return;
        for (String tag : v.getTags()) {
            if (!tag.startsWith("gscraft_npc_")) continue;
            // ONE of each survivor, ever. `summon` and the datapack's `kill @e[...]` reach loaded chunks only, so a copy left in
            // an unloaded one (the old south compound, a test spot) came back when its chunk loaded - and this hook then MOVED it
            // onto the owner's spot, beside the one already standing there (owner, 2026-09-19: "make sure no duplicates will
            // exist"). A survivor arriving while another of the same name stands is refused; refused from disk, it is gone for good.
            for (Entity other : level.getAllEntities()) {
                if (other != v && other instanceof Villager && other.isAlive() && !other.isRemoved() && other.getTags().contains(tag)) {
                    event.setCanceled(true);
                    v.discard();
                    GscraftWar.LOG.info("[gscraft] npc: a second {} arrived at {} and was refused (one stands at {})", tag.substring("gscraft_npc_".length()),
                            v.blockPosition().toShortString(), other.blockPosition().toShortString());
                    return;
                }
            }
            Spot spot = get(level).inForce(tag.substring("gscraft_npc_".length()));
            if (spot == null || v.distanceToSqr(spot.x(), spot.y(), spot.z()) < 0.5) return;
            v.moveTo(spot.x(), spot.y(), spot.z(), spot.yaw(), 0f);
            v.setYHeadRot(spot.yaw());
            v.setYBodyRot(spot.yaw());
            return;
        }
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("npc")
                        .then(Commands.literal("list").executes(NpcPlaces::list))
                        .then(Commands.literal("export").executes(NpcPlaces::export))
                        .then(Commands.literal("respawn").executes(ctx -> respawn(ctx, null))
                                .then(Commands.argument("id", StringArgumentType.word()).executes(ctx -> respawn(ctx, StringArgumentType.getString(ctx, "id")))))
                        .then(Commands.literal("clear").then(Commands.argument("id", StringArgumentType.word())
                                .executes(ctx -> clear(ctx, "start"))
                                .then(Commands.argument("slot", StringArgumentType.word()).executes(ctx -> clear(ctx, StringArgumentType.getString(ctx, "slot"))))))
                        .then(Commands.literal("place").then(Commands.argument("id", StringArgumentType.word())
                                .executes(ctx -> place(ctx, "start", null, null))
                                .then(Commands.argument("slot", StringArgumentType.word())
                                        .executes(ctx -> place(ctx, StringArgumentType.getString(ctx, "slot"), null, null))
                                        .then(Commands.argument("pos", Vec3Argument.vec3()).then(Commands.argument("yaw", FloatArgumentType.floatArg(-360, 360))
                                                .executes(ctx -> place(ctx, StringArgumentType.getString(ctx, "slot"), Vec3Argument.getVec3(ctx, "pos"), FloatArgumentType.getFloat(ctx, "yaw"))))))))));
    }

    private static int say(CommandContext<CommandSourceStack> ctx, String text) {
        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
        return 1;
    }

    /** stand where they should stand and look where they should look; or give the spot and the yaw (the console, the tests) */
    private static int place(CommandContext<CommandSourceStack> ctx, String slot, Vec3 at, Float yaw) {
        String id = StringArgumentType.getString(ctx, "id");
        Survivors.Def def = def(id);
        if (def == null) return say(ctx, "no survivor '" + id + "'; one of " + Survivors.ALL.stream().map(Survivors.Def::id).toList()) - 1;
        if (!SLOTS.contains(slot)) return say(ctx, "slot is start or building") - 1;
        if (slot.equals("building") && !BUILDING_STAGE.containsKey(id)) return say(ctx, def.name() + " lives in the compound: only a start spot") - 1;
        CommandSourceStack src = ctx.getSource();
        Vec3 p = at != null ? at : src.getPosition();
        float facing = yaw != null ? yaw : src.getRotation().y;
        Spot spot = new Spot(Math.floor(p.x) + 0.5, p.y, Math.floor(p.z) + 0.5, facing);   // the block's centre, the height as given
        NpcPlaces data = get(src.getLevel());
        data.spots.put(id + "/" + slot, spot);
        data.setDirty();
        boolean now = spot.equals(data.inForce(id));
        if (now) summon(src.getServer().overworld(), def, spot);
        GscraftWar.LOG.info("[gscraft] npc: {} {} placed at {}{}", id, slot, spot.text(), now ? "" : " (not in force now)");
        return say(ctx, def.name() + " " + slot + " spot: " + spot.text() + (now ? " - standing there now" : " - saved; it takes effect " + (slot.equals("building")
                ? "when " + BUILDING_STAGE.get(id) + " is set" : "when they are back in the compound")));
    }

    private static int clear(CommandContext<CommandSourceStack> ctx, String slot) {
        String id = StringArgumentType.getString(ctx, "id");
        NpcPlaces data = get(ctx.getSource().getLevel());
        boolean had = data.spots.remove(id + "/" + slot) != null;
        data.setDirty();
        return say(ctx, had ? id + " " + slot + " spot cleared: the datapack's computed spot stands again (run /function gscraft:camp_npcs or /gscraft npc respawn)" : id + " had no " + slot + " spot saved");
    }

    /** every survivor (or one) put up again: the owner's spot in force, else the datapack's function for them */
    private static int respawn(CommandContext<CommandSourceStack> ctx, String only) {
        CommandSourceStack src = ctx.getSource();
        NpcPlaces data = get(src.getLevel());
        int mine = 0, theirs = 0;
        for (Survivors.Def d : Survivors.ALL) {
            if (only != null && !only.equals(d.id())) continue;
            Spot spot = data.inForce(d.id());
            if (spot != null) {
                summon(src.getServer().overworld(), d, spot);
                mine++;
            } else {
                String stage = BUILDING_STAGE.get(d.id());
                String fn = stage != null && !Stages.isSet(stage) ? "camp_start_" + d.id() : "camp_npc_" + d.id();
                src.getServer().getCommands().performPrefixedCommand(src.withSuppressedOutput(), "function gscraft:" + fn);
                theirs++;
            }
        }
        return say(ctx, "survivors put up: " + mine + " at saved spots, " + theirs + " by the datapack's functions");
    }

    private static int list(CommandContext<CommandSourceStack> ctx) {
        ServerLevel level = ctx.getSource().getServer().overworld();
        NpcPlaces data = get(level);
        StringBuilder sb = new StringBuilder("survivors' spots (saved with the world):");
        for (Survivors.Def d : Survivors.ALL) {
            Spot s = data.spot(d.id(), "start"), b = data.spot(d.id(), "building"), f = data.inForce(d.id());
            String stands = "not loaded";
            int copies = 0;
            for (Entity e : level.getAllEntities()) {
                if (e instanceof Villager && e.isAlive() && e.getTags().contains("gscraft_npc_" + d.id())) {
                    stands = String.format(Locale.ROOT, "%.1f %.1f %.1f", e.getX(), e.getY(), e.getZ());
                    copies++;
                }
            }
            if (copies > 1) stands += " - " + copies + " COPIES LOADED (run /gscraft npc respawn " + d.id() + ")";
            sb.append("\n  ").append(d.id()).append(": start ").append(s == null ? "(computed)" : s.text());
            if (BUILDING_STAGE.containsKey(d.id())) sb.append("; building ").append(b == null ? "(computed)" : b.text()).append(" [").append(BUILDING_STAGE.get(d.id())).append(Stages.isSet(BUILDING_STAGE.get(d.id())) ? " set]" : " unset]");
            sb.append("; in force ").append(f == null ? "computed" : "saved").append("; stands at ").append(stands);
        }
        return say(ctx, sb.toString());
    }

    /** the saved spots as lines to paste into tools/camp.py when they are final */
    private static int export(CommandContext<CommandSourceStack> ctx) {
        NpcPlaces data = get(ctx.getSource().getLevel());
        if (data.spots.isEmpty()) return say(ctx, "no spots saved");
        StringBuilder sb = new StringBuilder("saved spots (id/slot x y z yaw):");
        data.spots.forEach((key, s) -> sb.append(String.format(Locale.ROOT, "%n  %s %.1f %.1f %.1f %.0f", key, s.x(), s.y(), s.z(), s.yaw())));
        GscraftWar.LOG.info("[gscraft] npc export: {}", sb.toString().replace("\n", " |"));
        return say(ctx, sb.toString());
    }
}
