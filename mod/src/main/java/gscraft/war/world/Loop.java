package gscraft.war.world;

import gscraft.war.GscraftWar;
import gscraft.war.WarEvents;
import gscraft.war.entity.Kit;
import gscraft.war.entity.RankDef;
import gscraft.war.entity.Ranks;
import gscraft.war.entity.Scavenger;
import gscraft.war.entity.Soldier;
import gscraft.war.world.SiteData.Phase;
import gscraft.war.world.SiteData.Progress;
import gscraft.war.world.SiteData.State;
import gscraft.war.world.Sites.CampDef;
import gscraft.war.world.Sites.SiteDef;
import gscraft.war.world.Sites.WaveEntry;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * The strongpoint loop (design §6, fold-in review F1–F4, F12): the ladder unknown → scouted → looted → held →
 * defended, the assault (5 minutes, six waves every 45 s from the site's edges), the fortify clock (40 minutes of
 * online time, the warning in its last ten, the title at two), the counterattack (three waves at the camp's approach
 * from the attacking site's side), the loss check (five attackers in the camp square for 30 s: lost, the site stays
 * held, another clock), the site guard (a garrison at the anchor: Recruits and Guard Villagers, doubled on defended),
 * and one contested site at a time. Clocks count online ticks only.
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Loop {
    public static final String WAVE_TAG = "gs_wave";
    public static final String GUARD_TAG = "gscraft_siteguard_";
    static final int ASSAULT_TICKS = 6000;
    static final int ASSAULT_WAVES = 6;
    static final int WAVE_GAP = 900;
    static final int FORTIFY_TICKS = 48000;
    static final int WARNING_TICKS = 12000;
    static final int TWO_MINUTES = 2400;
    static final int DEFENCE_WAVES = 3;
    static final int STRAGGLER_TICKS = 9600;
    static final int LOSS_COUNT = 5;
    static final int LOSS_TICKS = 600;
    static final int GUARD_EVERY = 600;
    static final int GUARD_TARGET = 6;
    /** the site guard: two recruits, a bowman, a shieldman, two Guard Villagers */
    private static final List<String> GUARD = List.of("recruits:recruit", "recruits:recruit", "recruits:bowman",
            "recruits:recruit_shieldman", "guardvillagers:guard", "guardvillagers:guard");

    /** true: clocks run with nobody online (tests only) */
    private static volatile boolean freeClock;
    private static int ticks;
    private static final Map<String, ServerBossEvent> bars = new HashMap<>();
    /** nobody within this of the fight: the clocks freeze; after AWAY_TICKS the wave is taken back */
    static final int AWAY_RANGE = 128;
    static final int AWAY_TICKS = 1200;
    private static final Map<String, Integer> awayTicks = new HashMap<>();

    private Loop() {}

    public static void setFreeClock(boolean value) {
        freeClock = value;
    }

    public static boolean freeClock() {
        return freeClock;
    }

    /** a held or defended site keeps its ambient hostiles off (F4) */
    public static boolean suppressedAt(ServerLevel level, int x, int z) {
        if (Sites.all().isEmpty()) return false;
        SiteData data = SiteData.get(level);
        for (SiteDef site : Sites.all().values()) {
            if (!site.contains(x, z)) continue;
            State s = data.progress(site.id()).state;
            return s == State.HELD || s == State.DEFENDED;
        }
        return false;
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || Sites.all().isEmpty()) return;
        ServerLevel level = server.overworld();
        if (!freeClock && server.getPlayerList().getPlayers().isEmpty()) return;
        SiteData data = SiteData.get(level);
        data.online++;
        if (++ticks % 20 != 0) return;
        data.setDirty();
        for (SiteDef site : Sites.all().values()) {
            Progress p = data.progress(site.id());
            switch (p.phase) {
                case ASSAULT -> assault(level, data, site, p);
                case FORTIFY -> fortify(level, data, site, p);
                case COUNTER -> counter(level, data, site, p);
                default -> { }
            }
            if ((p.state == State.HELD || p.state == State.DEFENDED) && ticks % GUARD_EVERY == 0) keepGuard(level, site, p);
        }
    }

    // ---- the ladder

    /** the next rung; refused when a rung would be skipped or another site is contested. Returns a message. */
    public static String advance(ServerLevel level, SiteDef site, State to) {
        SiteData data = SiteData.get(level);
        Progress p = data.progress(site.id());
        if (to == State.UNKNOWN) {
            reset(level, data, site, p);
            return site.id() + " reset";
        }
        if (to.ordinal() != p.state.ordinal() + 1) {
            return site.id() + " is " + p.state.name().toLowerCase(Locale.ROOT) + "; the next rung is "
                    + State.values()[Math.min(p.state.ordinal() + 1, State.DEFENDED.ordinal())].name().toLowerCase(Locale.ROOT);
        }
        switch (to) {
            case HELD -> {
                if (!data.contested.isEmpty() && !data.contested.equals(site.id())) {
                    return "refused: " + data.contested + " is still contested";
                }
                data.contested = site.id();
                p.phase = Phase.ASSAULT;
                p.deadline = data.online + ASSAULT_TICKS;
                p.nextWave = data.online;
                p.wave = 0;
                data.setDirty();
                title(level.getServer(), Component.literal(site.name()), Component.translatable("gscraft.title.hold"));
                return site.id() + ": the assault begins, five minutes, " + ASSAULT_WAVES + " waves";
            }
            case DEFENDED -> {
                return "refused: defended is won at the gate, not set by hand";
            }
            default -> {
                setState(level, data, site, p, to);
                return site.id() + " is " + to.name().toLowerCase(Locale.ROOT);
            }
        }
    }

    private static void setState(ServerLevel level, SiteData data, SiteDef site, Progress p, State to) {
        p.state = to;
        data.setDirty();
        Stages.add(level.getServer(), site.id() + "_" + to.name().toLowerCase(Locale.ROOT));
    }

    private static void reset(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        for (State s : State.values()) Stages.remove(level.getServer(), site.id() + "_" + s.name().toLowerCase(Locale.ROOT));
        Stages.remove(level.getServer(), site.id() + "_lost");
        if (data.contested.equals(site.id())) data.contested = "";
        discardWave(level, site);
        for (Mob m : level.getEntitiesOfClass(Mob.class, around(site, 64), m -> m.getTags().contains(GUARD_TAG + site.id()))) m.discard();
        dropBar(site);
        Progress fresh = new Progress();
        p.state = fresh.state;
        p.lost = false;
        p.phase = Phase.NONE;
        p.wave = 0;
        p.warned = false;
        p.twoMinutes = false;
        p.lossTicks = 0;
        p.guardTarget = 0;
        data.setDirty();
    }

    /** the operator's clock: the phase's end lands this many seconds from now; in the counterattack, the next wave until all three are out */
    public static String clock(ServerLevel level, SiteDef site, int seconds) {
        SiteData data = SiteData.get(level);
        Progress p = data.progress(site.id());
        long at = data.online + seconds * 20L;
        switch (p.phase) {
            case ASSAULT, FORTIFY -> p.deadline = at;
            case COUNTER -> {
                if (p.wave < DEFENCE_WAVES) p.nextWave = at;
                else p.deadline = at;
            }
            default -> {
                return site.id() + " has no clock running";
            }
        }
        data.setDirty();
        return site.id() + ": " + p.phase.name().toLowerCase(Locale.ROOT) + " clock set to " + seconds + " s";
    }

    // ---- the assault

    /**
     * Nobody near the fight (players, or the director's phantoms): the phase's clocks move with the time, so nothing
     * is missed, and a wave left ticking for a minute with nobody there is taken back - the next wave comes when
     * someone does. A server with nobody on it at all is not "away": the clocks stop by themselves then.
     */
    private static boolean away(ServerLevel level, SiteData data, SiteDef site, Progress p, int cx, int cz) {
        if (Director.presence(level).isEmpty() || Director.anyoneWithin(level, cx + 0.5D, cz + 0.5D, AWAY_RANGE)) {
            awayTicks.remove(site.id());
            return false;
        }
        p.deadline += 20;
        p.nextWave += 20;
        int t = awayTicks.merge(site.id(), 20, Integer::sum);
        if (t >= AWAY_TICKS && waveCount(level, site) > 0) {
            discardWave(level, site);
            GscraftWar.LOG.info("[gscraft] {}: nobody within {} for a minute, the wave is taken back; the clock waits", site.id(), AWAY_RANGE);
        }
        return true;
    }

    private static int waveCount(ServerLevel level, SiteDef site) {
        String tag = WAVE_TAG + "_" + site.id();
        int n = 0;
        for (Entity e : level.getAllEntities()) {
            if (e.getTags().contains(tag)) n++;
        }
        return n;
    }

    private static void assault(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        if (away(level, data, site, p, site.anchorX(), site.anchorZ())) return;
        if (p.wave < ASSAULT_WAVES && data.online >= p.nextWave) {
            int placed = sendWave(level, site, site.assault().get(p.wave), edgePoints(level, site), scaleInside(level, site));
            p.wave++;
            p.nextWave = data.online + WAVE_GAP;
            GscraftWar.LOG.info("[gscraft] {} assault wave {} of {}: {} placed", site.id(), p.wave, ASSAULT_WAVES, placed);
        }
        long left = p.deadline - data.online;
        bar(level.getServer(), site, site.name() + " — hold — " + mmss(left), (float) left / ASSAULT_TICKS, BossEvent.BossBarColor.RED);
        if (left <= 0) {
            dropBar(site);
            setState(level, data, site, p, State.HELD);
            p.phase = Phase.FORTIFY;
            p.deadline = data.online + FORTIFY_TICKS;
            p.warned = false;
            p.twoMinutes = false;
            p.guardTarget = GUARD_TARGET;
            data.setDirty();
            keepGuard(level, site, p);
            title(level.getServer(), Component.literal(site.name() + " IS OURS"), Component.empty());
            GscraftWar.LOG.info("[gscraft] {} held; the fortify clock runs {} minutes of online time", site.id(), FORTIFY_TICKS / 1200);
        }
    }

    // ---- the fortify clock

    private static void fortify(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        long left = p.deadline - data.online;
        if (!p.warned && left <= WARNING_TICKS) {
            p.warned = true;
            level.getServer().getPlayerList().broadcastSystemMessage(Component.translatable("gscraft.line.tune.warning"), false);
        }
        if (!p.twoMinutes && left <= TWO_MINUTES) {
            p.twoMinutes = true;
            title(level.getServer(), Component.translatable("gscraft.title.coming"), Component.translatable("gscraft.title.coming.sub"));
        }
        if (left <= 0) {
            p.phase = Phase.COUNTER;
            p.wave = 0;
            p.nextWave = data.online;
            p.lossTicks = 0;
            data.setDirty();
            GscraftWar.LOG.info("[gscraft] {} counterattack: {} waves at the {} approach", site.id(), DEFENCE_WAVES, site.approach());
        }
    }

    // ---- the counterattack

    private static void counter(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        CampDef camp = Sites.camp();
        if (camp == null) return;
        if (away(level, data, site, p, (camp.sx0() + camp.sx1()) / 2, (camp.sz0() + camp.sz1()) / 2)) return;
        if (p.wave < DEFENCE_WAVES && data.online >= p.nextWave) {
            int[] at = camp.approaches().getOrDefault(site.approach(), camp.approaches().values().iterator().next());
            int placed = sendWave(level, site, site.defence().get(p.wave), List.of(new BlockPos(at[0], 0, at[1])), scaleOnline(level));
            p.wave++;
            p.nextWave = data.online + WAVE_GAP;
            if (p.wave == DEFENCE_WAVES) p.deadline = data.online + STRAGGLER_TICKS;
            GscraftWar.LOG.info("[gscraft] {} counterattack wave {} of {}: {} placed at the {} approach", site.id(), p.wave, DEFENCE_WAVES, placed, site.approach());
        }
        bar(level.getServer(), site, "THE GATE — wave " + Math.max(1, p.wave) + " of " + DEFENCE_WAVES, (float) p.wave / DEFENCE_WAVES, BossEvent.BossBarColor.RED);
        String tag = WAVE_TAG + "_" + site.id();
        AABB square = new AABB(camp.sx0(), level.getMinBuildHeight(), camp.sz0(), camp.sx1() + 1, level.getMaxBuildHeight(), camp.sz1() + 1);
        int inSquare = level.getEntitiesOfClass(Mob.class, square, m -> m.isAlive() && m.getTags().contains(tag)).size();
        p.lossTicks = inSquare >= LOSS_COUNT ? p.lossTicks + 20 : 0;
        if (p.lossTicks >= LOSS_TICKS) {
            p.lost = true;
            Stages.add(level.getServer(), site.id() + "_lost");
            discardWave(level, site);
            dropBar(site);
            p.phase = Phase.FORTIFY;
            p.deadline = data.online + FORTIFY_TICKS;
            p.warned = false;
            p.twoMinutes = false;
            p.lossTicks = 0;
            data.setDirty();
            title(level.getServer(), Component.translatable("gscraft.title.fell"), Component.translatable("gscraft.title.fell.sub"));
            GscraftWar.LOG.info("[gscraft] {}: the gate fell; the wave withdraws and another clock runs", site.id());
            return;
        }
        if (p.wave < DEFENCE_WAVES) return;
        int cx = (camp.sx0() + camp.sx1()) / 2;
        int cz = (camp.sz0() + camp.sz1()) / 2;
        AABB near = new AABB(cx - 128, level.getMinBuildHeight(), cz - 128, cx + 128, level.getMaxBuildHeight(), cz + 128);
        int alive = level.getEntitiesOfClass(Mob.class, near, m -> m.isAlive() && m.getTags().contains(tag)).size();
        if (alive > 0 && data.online < p.deadline) return;
        if (alive > 0) discardWave(level, site);
        dropBar(site);
        p.lost = false;
        p.phase = Phase.NONE;
        p.guardTarget = GUARD_TARGET * 2;
        data.contested = "";
        setState(level, data, site, p, State.DEFENDED);
        keepGuard(level, site, p);
        title(level.getServer(), Component.translatable("gscraft.title.held"), Component.empty());
        GscraftWar.LOG.info("[gscraft] {} defended; the site guard doubles", site.id());
    }

    // ---- waves

    /** the assault is scaled to the players inside the site; the counterattack to the players online */
    static float scaleInside(ServerLevel level, SiteDef site) {
        long n = level.players().stream().filter(pl -> site.contains(pl.getBlockX(), pl.getBlockZ())).count();
        return scale((int) n);
    }

    static float scaleOnline(ServerLevel level) {
        return scale(level.getServer().getPlayerList().getPlayerCount());
    }

    static float scale(int players) {
        if (players <= 1) return 0.4F;
        if (players == 2) return 0.6F;
        if (players <= 4) return 0.8F;
        if (players == 5) return 1.0F;
        return 1.2F;
    }

    /** eight points around the site's edges; the wave enters from outside, never from inside its buildings */
    private static List<BlockPos> edgePoints(ServerLevel level, SiteDef site) {
        int mx = (site.x0() + site.x1()) / 2;
        int mz = (site.z0() + site.z1()) / 2;
        return List.of(new BlockPos(site.x0() - 2, 0, mz), new BlockPos(site.x1() + 2, 0, mz), new BlockPos(mx, 0, site.z0() - 2),
                new BlockPos(mx, 0, site.z1() + 2), new BlockPos(site.x0() - 2, 0, site.z0() - 2), new BlockPos(site.x1() + 2, 0, site.z0() - 2),
                new BlockPos(site.x0() - 2, 0, site.z1() + 2), new BlockPos(site.x1() + 2, 0, site.z1() + 2));
    }

    private static int sendWave(ServerLevel level, SiteDef site, List<WaveEntry> wave, List<BlockPos> points, float scale) {
        RandomSource random = level.getRandom();
        int placed = 0;
        java.util.List<Mob> fighters = new java.util.ArrayList<>();
        for (WaveEntry entry : wave) {
            int n = entry.count() <= 0 ? 0 : Math.max(1, Math.round(entry.count() * scale));
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(entry.entity());
            if (type == null) {
                GscraftWar.LOG.warn("[gscraft] wave entity {} is not registered", entry.entity());
                continue;
            }
            for (int i = 0; i < n; i++) {
                BlockPos point = points.get(random.nextInt(points.size()));
                BlockPos pos = null;
                for (int t = 0; t < 8 && pos == null; t++) {
                    int x = point.getX() + random.nextInt(13) - 6;
                    int z = point.getZ() + random.nextInt(13) - 6;
                    if (!level.hasChunkAt(new BlockPos(x, 64, z))) break;
                    int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                    pos = Director.legacyStand(level, x, y, z);
                }
                if (pos == null) continue;
                Mob mob = placeWave(level, type, pos, entry.rank(), site);
                if (mob != null) {
                    placed++;
                    if (mob instanceof gscraft.war.entity.GunUser) fighters.add(mob);
                }
            }
        }
        // a wave's soldiers arrive as squads of up to six
        for (int i = 0; i < fighters.size(); i += gscraft.war.entity.Squad.MAX_SIZE) {
            gscraft.war.entity.Squad.form(fighters.subList(i, Math.min(fighters.size(), i + gscraft.war.entity.Squad.MAX_SIZE)));
        }
        return placed;
    }

    /** a wave body: tagged, never despawning, dressed as the named rank; torches are not asked - the wave is the point */
    static Mob placeWave(ServerLevel level, EntityType<?> type, BlockPos pos, String rank, SiteDef site) {
        Entity entity = type.create(level);
        if (!(entity instanceof Mob mob)) {
            if (entity != null) entity.discard();
            return null;
        }
        mob.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, level.getRandom().nextFloat() * 360.0F, 0.0F);
        mob.addTag(WarEvents.PLACED_TAG);
        mob.addTag(WAVE_TAG);
        mob.addTag(WAVE_TAG + "_" + site.id());
        if (!rank.isEmpty()) {
            if (mob instanceof Soldier s) s.pinRank(rank);
            else if (mob instanceof Scavenger s) s.pinRank(rank);
        }
        SpawnGroupData group = mob instanceof Zombie ? new Zombie.ZombieGroupData(false, false) : null;
        mob.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, group, null);
        if (mob instanceof Zombie zombie) dressWaveDead(zombie, rank, level.getRandom());
        mob.setPersistenceRequired();
        level.addFreshEntity(mob);
        return mob;
    }

    private static void dressWaveDead(Zombie zombie, String rank, RandomSource random) {
        ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(zombie.getType());
        if (key != null && GscraftWar.MODID.equals(key.getNamespace())) return;
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            zombie.setItemSlot(slot, ItemStack.EMPTY);
            zombie.setDropChance(slot, 0.0F);
        }
        RankDef def = Ranks.named("dead", rank.isEmpty() ? "The Dead" : rank);
        if (def == null) return;
        Kit.issueFrom(zombie, List.of(def), random);
        if (!def.name().equals("The Dead")) zombie.setCustomName(Component.literal(def.name()));
    }

    private static void discardWave(ServerLevel level, SiteDef site) {
        String tag = WAVE_TAG + "_" + site.id();
        // collect first: discarding while walking the level's live entity list skips neighbours
        List<Entity> doomed = new java.util.ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (e.getTags().contains(tag)) doomed.add(e);
        }
        for (Entity e : doomed) e.discard();
    }

    // ---- the site guard

    /** the guard stands at the anchor and is topped up to its target by kind, like any garrison (F3) */
    static int keepGuard(ServerLevel level, SiteDef site, Progress p) {
        if (p.guardTarget <= 0 || !level.hasChunkAt(new BlockPos(site.anchorX(), 64, site.anchorZ()))) return 0;
        String tag = GUARD_TAG + site.id();
        List<Mob> present = level.getEntitiesOfClass(Mob.class, around(site, 32), m -> m.isAlive() && m.getTags().contains(tag));
        int spawned = 0;
        int copies = Math.max(1, p.guardTarget / GUARD.size());
        for (String id : GUARD.stream().distinct().toList()) {
            ResourceLocation key = new ResourceLocation(id);
            int want = (int) GUARD.stream().filter(id::equals).count() * copies;
            int have = (int) present.stream().filter(m -> key.equals(ForgeRegistries.ENTITY_TYPES.getKey(m.getType()))).count();
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(key);
            if (type == null) {
                GscraftWar.LOG.warn("[gscraft] site guard entity {} is not registered", id);
                continue;
            }
            for (int i = have; i < want; i++) {
                // the anchor's ground floor, not its roof: the heightmap of a building is the roof
                BlockPos pos = null;
                for (int t = 0; t < 6 && pos == null; t++) {
                    int x = site.anchorX() + level.getRandom().nextInt(9) - 4;
                    int z = site.anchorZ() + level.getRandom().nextInt(9) - 4;
                    pos = Director.groundAt(level, x, z);
                }
                if (pos == null) continue;
                Entity e = type.create(level);
                if (!(e instanceof Mob mob)) {
                    if (e != null) e.discard();
                    continue;
                }
                mob.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, 0.0F, 0.0F);
                mob.addTag(tag);
                mob.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, null, null);
                mob.setPersistenceRequired();
                mob.restrictTo(new BlockPos(site.anchorX(), pos.getY(), site.anchorZ()), 16);
                level.addFreshEntity(mob);
                spawned++;
            }
        }
        if (spawned > 0) GscraftWar.LOG.info("[gscraft] {} site guard: {} summoned, target {}", site.id(), spawned, p.guardTarget);
        return spawned;
    }

    static int guardCount(ServerLevel level, SiteDef site) {
        String tag = GUARD_TAG + site.id();
        return level.getEntitiesOfClass(Mob.class, around(site, 32), m -> m.isAlive() && m.getTags().contains(tag)).size();
    }

    private static AABB around(SiteDef site, int margin) {
        return new AABB(site.x0() - margin, -64, site.z0() - margin, site.x1() + margin + 1, 320, site.z1() + margin + 1);
    }

    // ---- the screen

    private static void bar(MinecraftServer server, SiteDef site, String name, float progress, BossEvent.BossBarColor colour) {
        ServerBossEvent bar = bars.computeIfAbsent(site.id(), k -> new ServerBossEvent(Component.literal(name), colour, BossEvent.BossBarOverlay.PROGRESS));
        bar.setName(Component.literal(name));
        bar.setProgress(Math.max(0.0F, Math.min(1.0F, progress)));
        bar.setColor(colour);
        for (ServerPlayer p : server.getPlayerList().getPlayers()) bar.addPlayer(p);
    }

    private static void dropBar(SiteDef site) {
        ServerBossEvent bar = bars.remove(site.id());
        if (bar != null) bar.removeAllPlayers();
    }

    static void title(MinecraftServer server, Component title, Component subtitle) {
        for (ServerPlayer p : server.getPlayerList().getPlayers()) {
            p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 70, 20));
            p.connection.send(new ClientboundSetSubtitleTextPacket(subtitle));
            p.connection.send(new ClientboundSetTitleTextPacket(title));
        }
    }

    static String mmss(long ticks) {
        long s = Math.max(0, ticks) / 20;
        return String.format("%d:%02d", s / 60, s % 60);
    }

    public static String describe(ServerLevel level, SiteDef site) {
        SiteData data = SiteData.get(level);
        Progress p = data.progress(site.id());
        StringBuilder sb = new StringBuilder(site.id()).append(": ").append(p.state.name().toLowerCase(Locale.ROOT));
        if (p.lost) sb.append(", lost once");
        switch (p.phase) {
            case ASSAULT -> sb.append("; assault, ").append(mmss(p.deadline - data.online)).append(" left, wave ").append(p.wave).append(" of ").append(ASSAULT_WAVES);
            case FORTIFY -> sb.append("; fortify clock ").append(mmss(p.deadline - data.online)).append(p.warned ? ", warned" : "");
            case COUNTER -> sb.append("; counterattack wave ").append(p.wave).append(" of ").append(DEFENCE_WAVES).append(", in the square ").append(p.lossTicks / 20).append(" s");
            default -> { }
        }
        if (p.guardTarget > 0) sb.append("; guard ").append(guardCount(level, site)).append(" of ").append(p.guardTarget);
        if (data.contested.equals(site.id())) sb.append("; contested");
        return sb.toString();
    }

    /** the operator's stage tag helper: a compound the tests can read */
    public static CompoundTag snapshot(ServerLevel level) {
        return SiteData.get(level).save(new CompoundTag());
    }
}
