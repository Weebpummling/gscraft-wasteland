package gscraft.war.entity;

import gscraft.war.GscraftWar;
import gscraft.war.faction.Factions;
import gscraft.war.world.Director;
import gscraft.war.world.Zone;
import gscraft.war.world.Zones;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;

/**
 * Squads (feasibility C1–C4). A squad is a shared id and a slot on each body; nothing else is stored. The leader is
 * slot 0 while it lives, else the lowest slot alive. Out of a fight the members walk to their slots around the
 * leader ({@link SquadFollowGoal}) while the leader walks a patrol route from its zone ({@link PatrolGoal}). In a
 * fight the leader, once a second, bounds the squad toward a distant target - one team of alternate slots advances
 * eight blocks while the other holds and fires, then they swap - and calls the fall-back when the squad is under
 * half strength or pinned: everyone to a point twenty blocks away from the target, then hold.
 */
public final class Squad {
    public enum Formation { WEDGE, LINE, COLUMN }

    private static final double REACH = 64.0D;
    private static final int BOUND_EVERY = 80;
    private static final double BOUND_STEP = 8.0D;
    private static final double FALL_BACK_DIST = 20.0D;
    private static final int FALL_BACK_EVERY = 1200;
    private static final int PATROL_PICKUP_EVERY = 200;
    /** a patrol walks only with a player (or a phantom) this close; beyond it, it would only walk into the sweep */
    public static final double PATROL_NEAR = 96.0D;
    public static final int MAX_SIZE = 6;

    private Squad() {}

    /** one squad out of these fighters: slot 0 to a Sergeant if there is one; the others in the order given */
    public static UUID form(List<? extends Mob> fighters) {
        List<Mob> list = new ArrayList<>();
        for (Mob m : fighters) {
            if (m instanceof GunUser) list.add(m);
        }
        if (list.size() < 2) return null;
        list.sort(Comparator.comparingInt(m -> ((GunUser) m).role() == Role.SERGEANT ? 0 : 1));
        UUID id = UUID.randomUUID();
        for (int i = 0; i < list.size(); i++) {
            FighterState s = ((GunUser) list.get(i)).fighterState();
            s.squadId = id;
            s.slot = i;
            s.squadSize = list.size();
            s.formation = Formation.WEDGE;
        }
        return id;
    }

    /** the living members of this fighter's squad within reach, this fighter included */
    public static List<Mob> members(ServerLevel level, Mob any) {
        FighterState s = ((GunUser) any).fighterState();
        if (s.squadId == null) return List.of(any);
        UUID id = s.squadId;
        List<Mob> found = level.getEntitiesOfClass(Mob.class, any.getBoundingBox().inflate(REACH),
                m -> m.isAlive() && m instanceof GunUser g && id.equals(g.fighterState().squadId));
        found.sort(Comparator.comparingInt(m -> ((GunUser) m).fighterState().slot));
        return found;
    }

    public static Mob leader(ServerLevel level, Mob any) {
        List<Mob> members = members(level, any);
        return members.isEmpty() ? any : members.get(0);
    }

    public static boolean isLeader(ServerLevel level, Mob mob) {
        return leader(level, mob) == mob;
    }

    /** where a slot stands relative to the leader's heading */
    public static Vec3 slotPosition(Mob leader, Formation formation, int slot) {
        if (slot <= 0) return leader.position();
        double yaw = Math.toRadians(leader.getYRot());
        Vec3 forward = new Vec3(-Math.sin(yaw), 0.0D, Math.cos(yaw));
        Vec3 right = new Vec3(Math.cos(yaw), 0.0D, Math.sin(yaw));
        int pair = (slot + 1) / 2;
        double side = slot % 2 == 1 ? -1.0D : 1.0D;
        return switch (formation) {
            case WEDGE -> leader.position().add(right.scale(side * 2.0D * pair)).subtract(forward.scale(2.0D * pair));
            case LINE -> leader.position().add(right.scale(side * 2.5D * pair));
            case COLUMN -> leader.position().subtract(forward.scale(2.5D * slot));
        };
    }

    /** the leader's second: bounding, the fall-back, the patrol pickup. Called by the body once a second. */
    public static void leaderTick(Mob leader) {
        if (!(leader.level() instanceof ServerLevel level)) return;
        FighterState ls = ((GunUser) leader).fighterState();
        if (ls.squadId == null) return;
        List<Mob> members = members(level, leader);
        if (members.isEmpty() || members.get(0) != leader) return;
        long now = level.getGameTime();
        LivingEntity target = leader.getTarget();
        if (target == null || !target.isAlive()) {
            releaseSquadOrders(members);
            pickUpPatrol(level, leader, ls, now);
            return;
        }
        int alive = members.size();
        int suppressed = 0;
        for (Mob m : members) {
            if (((GunUser) m).fighterState().suppression >= 0.5F) suppressed++;
        }
        boolean weak = alive * 2 < ls.squadSize || (ls.suppression >= 0.6F && suppressed * 2 >= alive);
        if (weak && now < ls.nextFallBack) return;   // a squad that fell back holds where it got to; it does not bound again
        if (weak) {
            Vec3 away = leader.position().subtract(target.position());
            away = away.lengthSqr() < 1.0E-4D ? new Vec3(1.0D, 0.0D, 0.0D) : new Vec3(away.x, 0.0D, away.z).normalize();
            BlockPos point = stand(level, leader.position().add(away.scale(FALL_BACK_DIST)));
            for (Mob m : members) give(m, FighterState.Order.ADVANCE, point);
            ls.nextFallBack = now + FALL_BACK_EVERY;
            Callouts.say(leader, "fall_back");
            GscraftWar.LOG.info("[gscraft] squad of {} falls back to {} ({} alive of {}, {} suppressed)", leader.getName().getString(),
                    point.toShortString(), alive, ls.squadSize, suppressed);
            return;
        }
        Role role = ((GunUser) leader).role();
        double hold = role.range * role.holdAt;
        double dist = leader.distanceTo(target);
        if (dist > hold * 1.2D && alive >= 2) {
            // bounding overwatch: alternate teams by slot parity, swapping every four seconds
            if (now >= ls.nextBound) {
                ls.boundTeam ^= 1;
                ls.nextBound = now + BOUND_EVERY;
            }
            for (Mob m : members) {
                FighterState s = ((GunUser) m).fighterState();
                if ((s.slot & 1) == ls.boundTeam) {
                    Vec3 to = target.position().subtract(m.position());
                    to = new Vec3(to.x, 0.0D, to.z).normalize().scale(BOUND_STEP);
                    give(m, FighterState.Order.ADVANCE, stand(level, m.position().add(to)));
                } else if (s.order != FighterState.Order.HOLD || !s.orderBySquad) {
                    give(m, FighterState.Order.HOLD, m.blockPosition());
                }
            }
        } else {
            releaseSquadOrders(members);
        }
    }

    private static void give(Mob m, FighterState.Order order, BlockPos at) {
        FighterState s = ((GunUser) m).fighterState();
        if (s.order != FighterState.Order.NONE && !s.orderBySquad) return;   // the operator's order stands
        s.order = order;
        s.orderPos = at;
        s.orderBySquad = true;
    }

    private static void releaseSquadOrders(List<Mob> members) {
        for (Mob m : members) {
            FighterState s = ((GunUser) m).fighterState();
            if (s.orderBySquad) {
                s.order = FighterState.Order.NONE;
                s.orderBySquad = false;
            }
        }
    }

    private static BlockPos stand(ServerLevel level, Vec3 at) {
        BlockPos raw = BlockPos.containing(at);
        BlockPos found = Director.nearestStand(level, raw);
        return found != null ? found : raw;
    }

    /** an idle leader in a zone with patrol routes takes the nearest one, from its nearest waypoint */
    private static void pickUpPatrol(ServerLevel level, Mob leader, FighterState ls, long now) {
        if (!ls.route.isEmpty() || ls.order != FighterState.Order.NONE || now < ls.nextPatrolPickup) return;
        ls.nextPatrolPickup = now + PATROL_PICKUP_EVERY;
        if (!someoneNear(level, leader)) return;
        Zone zone = Zones.at(leader.getX(), leader.getZ());
        if (zone == null || zone.patrols().isEmpty()) return;
        List<BlockPos> best = null;
        int bestIndex = 0;
        double bestDist = Double.MAX_VALUE;
        for (List<BlockPos> route : zone.patrols()) {
            for (int i = 0; i < route.size(); i++) {
                double d = route.get(i).distSqr(leader.blockPosition());
                if (d < bestDist) {
                    bestDist = d;
                    best = route;
                    bestIndex = i;
                }
            }
        }
        if (best == null) return;
        ls.route = new ArrayList<>(best);
        ls.routeIndex = bestIndex;
        GscraftWar.LOG.info("[gscraft] squad of {} patrols {}'s route from waypoint {}", leader.getName().getString(), zone.name(), bestIndex);
    }

    public static boolean someoneNear(ServerLevel level, Mob mob) {
        return Director.anyoneWithin(level, mob.getX(), mob.getZ(), PATROL_NEAR);
    }

    /** the fighter's own squad, or a new one with every ally within twenty blocks */
    public static UUID formAround(ServerLevel level, Mob fighter) {
        List<Mob> allies = level.getEntitiesOfClass(Mob.class, fighter.getBoundingBox().inflate(20.0D),
                m -> m != fighter && m instanceof GunUser && Factions.allied(m, fighter));
        List<Mob> list = new ArrayList<>();
        list.add(fighter);
        list.addAll(allies.subList(0, Math.min(allies.size(), MAX_SIZE - 1)));
        return form(list);
    }

    public static AABB reach(Mob any) {
        return any.getBoundingBox().inflate(REACH);
    }
}
