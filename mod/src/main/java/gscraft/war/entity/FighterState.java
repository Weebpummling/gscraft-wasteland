package gscraft.war.entity;

import net.minecraft.nbt.CompoundTag;

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
    public boolean outOfAmmo;

    public FighterState(Role defaultRole) {
        this.role = defaultRole;
    }

    public void apply(RankDef r) {
        rank = r.name();
        role = r.role();
        magazines = r.magazines();
        outOfAmmo = false;
        kitIssued = true;
    }

    public void save(CompoundTag tag) {
        tag.putBoolean("GscraftKitIssued", kitIssued);
        tag.putString("GscraftRank", rank);
        tag.putString("GscraftRole", role.name());
        tag.putInt("GscraftMagazines", magazines);
        tag.putBoolean("GscraftOutOfAmmo", outOfAmmo);
    }

    public void load(CompoundTag tag) {
        kitIssued = tag.getBoolean("GscraftKitIssued");
        rank = tag.getString("GscraftRank");
        if (tag.contains("GscraftRole")) role = Role.parse(tag.getString("GscraftRole"));
        if (tag.contains("GscraftMagazines")) magazines = tag.getInt("GscraftMagazines");
        outOfAmmo = tag.getBoolean("GscraftOutOfAmmo");
    }
}
