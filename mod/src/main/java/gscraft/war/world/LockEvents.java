package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraftforge.event.entity.EntityMobGriefingEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.event.level.PistonEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * What a lock refuses: player break, place and right-click; any non-player placement; explosions lose every
 * affected block inside; mob griefing inside; fluids forming blocks inside; pistons within {@link Locks#PISTON_MARGIN}.
 * Ops in creative bypass the player rules so the world can still be edited by hand. Server-run commands never
 * post these events, so the quest's template functions pass.
 *
 * Also here: Pomkot's Mechs never grief, anywhere (the hub's Custodian destroys terrain on Hard) - the old
 * gscraft_mech_griefing.js.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class LockEvents {
    private static final String MECHS = "pomkotsmechs";

    private LockEvents() {}

    private static boolean overworld(LevelAccessor level) {
        return level instanceof Level l && l.dimension() == Level.OVERWORLD;
    }

    private static boolean bypass(Entity entity) {
        return entity instanceof Player p && p.hasPermissions(2) && p.isCreative();
    }

    private static boolean locked(LevelAccessor level, BlockPos pos) {
        return overworld(level) && Locks.locked(pos.getX(), pos.getZ());
    }

    @SubscribeEvent
    public static void broken(BlockEvent.BreakEvent event) {
        if (locked(event.getLevel(), event.getPos()) && !bypass(event.getPlayer())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void placed(BlockEvent.EntityPlaceEvent event) {
        if (locked(event.getLevel(), event.getPos()) && !bypass(event.getEntity())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void rightClicked(PlayerInteractEvent.RightClickBlock event) {
        if (locked(event.getLevel(), event.getPos()) && !bypass(event.getEntity())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void explosion(ExplosionEvent.Detonate event) {
        if (!overworld(event.getLevel())) return;
        event.getAffectedBlocks().removeIf(p -> Locks.locked(p.getX(), p.getZ()));
    }

    @SubscribeEvent
    public static void griefing(EntityMobGriefingEvent event) {
        Entity entity = event.getEntity();
        if (entity == null) return;
        ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(entity.getType());
        if (key != null && MECHS.equals(key.getNamespace())) {
            event.setResult(Event.Result.DENY);
            return;
        }
        if (locked(entity.level(), entity.blockPosition())) event.setResult(Event.Result.DENY);
    }

    @SubscribeEvent
    public static void fluid(BlockEvent.FluidPlaceBlockEvent event) {
        if (locked(event.getLevel(), event.getPos())) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void piston(PistonEvent.Pre event) {
        if (overworld(event.getLevel()) && Locks.nearLock(event.getPos().getX(), event.getPos().getZ(), Locks.PISTON_MARGIN)) {
            event.setCanceled(true);
        }
    }
}
