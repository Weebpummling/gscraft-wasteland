package gscraft.war.world;

import net.minecraft.nbt.CompoundTag;
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
            return p;
        }
    }

    private final Map<String, Progress> sites = new HashMap<>();
    private final Set<String> stages = new LinkedHashSet<>();
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
}
