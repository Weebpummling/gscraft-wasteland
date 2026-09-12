package gscraft.war.world;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import gscraft.war.GscraftWar;
import gscraft.war.WarEvents;
import gscraft.war.combat.Ballistics;
import gscraft.war.combat.BandageItem;
import gscraft.war.combat.Damage;
import gscraft.war.combat.PlayerWounds;
import gscraft.war.entity.Callouts;
import gscraft.war.entity.Cover;
import gscraft.war.entity.GrenadeGoal;
import gscraft.war.entity.GunAttackGoal;
import gscraft.war.entity.Role;
import gscraft.war.entity.Squad;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.DoubleConsumer;
import java.util.function.DoubleSupplier;

/**
 * The numbers behind the war, as data: {@code data/gscraft/gscraft_settings/*.json}, every file applied in name
 * order on top of the code's defaults, so the jar's {@code defaults.json} documents the baseline and a world
 * datapack's {@code zz_live.json} overrides what the server owner wants changed - {@code /reload} applies it, no
 * jar swap. Keys are dotted paths ({@code director.server_ceiling}) nested as JSON objects; unknown keys are
 * logged and ignored; {@code /gscraft settings} prints what is in force.
 *
 * Entries write straight into the static fields the code reads, so a value is live the tick after the reload.
 * Attributes fixed at spawn (follow range, health) are not here: they belong to the bodies already placed.
 */
public final class Settings extends SimpleJsonResourceReloadListener {
    private static final Gson GSON = new Gson();
    private static final Map<String, Entry> ENTRIES = new LinkedHashMap<>();
    private static final List<String> applied = new ArrayList<>();

    private record Entry(DoubleSupplier get, DoubleConsumer set, boolean whole, String doc) {}

    private static void e(String path, DoubleSupplier get, DoubleConsumer set, boolean whole, String doc) {
        ENTRIES.put(path, new Entry(get, set, whole, doc));
    }

    private static void i(String path, DoubleSupplier get, DoubleConsumer set, String doc) {
        e(path, get, set, true, doc);
    }

    private static void d(String path, DoubleSupplier get, DoubleConsumer set, String doc) {
        e(path, get, set, false, doc);
    }

    static {
        // the director
        i("director.interval_ticks", () -> Director.INTERVAL, v -> Director.INTERVAL = (int) v, "ticks between director passes");
        i("director.sweep_blocks", () -> Director.SWEEP, v -> Director.SWEEP = (int) v, "an ambient placement further than this from everyone, on two passes running, is taken back");
        i("director.player_ceiling", () -> Director.PLAYER_CEILING, v -> Director.PLAYER_CEILING = (int) v, "director creatures allowed within ceiling_box of one player, whatever the ground");
        i("director.server_ceiling", () -> Director.SERVER_CEILING, v -> Director.SERVER_CEILING = (int) v, "director creatures allowed on the whole server");
        i("director.ceiling_box", () -> Director.CEILING_BOX, v -> Director.CEILING_BOX = (int) v, "half-width of the player ceiling's box");
        i("director.garrison_wake", () -> Director.GARRISON_WAKE, v -> Director.GARRISON_WAKE = (int) v, "a garrison is placed when someone is this close to its zone centre");
        i("director.garrison_rest", () -> Director.GARRISON_REST, v -> Director.GARRISON_REST = (int) v, "a garrison with nobody this close for rest_passes is taken back");
        i("director.rest_passes", () -> Director.REST_PASSES, v -> Director.REST_PASSES = (int) v, "passes of nobody near before a garrison rests");
        i("director.horror_clear", () -> Director.HORROR_CLEAR, v -> Director.HORROR_CLEAR = (int) v, "one horror of a kind within this many blocks");
        d("director.sealed_share", () -> Director.SEALED_SHARE, v -> Director.SEALED_SHARE = (float) v, "share of indoor and underground placements allowed behind shut doors");
        for (Env env : Env.values()) {
            String p = "env." + env.name().toLowerCase(Locale.ROOT) + ".";
            d(p + "cap_scale", () -> env.capScale, v -> env.capScale = v, "multiplies a zone's cap on this ground");
            i(p + "min_r", () -> env.minR, v -> env.minR = (int) v, "placements land at least this far from the player");
            i(p + "max_r", () -> env.maxR, v -> env.maxR = (int) v, "and at most this far");
            i(p + "count_box", () -> env.countBox, v -> env.countBox = (int) v, "half-width of the box the cap is counted in");
            i(p + "count_y", () -> env.countY, v -> env.countY = (int) v, "half-height of that box");
        }
        // the strongpoint loop
        i("loop.assault_ticks", () -> Loop.ASSAULT_TICKS, v -> Loop.ASSAULT_TICKS = (int) v, "the assault's length in online ticks");
        i("loop.assault_waves", () -> Loop.ASSAULT_WAVES, v -> Loop.ASSAULT_WAVES = (int) v, "waves in an assault");
        i("loop.wave_gap_ticks", () -> Loop.WAVE_GAP, v -> Loop.WAVE_GAP = (int) v, "ticks between waves");
        i("loop.fortify_ticks", () -> Loop.FORTIFY_TICKS, v -> Loop.FORTIFY_TICKS = (int) v, "online ticks a held site gets before the counterattack");
        i("loop.warning_ticks", () -> Loop.WARNING_TICKS, v -> Loop.WARNING_TICKS = (int) v, "the radio warning comes this long before it");
        i("loop.defence_waves", () -> Loop.DEFENCE_WAVES, v -> Loop.DEFENCE_WAVES = (int) v, "waves in a counterattack");
        i("loop.straggler_ticks", () -> Loop.STRAGGLER_TICKS, v -> Loop.STRAGGLER_TICKS = (int) v, "after the last wave, stragglers are cleared after this long");
        i("loop.loss_count", () -> Loop.LOSS_COUNT, v -> Loop.LOSS_COUNT = (int) v, "attackers in the camp square that lose the gate");
        i("loop.loss_ticks", () -> Loop.LOSS_TICKS, v -> Loop.LOSS_TICKS = (int) v, "for this long");
        i("loop.guard_target", () -> Loop.GUARD_TARGET, v -> Loop.GUARD_TARGET = (int) v, "site guard size once held (doubled when defended)");
        i("loop.away_range", () -> Loop.AWAY_RANGE, v -> Loop.AWAY_RANGE = (int) v, "nobody this close to the fight: the clock waits");
        i("loop.away_ticks", () -> Loop.AWAY_TICKS, v -> Loop.AWAY_TICKS = (int) v, "and after this long away the wave is taken back");
        // squads
        i("squads.max_size", () -> Squad.MAX_SIZE, v -> Squad.MAX_SIZE = (int) v, "fighters in one squad, at most");
        i("squads.bound_every_ticks", () -> Squad.BOUND_EVERY, v -> Squad.BOUND_EVERY = (int) v, "bounding teams swap this often");
        d("squads.bound_step", () -> Squad.BOUND_STEP, v -> Squad.BOUND_STEP = v, "blocks a bounding team advances");
        d("squads.fall_back_blocks", () -> Squad.FALL_BACK_DIST, v -> Squad.FALL_BACK_DIST = v, "how far the fall-back goes");
        i("squads.fall_back_every_ticks", () -> Squad.FALL_BACK_EVERY, v -> Squad.FALL_BACK_EVERY = (int) v, "a squad falls back at most this often");
        d("squads.patrol_near", () -> Squad.PATROL_NEAR, v -> Squad.PATROL_NEAR = v, "a patrol walks only with someone this close");
        // the fight
        d("fight.hold_factor", () -> GunAttackGoal.HOLD_FACTOR, v -> GunAttackGoal.HOLD_FACTOR = v, "cover is taken and bounding stops inside range x hold_at x this");
        i("fight.reload_ticks", () -> GunAttackGoal.RELOAD_TICKS, v -> GunAttackGoal.RELOAD_TICKS = (int) v, "a magazine change");
        d("fight.marksman_prone_dist", () -> GunAttackGoal.MARKSMAN_PRONE_DIST, v -> GunAttackGoal.MARKSMAN_PRONE_DIST = v, "the Marksman goes flat beyond this, in the open");
        d("fight.marksman_min_dist", () -> GunAttackGoal.MARKSMAN_MIN_DIST, v -> GunAttackGoal.MARKSMAN_MIN_DIST = v, "and backs away inside this");
        d("fight.crouch_fire_dist", () -> GunAttackGoal.CROUCH_FIRE_DIST, v -> GunAttackGoal.CROUCH_FIRE_DIST = v, "crouched to fire beyond this");
        d("fight.crouch_at", () -> GunAttackGoal.CROUCH_AT, v -> GunAttackGoal.CROUCH_AT = (float) v, "suppression that puts a fighter on one knee");
        d("fight.pinned_at", () -> GunAttackGoal.PINNED_AT, v -> GunAttackGoal.PINNED_AT = (float) v, "suppression that pins it flat");
        i("fight.cover_lost_ticks", () -> GunAttackGoal.COVER_LOST_TICKS, v -> GunAttackGoal.COVER_LOST_TICKS = (int) v, "cover seen into for this long is dropped");
        i("fight.cover_travel_ticks", () -> GunAttackGoal.COVER_TRAVEL_TICKS, v -> GunAttackGoal.COVER_TRAVEL_TICKS = (int) v, "cover not reached in this long is dropped");
        i("fight.suppress_ticks", () -> GunAttackGoal.SUPPRESS_TICKS, v -> GunAttackGoal.SUPPRESS_TICKS = (int) v, "the Gunner keeps firing at a lost target for this long");
        i("cover.samples", () -> Cover.SAMPLES, v -> Cover.SAMPLES = (int) v, "spots tried per search");
        // the damage model
        d("damage.zone.head", () -> Damage.HEAD, v -> Damage.HEAD = (float) v, "a head hit's multiplier");
        d("damage.zone.thorax", () -> Damage.THORAX, v -> Damage.THORAX = (float) v, "a thorax hit's");
        d("damage.zone.stomach", () -> Damage.STOMACH, v -> Damage.STOMACH = (float) v, "a stomach hit's (it bleeds)");
        d("damage.zone.arms", () -> Damage.ARMS, v -> Damage.ARMS = (float) v, "an arm hit's (slow aim)");
        d("damage.zone.legs", () -> Damage.LEGS, v -> Damage.LEGS = (float) v, "a leg hit's (a crawl)");
        d("damage.pen_keep", () -> Damage.PEN_KEEP, v -> Damage.PEN_KEEP = (float) v, "share of the zone damage a round that goes through a piece leaves");
        d("damage.blunt", () -> Damage.BLUNT, v -> Damage.BLUNT = (float) v, "share a stopped round leaves");
        d("damage.blast_per_class", () -> Damage.BLAST_PER_CLASS, v -> Damage.BLAST_PER_CLASS = (float) v, "a blast loses this much per class of the vest");
        d("damage.blast_plate_spend", () -> Damage.BLAST_PLATE_SPEND, v -> Damage.BLAST_PLATE_SPEND = (float) v, "share of a blast the plate pays in points");
        i("damage.crawl_ticks", () -> Damage.CRAWL_TICKS, v -> Damage.CRAWL_TICKS = (int) v, "a fighter's leg wound");
        i("damage.arm_ticks", () -> Damage.ARM_TICKS, v -> Damage.ARM_TICKS = (int) v, "a fighter's arm wound");
        i("damage.bleed_ticks", () -> Damage.BLEED_TICKS, v -> Damage.BLEED_TICKS = (int) v, "a fighter's bleed");
        i("damage.bleed_every", () -> Damage.BLEED_EVERY, v -> Damage.BLEED_EVERY = (int) v, "ticks between bleed hits");
        d("damage.bleed_damage", () -> Damage.BLEED_DAMAGE, v -> Damage.BLEED_DAMAGE = (float) v, "each bleed hit");
        i("damage.player_leg_ticks", () -> PlayerWounds.PLAYER_LEG_TICKS, v -> PlayerWounds.PLAYER_LEG_TICKS = (int) v, "a player's leg wound, untreated");
        i("damage.player_arm_ticks", () -> PlayerWounds.PLAYER_ARM_TICKS, v -> PlayerWounds.PLAYER_ARM_TICKS = (int) v, "a player's arm wound, untreated");
        i("damage.player_bleed_ticks", () -> PlayerWounds.PLAYER_BLEED_TICKS, v -> PlayerWounds.PLAYER_BLEED_TICKS = (int) v, "a player's bleed, untreated");
        d("damage.head_below_eyes", () -> Ballistics.HEAD_BELOW_EYES, v -> Ballistics.HEAD_BELOW_EYES = v, "the head reaches this far below the eyes");
        d("damage.thorax_bottom", () -> Ballistics.THORAX_BOTTOM, v -> Ballistics.THORAX_BOTTOM = v, "fraction of height where the thorax ends");
        d("damage.stomach_bottom", () -> Ballistics.STOMACH_BOTTOM, v -> Ballistics.STOMACH_BOTTOM = v, "fraction of height where the stomach ends and the legs begin");
        d("damage.arm_share", () -> Ballistics.ARM_SHARE, v -> Ballistics.ARM_SHARE = v, "outer share of the half-width that is an arm");
        i("damage.bandage_ticks", () -> BandageItem.USE_TICKS, v -> BandageItem.USE_TICKS = (int) v, "how long a bandage takes");
        d("damage.bandage_heal", () -> BandageItem.HEAL, v -> BandageItem.HEAL = (float) v, "what it heals");
        d("cover.min_r", () -> Cover.MIN_R, v -> Cover.MIN_R = v, "nearest cover looked for");
        d("cover.max_r", () -> Cover.MAX_R, v -> Cover.MAX_R = v, "furthest");
        d("cover.lean", () -> Cover.LEAN, v -> Cover.LEAN = v, "how far the lean steps out");
        d("cover.too_close", () -> Cover.TOO_CLOSE, v -> Cover.TOO_CLOSE = v, "no cover this close to the target");
        d("grenades.min_dist", () -> GrenadeGoal.MIN_DIST, v -> GrenadeGoal.MIN_DIST = v, "grenades thrown at targets at least this far");
        d("grenades.max_dist", () -> GrenadeGoal.MAX_DIST, v -> GrenadeGoal.MAX_DIST = v, "and at most this far");
        i("grenades.cooldown_ticks", () -> GrenadeGoal.COOLDOWN, v -> GrenadeGoal.COOLDOWN = (int) v, "between throws by one fighter");
        d("grenades.chance", () -> GrenadeGoal.CHANCE_IN_THE_OPEN, v -> GrenadeGoal.CHANCE_IN_THE_OPEN = (float) v, "chance per check at a visible target");
        i("callouts.throttle_ticks", () -> Callouts.THROTTLE, v -> Callouts.THROTTLE = (int) v, "one line per fighter per key this often");
        d("callouts.earshot", () -> Callouts.EARSHOT, v -> Callouts.EARSHOT = v, "players this close read it");
        d("callouts.area", () -> Callouts.AREA, v -> Callouts.AREA = v, "one voice per this many blocks");
        i("callouts.area_ticks", () -> Callouts.AREA_TICKS, v -> Callouts.AREA_TICKS = (int) v, "per this long");
        d("sounds.loud", () -> WarEvents.LOUD, v -> WarEvents.LOUD = v, "a shot is heard by fighters this far");
        d("sounds.silenced", () -> WarEvents.SILENCED, v -> WarEvents.SILENCED = v, "a silenced one");
        i("projectiles.max_age_ticks", () -> ProjectileSweep.DEFAULT_MAX_AGE, v -> ProjectileSweep.setDefaultMaxAge((int) v), "projectiles older than this are retired");
        for (Role role : Role.values()) {
            String p = "roles." + role.name().toLowerCase(Locale.ROOT) + ".";
            d(p + "range", () -> role.range, v -> role.range = (float) v, "furthest a target is engaged");
            i(p + "aim_ticks", () -> role.aimTicks, v -> role.aimTicks = (int) v, "sight needed before the first shot");
            i(p + "burst_min", () -> role.burstMin, v -> role.burstMin = (int) v, "shots per burst, at least");
            i(p + "burst_max", () -> role.burstMax, v -> role.burstMax = (int) v, "at most");
            i(p + "pause_min", () -> role.pauseMin, v -> role.pauseMin = (int) v, "ticks between bursts, at least");
            i(p + "pause_max", () -> role.pauseMax, v -> role.pauseMax = (int) v, "at most");
            d(p + "spread", () -> role.spread, v -> role.spread = (float) v, "degrees of scatter");
            d(p + "hold_at", () -> role.holdAt, v -> role.holdAt = (float) v, "fraction of range where it stops closing in");
        }
    }

    /** the code's own numbers, captured once so a reload starts from them and not from the last file */
    private static final Map<String, Double> DEFAULTS = new LinkedHashMap<>();

    static {
        ENTRIES.forEach((k, e) -> DEFAULTS.put(k, e.get().getAsDouble()));
    }

    public Settings() {
        super(GSON, "gscraft_settings");
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager resources, ProfilerFiller profiler) {
        DEFAULTS.forEach((k, v) -> ENTRIES.get(k).set().accept(v));
        applied.clear();
        int set = 0;
        List<ResourceLocation> order = new ArrayList<>(files.keySet());
        order.sort((a, b) -> a.getPath().compareTo(b.getPath()));
        for (ResourceLocation id : order) {
            JsonElement root = files.get(id);
            if (!root.isJsonObject()) continue;
            int n = walk("", root.getAsJsonObject(), id);
            set += n;
            applied.add(id.getPath() + " (" + n + ")");
        }
        GscraftWar.LOG.info("[gscraft] settings: {} values from {}", set, applied);
    }

    private static int walk(String prefix, JsonObject o, ResourceLocation id) {
        int n = 0;
        for (Map.Entry<String, JsonElement> kv : o.entrySet()) {
            String path = prefix.isEmpty() ? kv.getKey() : prefix + "." + kv.getKey();
            JsonElement v = kv.getValue();
            if (v.isJsonObject()) {
                n += walk(path, v.getAsJsonObject(), id);
            } else if (v instanceof JsonPrimitive p && p.isNumber()) {
                Entry e = ENTRIES.get(path);
                if (e == null) {
                    GscraftWar.LOG.warn("[gscraft] settings {}: no setting named {}", id, path);
                    continue;
                }
                e.set().accept(p.getAsDouble());
                n++;
            } else if (!path.startsWith("_")) {
                GscraftWar.LOG.warn("[gscraft] settings {}: {} is not a number", id, path);
            }
        }
        return n;
    }

    /** every setting in force, one per line: path = value (default) - doc */
    public static List<String> describe(String filter) {
        List<String> out = new ArrayList<>();
        ENTRIES.forEach((k, e) -> {
            if (filter != null && !k.startsWith(filter)) return;
            double v = e.get().getAsDouble();
            double def = DEFAULTS.get(k);
            String val = e.whole() ? Integer.toString((int) v) : trim(v);
            String d = e.whole() ? Integer.toString((int) def) : trim(def);
            out.add(k + " = " + val + (v != def ? " (default " + d + ")" : "") + " - " + e.doc());
        });
        return out;
    }

    public static List<String> applied() {
        return List.copyOf(applied);
    }

    private static String trim(double v) {
        String s = String.format(Locale.ROOT, "%.3f", v);
        return s.contains(".") ? s.replaceAll("0+$", "").replaceAll("\\.$", "") : s;
    }
}
