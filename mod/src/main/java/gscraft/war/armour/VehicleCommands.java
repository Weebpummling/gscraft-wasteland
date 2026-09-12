package gscraft.war.armour;

import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import gscraft.war.GscraftWar;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.commands.arguments.ResourceLocationArgument;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;

/**
 * The armour probe (design §7, V1): {@code /gscraft vehicle} reads and drives a Superb Warfare vehicle from the
 * console so the two questions that decide the rest are answered on the local server - does it drive on inputs
 * with nobody aboard, and what does each damage source come to after the mod's modifier list.
 * <pre>
 *   status &lt;vehicle&gt;                         health, parts, energy, inputs, turret
 *   fuel &lt;vehicle&gt;                           energy to the maximum
 *   input &lt;vehicle&gt; &lt;forward|back|left|right|sprint|fire&gt; &lt;on|off&gt;
 *   drive &lt;vehicle&gt; &lt;ticks&gt; [sprint]           forward for that long, then stop; the distance is reported
 *   target &lt;vehicle&gt; &lt;entity&gt; | none          the AI turret's target
 *   hit &lt;vehicle&gt; &lt;damage type&gt; &lt;amount&gt; [attacker]   what the list makes of it and what the hurt did
 * </pre>
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class VehicleCommands {
    private static final class Drive {
        final Vec3 from;
        int left;
        final boolean sprint;

        Drive(Vec3 from, int ticks, boolean sprint) {
            this.from = from;
            this.left = ticks;
            this.sprint = sprint;
        }
    }

    private static final Map<Integer, Drive> DRIVES = new HashMap<>();

    private VehicleCommands() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("gscraft").requires(s -> s.hasPermission(2))
                .then(Commands.literal("vehicle")
                        .then(Commands.literal("status").then(Commands.argument("vehicle", EntityArgument.entity()).executes(ctx -> {
                            Entity v = vehicle(ctx);
                            say(ctx, Vehicles.describe(v));
                            return 1;
                        })))
                        .then(Commands.literal("fuel").then(Commands.argument("vehicle", EntityArgument.entity()).executes(ctx -> {
                            Entity v = vehicle(ctx);
                            Vehicles.refuel(v);
                            say(ctx, String.format(Locale.ROOT, "energy %d/%d", Vehicles.energy(v), Vehicles.maxEnergy(v)));
                            return 1;
                        })))
                        .then(Commands.literal("input").then(Commands.argument("vehicle", EntityArgument.entity())
                                .then(Commands.argument("which", StringArgumentType.word()).then(Commands.argument("on", StringArgumentType.word()).executes(ctx -> {
                                    Entity v = vehicle(ctx);
                                    String which = StringArgumentType.getString(ctx, "which");
                                    boolean on = StringArgumentType.getString(ctx, "on").equals("on");
                                    boolean ok = Vehicles.input(v, which, on);
                                    say(ctx, ok ? which + " " + (on ? "on" : "off") + "; now " + Vehicles.inputState(v, which) : "no such input " + which);
                                    return ok ? 1 : 0;
                                })))))
                        .then(Commands.literal("drive").then(Commands.argument("vehicle", EntityArgument.entity())
                                .then(Commands.argument("ticks", IntegerArgumentType.integer(1, 1200)).executes(ctx -> drive(ctx, false))
                                        .then(Commands.literal("sprint").executes(ctx -> drive(ctx, true))))))
                        .then(Commands.literal("target").then(Commands.argument("vehicle", EntityArgument.entity())
                                .then(Commands.literal("none").executes(ctx -> {
                                    Entity v = vehicle(ctx);
                                    say(ctx, "turret target cleared: " + Vehicles.setTurretTarget(v, null));
                                    return 1;
                                }))
                                .then(Commands.argument("target", EntityArgument.entity()).executes(ctx -> {
                                    Entity v = vehicle(ctx);
                                    Entity t = EntityArgument.getEntity(ctx, "target");
                                    boolean ok = Vehicles.setTurretTarget(v, t.getUUID());
                                    say(ctx, (ok ? "turret target " : "no turret target field; ") + t.getName().getString());
                                    return ok ? 1 : 0;
                                }))))
                        .then(Commands.literal("hit").then(Commands.argument("vehicle", EntityArgument.entity())
                                .then(Commands.argument("type", ResourceLocationArgument.id()).then(Commands.argument("amount", FloatArgumentType.floatArg(0.0F))
                                        .executes(ctx -> hit(ctx, null))
                                        .then(Commands.argument("attacker", EntityArgument.entity()).executes(ctx -> hit(ctx, EntityArgument.getEntity(ctx, "attacker"))))))))));
    }

    private static Entity vehicle(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        Entity v = EntityArgument.getEntity(ctx, "vehicle");
        if (!Vehicles.isVehicle(v)) throw new com.mojang.brigadier.exceptions.SimpleCommandExceptionType(Component.literal(v.getName().getString() + " is not a Superb Warfare vehicle")).create();
        return v;
    }

    private static int drive(CommandContext<CommandSourceStack> ctx, boolean sprint) throws CommandSyntaxException {
        Entity v = vehicle(ctx);
        int ticks = IntegerArgumentType.getInteger(ctx, "ticks");
        DRIVES.put(v.getId(), new Drive(v.position(), ticks, sprint));
        say(ctx, String.format(Locale.ROOT, "driving %s forward for %d ticks%s from %.1f %.1f %.1f (energy %d)", v.getName().getString(), ticks, sprint ? " at a sprint" : "", v.getX(), v.getY(), v.getZ(), Vehicles.energy(v)));
        return 1;
    }

    private static int hit(CommandContext<CommandSourceStack> ctx, Entity attacker) throws CommandSyntaxException {
        Entity v = vehicle(ctx);
        ResourceLocation id = ResourceLocationArgument.getId(ctx, "type");
        float amount = FloatArgumentType.getFloat(ctx, "amount");
        ServerLevel level = ctx.getSource().getLevel();
        Optional<Holder.Reference<DamageType>> holder = level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolder(ResourceKey.create(Registries.DAMAGE_TYPE, id));
        if (holder.isEmpty()) {
            say(ctx, "no damage type " + id);
            return 0;
        }
        DamageSource source = new DamageSource(holder.get(), attacker, attacker);
        float before = Vehicles.health(v);
        float computed = Vehicles.compute(v, source, amount);
        boolean took = v.hurt(source, amount);
        float after = Vehicles.health(v);
        say(ctx, String.format(Locale.ROOT, "%s %.1f by %s: the list makes it %.2f; hurt %s; health %.1f -> %.1f (%.2f taken); wreck %s",
                id, amount, attacker == null ? "nobody" : attacker.getName().getString(), computed, took, before, after, before - after, Vehicles.wreck(v)));
        return 1;
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || DRIVES.isEmpty()) return;
        for (ServerLevel level : event.getServer().getAllLevels()) {
            Iterator<Map.Entry<Integer, Drive>> it = DRIVES.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry<Integer, Drive> e = it.next();
                Entity v = level.getEntity(e.getKey());
                if (v == null) continue;
                Drive d = e.getValue();
                if (--d.left > 0) {
                    Vehicles.input(v, "forward", true);
                    Vehicles.input(v, "sprint", d.sprint);
                } else {
                    Vehicles.allStop(v);
                    GscraftWar.LOG.info("[gscraft] vehicle drive done: {} moved {} blocks to {} {} {} (energy {})", v.getName().getString(),
                            String.format(Locale.ROOT, "%.2f", v.position().distanceTo(d.from)), String.format(Locale.ROOT, "%.1f", v.getX()), String.format(Locale.ROOT, "%.1f", v.getY()), String.format(Locale.ROOT, "%.1f", v.getZ()), Vehicles.energy(v));
                    it.remove();
                }
            }
        }
    }

    private static void say(CommandContext<CommandSourceStack> ctx, String text) {
        ctx.getSource().sendSuccess(() -> Component.literal(text), false);
    }
}
