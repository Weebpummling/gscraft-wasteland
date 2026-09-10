package gscraft.war.world;

import gscraft.war.GscraftWar;
import gscraft.war.WarEvents;
import gscraft.war.entity.Homed;
import gscraft.war.entity.Kit;
import gscraft.war.entity.RankDef;
import gscraft.war.entity.Ranks;
import gscraft.war.faction.FactionMember;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.monster.Drowned;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.MobSpawnEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * The director (review §11 phase 4): places the ambient Dead, Scavengers and soldiers around players by zone,
 * keeps the outposts' garrisons standing, and lets each horror into the ground it belongs to. It replaces In
 * Control's faction rules and the KubeJS area spawner, and it answers the one question both could not: how many
 * stand near *this* player, on *this* ground.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Director {
    public static final int INTERVAL = 200;
    private static final int COUNT_BOX = 48;
    private static final int COUNT_Y = 10;
    private static final int MIN_R = 20;
    private static final int MAX_R = 44;
    private static final int TRIES = 6;
    private static final int HORROR_MIN_R = 32;
    private static final int HORROR_MAX_R = 56;
    private static final int HORROR_CLEAR = 96;
    private static final int GARRISON_WAKE = 128;
    private static final String GARRISON_TAG = "gs_garrison_";

    private static int ticks;
    private static boolean paused;
    private static long passes;
    private static long placed;
    private static long refused;
    private static long nanos;
    private static final Set<ResourceLocation> warnedIds = new HashSet<>();

    private Director() {}

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || paused) return;
        if (++ticks % INTERVAL != 0) return;
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;
        ServerLevel level = server.overworld();
        if (level.players().isEmpty()) return;
        long t0 = System.nanoTime();
        for (ServerPlayer player : level.players()) {
            if (player.isSpectator()) continue;
            ambient(level, player.blockPosition());
            horrors(level, player.blockPosition(), false);
        }
        garrisons(level, null, false);
        nanos += System.nanoTime() - t0;
        passes++;
    }

    public static void setPaused(boolean value) {
        paused = value;
    }

    public static String stats() {
        double ms = passes == 0 ? 0 : nanos / 1e6 / passes;
        return String.format("director %s: %d passes, %d placed, %d refused by spawn checks, %.3f ms per pass",
                paused ? "paused" : "running", passes, placed, refused, ms);
    }

    /** one ambient placement near a player, if the zone's cap allows it */
    public static boolean ambient(ServerLevel level, BlockPos at) {
        Zone zone = Zones.at(at.getX(), at.getZ());
        if (zone == null || zone.exclude() || zone.cap() <= 0) return false;
        if (countOurs(level, at) >= zone.cap()) return false;
        return placeNear(level, at, MIN_R, MAX_R, null) != null;
    }

    public static int countOurs(ServerLevel level, BlockPos at) {
        AABB box = new AABB(at).inflate(COUNT_BOX, COUNT_Y, COUNT_BOX);
        return level.getEntitiesOfClass(Mob.class, box,
                m -> m instanceof FactionMember || m.getTags().contains(WarEvents.PLACED_TAG)).size();
    }

    /**
     * Find standing room 20 to 44 blocks out and place what the zone at that spot calls for. The zone is read at
     * the spot, not at the player, so a player at a border draws from the ground each placement lands on.
     */
    public static Mob placeNear(ServerLevel level, BlockPos at, int minR, int maxR, ResourceLocation forced) {
        RandomSource random = level.getRandom();
        for (int t = 0; t < TRIES; t++) {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double dist = minR + random.nextDouble() * (maxR - minR);
            int x = Mth.floor(at.getX() + Math.cos(angle) * dist);
            int z = Mth.floor(at.getZ() + Math.sin(angle) * dist);
            Zone here = Zones.at(x, z);
            if (here == null || here.exclude()) continue;
            ResourceLocation id = forced != null ? forced : pick(here.spawns(), random);
            EntityType<?> type = type(id);
            if (type == null) continue;
            BlockPos pos = findStand(level, x, at.getY(), z, type == EntityType.DROWNED);
            if (pos == null) continue;
            // a zombie under open sky by day burns; the husk is the same body that does not
            if (type == EntityType.ZOMBIE && level.isDay() && level.canSeeSky(pos)) type = EntityType.HUSK;
            Mob mob = spawn(level, type, pos, here);
            if (mob != null) return mob;
        }
        return null;
    }

    private static EntityType<?> type(ResourceLocation id) {
        if (id == null) return null;
        if (!ForgeRegistries.ENTITY_TYPES.containsKey(id)) {
            if (warnedIds.add(id)) GscraftWar.LOG.warn("[gscraft] zone names unknown entity {}", id);
            return null;
        }
        return ForgeRegistries.ENTITY_TYPES.getValue(id);
    }

    private static ResourceLocation pick(List<SpawnEntry> entries, RandomSource random) {
        int total = 0;
        for (SpawnEntry e : entries) total += Math.max(0, e.weight());
        if (total <= 0) return null;
        int roll = random.nextInt(total);
        for (SpawnEntry e : entries) {
            roll -= Math.max(0, e.weight());
            if (roll < 0) return e.entity();
        }
        return null;
    }

    /** standing room near the reference height: roofs and cellars both count, water only for the drowned */
    private static BlockPos findStand(ServerLevel level, int x, int y0, int z, boolean aquatic) {
        for (int dy = 10; dy >= -24; dy--) {
            BlockPos p = new BlockPos(x, y0 + dy, z);
            if (!level.hasChunkAt(p)) return null;
            BlockState feet = level.getBlockState(p);
            BlockState head = level.getBlockState(p.above());
            if (aquatic) {
                if (feet.getFluidState().is(FluidTags.WATER) && head.getFluidState().is(FluidTags.WATER)) return p;
                continue;
            }
            BlockPos below = p.below();
            if (level.getBlockState(below).isFaceSturdy(level, below, Direction.UP)
                    && feet.getCollisionShape(level, p).isEmpty() && feet.getFluidState().isEmpty()
                    && head.getCollisionShape(level, p.above()).isEmpty()) {
                return p;
            }
        }
        return null;
    }

    private static Mob spawn(ServerLevel level, EntityType<?> type, BlockPos pos, Zone zone) {
        Entity entity = type.create(level);
        if (!(entity instanceof Mob mob)) {
            if (entity != null) entity.discard();
            return null;
        }
        mob.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, level.getRandom().nextFloat() * 360.0F, 0.0F);
        if (!spawnAllowed(mob, level)) {
            refused++;
            return null;
        }
        mob.addTag(WarEvents.PLACED_TAG);
        mob.addTag("gs_director");
        // the zombie family: never a baby, never a chicken jockey
        net.minecraft.world.entity.SpawnGroupData group = mob instanceof Zombie ? new Zombie.ZombieGroupData(false, false) : null;
        mob.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, group, null);
        if (mob instanceof Zombie zombie) dressDead(zombie, zone, level.getRandom());
        level.addFreshEntity(mob);
        placed++;
        return mob;
    }

    /**
     * Placement answers the same questions a natural spawn asks, so anything that suppresses natural spawns - the
     * Magnum Torches first - suppresses the director too. Only an explicit refusal counts: the vanilla default for
     * a monster is darkness, and the Dead are ambient by day.
     */
    static boolean spawnAllowed(Mob mob, ServerLevel level) {
        MobSpawnEvent.PositionCheck check = new MobSpawnEvent.PositionCheck(mob, level, MobSpawnType.NATURAL, null);
        MinecraftForge.EVENT_BUS.post(check);
        if (check.getResult() == Event.Result.DENY) return false;
        // the torches do not listen to Forge's spawn events; they are asked directly
        return !MagnumTorchCompat.refuses(mob, level);
    }

    /** the Dead wear what they died in: the zone names which ranks, the ranks file what each wears */
    private static void dressDead(Zombie zombie, Zone zone, RandomSource random) {
        List<RankDef> pool = new ArrayList<>();
        for (String name : zone.deadRanks()) {
            RankDef r = Ranks.named("dead", name);
            if (r != null) pool.add(r);
        }
        if (pool.isEmpty()) {
            RankDef plain = Ranks.named("dead", zombie instanceof Drowned ? "The Drowned" : "The Dead");
            if (plain != null) pool.add(plain);
        }
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            // the drowned keep the trident vanilla gave them; everyone else starts bare
            if (!(zombie instanceof Drowned && slot == EquipmentSlot.MAINHAND)) zombie.setItemSlot(slot, ItemStack.EMPTY);
            zombie.setDropChance(slot, 0.0F);
        }
        RankDef rank = Kit.issueFrom(zombie, pool, random);
        if (rank != null && !rank.name().equals("The Dead")) zombie.setCustomName(Component.literal(rank.name()));
    }

    /** one attempt at each horror the zone admits; force skips the chance roll, not the night rule */
    public static int horrors(ServerLevel level, BlockPos at, boolean force) {
        Zone zone = Zones.at(at.getX(), at.getZ());
        if (zone == null || zone.exclude()) return 0;
        int n = 0;
        for (HorrorDef horror : zone.horrors()) {
            if (horror.night() && level.isDay()) continue;
            if (!force && level.getRandom().nextDouble() >= horror.chance()) continue;
            EntityType<?> type = type(horror.entity());
            if (type == null) continue;
            AABB near = new AABB(at).inflate(HORROR_CLEAR);
            if (!level.getEntitiesOfClass(Entity.class, near, e -> e.getType() == type).isEmpty()) continue;
            if (placeNear(level, at, HORROR_MIN_R, HORROR_MAX_R, horror.entity()) != null) n++;
        }
        return n;
    }

    /**
     * Keep every garrison standing. A garrison wakes when a player is within 128 blocks of it, counts its members
     * inside the zone, and tops up whatever is missing - at once the first time, then only once the refill time has
     * passed since the last top-up, so an outpost the players have just emptied stays empty for a while.
     *
     * @param only  one zone by name, or null for all
     * @param force skip both the player and the refill-time checks (the test command)
     */
    public static int garrisons(ServerLevel level, String only, boolean force) {
        GarrisonData data = GarrisonData.get(level);
        long now = level.getGameTime();
        int spawned = 0;
        for (Zone zone : Zones.all()) {
            GarrisonDef garrison = zone.garrison();
            if (garrison == null || !zone.hasBox() || (only != null && !only.equals(zone.name()))) continue;
            int cx = zone.centerX();
            int cz = zone.centerZ();
            if (!level.hasChunkAt(new BlockPos(cx, 64, cz))) continue;
            if (!force && level.players().stream().noneMatch(p -> p.distanceToSqr(cx, p.getY(), cz) <= GARRISON_WAKE * GARRISON_WAKE)) {
                continue;
            }
            String tag = GARRISON_TAG + zone.name();
            AABB box = new AABB(zone.x0(), level.getMinBuildHeight(), zone.z0(), zone.x1() + 1, level.getMaxBuildHeight(), zone.z1() + 1)
                    .inflate(16.0D, 0.0D, 16.0D);
            int alive = level.getEntitiesOfClass(Mob.class, box, m -> m.getTags().contains(tag)).size();
            int missing = garrison.count() - alive;
            if (missing <= 0) continue;
            Long last = data.lastRefill(zone.name());
            if (!force && last != null && now - last < garrison.refillTicks()) continue;
            EntityType<?> type = type(garrison.entity());
            if (type == null) continue;
            for (int i = 0; i < missing; i++) {
                BlockPos pos = surfaceIn(level, zone);
                if (pos == null) continue;
                Mob mob = spawn(level, type, pos, zone);
                if (mob == null) continue;
                mob.addTag(tag);
                mob.setPersistenceRequired();
                BlockPos home = new BlockPos(cx, pos.getY(), cz);
                int radius = Math.max(8, zone.halfExtent());
                if (mob instanceof Homed homed) homed.setHome(home, radius);
                else mob.restrictTo(home, radius);
                spawned++;
            }
            data.markRefill(zone.name(), now);
        }
        return spawned;
    }

    private static BlockPos surfaceIn(ServerLevel level, Zone zone) {
        RandomSource random = level.getRandom();
        for (int t = 0; t < 12; t++) {
            int x = zone.x0() + random.nextInt(Math.max(1, zone.x1() - zone.x0()));
            int z = zone.z0() + random.nextInt(Math.max(1, zone.z1() - zone.z0()));
            if (!level.hasChunkAt(new BlockPos(x, 64, z))) continue;
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            BlockPos p = new BlockPos(x, y, z);
            BlockPos below = p.below();
            if (level.getBlockState(below).isFaceSturdy(level, below, Direction.UP) && level.getBlockState(p).getFluidState().isEmpty()) {
                return p;
            }
        }
        return null;
    }
}
