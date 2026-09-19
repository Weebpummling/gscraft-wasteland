#!/usr/bin/env python3
"""The quest book (system doc 2026-09-13 §7 builds 6-7; quests §2-§7, onboarding §4, start-compound §5).

    python chapters.py             -> build/ftbquests/quests/data.snbt, chapters/<chapter>.snbt and tools/quests.json
    python chapters.py --install   -> also copied to G:/GSCraft/server/config/ftbquests/quests (the local server;
                                      FTB Quests reads config/ftbquests/quests, file version 13; then `/ftbquests reload`)

Eight chapters: the compound (the hub: Wake up, six visible Meet quests saying where each survivor stands, 2026-09-17), one per survivor (tagged with the survivor's id, which the right-click opens by:
`/ftbquests open_book #<chapter>`), hidden behind a "meet" quest that completes on the per-player seen_<id> advancement,
and "The pocket" for the north gate and the five building takes, whose askers arrive with them. Every quest is a line of the
QUESTS table: title (four words, the survivor's phrasing), the voice line, the task line, tasks (hand-ins consume;
"show" does not; locations are the sites' boxes; stages are advancement tasks) and rewards (items; stages and lines as
command rewards, claimed on their own). Ids are stable hashes of the keys, so a rewrite keeps progress.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "mod/src/main/resources/data/gscraft"
SURVIVORS = RES / "gscraft_survivors/survivors.json"
SITES = RES / "gscraft_sites"
OUT = ROOT / "build/ftbquests/quests"
RECORD = ROOT / "tools/quests.json"
SERVER = Path("G:/GSCraft/server/config/ftbquests/quests")
VERSION = 13


def hex_id(name):
    """a stable 16-hex id from the key, with the TOP BIT CLEARED: FTB Quests reads an id as a signed long, so one at or above
    8000000000000000 is an "Invalid Object ID" to its commands and, worse, a dependency pointing at one resolves to nothing -
    the quest behind it is startable from the first minute (found 2026-09-18 by phase 42: 20 of 33 ids were high, and
    "Nuts and bolts" never waited for "Meet Walker"). Clearing the bit changed those ids once; progress on them reset."""
    return format(int(hashlib.sha1(("gscraft:" + name).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF, "016X")


def site_box(site):
    return json.loads((SITES / f"{site}.json").read_text(encoding="utf-8"))["box"]


# ---- the task and reward shapes
def item(id_, count=1, consume=True):
    return {"type": "item", "item": id_, "count": count, "consume": consume}


def show(id_):
    return item(id_, 1, consume=False)


def loc(name, box):
    return {"type": "location", "name": name, "box": box}


def adv(stage):
    return {"type": "advancement", "stage": stage}


CHECK = {"type": "checkmark"}


def give(id_, count=1):
    return {"type": "item", "item": id_, "count": count}


def stage(name):
    return {"type": "stage", "stage": name}


def say(npc, key):
    return {"type": "say", "npc": npc, "key": key}


def cmd(command):
    return {"type": "cmd", "command": command}


# where each survivor stands at the start (start-compound §6), for the hub's Meet quests
WHERE = {
    "walker": ("the yard, at its south end", 2, -2), "michael": ("the brick works, east of the hall", 2, 2),
    "marshall": ("the big hall", 4, -2), "tony": ("the annex, south of the hall", 4, 2),
    "tune": ("the shed by the north gate", 6, -2), "james": ("the road inside the north gate", 6, 2),
}


def meet(npc):
    """the hub's Meet quest (visible, in the compound chapter): completes on the seen_<npc> advancement, the right-click"""
    where, x, y = WHERE[npc]
    return {"key": f"meet_{npc}", "chapter": "compound", "title": "Meet " + npc.capitalize(), "voice": "", "task": f"{npc.capitalize()} is in {where}. Right-click them; their chapter opens here.",
            "x": x, "y": y, "tasks": [adv(f"seen_{npc}")], "rewards": [], "deps": ["wake"], "icon": MEET_ICONS[npc]}


CHAPTERS = [
    # (chapter tag, title, order); the compound first, the six survivors from survivors.json, then the pocket
    ("compound", "The compound", -1),
    ("pocket", "The pocket", 6),
    ("notes", "Field notes", 7),
]
MEET_ICONS = {"walker": "gscraft:wrench", "tony": "gscraft:bandage", "michael": "gscraft:wire_spool", "tune": "gscraft:circuit_board", "james": "minecraft:compass", "marshall": "gscraft:claim_marker"}
ICONS = {"compound": "gscraft:station", "walker": "gscraft:wrench", "tony": "gscraft:bandage", "michael": "gscraft:wire_spool", "tune": "gscraft:circuit_board",
         "james": "minecraft:compass", "marshall": "gscraft:claim_marker", "pocket": "superbwarfare:sandbag", "notes": "minecraft:writable_book"}

QUESTS = [
    # The compound: the one page that says where you are (always visible)
    {"key": "wake", "chapter": "compound", "title": "Wake up", "voice": "Skadowsky. Somebody's town.",
     "task": "You woke in the yard of a walled compound: the big hall east of you, the brick works beyond it, the road out through the north gate. Six survivors live here; meet them (the quests to the right). This journal opens with J or by right-clicking a survivor. The notebook in your pack has the controls.",
     "x": 0, "y": 0, "tasks": [adv("joined")], "rewards": [], "deps": []},   # completes itself on the first join (the per-player `joined` stage): no checkmark to find
    # Walker
    meet("walker"),
    {"key": "W1", "chapter": "walker", "title": "Nuts and bolts", "voice": "Bring me anything with a thread on it.", "task": "Hand in eight bolts and eight nuts from the town's rooms. The reward is a wrench and two blueprint cards: a card in your station's top-left slot is an order.",
     "x": 2, "y": 0, "tasks": [item("gscraft:bolt", 8), item("gscraft:nut", 8)], "deps": ["meet_walker"],
     "rewards": [give("gscraft:wrench"), give("gscraft:card_fastener_kit"), give("gscraft:card_hand_tools"), stage("bp_fastener_kit"), stage("bp_hand_tools"), say("walker", "station")]},
    {"key": "W2", "chapter": "walker", "title": "A place for everything", "voice": "You'll need somewhere to put it all.", "task": "Put the fastener-kit card in your station, four bolts, nuts, screws and nails under it, and wait two minutes. Bring me two kits. The kit is a wrench's work: put the one I gave you in the slot beside the card.",
     "x": 4, "y": 0, "tasks": [item("gscraft:fastener_kit", 2)], "deps": ["W1"],
     "rewards": [give("sophisticatedbackpacks:backpack"), stage("storage_1")]},
    {"key": "W3", "chapter": "walker", "title": "Frame of mind", "voice": "Scrap is only scrap till it's welded.", "task": "Bring twelve metal scrap and show me a welding torch. Workshop 1: every station order runs a little faster, for everyone.",
     "x": 6, "y": 0, "tasks": [item("gscraft:metal_scrap", 12), show("gscraft:welding_torch")], "deps": ["W2"],
     "rewards": [give("gscraft:card_steel_frame"), stage("bp_steel_frame"), stage("workshop_1")]},
    # the loot design (2026-09-19): every survivor's line gets one more rung, and each is the use of something the tables
    # dropped that nothing took - the garage's engine parts here
    {"key": "W4", "chapter": "walker", "title": "It still runs", "voice": "Give me a battery, two plugs and oil and I'll give you a week's welding.", "task": "A car battery, two spark plugs and two motor oil: garages, and the brick works east of the hall. Workshop 2: station orders run faster still.",
     "x": 8, "y": 0, "tasks": [item("gscraft:car_battery", 1), item("gscraft:spark_plug", 2), item("gscraft:motor_oil", 2)], "deps": ["W3"],
     "rewards": [give("gscraft:steel_frame", 2), give("gscraft:fastener_kit", 4), stage("workshop_2")]},
    # Tony
    meet("tony"),
    {"key": "T1", "chapter": "tony", "title": "Field dressing", "voice": "The shelves here are bare.", "task": "Hand in four bandages and two painkillers.",
     "x": 2, "y": 0, "tasks": [item("gscraft:bandage", 4), item("gscraft:painkillers", 2)], "deps": ["meet_tony"],
     "rewards": [give("gscraft:card_med_kit"), stage("bp_med_kit")]},
    {"key": "T2", "chapter": "tony", "title": "Stock the clinic", "voice": "Two for the shelf, and you get more back.", "task": "Order two med kits and bring them. Bandages and painkillers are in any flat; antiseptic and syringes are only where medicine was kept - the clinic in the north complex, or the hospital. Neither is ours: go armed, or go later. With the clinic stocked, Tony cures a bite and gets a downed player up, inside the compound.",
     "x": 4, "y": 0, "tasks": [item("gscraft:med_kit", 2)], "deps": ["T1"],
     "rewards": [give("gscraft:med_kit", 4), stage("medical_1")]},
    {"key": "T3", "chapter": "tony", "title": "Clean air, clean blood", "voice": "A ward needs both.", "task": "Three gas-mask filters and two blood bags. Flats have the filters; blood is only where medicine was kept. After this a death also gives back a magazine of rounds and two bandages.",
     "x": 6, "y": 0, "tasks": [item("gscraft:gas_mask_filter", 3), item("gscraft:blood_bag", 2)], "deps": ["T2"],
     "rewards": [give("gscraft:med_kit", 3), stage("medical_2")]},
    # Michael
    meet("michael"),
    {"key": "M1", "chapter": "michael", "title": "Sparks", "voice": "Wire first. Everything else is wire with a job.", "task": "Hand in three wire spools, a power cord and a water filter.",
     "x": 2, "y": 0, "tasks": [item("gscraft:wire_spool", 3), item("gscraft:power_cord", 1), item("gscraft:water_filter", 1)], "deps": ["meet_michael"],
     "rewards": [give("gscraft:card_wiring_harness"), give("gscraft:card_filter_cartridge"), stage("bp_wiring_harness"), stage("bp_filter_cartridge")]},
    {"key": "M2", "chapter": "michael", "title": "Lights on", "voice": "There's a generator under that tarp.", "task": "Order two wiring harnesses and find a light bulb. Lit, the compound keeps what is out there further from its wall. A harness is pliers' work: Walker's hand-tools card makes a pair, and workshops have them.",
     "x": 4, "y": 0, "tasks": [item("gscraft:wiring_harness", 2), item("gscraft:light_bulb", 1)], "deps": ["M1"],
     "rewards": [stage("generator_1"), say("michael", "lights")]},
    {"key": "M3", "chapter": "michael", "title": "Water", "voice": "The tank's fine. What comes out of it isn't.", "task": "Order two filter cartridges and find a pressure gauge; workshops have the gauges. Clean water: inside the compound, wounds close on their own.",
     "x": 6, "y": 0, "tasks": [item("gscraft:filter_cartridge", 2), item("gscraft:pressure_gauge", 1)], "deps": ["M2"],
     "rewards": [give("gscraft:canned_goods", 6), stage("water_1")]},
    # Tune
    meet("tune"),
    {"key": "U1", "chapter": "tune", "title": "Static", "voice": "I can hear the town from here. I'd like to hear further.", "task": "Hand in a circuit board, two capacitors and a broken radio.",
     "x": 2, "y": 0, "tasks": [item("gscraft:circuit_board", 1), item("gscraft:capacitor", 2), item("gscraft:broken_radio", 1)], "deps": ["meet_tune"],
     "rewards": [give("gscraft:card_circuit_assembly"), stage("bp_circuit_assembly")]},
    {"key": "U2", "chapter": "tune", "title": "The map", "voice": "Two of those and the map talks.", "task": "Order two circuit assemblies and bring them. Radio 1: Tune hears a counterattack ten minutes out. They want a screwdriver set in the tool slot: Walker's hand-tools card makes one.",
     "x": 4, "y": 0, "tasks": [item("gscraft:circuit_assembly", 2)], "deps": ["U1"],
     "rewards": [stage("radio_1"), say("tune", "map")]},
    {"key": "U3", "chapter": "tune", "title": "What was on them", "voice": "Offices kept everything. Bring me their drives.", "task": "Three hard drives, from the town's offices. What is on them is how Tune raises the Cobra, and how she counts a held strongpoint's clock down for everyone to see.",
     "x": 6, "y": 0, "tasks": [item("gscraft:hard_drive", 3)], "deps": ["U2"],
     "rewards": [give("gscraft:circuit_assembly", 1), stage("radio_2")]},   # the drives held the frequencies: `radio_2` gates Air support and nothing set it (audit, 2026-09-19)
    # James
    meet("james"),
    {"key": "J1", "chapter": "james", "title": "Get your bearings", "voice": "Walk it before you trust it.", "task": "Reach the level crossing and the mast's field.",
     "x": 2, "y": 0, "tasks": [loc("the level crossing", site_box("crossing")), loc("the mast's field", site_box("mast"))], "deps": ["meet_james"],
     "rewards": [give("minecraft:compass"), give("minecraft:map")]},
    {"key": "J2", "chapter": "james", "title": "Paper trail", "voice": "Somebody wrote down where things were.", "task": "Three folders of documents, from the town's offices.",
     "x": 4, "y": 0, "tasks": [item("gscraft:folder_of_documents", 3)], "deps": ["J1"],
     "rewards": [give("superbwarfare:handgun_ammo", 24), give("gscraft:canned_goods", 2)]},
    meet("marshall"),
    # Marshall: only after the five introductions
    {"key": "R1", "chapter": "marshall", "title": "Muster", "voice": "We're squatting in someone's town.", "task": "Marshall has a plan for the town. Hear him out.",
     "x": 0, "y": 0, "tasks": [CHECK], "deps": ["W1", "T1", "M1", "U1", "J1"], "hide_until_deps": True,
     "rewards": [give("gscraft:card_claim_marker"), stage("bp_claim_marker"), stage("marshall_speaks"), say("marshall", "speaks")]},
    # The hospital (slice review 2026-09-19, finding 1): the strongpoint had no quest and no way to climb but the operator's
    # command. Its three rungs are the stages the loop sets - scouted by walking in, looted by searching six containers
    # (world/SitePlay.java), held by the marker - and each is an advancement task here.
    {"key": "H1", "chapter": "marshall", "title": "Eyes on it", "voice": "The hospital. Go and look, and come back breathing.", "task": "North up the road, past the junction. Walk into the hospital's grounds; seeing it is enough.",
     "x": 2, "y": -2, "tasks": [adv("hospital_scouted")], "deps": ["R1"], "hide_until_deps": True, "rewards": [], "icon": "minecraft:spyglass"},
    {"key": "H2", "chapter": "marshall", "title": "What they left", "voice": "Tell me what is still on the shelves.", "task": "Search six of the hospital's cupboards and lockers. What you find is yours.",
     "x": 4, "y": -2, "tasks": [adv("hospital_looted")], "deps": ["H1"], "rewards": [give("gscraft:med_kit", 2)], "icon": "gscraft:med_kit"},
    {"key": "H3", "chapter": "marshall", "title": "Plant it", "voice": "Now we take it.", "task": "Build the claim marker at your station - it wants a hand drill in the tool slot - and plant it at the hospital. Then hold for five minutes.",
     "x": 6, "y": -2, "tasks": [adv("hospital_held")], "deps": ["H2"], "rewards": [], "icon": "gscraft:claim_marker"},
    # Marshall's support (strikes note 2026-09-13): the tube, then the fire missions as repeatable hand-ins
    {"key": "tube", "chapter": "marshall", "title": "The tube", "voice": "A mortar is three pieces and a plate.", "task": "Find a mortar's barrel, bipod and base plate in the town's workshops; hand them in with two steel frames. The tube stands in the yard; its shells are a station order, and so is the powder that fills them.",
     "x": 2, "y": 0, "tasks": [item("superbwarfare:mortar_barrel", 1), item("superbwarfare:mortar_bipod", 1), item("superbwarfare:mortar_base_plate", 1), item("gscraft:steel_frame", 2)], "deps": ["R1"], "hide_until_deps": True,
     "rewards": [stage("mortar_built"), cmd("/function gscraft:yard_mortar"), give("gscraft:card_mortar_shell"), stage("bp_mortar_shell"),
                 give("gscraft:card_powder"), stage("bp_powder"),   # the shell order needs powder; without this card the fire mission could never be fed (itemflow, 2026-09-18)
                 say("marshall", "tube")]},
    # rounds are RENEWABLE (loot design 2026-09-19): scrap makes casings, gunpowder and solvent make powder, and the two make
    # rounds. The powder card comes here as well as with The tube, or a player who never built the tube could never load one
    {"key": "brass", "chapter": "marshall", "title": "Brass", "voice": "We stop counting rounds the day we can make them.", "task": "Sixteen metal scrap and two gunpowder. Soldiers carry the powder; so do the factories.",
     "x": 2, "y": 2, "tasks": [item("gscraft:metal_scrap", 16), item("minecraft:gunpowder", 2)], "deps": ["R1"], "hide_until_deps": True,
     "rewards": [give("gscraft:card_rounds"), stage("bp_rounds"), give("gscraft:card_powder"), stage("bp_powder")]},
    {"key": "tags", "chapter": "marshall", "title": "Tags", "voice": "Every tag is a rifle that isn't pointed at us.", "task": "Five dog tags, off soldiers of either army. Marshall pays in rounds, every time.",
     "x": 4, "y": 2, "tasks": [item("superbwarfare:dog_tag", 5)], "deps": ["brass"], "repeat": True,
     "rewards": [give("superbwarfare:rifle_ammo", 16), give("superbwarfare:handgun_ammo", 8)]},
    {"key": "fire_mission", "chapter": "marshall", "title": "Fire mission", "voice": "Six shells buys you one call.", "task": "Hand in six mortar shells for a fire-mission grenade. Throw it where you want the rounds; fifteen seconds, then six of them.",
     "x": 4, "y": 0, "tasks": [item("superbwarfare:mortar_shell", 6)], "deps": ["tube"], "repeat": True,
     "rewards": [give("gscraft:strike_mortar")]},
    {"key": "fire_for_effect", "chapter": "marshall", "title": "Fire for effect", "voice": "The guns reach further than the tube, and hit harder.", "task": "With a strongpoint held, four heavy shells buy a call on its guns: wider, heavier, twenty seconds out.",
     "x": 6, "y": 0, "tasks": [adv("gun_fired"), item("superbwarfare:large_shell_he", 4)], "deps": ["tube"], "repeat": True, "hide_until_deps": True,
     "rewards": [give("gscraft:strike_artillery")]},
    {"key": "air_support", "chapter": "marshall", "title": "Air support", "voice": "Tune found a Cobra on the net. She wants rockets for it.", "task": "Once Tune has read the drives (What was on them), four rockets buy the Cobra: a rocket and gun run on the smoke, thirty seconds out.",
     "x": 8, "y": 0, "tasks": [adv("radio_2"), item("superbwarfare:medium_rocket_he", 4)], "deps": ["tube"], "repeat": True, "hide_until_deps": True,
     "rewards": [give("gscraft:strike_air")]},
    # The pocket: the gap, then the five takes (start-compound §5; ruling R22/R23)
    {"key": "R0", "chapter": "pocket", "title": "The north gate", "voice": "Marshall wants that gate shut before dark.", "task": "Two cloth and four sand at any station make four sandbags; no card needed. Hand in eight, and the north gate is barred. Marshall has a rifle for whoever goes out past it.",
     "x": 0, "y": 0, "tasks": [item("superbwarfare:sandbag", 8)], "deps": ["W1"], "hide_until_deps": True,
     # the long gun before the junction (slice review, step 2): Superb Warfare's Marlin, a lever action that takes the rifle rounds
     # every soldier drops - sixteen a shot, eight in the tube, slow. It comes empty: the rounds are pocketed and loaded, as the notebook says
     "rewards": [stage("compound_closed"), cmd("/function gscraft:gate_close"), give("superbwarfare:marlin"), give("superbwarfare:rifle_ammo", 32)]},
    # the vest with the junction: class 4, and the plates soldiers drop (0.15 a body) refill it - the armour the review found nothing led to
    {"key": "square", "chapter": "pocket", "title": "The junction", "voice": "The square is ours if we say it is.", "task": "Walk the paved junction north-west of the compound, across the rails, and bring back eight metal scrap from its streets. That lights its torch.",
     "x": 2, "y": 0, "tasks": [loc("the square", site_box("square")), item("gscraft:metal_scrap", 8)], "deps": ["R0"],
     "rewards": [stage("square_taken"), stage("skadowsky_scouted"), give("superbwarfare:ru_chest_6b43"), give("superbwarfare:armor_plate", 2)]},
    {"key": "gatehouse", "chapter": "pocket", "title": "The gatehouse", "voice": "The bridge's east end. Bar the doors and Marshall moves in.", "task": "Reach the gatehouse; hand in a fastener kit and eight scrap.",
     "x": 4, "y": -2, "tasks": [loc("the gatehouse", site_box("gatehouse")), item("gscraft:fastener_kit", 1), item("gscraft:metal_scrap", 8)], "deps": ["square"],
     "rewards": [stage("gatehouse_taken")]},
    {"key": "clinic", "chapter": "pocket", "title": "The north complex", "voice": "Twenty-four beds, and a shack with an aerial.", "task": "Reach the clinic; hand in a fastener kit and eight scrap.",
     "x": 4, "y": 0, "tasks": [loc("the north complex", site_box("north")), item("gscraft:fastener_kit", 1), item("gscraft:metal_scrap", 8)], "deps": ["square"],
     "rewards": [stage("clinic_taken")]},
    {"key": "crossing", "chapter": "pocket", "title": "The crossing", "voice": "The east gate is a railway crossing.", "task": "Reach the signal box; hand in a fastener kit and eight scrap.",
     "x": 4, "y": 2, "tasks": [loc("the crossing", site_box("crossing")), item("gscraft:fastener_kit", 1), item("gscraft:metal_scrap", 8)], "deps": ["square"],
     "rewards": [stage("crossing_taken")]},
    {"key": "mast", "chapter": "pocket", "title": "The mast's field", "voice": "The mast is dead. The field under it doesn't have to be.", "task": "Reach the field; hand in two fastener kits and sixteen scrap.",
     "x": 6, "y": 0, "tasks": [loc("the mast's field", site_box("mast")), item("gscraft:fastener_kit", 2), item("gscraft:metal_scrap", 16)], "deps": ["gatehouse", "clinic", "crossing"],
     "rewards": [stage("mast_taken"), stage("skadowsky_held")]},
    # Field notes (onboarding §4.5): the chapter that writes itself - each entry invisible until its per-player note_<key>
    # advancement is granted (journal/FieldNotes.java), two lines, no reward; the rule gets its name after the fact
    {"key": "note_death", "chapter": "notes", "title": "The first death", "voice": "It happens to everyone once.", "task": "You came back in the compound with the pistol, loaded, and the notebook. Everything else lies where you fell; a friend can get you up before it comes to that.",
     "x": 0, "y": 0, "tasks": [adv("note_death")], "rewards": [], "deps": [], "invisible": True, "until_tasks": 1, "icon": "minecraft:skeleton_skull"},
    {"key": "note_bulky", "chapter": "notes", "title": "Heavy", "voice": "Some things are carried, not pocketed.", "task": "Some things are bulky - the tooltip says so in gold. Carrying one slows you and stops you sprinting; one at a time.",
     "x": 2, "y": 0, "tasks": [adv("note_bulky")], "rewards": [], "deps": [], "invisible": True, "until_tasks": 1, "icon": "gscraft:steel_frame"},
    {"key": "note_vehicle", "chapter": "notes", "title": "Wheels", "voice": "It still runs.", "task": "A seat is a right-click; out is sneak. The fuel and the rounds are the vehicle's own - the crews out there have the same ones.",
     "x": 4, "y": 0, "tasks": [adv("note_vehicle")], "rewards": [], "deps": [], "invisible": True, "until_tasks": 1, "icon": "minecraft:minecart"},
    {"key": "note_infected", "chapter": "notes", "title": "Bitten", "voice": "It is in the blood now.", "task": "An infection runs on a clock. A med kit, held to use, cures it; so does the compound, once Tony's clinic is stocked. Tony's card makes the kits - carry one north.",
     "x": 6, "y": 0, "tasks": [adv("note_infected")], "rewards": [], "deps": [], "invisible": True, "until_tasks": 1, "icon": "minecraft:rotten_flesh"},
    {"key": "note_warning", "chapter": "notes", "title": "They are coming back", "voice": "Tune heard them first.", "task": "A held strongpoint is counterattacked when its clock runs out. The warning comes ten minutes ahead; the walls you built are what meets them.",
     "x": 8, "y": 0, "tasks": [adv("note_warning")], "rewards": [], "deps": [], "invisible": True, "until_tasks": 1, "icon": "minecraft:bell"},
]


# ---- snbt writing (FTB Library's shape: one key per line, tabs, no commas)
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def snbt(value, depth=0):
    pad = "\t" * depth
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value}d"
    if isinstance(value, str):
        return q(value)
    if isinstance(value, tuple):   # an int array
        return "[I;" + ", ".join(str(v) for v in value) + "]"
    if isinstance(value, list):
        if not value:
            return "[ ]"
        inner = "".join(pad + "\t" + snbt(v, depth + 1) + "\n" for v in value)
        return "[\n" + inner + pad + "]"
    if isinstance(value, dict):
        if not value:
            return "{ }"
        inner = "".join(pad + "\t" + k + ": " + snbt(v, depth + 1) + "\n" for k, v in value.items())
        return "{\n" + inner + pad + "}"
    raise TypeError(type(value))


def task_nbt(qkey, i, t):
    base = {"id": hex_id(f"task:{qkey}:{i}")}
    if t["type"] == "item":
        base.update({"type": "item", "item": t["item"], "count": t["count"]})
        if t["consume"]:
            base["consume_items"] = True
        else:
            base["title"] = "Show " + t["item"].split(":")[1].replace("_", " ")
    elif t["type"] == "location":
        x0, x1, z0, z1 = t["box"]
        base.update({"type": "location", "title": "Reach " + t["name"], "dimension": "minecraft:overworld", "ignore_dimension": False,
                     "position": (min(x0, x1), 40, min(z0, z1)), "size": (abs(x1 - x0) + 1, 70, abs(z1 - z0) + 1)})
    elif t["type"] == "advancement":
        base.update({"type": "advancement", "advancement": f"gscraft:stage/{t['stage']}", "criterion": "set"})
    elif t["type"] == "checkmark":
        base.update({"type": "checkmark"})
    return base


def reward_nbt(qkey, i, r):
    base = {"id": hex_id(f"reward:{qkey}:{i}")}
    if r["type"] == "item":
        base.update({"type": "item", "auto": "enabled", "item": r["item"], "count": r["count"]})
    elif r["type"] == "stage":
        base.update({"type": "command", "title": "the stage " + r["stage"], "command": f"/gscraft stage add {r['stage']}", "elevate_perms": True, "silent": True, "auto": "invisible"})
    elif r["type"] == "say":
        base.update({"type": "command", "title": r["npc"] + " speaks", "command": f"/gscraft say {r['npc']} {r['key']} @s", "elevate_perms": True, "silent": True, "auto": "invisible"})
    elif r["type"] == "cmd":
        base.update({"type": "command", "title": r["command"].split(" ")[0].lstrip("/"), "command": r["command"], "elevate_perms": True, "silent": True, "auto": "invisible"})
    return base


def quest_nbt(d):
    nbt = {"id": hex_id("quest:" + d["key"]), "x": float(d["x"]), "y": float(d["y"]), "title": d["title"]}
    if d.get("voice"):
        nbt["subtitle"] = d["voice"]
    if d.get("task"):
        nbt["description"] = [d["task"]]
    if d.get("deps"):
        nbt["dependencies"] = [hex_id("quest:" + k) for k in d["deps"]]
    if d.get("icon"):
        nbt["icon"] = d["icon"]
    if d.get("invisible"):
        nbt["invisible"] = True
    if d.get("until_tasks"):
        nbt["invisible_until_tasks"] = d["until_tasks"]   # a field note: it appears when its one task is done
    if d.get("hide_until_deps"):
        nbt["hide_until_deps_complete"] = True
    if d.get("repeat"):
        nbt["can_repeat"] = True
    nbt["tasks"] = [task_nbt(d["key"], i, t) for i, t in enumerate(d["tasks"])]
    nbt["rewards"] = [reward_nbt(d["key"], i, r) for i, r in enumerate(d["rewards"])]
    return nbt


def chapter_nbt(tag, title, index, quests):
    nbt = {"id": hex_id(tag), "group": "", "order_index": index, "filename": tag, "title": title, "default_quest_shape": "",
            "default_hide_dependency_lines": False, "tags": [tag], "quests": [quest_nbt(d) for d in quests], "quest_links": []}
    if tag in ICONS:
        nbt["icon"] = ICONS[tag]
    return nbt


DATA = {"version": VERSION, "default_quest_shape": "circle", "default_reward_team": False, "disable_gui": False, "drop_loot_crates": False}


def main(argv):
    survivors = json.loads(SURVIVORS.read_text(encoding="utf-8"))["survivors"]
    chapters = sorted([(d["chapter"], d["name"].split(" ")[0], i) for i, d in enumerate(survivors)] + CHAPTERS, key=lambda c: c[2])
    keys = [d["key"] for d in QUESTS]
    assert len(keys) == len(set(keys)), "duplicate quest keys"
    for d in QUESTS:
        for k in d.get("deps", []):
            assert k in keys, f"{d['key']} depends on unknown {k}"
        assert d["chapter"] in [c[0] for c in chapters], f"{d['key']} in unknown chapter {d['chapter']}"
    (OUT / "chapters").mkdir(parents=True, exist_ok=True)
    (OUT / "data.snbt").write_text(snbt(DATA) + "\n", encoding="utf-8")
    for tag, title, index in chapters:
        quests = [d for d in QUESTS if d["chapter"] == tag]
        (OUT / "chapters" / f"{tag}.snbt").write_text(snbt(chapter_nbt(tag, title, index, quests)) + "\n", encoding="utf-8")
    RECORD.write_text(json.dumps({"chapters": [{"tag": t, "title": ti, "id": hex_id(t)} for t, ti, _ in chapters],
                                  "quests": [dict(d, id=hex_id("quest:" + d["key"])) for d in QUESTS]}, indent=1), encoding="utf-8")
    print(f"{len(chapters)} chapters, {len(QUESTS)} quests written to {OUT}; record {RECORD.name}")
    if "--install" in argv:
        (SERVER / "chapters").mkdir(parents=True, exist_ok=True)
        shutil.copy(OUT / "data.snbt", SERVER / "data.snbt")
        for tag, _, _ in chapters:
            shutil.copy(OUT / "chapters" / f"{tag}.snbt", SERVER / "chapters" / f"{tag}.snbt")
        print(f"installed to {SERVER}")


if __name__ == "__main__":
    main(sys.argv[1:])
