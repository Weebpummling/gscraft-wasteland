package gscraft.war.world;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.BlockPos;
import java.util.LinkedHashMap;
import java.util.UUID;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/**
 * The loop's record (fold-in review §2): every site's rung and fight, the one contested slot, the online clock and
 * the stages the quest book reads. Stages are tags on players; this is the source they are re-applied from.
 */
public final class SiteData extends SavedData {
    private static final String NAME = "gscraft_sites";

    public enum State { UNKNOWN, SCOUTED, LOOTED, HELD, DEFENDED }

    public enum Phase { NONE, ASSAULT, FORTIFY, COUNTER }

    public static final class Progress {
        public State state = State.UNKNOWN;
        public boolean lost;
        public Phase phase = Phase.NONE;
        /** online tick the phase ends at: the assault's end, the fortify clock's end, the counterattack's last chance */
        public long deadline;
        /** online tick of the next wave */
        public long nextWave;
        public int wave;
        public boolean warned;
        public boolean twoMinutes;
        public int lossTicks;
        public int guardTarget;
        /** the site's boss has been placed (or refused); the reset clears it */
        public boolean bossPlaced;
        /** the claim marker's banner, while the assault runs and after; null when none was placed (the console's claim) */
        public BlockPos marker;

        CompoundTag save() {
            CompoundTag t = new CompoundTag();
            t.putString("State", state.name());
            t.putBoolean("Lost", lost);
            t.putString("Phase", phase.name());
            t.putLong("Deadline", deadline);
            t.putLong("NextWave", nextWave);
            t.putInt("Wave", wave);
            t.putBoolean("Warned", warned);
            t.putBoolean("TwoMinutes", twoMinutes);
            t.putInt("LossTicks", lossTicks);
            t.putInt("GuardTarget", guardTarget);
            t.putBoolean("BossPlaced", bossPlaced);
            if (marker != null) t.putIntArray("Marker", new int[]{marker.getX(), marker.getY(), marker.getZ()});
            return t;
        }

        static Progress load(CompoundTag t) {
            Progress p = new Progress();
            p.state = State.valueOf(t.getString("State"));
            p.lost = t.getBoolean("Lost");
            p.phase = Phase.valueOf(t.getString("Phase"));
            p.deadline = t.getLong("Deadline");
            p.nextWave = t.getLong("NextWave");
            p.wave = t.getInt("Wave");
            p.warned = t.getBoolean("Warned");
            p.twoMinutes = t.getBoolean("TwoMinutes");
            p.lossTicks = t.getInt("LossTicks");
            p.guardTarget = t.getInt("GuardTarget");
            p.bossPlaced = t.getBoolean("BossPlaced");
            if (t.contains("Marker")) {
                int[] m = t.getIntArray("Marker");
                if (m.length == 3) p.marker = new BlockPos(m[0], m[1], m[2]);
            }
            return p;
        }
    }

    private final Map<String, Progress> sites = new HashMap<>();
    private final Set<String> stages = new LinkedHashSet<>();
    private final Map<UUID, BlockPos> stations = new LinkedHashMap<>();   // a player's work station (crafting §4: one each)
    public long online;
    public String contested = "";

    public static SiteData get(ServerLevel level) {
        return level.getServer().overworld().getDataStorage().computeIfAbsent(SiteData::load, SiteData::new, NAME);
    }

    private static SiteData load(CompoundTag tag) {
        SiteData data = new SiteData();
        data.online = tag.getLong("Online");
        data.contested = tag.getString("Contested");
        CompoundTag sites = tag.getCompound("Sites");
        for (String id : sites.getAllKeys()) data.sites.put(id, Progress.load(sites.getCompound(id)));
        for (Tag t : tag.getList("Stages", Tag.TAG_STRING)) data.stages.add(t.getAsString());
        for (Tag t : tag.getList("Stations", Tag.TAG_COMPOUND)) {
            CompoundTag c = (CompoundTag) t;
            if (c.hasUUID("Owner")) data.stations.put(c.getUUID("Owner"), new BlockPos(c.getInt("X"), c.getInt("Y"), c.getInt("Z")));
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putLong("Online", online);
        tag.putString("Contested", contested);
        CompoundTag s = new CompoundTag();
        sites.forEach((id, p) -> s.put(id, p.save()));
        tag.put("Sites", s);
        ListTag list = new ListTag();
        for (String stage : stages) list.add(StringTag.valueOf(stage));
        tag.put("Stages", list);
        ListTag st = new ListTag();
        stations.forEach((id, pos) -> {
            CompoundTag c = new CompoundTag();
            c.putUUID("Owner", id);
            c.putInt("X", pos.getX());
            c.putInt("Y", pos.getY());
            c.putInt("Z", pos.getZ());
            st.add(c);
        });
        tag.put("Stations", st);
        return tag;
    }

    public Progress progress(String id) {
        return sites.computeIfAbsent(id, k -> new Progress());
    }

    public Map<String, Progress> all() {
        return sites;
    }

    public Set<String> stages() {
        return stages;
    }

    public boolean addStage(String stage) {
        boolean added = stages.add(stage);
        if (added) setDirty();
        return added;
    }

    public boolean removeStage(String stage) {
        boolean removed = stages.remove(stage);
        if (removed) setDirty();
        return removed;
    }

    public BlockPos station(UUID owner) {
        return stations.get(owner);
    }

    public Map<UUID, BlockPos> stations() {
        return stations;
    }

    public void bindStation(UUID owner, BlockPos pos) {
        stations.put(owner, pos.immutable());
        setDirty();
    }

    public void unbindStation(UUID owner, BlockPos pos) {
        if (pos.equals(stations.get(owner))) {
            stations.remove(owner);
            setDirty();
        }
    }
}
