package gscraft.war.world;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;

/**
 * When each garrison was last topped up. The members themselves are ordinary persistent entities saved with their
 * chunks; this only keeps a wiped outpost from refilling the moment a player walks back into range.
 */
public final class GarrisonData extends SavedData {
    private static final String NAME = "gscraft_garrisons";

    private final Map<String, Long> lastRefill = new HashMap<>();

    public static GarrisonData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(GarrisonData::load, GarrisonData::new, NAME);
    }

    private static GarrisonData load(CompoundTag tag) {
        GarrisonData data = new GarrisonData();
        CompoundTag refills = tag.getCompound("LastRefill");
        for (String key : refills.getAllKeys()) data.lastRefill.put(key, refills.getLong(key));
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        CompoundTag refills = new CompoundTag();
        lastRefill.forEach(refills::putLong);
        tag.put("LastRefill", refills);
        return tag;
    }

    public Long lastRefill(String zone) {
        return lastRefill.get(zone);
    }

    public void markRefill(String zone, long gameTime) {
        lastRefill.put(zone, gameTime);
        setDirty();
    }
}
