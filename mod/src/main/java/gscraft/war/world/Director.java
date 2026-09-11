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
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Drowned;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
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
 * The director (review §11 phase 4): places the ambient Dead, Scavengers and soldiers around players by zone, keeps
 * the outposts' garrisons and each zone's unique creature standing, and lets each horror into the ground it belongs
 * to. It replaces In Control's faction rules and the KubeJS area spawner.
 *
 * Placement is layered by the kind of ground (see {@link Env}): a player in the open gets a thinner scatter further
 * out, a player inside a building or underground gets a denser one close by, on the same kind of ground, counted
 * against its own cap. The first version looked from ten blocks above the player's feet down to twenty-four below
 * and took the highest standing room it found, so a player in the street drew the Dead onto roofs and into cellars,
 * and every one of them counted against the street's cap; {@link #survey} measures both, side by side.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Director {
    public static final int INTERVAL = 200;
    private static final int TRIES = 10;
    private static final int HORROR_CLEAR = 96;
    private static final int GARRISON_WAKE = 128;
    private static final String GARRISON_TAG = "gs_garrison_";
    private static final String LAIR_TAG = "gs_lair_";
    /** marks a creature placed behind shut doors, out of the player's reach (owner, 2026-09-10: a small share) */
    public static final String SEALED_TAG = "gs_sealed";
    /** the share of indoor and underground placements allowed to skip the walk-to-the-player rule */
    private static final float SEALED_SHARE = 0.2F;
    /** a zone entry naming this places a zombie horse with one of the Dead riding it */
    public static final ResourceLocation RIDER = new ResourceLocation(GscraftWar.MODID, "rider");

    private static int ticks;
    private static boolean paused;
    private static long passes;
    private static long placed;
    private static long refused;
    private static long swept;
    /** an ambient placement further than this from every player is taken back */
    private static final int SWEEP = 160;
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
        swept += sweep(level);
        nanos += System.nanoTime() - t0;
        passes++;
    }

    /** the director's own despawn: ambient placements (not garrisons, lairs, waves or guards) beyond SWEEP of everyone */
    static int sweep(ServerLevel level) {
        int n = 0;
        java.util.List<Mob> doomed = new java.util.ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (!(e instanceof Mob mob) || !mob.getTags().contains("gs_director")) continue;
            if (mob.getTags().stream().anyMatch(t -> t.startsWith(GARRISON_TAG) || t.startsWith(LAIR_TAG) || t.startsWith("gs_wave"))) continue;
            boolean near = false;
            for (ServerPlayer p : level.players()) {
                if (p.distanceToSqr(mob) <= (double) SWEEP * SWEEP) {
                    near = true;
                    break;
                }
            }
            if (!near) doomed.add(mob);
        }
        for (Mob mob : doomed) {
            mob.discard();
            n++;
        }
        return n;
    }

    public static void setPaused(boolean value) {
        paused = value;
    }

    public static String stats() {
        double ms = passes == 0 ? 0 : nanos / 1e6 / passes;
        return String.format("director %s: %d passes, %d placed, %d refused by spawn checks, %d swept back, %.3f ms per pass",
                paused ? "paused" : "running", passes, placed, refused, swept, ms);
    }

    // ---- ambient placement

    /** one placement near a player, if the zone's cap for the ground the player stands on allows it */
    public static boolean ambient(ServerLevel level, BlockPos at) {
        Zone zone = Zones.at(at.getX(), at.getZ());
        if (zone == null || zone.exclude() || zone.cap() <= 0) return false;
        Env env = Env.at(level, at);
        int cap = capFor(zone, env);
        int room = cap - countOurs(level, at, env);
        if (room < Math.min(2, cap)) return false;    // never a lone straggler: wait until a group fits
        boolean sealed = rollSealed(level, env) && countSealed(level, at, env) < sealedCap(cap);
        Mob first = placeNear(level, at, env, null, sealed);
        if (first == null) return false;
        // the rest of the group, the same kind, a few blocks from the first (owner, 2026-09-10: groups of 2-4)
        int size = Math.min(room, zone.groupSize(env, level.getRandom()));
        ResourceLocation kind = ForgeRegistries.ENTITY_TYPES.getKey(first.getType());
        boolean rider = first.getVehicle() != null;
        for (int i = 1; i < size; i++) {
            Mob next = placeBeside(level, first.blockPosition(), env, rider ? RIDER : kind, sealed);
            if (next == null) break;
        }
        return true;
    }

    /** one more of the same kind within a few blocks of a placed creature, on the same kind of ground */
    static Mob placeBeside(ServerLevel level, BlockPos beside, Env env, ResourceLocation kind, boolean allowSealed) {
        RandomSource random = level.getRandom();
        for (int t = 0; t < TRIES; t++) {
            int x = beside.getX() + random.nextInt(9) - 4;
            int z = beside.getZ() + random.nextInt(9) - 4;
            Zone here = Zones.at(x, z);
            if (here == null || here.exclude() || Loop.suppressedAt(level, x, z)) continue;
            boolean rider = RIDER.equals(kind);
            EntityType<?> type = rider ? EntityType.ZOMBIE_HORSE : type(kind);
            if (type == null) return null;
            boolean aquatic = type == EntityType.DROWNED;
            BlockPos pos = findStand(level, x, beside.getY(), z, env, aquatic);
            if (pos == null) continue;
            if (env != Env.OPEN && !aquatic && !allowSealed && !reaches(level, pos, beside)) continue;
            if (type == EntityType.ZOMBIE && level.isDay() && env == Env.OPEN) type = EntityType.HUSK;
            Mob mob = rider ? spawnRider(level, pos, here) : spawn(level, type, pos, here);
            if (mob != null) return mob;
        }
        return null;
    }

    /** whether this placement may land behind shut doors: indoors or underground, one time in five */
    public static boolean rollSealed(ServerLevel level, Env env) {
        return env != Env.OPEN && level.getRandom().nextFloat() < SEALED_SHARE;
    }

    /** creatures behind shut doors are held to a quarter of the cap, so they never starve the ones that can reach */
    public static int sealedCap(int cap) {
        return Math.max(1, cap / 4);
    }

    public static int countSealed(ServerLevel level, BlockPos at, Env env) {
        AABB box = new AABB(at).inflate(env.countBox, env.countY, env.countBox);
        return level.getEntitiesOfClass(Mob.class, box,
                m -> m.getTags().contains(SEALED_TAG) && Env.at(level, m.blockPosition()) == env).size();
    }

    public static int capFor(Zone zone, Env env) {
        return Math.max(1, (int) Math.round(zone.cap() * env.capScale));
    }

    /** the director's own creatures near a point, on the same kind of ground only */
    public static int countOurs(ServerLevel level, BlockPos at, Env env) {
        AABB box = new AABB(at).inflate(env.countBox, env.countY, env.countBox);
        return level.getEntitiesOfClass(Mob.class, box,
                m -> (m instanceof FactionMember || m.getTags().contains(WarEvents.PLACED_TAG))
                        && Env.at(level, m.blockPosition()) == env).size();
    }

    /**
     * Find standing room on the same kind of ground as the reference point and place what the zone at that spot
     * draws for that ground. The zone is read where the placement lands.
     */
    public static Mob placeNear(ServerLevel level, BlockPos at, Env env, ResourceLocation forced) {
        return placeNear(level, at, env, forced, false);
    }

    /** @param allowSealed indoors or underground, the placement may stand where it cannot walk to the player */
    public static Mob placeNear(ServerLevel level, BlockPos at, Env env, ResourceLocation forced, boolean allowSealed) {
        RandomSource random = level.getRandom();
        for (int t = 0; t < TRIES; t++) {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double dist = env.minR + random.nextDouble() * (env.maxR - env.minR);
            int x = Mth.floor(at.getX() + Math.cos(angle) * dist);
            int z = Mth.floor(at.getZ() + Math.sin(angle) * dist);
            Zone here = Zones.at(x, z);
            if (here == null || here.exclude() || Loop.suppressedAt(level, x, z)) continue;
            ResourceLocation id = forced != null ? forced : pick(here.spawnsFor(env), random, level.isDay());
            if (id == null) continue;
            boolean rider = RIDER.equals(id);
            if (rider && env != Env.OPEN) continue;
            EntityType<?> type = rider ? EntityType.ZOMBIE_HORSE : type(id);
            if (type == null) continue;
            boolean aquatic = type == EntityType.DROWNED;
            BlockPos pos = findStand(level, x, at.getY(), z, env, aquatic);
            if (pos == null) continue;
            boolean shut = env != Env.OPEN && !aquatic && !reaches(level, pos, at);
            if (shut && !allowSealed) continue;
            // a zombie under open sky by day burns; the husk is the same body that does not
            if (type == EntityType.ZOMBIE && level.isDay() && env == Env.OPEN) type = EntityType.HUSK;
            Mob mob = rider ? spawnRider(level, pos, here) : spawn(level, type, pos, here);
            if (mob != null) {
                if (shut) mob.addTag(SEALED_TAG);
                return mob;
            }
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

    private static ResourceLocation pick(List<SpawnEntry> entries, RandomSource random, boolean day) {
        int total = 0;
        for (SpawnEntry e : entries) {
            if (!(e.night() && day)) total += Math.max(0, e.weight());
        }
        if (total <= 0) return null;
        int roll = random.nextInt(total);
        for (SpawnEntry e : entries) {
            if (e.night() && day) continue;
            roll -= Math.max(0, e.weight());
            if (roll < 0) return e.entity();
        }
        return null;
    }

    private static Zombie probe;

    /**
     * Inside and underground, placement has to be able to walk to the player. Measured 2026-09-10: in the RUAF post
     * 33 of 34 indoor placements stood behind shut doors, filling the cap with creatures nobody would meet.
     * The probe is a zombie that is never added to the world; only its path finder is used.
     */
    static boolean reaches(ServerLevel level, BlockPos from, BlockPos to) {
        if (probe == null || probe.level() != level) {
            probe = EntityType.ZOMBIE.create(level);
            if (probe == null) return true;
            var follow = probe.getAttribute(Attributes.FOLLOW_RANGE);
            if (follow != null) follow.setBaseValue(64.0D);
        }
        probe.moveTo(from.getX() + 0.5D, from.getY(), from.getZ() + 0.5D, 0.0F, 0.0F);
        probe.setOnGround(true);
        Path path = probe.getNavigation().createPath(to, 1);
        return path != null && path.canReach();
    }

    /** standing room nearest the reference height, on the same kind of ground; water only for the drowned */
    static BlockPos findStand(ServerLevel level, int x, int y0, int z, Env env, boolean aquatic) {
        int reach = Math.max(env.dyUp, env.dyDown);
        for (int d = 0; d <= reach; d++) {
            for (int sign = -1; sign <= 1; sign += 2) {
                if (d == 0 && sign == 1) continue;
                int dy = d * sign;
                if (dy > env.dyUp || -dy > env.dyDown) continue;
                BlockPos p = new BlockPos(x, y0 + dy, z);
                if (!level.hasChunkAt(p)) return null;
                if (!standable(level, p, aquatic)) continue;
                if (!aquatic && Env.at(level, p) != env) continue;
                return p;
            }
        }
        return null;
    }

    /** the nearest standing room to a point, within three blocks across and two up or down; null when there is none */
    public static BlockPos nearestStand(ServerLevel level, BlockPos at) {
        if (standable(level, at, false)) return at;
        for (int r = 1; r <= 3; r++) {
            for (int dy = -2; dy <= 2; dy++) {
                for (int dx = -r; dx <= r; dx++) {
                    for (int dz = -r; dz <= r; dz++) {
                        BlockPos p = at.offset(dx, dy, dz);
                        if (level.hasChunkAt(p) && standable(level, p, false)) return p;
                    }
                }
            }
        }
        return null;
    }

    /** the first version's search, kept only so {@link #survey} can measure what the layered one changed */
    static BlockPos legacyStand(ServerLevel level, int x, int y0, int z) {
        for (int dy = 10; dy >= -24; dy--) {
            BlockPos p = new BlockPos(x, y0 + dy, z);
            if (!level.hasChunkAt(p)) return null;
            if (standable(level, p, false)) return p;
        }
        return null;
    }

    private static boolean standable(ServerLevel level, BlockPos p, boolean aquatic) {
        BlockState feet = level.getBlockState(p);
        BlockState head = level.getBlockState(p.above());
        if (aquatic) return feet.getFluidState().is(FluidTags.WATER) && head.getFluidState().is(FluidTags.WATER);
        BlockPos below = p.below();
        return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP)
                && feet.getCollisionShape(level, p).isEmpty() && feet.getFluidState().isEmpty()
                && head.getCollisionShape(level, p.above()).isEmpty();
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
        // vanilla would despawn it at random beyond 32 blocks; the director keeps it and sweeps it itself past SWEEP
        mob.setPersistenceRequired();
        // the zombie family: never a baby, never a chicken jockey
        SpawnGroupData group = mob instanceof Zombie ? new Zombie.ZombieGroupData(false, false) : null;
        mob.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, group, null);
        if (mob instanceof Zombie zombie) {
            ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(type);
            if (key != null && GscraftWar.MODID.equals(key.getNamespace())) {
                clearGear(zombie);   // the mod's own Dead are their own look, not a dressed rank
            } else {
                dressDead(zombie, zone, level.getRandom());
            }
        }
        level.addFreshEntity(mob);
        placed++;
        return mob;
    }

    /** the Dead's cavalry (entities-v8 §3.1): a zombie horse, one of the Dead in the saddle */
    private static Mob spawnRider(ServerLevel level, BlockPos pos, Zone zone) {
        Mob horse = spawn(level, EntityType.ZOMBIE_HORSE, pos, zone);
        if (horse == null) return null;
        Mob rider = spawn(level, EntityType.ZOMBIE, pos, zone);
        if (rider != null) {
            rider.startRiding(horse, true);
            rider.setCustomName(Component.literal("Rider"));
        }
        return horse;
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

    private static void clearGear(Zombie zombie) {
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            zombie.setItemSlot(slot, ItemStack.EMPTY);
            zombie.setDropChance(slot, 0.0F);
        }
    }

    /** the Dead wear what they died in: the zone names which ranks, the ranks file what each wears */
    private static void dressDead(Zombie zombie, Zone zone, RandomSource random) {
        List<RankDef> pool = new ArrayList<>();
        for (String name : zone.deadRanks()) {
            RankDef r = Ranks.named("dead", name);
            if (r != null) pool.add(r);
        }
        if (pool.isEmpty() || zombie instanceof Drowned) {
            pool.clear();
            RankDef plain = Ranks.named("dead", zombie instanceof Drowned ? drownedRank(zone) : "The Dead");
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

    private static String drownedRank(Zone zone) {
        return zone.deadRanks().contains("Drowned Patrol") ? "Drowned Patrol" : "The Drowned";
    }

    // ---- horrors

    /** one attempt at each horror the zone admits; force skips the chance roll, not the night or ground rules */
    public static int horrors(ServerLevel level, BlockPos at, boolean force) {
        Zone zone = Zones.at(at.getX(), at.getZ());
        if (zone == null || zone.exclude()) return 0;
        Env env = Env.at(level, at);
        int n = 0;
        for (HorrorDef horror : zone.horrors()) {
            if (horror.night() && level.isDay()) continue;
            if (!horror.envs().isEmpty() && !horror.envs().contains(env)) continue;
            if (!force && level.getRandom().nextDouble() >= horror.chance()) continue;
            EntityType<?> type = type(horror.entity());
            if (type == null) continue;
            AABB near = new AABB(at).inflate(HORROR_CLEAR);
            if (!level.getEntitiesOfClass(Entity.class, near, e -> e.getType() == type).isEmpty()) continue;
            if (placeNear(level, at, env, horror.entity()) != null) n++;
        }
        return n;
    }

    // ---- garrisons and lairs

    /**
     * Keep every garrison and lair standing. Each wakes when a player is within 128 blocks, counts its members inside
     * the zone, and tops up whatever is missing - at once the first time, then only once its refill time has passed
     * since the last top-up. A lair is the zone's unique creature: one, and a long wait before it returns.
     *
     * @param only  one zone by name, or null for all
     * @param force skip both the player and the refill-time checks (the test command)
     */
    public static int garrisons(ServerLevel level, String only, boolean force) {
        GarrisonData data = GarrisonData.get(level);
        int spawned = 0;
        for (Zone zone : Zones.all()) {
            if (!zone.hasBox() || (only != null && !only.equals(zone.name()))) continue;
            if (zone.garrison() != null) spawned += keep(level, data, zone, zone.garrison(), GARRISON_TAG, "", force);
            if (zone.lair() != null) spawned += keep(level, data, zone, zone.lair(), LAIR_TAG, "lair:", force);
        }
        return spawned;
    }

    private static int keep(ServerLevel level, GarrisonData data, Zone zone, GarrisonDef def, String tagPrefix,
                            String dataPrefix, boolean force) {
        int cx = zone.centerX();
        int cz = zone.centerZ();
        if (!level.hasChunkAt(new BlockPos(cx, 64, cz))) return 0;
        if (!force && level.players().stream().noneMatch(p -> p.distanceToSqr(cx, p.getY(), cz) <= GARRISON_WAKE * GARRISON_WAKE)) {
            return 0;
        }
        String tag = tagPrefix + zone.name();
        AABB box = new AABB(zone.x0(), level.getMinBuildHeight(), zone.z0(), zone.x1() + 1, level.getMaxBuildHeight(), zone.z1() + 1)
                .inflate(16.0D, 0.0D, 16.0D);
        int alive = level.getEntitiesOfClass(Mob.class, box, m -> m.isAlive() && m.getTags().contains(tag)).size();
        int missing = def.count() - alive;
        if (missing <= 0) return 0;
        long now = level.getGameTime();
        Long last = data.lastRefill(dataPrefix + zone.name());
        if (!force && last != null && now - last < def.refillTicks()) return 0;
        EntityType<?> type = type(def.entity());
        if (type == null) return 0;
        int spawned = 0;
        for (int i = 0; i < missing; i++) {
            BlockPos pos = groundIn(level, zone);
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
        data.markRefill(dataPrefix + zone.name(), now);
        return spawned;
    }

    /**
     * Ground-floor standing room inside a zone: the lowest spot in a column that is not underground. The top of the
     * column is a roof as often as not - the garrison of a brick block belongs in the block, not on it.
     */
    private static BlockPos groundIn(ServerLevel level, Zone zone) {
        RandomSource random = level.getRandom();
        for (int t = 0; t < 48; t++) {
            int x = zone.x0() + random.nextInt(Math.max(1, zone.x1() - zone.x0()));
            int z = zone.z0() + random.nextInt(Math.max(1, zone.z1() - zone.z0()));
            if (!level.hasChunkAt(new BlockPos(x, 64, z))) continue;
            BlockPos p = groundAt(level, x, z);
            if (p != null) return p;
        }
        // a zone of water and unloaded ground: the centre column, then nothing
        if (level.hasChunkAt(new BlockPos(zone.centerX(), 64, zone.centerZ()))) return groundAt(level, zone.centerX(), zone.centerZ());
        return null;
    }

    /** the lowest standing room in a column that is not underground: a building's ground floor, or the ground itself */
    static BlockPos groundAt(ServerLevel level, int x, int z) {
        int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        for (int y = Math.max(level.getMinBuildHeight() + 1, top - 60); y <= top; y++) {
            BlockPos p = new BlockPos(x, y, z);
            if (standable(level, p, false) && Env.at(level, p) != Env.UNDERGROUND) return p;
        }
        return null;
    }

    /**
     * The nearest ground-floor room to a column: the lowest standing room that is not underground, inside, with a
     * floor of at least twenty indoor standing spots around it, so a sealed pocket in a foundation does not count.
     * The survey's indoor reference points come from here.
     */
    public static BlockPos groundRoom(ServerLevel level, int cx, int cz, int radius) {
        for (int r = 0; r <= radius; r += 2) {
            for (int dx = -r; dx <= r; dx += 2) {
                for (int dz = -r; dz <= r; dz += 2) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
                    int x = cx + dx;
                    int z = cz + dz;
                    if (!level.hasChunkAt(new BlockPos(x, 64, z))) continue;
                    int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                    for (int y = Math.max(level.getMinBuildHeight() + 1, top - 60); y <= top; y++) {
                        BlockPos p = new BlockPos(x, y, z);
                        if (!standable(level, p, false)) continue;
                        Env env = Env.at(level, p);
                        if (env == Env.UNDERGROUND) continue;
                        if (env == Env.INDOOR && floorAround(level, p) >= 20) return p;
                        break;
                    }
                }
            }
        }
        return null;
    }

    private static int floorAround(ServerLevel level, BlockPos at) {
        int n = 0;
        for (int dx = -4; dx <= 4; dx++) {
            for (int dz = -4; dz <= 4; dz++) {
                BlockPos p = at.offset(dx, 0, dz);
                if (standable(level, p, false) && Env.at(level, p) == Env.INDOOR) n++;
            }
        }
        return n;
    }

    // ---- the survey

    /** what placement from one reference point produces, measured without placing anything */
    public record Survey(Env reference, int samples, int found, int open, int indoor, int underground,
                        double meanRise, int visible, int reachable, int checked, int behindDoors) {
        public String describe(String label) {
            return String.format("%s: found %d of %d; open %d, indoor %d, underground %d; same ground as you %d%%; "
                            + "mean height from you %.1f; visible %d%%; walkable to you %d of %d; behind shut doors %d",
                    label, found, samples, open, indoor, underground,
                    found == 0 ? 0 : Math.round(100.0 * sameAs(reference) / found), meanRise,
                    found == 0 ? 0 : Math.round(100.0 * visible / found), reachable, checked, behindDoors);
        }

        private int sameAs(Env env) {
            return switch (env) {
                case OPEN -> open;
                case INDOOR -> indoor;
                case UNDERGROUND -> underground;
            };
        }
    }

    /**
     * Sample placement spots around a reference point with either search - the first version's or the layered one -
     * and classify each: the kind of ground, the height from the reference, whether it can be seen from the
     * reference's eyes, and (for the first 40) whether one of the Dead standing there can walk to it.
     */
    public static Survey survey(ServerLevel level, BlockPos ref, int samples, boolean legacy) {
        Env env = Env.at(level, ref);
        RandomSource random = level.getRandom();
        Zombie probe = EntityType.ZOMBIE.create(level);
        if (probe == null) return new Survey(env, samples, 0, 0, 0, 0, 0, 0, 0, 0, 0);
        var follow = probe.getAttribute(Attributes.FOLLOW_RANGE);
        if (follow != null) follow.setBaseValue(64.0D);
        int found = 0, open = 0, indoor = 0, under = 0, visible = 0, reachable = 0, checked = 0, behind = 0;
        double rise = 0;
        Vec3 eyes = Vec3.atBottomCenterOf(ref).add(0, 1.62D, 0);
        for (int i = 0; i < samples; i++) {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double dist = legacy ? 20 + random.nextDouble() * 24 : env.minR + random.nextDouble() * (env.maxR - env.minR);
            int x = Mth.floor(ref.getX() + Math.cos(angle) * dist);
            int z = Mth.floor(ref.getZ() + Math.sin(angle) * dist);
            Zone here = Zones.at(x, z);
            if (here == null || here.exclude()) continue;
            BlockPos pos = legacy ? legacyStand(level, x, ref.getY(), z) : findStand(level, x, ref.getY(), z, env, false);
            if (pos == null) continue;
            if (!legacy && env != Env.OPEN && !reaches(level, pos, ref)) {
                behind++;
                continue;
            }
            found++;
            switch (Env.at(level, pos)) {
                case OPEN -> open++;
                case INDOOR -> indoor++;
                case UNDERGROUND -> under++;
            }
            rise += Math.abs(pos.getY() - ref.getY());
            Vec3 target = Vec3.atBottomCenterOf(pos).add(0, 1.5D, 0);
            if (level.clip(new ClipContext(eyes, target, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, probe)).getType() == HitResult.Type.MISS) {
                visible++;
            }
            if (checked < 40) {
                probe.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, 0.0F, 0.0F);
                probe.setOnGround(true);
                Path path = probe.getNavigation().createPath(ref, 1);
                checked++;
                if (path != null && path.canReach()) reachable++;
            }
        }
        probe.discard();
        return new Survey(env, samples, found, open, indoor, under, found == 0 ? 0 : rise / found, visible, reachable, checked, behind);
    }
}
