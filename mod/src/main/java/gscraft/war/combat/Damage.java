package gscraft.war.combat;

import gscraft.war.entity.FighterState;
import gscraft.war.entity.GunUser;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

import java.util.Locale;

/**
 * The damage model (docs/gscraft-damage-model-feasibility-2026-09-11.md): vanilla health stays the pool; the
 * zone, the piece over it and its plate decide how much of a hit reaches it. A round whose penetration class
 * reaches the piece's class goes through and the body takes PEN_KEEP of the zone damage; a round the piece
 * stops leaves BLUNT; either way the plate loses the round's base damage in points, and at zero the piece is
 * cloth. Plate points live on the worn item: the chest under Superb Warfare's own "ArmorPlate" key so a
 * player's HUD shows it and their plate items refill it, the helmet under "GscraftPlate". A body wearing at
 * least one known piece is judged by this model alone for bullets - vanilla armour is bypassed for it; a body
 * with none (the Dead, animals) gets the zone multiplier and vanilla armour as before.
 */
public final class Damage {
    public static float HEAD = 3.5F;
    public static float THORAX = 1.0F;
    public static float STOMACH = 1.1F;
    public static float ARMS = 0.6F;
    public static float LEGS = 0.5F;
    public static float PEN_KEEP = 0.85F;
    public static float BLUNT = 0.3F;
    /** a blast against a vest: the body keeps 1 - class x this */
    public static float BLAST_PER_CLASS = 0.1F;
    public static float BLAST_PLATE_SPEND = 0.5F;
    public static int CRAWL_TICKS = 300;
    public static int ARM_TICKS = 400;
    public static int BLEED_TICKS = 200;
    public static int BLEED_EVERY = 40;
    public static float BLEED_DAMAGE = 1.0F;
    public static final String CHEST_PLATE_TAG = "ArmorPlate";
    public static final String HEAD_PLATE_TAG = "GscraftPlate";

    private Damage() {}

    public record Result(Zone zone, float damage, boolean modelled, boolean stopped, EquipmentSlot slot, int plateLeft, int plateWas) {
        public String describe() {
            String s = zone.name().toLowerCase(Locale.ROOT) + " " + String.format(Locale.ROOT, "%.1f", damage);
            if (slot != null) s += (stopped ? " stopped by " : " through ") + slot.getName() + " plate " + plateWas + "->" + plateLeft;
            else if (!modelled) s += " (vanilla armour)";
            return s;
        }
    }

    /** whether this body is judged by the model: it wears at least one piece the armour data knows */
    public static boolean modelled(LivingEntity target) {
        return ArmorData.of(target.getItemBySlot(EquipmentSlot.HEAD)) != null || ArmorData.of(target.getItemBySlot(EquipmentSlot.CHEST)) != null;
    }

    /** a bullet of this base damage and penetration class landing in this zone */
    public static Result bullet(LivingEntity target, Zone zone, float base, int penetration) {
        float d = base * zone.multiplier();
        boolean modelled = modelled(target);
        EquipmentSlot slot = zone == Zone.HEAD ? EquipmentSlot.HEAD : (zone == Zone.THORAX || zone == Zone.STOMACH) ? EquipmentSlot.CHEST : null;
        if (slot == null) return new Result(zone, d, modelled, false, null, 0, 0);
        ItemStack piece = target.getItemBySlot(slot);
        ArmorData.Piece data = ArmorData.of(piece);
        if (data == null) return new Result(zone, d, modelled, false, null, 0, 0);
        int was = plate(piece, slot, data);
        if (was <= 0) return new Result(zone, d, modelled, false, slot, 0, 0);
        boolean stopped = penetration < data.armorClass();
        d *= stopped ? BLUNT : PEN_KEEP;
        int left = Math.max(0, was - Math.round(base));
        setPlate(piece, slot, left);
        return new Result(zone, d, modelled, stopped, slot, left, was);
    }

    /** a blast: no zone; the vest's class keeps a share of it off the body and the plate takes half the hit */
    public static Result blast(LivingEntity target, float amount) {
        ItemStack piece = target.getItemBySlot(EquipmentSlot.CHEST);
        ArmorData.Piece data = ArmorData.of(piece);
        boolean modelled = modelled(target);
        if (data == null) return new Result(Zone.THORAX, amount, modelled, false, null, 0, 0);
        int was = plate(piece, EquipmentSlot.CHEST, data);
        if (was <= 0) return new Result(Zone.THORAX, amount, modelled, false, EquipmentSlot.CHEST, 0, 0);
        float keep = Math.max(0.2F, 1.0F - data.armorClass() * BLAST_PER_CLASS);
        int left = Math.max(0, was - Math.round(amount * BLAST_PLATE_SPEND));
        setPlate(piece, EquipmentSlot.CHEST, left);
        return new Result(Zone.THORAX, amount * keep, modelled, true, EquipmentSlot.CHEST, left, was);
    }

    /** the plate points on a worn piece; a piece never hit yet carries its full points */
    public static int plate(ItemStack piece, EquipmentSlot slot, ArmorData.Piece data) {
        CompoundTag tag = piece.getOrCreateTag();
        String key = slot == EquipmentSlot.HEAD ? HEAD_PLATE_TAG : CHEST_PLATE_TAG;
        if (!tag.contains(key)) {
            setPlate(piece, slot, data.points());
            return data.points();
        }
        return slot == EquipmentSlot.HEAD ? tag.getInt(key) : (int) Math.round(tag.getDouble(key));
    }

    public static void setPlate(ItemStack piece, EquipmentSlot slot, int points) {
        CompoundTag tag = piece.getOrCreateTag();
        if (slot == EquipmentSlot.HEAD) tag.putInt(HEAD_PLATE_TAG, points);
        else tag.putDouble(CHEST_PLATE_TAG, points);
    }

    /** the wound a zone leaves: a fighter crawls, aims slowly or bleeds; a player the same until bandaged */
    public static void wound(LivingEntity target, Zone zone) {
        long now = target.level().getGameTime();
        if (target instanceof GunUser user) {
            FighterState s = user.fighterState();
            switch (zone) {
                case LEGS -> s.crawlUntil = now + CRAWL_TICKS;
                case ARMS -> s.armUntil = now + ARM_TICKS;
                case STOMACH -> s.bleedTicks = Math.max(s.bleedTicks, BLEED_TICKS);
                default -> { }
            }
        } else if (target instanceof Player player) {
            PlayerWounds.wound(player, zone);
        }
    }

    public static void record(LivingEntity target, Result r, String how) {
        if (target instanceof GunUser user) user.fighterState().lastHit = how + ": " + r.describe();
    }
}
