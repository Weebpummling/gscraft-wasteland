package gscraft.war.world;

import gscraft.war.GscraftWar;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.item.PrimedTnt;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Block destruction by blasts (owner, 2026-09-13): on, for wooden blocks only. Superb Warfare's blasts - the vehicles'
 * guns and rockets, the fire missions' shells, grenades, C4 - take blocks only with explosion_destroy on in the
 * server config (tools/armour_override.py sets it); this keeps every non-wooden block out of any blast's list, so
 * a shell wrecks a shed and a fence and leaves stone, brick and earth. Vanilla TNT is left as it is. The block
 * tag gscraft:wooden (data/gscraft/tags/blocks) says what counts; the vehicles' collision list is the same tag.
 * Bullets never break blocks (allow_projectile_destroy_glass off).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class BlastRule {
    private BlastRule() {}

    public static final TagKey<Block> WOODEN = BlockTags.create(new ResourceLocation(GscraftWar.MODID, "wooden"));

    @SubscribeEvent
    public static void detonate(ExplosionEvent.Detonate event) {
        Level level = event.getLevel();
        if (level.isClientSide || event.getExplosion().getExploder() instanceof PrimedTnt) return;
        event.getAffectedBlocks().removeIf(p -> !level.getBlockState(p).is(WOODEN));
    }
}
