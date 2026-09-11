package gscraft.war.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Mob;

/**
 * The rank a fighter was issued and what it has left, saved with the entity. {@code GscraftRank} on a summon pins
 * the rank to issue - the director and the tests both use that - and {@code GscraftKitIssued} pins the whole
 * loadout as summoned.
 */
public final class FighterState {
    public boolean kitIssued;
    public String rank = "";
    public Role role;
    public int magazines;
    public int grenades;
    public boolean outOfAmmo;
    /** under fire, 0 to 1; not saved - it decays in seconds (feasibility A4) */
    public float suppression;
    /** game time the next grenade may be thrown */
    public long nextGrenade;
    /** a garrison member's post; radius 0 means it roams */
    public BlockPos home = BlockPos.ZERO;
    public int homeRadius;

    public FighterState(Role defaultRole) {
        this.role = defaultRole;
    }

    public void apply(RankDef r) {
        rank = r.name();
        role = r.role();
        magazines = r.magazines();
        grenades = r.grenades();
        outOfAmmo = false;
        kitIssued = true;
    }

    public void save(CompoundTag tag) {
        tag.putBoolean("GscraftKitIssued", kitIssued);
        tag.putString("GscraftRank", rank);
        tag.putString("GscraftRole", role.name());
        tag.putInt("GscraftMagazines", magazines);
        tag.putInt("GscraftGrenades", grenades);
        tag.putBoolean("GscraftOutOfAmmo", outOfAmmo);
        if (homeRadius > 0) {
            tag.putLong("GscraftHome", home.asLong());
            tag.putInt("GscraftHomeRadius", homeRadius);
        }
    }

    public void load(CompoundTag tag) {
        kitIssued = tag.getBoolean("GscraftKitIssued");
        rank = tag.getString("GscraftRank");
        if (tag.contains("GscraftRole")) role = Role.parse(tag.getString("GscraftRole"));
        if (tag.contains("GscraftMagazines")) magazines = tag.getInt("GscraftMagazines");
        grenades = tag.getInt("GscraftGrenades");
        outOfAmmo = tag.getBoolean("GscraftOutOfAmmo");
        if (tag.contains("GscraftHomeRadius")) {
            home = BlockPos.of(tag.getLong("GscraftHome"));
            homeRadius = tag.getInt("GscraftHomeRadius");
        }
    }

    /** a burst of fire nearby, or a hit: the value rises and decays over three seconds */
    public void suppress(float amount) {
        suppression = Math.min(1.0F, suppression + amount);
    }

    public void decaySuppression() {
        if (suppression > 0.0F) suppression = Math.max(0.0F, suppression - 1.0F / 60.0F);
    }

    /** re-bind the mob to its post; restrictTo itself is not saved by vanilla */
    public void applyHome(Mob mob) {
        if (homeRadius > 0) mob.restrictTo(home, homeRadius);
    }
}
