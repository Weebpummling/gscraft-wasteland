package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * The camp's function levels as SYSTEMS (owner, 2026-09-19: "apply the upgrade system to just system based and skip the
 * upgrade visuals"). Each level is a stage a survivor's quest already sets (quests doc §2-§5); until now nothing read
 * them. No block is placed and nothing is built: a level changes a rule.
 * <pre>
 * workshop_1  W3  station orders take WORKSHOP_1 of their time          workshop_2  W4  ... WORKSHOP_2
 * storage_1   W2  the backpack (the quest's own reward; no rule)
 * medical_1   T2  the clinic: inside the compound an infection is cured, and a downed player is on their feet after
 *                 CLINIC_REVIVE_SECONDS (quests doc T2: "revived by the script after 10 s")
 * medical_2   T3  a lighter death: the respawn also gives a magazine of pistol rounds and two bandages
 * generator_1 M2  lights: nothing hostile is placed within GENERATOR_MARGIN more blocks of the compound's wall
 * water_1     M3  clean water: inside the compound a hurt player mends, half a heart every WATER_EVERY_SECONDS
 * radio_1     U2  the warning: Tune's ten-minute warning of a counterattack is heard only with Radio 1 (Loop.fortify)
 * radio_2     U3  the whole countdown of a held site's clock as a bar (Loop.fortify), and the Cobra (Air support's gate)
 * </pre>
 * Where the design's own effect exists it is the design's (medical, radio); where the design named recipes that do not
 * exist (workshop, generator, water) the effect is a rule in the same spirit, and every number is a setting.
 * {@code /gscraft upgrades} lists each level, whether it is set and what it does now; {@code /gscraft upgrades at <pos>}
 * says whether the director may place at a spot, which is how the generator's margin is proven without a player.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Upgrades {
    private Upgrades() {}

    public static double WORKSHOP_1 = 0.85D, WORKSHOP_2 = 0.70D;
    public static int GENERATOR_MARGIN = 16;
    public static int CLINIC_REVIVE_SECONDS = 10;
    public static int WATER_EVERY_SECONDS = 5;
    public static int DEATH_ROUNDS = 17, DEATH_BANDAGES = 2;

    private static final Map<UUID, Integer> downed = new HashMap<>();

    /** what a station order's time is multiplied by */
    public static double stationFactor() {
        return Stages.isSet("workshop_2") ? WORKSHOP_2 : Stages.isSet("workshop_1") ? WORKSHOP_1 : 1.0D;
    }

    /** blocks added to the compound's no-placement margin */
    public static int marginBonus(String zone) {
        return zone.equals("camp_compound") && Stages.isSet("generator_1") ? GENERATOR_MARGIN : 0;
    }

    public static boolean warningHeard() {
        return Stages.isSet("radio_1");
    }

    public static boolean countdownShown() {
        return Stages.isSet("radio_2");
    }

    /** Medical 2: what a death gives back on top of the kit's respawn entries; the count of stacks given */
    public static int afterRespawn(ServerPlayer p) {
        if (!Stages.isSet("medical_2")) return 0;
        int given = 0;
        for (String[] e : new String[][] {{"superbwarfare:handgun_ammo", String.valueOf(DEATH_ROUNDS)}, {"gscraft:bandage", String.valueOf(DEATH_BANDAGES)}}) {
            var item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(e[0]));
            int n = Integer.parseInt(e[1]);
            if (item == null || n <= 0) continue;   // on top of the basic gear the respawn gives (2026-09-20), so no 'already carried' test
            ItemStack s = new ItemStack(item, n);
            if (!p.getInventory().add(s)) p.drop(s, false);
            given++;
        }
        return given;
    }

    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer p) || p.tickCount % 20 != 0) return;
        if (p.level().dimension() != Level.OVERWORLD || p.isSpectator()) return;
        Sites.CampDef camp = Sites.camp();
        if (camp == null || !camp.inSquare(p.getX(), p.getZ())) {
            downed.remove(p.getUUID());
            return;
        }
        if (Stages.isSet("medical_1")) {
            MobEffect infected = ForgeRegistries.MOB_EFFECTS.getValue(new ResourceLocation("hordes", "infected"));
            if (infected != null && p.hasEffect(infected) && p.removeEffect(infected)) {
                p.displayClientMessage(Component.translatable("gscraft.upgrade.cured"), false);
                GscraftWar.LOG.info("[gscraft] upgrades: the clinic cured {}", p.getGameProfile().getName());
            }
            if (bleeding(p)) {
                int s = downed.merge(p.getUUID(), 1, Integer::sum);
                if (s >= CLINIC_REVIVE_SECONDS && revive(p)) {
                    downed.remove(p.getUUID());
                    p.displayClientMessage(Component.translatable("gscraft.upgrade.revived"), false);
                    GscraftWar.LOG.info("[gscraft] upgrades: the clinic got {} up", p.getGameProfile().getName());
                }
            } else downed.remove(p.getUUID());
        }
        if (Stages.isSet("water_1") && WATER_EVERY_SECONDS > 0 && (p.tickCount / 20) % WATER_EVERY_SECONDS == 0
                && p.isAlive() && p.getHealth() < p.getMaxHealth() && !bleeding(p)) p.heal(1.0F);
    }

    // PlayerRevive, by reflection: team.creative.playerrevive.server.PlayerReviveServer.isBleeding(Player) / revive(Player)
    private static Method isBleeding, revive;
    private static boolean looked;

    private static void look() {
        if (looked) return;
        looked = true;
        try {
            Class<?> c = Class.forName("team.creative.playerrevive.server.PlayerReviveServer");
            isBleeding = c.getMethod("isBleeding", net.minecraft.world.entity.player.Player.class);
            revive = c.getMethod("revive", net.minecraft.world.entity.player.Player.class);
        } catch (ReflectiveOperationException | LinkageError ex) {
            GscraftWar.LOG.warn("[gscraft] upgrades: PlayerRevive is not reachable ({}): the clinic cannot get a downed player up", ex.toString());
        }
    }

    public static boolean reviveReachable() {
        look();
        return isBleeding != null && revive != null;
    }

    public static boolean bleeding(ServerPlayer p) {
        look();
        try {
            return isBleeding != null && (boolean) isBleeding.invoke(null, p);
        } catch (ReflectiveOperationException ex) {
            return false;
        }
    }

    private static boolean revive(ServerPlayer p) {
        try {
            if (revive == null) return false;
            revive.invoke(null, p);
            return true;
        } catch (ReflectiveOperationException ex) {
            return false;
        }
    }

    private static String line(String stage, String what) {
        return (Stages.isSet(stage) ? "[x] " : "[ ] ") + stage + ": " + what;
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("upgrades").executes(ctx -> {
                    String out = String.join("\n",
                            line("workshop_1", "station orders at x" + WORKSHOP_1), line("workshop_2", "station orders at x" + WORKSHOP_2),
                            line("medical_1", "the clinic: in the compound an infection is cured and a downed player is up after " + CLINIC_REVIVE_SECONDS + " s (PlayerRevive reachable: " + reviveReachable() + ")"),
                            line("medical_2", "a death also gives back " + DEATH_ROUNDS + " pistol rounds and " + DEATH_BANDAGES + " bandages"),
                            line("generator_1", "nothing hostile placed within " + GENERATOR_MARGIN + " more blocks of the compound"),
                            line("water_1", "in the compound a hurt player mends half a heart every " + WATER_EVERY_SECONDS + " s"),
                            line("radio_1", "Tune's ten-minute warning of a counterattack is heard"), line("radio_2", "a held site's whole countdown is shown; the Cobra can be called"),
                            "now: station factor " + stationFactor() + "; compound margin +" + marginBonus("camp_compound") + "; warning heard " + warningHeard() + "; countdown shown " + countdownShown());
                    ctx.getSource().sendSuccess(() -> Component.literal(out), false);
                    return 1;
                }).then(Commands.literal("at").then(Commands.argument("pos", BlockPosArgument.blockPos()).executes(ctx -> {
                    BlockPos pos = BlockPosArgument.getBlockPos(ctx, "pos");
                    boolean refused = Zones.nearExcluded(pos.getX(), pos.getZ());
                    boolean soldiers = Director.tooCloseForSoldiers(ctx.getSource().getLevel(), pos.getX(), pos.getZ());
                    ctx.getSource().sendSuccess(() -> Component.literal(pos.toShortString() + ": placement " + (refused ? "REFUSED (an excluded zone's margin)" : "allowed by the margins") + "; soldiers " + (refused || soldiers ? "REFUSED" : "allowed")), false);
                    return refused ? 0 : 1;
                })))));
    }
}
