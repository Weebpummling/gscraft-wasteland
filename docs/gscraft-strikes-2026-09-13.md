# The fire missions — a design pass, 2026-09-13

*The owner's ask: an item that calls in a mortar strike (a delay, a spotting round, a short barrage), earned by a
repeatable quest that hands in shells, after a questline that builds a mortar in the compound; upgraded to an
artillery strike once the strongpoints' guns stand; and an air strike by an AH-1 on a smoke grenade after thirty
seconds. A global cooldown, and everyone told. Three special grenades. This note is the design; the build is in the
mod (`gscraft.war.strike`) and the book (`tools/chapters.py`), tested by phase 38. The system document's rulings
R31-R32 point here.*

## 1. What the pack has to fire

Superb Warfare 0.8.9 ships the rounds and the sounds; DragonRise: Reforge ships the airframe. Nothing new is modelled.

| Round | Entity | Item (the hand-in) | Used by |
|---|---|---|---|
| Mortar shell (HE, WP) | `superbwarfare:mortar_shell` | `superbwarfare:mortar_shell`, `mortar_shell_wp` | the mortar strike |
| Cannon shell (AP, HE, CM, WP) | `superbwarfare:cannon_shell` | `superbwarfare:large_shell_he` (the Mle 1934's) | the artillery strike |
| Small cannon shell | `superbwarfare:small_cannon_shell` | `small_shell_he` (the Mk 42's) | — (a lighter gun later) |
| Medium rocket (AP, HE, CM) | `superbwarfare:medium_rocket` | `superbwarfare:medium_rocket_he` | the Cobra's salvo |
| Small rocket | `superbwarfare:small_rocket` | `superbwarfare:small_rocket` | — (the AH-6's pods) |
| Cannon round | `superbwarfare:projectile` | — | the Cobra's guns |
| Aerial bombs, Mk 82 | `superbwarfare:mk_82`, `melon_bomb` | `small/medium_aerial_bomb` | — (a bomber, later) |

Airframes: `dragonrise_reforge:ah1f` (**AH-1F Cobra**, the one asked for), `dragonrise_reforge:ah64`,
`superbwarfare:ah_6`, `fcp:littlebird_armed`, `fcp:viper`. The Cobra is a Superb Warfare vehicle entity, so the mod's
health readers work on it; it is flown as a prop (its position set every tick), never by a pilot.

Every round is spawned **in flight above the target**, seventy blocks up and falling, with our numbers for damage,
blast and radius set through the mod's own setters (reflection, as the vehicles do: Superb Warfare is not a compile
dependency). So the sound, the trail, the blast and the block damage are the mod's, and the config that tamed the
explosions (`tools/armour_override.py`) tames these too. The mortar's own `mortar` entity stays out of it: the tube in
the yard is dressing and a station order's excuse, not the thing that fires.

## 2. The three grenades

All three are thrown like a snowball. Where one lands it stays as a **column of coloured smoke** until the rounds have
come (orange for the tube, red for the guns, violet for the Cobra) - the target everyone can see - and the call goes
out. A grenade thrown while the tube is hot is refused in the hand, Marshall says so, and nothing is spent; one that
lands during another's window drops back on the ground.

| | Fire mission: mortar | Fire mission: guns | Air support: Cobra |
|---|---|---|---|
| Item | `gscraft:strike_mortar` | `gscraft:strike_artillery` | `gscraft:strike_air` |
| Cooldown (its own) | 3:00 | 5:00 | 8:00 |
| Delay to the first round | **15 s** | 20 s | 20 s to the airframe (owner, 2026-09-13: was 30) |
| Then | a spotting round (half strength); 4 s; **six rounds**, 1.5 s apart, within 6 blocks | a spotting round; 5 s; **eight heavy rounds**, 1.25 s apart, within 12 blocks | from 150 blocks out **about 29 rockets** in pairs converging on the smoke; over the smoke **five seconds of guns** on anything hostile within 12 |
| Blast per round | 80, radius 5 | 160, radius 9 | rockets 120, radius 6; a cannon round 14 |
| On a hull (the vehicle rules multiply: `tools/armour_override.py`) | 0.6x on light, 0.4x on heavy (`@mortar_shell 1.5`) | **1.2x on light, 0.75x on heavy** (`@cannon_shell 3`): a BMP dies to one round on the smoke, a T-90 to three | rockets 0.8x light, 0.5x heavy (`@medium_rocket 2`): two rockets for a BMP; the guns nothing to a hull |
| Breaks off | never | never | a hit on the helicopter: it flies straight out |
| Ends | the last round | the last round | 300 blocks past the smoke the Cobra is unloaded |
| The line | Marshall: *fire mission on the smoke, fifteen seconds* | Marshall: *guns on the smoke, fire for effect* | Marshall: *Cobra's up, twenty seconds, heads down* |
| Then | Tune: *splash, rounds following* | Tune: *splash* | Tune: *breaking off* / *off station* / *we lost the Cobra* |

**A cooldown per grenade** (owner, 2026-09-13: not one for all): the tube three minutes, the guns five, the Cobra eight
(`strike.cooldown_mortar|artillery|air`), each counted from its own last call, so a mortar call does not stop the guns.
The refusal comes in the right voice: Marshall for the tube and the guns, Tune for the Cobra. The console's
`/gscraft strike status|reset` reads and clears all three. Every number above is a setting (`strike.*`).

**The Cobra is crewed** (owner, 2026-09-13: "why not have it crewed like the other vehicles and fired from inside"): a crew
of the camp's faction sits in the seat, so the mod treats the airframe as manned (the rotor and the engine sound are its
own), and two crews sit in it: the pilot in seat 0 and a second in seat 1, which is the airframe's turret seat (the chin gun,
-40° to +10°). The turret crew lays and fires the 30 mm at what it sees with the mod's aiming, rate and damage; the
pilot's Hydra pods are fixed forward and the mod's own four-degree rule never lets an AI pilot fire them, so the run
pitches the nose onto the smoke from **150 blocks out to 45** (owner: engage earlier, more rockets) and pulls the trigger
on the airframe's weapon system (`vehicleShoot(pilot, "Rocket")`) every three ticks - the mod fires one rocket a trigger
at the pods' own 450 rpm, so a pass puts out about **29 rockets**; the pack's Cobra carries 38 in the pods
(`tools/armour_override.py`, the mod's 14) and fills them from the bay in a second (the mod's ten: a fresh airframe's
magazine is empty, and the ten seconds ate the whole run - 18 triggers put out three rockets before this). The line
dives from 55 up at 150 out to 25 over the smoke and climbs out the same way, so the chin gun's arc reaches the ground.
An invisible, invulnerable dummy at the smoke is the aim point when nothing hostile stands there; anything real
outranks it. **The airframe is fuelled** (owner: "put the battery in like it's supposed to") and flies at the mod's own
power (0.12, `AirRun.POWER`; the run only tops it up): the mod advances the blade by thirty times the power a tick on
every client, so at the full power the old run held the rotor turned eight times a pilot's rate and strobed on screen
(owner: "it kind of rotated"); at a pilot's power it turns as a flown Cobra's does. The client logs the blade angle once
a second while a run is in view (`client/AirDiag.java`, `[gscraft] airdiag` in the client log) - the proof came from
there. The run breaks off on a hit. The rockets hand-fired from 120 blocks out of the old run never arrived: 120 is
past the server's simulation distance and they froze in the air.

## 5. What is deliberately not done

- The Cobra has no pilot: it cannot be shot down by damage alone in the run's five seconds (a hit only makes it
  leave). If it dies (something the run does not do) Tune says *we lost the Cobra*.
- The rockets are fired from the airframe's position at the smoke: with the airframe flown as a prop they land
  well; a physics-flown helicopter would need a pilot goal, which is the vehicle crew's work for another day.
- The mortar in the yard is a Superb Warfare deployable placed by a function. It fires nothing; a player who loads
  it with shells can fire it themselves, which is fine.
- No strike inside the compound's box or on a survivor: not enforced. A player who calls one onto the yard wanted to.
