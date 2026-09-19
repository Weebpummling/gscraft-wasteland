package gscraft.war.journal;

import gscraft.war.GscraftWar;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;

/**
 * The one thing to do next (interface doc §4.1; owner, 2026-09-17: the journal was not intuitive): the first few quests
 * a player can start are pinned for them, so FTB Quests' own pinned-quest overlay shows what to do without the book
 * open. FTB Quests is reached by reflection (it is not a compile dependency, like Superb Warfare): its own class and
 * method names are plain in the jar. The mod only ever touches pins it set itself (kept on the player as GscraftPins),
 * so a player's own pins stay, and the tag gs_nopins turns it off for that player ({@code /gscraft journal pins}).
 */
@Mod.EventBusSubscriber(modid = GscraftWar.MODID)
public final class Pins {
    private Pins() {}

    public static int MAX = 3, EVERY = 40;
    public static final String OFF_TAG = "gs_nopins", OWNED = "GscraftPins";
    /** the book's chapters in reading order (tools/chapters.py); an unknown chapter sorts last */
    private static final List<String> ORDER = List.of("compound", "walker", "tony", "michael", "tune", "james", "marshall", "pocket", "notes");

    private static boolean tried, ok;
    private static Object file;
    private static Field fInstance, fId;
    private static Method mTeamData, mForAll, mCompleted, mCanStart, mSetPinned, mPinnedIds, mVisible, mRepeat, mChapter, mX, mY, mFilename, mTitle;

    /** FTB Quests' handles, resolved once; false when the mod is absent or its API moved (logged once) */
    static boolean api() {
        if (tried) return ok && instance() != null;
        tried = true;
        try {
            Class<?> cFile = Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile");
            Class<?> cBase = Class.forName("dev.ftb.mods.ftbquests.quest.BaseQuestFile");
            Class<?> cTeam = Class.forName("dev.ftb.mods.ftbquests.quest.TeamData");
            Class<?> cQuest = Class.forName("dev.ftb.mods.ftbquests.quest.Quest");
            Class<?> cObject = Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
            Class<?> cObjBase = Class.forName("dev.ftb.mods.ftbquests.quest.QuestObjectBase");
            Class<?> cChapter = Class.forName("dev.ftb.mods.ftbquests.quest.Chapter");
            fInstance = cFile.getField("INSTANCE");
            fId = cObjBase.getField("id");
            mTeamData = cBase.getMethod("getOrCreateTeamData", Entity.class);
            mForAll = cBase.getMethod("forAllQuests", Consumer.class);
            mCompleted = cTeam.getMethod("isCompleted", cObject);
            mCanStart = cTeam.getMethod("canStartTasks", cQuest);
            mSetPinned = cTeam.getMethod("setQuestPinned", Player.class, long.class, boolean.class);
            mPinnedIds = cTeam.getMethod("getPinnedQuestIds", Player.class);
            mVisible = cQuest.getMethod("isVisible", cTeam);
            mRepeat = cQuest.getMethod("canBeRepeated");
            mChapter = cQuest.getMethod("getChapter");
            mX = cQuest.getMethod("getX");
            mY = cQuest.getMethod("getY");
            mFilename = cChapter.getMethod("getFilename");
            mTitle = cObjBase.getMethod("getRawTitle");
            ok = true;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] journal: FTB Quests is not reachable, no pins: {}", ex.toString());
        }
        return ok && instance() != null;
    }

    private static Object instance() {
        try {
            file = fInstance == null ? null : fInstance.get(null);
        } catch (IllegalAccessException ex) {
            file = null;
        }
        return file;
    }

    /** a quest the player can start now: visible, its dependencies done, not done itself, not a repeatable hand-in */
    public record Next(long id, String title, String chapter, double x, double y) {}

    public static List<Next> available(ServerPlayer player) {
        List<Next> out = new ArrayList<>();
        if (!api()) return out;
        try {
            Object team = mTeamData.invoke(file, player);
            List<Object> quests = new ArrayList<>();
            mForAll.invoke(file, (Consumer<Object>) quests::add);
            for (Object q : quests) {
                if ((boolean) mRepeat.invoke(q) || (boolean) mCompleted.invoke(team, q)) continue;
                if (!(boolean) mVisible.invoke(q, team) || !(boolean) mCanStart.invoke(team, q)) continue;
                Object chapter = mChapter.invoke(q);
                out.add(new Next(fId.getLong(q), String.valueOf(mTitle.invoke(q)), String.valueOf(mFilename.invoke(chapter)), (double) mX.invoke(q), (double) mY.invoke(q)));
            }
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] journal: reading {}'s quests failed: {}", player.getGameProfile().getName(), ex.toString());
        }
        out.sort(Comparator.comparingInt((Next n) -> ORDER.contains(n.chapter()) ? ORDER.indexOf(n.chapter()) : ORDER.size())
                .thenComparingDouble(Next::x).thenComparingDouble(Next::y));
        return out;
    }

    public static Set<Long> owned(ServerPlayer player) {
        Set<Long> out = new HashSet<>();
        for (long id : player.getPersistentData().getLongArray(OWNED)) out.add(id);
        return out;
    }

    /** the mod's pins brought to the first MAX available quests; pins it does not own are left alone */
    public static void update(ServerPlayer player) {
        if (!api()) return;
        Set<Long> owned = owned(player);
        Set<Long> target = new HashSet<>();
        if (!player.getTags().contains(OFF_TAG)) {
            for (Next n : available(player)) {
                if (target.size() >= MAX) break;
                target.add(n.id());
            }
        }
        if (owned.equals(target)) return;
        try {
            Object team = mTeamData.invoke(file, player);
            Set<Long> pinned = new HashSet<>();
            for (Object id : (Iterable<?>) mPinnedIds.invoke(team, player)) pinned.add(((Number) id).longValue());
            for (long id : owned) if (!target.contains(id) && pinned.contains(id)) mSetPinned.invoke(team, player, id, false);
            Set<Long> now = new HashSet<>();
            for (long id : target) {
                if (pinned.contains(id) && !owned.contains(id)) continue;   // the player's own pin: not ours to own
                if (!pinned.contains(id)) mSetPinned.invoke(team, player, id, true);
                now.add(id);
            }
            player.getPersistentData().putLongArray(OWNED, now.stream().mapToLong(Long::longValue).toArray());
        } catch (ReflectiveOperationException | RuntimeException ex) {
            GscraftWar.LOG.warn("[gscraft] journal: pinning for {} failed: {}", player.getGameProfile().getName(), ex.toString());
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        MinecraftServer server = event.getServer();
        if (server.getTickCount() % EVERY != 0) return;
        for (ServerPlayer p : server.getPlayerList().getPlayers()) update(p);
    }

    /** the mod's list of its own pins survives a death (persistent data is per entity) */
    @SubscribeEvent
    public static void cloned(PlayerEvent.Clone event) {
        CompoundTag old = event.getOriginal().getPersistentData();
        if (old.contains(OWNED)) event.getEntity().getPersistentData().putLongArray(OWNED, old.getLongArray(OWNED));
    }
}
