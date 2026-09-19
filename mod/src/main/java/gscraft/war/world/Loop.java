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
    public static int ASSAULT_TICKS = 6000;
    public static int ASSAULT_WAVES = 6;
    public static int WAVE_GAP = 900;
    public static int FORTIFY_TICKS = 48000;
    public static int WARNING_TICKS = 12000;
    static final int TWO_MINUTES = 2400;
    public static int DEFENCE_WAVES = 3;
    public static int STRAGGLER_TICKS = 9600;
    public static int LOSS_COUNT = 5;
    public static int LOSS_TICKS = 600;
    static final int GUARD_EVERY = 600;
    public static int GUARD_TARGET = 6;
    /** the site guard: two recruits, a bowman, a shieldman, two Guard Villagers */
    private static final List<String> GUARD = List.of("recruits:recruit", "recruits:recruit", "recruits:bowman",
            "recruits:recruit_shieldman", "guardvillagers:guard", "guardvillagers:guard");

    /** true: clocks run with nobody online (tests only) */
    private static volatile boolean freeClock;
    private static int ticks;
    private static final Map<String, ServerBossEvent> bars = new HashMap<>();
    /** nobody within this of the fight: the clocks freeze; after AWAY_TICKS the wave is taken back */
    public static int AWAY_RANGE = 128;
    public static int AWAY_TICKS = 1200;
    private static final Map<String, Integer> awayTicks = new HashMap<>();

    private Loop() {}

    public static void setFreeClock(boolean value) {
        freeClock = value;
    }

    public static boolean freeClock() {
        return freeClock;
    }

    /** a held or defended site keeps its ambient hostiles off (F4) - unless the file says keep_ambient (a taken building:
     *  the Dead and the scavengers stay, owner 2026-09-12) */
    public static boolean suppressedAt(ServerLevel level, int x, int z) {
        if (Sites.all().isEmpty()) return false;
        SiteData data = SiteData.get(level);
        for (SiteDef site : Sites.all().values()) {
            if (!site.contains(x, z) || site.keepAmbient()) continue;
            State s = data.progress(site.id()).state;
            return s == State.HELD || s == State.DEFENDED;
        }
        return false;
    }

    // ---- the building take (system doc §6, slice build 0): the alias stage is the whole mechanism. Set (by the quest's
    // reward, or by hand), it takes the building: held, its functions run (the torch, the survivor), its zone flips. Unset,
    // the building is lost: its lost functions, the stages down, the zone back. No clear timer, no per-building counterattack,
    // loss check or guard - the sector's strongpoints carry the pressure.

    private static void building(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        if (site.alias() == null) return;
        boolean taken = Stages.isSet(site.alias());
        if (taken && p.state != State.HELD) {
            setState(level, data, site, p, State.HELD);
            p.lost = false;
            p.phase = Phase.NONE;
            p.guardTarget = 0;
            data.setDirty();
            run(level, site.held());
            title(level.getServer(), Component.literal(site.name()), Component.translatable("gscraft.title.taken"));
            GscraftWar.LOG.info("[gscraft] {} taken ({}); {} functions", site.id(), site.alias(), site.held().size());
        } else if (!taken && p.state == State.HELD) {
            p.state = State.UNKNOWN;
            Stages.remove(level.getServer(), site.id() + "_held");
            p.phase = Phase.NONE;
            data.setDirty();
            run(level, site.lost());
            title(level.getServer(), Component.translatable("gscraft.title.fell"), Component.translatable("gscraft.title.fell.sub"));
            GscraftWar.LOG.info("[gscraft] {} lost ({} unset); {} functions", site.id(), site.alias(), site.lost().size());
        }
    }

    /** the site's boss (system pass §3: placed, not rolled): once the site is scouted and the boss's stage (if any) is set,
     *  with its chunk loaded, the named vehicle is placed holding at its point; remembered, so a restart or a reload does not
     *  place a second; the site's reset takes it with the wave */
    private static void boss(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        Sites.BossDef b = site.boss();
        if (p.state == State.UNKNOWN) return;
        if (!b.stage().isEmpty() && !Stages.isSet(b.stage())) return;
        BlockPos at = new BlockPos(b.x(), b.y(), b.z());
        if (!level.hasChunkAt(at)) return;
        boolean ok = gscraft.war.armour.Armour.wave(level, site.id(), site.faction(), b.vehicle(), at, new BlockPos(b.tx(), 0, b.tz()), b.id(), b.name());
        p.bossPlaced = true;   // placed or refused (no stand): the loop does not try every second for good
        data.setDirty();
        GscraftWar.LOG.info("[gscraft] {} boss {} ({}) {} at {}", site.id(), b.id(), b.vehicle(), ok ? "placed" : "NOT placed - no stand with a hull's room", at.toShortString());
    }

    /** the site guard's size: the file's `guard` (0: none) or the default, doubled on defended */
    private static int guardFor(SiteDef site, int times) {
        return (site.guard() >= 0 ? site.guard() : GUARD_TARGET) * times;
    }

    /** the file's functions, run as the server */
    static void run(ServerLevel level, List<String> functions) {
        MinecraftServer server = level.getServer();
        for (String id : functions) {
            ResourceLocation key = ResourceLocation.tryParse(id);
            if (key == null) continue;
            var fn = server.getFunctions().get(key);
            if (fn.isEmpty()) {
                GscraftWar.LOG.warn("[gscraft] site function {} is not loaded", id);
                continue;
            }
            server.getFunctions().execute(fn.get(), server.createCommandSourceStack().withSuppressedOutput().withPermission(2));
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || Sites.all().isEmpty()) return;
        ServerLevel level = server.overworld();
        if (server.getTickCount() % 20 == 0) Stages.refresh(server);   // the zones read the stages from here
        if (!freeClock && server.getPlayerList().getPlayers().isEmpty()) return;
        SiteData data = SiteData.get(level);
        data.online++;
        if (++ticks % 20 != 0) return;
        data.setDirty();
        for (SiteDef site : Sites.all().values()) {
            Progress p = data.progress(site.id());
            if (site.building()) building(level, data, site, p);
            if (site.boss() != null && !p.bossPlaced) boss(level, data, site, p);
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
                Board.lamp(level, true);
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
        // a held strongpoint's guns answer Marshall's call: `gun_fired` gates Fire for effect, and NOTHING set it - the
        // artillery strike could never be earned (the completeness audit, 2026-09-19). Holding any strongpoint sets it.
        if (to == State.HELD && SitePlay.strongpoint(site)) Stages.add(level.getServer(), "gun_fired");
        Board.apply(level, site.id(), to.name().toLowerCase(Locale.ROOT));
    }

    private static void reset(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        for (State s : State.values()) Stages.remove(level.getServer(), site.id() + "_" + s.name().toLowerCase(Locale.ROOT));
        Stages.remove(level.getServer(), site.id() + "_lost");
        if (site.alias() != null) Stages.remove(level.getServer(), site.alias());
        if (data.contested.equals(site.id())) data.contested = "";
        discardWave(level, site);
        for (Mob m : level.getEntitiesOfClass(Mob.class, around(site, 64), m -> m.getTags().contains(GUARD_TAG + site.id()))) m.discard();
        dropBar(site);
        if (p.marker != null && level.getBlockState(p.marker).is(net.minecraft.tags.BlockTags.BANNERS)) level.removeBlock(p.marker, false);
        p.marker = null;
        Board.lamp(level, false);
        Board.apply(level, site.id(), "unknown");
        Progress fresh = new Progress();
        p.state = fresh.state;
        p.searched.clear();
        p.lost = false;
        p.phase = Phase.NONE;
        p.wave = 0;
        p.warned = false;
        p.twoMinutes = false;
        p.lossTicks = 0;
        p.guardTarget = 0;
        p.bossPlaced = false;
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

    /**
     * The claim marker set at a site (the item, or {@code /gscraft site <id> marker}): the assault begins if the rung allows;
     * the banner stands at the anchor and must survive, with a player inside at the end (map-design §6.1). Returns the message.
     */
    public static String claim(ServerLevel level, SiteDef site) {
        String msg = advance(level, site, State.HELD);
        if (!msg.contains("the assault begins")) return msg;
        BlockPos top = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, new BlockPos(site.anchorX(), 0, site.anchorZ()));
        level.setBlock(top, net.minecraft.world.level.block.Blocks.WHITE_BANNER.defaultBlockState(), 3);
        SiteData data = SiteData.get(level);
        Progress p = data.progress(site.id());
        p.marker = top;
        data.setDirty();
        GscraftWar.LOG.info("[gscraft] {}: the marker stands at {}", site.id(), top.toShortString());
        return msg + "; the marker stands at " + top.toShortString();
    }

    /** the marker still stands and somebody is inside the site */
    private static boolean markerHolds(ServerLevel level, SiteDef site, Progress p) {
        boolean standing = level.getBlockState(p.marker).is(net.minecraft.tags.BlockTags.BANNERS);
        AABB box = new AABB(site.x0(), level.getMinBuildHeight(), site.z0(), site.x1() + 1, level.getMaxBuildHeight(), site.z1() + 1);
        boolean inside = !level.getEntitiesOfClass(net.minecraft.server.level.ServerPlayer.class, box, pl -> pl.isAlive() && !pl.isSpectator()).isEmpty();
        if (!standing) GscraftWar.LOG.info("[gscraft] {}: the marker is down", site.id());
        if (!inside) GscraftWar.LOG.info("[gscraft] {}: nobody inside at the end", site.id());
        return standing && inside;
    }

    /** the assault lost: the site stays looted, the marker falls where it stood to be planted again (it was destroyed, and one
     *  marker is 25 minutes of orders and sixteen of each fastener: slice review 2026-09-19), Marshall says so */
    private static void assaultLost(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        discardWave(level, site);
        net.minecraft.world.item.Item markerItem = net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation(GscraftWar.MODID, "claim_marker"));
        if (p.marker != null && markerItem != null) net.minecraft.world.level.block.Block.popResource(level, p.marker, new net.minecraft.world.item.ItemStack(markerItem));
        if (p.marker != null && level.getBlockState(p.marker).is(net.minecraft.tags.BlockTags.BANNERS)) level.removeBlock(p.marker, false);
        p.marker = null;
        p.phase = Phase.NONE;
        p.wave = 0;
        if (data.contested.equals(site.id())) data.contested = "";
        data.setDirty();
        Board.lamp(level, false);
        Board.apply(level, site.id(), "looted");
        title(level.getServer(), Component.literal(site.name() + " — LOST"), Component.empty());
        for (net.minecraft.server.level.ServerPlayer pl : level.getServer().getPlayerList().getPlayers()) gscraft.war.survivor.Say.queue(pl, "marshall", "assault_lost", false);
        GscraftWar.LOG.info("[gscraft] {}: the assault is lost; the site stays looted", site.id());
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
            int placed = sendWave(level, site, site.assault().get(p.wave), edgePoints(level, site), scaleInside(level, site), new BlockPos(site.anchorX(), 0, site.anchorZ()), false);
            p.wave++;
            p.nextWave = data.online + WAVE_GAP;
            GscraftWar.LOG.info("[gscraft] {} assault wave {} of {}: {} placed", site.id(), p.wave, ASSAULT_WAVES, placed);
        }
        long left = p.deadline - data.online;
        bar(level.getServer(), site, site.name() + " — hold — " + mmss(left), (float) left / ASSAULT_TICKS, BossEvent.BossBarColor.RED);
        if (left <= 0) {
            dropBar(site);
            if (p.marker != null && !markerHolds(level, site, p)) {
                assaultLost(level, data, site, p);
                return;
            }
            Board.lamp(level, false);
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
            // Radio 1 is what hears it (quests doc U2: "the warning system"; world/Upgrades). Without it the two-minute title is all there is.
            if (Upgrades.warningHeard()) {
                level.getServer().getPlayerList().broadcastSystemMessage(Component.translatable("gscraft.line.tune.warning"), false);
                gscraft.war.journal.FieldNotes.noteAll(level.getServer(), "warning");   // the first time: a field note
            }
            GscraftWar.LOG.info("[gscraft] {}: the ten-minute warning {}", site.id(), Upgrades.warningHeard() ? "is heard (Radio 1)" : "goes unheard (no Radio 1)");
        }
        // Radio 2: the whole countdown from `held`, as the site's bar (it was the board's; the board is gone)
        if (Upgrades.countdownShown() && left > 0) bar(level.getServer(), site, site.name() + " — they come back in " + mmss(left), Math.min(1.0F, (float) left / FORTIFY_TICKS), BossEvent.BossBarColor.YELLOW);
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

    /** the wave's bodies that carry no order of their own (the Dead: vanilla mobs) are walked to the gate a leg at a time:
     *  every second, one without a target and with nothing to walk is pointed at it again (a target beyond the follow range
     *  gets a partial path, so the march is in legs) */
    private static void march(ServerLevel level, String tag, int gx, int gz) {
        int gy = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, gx, gz);
        for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(gx - 400, level.getMinBuildHeight(), gz - 400, gx + 400, level.getMaxBuildHeight(), gz + 400),
                m -> m.isAlive() && !(m instanceof gscraft.war.entity.GunUser) && m.getTags().contains(tag))) {
            if (m.getTarget() != null || !m.getNavigation().isDone()) continue;
            if (m.blockPosition().distSqr(new BlockPos(gx, gy, gz)) < 16.0D) continue;
            m.getNavigation().moveTo(gx + 0.5D, gy, gz + 0.5D, 1.0D);
        }
    }

    private static void counter(ServerLevel level, SiteData data, SiteDef site, Progress p) {
        CampDef camp = Sites.camp();
        if (camp == null) return;
        if (away(level, data, site, p, camp.targetX(), camp.targetZ())) return;
        if (p.wave < DEFENCE_WAVES && data.online >= p.nextWave) {
            int[] at = camp.approaches().getOrDefault(site.approach(), camp.approaches().values().iterator().next());
            int placed = sendWave(level, site, site.defence().get(Math.min(p.wave, site.defence().size() - 1)), List.of(new BlockPos(at[0], 0, at[1])), scaleOnline(level),
                    new BlockPos(camp.targetX(), 0, camp.targetZ()), true);   // the gate: where the wave goes
            p.wave++;
            p.nextWave = data.online + WAVE_GAP;
            if (p.wave == DEFENCE_WAVES) p.deadline = data.online + STRAGGLER_TICKS;
            GscraftWar.LOG.info("[gscraft] {} counterattack wave {} of {}: {} placed at the {} approach", site.id(), p.wave, DEFENCE_WAVES, placed, site.approach());
        }
        bar(level.getServer(), site, "THE GATE — wave " + Math.max(1, p.wave) + " of " + DEFENCE_WAVES, (float) p.wave / DEFENCE_WAVES, BossEvent.BossBarColor.RED);
        String tag = WAVE_TAG + "_" + site.id();
        march(level, tag, camp.targetX(), camp.targetZ());
        AABB square = new AABB(camp.sx0(), level.getMinBuildHeight(), camp.sz0(), camp.sx1() + 1, level.getMaxBuildHeight(), camp.sz1() + 1);
        int inSquare = level.getEntitiesOfClass(Mob.class, square, m -> m.isAlive() && m.getTags().contains(tag)).size();
        p.lossTicks = inSquare >= LOSS_COUNT ? p.lossTicks + 20 : 0;
        if (p.lossTicks >= LOSS_TICKS) {
            p.lost = true;
            Stages.add(level.getServer(), site.id() + "_lost");
            Board.apply(level, site.id(), "lost");
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
        // the wave still standing anywhere between the approaches and the gate (the north approach is 230 from the gate now
        // that the target is the compound's corner; 128 round the square's centre missed it, and a wave just placed read as beaten)
        int cx = camp.targetX();
        int cz = camp.targetZ();
        AABB near = new AABB(cx - 400, level.getMinBuildHeight(), cz - 400, cx + 400, level.getMaxBuildHeight(), cz + 400);
        int alive = level.getEntitiesOfClass(Mob.class, near, m -> m.isAlive() && m.getTags().contains(tag)).size();
        if (alive > 0 && data.online < p.deadline) return;
        if (alive > 0) discardWave(level, site);
        dropBar(site);
        p.lost = false;
        p.phase = Phase.NONE;
        p.guardTarget = guardFor(site, 2);
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

    /** @param target where the wave is going: the site's anchor for an assault, the camp's gate for the counterattack (armour drives there)
     *  @param advance the infantry is ordered to the target too (the counterattack: it walks from the approach to the gate; found
     *                 standing at the approach for good, 2026-09-12 - an assault's infantry is placed on the site's edges and fights) */
    private static int sendWave(ServerLevel level, SiteDef site, List<WaveEntry> wave, List<BlockPos> points, float scale, BlockPos target, boolean advance) {
        RandomSource random = level.getRandom();
        int placed = 0;
        java.util.List<Mob> fighters = new java.util.ArrayList<>();
        for (WaveEntry entry : wave) {
            if (!entry.stage().isEmpty() && !Stages.isSet(entry.stage())) continue;   // the answer before the question (system pass §3)
            int n = entry.count() <= 0 ? 0 : Math.max(1, Math.round(entry.count() * scale));
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(entry.entity());
            if (type == null) {
                GscraftWar.LOG.warn("[gscraft] wave entity {} is not registered", entry.entity());
                continue;
            }
            if (gscraft.war.armour.Vehicles.isVehicleType(type, level)) {
                // armour in the wave (design §3): crewed, on the edge, driving for the target; a boss holds where it is
                int want = entry.boss().isEmpty() ? n : Math.max(1, entry.count());
                for (int i = 0; i < want; i++) {
                    placed += gscraft.war.armour.Armour.wave(level, site.id(), entry.faction().isEmpty() ? site.faction() : entry.faction(), entry.entity(), points.get(random.nextInt(points.size())), target, entry.boss(), entry.name()) ? 1 : 0;
                }
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
        if (advance && !fighters.isEmpty()) {
            // the march: an order of its own (not the squad's, which would release it out of a fight), re-pathed by the order goal
            // every second, so a target beyond the follow range is reached in legs
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, target.getX(), target.getZ());
            BlockPos to = new BlockPos(target.getX(), y, target.getZ());
            for (Mob m : fighters) {
                gscraft.war.entity.FighterState st = ((gscraft.war.entity.GunUser) m).fighterState();
                st.order = gscraft.war.entity.FighterState.Order.ADVANCE;
                st.orderPos = to;
                st.orderBySquad = false;
            }
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
